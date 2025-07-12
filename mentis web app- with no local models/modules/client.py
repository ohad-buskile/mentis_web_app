from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime, timedelta
import uuid

from utils.csv_utils import read_csv, append_csv, get_user_by_email, update_user_mantra
from mentis_sentiment_analysis import sentiment_analysis
from mentis_summarization import summarization

client_bp = Blueprint('client', __name__, url_prefix='/client')


def _compute_latest_analysis(email: str):
    """Run weekly sentiment + summary for the given user."""
    entries = read_csv('journal.csv')
    user_entries = [e for e in entries if e['user_email'] == email]
    user_entries.sort(key=lambda x: x['datetime'], reverse=True)

    now = datetime.now()
    week_start = (now - timedelta(days=7)).isoformat()
    week_entries = [e for e in user_entries if week_start <= e['datetime'] <= now.isoformat()]

    if not week_entries:
        return None

    texts = ' '.join(e['text'] for e in week_entries)
    _, parent_raw, emo_raw = sentiment_analysis.analyze_sentiment(texts)
    parent_scores = {k: float(v) for k, v in parent_raw.items()}
    emotion_scores = {k: float(v) for k, v in emo_raw.items()}
    summary = summarization.summarize_entries(week_entries, period_label='week')

    return {
        'parent_scores': parent_scores,
        'emotions': emotion_scores,
        'summary': summary
    }


@client_bp.route('/')
def dashboard():
    # auth check
    if 'user' not in session or session['user']['role'] != 'client':
        return redirect(url_for('login'))

    email = session['user']['email']
    user = get_user_by_email(email) or session['user']
    mantra = user.get('mantra', '')

    # Load & paginate journal entries
    entries = read_csv('journal.csv')
    yours = [e for e in entries if e['user_email'] == email]
    yours.sort(key=lambda x: x['datetime'], reverse=True)

    page = int(request.args.get('page', 1))
    per_page = 5
    start, end = (page - 1) * per_page, (page - 1) * per_page + per_page
    paged = yours[start:end]
    total_pages = ((len(yours) - 1) // per_page) + 1 if yours else 1

    return render_template('client.html',
                           user=user,
                           entries=paged,
                           total_pages=total_pages,
                           current_page=page,
                           mantra=mantra)


@client_bp.route('/api/latest_analysis')
def latest_analysis_api():
    if 'user' not in session or session['user']['role'] != 'client':
        return jsonify({})
    email = session['user']['email']
    analysis = _compute_latest_analysis(email)
    return jsonify(analysis or {})


@client_bp.route('/add_entry', methods=['POST'])
def add_entry():
    if 'user' not in session or session['user']['role'] != 'client':
        return redirect(url_for('login'))
    entry_id = str(uuid.uuid4())
    email = session['user']['email']
    text = request.form['text']
    now = datetime.now().isoformat()
    append_csv('journal.csv', [entry_id, email, text, now])
    flash('Journal entry saved.')
    return redirect(url_for('client.dashboard'))


@client_bp.route('/set_mantra', methods=['POST'])
def set_mantra():
    if 'user' not in session:
        return redirect(url_for('login'))
    email = session['user']['email']
    new_mantra = request.form.get('mantra', '').strip()
    update_user_mantra(email, new_mantra)
    flash('Your mantra has been updated.')
    return redirect(url_for('client.dashboard'))
