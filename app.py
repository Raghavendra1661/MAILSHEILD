"""Streamlit interface for the phishing email detector."""
from pathlib import Path

import joblib
import streamlit as st

from features import find_urls

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "models" / "phishing_model.joblib"

st.set_page_config(page_title="MailShield | Email Security", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root { --ink:#17233b; --muted:#718096; --line:#e7edf5; --blue:#315efb; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background:linear-gradient(180deg,#f6f8ff 0%,#fbfcff 42%,#f7f9fc 100%); color:var(--ink); }
.block-container { max-width:1120px; padding-top:2rem; padding-bottom:3rem; }
.hero { padding:28px 32px; border:1px solid #e6ebf5; border-radius:22px;
        background:linear-gradient(115deg,#101d3b,#203d79); color:white; margin-bottom:24px; }
.eyebrow { color:#a9c0ff; font-size:12px; font-weight:700; letter-spacing:2px; text-transform:uppercase; }
.hero h1 { font-family:'Space Grotesk',sans-serif; font-size:38px; margin:8px 0 6px; color:white; }
.hero p { color:#d5def2; margin:0; font-size:15px; }
.panel { background:white; border:1px solid var(--line); border-radius:18px; padding:22px; }
.panel-title { font-family:'Space Grotesk',sans-serif; font-size:19px; font-weight:700; margin-bottom:5px; }
.muted { color:var(--muted); font-size:13px; }
.metric { background:white; border:1px solid var(--line); padding:18px; border-radius:16px; }
.metric-label { color:#718096; font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:.7px; }
.metric-value { font-family:'Space Grotesk',sans-serif; font-size:25px; font-weight:700; margin-top:5px; }
.verdict { border-radius:16px; padding:18px 20px; margin:12px 0 18px; font-weight:700; }
.danger { background:#fff1f1; border:1px solid #ffd5d5; color:#a62929; }
.safe { background:#edfbf4; border:1px solid #c9f0da; color:#167347; }
div.stButton > button { background:#315efb; color:white; border:0; border-radius:11px; padding:.65rem 1.2rem; font-weight:700; }
div.stButton > button:hover { background:#244bd5; color:white; }
div[data-testid="stTextArea"] textarea { border-radius:12px; border:1px solid #dce4f0; background:#fbfcff; }
footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="eyebrow">EMAIL THREAT ANALYSIS</div>
  <h1>MailShield</h1>
  <p>Check suspicious emails with machine-learning signals and clear, readable results.</p>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1.45, 1], gap="large")
with left:
    st.markdown('<div class="panel"><div class="panel-title">Analyse an email</div><div class="muted">Paste the message body below. You can include links and the original formatting.</div></div>', unsafe_allow_html=True)
    message = st.text_area(
        "Email message", height=260, label_visibility="collapsed",
        placeholder="Paste the email text here...\n\nExample: Your account has been temporarily locked. Verify your details at http://example.com",
    )
    run_check = st.button("Analyse email", type="primary", use_container_width=True)

with right:
    st.markdown("""
    <div class="panel">
      <div class="panel-title">What MailShield checks</div>
      <p class="muted">The model combines message patterns with basic link signals.</p>
      <hr style="border:0;border-top:1px solid #edf1f7;margin:16px 0">
      <b>Message content</b><p class="muted">Urgent language, account requests and common phishing phrases.</p>
      <b>Link characteristics</b><p class="muted">IP-based hosts, URL shorteners, unusual domains and plain HTTP links.</p>
      <b>Machine-learning score</b><p class="muted">A TF-IDF text model with additional numeric features.</p>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    st.info("Tip: Never enter passwords, OTPs or other private information into a message-analysis tool.")

if run_check:
    if not message.strip():
        st.warning("Paste an email message before running the analysis.")
    elif not MODEL_PATH.exists():
        st.error("The trained model is missing. Open a terminal in the project folder and run `python train.py`.")
    else:
        with st.spinner("Checking the message..."):
            model = joblib.load(MODEL_PATH)
            score = float(model.predict_proba([message])[0][1])
            urls = find_urls(message)
            is_phishing = score >= 0.5

        st.markdown("### Analysis result")
        verdict = "Potential phishing detected" if is_phishing else "No strong phishing pattern detected"
        style = "danger" if is_phishing else "safe"
        st.markdown(f'<div class="verdict {style}">{"⚠️" if is_phishing else "✓"} &nbsp; {verdict}</div>', unsafe_allow_html=True)

        a, b, c = st.columns(3)
        with a:
            st.markdown(f'<div class="metric"><div class="metric-label">Phishing score</div><div class="metric-value">{score:.0%}</div></div>', unsafe_allow_html=True)
        with b:
            st.markdown(f'<div class="metric"><div class="metric-label">Links found</div><div class="metric-value">{len(urls)}</div></div>', unsafe_allow_html=True)
        with c:
            st.markdown(f'<div class="metric"><div class="metric-label">Message length</div><div class="metric-value">{len(message):,}</div></div>', unsafe_allow_html=True)

        st.progress(score, text="Model phishing score")
        if urls:
            st.markdown("#### Links found in the message")
            for url in urls:
                st.code(url, language=None)
        else:
            st.success("No web links were detected in the pasted text.")

        st.caption("This is a machine-learning estimate, not proof that an email is safe or malicious. The model does not inspect email headers, follow links, or query live threat-intelligence services.")

st.markdown("---")
st.markdown('<div style="text-align:center;color:#8a96a8;font-size:12px">MAILSHIELD · Student machine-learning project · Use as a learning aid, not as a security guarantee</div>', unsafe_allow_html=True)
