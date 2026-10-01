"""
Email Ingestion Engine
Handles:
1. File upload parsing (.eml, .txt, .json)
2. Batch loading of curated enterprise scenarios
3. Direct interactive form submission
4. Simulated real-time inbox stream
"""

import email
from email import policy
from email.parser import BytesParser
import json
from typing import Dict, Any, List, Optional

from core.ai_engine import process_email
from core.database import save_email, get_email_by_id
from data.sample_emails import SAMPLE_EMAILS

def parse_eml_bytes(file_bytes: bytes) -> Dict[str, str]:
    """Parses RFC822 / MIME .eml file content."""
    msg = BytesParser(policy=policy.default).parsebytes(file_bytes)
    
    subject = msg.get("Subject", "No Subject")
    sender = msg.get("From", "unknown@domain.com")
    
    # Extract sender display name if present
    sender_name = ""
    if "<" in sender:
        parts = sender.split("<")
        sender_name = parts[0].strip().strip('"')
        sender = parts[1].replace(">", "").strip()
    else:
        sender_name = sender.split("@")[0].title()
        
    # Extract plain text body
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))
            if ctype == 'text/plain' and 'attachment' not in cdispo:
                body = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='ignore')
                break
    else:
        body = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8', errors='ignore')
        
    return {
        "subject": subject,
        "sender": sender,
        "sender_name": sender_name,
        "body": body.strip()
    }

def ingest_single_email(
    subject: str,
    body: str,
    sender: str = "customer@domain.com",
    sender_name: str = "",
    custom_id: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """Ingests, classifies, routes, and persists a single incoming email."""
    processed = process_email(
        subject=subject,
        body=body,
        sender=sender,
        sender_name=sender_name,
        custom_id=custom_id,
        api_key=api_key
    )
    save_email(processed)
    return processed

def load_seed_scenarios(api_key: Optional[str] = None, force_reset: bool = False) -> List[Dict[str, Any]]:
    """Loads all 10 curated enterprise scenarios into the database."""
    ingested = []
    for item in SAMPLE_EMAILS:
        # Check if already exists unless force reset
        existing = get_email_by_id(item["id"])
        if existing and not force_reset:
            ingested.append(existing)
            continue
            
        res = ingest_single_email(
            subject=item["subject"],
            body=item["body"],
            sender=item["sender"],
            sender_name=item["sender_name"],
            custom_id=item["id"],
            api_key=api_key
        )
        ingested.append(res)
    return ingested
