"""
AI Risk & Urgency Engine
Computes dynamic risk score (0-100) and triage ranking based on:
1. Urgency Level
2. Customer Sentiment & Escalation signals
3. Business / Financial Impact
4. Deadline Proximity
5. Department Workload & Backlog pressure
"""

import re
from typing import Dict, Any, List

def calculate_risk_profile(
    subject: str,
    body: str,
    category: str,
    sentiment: str,
    sentiment_score: float,
    priority: str,
    has_explicit_deadline: bool,
    monetary_amounts: List[str],
    current_dept_load: float = 0.5  # 0.0 to 1.0 (load ratio)
) -> Dict[str, Any]:
    """
    Computes a composite multi-factor risk score (0 to 100) and triage priority.
    """
    text = f"{subject} {body}".lower()
    
    # --- Factor 1: Urgency Score (0 - 100) ---
    urgency_base = {
        "Critical": 95,
        "High": 75,
        "Medium": 45,
        "Low": 20
    }.get(priority, 45)
    
    # Boost urgency if explicit urgent tokens exist
    urgent_boost = 0
    if any(k in text for k in ["immediately", "asap", "emergency", "urgent", "right now", "cannot wait", "at once"]):
        urgent_boost += 15
    if any(k in text for k in ["outage", "system down", "site down", "blocking", "production crash"]):
        urgent_boost += 25
    urgency_score = min(100, urgency_base + urgent_boost)
    
    # --- Factor 2: Sentiment & Escalation Impact (0 - 100) ---
    # sentiment_score ranges -1.0 (furious) to +1.0 (happy)
    sentiment_risk = (1.0 - sentiment_score) * 40  # 0 to 80
    
    escalation_flags = []
    if any(k in text for k in ["lawyer", "attorney", "sue", "legal action", "litigation", "court"]):
        sentiment_risk += 30
        escalation_flags.append("Legal escalation threat")
    if any(k in text for k in ["cancel contract", "cancelling subscription", "chargeback", "demand refund", "leaving your service"]):
        sentiment_risk += 20
        escalation_flags.append("Customer churn / chargeback risk")
    if any(k in text for k in ["unacceptable", "furious", "disgusted", "appalling", "terrible", "worst service"]):
        sentiment_risk += 15
        escalation_flags.append("High negative emotional intensity")
        
    sentiment_score_final = min(100, max(10, sentiment_risk))
    
    # --- Factor 3: Business & Financial Impact (0 - 100) ---
    impact_score = 30  # Baseline
    if category in ["Billing", "Complaints"]:
        impact_score += 25
    elif category in ["Technical Issues"]:
        impact_score += 20
    elif category in ["Sales"]:
        impact_score += 35
        
    # Check for large monetary amounts
    has_large_money = False
    for amt in monetary_amounts:
        if amt != "N/A":
            digits = re.sub(r'[^0-9.]', '', amt)
            try:
                val = float(digits)
                if val >= 500:
                    impact_score += 25
                    has_large_money = True
                    escalation_flags.append(f"Significant financial value ({amt})")
            except:
                pass
                
    if any(k in text for k in ["enterprise", "500 users", "all employees", "entire team", "ceo", "director"]):
        impact_score += 20
        escalation_flags.append("Enterprise / VIP account scale")
        
    impact_score = min(100, max(10, impact_score))
    
    # --- Factor 4: Deadline Proximity (0 - 100) ---
    deadline_score = 25
    if has_explicit_deadline:
        deadline_score = 75
        if any(k in text for k in ["today", "2 hours", "1 hour", "asap", "within 24 hours", "eod"]):
            deadline_score = 95
            escalation_flags.append("Critical near-term deadline detected")
        else:
            escalation_flags.append("Specific resolution deadline stated")
            
    # --- Factor 5: Department Workload Multiplier (0 - 100) ---
    # If the assigned department is overloaded (>70%), risk of SLA breach spikes
    dept_load_score = min(100, int(current_dept_load * 100))
    if current_dept_load > 0.8:
        escalation_flags.append("Target department operating at >80% queue capacity")
        
    # --- Calculate Composite Weighted Risk Score ---
    composite_risk = (
        (urgency_score * 0.30) +
        (sentiment_score_final * 0.25) +
        (impact_score * 0.25) +
        (deadline_score * 0.10) +
        (dept_load_score * 0.10)
    )
    
    # In case of spam, suppress operational risk score
    if category == "Spam":
        composite_risk = min(15.0, composite_risk * 0.2)
        escalation_flags = ["Spam Quarantine - No Business Action Required"]
        
    composite_risk = round(composite_risk, 1)
    
    # Assign Triage Tier
    if composite_risk >= 80:
        triage_tier = "🚨 Critical Triage (#1 Immediate)"
        badge_color = "#EF4444"
    elif composite_risk >= 60:
        triage_tier = "⚡ Elevated Priority"
        badge_color = "#F97316"
    elif composite_risk >= 40:
        triage_tier = "⏳ Standard Queue"
        badge_color = "#3B82F6"
    else:
        triage_tier = "☕ Low Risk / Routine"
        badge_color = "#10B981"
        
    return {
        "risk_score": composite_risk,
        "triage_tier": triage_tier,
        "badge_color": badge_color,
        "factors": {
            "urgency": urgency_score,
            "sentiment": sentiment_score_final,
            "impact": impact_score,
            "deadline": deadline_score,
            "department_load": dept_load_score
        },
        "escalation_flags": escalation_flags if escalation_flags else ["Standard processing workflow"]
    }
