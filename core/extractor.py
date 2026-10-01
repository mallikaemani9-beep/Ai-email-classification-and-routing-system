"""
Information Extraction Engine
Extracts Order IDs, Invoices, Customer Names, Monetary Amounts, Phone Numbers,
Deadlines, and Required Actions from raw email text.
"""

import re
from typing import Dict, Any, List

def extract_entities(subject: str, body: str, sender: str = "", sender_name: str = "") -> Dict[str, Any]:
    """
    Extracts structured entities from subject and body using pattern matching,
    NLP rules, and contextual heuristics.
    """
    full_text = f"{subject}\n{body}"
    
    # 1. Order / Invoice / Ticket IDs
    order_patterns = [
        r'(?:order|invoice|ticket|case|account|tracking|ref|claim|id)[\s#:]+([A-Z0-9\-_]{4,20})\b',
        r'#([0-9]{4,10})\b',
        r'\b(INV-[0-9A-Z]{4,12})\b',
        r'\b(ORD-[0-9A-Z]{4,12})\b',
        r'\b(TKT-[0-9A-Z]{4,12})\b'
    ]
    order_ids = []
    for pat in order_patterns:
        matches = re.findall(pat, full_text, re.IGNORECASE)
        for m in matches:
            clean_m = m.strip().strip("#")
            if clean_m and clean_m not in order_ids and not clean_m.lower() in ["help", "info", "please"]:
                order_ids.append(clean_m)
                
    # 2. Monetary Amounts
    money_pattern = r'(?:\$|€|£|USD|EUR|GBP)\s?[0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?|\b[0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?\s?(?:USD|EUR|GBP|dollars)\b'
    amounts = list(set(re.findall(money_pattern, full_text, re.IGNORECASE)))
    
    # 3. Customer Name
    customer_name = sender_name.strip() if sender_name else ""
    if not customer_name or customer_name.lower() in ["unknown", "anonymous", ""]:
        # Try signoff extraction from email body
        signoff_patterns = [
            r'(?:thanks|thank you|regards|best regards|sincerely|cheers|warmly|best),?\s*\n+([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\b',
            r'(?:from|signed):?\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\b'
        ]
        for pat in signoff_patterns:
            match = re.search(pat, body, re.IGNORECASE)
            if match:
                candidate = match.group(1).strip()
                if len(candidate) > 2 and candidate.lower() not in ["support", "team", "customer", "admin"]:
                    customer_name = candidate
                    break
    if not customer_name and "@" in sender:
        parts = sender.split("@")[0].replace(".", " ").replace("_", " ").title()
        customer_name = parts
        
    # 4. Phone Numbers
    phone_pattern = r'(?:\+?[0-9]{1,3}[ -]?)?\(?[0-9]{3}\)?[ -]?[0-9]{3}[ -]?[0-9]{4}'
    phones = list(set(re.findall(phone_pattern, full_text)))
    
    # 5. Deadlines & Explicit Dates
    deadline_patterns = [
        r'(?:by|before|until|deadline[:\s]+)(?:today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|[0-9]{1,2}(?:st|nd|rd|th)?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*|[0-9]{1,2}/[0-9]{1,2}(?:/[0-9]{2,4})?|\b[0-9]{1,2}\s*(?:hours|hrs|days|business days))\b',
        r'\b(?:asap|as soon as possible|immediately|urgently)\b'
    ]
    deadlines = []
    for pat in deadline_patterns:
        found = re.findall(pat, full_text, re.IGNORECASE)
        for f in found:
            f_clean = f.strip()
            if f_clean and f_clean.lower() not in [d.lower() for d in deadlines]:
                deadlines.append(f_clean)
                
    # 6. Core Stated Issue Identification
    issue = detect_core_issue(subject, body)
    
    # 7. Recommended Action
    action = recommend_action(subject, body, order_ids, amounts)
    
    return {
        "customer_name": customer_name or "Valued Client",
        "order_ids": order_ids if order_ids else ["N/A"],
        "primary_order_id": order_ids[0] if order_ids else "N/A",
        "monetary_amounts": amounts if amounts else ["N/A"],
        "phone_numbers": phones if phones else ["N/A"],
        "deadlines": deadlines if deadlines else ["Standard SLA"],
        "has_explicit_deadline": len(deadlines) > 0,
        "identified_issue": issue,
        "required_action": action
    }

def detect_core_issue(subject: str, body: str) -> str:
    """Identifies the root topic / issue of the communication."""
    text = f"{subject} {body}".lower()
    
    if any(k in text for k in ["charged twice", "double charge", "duplicate charge", "overcharged"]):
        return "Duplicate charge on account"
    if any(k in text for k in ["refund", "money back", "reimbursement"]):
        return "Customer requesting refund"
    if any(k in text for k in ["500 internal server", "error 500", "crash", "glitch", "bug in"]):
        return "Software application bug / system error"
    if any(k in text for k in ["downtime", "server down", "outage", "latency", "timeout"]):
        return "Production service outage / high latency"
    if any(k in text for k in ["demo", "enterprise pricing", "quote for", "purchase seats"]):
        return "Enterprise procurement / sales inquiry"
    if any(k in text for k in ["resume", "cv", "application for", "job opening", "interview"]):
        return "Candidate job application"
    if any(k in text for k in ["lawyer", "attorney", "unacceptable", "furious", "terrible service"]):
        return "Severe customer escalation / complaint"
    if any(k in text for k in ["where is my order", "tracking", "delivery delay", "not received"]):
        return "Package delivery status inquiry"
    if any(k in text for k in ["password reset", "cannot login", "locked out", "2fa"]):
        return "Account access / login authentication issue"
    if any(k in text for k in ["leave policy", "health insurance", "payroll question", "401k"]):
        return "Internal HR benefits / policy question"
        
    return subject.strip()[:60] if subject else "General inquiry"

def recommend_action(subject: str, body: str, order_ids: List[str], amounts: List[str]) -> str:
    """Recommends next operational step for the department."""
    text = f"{subject} {body}".lower()
    
    if any(k in text for k in ["charged twice", "double charge", "refund"]):
        id_str = f" for order #{order_ids[0]}" if order_ids and order_ids[0] != "N/A" else ""
        return f"Verify payment gateway logs and process refund{id_str}"
    if any(k in text for k in ["error", "bug", "crash", "500", "timeout", "downtime"]):
        return "Escalate to on-call Tech Ops engineer; check telemetry logs"
    if any(k in text for k in ["pricing", "demo", "quote", "enterprise"]):
        return "Assign Account Executive to schedule demo & send commercial proposal"
    if any(k in text for k in ["resume", "application", "job", "candidate"]):
        return "Screen candidate resume and schedule technical interview"
    if any(k in text for k in ["lawsuit", "attorney", "unacceptable", "sue"]):
        return "Flag for immediate review by Senior Management & Customer Relations Lead"
    if any(k in text for k in ["tracking", "where is my", "delivery"]):
        return "Inspect warehouse fulfillment status and provide tracking link"
    if any(k in text for k in ["password", "login", "reset", "2fa"]):
        return "Verify caller identity and issue secure one-time password reset link"
        
    return "Review customer inquiry and provide standard resolution response"
