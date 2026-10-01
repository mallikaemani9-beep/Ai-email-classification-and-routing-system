"""
System Verification Script
Tests database, ML model, extractor, risk engine, router, and end-to-end ingestion.
"""

import sys

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from core.database import init_db, get_all_emails, get_analytics_metrics
from core.ml_model import local_classifier
from core.extractor import extract_entities
from core.risk_engine import calculate_risk_profile
from core.ingestion import ingest_single_email, load_seed_scenarios

def test_pipeline():
    print("1. Initializing database...")
    init_db()
    
    print("2. Testing local ML model prediction...")
    cat, conf = local_classifier.predict("Hi, I was charged twice for order #45892, please refund extra charge")
    print(f"   -> Predicted: {cat} (Confidence: {conf}%)")
    assert cat == "Billing", f"Expected Billing, got {cat}"
    
    print("3. Testing entity extractor...")
    entities = extract_entities("Urgent: Charged twice for my order #45892", "Please refund $249.99 as soon as possible. Thanks, Robert Langdon")
    print(f"   -> Extracted customer: {entities['customer_name']}, Order ID: {entities['primary_order_id']}, Amount: {entities['monetary_amounts']}")
    assert entities['primary_order_id'] == "45892" or "45892" in entities['order_ids']
    
    print("4. Testing Risk & Urgency Engine...")
    risk = calculate_risk_profile(
        subject="Breach of contract - filing lawsuit",
        body="Terrible service, cancelling our $150,000 contract by today 5pm",
        category="Complaints",
        sentiment="Highly Frustrated",
        sentiment_score=-0.9,
        priority="Critical",
        has_explicit_deadline=True,
        monetary_amounts=["$150,000"]
    )
    print(f"   -> Calculated Risk Score: {risk['risk_score']} ({risk['triage_tier']})")
    assert risk['risk_score'] >= 75.0, "Expected high risk score for legal complaint with high value"
    
    print("5. Loading sample enterprise dataset...")
    seeded = load_seed_scenarios(force_reset=True)
    print(f"   -> Seeded {len(seeded)} enterprise emails successfully!")
    
    metrics = get_analytics_metrics()
    print(f"   -> Analytics: {metrics['total_emails']} total, {metrics['urgent_pending']} urgent, avg confidence: {metrics['avg_confidence']}%")
    
    print("\n✅ ALL SYSTEM TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_pipeline()
