# FinanceIQ - Personal Finance Tracker and Spending Analyzer

A web app that takes your bank CSV file and gives you a visual breakdown of your spending, detects unusual expenses, and uses a machine learning model to automatically label your transactions.

Built this as a personal project to actually understand where my money goes every month.

[![CI](https://github.com/AlizadaMadina/finance-tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/AlizadaMadina/finance-tracker/actions)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## Live Demo

Try it here: [https://finance-tracker-w5zt.onrender.com](https://finance-tracker-w5zt.onrender.com)

Just upload your bank CSV and it will analyze your spending instantly. No account needed, no data stored.

Note: The free server sleeps after inactivity so the first load might take 30 seconds.

---

## What it does

- Upload any bank CSV file (Scotiabank, TD, RBC, etc.) and get a spending dashboard instantly
- Automatically categorizes transactions using a ML model trained on 8,000 Canadian transactions
- Detects spending anomalies, for example if you spent 40% more on food this month vs your average
- Shows spending by category, daily spending, monthly income vs expenses trend
- Works from the browser, no code needed

---

## How the ML model works

Instead of manually writing rules like "if description contains uber then category is transport", I trained a real classification model.

The model uses TF-IDF to convert transaction descriptions into numbers, then Logistic Regression to predict the category. It was trained on 8,000 synthetic Canadian transactions I generated with real merchant names (Tim Hortons, Safeway, Aritzia, Translink, etc.) and tested on my real Scotiabank data.

Results on real bank data:
- Overall accuracy: 85%
- Transport: 100%
- Groceries: 100%
- Healthcare: 100%
- Food: 88% F1-score
- Shopping: 55% F1-score (hardest category)

The model is saved as model.pkl and loaded when the web app starts. Every uploaded CSV gets categorized automatically.

---

## Running locally

```bash
git clone https://github.com/AlizadaMadina/finance-tracker.git
cd finance-tracker
pip install -r requirements.txt
python app.py
```

Then go to http://localhost:8000 in your browser.

To retrain the ML model from scratch:

```bash
python generate_data.py
python train_model.py
```

---

## CLI commands

If you prefer the terminal over the web app:

```bash
python cli.py demo                          # load sample data
python cli.py import transactions.csv       # import your CSV
python cli.py summary                       # monthly overview
python cli.py categories --month 2026-04   # spending by category
python cli.py anomalies                     # detect unusual spending
python cli.py budget set Food 400          # set a budget
python cli.py budget check                 # check budget status
python cli.py report                       # generate HTML report
```

---

## Project structure

finance-tracker/
├── app.py               # Flask web server
├── cli.py               # command line interface
├── database.py          # SQLite schema and connection
├── importer.py          # CSV parser and categorizer
├── analytics.py         # SQL queries and anomaly detection
├── report.py            # HTML report generator
├── generate_data.py     # generates synthetic Canadian training data
├── train_model.py       # trains and saves the ML model
├── model.pkl            # saved trained model
├── templates/
│   └── index.html       # web app frontend
├── tests/
│   └── test_core.py     # test suite
└── data/                # database and CSV files
---

## Tech stack

- Python, Flask, SQLite
- scikit-learn (TF-IDF + Logistic Regression)
- pandas for data processing
- Chart.js for the dashboard charts
- GitHub Actions for CI
- Render for deployment

---

## What I learned

- How to design a SQL database and write aggregate queries
- How to build and train a text classification model
- The difference between in-distribution and out-of-distribution accuracy (my model got 99% on the synthetic test set but 85% on real data, which taught me a lot about overfitting)
- How to build a full stack web app and deploy it

---

## Roadmap

- PDF export of monthly reports
- Support for multi-currency transactions
- Better handling of chequing account data where banks use vague descriptions

---

## License

MIT

---

## Author

Madina Alizada