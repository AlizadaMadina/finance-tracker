#!/usr/bin/env python3
"""
cli.py — Personal Finance Tracker CLI
Usage: python cli.py <command> [options]
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime


def cmd_import(args):
    from importer import import_csv
    import_csv(
        args.file,
        account=args.account,
        date_col=args.date_col,
        desc_col=args.desc_col,
        amount_col=args.amount_col,
        skip_rows=args.skip,
    )


def cmd_summary(args):
    from analytics import monthly_summary, overall_stats
    stats = overall_stats()
    if not stats.get("total_transactions"):
        print("No data yet. Import a CSV first: python cli.py import <file.csv>")
        return

    print(f"\n{'═'*52}")
    print(f"  📊 FINANCE TRACKER — OVERALL SUMMARY")
    print(f"{'═'*52}")
    print(f"  Transactions : {stats['total_transactions']}")
    print(f"  Date range   : {stats['earliest']} → {stats['latest']}")
    print(f"  Total income : ${stats['total_income']:>10,.2f}")
    print(f"  Total spent  : ${stats['total_spent']:>10,.2f}")
    net = stats['total_income'] - stats['total_spent']
    print(f"  Net          : ${net:>+10,.2f}")
    print(f"{'═'*52}\n")

    print(f"  {'MONTH':<10}  {'INCOME':>10}  {'EXPENSES':>10}  {'NET':>10}  {'TXS':>5}")
    print(f"  {'─'*10}  {'─'*10}  {'─'*10}  {'─'*10}  {'─'*5}")
    for m in monthly_summary():
        net_m = m['net']
        net_str = f"${net_m:>+,.2f}"
        print(f"  {m['month']:<10}  ${m['income']:>9,.2f}  ${m['expenses']:>9,.2f}  {net_str:>10}  {m['tx_count']:>5}")
    print()


def cmd_categories(args):
    from analytics import spending_by_category
    month = args.month
    data = spending_by_category(month)

    label = f"for {month}" if month else "(all time)"
    print(f"\n  🗂  Spending by Category {label}")
    print(f"  {'─'*40}")
    total = sum(d["total"] for d in data)
    for d in data:
        pct = d["total"] / total * 100 if total else 0
        bar = "█" * int(pct / 2)
        print(f"  {d['category']:<22} ${d['total']:>8,.2f}  {pct:5.1f}%  {bar}")
    print(f"  {'─'*40}")
    print(f"  {'TOTAL':<22} ${total:>8,.2f}\n")


def cmd_anomalies(args):
    from analytics import detect_anomalies, monthly_summary

    months = monthly_summary()
    if not months:
        print("No data available.")
        return

    month = args.month or months[-1]["month"]
    anomalies = detect_anomalies(month, lookback_months=args.lookback)

    print(f"\n  🚨 Anomaly Detection — {month}")
    print(f"  {'─'*50}")
    if not anomalies:
        print("  ✅ No significant anomalies detected.\n")
        return

    for a in anomalies:
        icon = "🔴" if a["pct_change"] >= 50 else "🟡"
        print(f"  {icon} {a['category']:<22} +{a['pct_change']:.1f}%")
        print(f"       Current: ${a['current']:,.2f}  |  Avg: ${a['avg_prior']:,.2f}  |  Delta: +${a['delta']:,.2f}")
    print()


def cmd_budget(args):
    from analytics import set_budget, check_budgets, monthly_summary

    if args.budget_cmd == "set":
        set_budget(args.category, args.amount)

    elif args.budget_cmd == "check":
        months = monthly_summary()
        month = args.month or (months[-1]["month"] if months else None)
        if not month:
            print("No data available.")
            return

        budgets = check_budgets(month)
        if not budgets:
            print(f"\n  No budgets set. Use: python cli.py budget set <category> <amount>\n")
            return

        print(f"\n  🎯 Budget Status — {month}")
        print(f"  {'─'*56}")
        print(f"  {'CATEGORY':<22} {'LIMIT':>8}  {'SPENT':>8}  {'REMAINING':>10}  {'%':>6}")
        print(f"  {'─'*56}")
        for b in budgets:
            status = "🔴" if b["over_budget"] else ("🟡" if b["pct_used"] > 80 else "🟢")
            rem = f"${b['remaining']:+,.2f}"
            print(f"  {status} {b['category']:<20} ${b['limit']:>7,.2f}  ${b['spent']:>7,.2f}  {rem:>10}  {b['pct_used']:>5.1f}%")
        print()


def cmd_report(args):
    from report import build_report
    from analytics import monthly_summary

    months = monthly_summary()
    if not months:
        print("No data to report. Import transactions first.")
        return

    month = args.month or months[-1]["month"]
    path = build_report(month)
    print(f"  Open in browser: file://{Path(path).resolve()}")


def cmd_recent(args):
    from analytics import recent_transactions
    txs = recent_transactions(args.limit)
    print(f"\n  📋 Recent Transactions (last {args.limit})")
    print(f"  {'─'*72}")
    print(f"  {'DATE':<12} {'DESCRIPTION':<30} {'CATEGORY':<18} {'AMOUNT':>9}")
    print(f"  {'─'*72}")
    for t in txs:
        amt = f"${t['amount']:>+,.2f}"
        color = amt  # plain text in CLI
        desc = t["description"][:28]
        cat = t["category"][:16]
        print(f"  {t['date']:<12} {desc:<30} {cat:<18} {amt:>9}")
    print()


def cmd_demo(args):
    """Load sample data for demonstration."""
    import csv
    import random
    from pathlib import Path
    from datetime import date, timedelta

    print("  Generating demo transactions...")
    demo_file = Path("data/demo_transactions.csv")
    demo_file.parent.mkdir(exist_ok=True)

    MERCHANTS = [
        ("Safeway Groceries", -80, -200),
        ("Starbucks Coffee", -5, -15),
        ("Netflix", -17, -17),
        ("Uber", -12, -40),
        ("Amazon", -25, -150),
        ("Shoppers Drug Mart", -20, -80),
        ("Restaurant Sushi", -35, -100),
        ("BC Hydro", -80, -120),
        ("Rogers Internet", -75, -75),
        ("Gym Membership", -50, -50),
        ("McDonald's", -8, -20),
        ("London Drugs", -15, -60),
        ("Spotify", -10, -10),
        ("Skip The Dishes", -25, -60),
        ("Tim Hortons", -3, -8),
    ]

    start = date(2024, 1, 1)
    end = date(2024, 12, 31)
    delta = end - start

    rows = [["Date", "Description", "Amount", "Account"]]
    salary_dates = []
    d = start
    while d <= end:
        if d.day == 15 or d.day == 30:
            salary_dates.append(d)
        d += timedelta(days=1)

    for pay_date in salary_dates:
        rows.append([pay_date.isoformat(), "Payroll Direct Deposit", "2750.00", "Chequing"])

    random.seed(42)
    for _ in range(280):
        day_offset = random.randint(0, delta.days)
        tx_date = start + timedelta(days=day_offset)
        merchant, lo, hi = random.choice(MERCHANTS)
        amount = round(random.uniform(lo, hi), 2)
        rows.append([tx_date.isoformat(), merchant, str(amount), "Chequing"])

    with open(demo_file, "w", newline="") as f:
        csv.writer(f).writerows(rows)

    print(f"  Demo CSV created: {demo_file}")
    from importer import import_csv
    import_csv(str(demo_file), account="Demo Chequing")
    print("\n  ✅ Demo data loaded! Try:")
    print("     python cli.py summary")
    print("     python cli.py report")
    print("     python cli.py anomalies")


def main():
    parser = argparse.ArgumentParser(
        prog="finance-tracker",
        description="Personal Finance Tracker & Spending Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py demo                          Load sample data
  python cli.py import bank.csv               Import transactions
  python cli.py summary                       Monthly overview
  python cli.py categories --month 2024-03    Spending by category
  python cli.py anomalies --month 2024-03     Detect unusual spending
  python cli.py budget set Food 400           Set a budget
  python cli.py budget check                  Check budget status
  python cli.py report --month 2024-03        Generate HTML report
  python cli.py recent --limit 30             Recent transactions
        """,
    )
    sub = parser.add_subparsers(dest="command")

    # import
    p_import = sub.add_parser("import", help="Import transactions from CSV")
    p_import.add_argument("file", help="Path to CSV file")
    p_import.add_argument("--account", default="Default", help="Account name")
    p_import.add_argument("--date-col", type=int, default=None, dest="date_col")
    p_import.add_argument("--desc-col", type=int, default=None, dest="desc_col")
    p_import.add_argument("--amount-col", type=int, default=None, dest="amount_col")
    p_import.add_argument("--skip", type=int, default=0, help="Skip N rows before header")

    # summary
    sub.add_parser("summary", help="Monthly income/expense overview")

    # categories
    p_cat = sub.add_parser("categories", help="Spending breakdown by category")
    p_cat.add_argument("--month", help="YYYY-MM filter")

    # anomalies
    p_ano = sub.add_parser("anomalies", help="Detect unusual spending")
    p_ano.add_argument("--month", help="YYYY-MM (default: latest)")
    p_ano.add_argument("--lookback", type=int, default=3, help="Months to compare against")

    # budget
    p_bud = sub.add_parser("budget", help="Manage budgets")
    bud_sub = p_bud.add_subparsers(dest="budget_cmd")
    p_bud_set = bud_sub.add_parser("set")
    p_bud_set.add_argument("category")
    p_bud_set.add_argument("amount", type=float)
    p_bud_chk = bud_sub.add_parser("check")
    p_bud_chk.add_argument("--month", help="YYYY-MM (default: latest)")

    # report
    p_rep = sub.add_parser("report", help="Generate HTML monthly report")
    p_rep.add_argument("--month", help="YYYY-MM (default: latest)")

    # recent
    p_rec = sub.add_parser("recent", help="Show recent transactions")
    p_rec.add_argument("--limit", type=int, default=20)

    # demo
    sub.add_parser("demo", help="Load sample data to explore the tool")

    args = parser.parse_args()

    dispatch = {
        "import": cmd_import,
        "summary": cmd_summary,
        "categories": cmd_categories,
        "anomalies": cmd_anomalies,
        "budget": cmd_budget,
        "report": cmd_report,
        "recent": cmd_recent,
        "demo": cmd_demo,
    }

    if args.command in dispatch:
        dispatch[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
