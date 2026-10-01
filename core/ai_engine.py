"""
Unified AI Classification, Sentiment, Summarization & Orchestration Engine
Supports:
1. Gemini 2.5/Flash API (via google-genai) for state-of-the-art GenAI analysis
2. Local Scikit-Learn TF-IDF + Calibrated ML Model fallback (Zero-configuration offline mode)
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional, List

from config import CATEGORIES, PRIORITIES
from core.ml_model import local_classifier
from core.extractor import extract_entities
from core.risk_engine import calculate_risk_profile
from core.spam_detector import detect_spam, check_duplicate, generate_content_hash
from core.router import route_email, get_department_workload_ratio
from core.response_generator import generate_draft_response
from core.database import get_all_emails

# Try importing Google GenAI
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

def analyze_sentiment_local(text: str) -> Dict[str, Any]:
    """Fast, accurate rule-based sentiment and emotion polarity analyzer."""
    text_lower = text.lower()
    
    positive_words = [
        "thank", "thanks", "great", "excellent", "awesome", "appreciate", "helpful",
        "love", "fantastic", "pleasure", "glad", "wonderful", "delighted", "kudos"
    ]
    negative_words = [
        "disappointed", "poor", "bad", "slow", "broken", "issue", "bug", "error",
        "fail", "problem", "difficult", "confused", "delayed", "wrong", "missing"
    ]
    frustrated_words = [
        "unacceptable", "furious", "angry", "horrible", "terrible", "worst",
        "disgusted", "lawyer", "attorney", "sue", "scam", "cheat", "rip off", "waste"
    ]
    
    pos_count = sum(1 for w in positive_words if w in text_lower)
    neg_count = sum(1 for w in negative_words if w in text_lower)
    frust_count = sum(1 for w in frustrated_words if w in text_lower)
    
    if frust_count >= 1:
        sentiment = "Highly Frustrated"
        score = -0.85
    elif neg_count > pos_count:
        sentiment = "Negative"
        score = -0.5
    elif pos_count > neg_count:
        sentiment = "Positive"
        score = 0.7
    else:
        sentiment = "Neutral"
        score = 0.0
        
    return {
        "sentiment": sentiment,
        "sentiment_score": score
    }

def detect_priority_local(text: str, category: str, sentiment: str) -> str:
    """Local heuristic priority detection."""
    text_lower = text.lower()
    
    if any(k in text_lower for k in ["outage", "production down", "emergency", "system down", "data breach", "legal action", "sue"]):
        return "Critical"
    if sentiment == "Highly Frustrated" or category == "Complaints":
        return "High"
    if any(k in text_lower for k in ["asap", "immediately", "urgent", "charged twice", "double charge", "refund", "cannot login"]):
        return "High"
    if category in ["Billing", "Technical Issues"]:
        return "Medium"
    if any(k in text_lower for k in ["when you have time", "no rush", "casual inquiry", "general question"]):
        return "Low"
    return "Medium"

def summarize_text_local(subject: str, body: str) -> str:
    """Creates a clean extractive 1-2 sentence summary."""
    lines = [l.strip() for l in body.split("\n") if l.strip()]
    if not lines:
        return subject
    # Pick first 1-2 substantive sentences
    sentences = re.split(r'(?<=[.!?])\s+', " ".join(lines))
    substantive = [s for s in sentences if len(s.split()) > 4 and not s.lower().startswith(("hi", "hello", "dear", "thanks", "regards"))]
    if substantive:
        summary = " ".join(substantive[:2])
    else:
        summary = lines[0]
    return summary[:220]

def analyze_with_gemini(subject: str, body: str, sender: str, api_key: str) -> Optional[Dict[str, Any]]:
    """Analyzes email using Google Gemini LLM API."""
    if not GENAI_AVAILABLE or not api_key:
        return None
        
    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""
You are an expert enterprise email classification AI. Analyze the following incoming email and output ONLY valid JSON matching this schema:
{{
  "category": "Customer Support" | "Billing" | "Technical Issues" | "Sales" | "Complaints" | "HR" | "Job Applications" | "General Queries" | "Spam",
  "priority": "Low" | "Medium" | "High" | "Critical",
  "confidence_score": <number between 70.0 and 99.9>,
  "sentiment": "Positive" | "Neutral" | "Negative" | "Highly Frustrated",
  "sentiment_score": <number between -1.0 and 1.0>,
  "summary": "<1-2 sentence executive summary of customer issue and intent>",
  "customer_name": "<Customer Name>",
  "identified_issue": "<concise issue description>",
  "required_action": "<recommended action for department>"
}}

EMAIL:
Sender: {sender}
Subject: {subject}
Body:
{body}
"""
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2
            )
        )
        data = json.loads(response.text)
        return data
    except Exception as e:
        print(f"Gemini API analysis notice: {e}, falling back to local ML engine.")
        return None

def process_email(
    subject: str,
    body: str,
    sender: str = "customer@example.com",
    sender_name: str = "",
    custom_id: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Complete end-to-end pipeline:
    Duplicate Check -> Spam Detection -> Classification -> Sentiment ->
    Information Extraction -> Risk & Urgency Engine -> Smart Routing -> Response Generation.
    """
    email_id = custom_id or f"EML-{int(datetime.now().timestamp() * 1000) % 100000:05d}"
    content_hash = generate_content_hash(subject, body)
    full_text = f"{subject}\n{body}"
    
    # 1. Duplicate Detection
    existing_emails = get_all_emails(limit=60)
    is_dup, dup_of, similarity = check_duplicate(content_hash, subject, body, existing_emails)
    
    # 2. Spam Detection
    is_spam, spam_score, spam_flags = detect_spam(subject, body, sender)
    
    # 3. Information Extraction
    entities = extract_entities(subject, body, sender, sender_name)
    
    # 4. Classification & Sentiment: Gemini or Local
    gemini_result = None
    if api_key or os.getenv("GEMINI_API_KEY"):
        key_to_use = api_key or os.getenv("GEMINI_API_KEY")
        gemini_result = analyze_with_gemini(subject, body, sender, key_to_use)
        
    if gemini_result:
        category = gemini_result.get("category", "General Queries")
        if category not in CATEGORIES:
            category = "General Queries"
        priority = gemini_result.get("priority", "Medium")
        confidence = float(gemini_result.get("confidence_score", 95.0))
        sentiment = gemini_result.get("sentiment", "Neutral")
        sentiment_score = float(gemini_result.get("sentiment_score", 0.0))
        summary = gemini_result.get("summary", summarize_text_local(subject, body))
        if gemini_result.get("identified_issue"):
            entities["identified_issue"] = gemini_result["identified_issue"]
        if gemini_result.get("required_action"):
            entities["required_action"] = gemini_result["required_action"]
        source = "Gemini 2.5 Flash"
    else:
        # Local ML Pipeline
        if is_spam:
            category = "Spam"
            confidence = max(88.0, spam_score)
        else:
            category, confidence = local_classifier.predict(full_text)
            
        sentiment_res = analyze_sentiment_local(full_text)
        sentiment = sentiment_res["sentiment"]
        sentiment_score = sentiment_res["sentiment_score"]
        priority = detect_priority_local(full_text, category, sentiment)
        summary = summarize_text_local(subject, body)
        source = "Local ML (TF-IDF + Calibrated Model)"

    # If spam was detected strongly by heuristics, ensure category is Spam
    if is_spam and category != "Spam" and spam_score >= 70:
        category = "Spam"
        priority = "Low"
        
    # 5. Smart Routing
    routing_result = route_email(category, priority, subject, body, sender)
    department = routing_result["department"]
    assigned_agent = routing_result["assigned_agent"]
    sla_deadline = routing_result["sla_deadline"]
    dept_load = routing_result["department_load_ratio"]
    
    # 6. AI Risk & Urgency Engine
    risk_profile = calculate_risk_profile(
        subject=subject,
        body=body,
        category=category,
        sentiment=sentiment,
        sentiment_score=sentiment_score,
        priority=priority,
        has_explicit_deadline=entities.get("has_explicit_deadline", False),
        monetary_amounts=entities.get("monetary_amounts", []),
        current_dept_load=dept_load
    )
    
    # 7. Suggested Response
    suggested_response = generate_draft_response(
        category=category,
        sentiment=sentiment,
        entities=entities,
        subject=subject,
        body=body,
        assigned_agent=assigned_agent
    )
    
    # Status
    status = "Quarantined" if is_spam else "New"
    if is_dup:
        status = "Duplicate"

    return {
        "id": email_id,
        "message_id": f"msg-{email_id}",
        "sender": sender,
        "sender_name": entities.get("customer_name") or sender_name or "Anonymous",
        "subject": subject,
        "body": body,
        "received_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "category": category,
        "priority": priority,
        "urgency_level": priority,
        "sentiment": sentiment,
        "sentiment_score": sentiment_score,
        "confidence_score": confidence,
        "risk_score": risk_profile["risk_score"],
        "risk_factors": risk_profile,
        "department": department,
        "assigned_agent": assigned_agent,
        "summary": summary,
        "extracted_entities": entities,
        "suggested_action": entities.get("required_action", "Review and triage"),
        "suggested_response": suggested_response,
        "status": status,
        "is_spam": is_spam,
        "spam_score": spam_score,
        "is_duplicate": is_dup,
        "duplicate_of_id": dup_of,
        "sla_deadline": sla_deadline,
        "sla_breached": False,
        "classification_source": source,
        "content_hash": content_hash
    }
