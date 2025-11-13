# Smartphone Sales AI Agent

[![Streamlit](https://img.shields.io/badge/Streamlit-%23FF4B4B?style=for-the-badge\&logo=streamlit)](#) [![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge\&logo=python)](#)

A beautiful, polished Streamlit app that turns a local smartphone sales dataset into an AI-powered question-answering interface. Ask natural‑language questions and the app translates them into safe SQL queries run against a local SQLite database — then shows results, explanations, and charts.

---
# https://huggingface.co/spaces/SanjarBS/itpu-capstone1

## ✨ Highlights

* **Natural-language SQL**: Ask questions like *"Phones under $500"* or *"Top 5 by battery life"* and get instant results.
* **Safety-first execution**: Uses parameterized queries and whitelist checks before running any generated SQL against your local DB.
* **Interactive UI**: Dataset overview, sample rows, schema, stats, charts and a chat-like assistant experience.
* **Correction hints**: If the LLM guesses a wrong column name, the UI offers AI-suggested corrections.
* **Optional support tickets**: Create GitHub issues automatically (optional — requires GitHub token in secrets).

---

## 🧭 Project structure

```
capstone1/
├─ .streamlit/
│  └─ secrets.toml        # (optional) GITHUB_TOKEN, GITHUB_REPO
├─ src/
│  ├─ app.py              # Streamlit app
│  ├─ seed_db.py          # CSV → SQLite helper
│  └─ "Mobiles Dataset (2025).csv"
├─ requirements.txt
└─ README.md
```

---

## 🚀 Quick start

1. Clone the repo:

```bash
git clone https://github.com/yourusername/capstone1.git
cd capstone1
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. (Optional) Add GitHub secrets for support tickets:

Create `.streamlit/secrets.toml` with:

```toml
GITHUB_TOKEN = "ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
GITHUB_REPO  = "your-username/your-repo-name"
```

4. Start the app:

```bash
streamlit run src/app.py
```
---

## 🖼 Example usage

Try these prompts in the app's chat box:

* `Phones under $500`
* `Top 5 phones by battery capacity`
* `Show average price by brand`
* `Which models were released after 2023?`

The assistant will display the generated SQL, the results, and a short explanation.

---

## 📸 Screenshots

<img width="1903" height="956" alt="1" src="https://github.com/user-attachments/assets/203022b7-9719-4bf1-9549-e450a8e07f5e" />

<img width="1907" height="956" alt="2" src="https://github.com/user-attachments/assets/b9221497-e47a-4d67-92ec-c36e6383df39" />

<img width="1902" height="953" alt="3" src="https://github.com/user-attachments/assets/61e55367-1489-4581-96f5-a825ffe1d734" />

<img width="1900" height="957" alt="4" src="https://github.com/user-attachments/assets/34a262cc-f82b-4b05-8721-8b7ddb0e2a7f" />

<img width="1906" height="958" alt="5" src="https://github.com/user-attachments/assets/5c3bf4d1-c8b3-400b-b094-20bf044f88c2" />


