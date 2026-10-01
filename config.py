"""
System Configuration & Constants
AI-Powered Email Classification and Routing System
"""

import os

# Application Info
APP_TITLE = "MailPulse AI"
APP_SUBTITLE = "Enterprise AI Email Classification, Risk Triage & Smart Routing System"
VERSION = "2.0.0"

# Supported Categories
CATEGORIES = [
    "Customer Support",
    "Billing",
    "Technical Issues",
    "Sales",
    "Complaints",
    "HR",
    "Job Applications",
    "General Queries",
    "Spam"
]

# Priorities and SLA Hours
PRIORITIES = {
    "Critical": {"sla_hours": 1, "color": "#EF4444", "badge": "🚨 Critical"},
    "High": {"sla_hours": 4, "color": "#F97316", "badge": "⚡ High"},
    "Medium": {"sla_hours": 12, "color": "#F59E0B", "badge": "⏳ Medium"},
    "Low": {"sla_hours": 24, "color": "#10B981", "badge": "☕ Low"}
}

# Departments, default agents, and capacities
DEPARTMENTS = {
    "Finance & Billing": {
        "agents": ["Sarah Jenkins (Lead)", "David Vance", "Elena Rostova"],
        "max_capacity": 25,
        "keywords": ["invoice", "charge", "refund", "billing", "payment", "subscription", "receipt", "credit card", "bank", "overcharged", "duplicate transaction"]
    },
    "Customer Support": {
        "agents": ["Emily Watson (Lead)", "Carlos Mendez", "Chloe Bennett"],
        "max_capacity": 40,
        "keywords": ["help", "assistance", "how to", "order status", "delivery", "tracking", "guide", "inquiry", "account access", "password reset"]
    },
    "Tech Support & IT Ops": {
        "agents": ["Alex Rivera (Lead)", "Priya Patel", "Marcus Sterling"],
        "max_capacity": 20,
        "keywords": ["bug", "error", "crash", "api", "database", "500", "server", "glitch", "broken", "timeout", "downtime", "deployment", "ssl", "stack trace"]
    },
    "Sales & Enterprise BD": {
        "agents": ["Marcus Sterling (Lead)", "Rachel Torres", "Daniel Craig"],
        "max_capacity": 30,
        "keywords": ["pricing", "demo", "enterprise plan", "quote", "partnership", "contract", "license", "procurement", "rfp", "purchase order"]
    },
    "Executive Escalations": {
        "agents": ["Rachel Torres (Director)", "Michael Chang (VP)"],
        "max_capacity": 10,
        "keywords": ["unacceptable", "lawyer", "attorney", "sue", "legal action", "furious", "cancel contract", "supervisor", "ceo", "terrible service", "scam"]
    },
    "People Operations (HR)": {
        "agents": ["Jessica Alba (HR Director)", "Mark Sullivan"],
        "max_capacity": 20,
        "keywords": ["leave", "payroll", "benefits", "health insurance", "workplace", "onboarding", "policy", "harassment", "internal transfer", "employee"]
    },
    "Talent Acquisition": {
        "agents": ["Chloe Bennett (Recruiter)", "Amanda Lee"],
        "max_capacity": 35,
        "keywords": ["resume", "cv", "application", "job opening", "interview", "portfolio", "hiring", "candidate", "role", "linkedin profile"]
    },
    "General Office & Info": {
        "agents": ["Amanda Lee (Front Desk)", "System Bot"],
        "max_capacity": 50,
        "keywords": ["hours", "address", "location", "contact", "press", "media", "general", "feedback", "event", "office"]
    },
    "Quarantine / Security": {
        "agents": ["Automated Security Bot", "SecOps Team"],
        "max_capacity": 100,
        "keywords": ["lottery", "wire transfer", "inheritance", "crypto giveaway", "urgent bank update", "verify password now", "winner", "casino"]
    }
}

# Category to Default Department Mapping
CATEGORY_TO_DEPARTMENT = {
    "Billing": "Finance & Billing",
    "Customer Support": "Customer Support",
    "Technical Issues": "Tech Support & IT Ops",
    "Sales": "Sales & Enterprise BD",
    "Complaints": "Executive Escalations",
    "HR": "People Operations (HR)",
    "Job Applications": "Talent Acquisition",
    "General Queries": "General Office & Info",
    "Spam": "Quarantine / Security"
}

# AI Risk Engine Weights
RISK_WEIGHTS = {
    "urgency": 0.30,
    "sentiment": 0.25,
    "impact": 0.25,
    "deadline_proximity": 0.10,
    "department_load": 0.10
}

# Database Path
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "email_system.db")
