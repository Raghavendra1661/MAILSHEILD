"""Command-line prediction for one email or a text file."""
import argparse
from pathlib import Path

import joblib

from features import find_urls

MODEL_PATH = Path(__file__).resolve().parent / "models" / "phishing_model.joblib"


def main():
    parser = argparse.ArgumentParser(description="Check an email for phishing indicators.")
    parser.add_argument("text", nargs="?", help="Email text to analyse")
    parser.add_argument("--file", help="Read email text from a UTF-8 file")
    args = parser.parse_args()

    if args.file:
        message = Path(args.file).read_text(encoding="utf-8", errors="replace")
    elif args.text:
        message = args.text
    else:
        parser.error("Provide email text or use --file.")

    if not MODEL_PATH.exists():
        parser.error("Model not found. Run: python train.py")

    model = joblib.load(MODEL_PATH)
    probability = float(model.predict_proba([message])[0][1])
    verdict = "Phishing" if probability >= 0.5 else "Likely safe"

    print(f"Assessment: {verdict}")
    print(f"Phishing score: {probability:.1%}")
    urls = find_urls(message)
    if urls:
        print("Links found:")
        for url in urls:
            print(f"  - {url}")


if __name__ == "__main__":
    main()
