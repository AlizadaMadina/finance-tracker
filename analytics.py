"""
analytics.py - Spending insights, trends, and anomaly detection engine
"""

from database import get_connection
from collections import defaultdict
import json


# Core Query Helpers

def spending_by_category(month: str = None) -> list[dict]:
    """
    Total spending per category.
    month format: 'YYYY-MM' (optional filter)
    Returns expenses only (amount < 0).
    """
    conn = get_connection()
    if month:
        rows = conn.execute("""
            SELECT category,
                   ROUND(SUM(ABS(amount)), 2) AS total,
                   COUNT(*) AS tx_count
            FROM transactions
            WHERE amount < 0
              AND strftime('%Y-%m', date) = ?
            GROUP BY category
            ORDER BY total DESC
        """, (month,)).fetchall()
    else:
        rows = conn.execute("""
            SELECT category,
                   ROUND(SUM(ABS(amount)), 2) AS total,
                   COUNT(*) AS tx_count
            FROM transactions
            WHERE amount < 0
            GROUP BY category
            ORDER BY total DESC
        """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def monthly_summary() -> list[dict]:
    """Income vs expenses vs net by month."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT strftime('%Y-%m', date) AS month,
               ROUND(SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END), 2) AS income,
               ROUND(SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END), 2) AS expenses,
               ROUND(SUM(amount), 2) AS net,
               COUNT(*) AS tx_count
        FROM transactions
        GROUP BY month
        ORDER BY month
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def top_merchants(month: str = None, limit: int = 10) -> list[dict]:
    """Top spending merchants/descriptions."""
    conn = get_connection()
    where = "WHERE amount < 0 AND strftime('%Y-%m', date) = ?" if month else "WHERE amount < 0"
    params = (month,) if month else ()
    rows = conn.execute(f"""
        SELECT description,
               ROUND(SUM(ABS(amount)), 2) AS total,
               COUNT(*) AS visits
        FROM transactions
        {where}
        GROUP BY description
        ORDER BY total DESC
        LIMIT {limit}
    """, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def recent_transactions(limit: int = 20) -> list[dict]:
    """Most recent transactions."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT date, description, amount, category, account
        FROM transactions
        ORDER BY date DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def daily_spending(month: str) -> list[dict]:
    """Day-by-day spending for a given month."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT date,
               ROUND(SUM(ABS(amount)), 2) AS spent
        FROM transactions
        WHERE amount < 0
          AND strftime('%Y-%m', date) = ?
        GROUP BY date
        ORDER BY date
    """, (month,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# Anomaly Detection

def detect_anomalies(current_month: str, lookback_months: int = 3) -> list[dict]:
    """
    Compare current month's category spending vs prior N-month average.
    Flags categories where spending increased by >= 25%.
    Returns list of anomaly dicts with context.
    """
    conn = get_connection()

    # Get all months in DB
    all_months = [
        r[0] for r in conn.execute(
            "SELECT DISTINCT strftime('%Y-%m', date) FROM transactions ORDER BY 1"
        ).fetchall()
    ]

    if current_month not in all_months:
        conn.close()
        return []

    idx = all_months.index(current_month)
    prior_months = all_months[max(0, idx - lookback_months):idx]

    if not prior_months:
        conn.close()
        return []

    # Current month spending by category
    current_rows = conn.execute("""
        SELECT category, ROUND(SUM(ABS(amount)), 2) AS total
        FROM transactions
        WHERE amount < 0 AND strftime('%Y-%m', date) = ?
        GROUP BY category
    """, (current_month,)).fetchall()
    current = {r["category"]: r["total"] for r in current_rows}

    # Prior months average by category
    placeholders = ",".join("?" * len(prior_months))
    prior_rows = conn.execute(f"""
        SELECT category,
               ROUND(SUM(ABS(amount)) / ?, 2) AS avg_total
        FROM transactions
        WHERE amount < 0
          AND strftime('%Y-%m', date) IN ({placeholders})
        GROUP BY category
    """, [len(prior_months)] + prior_months).fetchall()
    prior = {r["category"]: r["avg_total"] for r in prior_rows}

    conn.close()

    anomalies = []
    THRESHOLD = 0.25  # 25% increase triggers a flag

    for category, curr_amount in current.items():
        avg = prior.get(category, 0)
        if avg == 0:
            continue  # New category, skip
        pct_change = (curr_amount - avg) / avg
        if pct_change >= THRESHOLD:
            anomalies.append({
                "category": category,
                "current": curr_amount,
                "avg_prior": avg,
                "pct_change": round(pct_change * 100, 1),
                "delta": round(curr_amount - avg, 2),
            })

    anomalies.sort(key=lambda x: x["pct_change"], reverse=True)
    return anomalies


#  Budget Checking

def check_budgets(month: str) -> list[dict]:
    """Compare actual spending vs budgets for a given month."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT b.category,
               b.monthly_limit,
               COALESCE(ROUND(SUM(ABS(t.amount)), 2), 0) AS spent
        FROM budgets b
        LEFT JOIN transactions t
               ON t.category = b.category
              AND t.amount < 0
              AND strftime('%Y-%m', t.date) = ?
        GROUP BY b.category, b.monthly_limit
        ORDER BY (spent / b.monthly_limit) DESC
    """, (month,)).fetchall()
    conn.close()

    results = []
    for r in rows:
        pct = (r["spent"] / r["monthly_limit"] * 100) if r["monthly_limit"] else 0
        results.append({
            "category": r["category"],
            "limit": r["monthly_limit"],
            "spent": r["spent"],
            "remaining": round(r["monthly_limit"] - r["spent"], 2),
            "pct_used": round(pct, 1),
            "over_budget": r["spent"] > r["monthly_limit"],
        })
    return results


def set_budget(category: str, monthly_limit: float):
    """Upsert a budget limit for a category."""
    conn = get_connection()
    conn.execute("""
        INSERT INTO budgets (category, monthly_limit)
        VALUES (?, ?)
        ON CONFLICT(category) DO UPDATE SET monthly_limit = excluded.monthly_limit
    """, (category, monthly_limit))
    conn.commit()
    conn.close()
    print(f"✅ Budget set: {category} → ${monthly_limit:.2f}/month")


# Stats

def overall_stats() -> dict:
    conn = get_connection()
    r = conn.execute("""
        SELECT COUNT(*) AS total_transactions,
               MIN(date) AS earliest,
               MAX(date) AS latest,
               ROUND(SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END), 2) AS total_spent,
               ROUND(SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END), 2) AS total_income
        FROM transactions
    """).fetchone()
    conn.close()
    return dict(r) if r else {}


if __name__ == "__main__":
    from pprint import pprint
    print("\n── Monthly Summary ──")
    pprint(monthly_summary())
    print("\n── Top Categories (all time) ──")
    pprint(spending_by_category())
    print("\n── Overall Stats ──")
    pprint(overall_stats())
