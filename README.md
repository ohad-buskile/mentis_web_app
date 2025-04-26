
# Mentis — AI-Powered Therapy Support App

Mentis is a therapy journaling platform designed to empower users to track their emotions, receive insights, and help therapists prepare for sessions with meaningful, data-driven analysis.

This project provides:
- **Secure journal entry** and **analysis** for clients.
- **Sentiment analysis** and **summarization** of user logs.
- **Dashboards** for both clients and therapists.

---

## 📦 Project Structure

- `app.py` — Flask application managing user authentication and dashboards.
- `utils/` — CSV reading/writing utilities, sentiment analysis module, summarization module.
- `templates/` — HTML templates (base, login, register, client and therapist dashboards).
- `mentis_summarization/` — Local model files (excluded from GitHub).

---

## 📈 Models Used

This project uses two locally fine-tuned models:

| Purpose | Model | Training |
|:--------|:------|:---------|
| Summarization | **T5-Small** | Fine-tuned locally on therapy-style journal data |
| Sentiment Analysis | **DistilBERT-base-uncased** | Fine-tuned locally for positive, neutral, and negative classification |

> ⚡ **Important Note:**  
> The trained model files were **too large to upload to GitHub** (GitHub limit = 100MB).  
> If needed, you can retrain your own or request access separately.

---

## 🔗 Data Sources

- **Summarization training data:**  
  https://www.kaggle.com/datasets/gowrishankarp/newspaper-text-summarization-cnn-dailymail

- **Sentiment analysis training data:**  
  https://www.kaggle.com/datasets/madhavmalhotra/journal-entries-with-labelled-emotions



---

## 🚀 Running the App Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/mentis.git
   cd mentis
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare local model files:**
   Place the trained summarization and sentiment analysis models inside:
   ```
   mentis_summarization/t5-small-local/
   ```

4. **Run the Flask app:**
   ```bash
   python app.py
   ```

5. **Access the app:**
   Open your browser and go to `http://127.0.0.1:5000/`.

---

## 🔒 Privacy & Security

- All user data is stored locally in CSV files.
- Users have the right to delete their data at any time.
- No personal information is shared with any third parties.

---


## 🙏 Acknowledgements

Developed as part of the **Final Project** at  
**Afeka College of Engineering**.

**Authors:**
- Ohad Buskile
- Ilana Gofman

