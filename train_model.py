"""
train_model.py — Train ML model to classify bank transactions
Run with: python train_model.py
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import Pipeline
import pickle
import os

print("📂 Loading training data...")
train = pd.read_csv("data/ca_train_transactions.csv")
test = pd.read_csv("data/ca_test_transactions.csv")

print(f"  Training samples: {len(train)}")
print(f"  Test samples: {len(test)}")
print(f"  Categories: {sorted(train['category'].unique())}")

# ── Features and Labels ───────────────────────────────────────────────────
X_train = train["transaction_text"]
y_train = train["category"]
X_test = test["transaction_text"]
y_test = test["category"]

# ── Build Pipeline ────────────────────────────────────────────────────────
# Pipeline = TF-IDF + Logistic Regression in one step
# Think of it like an assembly line:
# Raw text → TF-IDF converts to numbers → Model predicts category

print("\n🤖 Training model...")
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        ngram_range=(1, 2),  # use single words AND pairs of words
        max_features=5000,   # keep top 5000 most useful words
        lowercase=True,
        stop_words="english"
    )),
    ("clf", LogisticRegression(
        max_iter=1000,
        random_state=42
    ))
])

pipeline.fit(X_train, y_train)

# ── Evaluate on synthetic Test Set ───────────────────────────────────────────
print("\n📊 Results on synthetic test set:")
y_pred = pipeline.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"  Accuracy: {accuracy * 100:.2f}%")
print("\n  Detailed report:")
print(classification_report(y_test, y_pred))

# ── Feature Importance ────────────────────────────────────────────────────
# Which words are most important for each category?
print("\n🔍 Top words per category:")
vectorizer = pipeline.named_steps["tfidf"]
classifier = pipeline.named_steps["clf"]
feature_names = vectorizer.get_feature_names_out()

for i, category in enumerate(classifier.classes_):
    top_indices = classifier.coef_[i].argsort()[-5:][::-1]
    top_words = [feature_names[j] for j in top_indices]
    print(f"  {category:<20} → {', '.join(top_words)}")

# ── Save Model ────────────────────────────────────────────────────────────
print("\n💾 Saving model...")
with open("model.pkl", "wb") as f:
    pickle.dump(pipeline, f)
print("  Saved to model.pkl ✅")

# ── Test on YOUR real labeled Scotiabank data ─────────────────────────────
print("\n🏦 Testing on YOUR real Scotiabank transactions...")
real = pd.read_csv("data/my_real_transactions.csv")
X_real = real["transaction_text"]
y_real = real["category"]

y_real_pred = pipeline.predict(X_real)
real_accuracy = accuracy_score(y_real, y_real_pred)
print(f"\n  Real-world accuracy: {real_accuracy * 100:.2f}%")
print("\n  Detailed results:")
print(classification_report(y_real, y_real_pred, zero_division=0))

print("\n  Transaction by transaction:")
print(f"  {'Transaction':<35} {'Actual':<20} {'Predicted':<20} {'✓/✗'}")
print(f"  {'─'*80}")
for tx, actual, pred in zip(X_real, y_real, y_real_pred):
    correct = "✅" if actual == pred else "❌"
    print(f"  {tx:<35} {actual:<20} {pred:<20} {correct}")
