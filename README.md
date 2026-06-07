# VerifyHire
Explainable internship fraud detection system using ML + rule-based signals.  It analyzes job posts and URLs, outputs risk scores with evidence, and highlights scam patterns like UPI, fees, and phishing. Focus on transparency and reproducibility.
# Internship Risk Analyzer

Explainable system for detecting internship fraud in job posts and URLs using machine learning, rule-based signals, and similarity analysis.

---

## Problem

Students often face fake internships:
- registration fee scams
- UPI payment requests
- Telegram/WhatsApp recruitment traps
- phishing URLs

This project evaluates internship authenticity with structured risk scoring and evidence.

---

## Features

### 1. Text Scam Detection
- Internship message classification
- Scam vs legit prediction
- Risk scoring (0–100)

### 2. URL Risk Checker
- Phishing detection
- Suspicious TLD analysis
- Domain pattern scoring
- Shortener handling

### 3. Rule-Based Fraud Signals
- UPI detection
- Payment request detection
- Urgency detection
- Fee-based scam patterns

### 4. Explainability Layer
- Shows triggered signals
- Risk breakdown
- Transparent reasoning

### 5. Similarity Analysis
- Template-based scam detection
- Repeated scam pattern identification

---

## System Architecture

Input (Job Post / URL)
      ↓
Preprocessing
      ↓
Feature Extraction
      ↓
Rule Engine + ML Model
      ↓
Risk Fusion
      ↓
Explainability Layer
      ↓
Final Risk Score

---

## Tech Stack

- Python
- Pandas, NumPy
- Scikit-learn
- Regex
- TLDExtract
- FastAPI (optional backend)
- React (optional frontend)

---

## Model Metrics (Sample)

- Accuracy: 88%
- Precision: 89%
- Recall: 82%
- F1 Score: 85%
- False Positive Rate: 8%
- Adversarial Recall: 73%

---

## Supported Scam Types

- UPI payment scams
- Registration fee scams
- Captcha job scams
- Fake recruiter messages
- Telegram/WhatsApp recruitment scams
- Phishing URLs
- Fake government job sites

---

## Key Output

Each prediction includes:

- Risk score (0–100)
- Classification (Legit / Scam)
- Triggered signals
- Explanation summary

---
  
## Example

Input: 

Pay ₹500 registration fee to confirm internship
UPI: hrjobs@ybl


Output:

Risk Score: 92
Label: Scam
Signals:

UPI detected
Registration fee detected
Urgency detected


---

## Disclaimer

AI predictions are probabilistic and may be incorrect. Always verify internship opportunities and employers through official company channels before taking action.

---

## Limitations

- Depends on training data quality
- May misclassify legitimate recruiter messages
- Sensitive to unseen scam patterns

---

## Future Improvements

- Better negation handling
- Larger legitimate dataset
- URL graph-based detection
- Transformer-based classifier
- Real-time threat intelligence integration

---

## License

For educational use only.
