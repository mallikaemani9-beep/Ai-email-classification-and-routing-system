"""
MailPulse AI - Enterprise Web UI Server
Runs a lightweight, zero-dependency HTTP server delivering the modern
glassmorphic HTML5/CSS/JavaScript dashboard with live SQLite and AI pipeline integration.
"""

import os
import sys

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import socket
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.database import (
    init_db, get_all_emails, get_email_by_id, save_human_correction,
    update_email_status, get_analytics_metrics
)
from core.ingestion import ingest_single_email, load_seed_scenarios

WEB_DIR = os.path.join(BASE_DIR, "web")

class MailPulseHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == "/api/emails":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            emails = get_all_emails(limit=50)
            formatted = []
            for e in emails:
                formatted.append({
                    "id": e["id"],
                    "sender_name": e.get("sender_name") or e.get("sender", "Anonymous"),
                    "sender": e.get("sender", ""),
                    "subject": e.get("subject", ""),
                    "body": e.get("body", ""),
                    "category": e.get("category", "General Queries"),
                    "priority": e.get("priority", "Medium"),
                    "department": e.get("department", "General Inquiries & Reception"),
                    "agent": e.get("assigned_agent", "Unassigned"),
                    "risk_score": int(e.get("risk_score", 50)),
                    "risk_tier": "Severe Operational Risk" if e.get("risk_score", 0) >= 80 else "Standard Review",
                    "sla_clock": f"⏱️ {e.get('priority')} SLA",
                    "status": "Resolved" if e.get("status") == "Resolved" else "Pending",
                    "confidence": float(e.get("confidence_score", 95.0)),
                    "factors": e.get("risk_factors") or {"urgency": 70, "sentiment": 50, "impact": 60, "deadline": 50},
                    "entities": e.get("extracted_entities") or {}
                })
            self.wfile.write(json.dumps(formatted).encode("utf-8"))
            return

        elif parsed.path == "/api/metrics":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            metrics = get_analytics_metrics()
            self.wfile.write(json.dumps(metrics).encode("utf-8"))
            return

        # Serve static assets from web/
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
        
        try:
            data = json.loads(post_body)
        except:
            data = {}

        if parsed.path == "/api/ingest":
            sender = data.get("sender", "unknown@domain.com")
            subject = data.get("subject", "No Subject")
            body = data.get("body", "")
            
            result = ingest_single_email(
                sender=sender,
                subject=subject,
                body=body
            )
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
            return

        elif parsed.path == "/api/feedback":
            email_id = data.get("email_id")
            new_cat = data.get("new_category")
            new_prio = data.get("new_priority")
            new_dept = data.get("new_department")
            
            if email_id and new_cat:
                save_human_correction(
                    email_id=email_id,
                    old_category=data.get("old_category", ""),
                    new_category=new_cat,
                    old_priority=data.get("old_priority", ""),
                    new_priority=new_prio or "Medium",
                    old_dept=data.get("old_department", ""),
                    new_dept=new_dept or "Tech Support & IT Ops",
                    notes="Saved via Web UI"
                )
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

def find_free_port(start_port=8000):
    port = start_port
    while port < 65535:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("localhost", port)) != 0:
                return port
            port += 1
    return 8000

def main():
    print("=" * 65)
    print("🚀 MailPulse AI - Enterprise Web UI Server")
    print("=" * 65)
    
    # 1. Initialize SQLite Database & Seeds
    init_db()
    existing = get_all_emails(limit=1)
    if not existing:
        print("📦 Seeding initial enterprise test scenarios into SQLite database...")
        load_seed_scenarios()

    port = find_free_port(8000)
    server_address = ("", port)
    
    httpd = ThreadingHTTPServer(server_address, MailPulseHandler)
    url = f"http://localhost:{port}"
    
    print(f"✨ Dashboard live at: {url}")
    print(f"📁 Serving Web UI from: {WEB_DIR}")
    print("⚡ Real-time Triage, Risk Gauges & Response Drafter Ready")
    print("=" * 65)
    print("Press Ctrl+C to stop the server.\n")

    try:
        webbrowser.open(url)
    except:
        pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server gracefully...")
        httpd.server_close()

if __name__ == "__main__":
    main()
