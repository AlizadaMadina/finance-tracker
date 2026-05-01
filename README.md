# 💰 FinanceIQ — Personal Finance Tracker & Spending Analyzer

> Upload your bank transactions, detect spending anomalies, and get a beautiful dashboard — all in your browser or from the command line.

[![CI](https://github.com/AlizadaMadina/finance-tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/AlizadaMadina/finance-tracker/actions)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## What It Does

This is not just another expense logger. The core value is the **insights engine**:

- 📥 **Smart CSV Import** — Auto-detects column names from any major bank export format
- 🗂 **Auto-Categorization** — 15+ keyword rules (Groceries, Transport, Subscriptions, etc.)
- 🚨 **Anomaly Detection** — Flags categories where you spent significantly more than your rolling average
- 🎯 **Budget Tracking** — Set monthly limits per category, track progress
- 📊 **Beautiful Web Dashboard** — Upload your CSV and see interactive charts instantly
- 📈 **HTML Reports** — Auto-generated monthly reports with charts
- 🔍 **SQL-Powered Analytics** — All data lives in a local SQLite file you fully own

---

## Running the Web App

```bash
python app.py
```

Then open your browser and go to:
http://localhost:8000

Upload your bank CSV file, click **Analyze my spending** and see your full dashboard instantly — no code needed!

---

## Quick Start (CLI)

```bash
# 1. Clone and install
git clone https://github.com/YOUR_USERNAME/finance-tracker.git
cd finance-tracker
pip install -r requirements.txt

# 2. Load demo data to explore
python cli.py demo

# 3. See your overview
python cli.py summary

# 4. Generate a report
python cli.py report
```

---

## Importing Your Own Data

Most banks let you export transactions as CSV (look for "Download" or "Export" in your banking portal).

```bash
# Auto-detect columns (works with most bank exports)
python cli.py import ~/Downloads/transactions.csv --account "TD Chequing"

# If auto-detect fails, specify column indices manually (0-indexed)
python cli.py import ~/Downloads/export.csv --date-col 0 --desc-col 2 --amount-col 4
```

**Supported banks:**
- Scotiabank, TD, RBC, BMO, CIBC, Tangerine
- Chase, Bank of America, Wells Fargo
- Any CSV with date / description / amount columns

---

## CLI Commands

| Command | Description |
|---|---|
| `python cli.py demo` | Load sample transactions |
| `python cli.py import <file.csv>` | Import transactions from CSV |
| `python cli.py summary` | Month-by-month income/expense table |
| `python cli.py categories --month 2024-03` | Spending breakdown by category |
| `python cli.py anomalies --month 2024-03` | Detect unusual spending vs prior months |
| `python cli.py budget set Groceries 400` | Set a monthly budget |
| `python cli.py budget check` | Check all budget statuses |
| `python cli.py report --month 2024-03` | Generate HTML report |
| `python cli.py recent --limit 30` | Show recent transactions |

---

## Project Structure

finance-tracker/
├── app.py            # Flask web server
├── cli.py            # CLI entry point
├── database.py       # SQLite schema and connection
├── importer.py       # CSV parser and auto-categorizer
├── analytics.py      # SQL queries, anomaly detection, budgets
├── report.py         # HTML report generator
├── templates/
│   └── index.html    # Web app frontend
├── requirements.txt
├── tests/
│   └── test_core.py  # Pytest test suite
├── data/             # SQLite DB lives here (gitignored)
└── reports/          # Generated HTML reports (gitignored)

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Skills & Technologies

- **Python** — CSV parsing, Flask web framework, argparse CLI
- **SQL / SQLite** — Aggregate queries, window functions, upserts
- **Data Analysis** — Rolling averages, anomaly detection, spending trends
- **Frontend** — HTML, CSS, JavaScript, Chart.js
- **Software Engineering** — Separation of concerns, testing, CI/CD with GitHub Actions

---

## Roadmap

- [ ] AI-powered auto-categorization using Claude API
- [ ] PDF export of monthly reports
- [ ] Multi-currency support
- [ ] Deploy to web so anyone can use it online

---

## License

MIT — use freely, no warranties.


---

## Author

Madina Alizada
