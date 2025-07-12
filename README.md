# Mentis — AI‑Powered Therapy Support App

Mentis is a therapy journaling platform designed to empower users to track their emotions, receive insights, and help therapists prepare for sessions with meaningful, data‑driven analysis.

---

## ✨ Key Features

* **Secure journal entry** and **analysis** for clients.
* **Sentiment analysis** and **summarization** of user logs powered by locally fine‑tuned language models.
* **Dashboards** with rich visualizations for both clients and therapists.

---

## 📦 Project Structure

```
mentis/
├── app.py                     # Flask entry‑point
├── utils/
│   └── csv_utils.py           # Lightweight CSV database helpers
├── mentis_sentiment_analysis/
│   └── distilbert_emotion_finetuned_full/  # ⬇️ place model here
├── mentis_summarization/
│   └── journal_summary_model/             # ⬇️ place model here
└── templates/                # Jinja2 HTML templates
    ├── base.html
    ├── login.html
    ├── register.html
    ├── client.html
    └── therapist.html
```

> **Important:**  Model directories are **ignored** in Git.  You will download them separately (see Quick‑Start below).

---

## 📈 Models Used

| Purpose            | Model                                                         | Fine‑Tuning Corpus                                    |
| :----------------- | :------------------------------------------------------------ | :---------------------------------------------------- |
| Summarization      | `journal_summary_model` (T5‑Small)                            | Step‑1 CNN/DailyMail → Step‑2 synthetic therapy notes |
| Sentiment Analysis | `distilbert_emotion_finetuned_full` (DistilBERT‑base‑uncased) | Kaggle tagged journal emotions                        |

---

## 🔗 Training Data Sources

* **CNN/DailyMail summarization** – [https://www.kaggle.com/datasets/gowrishankarp/newspaper-text-summarization-cnn-dailymail](https://www.kaggle.com/datasets/gowrishankarp/newspaper-text-summarization-cnn-dailymail)
* **Synthetic therapy notes (phase‑2)** – see `data/mock_journals.csv` (in repo)
* **Emotion‑labelled journals** – [https://www.kaggle.com/datasets/madhavmalhotra/journal-entries-with-labelled-emotions](https://www.kaggle.com/datasets/madhavmalhotra/journal-entries-with-labelled-emotions)

---

## 🚀 Quick‑Start (Run Locally)

> The following assumes **Python 3.10+** and **pip** are available.

1. **Download the code**   
   Clone or download the entire project directory:

   ```bash
   git clone https://github.com/your‑username/mentis.git
   cd mentis
   ```

2. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Download the fine‑tuned models**

   A shared Google Drive folder (https://drive.google.com/drive/folders/1VziVh0rc2nyd-jfI3xyQ11hohq5CcX7Q?usp=sharing) contains two zipped model folders:

   | Folder on Drive                     | Destination in project       |
   | ----------------------------------- | ---------------------------- |
   | `distilbert_emotion_finetuned_full` | `mentis_sentiment_analysis/` |
   | `journal_summary_model`             | `mentis_summarization/`      |

   After extracting, your tree should look like this:

   ```
   mentis/
   ├── mentis_sentiment_analysis/
   │   └── distilbert_emotion_finetuned_full/
   └── mentis_summarization/
       └── journal_summary_model/
   ```

4. **Launch the Flask app**   
   Open the project in **PyCharm** (or any IDE). Run `app.py`.

   ```bash
   python app.py
   ```

   By default the server starts on **[http://127.0.0.1:5000]**. If you prefer a different port, edit the last line in `app.py`:

   ```python
   app.run(debug=True, port=8000)
   ```

5. **Open your browser** and navigate to the printed local URL (e.g. `http://127.0.0.1:5000`). Register a new account and start journaling! ✨

---

## 🔒 Privacy & Security

* All user data is stored **locally** in CSV files – no external database or cloud service.
* Users may delete their data at any time.
* The application never shares personal information with third parties.

---

## 🙏 Acknowledgements

Developed as part of the **Final Project** at **Afeka College of Engineering**.

**Authors**

* Ohad Buskile
* Ilana Gofman
