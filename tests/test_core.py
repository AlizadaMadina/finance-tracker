"""
tests/test_core.py — Unit tests for finance tracker
Run with: pytest tests/ -v
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Patch DB path to use temp file during tests
import tempfile
from pathlib import Path
import database

@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    """Redirect DB to a temporary file for each test."""
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.db")
    import analytics
    monkeypatch.setattr(analytics, "get_connection", database.get_connection)
    import importer
    monkeypatch.setattr(importer, "get_connection", database.get_connection)
    database.init_db()
    yield


# Importer Tests

class TestImporter:
    def test_parse_amount_standard(self):
        from importer import parse_amount
        assert parse_amount("$1,234.56") == 1234.56
        assert parse_amount("-$500.00") == -500.0
        assert parse_amount("(200.00)") == -200.0
        assert parse_amount("0.00") == 0.0

    def test_parse_date_formats(self):
        from importer import parse_date
        assert parse_date("2024-03-15") == "2024-03-15"
        assert parse_date("03/15/2024") == "2024-03-15"
        assert parse_date("15/03/2024") == "2024-03-15"
        assert parse_date("Mar 15, 2024") == "2024-03-15"

    def test_parse_date_invalid(self):
        from importer import parse_date
        with pytest.raises(ValueError):
            parse_date("not-a-date")

    def test_import_csv(self, tmp_path):
        import csv
        from importer import import_csv
        csv_file = tmp_path / "test.csv"
        with open(csv_file, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["Date", "Description", "Amount", "Account"])
            w.writerow(["2024-01-10", "Safeway Groceries", "-85.50", "Chequing"])
            w.writerow(["2024-01-15", "Payroll Deposit", "2750.00", "Chequing"])
            w.writerow(["2024-01-20", "Netflix", "-17.99", "Chequing"])

        count = import_csv(str(csv_file), account="Test")
        assert count == 3

    def test_categorization(self, tmp_path):
        import csv
        from importer import import_csv, seed_rules
        from analytics import spending_by_category

        seed_rules()
        csv_file = tmp_path / "cats.csv"
        with open(csv_file, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["Date", "Description", "Amount"])
            w.writerow(["2024-02-01", "Netflix Subscription", "-17.99"])
            w.writerow(["2024-02-01", "Uber Ride", "-18.50"])
            w.writerow(["2024-02-01", "Safeway Groceries", "-92.30"])

        import_csv(str(csv_file))
        cats = {c["category"]: c["total"] for c in spending_by_category()}
        assert "Subscriptions" in cats
        assert "Transport" in cats
        assert "Groceries" in cats


# Analytics Tests

class TestAnalytics:
    def _seed(self, rows):
        """Insert test transaction rows directly."""
        conn = database.get_connection()
        for row in rows:
            conn.execute(
                "INSERT INTO transactions (date, description, amount, category) VALUES (?,?,?,?)",
                row
            )
        conn.commit()
        conn.close()

    def test_spending_by_category(self):
        from analytics import spending_by_category
        self._seed([
            ("2024-03-01", "Starbucks", -5.50, "Food & Dining"),
            ("2024-03-05", "Safeway", -90.00, "Groceries"),
            ("2024-03-10", "Starbucks", -6.00, "Food & Dining"),
        ])
        cats = {c["category"]: c["total"] for c in spending_by_category("2024-03")}
        assert cats["Food & Dining"] == pytest.approx(11.50)
        assert cats["Groceries"] == pytest.approx(90.00)

    def test_monthly_summary(self):
        from analytics import monthly_summary
        self._seed([
            ("2024-03-01", "Employer", 2750.00, "Income"),
            ("2024-03-10", "Rent", -1400.00, "Housing"),
            ("2024-03-15", "Groceries", -120.00, "Groceries"),
        ])
        months = {m["month"]: m for m in monthly_summary()}
        assert "2024-03" in months
        m = months["2024-03"]
        assert m["income"] == pytest.approx(2750.00)
        assert m["expenses"] == pytest.approx(1520.00)
        assert m["net"] == pytest.approx(1230.00)

    def test_anomaly_detection(self):
        from analytics import detect_anomalies
        # Seed 3 prior months with ~$100 food
        for month in ["2024-01", "2024-02", "2024-03"]:
            self._seed([
                (f"{month}-10", "Restaurant", -100.00, "Food & Dining"),
            ])
        # Current month: 2x spending
        self._seed([("2024-04-10", "Restaurant", -200.00, "Food & Dining")])

        anomalies = detect_anomalies("2024-04")
        assert len(anomalies) == 1
        assert anomalies[0]["category"] == "Food & Dining"
        assert anomalies[0]["pct_change"] >= 25

    def test_budget_check(self):
        from analytics import set_budget, check_budgets
        self._seed([("2024-03-10", "Amazon", -350.00, "Shopping")])
        set_budget("Shopping", 300.00)
        budgets = {b["category"]: b for b in check_budgets("2024-03")}
        assert "Shopping" in budgets
        assert budgets["Shopping"]["over_budget"] is True
        assert budgets["Shopping"]["spent"] == pytest.approx(350.00)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
