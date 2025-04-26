from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
import uuid
from utils import csv_utils, sentiment_analysis
from mentis_summarization import summarization

therapist_bp = Blueprint('therapist', __name__, url_prefix='/therapist')


@therapist_bp.route('/', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session or session['user']['role'] != 'therapist':
        return redirect(url_for('login'))

    therapist_email = session['user']['email']
    clients = csv_utils.get_clients_for_therapist(therapist_email)
    selected_client_email = request.form.get('client_select') or (clients[0]['email'] if clients else None)

    summary = ""
    sentiment = ""
    entry_counts = []
    sentiment_trend = []

    if request.form.get('range'):
        entries = csv_utils.read_csv('journal.csv')
        now = datetime.now()
        range_type = request.form['range']
        start = now - timedelta(days=7 if range_type == 'week' else 30)
        filtered = [e for e in entries if
                    e['user_email'] == selected_client_email and start.isoformat() <= e['datetime'] <= now.isoformat()]

        if filtered:
            summary = summarization.summarize_entries(filtered)
            sentiment = sentiment_analysis.analyze_sentiment(" ".join([e['text'] for e in filtered]))

            # for chart 1 - daily counts
            date_count = {}
            for e in filtered:
                date = e['datetime'].split('T')[0]
                date_count[date] = date_count.get(date, 0) + 1
            entry_counts = sorted(date_count.items())

            # for chart 2 - sentiment trend
            sentiment_map = {"positive": 1, "neutral": 0, "negative": -1}
            sentiment_trend = [
                (e['datetime'].split('T')[0], sentiment_map[sentiment_analysis.analyze_sentiment(e['text'])]) for e in
                filtered]
            sentiment_trend = sorted(sentiment_trend)

    return render_template('therapist.html', user=session['user'],
                           clients=clients,
                           selected_client_email=selected_client_email,
                           summary=summary,
                           sentiment=sentiment,
                           entry_counts=entry_counts,
                           sentiment_trend=sentiment_trend)


@therapist_bp.route('/analyze', methods=['POST'])
def analyze():
    if 'user' not in session:
        return redirect(url_for('login'))

    client_email = request.form['client_email']
    start = request.form['start'] + "T00:00:00"
    end = request.form['end'] + "T23:59:59"

    entries = csv_utils.read_csv('journal.csv')
    filtered = [e for e in entries if e['user_email'] == client_email and start <= e['datetime'] <= end]

    if not filtered:
        flash("No entries found for client in this date range.")
        return redirect(url_for('therapist.dashboard'))

    texts = " ".join([e['text'] for e in filtered])
    related_ids = ",".join([e['entry_id'] for e in filtered])
    analysis_id = str(uuid.uuid4())
    sentiment = sentiment_analysis.analyze_sentiment(texts)
    summary = summarization.summarize_entries(filtered)
    date_span = f"{request.form['start']} to {request.form['end']}"

    csv_utils.append_csv('analysis.csv', [analysis_id, client_email, related_ids, sentiment, summary, date_span])
    flash(f"Sentiment: {sentiment} | Summary: {summary}")
    return redirect(url_for('therapist.dashboard'))

@therapist_bp.route('/assign', methods=['POST'])
def assign_client():
    if 'user' not in session:
        return redirect(url_for('login'))

    client_email = request.form['client_email']
    therapist_email = session['user']['email']

    if csv_utils.assign_client_to_therapist(client_email, therapist_email):
        flash(f"{client_email} assigned successfully.")
    else:
        flash("Client not found or already assigned.")

    return redirect(url_for('therapist.dashboard'))
