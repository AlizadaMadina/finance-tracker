from flask import Flask, request, jsonify, send_from_directory
import tempfile, os, pickle
from pathlib import Path

app = Flask(__name__, template_folder='templates')

# Load ML model once when app starts
ML_MODEL = None
model_path = Path("model.pkl")
if model_path.exists():
    with open(model_path, "rb") as f:
        ML_MODEL = pickle.load(f)
    print("✅ ML model loaded!")
else:
    print("⚠️  No ML model found, using keyword rules only")


@app.route("/")
def index():
    return send_from_directory('templates', 'index.html')


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    files = request.files.getlist("file")
    if not files or files[0].filename == "":
        return jsonify({"error": "No file uploaded"}), 400
    
    for file in files:
        if not file.filename.endswith(".csv"):
            return jsonify({"error": f"{file.filename} is not a CSV file"}), 400

    account = request.form.get("account", "Uploaded Account")
    flip_amounts = request.form.get("flip_amounts", "false") == "true"

    tmp_paths = []
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

        total_count = 0
        for file in files:
            with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="wb") as tmp:
                file.save(tmp)
                tmp_paths.append(tmp.name)
            count = importer.import_csv(tmp_paths[-1], account=account)
            total_count += count

        if total_count == 0:
            return jsonify({"error": "No transactions could be read from these files."}), 400

        if flip_amounts:
            conn = database.get_connection()
            conn.execute("UPDATE transactions SET amount = -amount WHERE amount > 0")
            conn.commit()
            conn.close()

        if ML_MODEL:
            conn = database.get_connection()
            txs = conn.execute("SELECT id, description FROM transactions").fetchall()
            for tx in txs:
                try:
                    predicted = ML_MODEL.predict([tx["description"]])[0]
                    conn.execute("UPDATE transactions SET category=? WHERE id=?",
                                (predicted, tx["id"]))
                except:
                    pass
            conn.commit()
            conn.close()
        else:
            conn = database.get_connection()
            conn.execute("UPDATE transactions SET category='transfers' WHERE description LIKE '%payment from%'")
            conn.commit()
            conn.close()

        monthly = analytics.monthly_summary()
        if not monthly:
            return jsonify({"error": "Could not parse dates in this CSV"}), 400

        latest_month = monthly[-1]["month"]
        result = {
            "success": True,
            "month": latest_month,
            "transaction_count": total_count,
            "files_uploaded": len(files),
            "ml_categorized": ML_MODEL is not None,
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
        for tmp_path in tmp_paths:
            try: os.unlink(tmp_path)
            except: pass
        database.DB_PATH = original_db
        try: os.unlink(tmp_db.name)
        except: pass


if __name__ == "__main__":
    print("\n🚀 Finance Tracker — open http://localhost:8000\n")
    app.run(debug=True, port=8000)