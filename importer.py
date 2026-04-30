"""
importer.py — CSV transaction importer with auto-categorization
Supports common bank export formats (date, description, amount columns).
"""

import csv
import re
from pathlib import Path
from datetime import datetime
from database import get_connection, init_db

# Default keyword → category rules
DEFAULT_RULES = [
    ("uber|lyft|taxi|transit|bus|skytrain|translink", "Transport"),
    ("netflix|spotify|disney|hulu|youtube premium|apple tv", "Subscriptions"),
    ("amazon|shopify|ebay|etsy|walmart|costco|best buy", "Shopping"),
    ("grocery|safeway|whole foods|superstore|t&t|save-on|loblaws", "Groceries"),
    ("restaurant|mcdonald|pizza|sushi|burger|cafe|coffee|tim horton|starbucks|skip|doordash|uber eats", "Food & Dining"),
    ("hydro|hydro one|bc hydro|enmax|atco|gas|utilities|bell|telus|rogers|shaw|internet", "Utilities"),
    ("rent|mortgage|strata|property", "Housing"),
    ("gym|fitness|sport|yoga|peloton", "Health & Fitness"),
    ("pharmacy|drug|shoppers|london drugs|clinic|doctor|dentist|medical", "Healthcare"),
    ("insurance|manulife|sunlife|great-west|wawanesa", "Insurance"),
    ("salary|payroll|direct deposit|paycheck|employment insurance", "Income"),
    ("atm|withdrawal|cash", "Cash"),
    ("transfer|e-transfer|interac", "Transfers"),
    ("interest|service fee|bank fee|nsf|overdraft", "Bank Fees"),
]


def seed_rules():
    """Insert default category rules into DB (skip if already exist)."""
    conn = get_connection()
    existing = conn.execute("SELECT COUNT(*) FROM category_rules").fetchone()[0]
    if existing == 0:
        for keyword, category in DEFAULT_RULES:
            conn.execute(
                "INSERT INTO category_rules (keyword, category) VALUES (?, ?)",
                (keyword, category),
            )
        conn.commit()
        print(f"  Seeded {len(DEFAULT_RULES)} category rules.")
    conn.close()


def categorize(description: str, conn) -> str:
    """Match description against DB rules (case-insensitive regex)."""
    rules = conn.execute("SELECT keyword, category FROM category_rules").fetchall()
    desc_lower = description.lower()
    for rule in rules:
        if re.search(rule["keyword"], desc_lower):
            return rule["category"]
    return "Uncategorized"


def detect_columns(header: list[str]) -> dict:
    """
    Try to auto-detect date/description/amount columns from header names.
    Returns a dict with keys: date_col, desc_col, amount_col (indices).
    """
    header_lower = [h.lower().strip() for h in header]

    date_candidates = ["date", "transaction date", "posted date", "trans date"]
    desc_candidates = ["description", "details", "merchant", "payee", "memo", "narration"]
    amount_candidates = ["amount", "debit", "credit", "transaction amount", "cad$"]

    def find(candidates):
        for c in candidates:
            for i, h in enumerate(header_lower):
                if c in h:
                    return i
        return None

    date_col = find(date_candidates)
    desc_col = find(desc_candidates)
    amount_col = find(amount_candidates)

    if None in (date_col, desc_col, amount_col):
        raise ValueError(
            f"Could not detect columns. Header: {header}\n"
            "Use --date, --desc, --amount flags to specify column indices."
        )
    return {"date": date_col, "desc": desc_col, "amount": amount_col}


def parse_amount(raw: str) -> float:
    """Handle formats like '$1,234.56', '-$500', '(200.00)' (negative bracket notation)."""
    raw = raw.strip().replace(",", "").replace("$", "").replace(" ", "")
    negative = raw.startswith("(") and raw.endswith(")")
    raw = raw.strip("()")
    amount = float(raw)
    return -abs(amount) if negative else amount


def parse_date(raw: str) -> str:
    """Try common date formats, return ISO 8601 (YYYY-MM-DD)."""
    formats = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%m-%d-%Y", "%d-%m-%Y",
               "%Y/%m/%d", "%b %d, %Y", "%B %d, %Y", "%d %b %Y"]
    raw = raw.strip()
    for fmt in formats:
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: '{raw}'")


def import_csv(
    filepath: str,
    account: str = "Default",
    date_col: int = None,
    desc_col: int = None,
    amount_col: int = None,
    skip_rows: int = 0,
    encoding: str = "utf-8-sig",
) -> int:
    """
    Import transactions from a CSV file.
    Returns the number of rows inserted.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    init_db()
    seed_rules()
    conn = get_connection()

    inserted = 0
    skipped = 0

    with open(path, newline="", encoding=encoding) as f:
        reader = csv.reader(f)

        for _ in range(skip_rows):
            next(reader, None)

        header = next(reader)

        # Use provided indices or auto-detect
        if None in (date_col, desc_col, amount_col):
            cols = detect_columns(header)
            date_col = cols["date"]
            desc_col = cols["desc"]
            amount_col = cols["amount"]

        print(f"  Columns → date[{date_col}] desc[{desc_col}] amount[{amount_col}]")

        for row_num, row in enumerate(reader, start=2):
            if len(row) <= max(date_col, desc_col, amount_col):
                skipped += 1
                continue
            try:
                date = parse_date(row[date_col])
                description = row[desc_col].strip()
                amount = parse_amount(row[amount_col])
                category = categorize(description, conn)

                conn.execute(
                    """INSERT INTO transactions (date, description, amount, category, account)
                       VALUES (?, ?, ?, ?, ?)""",
                    (date, description, amount, category, account),
                )
                inserted += 1
            except Exception as e:
                print(f"  ⚠️  Row {row_num} skipped: {e}")
                skipped += 1

    conn.commit()
    conn.close()
    print(f"✅ Imported {inserted} transactions ({skipped} skipped) from '{path.name}'")
    return inserted


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python importer.py <path/to/transactions.csv> [account_name]")
        sys.exit(1)
    account = sys.argv[2] if len(sys.argv) > 2 else "Default"
    import_csv(sys.argv[1], account=account)
