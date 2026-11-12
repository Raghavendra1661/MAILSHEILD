"""Small, explainable features used by the phishing email classifier."""
import re
from urllib.parse import urlparse

import numpy as np

URL_RE = re.compile(r"(https?://[^\s<>\"')]+|www\.[^\s<>\"')]+)", re.I)
IP_RE = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}$")

SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "ow.ly", "is.gd",
    "buff.ly", "cutt.ly", "rebrand.ly", "goo.gl",
}
RISKY_TLDS = {".xyz", ".top", ".click", ".work", ".info", ".biz", ".ru", ".tk", ".ml", ".gq", ".cf"}
KEYWORDS = (
    "urgent", "immediately", "verify", "confirm", "suspended", "locked",
    "password", "login", "sign in", "account", "security alert",
    "unusual activity", "click here", "limited time", "winner", "claim",
    "refund", "payment", "expire", "credit card", "act now",
)


def find_urls(message):
    """Return URLs found in a message, without trailing sentence punctuation."""
    return [item.rstrip(".,;:!?") for item in URL_RE.findall(message or "")]


def _hostname(url):
    candidate = url if url.lower().startswith(("http://", "https://")) else f"http://{url}"
    try:
        return (urlparse(candidate).hostname or "").lower()
    except ValueError:
        return ""


def email_features(message):
    message = message if isinstance(message, str) else ""
    urls = find_urls(message)
    hosts = [_hostname(url) for url in urls]
    letters = [char for char in message if char.isalpha()]

    return [
        len(urls),
        int(any(IP_RE.fullmatch(host) for host in hosts)),
        int(any(host in SHORTENERS for host in hosts)),
        int(any("@" in url.split("//", 1)[-1].split("/", 1)[0] for url in urls)),
        max((len(url) for url in urls), default=0),
        max((host.count(".") for host in hosts), default=0),
        int(any(host.endswith(tuple(RISKY_TLDS)) for host in hosts)),
        sum("-" in host for host in hosts),
        sum(url.lower().startswith("http://") for url in urls),
        sum(message.lower().count(word) for word in KEYWORDS),
        message.count("!"),
        sum(char.isupper() for char in letters) / len(letters) if letters else 0.0,
        int(bool(re.search(r"<\s*(html|a\s|form|img|script)", message, re.I))),
        sum(char.isdigit() for char in message) / len(message) if message else 0.0,
        len(message),
    ]


def extract_features(messages):
    return np.asarray([email_features(message) for message in messages], dtype=float)
