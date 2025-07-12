# summarization.py — Mentis summariser (FLAN-T5-base fine-tuned on notes)
import os, torch
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_dt
from transformers import T5Tokenizer, T5ForConditionalGeneration
from collections import defaultdict

# ── model init ──
_THIS_DIR  = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR  = os.path.join(_THIS_DIR, "journal_summary_model").replace("\\", "/")

tok   = T5Tokenizer.from_pretrained(MODEL_DIR, local_files_only=True)
model = T5ForConditionalGeneration.from_pretrained(MODEL_DIR, local_files_only=True)

_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(_device)
import csv
from datetime import datetime

def get_latest_entries(client_email):
    """
    Return a list of text entries from journal.csv for this client.
    """
    entries = []
    with open('journal.csv', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('email') == client_email:
                entries.append(row.get('text', ''))
    return entries
# ── generation helpers ──

def _gen_cfg(period: str):
    cfg = dict(
        no_repeat_ngram_size=4,
        repetition_penalty=1.1,
        early_stopping=True,
        eos_token_id=tok.eos_token_id,
        pad_token_id=tok.eos_token_id,
    )
    if period == "week":
        cfg.update(num_beams=3, do_sample=False, max_length=90, min_length=40)
    else:
        cfg.update(num_beams=4, do_sample=False, max_length=100, min_length=40)
    return cfg

PROMPT_TMPL = "summarize: {note}"

STOP_PHRASES = [
    "National Institutes of Health",
    "All rights reserved",
    "broadcast",
    "Disclaimer"
]

def _clean(txt: str) -> str:
    for p in STOP_PHRASES:
        if p in txt:
            txt = txt.split(p)[0].strip()
    return txt

def _generate_summary(note_text: str, period: str, date: str) -> str:
    print(f"[GENERATING] {date} with {len(note_text.split())} words")
    prompt = PROMPT_TMPL.format(note=note_text)
    enc = tok(prompt, return_tensors="pt", truncation=True, max_length=512, padding="max_length").to(_device)
    ids = model.generate(**enc, **_gen_cfg(period))
    return _clean(tok.decode(ids[0], skip_special_tokens=True).strip())

# ── main controller ──

def summarize_entries(entries, period_label: str = "month", short_mode=False) -> str:
    if not entries:
        return "No valid journal entries to summarize."

    day_notes = defaultdict(list)
    for e in entries:
        try:
            dt  = parse_dt(e["datetime"])
            key = dt.strftime("%A %d.%m")
            text = e["text"].strip().replace("\n", " ")
            if text not in day_notes[key]:  # Deduplicate by exact string
                day_notes[key].append(text)
        except Exception:
            continue

    if not day_notes:
        return "No valid text entries to summarize."

    day_summaries = {}
    for day, texts in sorted(day_notes.items()):
        try:
            joined_text = "\n\n---\n\n".join(f"{t}" for t in texts)
            day_summaries[day] = _generate_summary(joined_text, period="week", date=day)
        except Exception as err:
            day_summaries[day] = f"⚠️ Failed: {err}"

    if period_label == "week":
        return "\n\n".join(f"🗓️ {d}\n• {s}" for d, s in day_summaries.items())

    week_raw = defaultdict(list)
    for day_str, bullet in day_summaries.items():
        try:
            dt      = datetime.strptime(day_str, "%A %d.%m")
            monday  = dt - timedelta(days=dt.weekday())
            week_key = f"Week of {monday.strftime('%d.%m')}"
            week_raw[week_key].append(bullet)
        except Exception:
            continue

    output = []
    for wk, bullets in sorted(week_raw.items()):
        try:
            joined  = " \n\n---\n\n".join(bullets)
            summary = _generate_summary(joined, period="month", date=wk)
            output.append(f"{wk}:\n• {summary}")
        except Exception as err:
            output.append(f"{wk}: ⚠️ Failed to summarise week: {err}")

    if short_mode:
        return " | ".join(s.split("\n")[0].replace("•", "").strip() for s in output)

    return "\n\n".join(output)
