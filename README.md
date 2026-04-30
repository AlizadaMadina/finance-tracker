# 💰 Personal Finance Tracker & Spending Analyzer

> Import your bank transactions, detect spending anomalies, and get a beautiful monthly HTML report — all from the command line.

[![CI](https://github.com/YOUR_USERNAME/finance-tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/finance-tracker/actions)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## What It Does

This is not just another expense logger. The core value is the **insights engine**:

- 📥 **Smart CSV Import** — Auto-detects column names from any major bank export format
- 🗂 **Auto-Categorization** — 15+ keyword rules (Groceries, Transport, Subscriptions, etc.)
- 🚨 **Anomaly Detection** — Flags categories where you spent significantly more than your rolling average
- 🎯 **Budget Tracking** — Set monthly limits per category, track progress
- 📊 **HTML Reports** — Auto-generated monthly reports with interactive charts (donut, trend, daily)
- 🔍 **SQL-Powered Analytics** — All data lives in a local SQLite file you fully own

---

## Quick Start

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
#    → Opens: reports/report_2024-12.html
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

**Supported formats include:**
- TD Bank, RBC, BMO, Scotiabank, CIBC, Tangerine
- Chase, Bank of America, Wells Fargo
- Any CSV with date / description / amount columns

---

## Commands

| Command | Description |
|---|---|
| `python cli.py demo` | Load ~300 sample transactions |
| `python cli.py import <file.csv>` | Import transactions from CSV |
| `python cli.py summary` | Month-by-month income/expense table |
| `python cli.py categories --month 2024-03` | Spending breakdown by category |
| `python cli.py anomalies --month 2024-03` | Detect unusual spending vs prior months |
| `python cli.py budget set Groceries 400` | Set a monthly budget |
| `python cli.py budget check` | Check all budget statuses |
| `python cli.py report --month 2024-03` | Generate HTML report |
| `python cli.py recent --limit 30` | Show recent transactions |

---

## Example: Anomaly Detection

```
🚨 Anomaly Detection — 2024-03
──────────────────────────────────────────────────
🔴 Food & Dining          +72.3%
     Current: $428.50  |  Avg: $248.90  |  Delta: +$179.60
🟡 Shopping               +38.1%
     Current: $312.00  |  Avg: $226.00  |  Delta: +$86.00
```

Anomalies are detected by comparing the current month against the rolling N-month average (default: 3 months). Any category up 25%+ is flagged.

---

## Example: Monthly Summary

```
══════════════════════════════════════════════════════
  MONTH       INCOME      EXPENSES         NET    TXS
  ──────────  ──────────  ──────────  ──────────  ─────
  2024-01    $5,500.00   $3,821.30   +$1,678.70     48
  2024-02    $5,500.00   $4,102.80   +$1,397.20     52
  2024-03    $5,500.00   $4,480.50   +$1,019.50     61
```

---

## Project Structure

```
finance-tracker/
├── cli.py            # Main CLI entry point
├── database.py       # SQLite schema & connection
├── importer.py       # CSV parser + auto-categorizer
├── analytics.py      # SQL queries, anomaly detection, budgets
├── report.py         # HTML report generator
├── requirements.txt
├── tests/
│   └── test_core.py  # Pytest test suite (9 tests)
├── data/             # SQLite DB lives here (gitignored)
└── reports/          # Generated HTML reports (gitignored)
```

---

## Customizing Categories

Category rules are stored in the `category_rules` table. You can add custom rules:

```python
from database import get_connection
conn = get_connection()
conn.execute("INSERT INTO category_rules (keyword, category) VALUES (?, ?)", 
             ("whole foods|t&t|choices", "Groceries"))
conn.commit()
```

Or re-categorize a transaction manually:
```sql
-- In any SQLite client:
UPDATE transactions SET category = 'Healthcare' WHERE description LIKE '%Shoppers%';
```

---

## Running Tests

```bash
pytest tests/ -v
# 9 passed in 0.55s
```

Tests cover: CSV parsing, date formats, amount parsing, categorization, spending analytics, anomaly detection, and budget checking — all against an in-memory test database.

---

## Skills You'll Build

Working through this project teaches:

- **Python**: CSV parsing, date handling, dataclasses, argparse CLI design
- **SQL / SQLite**: Aggregate queries (`SUM`, `GROUP BY`, `CASE WHEN`), window functions, upserts
- **Data Analysis**: Rolling averages, percentage change, anomaly thresholds
- **HTML Report Generation**: Templating, Chart.js integration, responsive design
- **Software Engineering**: Separation of concerns, test fixtures, CI/CD with GitHub Actions

---

## Roadmap Ideas

- [ ] Web dashboard (Flask/FastAPI) instead of CLI-only
- [ ] PDF export using `weasyprint`
- [ ] Plaid API integration for automatic bank sync
- [ ] Email delivery of monthly reports
- [ ] Multi-currency support

---

## License

MIT — use freely, no warranties.
