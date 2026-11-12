"""
Builds a small practice dataset (data/emails.csv) so the project runs out of the box.

IMPORTANT: this is synthetic. It is only here so you can test the code.
For your final results, download a real dataset (see README) and drop it in data/.
"""
import random
import pandas as pd

random.seed(7)

BRANDS = ["PayPal", "Amazon", "Netflix", "Apple", "Microsoft", "HDFC Bank", "SBI", "Google", "Facebook", "DHL"]
NAMES = ["Rahul", "Priya", "Amit", "Sneha", "John", "Meera", "Karan", "Anita", "David", "Neha"]
GOOD_DOMAINS = ["amazon.com", "paypal.com", "github.com", "google.com", "microsoft.com", "linkedin.com",
                "marwadiuniversity.ac.in", "wikipedia.org", "coursera.org", "zoom.us"]
BAD_HOSTS = ["secure-{b}-login.xyz", "{b}-verify-account.top", "account-{b}.click", "update.{b}.security-check.ru",
             "{b}.support-center.info", "bit.ly", "tinyurl.com", "192.168.44.12", "203.0.113.57"]

phish_templates = [
    "Dear customer, your {B} account has been suspended due to unusual activity. Verify your password immediately: {url}",
    "URGENT: We detected a login attempt on your {B} account. Confirm your identity or it will be locked within 24 hours. {url}",
    "Congratulations! You are the winner of a $500 {B} gift card. Claim your prize now: {url}",
    "Your payment of $89.99 could not be processed. Update your credit card details here to avoid cancellation: {url}",
    "Security alert from {B}. Someone tried to sign in from a new device. Click here to secure your account: {url}",
    "Invoice #{n} attached. Please review the payment details and log in to approve: {url}",
    "Hello {name}, you have a pending refund of ${n}. Act now and confirm your bank details at {url}",
    "<html><body><p>Your {B} password expires today!</p><a href='{url}'>Keep my password</a></body></html>",
    "Final notice: your mailbox is full. Click here to increase storage or lose your emails. {url}",
    "Dear {B} user, we noticed unusual activity. Please verify your SSN and account number to restore access. {url}",
]
# phishing mails that are sneakier: no obvious url or weak language
phish_quiet = [
    "Hi {name}, are you available? I need you to buy some gift cards for a client today. Reply as soon as you see this.",
    "Hello, this is HR. Please reply with your bank account details so we can fix your salary payment.",
    "Your {B} package could not be delivered. Reply with your address and card number to reschedule.",
]

safe_templates = [
    "Hi {name}, just a reminder that our project meeting is tomorrow at {n}pm. Agenda is attached. Thanks!",
    "Hello {name}, your {B} order #{n} has shipped. You can track it from your account at {url}",
    "Hi team, the lecture notes for this week are uploaded at {url}. Let me know if anything is missing.",
    "Thanks for registering for the workshop on machine learning. Details and the schedule are here: {url}",
    "Hey {name}, are we still on for lunch on Friday? Also, did you finish the assignment?",
    "Your monthly statement is ready. For your security we never ask for your password by email. View it at {url}",
    "Dear {name}, congratulations on completing the course! Your certificate is available at {url}",
    "Reminder: your invoice #{n} is due next week. You can download it from {url}. Regards, Accounts team",
    "Hi {name}, sharing the slides from today's class. Please go through them before the next lab session.",
    "Newsletter: this month's top articles on web development and security. Read more at {url}",
    "Hi {name}, your password was changed successfully. If this was you, no action is needed.",
    "Please find the minutes of the meeting below. Action items: update the report, review the code, confirm the venue.",
]


def make_url(bad):
    if bad:
        host = random.choice(BAD_HOSTS).format(b=random.choice(BRANDS).lower().replace(" ", ""))
        scheme = random.choice(["http://", "http://", "https://"])
        path = random.choice(["/login", "/verify?id=%d" % random.randint(1000, 99999), "/secure/update.php", "/a1b2c3"])
        return scheme + host + path
    host = random.choice(GOOD_DOMAINS)
    return "https://www." + host + random.choice(["", "/account", "/orders", "/courses/ml", "/docs"])


def make_email(label):
    if label == "Phishing":
        pool = phish_quiet if random.random() < 0.15 else phish_templates
        tmpl, bad = random.choice(pool), True
    else:
        tmpl, bad = random.choice(safe_templates), False
        # some real emails also use a lookalike-ish or shortened link
        if random.random() < 0.06:
            bad = True
    text = tmpl.format(B=random.choice(BRANDS), name=random.choice(NAMES), n=random.randint(10, 99999),
                       url=make_url(bad))
    # a bit of noise so the model doesn't see perfectly clean text
    if random.random() < 0.3:
        text += random.choice(["\n\nRegards,\nSupport Team", "\n\nThanks", "\n\n--\nSent from my phone"])
    return text


rows = [(make_email("Phishing"), "Phishing") for _ in range(900)]
rows += [(make_email("Safe"), "Safe") for _ in range(900)]
random.shuffle(rows)

pd.DataFrame(rows, columns=["text", "label"]).to_csv("data/emails.csv", index=False)
print("saved data/emails.csv with", len(rows), "emails")
