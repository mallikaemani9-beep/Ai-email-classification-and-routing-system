"""
Database Layer for AI Email Classification and Routing System
SQLite implementation with full transaction support, audit logs, and feedback loop tracking.
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "email_system.db")

def ensure_db_dir():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

def get_connection() -> sqlite3.Connection:
    ensure_db_dir()
    conn = sqlite3.connect(DB_FILE, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes all necessary database tables and indexes."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Emails Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id TEXT PRIMARY KEY,
                message_id TEXT,
                sender TEXT NOT NULL,
                sender_name TEXT,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                urgency_level TEXT,
                sentiment TEXT,
                sentiment_score REAL DEFAULT 0.0,
                confidence_score REAL DEFAULT 0.0,
                risk_score REAL DEFAULT 0.0,
                risk_factors TEXT,
                department TEXT NOT NULL,
                assigned_agent TEXT,
                summary TEXT,
                extracted_entities TEXT,
                suggested_action TEXT,
                suggested_response TEXT,
                status TEXT DEFAULT 'New',
                is_spam INTEGER DEFAULT 0,
                spam_score REAL DEFAULT 0.0,
                is_duplicate INTEGER DEFAULT 0,
                duplicate_of_id TEXT,
                sla_deadline TIMESTAMP,
                sla_breached INTEGER DEFAULT 0,
                classification_source TEXT DEFAULT 'AI Engine',
                content_hash TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. Human-in-the-Loop Feedback Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id TEXT NOT NULL,
                old_category TEXT,
                new_category TEXT,
                old_priority TEXT,
                new_priority TEXT,
                old_department TEXT,
                new_department TEXT,
                feedback_notes TEXT,
                corrected_by TEXT DEFAULT 'Human Admin',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (email_id) REFERENCES emails (id)
            )
        """)
        
        # 3. System Audit Logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id TEXT,
                action TEXT NOT NULL,
                details TEXT,
                actor TEXT DEFAULT 'AI Engine',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 4. Custom Dynamic Routing Rules
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS routing_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_name TEXT NOT NULL,
                condition_field TEXT NOT NULL,
                condition_operator TEXT NOT NULL,
                condition_value TEXT NOT NULL,
                target_department TEXT NOT NULL,
                target_agent TEXT,
                priority_override TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Indexes for fast querying
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_emails_cat ON emails(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_emails_prio ON emails(priority)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_emails_dept ON emails(department)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_emails_status ON emails(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_emails_hash ON emails(content_hash)")
        
        conn.commit()

# --- Email Operations ---

def save_email(email_data: Dict[str, Any]) -> str:
    """Inserts or updates an email record."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Serialize JSON fields if dict/list
        risk_factors_json = json.dumps(email_data.get("risk_factors", {})) if isinstance(email_data.get("risk_factors"), (dict, list)) else email_data.get("risk_factors", "{}")
        extracted_entities_json = json.dumps(email_data.get("extracted_entities", {})) if isinstance(email_data.get("extracted_entities"), (dict, list)) else email_data.get("extracted_entities", "{}")
        
        sql = """
            INSERT OR REPLACE INTO emails (
                id, message_id, sender, sender_name, subject, body, received_at,
                category, priority, urgency_level, sentiment, sentiment_score,
                confidence_score, risk_score, risk_factors, department, assigned_agent,
                summary, extracted_entities, suggested_action, suggested_response,
                status, is_spam, spam_score, is_duplicate, duplicate_of_id,
                sla_deadline, sla_breached, classification_source, content_hash, updated_at
            ) VALUES (
                :id, :message_id, :sender, :sender_name, :subject, :body, :received_at,
                :category, :priority, :urgency_level, :sentiment, :sentiment_score,
                :confidence_score, :risk_score, :risk_factors, :department, :assigned_agent,
                :summary, :extracted_entities, :suggested_action, :suggested_response,
                :status, :is_spam, :spam_score, :is_duplicate, :duplicate_of_id,
                :sla_deadline, :sla_breached, :classification_source, :content_hash, :updated_at
            )
        """
        
        params = {
            "id": email_data["id"],
            "message_id": email_data.get("message_id", f"msg-{email_data['id']}"),
            "sender": email_data.get("sender", "unknown@domain.com"),
            "sender_name": email_data.get("sender_name", "Anonymous"),
            "subject": email_data.get("subject", "No Subject"),
            "body": email_data.get("body", ""),
            "received_at": email_data.get("received_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "category": email_data.get("category", "General Queries"),
            "priority": email_data.get("priority", "Medium"),
            "urgency_level": email_data.get("urgency_level", "Medium"),
            "sentiment": email_data.get("sentiment", "Neutral"),
            "sentiment_score": float(email_data.get("sentiment_score", 0.0)),
            "confidence_score": float(email_data.get("confidence_score", 85.0)),
            "risk_score": float(email_data.get("risk_score", 50.0)),
            "risk_factors": risk_factors_json,
            "department": email_data.get("department", "General Office & Info"),
            "assigned_agent": email_data.get("assigned_agent", "Unassigned"),
            "summary": email_data.get("summary", ""),
            "extracted_entities": extracted_entities_json,
            "suggested_action": email_data.get("suggested_action", ""),
            "suggested_response": email_data.get("suggested_response", ""),
            "status": email_data.get("status", "New"),
            "is_spam": 1 if email_data.get("is_spam") else 0,
            "spam_score": float(email_data.get("spam_score", 0.0)),
            "is_duplicate": 1 if email_data.get("is_duplicate") else 0,
            "duplicate_of_id": email_data.get("duplicate_of_id"),
            "sla_deadline": email_data.get("sla_deadline"),
            "sla_breached": 1 if email_data.get("sla_breached") else 0,
            "classification_source": email_data.get("classification_source", "AI Engine"),
            "content_hash": email_data.get("content_hash", ""),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        cursor.execute(sql, params)
        conn.commit()
        
        # Log Ingestion/Update
        add_audit_log(
            email_id=email_data["id"],
            action="Email Stored",
            details=f"Category: {email_data.get('category')} | Department: {email_data.get('department')} | Priority: {email_data.get('priority')}",
            actor=email_data.get("classification_source", "AI Engine")
        )
        
        return email_data["id"]

def get_email_by_id(email_id: str) -> Optional[Dict[str, Any]]:
    """Fetches a single email record with decoded JSON fields."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM emails WHERE id = ?", (email_id,))
        row = cursor.fetchone()
        if not row:
            return None
        
        d = dict(row)
        try:
            d["risk_factors"] = json.loads(d.get("risk_factors") or "{}")
        except:
            d["risk_factors"] = {}
        try:
            d["extracted_entities"] = json.loads(d.get("extracted_entities") or "{}")
        except:
            d["extracted_entities"] = {}
            
        return d

def get_all_emails(
    search_query: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    department: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: str = "risk_score",
    sort_desc: bool = True,
    limit: int = 200
) -> List[Dict[str, Any]]:
    """Retrieves emails with multi-dimensional filtering, searching, and risk ranking."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        query = "SELECT * FROM emails WHERE 1=1"
        params = []
        
        if search_query:
            query += " AND (subject LIKE ? OR body LIKE ? OR sender LIKE ? OR sender_name LIKE ? OR id LIKE ?)"
            like_term = f"%{search_query}%"
            params.extend([like_term, like_term, like_term, like_term, like_term])
            
        if category and category != "All":
            query += " AND category = ?"
            params.append(category)
            
        if priority and priority != "All":
            query += " AND priority = ?"
            params.append(priority)
            
        if department and department != "All":
            query += " AND department = ?"
            params.append(department)
            
        if status and status != "All":
            query += " AND status = ?"
            params.append(status)
            
        allowed_sorts = ["risk_score", "received_at", "priority", "confidence_score", "sla_deadline"]
        order_col = sort_by if sort_by in allowed_sorts else "risk_score"
        direction = "DESC" if sort_desc else "ASC"
        
        query += f" ORDER BY {order_col} {direction} LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            d = dict(row)
            try:
                d["risk_factors"] = json.loads(d.get("risk_factors") or "{}")
            except:
                d["risk_factors"] = {}
            try:
                d["extracted_entities"] = json.loads(d.get("extracted_entities") or "{}")
            except:
                d["extracted_entities"] = {}
            results.append(d)
            
        return results

def find_duplicate_by_hash(content_hash: str) -> Optional[Dict[str, Any]]:
    """Looks for an existing email with the same content hash."""
    if not content_hash:
        return None
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, subject, received_at FROM emails WHERE content_hash = ? LIMIT 1", (content_hash,))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_email_status(email_id: str, new_status: str, actor: str = "Agent"):
    """Updates status (e.g. 'In Progress', 'Resolved', 'Quarantined')."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE emails SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
        """, (new_status, email_id))
        conn.commit()
        add_audit_log(email_id, "Status Updated", f"Status changed to {new_status}", actor)

def update_suggested_response(email_id: str, new_response: str):
    """Saves edited response draft."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE emails SET suggested_response = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
        """, (new_response, email_id))
        conn.commit()
        add_audit_log(email_id, "Draft Edited", "Agent refined the AI suggested draft response", "Agent")

def save_human_correction(
    email_id: str,
    new_category: str,
    new_priority: str,
    new_department: str,
    feedback_notes: str = "",
    corrected_by: str = "Human Reviewer"
) -> bool:
    """
    Applies human-in-the-loop correction to an email and logs the feedback
    for model fine-tuning and retraining.
    """
    email = get_email_by_id(email_id)
    if not email:
        return False
        
    old_category = email["category"]
    old_priority = email["priority"]
    old_department = email["department"]
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Update email record
        cursor.execute("""
            UPDATE emails SET
                category = ?,
                priority = ?,
                department = ?,
                classification_source = 'Human Correction',
                confidence_score = 100.0,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (new_category, new_priority, new_department, email_id))
        
        # 2. Record in feedback table
        cursor.execute("""
            INSERT INTO feedback_logs (
                email_id, old_category, new_category,
                old_priority, new_priority, old_department, new_department,
                feedback_notes, corrected_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            email_id, old_category, new_category,
            old_priority, new_priority, old_department, new_department,
            feedback_notes, corrected_by
        ))
        
        conn.commit()
        
    # 3. Add to audit log
    add_audit_log(
        email_id=email_id,
        action="Human Correction",
        details=f"Changed: Cat({old_category} -> {new_category}), Prio({old_priority} -> {new_priority}), Dept({old_department} -> {new_department})",
        actor=corrected_by
    )
    return True

def get_feedback_logs(limit: int = 100) -> List[Dict[str, Any]]:
    """Returns human-in-the-loop corrections for ML model retraining/evaluation."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT f.*, e.subject, e.body 
            FROM feedback_logs f
            LEFT JOIN emails e ON f.email_id = e.id
            ORDER BY f.timestamp DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

def add_audit_log(email_id: Optional[str], action: str, details: str, actor: str = "AI Engine"):
    """Inserts an immutable audit log record."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_logs (email_id, action, details, actor)
                VALUES (?, ?, ?, ?)
            """, (email_id, action, details, actor))
            conn.commit()
    except Exception as e:
        print(f"Error logging audit: {e}")

def get_audit_logs(email_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    """Retrieves system activity audit trails."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if email_id:
            cursor.execute("""
                SELECT * FROM audit_logs WHERE email_id = ? ORDER BY timestamp DESC LIMIT ?
            """, (email_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?
            """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

def get_analytics_metrics() -> Dict[str, Any]:
    """Computes comprehensive dashboard KPIs and distribution stats."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Total counts
        cursor.execute("SELECT COUNT(*) FROM emails")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM emails WHERE priority IN ('High', 'Critical') AND status != 'Resolved'")
        urgent_pending = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(confidence_score) FROM emails")
        avg_confidence = cursor.fetchone()[0] or 0.0
        
        cursor.execute("SELECT COUNT(*) FROM emails WHERE is_spam = 1")
        spam_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM emails WHERE is_duplicate = 1")
        duplicate_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM emails WHERE status = 'Resolved'")
        resolved_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM feedback_logs")
        corrections_count = cursor.fetchone()[0]

        # Category distribution
        cursor.execute("SELECT category, COUNT(*) as count FROM emails GROUP BY category ORDER BY count DESC")
        category_dist = [{"category": row["category"], "count": row["count"]} for row in cursor.fetchall()]

        # Priority distribution
        cursor.execute("SELECT priority, COUNT(*) as count FROM emails GROUP BY priority")
        priority_dist = [{"priority": row["priority"], "count": row["count"]} for row in cursor.fetchall()]

        # Department workload
        cursor.execute("""
            SELECT department, 
                   COUNT(*) as total_tickets,
                   SUM(CASE WHEN status != 'Resolved' THEN 1 ELSE 0 END) as active_tickets
            FROM emails 
            GROUP BY department
        """)
        department_workload = [
            {"department": row["department"], "total": row["total_tickets"], "active": row["active_tickets"]} 
            for row in cursor.fetchall()
        ]

        # Sentiment breakdown
        cursor.execute("SELECT sentiment, COUNT(*) as count FROM emails GROUP BY sentiment")
        sentiment_dist = [{"sentiment": row["sentiment"], "count": row["count"]} for row in cursor.fetchall()]

        return {
            "total_emails": total,
            "urgent_pending": urgent_pending,
            "avg_confidence": round(avg_confidence, 1),
            "spam_count": spam_count,
            "duplicate_count": duplicate_count,
            "resolved_count": resolved_count,
            "corrections_count": corrections_count,
            "category_distribution": category_dist,
            "priority_distribution": priority_dist,
            "department_workload": department_workload,
            "sentiment_distribution": sentiment_dist
        }

def get_routing_rules() -> List[Dict[str, Any]]:
    """Returns custom dynamic routing rules."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM routing_rules WHERE is_active = 1 ORDER BY id ASC")
        return [dict(r) for r in cursor.fetchall()]

def add_routing_rule(name: str, field: str, op: str, value: str, dept: str, agent: str = "", priority_override: str = ""):
    """Adds a new automated routing rule."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO routing_rules (rule_name, condition_field, condition_operator, condition_value, target_department, target_agent, priority_override)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, field, op, value, dept, agent, priority_override))
        conn.commit()

def delete_routing_rule(rule_id: int):
    """Deletes a routing rule."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM routing_rules WHERE id = ?", (rule_id,))
        conn.commit()

def clear_all_data():
    """Resets database for testing purposes."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM emails")
        cursor.execute("DELETE FROM feedback_logs")
        cursor.execute("DELETE FROM audit_logs")
        conn.commit()
