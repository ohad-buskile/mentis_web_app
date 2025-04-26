from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
import uuid
from utils import csv_utils, sentiment_analysis
from mentis_summarization import summarization

client_bp = Blueprint('client', __name__, url_prefix='/client')

@client_bp.route('/')
def dashboard():
    if 'user' not in session or session['user']['role'] != 'client':
        return redirect(url_for('login'))

    email = session['user']['email']
    page = int(request.args.get('page', 1))
    entries = csv_utils.read_csv('journal.csv')
    user_entries = [e for e in entries if e['user_email'] == email]
    user_entries.sort(key=lambda x: x['datetime'], reverse=True)

    per_page = 5
    start = (page - 1) * per_page
    end = start + per_page
    total_pages = (len(user_entries) + per_page - 1) // per_page

    return render_template('client.html',
                           user=session['user'],
                           entries=user_entries[start:end],
                           current_page=page,
                           total_pages=total_pages)

@client_bp.route('/add', methods=['POST'])
def add_entry():
    if 'user' not in session:
        return redirect(url_for('login'))

    entry_id = str(uuid.uuid4())
    email = session['user']['email']
    text = request.form['text']
    now = datetime.now().isoformat()

    csv_utils.append_csv('journal.csv', [entry_id, email, text, now])
    flash("Journal entry saved.")
    return redirect(url_for('client.dashboard'))

@client_bp.route('/analyze', methods=['POST'])
def analyze():
    if 'user' not in session:
        return redirect(url_for('login'))

    email = session['user']['email']
    range_type = request.form['range']
    now = datetime.now()

    if range_type == 'week':
        start = (now - timedelta(days=7)).isoformat()
    elif range_type == 'month':
        start = (now - timedelta(days=30)).isoformat()
    else:
        flash("Invalid range.")
        return redirect(url_for('client.dashboard'))

    end = now.isoformat()

    entries = csv_utils.read_csv('journal.csv')
    filtered = [e for e in entries if e['user_email'] == email and start <= e['datetime'] <= end]

    if not filtered:
        flash("No entries found in this range.")
        return redirect(url_for('client.dashboard'))

    texts = " ".join([e['text'] for e in filtered])
    related_ids = ",".join([e['entry_id'] for e in filtered])
    analysis_id = str(uuid.uuid4())
    sentiment = sentiment_analysis.analyze_sentiment(texts)
    summary = summarization.summarize_entries(filtered)
    date_span = f"{range_type.title()}"

    csv_utils.append_csv('analysis.csv', [analysis_id, email, related_ids, sentiment, summary, date_span])
    flash(f"Sentiment: {sentiment} | Summary: {summary}")
    return redirect(url_for('client.dashboard'))

@client_bp.route('/summarize', methods=['POST'])
def summarize():
    if 'user' not in session:
        return redirect(url_for('login'))

    email = session['user']['email']
    range_type = request.form['range']
    now = datetime.now()

    if range_type == 'week':
        start_dt = now - timedelta(days=7)
    elif range_type == 'month':
        start_dt = now - timedelta(days=30)
    else:
        flash("Invalid range.")
        return redirect(url_for('client.dashboard'))

    entries = csv_utils.read_csv('journal.csv')
    filtered = [e for e in entries if e['user_email'] == email and start_dt.isoformat() <= e['datetime'] <= now.isoformat()]

    if not filtered:
        flash("No entries found for summarization.")
        return redirect(url_for('client.dashboard'))

    summary = summarization.summarize_entries(filtered)
    flash(f"Summary: {summary}")
    return redirect(url_for('client.dashboard'))
