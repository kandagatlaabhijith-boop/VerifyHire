# ============================================================
#  FEATURE ENGINEERING — Context-Aware
#  v1.2: Replaced independent keyword flags with semantic
#         context features and interaction terms
# ============================================================

import re
from payment_detector import detect_negation, detect_upi
from normalization import normalize_text


# ── Stopwords for text preprocessing ────────────────────────
STOPWORDS = {
    "the", "is", "and", "to",
    "a", "of", "for", "in", "on"
}


def preprocess(text):
    """Tokenize and clean text for NaiveBayes."""
    text = normalize_text(text)
    text = re.sub(r"[^a-zA-Z0-9 ]", "", text)
    tokens = text.split()
    tokens = [word for word in tokens if word not in STOPWORDS]
    return tokens


# ── Context keyword sets ────────────────────────────────────

LINKEDIN_PHRASES = [
    "let's connect", "lets connect", "connect on linkedin",
    "following your work", "great profile", "career journey",
    "thanks for connecting", "linkedin", "mutual connection",
    "connection request", "linkedin network", "professional network",
    "your profile", "connect with me", "nice to connect",
    "linkedin invitation", "impressed by your",
    "looking forward to connecting", "networking",
]

RECRUITER_PHRASES = [
    "application received", "application under review",
    "interview scheduled", "assessment link",
    "we will update you", "shortlisted",
    "congratulations on being selected", "next round",
    "hr will contact", "recruiter", "hiring manager",
    "talent acquisition", "recruitment drive",
    "we are reviewing", "status update",
    "your candidature", "selection process",
    "round of interview", "interview rounds",
    "technical round", "hr round",
    "offer letter provided", "offer letter",
]

CAMPUS_AMBASSADOR_PHRASES = [
    "campus ambassador", "campus coordinator",
    "coordinator application", "onboarding session",
    "selected as campus", "campus representative",
    "campus partner", "brand ambassador",
    "college representative", "campus lead",
    "fill onboarding form", "ambassador program",
]

ONBOARDING_PHRASES = [
    "onboarding", "orientation", "induction",
    "welcome aboard", "joining formalities",
    "onboarding group", "welcome session",
    "team introduction", "reporting manager",
    "first day instructions", "joining date",
    "day one", "joining kit",
]

TELEGRAM_PHRASES = [
    "telegram channel", "telegram group",
    "telegram", "join telegram",
    "telegram link", "t.me",
]

WHATSAPP_PHRASES = [
    "whatsapp group", "whatsapp", "join whatsapp",
    "whatsapp link", "whatsapp number",
]

COURSE_PROMOTION_PHRASES = [
    "resume support", "placement assistance",
    "live mentor", "mentor sessions",
    "certification course", "training program",
    "mern stack", "full stack",
    "skill development", "career guidance",
    "workshop", "bootcamp", "masterclass",
    "webinar", "hands-on training",
]

INTERVIEW_PHRASES = [
    "interview", "assessment", "coding test",
    "technical interview", "hr interview",
    "case study", "group discussion",
    "aptitude test", "written test",
    "take home assignment", "online assessment",
]

STIPEND_PHRASES = [
    "stipend", "per month", "monthly salary",
    "compensation", "paid internship",
    "ctc", "salary",
]

URGENCY_PHRASES = [
    "urgent", "immediately", "hurry",
    "limited slots", "limited seats",
    "closing soon", "last chance",
    "apply now", "join now",
    "today only", "act fast",
    "don't miss", "seats limited",
    "limited openings",
]

PAYMENT_DEMAND_PHRASES = [
    "registration fee", "processing fee",
    "application fee", "training fee",
    "activation fee", "joining fee",
    "starter fee", "security deposit",
    "caution deposit", "pay fee",
    "send money", "advance payment",
    "advance fee", "platform access charge",
    "commitment charge", "training charge",
    "verification payment", "nominal fee",
    "small fee", "pay to join",
    "pay to confirm", "pay to start",
    "pay to access", "pay to register",
    "registration charge",
    "one-time registration", "one time registration",
    "one-time fee", "one-time charge",
    "one time charge",
    "pay via", "paying via",
    "paying to", "by paying",
    "platform fee", "platform access fee",
    "commitment fee", "verification fee",
    "clearance charge", "clearance fee",
    "activation charge", "setup fee",
    "subscription fee", "subscription",
    "refundable commitment", "refundable commitment fee",
    "processing charge", "joining charge",
    "application charge", "security charge",
    "caution charge", "deposit",
    "verification deposit", "transfer fee",
    "open account", "charge to access",
    "fee to access",
]

UPI_PHRASES = [
    "upi", "gpay", "google pay",
    "phonepe", "bhim", "upi id",
    "paytm payment",
]

OFFICIAL_EMAIL_PATTERN = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(com|org|in|co\.in|edu|gov)"
)

COMPANY_DOMAIN_PATTERNS = [
    "careers.", "nextstep.", "amazon.jobs",
    ".com/careers", "/careers", "naukri.com",
    "internshala.com", "linkedin.com",
    "letsintern.com", "unstop.com",
]

GOOGLE_FORM_PATTERNS = [
    "docs.google.com/forms", "forms.gle",
    "google form", "google forms",
]

STARTUP_PHRASES = [
    "startup", "early stage", "growing team",
    "founding team", "seed funded", "series a",
    "fast growing", "student interns welcome",
    "immediate joiners", "work from home",
    "remote position", "remote internship",
    "wfh", "student friendly",
]


def _count_matches(text_lower, phrases):
    """Count how many phrases from the list appear in text."""
    return sum(1 for phrase in phrases if phrase in text_lower)


def _has_match(text_lower, phrases):
    """Check if any phrase from the list appears in text."""
    return any(phrase in text_lower for phrase in phrases)


def extract_features(text):
    """
    Extract context-aware features from text.

    Returns a dict of 20+ features including interaction terms
    that capture conditional risk logic.
    """
    text_norm = normalize_text(text)
    text_lower = text_norm.lower()

    # ── Base presence features ──────────────────────────────
    telegram_present = int(_has_match(text_lower, TELEGRAM_PHRASES))
    whatsapp_present = int(_has_match(text_lower, WHATSAPP_PHRASES))

    # Payment: check negation FIRST
    negation = detect_negation(text_norm)
    negation_detected = negation["negation_detected"]

    raw_payment_present = _has_match(text_lower, PAYMENT_DEMAND_PHRASES)
    payment_present = int(raw_payment_present and not negation_detected)
    payment_negated = int(negation_detected)

    upi_present = int(_has_match(text_lower, UPI_PHRASES))
    official_email_present = int(bool(OFFICIAL_EMAIL_PATTERN.search(text_norm)))
    company_domain_present = int(_has_match(text_lower, COMPANY_DOMAIN_PATTERNS))
    google_form_present = int(_has_match(text_lower, GOOGLE_FORM_PATTERNS))
    onboarding_context_present = int(_has_match(text_lower, ONBOARDING_PHRASES))
    assessment_context_present = int(_has_match(text_lower, INTERVIEW_PHRASES))

    # ── Context features ────────────────────────────────────
    linkedin_context = int(_has_match(text_lower, LINKEDIN_PHRASES))
    recruiter_context = int(_has_match(text_lower, RECRUITER_PHRASES))
    campus_ambassador_context = int(_has_match(text_lower, CAMPUS_AMBASSADOR_PHRASES))
    stipend_mentioned = int(_has_match(text_lower, STIPEND_PHRASES))
    course_promotion = int(_has_match(text_lower, COURSE_PROMOTION_PHRASES))
    startup_context = int(_has_match(text_lower, STARTUP_PHRASES))

    # ── Urgency score (count, not binary) ───────────────────
    urgency_score = _count_matches(text_lower, URGENCY_PHRASES)

    # ── Interaction features (conditional risk logic) ───────
    # Telegram + payment = suspicious
    telegram_plus_payment = int(telegram_present and payment_present)
    # Telegram + UPI = high risk
    telegram_plus_upi = int(telegram_present and upi_present)
    # WhatsApp + payment = suspicious
    whatsapp_plus_payment = int(whatsapp_present and payment_present)
    # Platform present WITHOUT payment = neutral (positive signal)
    platform_no_payment = int(
        (telegram_present or whatsapp_present) and not payment_present
    )
    # Legitimate context signal: any legit indicator present
    legit_context_score = (
        linkedin_context + recruiter_context +
        campus_ambassador_context + assessment_context_present +
        stipend_mentioned + company_domain_present +
        onboarding_context_present
    )

    return {
        # Presence features
        "telegram_present": telegram_present,
        "whatsapp_present": whatsapp_present,
        "payment_present": payment_present,
        "payment_negated": payment_negated,
        "upi_present": upi_present,
        "official_email_present": official_email_present,
        "company_domain_present": company_domain_present,
        "google_form_present": google_form_present,
        "onboarding_context_present": onboarding_context_present,
        "assessment_context_present": assessment_context_present,

        # Context features
        "linkedin_context": linkedin_context,
        "recruiter_context": recruiter_context,
        "campus_ambassador_context": campus_ambassador_context,
        "stipend_mentioned": stipend_mentioned,
        "course_promotion": course_promotion,
        "startup_context": startup_context,

        # Scores
        "urgency_score": urgency_score,
        "text_length": len(text_norm.split()),

        # Interaction features
        "telegram_plus_payment": telegram_plus_payment,
        "telegram_plus_upi": telegram_plus_upi,
        "whatsapp_plus_payment": whatsapp_plus_payment,
        "platform_no_payment": platform_no_payment,
        "legit_context_score": legit_context_score,
    }