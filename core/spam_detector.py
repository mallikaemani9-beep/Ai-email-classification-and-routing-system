"""
Spam & Duplicate Detection Module
Computes cryptographic content hashes, detects identical/near duplicates,
and scores phishing/spam probability.
"""

import hashlib
import re
from typing import Tuple, Optional, Dict, Any, List

SPAM_TRIGGERS = [
    (r"\b(?:won|winner|winning)\b.*\b(?:\$|dollars|lottery|prize)\b", 40),
    (r"\b(?:wire transfer|western union|moneygram|claim inheritance)\b", 45),
    (r"\b(?:crypto|bitcoin|eth)\b.*\b(?:100x|guaranteed|giveaway|investment return)\b", 40),
    (r"\b(?:verify your bank|account suspended|confirm password immediately)\b", 35),
    (r"\b(?:viagra|cialis|pharmacy|weight loss pill|cheap pills)\b", 50),
    (r"\b(?:urgent response required|barrister|prince|diplomatic agent)\b", 45),
    (r"\b(?:refinance mortgage|pre-approved loan 0%)\b", 30),
    (r"\b(?:meet hot singles|dating online|chat now)\b", 45),
    (r"\b(?:100% free|no risk|act now limited time offer)\b", 25),
    (r"\b(?:click here to claim|click the link below to unlock)\b", 25)
]

def generate_content_hash(subject: str, body: str) -> str:
    """Creates a normalized cryptographic SHA-256 fingerprint for duplicate detection."""
    # Normalize: remove non-alphanumeric and extra whitespace
    clean_text = re.sub(r'[^a-zA-Z0-9]', '', f"{subject} {body}".lower())
    return hashlib.sha256(clean_text.encode('utf-8')).hexdigest()

def detect_spam(subject: str, body: str, sender: str = "") -> Tuple[bool, float, List[str]]:
    """
    Evaluates email for spam/phishing signals.
    Returns (is_spam, spam_score, detected_flags)
    """
    text = f"{subject} {body}".lower()
    score = 0.0
    flags = []
    
    # 1. Regex Rule Triggers
    for pattern, weight in SPAM_TRIGGERS:
        if re.search(pattern, text):
            score += weight
            flags.append(f"Triggered spam heuristic rule (+{weight} pts)")
            
    # 2. Excessive Capital Letters
    raw_text = f"{subject} {body}"
    caps_count = sum(1 for c in raw_text if c.isupper())
    total_letters = sum(1 for c in raw_text if c.isalpha())
    if total_letters > 20 and (caps_count / total_letters) > 0.40:
        score += 25
        flags.append("Excessive uppercase lettering / shouting (+25 pts)")
        
    # 3. Excessive Exclamation Marks or Currency symbols
    if text.count("!") >= 4 or text.count("$$$") >= 1:
        score += 15
        flags.append("Repeated punctuation / currency symbols (+15 pts)")
        
    # 4. Suspicious Sender Domain
    sender_lower = sender.lower()
    suspicious_tlds = [".xyz", ".top", ".click", ".win", ".loan", ".racing", ".accountant"]
    if any(sender_lower.endswith(tld) for tld in suspicious_tlds):
        score += 30
        flags.append("High-risk sender top-level domain (+30 pts)")
        
    spam_score = min(100.0, score)
    is_spam = spam_score >= 60.0
    
    return is_spam, round(spam_score, 1), flags

def check_duplicate(
    content_hash: str,
    subject: str,
    body: str,
    existing_emails: List[Dict[str, Any]]
) -> Tuple[bool, Optional[str], float]:
    """
    Checks if this email is an exact or near duplicate of any existing email.
    Returns (is_duplicate, duplicate_of_id, similarity_score)
    """
    # 1. Exact Hash Match
    for existing in existing_emails:
        if existing.get("content_hash") == content_hash:
            return True, existing.get("id"), 100.0
            
    # 2. Near Duplicate (Jaccard similarity on significant tokens)
    tokens_new = set(re.findall(r'\b\w{4,}\b', f"{subject} {body}".lower()))
    if not tokens_new:
        return False, None, 0.0
        
    for existing in existing_emails[:50]:  # check recent 50
        tokens_old = set(re.findall(r'\b\w{4,}\b', f"{existing.get('subject', '')} {existing.get('body', '')}".lower()))
        if not tokens_old:
            continue
        intersection = len(tokens_new.intersection(tokens_old))
        union = len(tokens_new.union(tokens_old))
        if union > 0:
            jaccard = (intersection / union) * 100.0
            if jaccard >= 88.0:
                return True, existing.get("id"), round(jaccard, 1)
                
    return False, None, 0.0
