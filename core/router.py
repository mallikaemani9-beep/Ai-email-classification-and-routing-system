"""
Smart Department Routing & Workload Management Engine
Routes emails to responsible departments/agents based on:
1. Custom Dynamic Rules (Priority 1)
2. AI Category Predictions (Priority 2)
3. Department Workload & Capacity Balancing
4. SLA Deadline Calculation
"""

import random
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, Optional, List
from config import CATEGORY_TO_DEPARTMENT, DEPARTMENTS, PRIORITIES
from core.database import get_connection, get_routing_rules

def calculate_sla_deadline(priority: str) -> Tuple[str, int]:
    """Calculates SLA deadline timestamp and allotted hours."""
    sla_info = PRIORITIES.get(priority, PRIORITIES["Medium"])
    hours = sla_info["sla_hours"]
    deadline = datetime.now() + timedelta(hours=hours)
    return deadline.strftime("%Y-%m-%d %H:%M:%S"), hours

def get_department_workload_ratio(department: str) -> float:
    """Calculates active load ratio (0.0 to 1.0+) of the specified department."""
    dept_meta = DEPARTMENTS.get(department)
    max_cap = dept_meta["max_capacity"] if dept_meta else 30
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM emails 
            WHERE department = ? AND status NOT IN ('Resolved', 'Quarantined')
        """, (department,))
        active_count = cursor.fetchone()[0]
        
    return min(1.2, active_count / max(1, max_cap))

def evaluate_custom_rules(subject: str, body: str, sender: str) -> Optional[Dict[str, Any]]:
    """Evaluates user-configured dynamic rules stored in SQLite."""
    rules = get_routing_rules()
    text_data = {
        "subject": subject.lower(),
        "body": body.lower(),
        "sender": sender.lower()
    }
    
    for rule in rules:
        field = rule.get("condition_field", "subject").lower()
        op = rule.get("condition_operator", "contains").lower()
        val = rule.get("condition_value", "").lower()
        
        target_text = text_data.get(field, "")
        matched = False
        
        if op == "contains" and val in target_text:
            matched = True
        elif op == "starts_with" and target_text.startswith(val):
            matched = True
        elif op == "equals" and target_text == val:
            matched = True
            
        if matched:
            return {
                "matched_rule_id": rule["id"],
                "rule_name": rule["rule_name"],
                "department": rule["target_department"],
                "assigned_agent": rule.get("target_agent") or "",
                "priority_override": rule.get("priority_override") or None
            }
            
    return None

def route_email(
    category: str,
    priority: str,
    subject: str,
    body: str,
    sender: str
) -> Dict[str, Any]:
    """
    Determines final Department, Assigned Agent, and SLA Target.
    """
    # 1. Check custom user rules
    custom_rule = evaluate_custom_rules(subject, body, sender)
    if custom_rule:
        dept = custom_rule["department"]
        agent = custom_rule["assigned_agent"]
        if custom_rule["priority_override"]:
            priority = custom_rule["priority_override"]
        routing_notes = f"Routed via Custom Automation Rule: '{custom_rule['rule_name']}'"
    else:
        # 2. Default mapping
        dept = CATEGORY_TO_DEPARTMENT.get(category, "General Office & Info")
        agent = ""
        routing_notes = f"Auto-routed based on AI Category: {category}"

    # 3. Select agent if not specified
    dept_info = DEPARTMENTS.get(dept, DEPARTMENTS["General Office & Info"])
    available_agents = dept_info["agents"]
    if not agent or agent not in available_agents:
        # Pick agent with low workload or pseudo round-robin
        agent = random.choice(available_agents)
        
    # 4. Compute SLA
    sla_deadline, sla_hours = calculate_sla_deadline(priority)
    
    # 5. Workload Ratio
    load_ratio = get_department_workload_ratio(dept)
    
    return {
        "department": dept,
        "assigned_agent": agent,
        "priority": priority,
        "sla_deadline": sla_deadline,
        "sla_hours": sla_hours,
        "department_load_ratio": round(load_ratio, 2),
        "routing_notes": routing_notes
    }
