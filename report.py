"""
report.py — Auto-generate a HTML monthly finance report
"""

import os
import json
from datetime import datetime
from pathlib import Path
from analytics import (
    spending_by_category,
    monthly_summary,
    top_merchants,
    detect_anomalies,
    check_budgets,
    overall_stats,
    daily_spending,
)

REPORTS_DIR = Path("reports")


def generate_color_palette(n: int) -> list[str]:
    """Generate n distinct colors."""
    colors = [
        "#6366f1", "#f59e0b", "#10b981", "#ef4444", "#3b82f6",
        "#ec4899", "#14b8a6", "#f97316", "#8b5cf6", "#84cc16",
        "#06b6d4", "#e11d48", "#d97706", "#059669", "#7c3aed",
    ]
    return [colors[i % len(colors)] for i in range(n)]


def build_report(month: str, output_path: Path = None) -> Path:
    """
    Build an HTML report for the given month (YYYY-MM).
    Returns the path to the saved file.
    """
    REPORTS_DIR.mkdir(exist_ok=True)
    if output_path is None:
        output_path = REPORTS_DIR / f"report_{month}.html"

    # Gather data
    categories = spending_by_category(month)
    monthly = monthly_summary()
    merchants = top_merchants(month, limit=8)
    anomalies = detect_anomalies(month)
    budgets = check_budgets(month)
    stats = overall_stats()
    daily = daily_spending(month)

    # Format month label
    try:
        month_label = datetime.strptime(month, "%Y-%m").strftime("%B %Y")
    except ValueError:
        month_label = month

    # Current month totals
    curr = next((m for m in monthly if m["month"] == month), {})
    income = curr.get("income", 0)
    expenses = curr.get("expenses", 0)
    net = curr.get("net", 0)

    # Chart data
    cat_labels = json.dumps([c["category"] for c in categories])
    cat_values = json.dumps([c["total"] for c in categories])
    cat_colors = json.dumps(generate_color_palette(len(categories)))

    monthly_labels = json.dumps([m["month"] for m in monthly])
    monthly_income = json.dumps([m["income"] for m in monthly])
    monthly_expenses = json.dumps([m["expenses"] for m in monthly])

    daily_labels = json.dumps([d["date"] for d in daily])
    daily_values = json.dumps([d["spent"] for d in daily])

    # Anomaly cards HTML
    anomaly_html = ""
    if anomalies:
        for a in anomalies:
            severity = "high" if a["pct_change"] >= 50 else "medium"
            anomaly_html += f"""
            <div class="anomaly-card {severity}">
                <div class="anomaly-icon">{"🔴" if severity == "high" else "🟡"}</div>
                <div class="anomaly-body">
                    <strong>{a["category"]}</strong>
                    <span>+{a["pct_change"]}% vs prior avg</span>
                    <small>Spent ${a["current"]:,.2f} vs avg ${a["avg_prior"]:,.2f} (+${a["delta"]:,.2f})</small>
                </div>
            </div>"""
    else:
        anomaly_html = '<p class="no-data">✅ No spending anomalies detected this month.</p>'

    # Budget rows HTML
    budget_html = ""
    if budgets:
        for b in budgets:
            bar_class = "over" if b["over_budget"] else ("warn" if b["pct_used"] > 80 else "ok")
            budget_html += f"""
            <div class="budget-row">
                <div class="budget-label">
                    <span>{b["category"]}</span>
                    <span>${b["spent"]:,.2f} / ${b["limit"]:,.2f}</span>
                </div>
                <div class="budget-bar-track">
                    <div class="budget-bar {bar_class}" style="width: {min(b["pct_used"], 100):.1f}%"></div>
                </div>
                <div class="budget-pct {"over-text" if b["over_budget"] else ""}">{b["pct_used"]}%</div>
            </div>"""
    else:
        budget_html = '<p class="no-data">No budgets set. Use <code>python cli.py budget set &lt;category&gt; &lt;amount&gt;</code></p>'

    # Top merchants HTML
    merchants_html = ""
    for m in merchants:
        merchants_html += f"""
        <div class="merchant-row">
            <span class="merchant-name">{m["description"]}</span>
            <span class="merchant-visits">{m["visits"]}×</span>
            <span class="merchant-total">${m["total"]:,.2f}</span>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Finance Report — {month_label}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  :root {{
    --bg: #0f0f13;
    --surface: #18181f;
    --surface2: #22222e;
    --border: #2e2e3e;
    --text: #e8e8f0;
    --muted: #8888a8;
    --accent: #6366f1;
    --green: #10b981;
    --red: #ef4444;
    --yellow: #f59e0b;
    --radius: 12px;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: 'Segoe UI', system-ui, sans-serif; min-height: 100vh; }}

  header {{
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-bottom: 1px solid var(--border);
    padding: 2.5rem 3rem;
    display: flex; justify-content: space-between; align-items: flex-end;
  }}
  header h1 {{ font-size: 2rem; font-weight: 700; }}
  header h1 span {{ color: var(--accent); }}
  header p {{ color: var(--muted); font-size: 0.9rem; margin-top: 0.25rem; }}
  .generated {{ color: var(--muted); font-size: 0.8rem; }}

  main {{ max-width: 1200px; margin: 0 auto; padding: 2rem 1.5rem; }}

  .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
  .kpi-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
  }}
  .kpi-label {{ font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; }}
  .kpi-value {{ font-size: 1.75rem; font-weight: 700; }}
  .kpi-value.income {{ color: var(--green); }}
  .kpi-value.expense {{ color: var(--red); }}
  .kpi-value.net {{ color: {"var(--green)" if net >= 0 else "var(--red)"}; }}

  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem; }}
  @media (max-width: 768px) {{ .grid-2 {{ grid-template-columns: 1fr; }} }}

  .card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
  }}
  .card h2 {{ font-size: 1rem; font-weight: 600; margin-bottom: 1.25rem; color: var(--text); display: flex; align-items: center; gap: 0.5rem; }}
  .card canvas {{ max-height: 260px; }}

  .wide {{ grid-column: 1 / -1; }}

  .anomaly-card {{
    display: flex; align-items: flex-start; gap: 0.75rem;
    padding: 0.875rem;
    border-radius: 8px;
    margin-bottom: 0.5rem;
    border: 1px solid;
  }}
  .anomaly-card.high {{ background: rgba(239,68,68,0.08); border-color: rgba(239,68,68,0.3); }}
  .anomaly-card.medium {{ background: rgba(245,158,11,0.08); border-color: rgba(245,158,11,0.3); }}
  .anomaly-icon {{ font-size: 1.1rem; }}
  .anomaly-body {{ display: flex; flex-direction: column; gap: 0.2rem; }}
  .anomaly-body strong {{ font-size: 0.95rem; }}
  .anomaly-body span {{ font-size: 0.85rem; color: var(--yellow); }}
  .anomaly-body small {{ font-size: 0.78rem; color: var(--muted); }}

  .budget-row {{ margin-bottom: 1rem; }}
  .budget-label {{ display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.35rem; color: var(--muted); }}
  .budget-bar-track {{ background: var(--surface2); border-radius: 999px; height: 8px; overflow: hidden; }}
  .budget-bar {{ height: 100%; border-radius: 999px; transition: width 0.4s; }}
  .budget-bar.ok {{ background: var(--green); }}
  .budget-bar.warn {{ background: var(--yellow); }}
  .budget-bar.over {{ background: var(--red); }}
  .budget-pct {{ font-size: 0.78rem; color: var(--muted); text-align: right; margin-top: 0.2rem; }}
  .over-text {{ color: var(--red); }}

  .merchant-row {{ display: flex; align-items: center; gap: 0.5rem; padding: 0.6rem 0; border-bottom: 1px solid var(--border); font-size: 0.88rem; }}
  .merchant-row:last-child {{ border-bottom: none; }}
  .merchant-name {{ flex: 1; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .merchant-visits {{ color: var(--muted); min-width: 2.5rem; text-align: center; }}
  .merchant-total {{ font-weight: 600; min-width: 5rem; text-align: right; }}

  .no-data {{ color: var(--muted); font-size: 0.9rem; padding: 1rem 0; }}

  footer {{ text-align: center; color: var(--muted); font-size: 0.8rem; padding: 2rem; border-top: 1px solid var(--border); margin-top: 2rem; }}
</style>
</head>
<body>

<header>
  <div>
    <h1>💰 Finance Report — <span>{month_label}</span></h1>
    <p>Personal Spending Analysis</p>
  </div>
  <div class="generated">Generated {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>
</header>

<main>
  <!-- KPI Row -->
  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-label">Total Income</div>
      <div class="kpi-value income">${income:,.2f}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Total Expenses</div>
      <div class="kpi-value expense">${expenses:,.2f}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Net Savings</div>
      <div class="kpi-value net">${net:+,.2f}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Transactions</div>
      <div class="kpi-value">{curr.get("tx_count", 0)}</div>
    </div>
  </div>

  <!-- Row 1: Donut + Daily Spending -->
  <div class="grid-2">
    <div class="card">
      <h2>🍩 Spending by Category</h2>
      <canvas id="donutChart"></canvas>
    </div>
    <div class="card">
      <h2>📅 Daily Spending</h2>
      <canvas id="dailyChart"></canvas>
    </div>
  </div>

  <!-- Row 2: Monthly Trend (wide) -->
  <div class="card" style="margin-bottom: 1.5rem;">
    <h2>📈 Monthly Trend</h2>
    <canvas id="trendChart" style="max-height: 220px;"></canvas>
  </div>

  <!-- Row 3: Anomalies + Budgets -->
  <div class="grid-2">
    <div class="card">
      <h2>🚨 Spending Anomalies</h2>
      {anomaly_html}
    </div>
    <div class="card">
      <h2>🎯 Budget Status</h2>
      {budget_html}
    </div>
  </div>

  <!-- Row 4: Top Merchants -->
  <div class="card" style="margin-top: 1.5rem;">
    <h2>🏪 Top Merchants This Month</h2>
    {merchants_html if merchants_html else '<p class="no-data">No transactions found.</p>'}
  </div>
</main>

<footer>
  Personal Finance Tracker · finance-tracker · {datetime.now().strftime("%Y")}
</footer>

<script>
const GRID_COLOR = 'rgba(255,255,255,0.06)';
const TEXT_COLOR = '#8888a8';

// Donut
new Chart(document.getElementById('donutChart'), {{
  type: 'doughnut',
  data: {{
    labels: {cat_labels},
    datasets: [{{ data: {cat_values}, backgroundColor: {cat_colors}, borderWidth: 2, borderColor: '#18181f' }}]
  }},
  options: {{
    cutout: '60%',
    plugins: {{
      legend: {{ position: 'right', labels: {{ color: TEXT_COLOR, boxWidth: 12, padding: 12, font: {{ size: 11 }} }} }}
    }}
  }}
}});

// Daily bar chart
new Chart(document.getElementById('dailyChart'), {{
  type: 'bar',
  data: {{
    labels: {daily_labels},
    datasets: [{{ label: 'Spent', data: {daily_values}, backgroundColor: 'rgba(99,102,241,0.7)', borderRadius: 4 }}]
  }},
  options: {{
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      x: {{ ticks: {{ color: TEXT_COLOR, maxTicksLimit: 8 }}, grid: {{ color: GRID_COLOR }} }},
      y: {{ ticks: {{ color: TEXT_COLOR, callback: v => '$' + v }}, grid: {{ color: GRID_COLOR }} }}
    }}
  }}
}});

// Trend line chart
new Chart(document.getElementById('trendChart'), {{
  type: 'line',
  data: {{
    labels: {monthly_labels},
    datasets: [
      {{ label: 'Income', data: {monthly_income}, borderColor: '#10b981', backgroundColor: 'rgba(16,185,129,0.08)', tension: 0.4, fill: true, pointRadius: 4 }},
      {{ label: 'Expenses', data: {monthly_expenses}, borderColor: '#ef4444', backgroundColor: 'rgba(239,68,68,0.08)', tension: 0.4, fill: true, pointRadius: 4 }}
    ]
  }},
  options: {{
    plugins: {{ legend: {{ labels: {{ color: TEXT_COLOR }} }} }},
    scales: {{
      x: {{ ticks: {{ color: TEXT_COLOR }}, grid: {{ color: GRID_COLOR }} }},
      y: {{ ticks: {{ color: TEXT_COLOR, callback: v => '$' + v }}, grid: {{ color: GRID_COLOR }} }}
    }}
  }}
}});
</script>
</body>
</html>"""

    output_path.write_text(html, encoding="utf-8")
    print(f"✅ Report saved → {output_path}")
    return output_path


if __name__ == "__main__":
    import sys
    from analytics import monthly_summary
    months = monthly_summary()
    if not months:
        print("No data in database. Import some transactions first.")
        sys.exit(1)
    month = sys.argv[1] if len(sys.argv) > 1 else months[-1]["month"]
    build_report(month)
