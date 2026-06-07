# ============================================================
#  INTERNSHIP RISK ANALYZER — FastAPI Backend
#  File: main.py   (v2.0: Fusion Layer, Rules Engine, Logging)
#  Run with: uvicorn main:app --reload
# ============================================================

import os
import json
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

# Import modules
from part2_ml_model import EnsembleModel
from url_checker import analyze_url
from payment_detector import detect_payment, detect_negation
from explainability import explain_prediction
from trust_layer import get_domain_trust
from part1_dataset_similarity import extract_features
from normalization import normalize_text

# ── Create the FastAPI app ──────────────────────────────────
app = FastAPI(title="Internship Risk Analyzer API v2.0")

# ── Allow React frontend to talk to this backend ────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Train the ML model once when the server starts ──────────
print("Training ML model... please wait...")
model = EnsembleModel()
model.train()
print("Model ready!")

# ============================================================
#  REQUEST BODY SCHEMAS
# ============================================================

class AnalyzeRequest(BaseModel):
    text: str
    url: Optional[str] = None

class URLRequest(BaseModel):
    url: str

class TextRequest(BaseModel):
    text: str

# ============================================================
#  LOGGING UTILITY
# ============================================================

def log_decision(input_text, normalized_text, rule_score, ml_prob, domain_score, final_score, risk_label, explanation_summary, triggered_features):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "decision_log.jsonl")
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "input_text": input_text,
        "normalized_text": normalized_text,
        "rule_score": float(round(rule_score, 2)),
        "ml_probability": float(round(ml_prob, 4)),
        "domain_score": float(round(domain_score, 2)),
        "final_score": float(round(final_score, 2)),
        "prediction": risk_label,
        "explanation": explanation_summary,
        "triggered_features": triggered_features
    }
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

# ============================================================
#  RULES ENGINE
# ============================================================

def calculate_rules_score(text: str) -> float:
    features = extract_features(text)
    
    rules_score = 0
    
    # 1. Payment demands (negation-aware)
    if features["payment_present"] == 1:
        if features["telegram_present"] == 1 or features["whatsapp_present"] == 1:
            if features["upi_present"] == 1:
                rules_score += 100
            else:
                rules_score += 85
        else:
            rules_score += 70
            
    # 2. UPI payments without explicit negation
    if features["upi_present"] == 1 and features["payment_negated"] == 0:
        if features["telegram_present"] == 1 or features["whatsapp_present"] == 1:
            rules_score = max(rules_score, 90)
        else:
            rules_score = max(rules_score, 60)
            
    # 3. Urgency
    if features["urgency_score"] >= 2:
        rules_score += 20
        
    # 4. Legit context mitigation
    if features["legit_context_score"] > 0:
        rules_score -= 30 * features["legit_context_score"]
        
    # 5. Overrides
    if features["payment_negated"] == 1:
        rules_score = min(rules_score, 10)
        
    rules_score = max(0.0, min(100.0, float(rules_score)))
    return rules_score

# ============================================================
#  ENDPOINT 1: /analyze
# ============================================================
@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    # Step 1: Run ML model on the text
    prediction = model.predict(req.text)
    ml_score = prediction["scam_probability"] * 100

    # Step 2: Extract normalized features and run Rules Engine
    features = extract_features(req.text)
    rules_score = calculate_rules_score(req.text)

    # Step 3: URL analysis (only if URL was provided)
    url_analysis = None
    domain_score = 0.0
    domain_trust = 0.3

    if req.url:
        url_result = analyze_url(req.url)
        domain_trust = get_domain_trust(url_result["domain"])
        domain_score = float(url_result["score"])
        url_analysis = {
            "domain": url_result["domain"],
            "risk":   url_result["risk"],
            "score":  url_result["score"],
        }

    # Step 4: Fusion Layer
    if req.url:
        final_score = 0.4 * rules_score + 0.4 * ml_score + 0.2 * domain_score
    else:
        final_score = 0.5 * rules_score + 0.5 * ml_score

    # Negation Override (if negated, cap final score to less than 15)
    if features["payment_negated"] == 1:
        final_score = min(final_score, 14.0)

    final_score = max(0.0, min(100.0, final_score))

    # Step 5: Risk Label
    if final_score >= 75:
        risk_label = "HIGH RISK"
    elif final_score >= 40:
        risk_label = "MEDIUM RISK"
    else:
        risk_label = "LOW RISK"

    # Step 6: Generate explanation
    explanation = explain_prediction(req.text)

    # Step 7: Logging
    triggered = {k: v for k, v in features.items() if v != 0}
    normalized = normalize_text(req.text)
    log_decision(
        input_text=req.text,
        normalized_text=normalized,
        rule_score=rules_score,
        ml_prob=prediction["scam_probability"],
        domain_score=domain_score,
        final_score=final_score,
        risk_label=risk_label,
        explanation_summary=explanation["summary"],
        triggered_features=triggered
    )

    # Return structure matching frontend expects
    payment_result = detect_payment(req.text)
    negation_result = detect_negation(req.text)

    return {
        "prediction":        prediction["prediction"],
        "confidence":        prediction["confidence"],
        "scam_probability":  prediction["scam_probability"],
        "final_score":       round(final_score, 2),
        "risk_label":        risk_label,
        "payment_detected":  payment_result["payment_detected"],
        "matched_keywords":  payment_result["matched_keywords"],
        "negation_detected": negation_result["negation_detected"],
        "reasons":           explanation["suspicious_signals"],
        "legitimate_signals": explanation["legitimate_signals"],
        "explanation_summary": explanation["summary"],
        "url_analysis":      url_analysis,
    }

# ============================================================
#  ENDPOINT 2: /url
# ============================================================
@app.post("/url")
def check_url(req: URLRequest):
    url_result   = analyze_url(req.url)
    domain_trust = get_domain_trust(url_result["domain"])

    # Scale raw score (0-100)
    score_100 = url_result["score"]

    if score_100 >= 75:
        risk_label = "HIGH RISK"
    elif score_100 >= 25:
        risk_label = "MEDIUM RISK"
    else:
        risk_label = "LOW RISK"

    return {
        "domain":       url_result["domain"],
        "raw_score":    url_result["score"] / 25.0, # original expected 0-4
        "score":        score_100,
        "risk":         url_result["risk"],
        "risk_label":   risk_label,
        "https":        req.url.startswith("https"),
        "domain_trust": domain_trust,
        "is_trusted":   domain_trust > 0.9,
    }

# ============================================================
#  ENDPOINT 3: /payment
# ============================================================
@app.post("/payment")
def check_payment(req: TextRequest):
    result = detect_payment(req.text)
    score = min(len(result["matched_keywords"]) * 20, 100)

    if result.get("negation_detected", False):
        score = 0

    if score >= 60:
        risk_label = "HIGH RISK"
    elif score >= 20:
        risk_label = "MEDIUM RISK"
    else:
        risk_label = "LOW RISK"

    return {
        "payment_detected":  result["payment_detected"],
        "matched_keywords":  result["matched_keywords"],
        "keyword_count":     len(result["matched_keywords"]),
        "score":             score,
        "risk_label":        risk_label,
        "negation_detected": result.get("negation_detected", False),
        "matched_negation":  result.get("matched_negation", []),
    }

# ============================================================
#  ENDPOINT 4: /explain
# ============================================================
@app.post("/explain")
def explain(req: TextRequest):
    prediction = model.predict(req.text)
    explanation = explain_prediction(req.text)
    payment = detect_payment(req.text)

    if prediction["prediction"] == "SCAM":
        verdict = (
            f"This posting shows {len(explanation['suspicious_signals'])} suspicious pattern(s) "
            f"with {round(prediction['scam_probability']*100, 1)}% scam probability. "
            f"Confidence: {prediction['confidence']}."
        )
    else:
        verdict = (
            f"This posting appears legitimate with "
            f"{round((1 - prediction['scam_probability'])*100, 1)}% safe probability. "
            f"{explanation['summary']}"
        )

    return {
        "prediction":       prediction["prediction"],
        "confidence":       prediction["confidence"],
        "scam_probability": prediction["scam_probability"],
        "suspicious_signals": explanation["suspicious_signals"],
        "legitimate_signals": explanation["legitimate_signals"],
        "explanation_summary": explanation["summary"],
        "reasons":          explanation["suspicious_signals"],
        "reason_count":     len(explanation["suspicious_signals"]),
        "verdict":          verdict,
        "features": {
            "payment_signals":   len(payment["matched_keywords"]),
            "negation_detected": payment.get("negation_detected", False),
        },
    }

# ============================================================
#  ENDPOINT 5: /benchmark
# ============================================================
@app.get("/benchmark")
def run_benchmark():
    import pandas as pd
    benchmark_path = "dataset/benchmark_dataset.csv"
    if not os.path.exists(benchmark_path):
        return {"error": "benchmark_dataset.csv not found"}

    df = pd.read_csv(benchmark_path, encoding="utf-8")

    results = []
    for _, row in df.iterrows():
        text = row["text"]
        actual = int(row["label"])
        scam_type = row["scam_type"]
        
        # Call the fusion prediction
        prediction = model.predict(text)
        rules_score = calculate_rules_score(text)
        
        url_score = 0.0
        if pd.notna(row.get("url")) and row["url"]:
            url_res = analyze_url(row["url"])
            url_score = float(url_res["score"])
            final_score = 0.4 * rules_score + 0.4 * (prediction["scam_probability"] * 100) + 0.2 * url_score
        else:
            final_score = 0.5 * rules_score + 0.5 * (prediction["scam_probability"] * 100)
            
        features = extract_features(text)
        if features["payment_negated"] == 1:
            final_score = min(final_score, 14.0)
            
        final_score = max(0.0, min(100.0, final_score))
        pred_label = 1 if final_score >= 40 else 0

        results.append({
            "actual": actual,
            "predicted": pred_label,
            "scam_type": scam_type,
        })

    # Per-slice metrics
    slices = df["scam_type"].unique()
    slice_metrics = {}

    overall_tp = overall_fp = overall_tn = overall_fn = 0

    for s in slices:
        sr = [r for r in results if r["scam_type"] == s]
        tp = sum(1 for r in sr if r["predicted"] == 1 and r["actual"] == 1)
        fp = sum(1 for r in sr if r["predicted"] == 1 and r["actual"] == 0)
        tn = sum(1 for r in sr if r["predicted"] == 0 and r["actual"] == 0)
        fn = sum(1 for r in sr if r["predicted"] == 0 and r["actual"] == 1)

        overall_tp += tp; overall_fp += fp
        overall_tn += tn; overall_fn += fn

        total = tp + fp + tn + fn
        acc = ((tp + tn) / total * 100) if total else 0
        prec = (tp / (tp + fp) * 100) if (tp + fp) else (100 if tp + fn == 0 else 0)
        rec = (tp / (tp + fn) * 100) if (tp + fn) else (100 if tp + fp == 0 else 0)
        f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) else 0

        slice_metrics[s] = {
            "accuracy": round(acc, 2),
            "precision": round(prec, 2),
            "recall": round(rec, 2),
            "f1": round(f1, 2),
            "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        }

    total_all = overall_tp + overall_fp + overall_tn + overall_fn
    return {
        "overall": {
            "accuracy": round((overall_tp + overall_tn) / total_all * 100, 2),
            "precision": round(overall_tp / (overall_tp + overall_fp) * 100, 2) if (overall_tp + overall_fp) else 0,
            "recall": round(overall_tp / (overall_tp + overall_fn) * 100, 2) if (overall_tp + overall_fn) else 0,
            "fpr": round(overall_fp / (overall_fp + overall_tn) * 100, 2) if (overall_fp + overall_tn) else 0,
        },
        "slices": slice_metrics,
        "total_samples": total_all,
    }

# ============================================================
#  ENDPOINT 6: GET / (health check)
# ============================================================
@app.get("/")
def root():
    return {"status": "ok", "message": "Internship Risk Analyzer API v2.0 is running"}

# ── Mount static files (React frontend build) ───────────────
# Place at the end so it doesn't intercept API routes
if os.path.exists("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")