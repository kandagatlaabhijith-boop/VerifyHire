# ============================================================
#  BENCHMARK EVALUATION — Per-Slice Metrics v2.0
#  v2.0: Evaluates 12 slices and unseen scams, checks all PRD criteria
#  Run: python benchmark_eval.py
# ============================================================

import os
import json
import pandas as pd
import numpy as np

from part2_ml_model import EnsembleModel
from url_checker import analyze_url
from main import calculate_rules_score
from part1_dataset_similarity import extract_features

def run_benchmark():
    """
    Load benchmark dataset, run the full pipeline on each sample,
    and compute per-slice + overall metrics.
    """
    # ── 1. Load benchmark data ──────────────────────────────
    benchmark_path = "dataset/benchmark_dataset.csv"
    if not os.path.exists(benchmark_path):
        print("ERROR: benchmark_dataset.csv not found. Run generate_datasets.py first.")
        return

    df = pd.read_csv(benchmark_path, encoding="utf-8")
    print(f"Loaded benchmark: {len(df)} samples")
    print(f"Slices: {df['scam_type'].value_counts().to_dict()}\n")

    # ── 2. Train model ──────────────────────────────────────
    print("Training model for benchmark evaluation...\n")
    model = EnsembleModel()
    model.train()

    # ── 3. Run predictions ──────────────────────────────────
    results = []
    for _, row in df.iterrows():
        text = row["text"]
        actual_label = int(row["label"])
        scam_type = row["scam_type"]
        url = row.get("url") if pd.notna(row.get("url")) else None

        # Full pipeline prediction
        prediction = model.predict(text)
        rules_score = calculate_rules_score(text)
        
        url_score = 0.0
        if url:
            url_res = analyze_url(url)
            url_score = float(url_res["score"])
            final_score = 0.4 * rules_score + 0.4 * (prediction["scam_probability"] * 100) + 0.2 * url_score
        else:
            final_score = 0.5 * rules_score + 0.5 * (prediction["scam_probability"] * 100)

        # Apply negation override
        features = extract_features(text)
        if features["payment_negated"] == 1:
            final_score = min(final_score, 14.0)

        final_score = max(0.0, min(100.0, final_score))

        # Risk label threshold (40 is MEDIUM RISK, representing SCAM in binary prediction)
        pred_label = 1 if final_score >= 40 else 0

        results.append({
            "text": text[:80],
            "actual": actual_label,
            "predicted": pred_label,
            "scam_prob": prediction["scam_probability"],
            "final_score": final_score,
            "scam_type": scam_type,
        })

    # ── 4. Compute per-slice metrics ────────────────────────
    slices = df["scam_type"].unique()
    slice_metrics = {}

    print("=" * 75)
    print("  SLICE-WISE BENCHMARK RESULTS (v2.0)")
    print("=" * 75)
    print(f"{'Slice':<27} {'Acc':>6} {'Prec':>6} {'Rec':>6} {'F1':>6} {'N':>5}")
    print("-" * 75)

    overall_tp = overall_fp = overall_tn = overall_fn = 0

    for slice_name in sorted(slices):
        slice_results = [r for r in results if r["scam_type"] == slice_name]
        is_scam_slice = slice_results[0]["actual"] == 1

        tp = fp = tn = fn = 0
        for r in slice_results:
            if r["predicted"] == 1 and r["actual"] == 1:
                tp += 1
            elif r["predicted"] == 1 and r["actual"] == 0:
                fp += 1
            elif r["predicted"] == 0 and r["actual"] == 0:
                tn += 1
            else:
                fn += 1

        overall_tp += tp
        overall_fp += fp
        overall_tn += tn
        overall_fn += fn

        total = tp + fp + tn + fn
        accuracy = ((tp + tn) / total) * 100 if total > 0 else 0
        precision = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else (100 if tp + fn == 0 else 0)
        recall = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else (100 if tp + fp == 0 else 0)
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0

        # For legit slices, accuracy represents the percentage of correctly labeled legit samples (TN / total)
        display_metric = accuracy

        slice_metrics[slice_name] = {
            "accuracy": round(accuracy, 2),
            "precision": round(precision, 2),
            "recall": round(recall, 2),
            "f1": round(f1, 2),
            "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "total": total,
            "is_scam": is_scam_slice,
        }

        # Check pass status
        status = "FAIL"
        if is_scam_slice:
            if slice_name == "upi_scam" and recall >= 95:
                status = "PASS"
            elif slice_name == "registration_fee_scam" and recall >= 95:
                status = "PASS"
            elif slice_name == "captcha_scam" and recall >= 90:
                status = "PASS"
            elif slice_name == "adversarial_obfuscation" and recall >= 70:
                status = "PASS"
            elif recall >= 75: # default recall for scams
                status = "PASS"
        else:
            if slice_name in ["linkedin_networking", "recruiter_update", "campus_ambassador", "whatsapp_onboarding"] and accuracy >= 90:
                status = "PASS"
            elif slice_name in ["telegram_legit", "course_promotion", "startup_hiring"] and accuracy >= 85:
                status = "PASS"
            elif accuracy >= 80: # default accuracy for legit
                status = "PASS"

        print(f"  [{status:>4}] {slice_name:<24} {accuracy:>5.1f}% {precision:>5.1f}% {recall:>5.1f}% {f1:>5.1f}% {total:>4}")

    # ── 5. Compute overall metrics ──────────────────────────
    total_all = overall_tp + overall_fp + overall_tn + overall_fn
    overall_accuracy = ((overall_tp + overall_tn) / total_all) * 100
    overall_precision = (overall_tp / (overall_tp + overall_fp)) * 100 if (overall_tp + overall_fp) > 0 else 0
    overall_recall = (overall_tp / (overall_tp + overall_fn)) * 100 if (overall_tp + overall_fn) > 0 else 0
    overall_f1 = (2 * overall_precision * overall_recall / (overall_precision + overall_recall)) if (overall_precision + overall_recall) > 0 else 0
    fpr = (overall_fp / (overall_fp + overall_tn)) * 100 if (overall_fp + overall_tn) > 0 else 0

    print("-" * 75)
    print(f"\n{'='*75}")
    print("  OVERALL BENCHMARK METRICS")
    print(f"{'='*75}")
    print(f"  Accuracy  : {overall_accuracy:.2f}%")
    print(f"  Precision : {overall_precision:.2f}%")
    print(f"  Recall    : {overall_recall:.2f}%")
    print(f"  F1 Score  : {overall_f1:.2f}%")
    print(f"  FPR       : {fpr:.2f}%")
    print(f"  TP={overall_tp} FP={overall_fp} TN={overall_tn} FN={overall_fn}")

    # ── 6. Evaluate Unseen Scam Dataset (unseen_scam_test.csv) ──
    unseen_path = "dataset/unseen_scam_test.csv"
    unseen_recall = 0.0
    if os.path.exists(unseen_path):
        unseen_df = pd.read_csv(unseen_path, encoding="utf-8")
        unseen_tp = 0
        unseen_fn = 0
        
        for _, row in unseen_df.iterrows():
            text = row["text"]
            url = row.get("url")
            
            prediction = model.predict(text)
            rules_score = calculate_rules_score(text)
            
            url_score = 0.0
            if url:
                url_res = analyze_url(url)
                url_score = float(url_res["score"])
                final_score = 0.4 * rules_score + 0.4 * (prediction["scam_probability"] * 100) + 0.2 * url_score
            else:
                final_score = 0.5 * rules_score + 0.5 * (prediction["scam_probability"] * 100)
                
            features = extract_features(text)
            if features["payment_negated"] == 1:
                final_score = min(final_score, 14.0)
                
            final_score = max(0.0, min(100.0, final_score))
            pred = 1 if final_score >= 40 else 0
            
            if pred == 1:
                unseen_tp += 1
            else:
                unseen_fn += 1
                
        unseen_recall = (unseen_tp / (unseen_tp + unseen_fn)) * 100
        print(f"\n{'='*75}")
        print("  UNSEEN SCAM EVALUATION")
        print(f"{'='*75}")
        print(f"  Samples      : {len(unseen_df)}")
        print(f"  Unseen Recall: {unseen_recall:.2f}%")
        print(f"  TP={unseen_tp} FN={unseen_fn}")

    # ── 7. Check PRD success criteria ───────────────────────
    print(f"\n{'='*75}")
    print("  PRD SUCCESS CRITERIA CHECK")
    print(f"{'='*75}")

    criteria = [
        ("Precision > 85%", overall_precision > 85, overall_precision),
        ("Recall > 75%", overall_recall > 75, overall_recall),
        ("F1 > 80%", overall_f1 > 80, overall_f1),
        ("False Positive Rate < 10%", fpr < 10, fpr),
    ]

    scam_recall_criteria = {
        "upi_scam": ("UPI Scam Recall > 95%", 95, "recall"),
        "registration_fee_scam": ("Fee Scam Recall > 95%", 95, "recall"),
        "captcha_scam": ("Captcha Scam Recall > 90%", 90, "recall"),
        "adversarial_obfuscation": ("Adversarial Recall > 70%", 70, "recall"),
    }

    legit_accuracy_criteria = {
        "linkedin_networking": ("LinkedIn Accuracy > 90%", 90, "accuracy"),
        "recruiter_update": ("Recruiter Accuracy > 90%", 90, "accuracy"),
        "campus_ambassador": ("Campus Accuracy > 90%", 90, "accuracy"),
        "whatsapp_onboarding": ("WhatsApp Legit Accuracy > 90%", 90, "accuracy"),
        "telegram_legit": ("Telegram Legit Accuracy > 85%", 85, "accuracy"),
        "course_promotion": ("Course Promotion Accuracy > 85%", 85, "accuracy"),
    }

    results_criteria = []
    for desc, met, val in criteria:
        results_criteria.append((desc, met, f"{val:.2f}%"))

    for slice_name, (desc, threshold, metric_key) in scam_recall_criteria.items():
        if slice_name in slice_metrics:
            val = slice_metrics[slice_name][metric_key]
            met = val >= threshold
            results_criteria.append((desc, met, f"{val:.2f}%"))

    for slice_name, (desc, threshold, metric_key) in legit_accuracy_criteria.items():
        if slice_name in slice_metrics:
            val = slice_metrics[slice_name][metric_key]
            met = val >= threshold
            results_criteria.append((desc, met, f"{val:.2f}%"))

    passed = 0
    for desc, met, val_str in results_criteria:
        status = "PASS" if met else "FAIL"
        print(f"  [{status:>4}] : {desc:<40} (Value: {val_str})")
        if met:
            passed += 1

    print(f"\n  Result: {passed}/{len(results_criteria)} criteria passed")
    print(f"{'='*75}\n")

    # ── 8. Save results to JSON ─────────────────────────────
    output = {
        "overall": {
            "accuracy": round(overall_accuracy, 2),
            "precision": round(overall_precision, 2),
            "recall": round(overall_recall, 2),
            "f1": round(overall_f1, 2),
            "fpr": round(fpr, 2),
        },
        "slices": slice_metrics,
        "unseen_scam_recall": round(unseen_recall, 2),
        "total_samples": total_all,
    }

    output_path = "dataset/benchmark_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    run_benchmark()
