from flask import Flask, render_template, request, jsonify
from urllib.parse import urlparse
import re
import ipaddress

app = Flask(__name__)

SCAM_WORDS = [
    "verify your account", "account suspended", "urgent",
    "otp", "click here", "claim your prize", "lottery",
    "bank details", "kyc", "blocked", "send money",
    "payment failed", "password", "update your details"
]


def make_result(level, title, details, tips=None):
    return {
        "level": level,
        "title": title,
        "details": details,
        "tips": tips or []
    }


def check_message(text):
    text = text.strip()

    if len(text) < 8:
        return make_result(
            "invalid", "Invalid input",
            ["Please enter a complete message."]
        )

    lower = text.lower()
    found = [word for word in SCAM_WORDS if word in lower]
    has_link = bool(re.search(r"(https?://|www\.)\S+", lower))
    asks_otp = "otp" in lower

    if asks_otp or (len(found) >= 2 and has_link):
        level, title = "high", "High-risk warning signs"
    elif found or has_link:
        level, title = "suspicious", "Suspicious message"
    else:
        level, title = "low", "No obvious warning signs found"

    details = []

    if found:
        details.append(
            "Suspicious phrases: " + ", ".join(found[:6])
        )

    if has_link:
        details.append(
            "A link was detected. Check its address before opening it."
        )

    if not details:
        details.append(
            "No common scam phrases were detected. "
            "This does not prove the message is safe."
        )

    return make_result(level, title, details, [
        "Never share your OTP, password or PIN.",
        "Verify unexpected requests through official channels."
    ])


def check_url(value):
    value = value.strip()

    if not value or len(value) > 2048:
        return make_result(
            "invalid", "Invalid URL",
            ["Enter a valid website address."]
        )

    candidate = value if "://" in value else "https://" + value

    try:
        parsed = urlparse(candidate)
        host = (parsed.hostname or "").lower()

        if (
            parsed.scheme not in ("http", "https")
            or not host
            or "." not in host
            or " " in value
        ):
            raise ValueError

        try:
            ipaddress.ip_address(host)
            is_ip = True
        except ValueError:
            is_ip = False

    except ValueError:
        return make_result(
            "invalid", "Invalid URL",
            ["Enter an address like https://example.com."]
        )

    warnings = []
    score = 0

    if parsed.scheme == "http":
        warnings.append("This address uses HTTP instead of HTTPS.")
        score += 1

    if is_ip:
        warnings.append("The address uses an IP address instead of a domain.")
        score += 2

    if "@" in parsed.netloc:
        warnings.append("The address contains an @ symbol.")
        score += 2

    if "xn--" in host:
        warnings.append("The domain contains encoded characters.")
        score += 2

    if host.count("-") >= 3 or len(host) > 45:
        warnings.append("The domain name is unusually complex.")
        score += 1

    if host in {
        "bit.ly", "tinyurl.com", "t.co",
        "cutt.ly", "is.gd", "rb.gy"
    }:
        warnings.append("This is a shortened URL.")
        score += 1

    if score >= 3:
        level, title = "high", "High-risk URL indicators"
    elif score:
        level, title = "suspicious", "Suspicious URL indicators"
    else:
        level, title = "low", "No obvious URL warning signs found"

    if not warnings:
        warnings.append(
            "No common URL warning signs were detected."
        )

    warnings.append(
        "This checker does not visit the website or verify it "
        "against a live threat database."
    )

    return make_result(level, title, warnings, [
        "Check the domain spelling carefully.",
        "Never enter banking details on an unexpected page."
    ])


def check_mobile(value):
    digits = re.sub(r"\D", "", value.strip())

    if not re.fullmatch(r"(?:91)?[6-9]\d{9}", digits):
        return make_result(
            "invalid", "Invalid mobile number",
            ["Enter a valid-looking 10-digit Indian mobile number."]
        )

    return make_result(
        "low", "Mobile number format looks valid",
        [
            "The number matches a common Indian mobile format.",
            "This does not verify the owner's identity or detect fraud."
        ],
        [
            "Never share OTPs or UPI PINs over a call.",
            "Verify callers using official contact details."
        ]
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/scan")
def scan():
    return render_template("scan.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/features")
def features():
    return render_template("features.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/api/check", methods=["POST"])
def api_check():
    data = request.get_json(silent=True) or {}
    kind = data.get("type")
    value = data.get("value")

    if not isinstance(value, str):
        return jsonify(make_result(
            "invalid", "Invalid input",
            ["Please enter valid text."]
        )), 400

    if kind == "message":
        result = check_message(value)
    elif kind == "url":
        result = check_url(value)
    elif kind == "mobile":
        result = check_mobile(value)
    else:
        return jsonify(make_result(
            "invalid", "Invalid checker",
            ["Please select a valid checker."]
        )), 400

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)