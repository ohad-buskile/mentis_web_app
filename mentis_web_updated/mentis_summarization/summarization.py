# Summarization logic
def summarize_entries(entries):
    combined = " ".join(e['text'] for e in entries)
    return (combined[:100] + "...") if len(combined) > 100 else combined
