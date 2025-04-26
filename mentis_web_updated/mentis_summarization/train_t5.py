from transformers import T5Tokenizer, T5ForConditionalGeneration

# Set the local path to your downloaded model
local_model_path = r"C:\Users\ohad.buskile\mentis_web_updated\mentis_summarization\t5-small-local"

print("🔹 Loading tokenizer from local path...")
tokenizer = T5Tokenizer.from_pretrained(local_model_path)
print("✅ Tokenizer loaded successfully.")

print("🔹 Loading model from local path...")
model = T5ForConditionalGeneration.from_pretrained(local_model_path)
print("✅ Model loaded successfully.")

def summarize_entries(entries):
    print(f"🔹 Received {len(entries)} entries for summarization.")

    combined = " ".join(e['text'] for e in entries)
    if not combined.strip():
        print("⚠️ No meaningful text found in entries.")
        return "No meaningful text to summarize."

    print("🔹 Tokenizing input text...")
    input_text = "summarize: " + combined
    inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)

    print("🔹 Generating summary...")
    summary_ids = model.generate(
        inputs,
        max_length=100,
        min_length=20,
        num_beams=4,
        early_stopping=True
    )

    decoded_summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    print("✅ Summary generated successfully.")
    return decoded_summary
