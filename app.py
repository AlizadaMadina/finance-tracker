from flask import Flask, request, jsonify, send_from_directory
import tempfile, os
from pathlib import Path

app = Flask(__name__, template_folder='templates')

@app.route("/")
def index():
    return send_from_directory('templates', 'index.html')

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    if not file.filename.endswith(".csv"):
        return jsonify({"error": "Please upload a CSV file"}), 400
    account = request.form.get("account", "Uploaded Account")
    flip_amounts = request.form.get("flip_amounts", "false") == "true"
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="wb") as tmp:
        file.save(tmp)
        tmp_path = tmp.name
    try:
        import database, analytics, importer
        tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        tmp_db.close()
        original_db = database.DB_PATH
        database.DB_PATH = Path(tmp_db.name)
        analytics.get_connection = database.get_connection
        importer.get_connection = database.get_connection
        database.init_db()
        importer.seed_rules()
        count = importer.import_csv(tmp_path, account=account)
        if count == 0:
            return jsonify({"error": "No transactions could be read from this CSV."}), 400
        if flip_amounts:
            conn = database.get_connection()
            conn.execute("UPDATE transactions SET amount = -amount WHERE amount > 0")
            conn.commit()
            conn.close()
        conn = database.get_connection()
        conn.execute("UPDATE transactions SET category='Transfers' WHERE description LIKE '%payment from%'")
        conn.commit()
        conn.close()
        monthly = analytics.monthly_summary()
        if not monthly:
            return jsonify({"error": "Could not parse dates in this CSV"}), 400
        latest_month = monthly[-1]["month"]
        result = {
            "success": True,
            "month": latest_month,
            "transaction_count": count,
            "stats": next((m for m in monthly if m["month"] == latest_month), {}),
            "categories": analytics.spending_by_category(latest_month),
            "monthly": monthly,
            "merchants": analytics.top_merchants(latest_month, limit=8),
            "anomalies": analytics.detect_anomalies(latest_month),
            "daily": analytics.daily_spending(latest_month),
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        os.unlink(tmp_path)
        database.DB_PATH = original_db
        try: os.unlink(tmp_db.name)
        except: pass

if __name__ == "__main__":
    print("\n🚀 Finance Tracker — open http://localhost:8000\n")
    app.run(debug=True, port=8000)