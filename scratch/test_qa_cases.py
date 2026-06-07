import os
import sys

# Add root directory to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from part2_ml_model import EnsembleModel
from url_checker import analyze_url
from payment_detector import detect_payment
from part1_dataset_similarity import extract_features
from main import calculate_rules_score

# Initialize model
model = EnsembleModel()
model.train()

def test_analyze(text, url=None):
    prediction = model.predict(text)
    ml_score = prediction["scam_probability"] * 100
    rules_score = calculate_rules_score(text)
    
    url_score = 0.0
    if url:
        url_res = analyze_url(url)
        url_score = float(url_res["score"])
        final_score = 0.4 * rules_score + 0.4 * ml_score + 0.2 * url_score
    else:
        final_score = 0.5 * rules_score + 0.5 * ml_score

    features = extract_features(text)
    if features["payment_negated"] == 1:
        final_score = min(final_score, 14.0)

    final_score = max(0.0, min(100.0, final_score))
    
    if final_score >= 75:
        risk_label = "HIGH RISK"
    elif final_score >= 40:
        risk_label = "MEDIUM RISK"
    else:
        risk_label = "LOW RISK"
        
    return {
        "final_score": final_score,
        "risk_label": risk_label
    }

print("Running QA Test Cases:")
print("=" * 60)

# Case 1: No registration fee required (Expected: Legitimate, Risk < 15)
c1 = test_analyze("No registration fee required")
print(f"Case 1: No registration fee required -> Score: {c1['final_score']:.2f}, Label: {c1['risk_label']} (Pass: {c1['final_score'] < 15})")

# Case 2: There is no payment required (Expected: Legitimate, Risk < 15)
c2 = test_analyze("There is no payment required")
print(f"Case 2: There is no payment required -> Score: {c2['final_score']:.2f}, Label: {c2['risk_label']} (Pass: {c2['final_score'] < 15})")

# Case 3: govt-jobs.xyz (Expected: Medium/High Risk)
c3_url = analyze_url("http://govt-jobs.xyz")
print(f"Case 3: URL govt-jobs.xyz -> Score: {c3_url['score']}, Risk: {c3_url['risk']} (Rules: {c3_url['triggered_rules']})")

# Case 4: easyjobs.tk/apply (Expected: Medium Risk)
c4_url = analyze_url("http://easyjobs.tk/apply")
print(f"Case 4: URL easyjobs.tk/apply -> Score: {c4_url['score']}, Risk: {c4_url['risk']} (Rules: {c4_url['triggered_rules']})")

# Case 5: WhatsApp onboarding group created (Expected: Legitimate)
c5 = test_analyze("WhatsApp onboarding group created")
print(f"Case 5: WhatsApp onboarding group created -> Score: {c5['final_score']:.2f}, Label: {c5['risk_label']} (Pass: {c5['risk_label'] == 'LOW RISK'})")

# Case 6: Application under review (Expected: Legitimate)
c6 = test_analyze("Application under review")
print(f"Case 6: Application under review -> Score: {c6['final_score']:.2f}, Label: {c6['risk_label']} (Pass: {c6['risk_label'] == 'LOW RISK'})")

# Case 7: LinkedIn networking message (Expected: Legitimate)
c7 = test_analyze("LinkedIn networking message")
print(f"Case 7: LinkedIn networking message -> Score: {c7['final_score']:.2f}, Label: {c7['risk_label']} (Pass: {c7['risk_label'] == 'LOW RISK'})")
