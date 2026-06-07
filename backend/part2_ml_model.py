import pandas as pd
import numpy as np
from collections import defaultdict
from part1_dataset_similarity import preprocess, extract_features


class NaiveBayesClassifier:

    def __init__(self, alpha=1.0):
        self.alpha = alpha
        self.class_log_prior = {}
        self.word_log_likelihood = {}
        self.vocabulary = set()

    def fit(self, texts, labels):

        class_counts = defaultdict(int)
        word_counts = defaultdict(lambda: defaultdict(int))

        for text, label in zip(texts, labels):
            class_counts[label] += 1
            tokens = preprocess(text)
            for word in tokens:
                word_counts[label][word] += 1
                self.vocabulary.add(word)

        total_docs = len(labels)

        for cls in class_counts:
            self.class_log_prior[cls] = float(
                np.log(class_counts[cls] / total_docs)
            )

        vocab_size = len(self.vocabulary)

        self.word_log_likelihood = {}

        for cls in class_counts:
            total_words = sum(word_counts[cls].values())
            self.word_log_likelihood[cls] = {}

            for word in self.vocabulary:
                count = word_counts[cls].get(word, 0)
                self.word_log_likelihood[cls][word] = float(
                    np.log(
                        (count + self.alpha)
                        /
                        (total_words + self.alpha * vocab_size)
                    )
                )

    def predict_proba(self, text):

        tokens = preprocess(text)
        scores = {}

        for cls in self.class_log_prior:
            score = self.class_log_prior[cls]
            for word in tokens:
                if word in self.word_log_likelihood[cls]:
                    score += self.word_log_likelihood[cls][word]
            scores[cls] = score

        score_array = np.array(list(scores.values()))
        score_array = score_array - np.max(score_array)
        exp_scores = np.exp(score_array)
        probs = exp_scores / np.sum(exp_scores)

        return {
            cls: float(prob)
            for cls, prob in zip(scores.keys(), probs)
        }

    def predict(self, text):
        proba = self.predict_proba(text)
        return max(proba, key=proba.get)



def sigmoid(z):
    z = np.clip(z, -500, 500)
    return float(1 / (1 + np.exp(-z)))


class LogisticRegression:

    def __init__(self, lr=0.03, epochs=20):
        self.lr = lr
        self.epochs = epochs
        self.weights = None
        self.bias = 0.0
        self.feature_keys = []

    def _vectorize(self, text):
        features = extract_features(text)
        return np.array(
            [features.get(k, 0) for k in self.feature_keys],
            dtype=np.float64
        )

    def fit(self, texts, labels):
        sample_features = extract_features(texts[0])
        self.feature_keys = list(sample_features.keys())
        self.weights = np.zeros(len(self.feature_keys))
        self.bias = 0.0

        # Gradient Descent
        for _ in range(self.epochs):
            for text, label in zip(texts, labels):
                x = self._vectorize(text)
                z = np.dot(self.weights, x) + self.bias
                pred = sigmoid(z)
                error = pred - label

                # Weight updates
                self.weights -= self.lr * error * x
                self.bias -= self.lr * error

    def predict_proba(self, text):
        x = self._vectorize(text)
        z = np.dot(self.weights, x) + self.bias
        prob = sigmoid(z)
        return {
            1: prob,
            0: 1 - prob
        }

    def predict(self, text):
        proba = self.predict_proba(text)
        return 1 if proba[1] >= 0.5 else 0


class EnsembleModel:

    def __init__(self):
        self.nb = NaiveBayesClassifier()
        self.lr = LogisticRegression()

    def train(self):
        # ── Load expanded and balanced dataset (v2.0) ──────
        try:
            df = pd.read_csv(
                "dataset/expanded_dataset.csv",
                encoding="utf-8"
            )
            print(f"Loaded expanded dataset: {len(df)} samples")
        except FileNotFoundError:
            raise FileNotFoundError("dataset/expanded_dataset.csv not found. Run generate_datasets.py first.")

        df = df.sample(
            frac=1,
            random_state=42
        ).reset_index(drop=True)

        texts = list(df["text"])
        labels = list(df["label"])

        split = int(len(texts) * 0.8)

        train_texts = texts[:split]
        train_labels = labels[:split]

        test_texts = texts[split:]
        test_labels = labels[split:]

        print(f"\nDataset Size : {len(texts)}")
        print(f"Train Samples: {len(train_texts)}")
        print(f"Test Samples : {len(test_texts)}\n")

        print("Training Naive Bayes...")
        self.nb.fit(train_texts, train_labels)

        print("Training Logistic Regression...")
        self.lr.fit(train_texts, train_labels)

        print("\nTraining Completed.\n")

        self._evaluate(test_texts, test_labels)

    def predict(self, text):

        nb_score = self.nb.predict_proba(text).get(1, 0)
        lr_score = self.lr.predict_proba(text).get(1, 0)

        weights = np.array([0.5, 0.5])
        scores = np.array([nb_score, lr_score])
        final_score = float(np.dot(weights, scores))

        final_score += np.random.normal(0, 0.005)
        final_score = np.clip(final_score, 0, 1)

        label = 1 if final_score >= 0.5 else 0

        gap = abs(final_score - 0.5)
        if gap > 0.3:
            confidence = "HIGH"
        elif gap > 0.1:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        return {
            "prediction":
                "SCAM"
                if label == 1
                else "LEGITIMATE",
            "confidence":
                confidence,
            "scam_probability":
                float(round(final_score, 4))
        }

    def _evaluate(self, texts, labels):

        tp = fp = tn = fn = 0

        for text, actual in zip(texts, labels):
            result = self.predict(text)
            pred = (
                1
                if result["prediction"] == "SCAM"
                else 0
            )

            if pred == 1 and actual == 1:
                tp += 1
            elif pred == 1 and actual == 0:
                fp += 1
            elif pred == 0 and actual == 0:
                tn += 1
            else:
                fn += 1

        total = tp + fp + tn + fn

        accuracy = (
            (tp + tn) / total
        ) * 100

        precision = (
            tp / (tp + fp)
        ) * 100 if (tp + fp) > 0 else 0

        recall = (
            tp / (tp + fn)
        ) * 100 if (tp + fn) > 0 else 0

        f1 = (
            2 * precision * recall
            /
            (precision + recall)
        ) if (precision + recall) > 0 else 0

        print("===== MODEL EVALUATION =====")
        print(f"Accuracy  : {round(accuracy, 2)}%")
        print(f"Precision : {round(precision, 2)}%")
        print(f"Recall    : {round(recall, 2)}%")
        print(f"F1 Score  : {round(f1, 2)}%")
        print(f"TP={tp} FP={fp} TN={tn} FN={fn}")
        print("============================\n")



if __name__ == "__main__":

    model = EnsembleModel()
    model.train()

    # Test negation handling
    negation_tests = [
        "No payment required",
        "No registration fee required",
        "Free internship program",
        "There is no payment required",
        "Fee waived for all applicants",
    ]

    print("===== NEGATION TESTS =====")
    for text in negation_tests:
        result = model.predict(text)
        print(f"  Input: {text}")
        print(f"  -> {result['prediction']} (scam_prob={result['scam_probability']})")
        print()

    # Test known scam
    scam_text = """
    Remote internship opportunity.
    Earn 35000 weekly.
    No experience required.
    Pay 499 registration fee immediately.
    Apply now:
    http://intern-fast-job.xyz
    """
    result = model.predict(scam_text)
    print("===== SCAM SAMPLE =====")
    for k, v in result.items():
        print(f"{k}: {v}")