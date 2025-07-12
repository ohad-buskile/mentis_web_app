"""Therapist blueprint – handles dashboard, client assignment and on-demand analysis
--------------------------------------------------------------------------
This version keeps the UI exactly as defined in *therapist.html* but
switches to a single-pass summarisation/sentiment flow so the request
returns in a few seconds on CPU instead of hanging the browser.
"""

from __future__ import annotations

from datetime import datetime, timedelta
import uuid

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from utils import csv_utils
from mentis_sentiment_analysis import sentiment_analysis
from mentis_summarization import summarization

therapist_bp = Blueprint("therapist", __name__, url_prefix="/therapist")

# Map high-level sentiment categories to a simple –1 … 1 score for the line
# chart. We deliberately collapse both "Uneasy" and "Struggling" to –1 so the
# graph remains intuitive.
_SENTIMENT_SCORE = {"Good": 1, "Neutral": 0, "Uneasy": -1, "Struggling": -1}


@therapist_bp.route("/", methods=["GET", "POST"])
def dashboard():
    """Default therapist view *and* analysis endpoint.

    • **GET**  ➜ plain dashboard with client picker.
    • **POST** ➜ triggered from the “Analyse Week / Month” buttons – runs a
      lightweight NLP pass and redisplays results on the same template.
    """

    # 1️⃣  ── auth guard
    if "user" not in session or session["user"].get("role") != "therapist":
        return redirect(url_for("login"))

    therapist_email = session["user"]["email"]
    clients = csv_utils.get_clients_for_therapist(therapist_email)

    # Safe-guard empty list so the template does not explode.
    selected_client_email: str | None = (
        request.form.get("client_select") or (clients[0]["email"] if clients else None)
    )
    period: str | None = request.form.get("range")  # "week", "month" or None (plain GET)

    summary: str = ""
    sentiment: str = ""
    parent_scores: list[tuple[str, float]] = []
    sentiment_trend: list[tuple[str, int]] = []

    # 2️⃣  ── run analysis when the form is submitted
    if period and selected_client_email:
        # Collect entries for the chosen window
        now = datetime.utcnow()
        window_start = now - timedelta(days=7 if period == "week" else 30)

        all_entries = csv_utils.read_csv("journal.csv")
        entries = [
            e
            for e in all_entries
            if e["user_email"] == selected_client_email
            and window_start.isoformat() <= e["datetime"] <= now.isoformat()
        ]

        if not entries:
            flash("No journal entries found for the selected period.", "warning")
        else:
            # --- summarise ***once*** instead of per-day for speed
            joined_text = "\n\n".join(e["text"] for e in entries)
            summary = summarization._generate_summary(
                joined_text,
                period=period,
                date=now.strftime("%Y-%m-%d"),
            )

            # --- sentiment pass (single model call)
            sentiment, parent_dict, _ = sentiment_analysis.analyze_sentiment(joined_text)
            parent_scores = [(k, float(v)) for k, v in parent_dict.items()]

            # --- very light trend: same score for every day that had an entry
            scores_by_date: dict[str, int] = {}
            for e in entries:
                day = e["datetime"].split("T")[0]
                scores_by_date.setdefault(day, _SENTIMENT_SCORE.get(sentiment, 0))
            sentiment_trend = sorted(scores_by_date.items())

            # --- persist to analysis.csv for history / therapist reviews
            csv_utils.append_csv(
                "analysis.csv",
                [
                    str(uuid.uuid4()),
                    selected_client_email,
                    ",".join(e["entry_id"] for e in entries),
                    sentiment,
                    summary.replace("\n", " "),
                    f"{window_start.date()} – {now.date()}",
                ],
            )

    # 3️⃣  ── render template
    return render_template(
        "therapist.html",
        user=session["user"],
        clients=clients,
        selected_client_email=selected_client_email,
        summary=summary,
        sentiment=sentiment,
        parent_scores=parent_scores,
        sentiment_trend=sentiment_trend,
    )


@therapist_bp.route("/assign", methods=["POST"])
def assign_client():
    """Bind an existing *client* account to the current therapist."""

    if "user" not in session:
        return redirect(url_for("login"))

    client_email = request.form["client_email"].strip().lower()
    therapist_email = session["user"]["email"]

    if csv_utils.assign_client_to_therapist(client_email, therapist_email):
        flash(f"{client_email} assigned successfully.", "success")
    else:
        flash("Client not found or already assigned.", "danger")

    return redirect(url_for("therapist.dashboard"))


# Optional: retained for bulk / custom-range analyses from other screens.
@therapist_bp.route("/analyze", methods=["POST"])
def analyze_custom_range():
    if "user" not in session:
        return redirect(url_for("login"))

    client_email = request.form.get("client_email")
    start_date = request.form.get("start")
    end_date = request.form.get("end")
    range_type = request.form.get("range_type", "month")  # fallback to month

    if not (client_email and start_date and end_date):
        flash("Missing parameters for custom analysis.", "danger")
        return redirect(url_for("therapist.dashboard"))

    start_iso = f"{start_date}T00:00:00"
    end_iso = f"{end_date}T23:59:59"

    entries = csv_utils.read_csv("journal.csv")
    entries = [
        e
        for e in entries
        if e["user_email"] == client_email and start_iso <= e["datetime"] <= end_iso
    ]

    if not entries:
        flash("No entries found in selected range.", "warning")
        return redirect(url_for("therapist.dashboard"))

    joined_text = "\n\n".join(e["text"] for e in entries)
    sentiment, _, _ = sentiment_analysis.analyze_sentiment(joined_text)
    summary = summarization._generate_summary(joined_text, period=range_type, date=start_date)

    csv_utils.append_csv(
        "analysis.csv",
        [
            str(uuid.uuid4()),
            client_email,
            ",".join(e["entry_id"] for e in entries),
            sentiment,
            summary.replace("\n", " "),
            f"{start_date} – {end_date}",
        ],
    )

    flash("Custom analysis completed and saved.", "success")
    return redirect(url_for("therapist.dashboard"))
