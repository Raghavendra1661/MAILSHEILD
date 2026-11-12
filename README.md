# MailShield — Phishing Email Detector

MailShield is a student machine-learning project that estimates whether an email message contains phishing patterns. It includes a clean Streamlit interface, a command-line option, and a reproducible training script.

## Features

- Paste an email into the web interface and review its predicted phishing score.
- Extract basic URL signals such as IP-based hosts, URL shorteners, unusual top-level domains and plain HTTP links.
- Combine TF-IDF text features with numeric message and URL features.
- Train a Logistic Regression classifier and evaluate it on a held-out test set.
- Run a prediction from the terminal or from a UTF-8 text file.

## Project structure

```text
phishing-email-detector/
├── app.py                 # Streamlit web interface
├── features.py            # Text and URL feature extraction
├── train.py               # Model training and evaluation
├── predict.py             # Command-line prediction
├── make_sample_data.py    # Creates a clearly synthetic practice dataset
├── data/
│   └── emails.csv
├── models/                # Trained model is saved here
└── requirements.txt
```

## Run on Windows

Open VS Code terminal in the project folder and run:

```bash
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
py train.py
py -m streamlit run app.py
```

Streamlit will print a local address, usually `http://localhost:8501`.

If the sample CSV is missing, create it first:

```bash
py make_sample_data.py
```

## Command-line use

```bash
py predict.py "Your account is locked. Verify at http://example.com"
py predict.py --file suspicious_email.txt
```

## Dataset and evaluation note

The included `data/emails.csv` is synthetic sample data created by `make_sample_data.py`. It is useful for checking that the application runs, but it is **not representative of real email traffic**. Scores measured on it must not be presented as real-world performance.

For a meaningful evaluation, replace it with a properly labelled public dataset, check its licence, remove duplicates, inspect class balance and map its labels to `Phishing` and `Safe`. Then train again:

```bash
py train.py --data data/your_dataset.csv
```

The training script recognises common text and label column names and stops if it encounters labels it does not understand.

## Limitations

- Analyses pasted message text only; it does not inspect sender headers, SPF, DKIM or DMARC.
- Does not open links or check them against a live blacklist.
- A low score does not prove an email is safe, and a high score does not prove it is malicious.
- The model is only as reliable as its training data and evaluation method.
- English-focused sample data will not represent every language or phishing style.

Use MailShield as an educational demonstration, not as a replacement for an email security gateway or human review.
