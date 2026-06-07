# ============================================================
#  PAYMENT DETECTOR — Negation-Aware
#  v1.2: Full negation detection layer
# ============================================================

import re
from backend.normalization import normalize_text


# ── Negation phrases that CANCEL payment signals ────────────
NEGATION_PHRASES = [
    "no payment required",
    "no payment needed",
    "no payment",
    "no registration fee",
    "no fee required",
    "no fee needed",
    "no fee",
    "no charges",
    "no hidden charges",
    "no hidden fees",
    "fee waived",
    "fee is waived",
    "fees waived",
    "payment waived",
    "payment is waived",
    "free internship",
    "free of cost",
    "free of charge",
    "without fee",
    "without any fee",
    "without payment",
    "without any payment",
    "without charges",
    "zero registration fee",
    "zero fee",
    "zero payment",
    "zero cost",
    "no cost",
    "completely free",
    "absolutely free",
    "not charged",
    "not required to pay",
    "don't have to pay",
    "don't need to pay",
    "do not pay",
    "no money required",
    "no money needed",
    "fee not applicable",
    "fee not required",
    "payment not required",
    "charges not applicable",
]

# ── Payment keywords that indicate a fee demand ─────────────
PAYMENT_KEYWORDS = [
    "registration fee",
    "processing fee",
    "application fee",
    "training fee",
    "activation fee",
    "joining fee",
    "starter fee",
    "security deposit",
    "caution deposit",
    "pay fee",
    "pay registration",
    "pay to join",
    "pay to start",
    "pay to confirm",
    "pay to access",
    "pay to register",
    "send money",
    "send amount",
    "advance payment",
    "advance fee",
    "platform access charge",
    "commitment charge",
    "training charge",
    "verification payment",
    "nominal fee",
    "small fee",
    "registration charge",
    "one-time registration",
    "one time registration",
    "one-time fee",
    "one-time charge",
    "one time charge",
    "pay via",
    "paying via",
    "paying to",
    "by paying",
    "platform fee",
    "platform access fee",
    "commitment fee",
    "verification fee",
    "clearance charge",
    "clearance fee",
    "activation charge",
    "setup fee",
    "subscription fee",
    "subscription",
    "refundable commitment",
    "refundable commitment fee",
    "processing charge",
    "joining charge",
    "application charge",
    "security charge",
    "caution charge",
    "deposit",
    "verification deposit",
    "transfer fee",
    "open account",
    "charge to access",
    "fee to access",
]

# ── UPI / digital payment method indicators ─────────────────
UPI_KEYWORDS = [
    "upi",
    "gpay",
    "google pay",
    "phonepe",
    "paytm payment",
    "bhim",
    "upi id",
    "upi payment",
]


def detect_negation(text):
    """
    Detect whether the text contains negation phrases that
    explicitly deny or waive payment requirements.

    Returns:
        dict with:
            - negation_detected (bool)
            - matched_negation (list of matched phrases)
    """
    text_lower = normalize_text(text)
    matched = []

    for phrase in NEGATION_PHRASES:
        if phrase in text_lower:
            matched.append(phrase)

    return {
        "negation_detected": len(matched) > 0,
        "matched_negation": matched,
    }


def detect_upi(text):
    """
    Detect UPI / digital payment method references.

    Returns:
        dict with:
            - upi_detected (bool)
            - matched_upi (list of matched keywords)
    """
    text_lower = normalize_text(text)
    matched = []

    for keyword in UPI_KEYWORDS:
        if keyword in text_lower:
            matched.append(keyword)

    return {
        "upi_detected": len(matched) > 0,
        "matched_upi": matched,
    }


def detect_payment(text):
    """
    Detect payment demands in text, respecting negation.

    Logic:
    1. Check negation first — if payment is explicitly denied,
       return payment_detected=False regardless of keywords.
    2. Only then check for payment demand keywords.

    Returns:
        dict with:
            - payment_detected (bool)
            - matched_keywords (list of matched payment keywords)
            - negation_detected (bool)
            - matched_negation (list of matched negation phrases)
    """
    text_norm = normalize_text(text)
    text_lower = text_norm

    # Step 1: Negation check (takes priority)
    negation = detect_negation(text_norm)
    if negation["negation_detected"]:
        return {
            "payment_detected": False,
            "matched_keywords": [],
            "negation_detected": True,
            "matched_negation": negation["matched_negation"],
        }

    # Step 2: Payment keyword check
    matched = []
    for keyword in PAYMENT_KEYWORDS:
        if keyword in text_lower:
            matched.append(keyword)

    # Step 3: UPI check (standalone UPI mention is also a signal)
    upi = detect_upi(text_norm)
    if upi["upi_detected"]:
        matched.extend(upi["matched_upi"])

    return {
        "payment_detected": len(matched) > 0,
        "matched_keywords": list(set(matched)),
        "negation_detected": False,
        "matched_negation": [],
    }