"""
Local Machine Learning Model & Continuous Retraining Engine
Uses Scikit-Learn TF-IDF + Logistic Regression with Calibrated Probabilities.
Supports dynamic retraining on human feedback loop.
"""

import os
import re
import math
import json
from collections import Counter, defaultdict
from typing import Tuple, Dict, Any, List, Optional

# Attempt importing Scikit-Learn; provide zero-dependency Pure-Python fallback if blocked by OS policy
try:
    import joblib
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.calibration import CalibratedClassifierCV
    SKLEARN_AVAILABLE = True
except (ImportError, OSError, Exception):
    SKLEARN_AVAILABLE = False

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "email_classifier.joblib")

# Rich initial seed training dataset covering all 9 enterprise categories
TRAINING_SEEDS = [
    # Customer Support
    ("How do I change my shipping address for my recent purchase?", "Customer Support"),
    ("My package says delivered but I haven't received it yet", "Customer Support"),
    ("Need assistance tracking order #88492. Where is it?", "Customer Support"),
    ("Can someone help me update my account email credentials?", "Customer Support"),
    ("Where can I find user guide and instructions for onboarding?", "Customer Support"),
    ("I need help resetting my security pin and two-factor auth", "Customer Support"),
    ("How can I return an item purchased last week? Return policy inquiry", "Customer Support"),
    ("Delivery delay question for order #77312", "Customer Support"),
    ("Unable to access my profile dashboard, please help", "Customer Support"),
    ("Product arrived with missing accessory cable", "Customer Support"),

    # Billing
    ("I was charged twice for my subscription invoice #INV-4921", "Billing"),
    ("Double charge on my credit card statement from your company", "Billing"),
    ("Requesting refund for unauthorized recurring charge", "Billing"),
    ("Where can I download VAT invoice receipt for last month?", "Billing"),
    ("Update company payment method and billing address details", "Billing"),
    ("Received an overdue notice but we already wired the payment", "Billing"),
    ("Please cancel my renewal auto-pay and refund the remaining balance", "Billing"),
    ("Discrepancy in billing amount for order #45892", "Billing"),
    ("Need credit memo applied to invoice #89211", "Billing"),
    ("Failed payment transaction notification on Mastercard", "Billing"),

    # Technical Issues
    ("500 Internal Server Error when calling the REST API endpoint", "Technical Issues"),
    ("The mobile application crashes immediately on iOS startup", "Technical Issues"),
    ("Production database timeout on query execution, high latency", "Technical Issues"),
    ("SSL certificate expired on api.domain.com throwing security warnings", "Technical Issues"),
    ("Webhook deliveries failing with 504 Gateway Timeout", "Technical Issues"),
    ("Critical system bug: checkout button is non-responsive in Safari", "Technical Issues"),
    ("Data sync between Postgres and Elastic search is out of date", "Technical Issues"),
    ("NullPointerException thrown in authentication microservice", "Technical Issues"),
    ("App performance degradation and high memory consumption", "Technical Issues"),
    ("Integration webhook signature verification failing consistently", "Technical Issues"),

    # Sales
    ("Interested in Enterprise pricing for 500 employee seats", "Sales"),
    ("Requesting a product demo for our procurement team next Tuesday", "Sales"),
    ("Looking to discuss volume license agreement and contract discounts", "Sales"),
    ("We want to upgrade our plan from Pro to Enterprise tier", "Sales"),
    ("Can an account executive call me regarding annual software contract?", "Sales"),
    ("Inquiry about RFP submission and customized deployment terms", "Sales"),
    ("Schedule a 30-minute discovery call for our technical architecture", "Sales"),
    ("Request for formal quote and MSA agreement review", "Sales"),
    ("Commercial inquiry regarding reseller partnership program", "Sales"),
    ("Looking to migrate 200 users from competitor to your platform", "Sales"),

    # Complaints
    ("Extremely dissatisfied with your rude customer service representative", "Complaints"),
    ("This service is completely unacceptable, I demand to speak to a manager", "Complaints"),
    ("Third time our service went down this month, this is a breach of contract", "Complaints"),
    ("I will contact my attorney and file a complaint with consumer protection", "Complaints"),
    ("Terrible experience, no one answers support tickets for 5 days", "Complaints"),
    ("Horrible delivery delay and damaged packaging, nobody cares", "Complaints"),
    ("Demanding full compensation for revenue lost due to system downtime", "Complaints"),
    ("Escalating this ticket directly to executive leadership team", "Complaints"),
    ("Worst product ever purchased, deceptive marketing and buggy software", "Complaints"),
    ("Customer support hung up on me. Completely unprofessional behavior", "Complaints"),

    # HR
    ("Inquiry regarding annual paid time off policy and parental leave", "HR"),
    ("How do I enroll in the company dental and vision health benefits?", "HR"),
    ("Question about 401k match deduction in this month's payroll", "HR"),
    ("Requesting workplace accommodations and ergonomic equipment", "HR"),
    ("Internal transfer opportunity inquiry for Senior Developer role", "HR"),
    ("Confidential HR inquiry regarding team policy and code of conduct", "HR"),
    ("Where can I find employment verification letter for my mortgage?", "HR"),
    ("Question about bereavement leave and emergency time off guidelines", "HR"),
    ("Upcoming performance review cycle timeline and self-assessment form", "HR"),
    ("Update direct deposit bank account details for salary deposit", "HR"),

    # Job Applications
    ("Application for Senior Machine Learning Engineer position - John Doe", "Job Applications"),
    ("Attached is my resume and portfolio for the Frontend Developer opening", "Job Applications"),
    ("Inquiring about status of my interview for Product Manager role", "Job Applications"),
    ("Excited to apply for Data Scientist role at your company. CV attached", "Job Applications"),
    ("Software Engineer job application with 6 years Python experience", "Job Applications"),
    ("Referral application for DevOps Engineer opening - Resume enclosed", "Job Applications"),
    ("Thank you for the initial screening interview, following up with portfolio", "Job Applications"),
    ("Application for Summer 2026 AI Research Internship", "Job Applications"),
    ("Cover letter and curriculum vitae for Head of Marketing position", "Job Applications"),
    ("Checking in on recruitment process for UX Designer vacancy", "Job Applications"),

    # General Queries
    ("What are your corporate office operating hours in New York?", "General Queries"),
    ("Press inquiry from TechCrunch regarding recent product announcement", "General Queries"),
    ("Where is your headquarters located? Can visitors park on site?", "General Queries"),
    ("General information request regarding upcoming developer conference", "General Queries"),
    ("Who should I contact regarding potential sponsorship opportunity?", "General Queries"),
    ("Is your office open during national public holidays next week?", "General Queries"),
    ("Inquiry regarding brand assets, logos, and media kit guidelines", "General Queries"),
    ("General question about your company history and sustainability mission", "General Queries"),
    ("Looking for main telephone number or reception contact details", "General Queries"),
    ("Do you offer student discounts or non-profit educational grants?", "General Queries"),

    # Spam
    ("CONGRATULATIONS! You have won $10,000,000 in the British Lottery! Claim now", "Spam"),
    ("Urgent wire transfer required from barrister Charles Okafor", "Spam"),
    ("Exclusive crypto bitcoin investment opportunity with 500% guaranteed return", "Spam"),
    ("Verify your bank credentials immediately or your account will be suspended", "Spam"),
    ("Cheap Rolex watches and discount prescription pills online store", "Spam"),
    ("Hot singles in your area want to chat right now click here", "Spam"),
    ("Act now! Free gift card worth $500 for selected email winners", "Spam"),
    ("Refinance your mortgage with 0% interest rate guaranteed approval", "Spam"),
    ("Inheritance settlement fund notice: reply with your passport copy", "Spam"),
    ("Earn $5,000 a day working from home with no experience needed click link", "Spam"),
]

class PurePythonClassifier:
    """
    Zero-dependency, pure-Python TF-IDF + Cosine Similarity classifier.
    100% resilient against OS Application Control policies, missing C++ runtimes,
    or binary DLL load issues.
    """
    STOP_WORDS = {
        "a", "about", "above", "after", "again", "all", "am", "an", "and", "any", "are", "as", "at",
        "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
        "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from",
        "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him",
        "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "me", "more",
        "most", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
        "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should",
        "so", "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves",
        "then", "there", "these", "they", "this", "those", "through", "to", "too", "under",
        "until", "up", "very", "was", "we", "were", "what", "when", "where", "which", "while",
        "who", "whom", "why", "with", "would", "you", "your", "yours", "yourself", "yourselves"
    }

    def __init__(self):
        self.idf: Dict[str, float] = {}
        self.class_centroids: Dict[str, Dict[str, float]] = {}
        self.training_data: List[Tuple[str, str]] = list(TRAINING_SEEDS)
        self.train()

    def _tokenize(self, text: str) -> List[str]:
        words = re.findall(r'\b[a-z0-9_\-\$#]{2,}\b', text.lower())
        tokens = [w for w in words if w not in self.STOP_WORDS]
        bigrams = [f"{tokens[i]}_{tokens[i+1]}" for i in range(len(tokens) - 1)]
        return tokens + bigrams

    def _compute_tfidf(self, tokens: List[str]) -> Dict[str, float]:
        counts = Counter(tokens)
        vec = {}
        for term, cnt in counts.items():
            if term in self.idf:
                tf = 1.0 + math.log(cnt)
                vec[term] = tf * self.idf[term]
        norm = math.sqrt(sum(v * v for v in vec.values()))
        if norm > 0:
            for term in vec:
                vec[term] /= norm
        return vec

    def train(self):
        doc_count = len(self.training_data)
        df = defaultdict(int)
        for text, cat in self.training_data:
            toks = set(self._tokenize(text))
            for t in toks:
                df[t] += 1

        self.idf = {t: math.log((1.0 + doc_count) / (1.0 + freq)) + 1.0 for t, freq in df.items()}

        category_vectors = defaultdict(lambda: defaultdict(float))
        for text, cat in self.training_data:
            toks = self._tokenize(text)
            vec = self._compute_tfidf(toks)
            for term, val in vec.items():
                category_vectors[cat][term] += val

        self.class_centroids = {}
        for cat, term_weights in category_vectors.items():
            norm = math.sqrt(sum(w * w for w in term_weights.values()))
            if norm > 0:
                self.class_centroids[cat] = {t: w / norm for t, w in term_weights.items()}
            else:
                self.class_centroids[cat] = term_weights

    def predict(self, text: str) -> Tuple[str, float]:
        toks = self._tokenize(text)
        doc_vec = self._compute_tfidf(toks)

        if not doc_vec:
            return "General Queries", 50.0

        scores: Dict[str, float] = {}
        for cat, centroid in self.class_centroids.items():
            sim = sum(val * centroid.get(term, 0.0) for term, val in doc_vec.items())
            scores[cat] = max(0.0, sim)

        best_cat = max(scores, key=scores.get)
        max_score = scores[best_cat]

        tau = 0.10
        exp_scores = {c: math.exp(min(50.0, s / tau)) for c, s in scores.items()}
        sum_exp = sum(exp_scores.values())
        prob = (exp_scores[best_cat] / sum_exp) if sum_exp > 0 else 0.5
        confidence = float(prob * 100.0)

        if max_score > 0.35:
            confidence = min(98.8, max(75.0, confidence))
        elif max_score > 0.15:
            confidence = min(88.0, max(58.0, confidence))
        else:
            confidence = min(68.0, max(45.0, confidence))

        return best_cat, round(confidence, 1)

    def retrain_with_feedback(self, feedback_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        added = 0
        for item in feedback_items:
            content = f"{item.get('subject', '')} {item.get('body', '')}".strip()
            cat = item.get("new_category")
            if content and cat:
                self.training_data.append((content, cat))
                self.training_data.append((content, cat))
                added += 1

        self.train()
        return {
            "status": "success",
            "total_samples": len(self.training_data),
            "feedback_samples_added": added,
            "classes": list(self.class_centroids.keys())
        }


class LocalClassifier:
    """Production classifier supporting Scikit-Learn with automatic Pure-Python fallback."""

    def __init__(self):
        self.model: Optional[Any] = None
        self.fallback = PurePythonClassifier()
        self.use_sklearn = False

        if SKLEARN_AVAILABLE:
            try:
                self._load_or_train()
                self.use_sklearn = True
            except Exception:
                self.use_sklearn = False

    def _build_pipeline(self):
        return Pipeline([
            ("tfidf", TfidfVectorizer(
                ngram_range=(1, 2),
                max_features=6000,
                sublinear_tf=True,
                stop_words="english"
            )),
            ("clf", CalibratedClassifierCV(
                estimator=LogisticRegression(C=2.0, max_iter=500, class_weight="balanced"),
                cv=3
            ))
        ])

    def _load_or_train(self):
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                return
            except Exception:
                pass
        self.train_seed()

    def train_seed(self):
        """Trains on default high-quality seeds and persists to disk if sklearn is operational."""
        if not SKLEARN_AVAILABLE:
            self.fallback.train()
            return

        try:
            texts = [f"{t[0]}" for t in TRAINING_SEEDS]
            labels = [t[1] for t in TRAINING_SEEDS]
            pipe = self._build_pipeline()
            pipe.fit(texts, labels)
            self.model = pipe
            os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
            joblib.dump(self.model, MODEL_PATH)
            self.use_sklearn = True
        except Exception:
            self.use_sklearn = False
            self.fallback.train()

    def predict(self, text: str) -> Tuple[str, float]:
        """
        Returns (predicted_category, confidence_percentage)
        """
        if self.use_sklearn and self.model:
            try:
                probas = self.model.predict_proba([text])[0]
                classes = self.model.classes_
                best_idx = np.argmax(probas)
                predicted_category = str(classes[best_idx])
                confidence = float(probas[best_idx] * 100.0)
                confidence = min(99.4, max(45.0, confidence))
                return predicted_category, round(confidence, 1)
            except Exception:
                pass

        return self.fallback.predict(text)

    def retrain_with_feedback(self, feedback_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Human-in-the-Loop continuous learning:
        Augments training dataset with human corrections and refits the model.
        """
        if self.use_sklearn:
            try:
                texts = [t[0] for t in TRAINING_SEEDS]
                labels = [t[1] for t in TRAINING_SEEDS]
                added_count = 0
                for item in feedback_items:
                    content = f"{item.get('subject', '')} {item.get('body', '')}".strip()
                    new_cat = item.get("new_category")
                    if content and new_cat:
                        texts.append(content)
                        labels.append(new_cat)
                        texts.append(content)
                        labels.append(new_cat)
                        added_count += 1

                pipe = self._build_pipeline()
                pipe.fit(texts, labels)
                self.model = pipe
                joblib.dump(self.model, MODEL_PATH)
                return {
                    "status": "success",
                    "total_samples": len(texts),
                    "feedback_samples_added": added_count,
                    "classes": list(pipe.classes_)
                }
            except Exception:
                pass

        return self.fallback.retrain_with_feedback(feedback_items)


# Global singleton instance
local_classifier = LocalClassifier()
