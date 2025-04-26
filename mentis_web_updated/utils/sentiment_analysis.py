# Sentiment analysis logic
def analyze_sentiment(text):
    if "happy" in text.lower():
        return "positive"
    elif "sad" in text.lower():
        return "negative"
    else:
        return "neutral"
