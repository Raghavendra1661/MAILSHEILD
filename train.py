"""Train and evaluate the phishing email classifier."""
import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from features import extract_features

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "models" / "phishing_model.joblib"
TEXT_COLUMNS = ("text", "Email Text", "email_text", "body", "Body", "message", "Message", "v2")
LABEL_COLUMNS = ("label", "Email Type", "Label", "class", "Class", "target", "Category", "v1")
PHISHING_LABELS = {"phishing", "phishing email", "spam", "malicious", "1", "true"}
SAFE_LABELS = {"safe", "safe email", "ham", "legitimate", "legitimate email", "0", "false"}


def load_dataset(path):
    frame = pd.read_csv(path, encoding="latin-1")
    text_col = next((name for name in TEXT_COLUMNS if name in frame.columns), None)
    label_col = next((name for name in LABEL_COLUMNS if name in frame.columns), None)
    if not text_col or not label_col:
        raise ValueError(f"Could not identify email and label columns. Found: {list(frame.columns)}")

    frame = frame[[text_col, label_col]].dropna().copy()
    frame.columns = ["text", "label"]
    frame["text"] = frame["text"].astype(str).str.strip()
    labels = frame["label"].astype(str).str.strip().str.lower()
    unknown = sorted(set(labels) - PHISHING_LABELS - SAFE_LABELS)
    if unknown:
        raise ValueError(
            "Unrecognised labels: " + ", ".join(unknown[:8]) +
            ". Map the dataset labels to 'Phishing' or 'Safe' before training."
        )
    frame["target"] = labels.isin(PHISHING_LABELS).astype(int)
    frame = frame[frame["text"].ne("")].drop_duplicates("text")
    if frame["target"].nunique() != 2:
        raise ValueError("The dataset must contain both Safe and Phishing examples.")
    return frame.reset_index(drop=True)


def build_model():
    text_features = TfidfVectorizer(
        lowercase=True, stop_words="english", ngram_range=(1, 2),
        min_df=2, max_features=20000, sublinear_tf=True,
    )
    numeric_features = Pipeline([
        ("extract", FunctionTransformer(extract_features, validate=False)),
        ("scale", StandardScaler()),
    ])
    combined = FeatureUnion([
        ("message", text_features),
        ("signals", numeric_features),
    ])
    return Pipeline([
        ("features", combined),
        ("classifier", LogisticRegression(max_iter=1500, class_weight="balanced")),
    ])


def main():
    parser = argparse.ArgumentParser(description="Train the phishing email detector.")
    parser.add_argument("--data", default=str(ROOT / "data" / "emails.csv"))
    parser.add_argument("--test-size", type=float, default=0.2)
    args = parser.parse_args()

    data = load_dataset(args.data)
    train_x, test_x, train_y, test_y = train_test_split(
        data["text"], data["target"], test_size=args.test_size,
        random_state=42, stratify=data["target"],
    )
    model = build_model()
    model.fit(train_x, train_y)

    predictions = model.predict(test_x)
    print(f"Emails used: {len(data)}")
    print(f"Accuracy: {accuracy_score(test_y, predictions):.3f}")
    print(f"F1 score: {f1_score(test_y, predictions):.3f}")
    print(classification_report(test_y, predictions, target_names=["Safe", "Phishing"]))
    print("Confusion matrix [Safe, Phishing]:")
    print(confusion_matrix(test_y, predictions))

    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to: {MODEL_PATH}")


if __name__ == "__main__":
    main()
