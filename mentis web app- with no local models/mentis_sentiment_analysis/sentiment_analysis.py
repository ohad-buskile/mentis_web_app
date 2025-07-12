from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os
import torch
import numpy as np

# ✅ Use __file__ to get correct relative path
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(_THIS_DIR, "distilbert_emotion_finetuned_full")

# ✅ Load from local only
tok = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
model = AutoModelForSequenceClassification.from_pretrained(model_path, local_files_only=True)

# ✅ Ensure on CPU
model.to("cpu")
model.eval()

# Define parent categories
parent_map = {
    "Good": ["happy", "satisfied", "proud", "excited"],
    "Neutral": ["nostalgic", "calm"],
    "Uneasy": ["anxious", "ashamed", "awkward", "confused"],
    "Struggling": ["sad", "angry", "frustrated", "afraid", "disgusted", "jealous", "bored"]
}

label_cols = sorted(set(sum(parent_map.values(), [])))

def analyze_sentiment(text):
    with torch.no_grad():
        inputs = tok(
            text,
            return_tensors="pt",
            truncation=True,
            padding="max_length",
            max_length=128
        )
        inputs = {k: v.to("cpu") for k, v in inputs.items()}
        logits = model(**inputs).logits
        probs = torch.sigmoid(logits)[0].numpy()

        # full basic-emotion breakdown
        emotion_scores = dict(zip(label_cols, probs))

        # Raw parent group scores
        parent_scores = {
            group: np.mean([emotion_scores[e] for e in members if e in emotion_scores])
            for group, members in parent_map.items()
        }

        # Normalize so max is 1.0
        max_score = max(parent_scores.values())
        if max_score > 0:
            parent_scores = {k: v / max_score for k, v in parent_scores.items()}

        # Top-level category
        top_category = max(parent_scores, key=parent_scores.get)

        # Return three values: top category, parent breakdown, and basic-emotion breakdown
        return top_category, parent_scores, emotion_scores
