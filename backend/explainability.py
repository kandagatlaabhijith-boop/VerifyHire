# ============================================================
#  EXPLAINABILITY ENGINE — Feature-Driven
#  v2.0
# ============================================================

from backend.part1_dataset_similarity import extract_features 

def explain_prediction(text: str) -> dict:
    """
    Generate human-readable explanations based directly on final
    processed features.
    """
    features = extract_features(text)
    
    suspicious = []
    legitimate = []
    
    # 1. Payment (negation-aware)
    if features["payment_negated"] == 1:
        legitimate.append("Payment requirement explicitly waived or negated.")
    elif features["payment_present"] == 1:
        suspicious.append("Payment demand detected (e.g. registration fee, caution deposit).")
        
    # 2. UPI / digital payment methods
    if features["upi_present"] == 1:
        if features["payment_negated"] == 0:
            suspicious.append("Digital payment method (UPI/GPay/PhonePe) referenced.")
        else:
            legitimate.append("UPI/digital payment referenced in waived/free context.")
            
    # 3. Urgency
    if features["urgency_score"] >= 2:
        suspicious.append(f"Multiple high-urgency words/phrases ({features['urgency_score']}) detected.")
        
    # 4. Platform interaction terms
    if features["telegram_plus_payment"] == 1:
        suspicious.append("Telegram communication combined with payment demand.")
    elif features["telegram_plus_upi"] == 1:
        suspicious.append("Telegram communication combined with UPI reference.")
    elif features["telegram_present"] == 1 and features["payment_present"] == 0:
        legitimate.append("Telegram used for coordination without payment requests.")
        
    if features["whatsapp_plus_payment"] == 1:
        suspicious.append("WhatsApp communication combined with payment demand.")
    elif features["whatsapp_present"] == 1 and features["payment_present"] == 0:
        legitimate.append("WhatsApp used for coordination without payment requests.")
        
    # 5. Legitimate context markers
    if features["linkedin_context"] == 1:
        legitimate.append("Professional LinkedIn networking context.")
    if features["recruiter_context"] == 1:
        legitimate.append("Official recruiter or hiring pipeline update context.")
    if features["campus_ambassador_context"] == 1:
        legitimate.append("Campus ambassador or student coordinator context.")
    if features["onboarding_context_present"] == 1:
        legitimate.append("Formal employee onboarding/orientation context.")
    if features["assessment_context_present"] == 1:
        legitimate.append("Formal candidate interview/assessment context.")
    if features["stipend_mentioned"] == 1:
        legitimate.append("Stipend or financial compensation mentioned.")
    if features["course_promotion"] == 1:
        legitimate.append("Legitimate training/course promotion context.")
    if features["startup_context"] == 1:
        legitimate.append("Startup recruitment/hiring context.")
    if features["official_email_present"] == 1:
        legitimate.append("Official company email address present.")
    if features["company_domain_present"] == 1:
        legitimate.append("Official careers portal or domain reference present.")
    if features["google_form_present"] == 1:
        legitimate.append("Google Form link used for standard application intake.")

    # Build summary verdict
    if len(suspicious) == 0 and len(legitimate) > 0:
        summary = f"Legitimate communication patterns detected ({len(legitimate)} safe signal(s))."
    elif len(suspicious) > 0 and len(legitimate) == 0:
        summary = f"Scam indicators detected ({len(suspicious)} suspicious signal(s))."
    elif len(suspicious) > 0 and len(legitimate) > 0:
        summary = f"Mixed signals: {len(suspicious)} suspicious, {len(legitimate)} legitimate. Manual review advised."
    else:
        summary = "Neutral communication style. No strong indicators in either direction."
        
    return {
        "suspicious_signals": suspicious,
        "legitimate_signals": legitimate,
        "summary": summary
    }