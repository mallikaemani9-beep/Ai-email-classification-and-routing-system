"""
MailPulse AI - Enterprise Email Classification, Risk Triage & Smart Routing System
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
from datetime import datetime

from config import (
    APP_TITLE, APP_SUBTITLE, VERSION, CATEGORIES, PRIORITIES,
    DEPARTMENTS, CATEGORY_TO_DEPARTMENT
)
from core.database import (
    init_db, get_all_emails, get_email_by_id, save_human_correction,
    update_email_status, update_suggested_response, get_analytics_metrics,
    get_feedback_logs, get_audit_logs, get_routing_rules, add_routing_rule,
    delete_routing_rule, clear_all_data
)
from core.ingestion import ingest_single_email, parse_eml_bytes, load_seed_scenarios
from core.ml_model import local_classifier

# Page Configuration
st.set_page_config(
    page_title=f"{APP_TITLE} - Intelligent Email Triage",
    page_icon="📨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "static", "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Initialize Database and Seed if Empty
init_db()
existing_check = get_all_emails(limit=1)
if not existing_check:
    load_seed_scenarios()

# Session State Management
if "selected_email_id" not in st.session_state:
    emails = get_all_emails(limit=1)
    st.session_state.selected_email_id = emails[0]["id"] if emails else None
if "api_key" not in st.session_state:
    st.session_state.api_key = os.getenv("GEMINI_API_KEY", "")

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"## ⚡ **{APP_TITLE}**")
    st.caption(f"v{VERSION} | Enterprise AI Email Operations")
    
    st.markdown("---")
    
    # Engine Settings
    st.markdown("### 🧠 AI Engine Status")
    api_key_input = st.text_input(
        "Gemini API Key (Optional)",
        value=st.session_state.api_key,
        type="password",
        help="If provided, uses Gemini 2.5 Flash. Otherwise, runs scikit-learn local ML engine with calibrated probabilities."
    )
    if api_key_input != st.session_state.api_key:
        st.session_state.api_key = api_key_input
        st.rerun()
        
    if st.session_state.api_key:
        st.markdown("""
        <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10B981; border-radius: 8px; padding: 8px 12px; font-size: 12px; color: #34D399; margin-bottom: 12px;">
            ✨ <b>Gemini 2.5 Flash Active</b> (Cloud GenAI)
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: rgba(99, 102, 241, 0.15); border: 1px solid #6366F1; border-radius: 8px; padding: 8px 12px; font-size: 12px; color: #818CF8; margin-bottom: 12px;">
            ⚡ <b>Local Scikit-Learn Active</b> (Zero-latency offline ML)
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Navigation
    menu = st.radio(
        "Navigation",
        [
            "📥 Inbox & Risk Triage Queue",
            "🔍 Email Detail & AI Insights",
            "🚀 Ingest & Test Lab",
            "📊 Analytics & SLA Command Center",
            "⚙️ Routing Rules & Continuous Learning"
        ],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 🛠️ Quick Simulation")
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        if st.button("🔄 Reset Seeds", use_container_width=True):
            clear_all_data()
            load_seed_scenarios(api_key=st.session_state.api_key, force_reset=True)
            st.success("Reset completed!")
            st.rerun()
    with col_sb2:
        if st.button("⚡ Quick Ingest", use_container_width=True):
            now_str = datetime.now().strftime("%H:%M:%S")
            ingest_single_email(
                subject=f"Urgent: Billing discrepancy on credit card [{now_str}]",
                body=f"Hello, I was charged twice for $149.00 under invoice #INV-9921. Please issue a refund immediately.\nThanks, Mark Taylor\nPhone: (555) 441-9920",
                sender="mark.taylor@enterprise.com",
                sender_name="Mark Taylor",
                api_key=st.session_state.api_key
            )
            st.success("New email triaged!")
            st.rerun()

# --- TOP HERO BANNER ---
st.markdown(f"""
<div class="hero-header">
    <div>
        <h1 class="hero-title">{APP_TITLE}</h1>
        <div class="hero-subtitle">{APP_SUBTITLE}</div>
    </div>
    <div style="text-align: right;">
        <span style="background: rgba(99, 102, 241, 0.2); border: 1px solid #6366F1; color: #A5B4FC; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 600;">
            🛡️ AI Risk & Urgency Engine Active
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# Helper function for HTML badges
def get_priority_badge_html(priority: str) -> str:
    p_lower = priority.lower()
    return f'<span class="prio-badge prio-{p_lower}">{priority}</span>'

def get_category_chip_html(cat: str) -> str:
    mapping = {
        "Billing": "cat-billing",
        "Technical Issues": "cat-tech",
        "Customer Support": "cat-support",
        "Sales": "cat-sales",
        "Complaints": "cat-complaints",
        "HR": "cat-hr",
        "Job Applications": "cat-jobs",
        "General Queries": "cat-general",
        "Spam": "cat-spam"
    }
    css_class = mapping.get(cat, "cat-general")
    return f'<span class="cat-chip {css_class}">{cat}</span>'

# ==============================================================================
# VIEW 1: INBOX & RISK TRIAGE QUEUE
# ==============================================================================
if menu == "📥 Inbox & Risk Triage Queue":
    metrics = get_analytics_metrics()
    
    # KPI Metric Cards
    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card" style="--accent-gradient: linear-gradient(90deg, #3B82F6, #60A5FA);">
            <div class="metric-label">Total Ingested</div>
            <div class="metric-val">{metrics['total_emails']}</div>
            <div class="metric-sub">{metrics['resolved_count']} Resolved tickets</div>
        </div>
        <div class="metric-card" style="--accent-gradient: linear-gradient(90deg, #EF4444, #F87171);">
            <div class="metric-label">Urgent / High Risk</div>
            <div class="metric-val">{metrics['urgent_pending']}</div>
            <div class="metric-sub">Requires priority triage</div>
        </div>
        <div class="metric-card" style="--accent-gradient: linear-gradient(90deg, #10B981, #34D399);">
            <div class="metric-label">AI Confidence Avg</div>
            <div class="metric-val">{metrics['avg_confidence']}%</div>
            <div class="metric-sub">Calibrated accuracy</div>
        </div>
        <div class="metric-card" style="--accent-gradient: linear-gradient(90deg, #F59E0B, #FBBF24);">
            <div class="metric-label">Human Corrections</div>
            <div class="metric-val">{metrics['corrections_count']}</div>
            <div class="metric-sub">Reinforcement feedback</div>
        </div>
        <div class="metric-card" style="--accent-gradient: linear-gradient(90deg, #64748B, #94A3B8);">
            <div class="metric-label">Spam & Duplicates</div>
            <div class="metric-val">{metrics['spam_count'] + metrics['duplicate_count']}</div>
            <div class="metric-sub">Quarantined / Filtered</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Filter and Search Bar
    st.markdown("### 📥 Priority Triage Inbox")
    col_search, col_f1, col_f2, col_f3, col_sort = st.columns([2.5, 1.2, 1.2, 1.2, 1.5])
    
    with col_search:
        search_kw = st.text_input("🔍 Search Subject, Sender, or Content", placeholder="Type keywords, order ID, email...")
    with col_f1:
        cat_filter = st.selectbox("Category", ["All"] + CATEGORIES)
    with col_f2:
        prio_filter = st.selectbox("Priority", ["All", "Critical", "High", "Medium", "Low"])
    with col_f3:
        dept_filter = st.selectbox("Department", ["All"] + list(DEPARTMENTS.keys()))
    with col_sort:
        sort_choice = st.selectbox(
            "Sort Order",
            ["AI Risk Score (Highest First)", "Received Time (Newest First)", "Confidence Score", "SLA Deadline Proximity"]
        )
        
    sort_map = {
        "AI Risk Score (Highest First)": ("risk_score", True),
        "Received Time (Newest First)": ("received_at", True),
        "Confidence Score": ("confidence_score", True),
        "SLA Deadline Proximity": ("sla_deadline", False)
    }
    sort_col, sort_desc = sort_map[sort_choice]
    
    emails = get_all_emails(
        search_query=search_kw,
        category=cat_filter,
        priority=prio_filter,
        department=dept_filter,
        sort_by=sort_col,
        sort_desc=sort_desc,
        limit=100
    )
    
    if not emails:
        st.info("No emails match your current search and filter criteria.")
    else:
        st.caption(f"Showing **{len(emails)}** triaged communications ranked dynamically:")
        
        # Render Interactive Cards
        for idx, em in enumerate(emails):
            with st.container():
                risk = em.get("risk_score", 50.0)
                risk_factors = em.get("risk_factors", {})
                triage_tier = risk_factors.get("triage_tier", "Standard Queue") if isinstance(risk_factors, dict) else "Standard Queue"
                badge_color = "#EF4444" if risk >= 80 else ("#F97316" if risk >= 60 else ("#3B82F6" if risk >= 40 else "#10B981"))
                
                c_rank, c_info, c_routing, c_action = st.columns([1.2, 4.5, 3.0, 1.3])
                
                with c_rank:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 12px 8px; background: rgba(30, 41, 59, 0.4); border-radius: 10px; border: 1px solid rgba(255,255,255,0.05);">
                        <div style="font-size: 11px; color: #94A3B8; font-weight: 600;">TRIAGE RANK</div>
                        <div style="font-size: 22px; font-weight: 800; color: #F8FAFC;">#{idx + 1}</div>
                        <div style="margin-top: 6px;">
                            <span style="background: {badge_color}22; color: {badge_color}; border: 1px solid {badge_color}; padding: 2px 6px; border-radius: 6px; font-size: 11px; font-weight: 700;">
                                {risk} RISK
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with c_info:
                    cat_html = get_category_chip_html(em['category'])
                    prio_html = get_priority_badge_html(em['priority'])
                    dup_tag = '<span style="background: #64748B; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; margin-left: 6px;">DUPLICATE</span>' if em.get("is_duplicate") else ''
                    spam_tag = '<span style="background: #DC2626; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; margin-left: 6px;">SPAM</span>' if em.get("is_spam") else ''
                    
                    st.markdown(f"""
                    <div>
                        <div style="margin-bottom: 6px;">
                            {cat_html} {prio_html} {dup_tag} {spam_tag}
                            <span style="font-size: 11px; color: #64748B; margin-left: 8px;">{em['id']} • {em['received_at']}</span>
                        </div>
                        <div style="font-weight: 700; font-size: 15px; color: #F1F5F9; margin-bottom: 4px;">
                            {em['subject']}
                        </div>
                        <div style="font-size: 12px; color: #94A3B8;">
                            From: <b>{em.get('sender_name') or em['sender']}</b> &lt;{em['sender']}&gt;
                        </div>
                        <div style="font-size: 12px; color: #CBD5E1; margin-top: 6px; background: rgba(255,255,255,0.03); padding: 6px 10px; border-radius: 6px; border-left: 2px solid #6366F1;">
                            💡 <i>{em.get('summary') or em['body'][:120] + '...'}</i>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with c_routing:
                    st.markdown(f"""
                    <div style="font-size: 12px; padding: 8px 12px; background: rgba(15, 23, 42, 0.5); border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
                        <div style="color: #94A3B8; margin-bottom: 2px;">Assigned Department:</div>
                        <div style="font-weight: 700; color: #38BDF8; margin-bottom: 6px;">🏢 {em['department']}</div>
                        <div style="color: #94A3B8; margin-bottom: 2px;">Assigned Agent:</div>
                        <div style="color: #E2E8F0; font-weight: 500;">👤 {em.get('assigned_agent', 'Unassigned')}</div>
                        <div style="color: #94A3B8; margin-top: 6px; font-size: 11px;">
                            ⏱️ SLA: <b>{em.get('sla_deadline', 'N/A')}</b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with c_action:
                    st.write("")
                    st.write("")
                    if st.button("Inspect 🔍", key=f"btn_view_{em['id']}", use_container_width=True):
                        st.session_state.selected_email_id = em["id"]
                        st.session_state.nav_target = "🔍 Email Detail & AI Insights"
                        st.rerun()
                        
                st.markdown("<hr style='border: none; border-top: 1px solid rgba(255,255,255,0.06); margin: 12px 0;'>", unsafe_allow_html=True)

# ==============================================================================
# VIEW 2: EMAIL DETAIL & AI INSIGHTS INSPECTOR
# ==============================================================================
elif menu == "🔍 Email Detail & AI Insights":
    st.markdown("### 🔍 Email Intelligence Inspector")
    
    all_emails = get_all_emails(limit=100)
    email_options = {e["id"]: f"{e['id']} | {e['category']} | {e['subject'][:50]}" for e in all_emails}
    
    current_id = st.session_state.get("selected_email_id")
    if current_id not in email_options and all_emails:
        current_id = all_emails[0]["id"]
        
    selected_id = st.selectbox(
        "Select Email to Inspect",
        options=list(email_options.keys()),
        format_func=lambda x: email_options.get(x, x),
        index=list(email_options.keys()).index(current_id) if current_id in email_options else 0
    )
    st.session_state.selected_email_id = selected_id
    
    email_data = get_email_by_id(selected_id)
    if not email_data:
        st.error("Email record not found.")
    else:
        # Header Bar for Selected Email
        col_hdr1, col_hdr2 = st.columns([3, 1])
        with col_hdr1:
            st.markdown(f"### {email_data['subject']}")
            st.caption(f"ID: `{email_data['id']}` • From: **{email_data.get('sender_name')}** &lt;{email_data['sender']}&gt; • Received: {email_data['received_at']}")
        with col_hdr2:
            st.markdown(f"""
            <div style="text-align: right;">
                {get_category_chip_html(email_data['category'])}
                {get_priority_badge_html(email_data['priority'])}
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        
        col_left, col_right = st.columns([1.1, 1.0], gap="large")
        
        # --- LEFT COLUMN: Email Body & Extracted Intelligence ---
        with col_left:
            st.markdown("#### 📄 Original Email Content")
            st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 18px; font-size: 13.5px; line-height: 1.6; color: #E2E8F0; white-space: pre-wrap; max-height: 300px; overflow-y: auto;">
{email_data['body']}
            </div>
            """, unsafe_allow_html=True)
            
            # AI Executive Summary
            st.markdown("#### 💡 AI Executive Summary")
            st.markdown(f"""
            <div class="ai-summary-box">
                {email_data.get('summary') or 'Summary not available.'}
            </div>
            """, unsafe_allow_html=True)
            
            # Extracted Structured Information
            st.markdown("#### 🏷️ Extracted Entities & Metadata")
            entities = email_data.get("extracted_entities", {})
            if isinstance(entities, dict):
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    st.markdown(f"**Customer Name:** `{entities.get('customer_name', 'N/A')}`")
                    st.markdown(f"**Primary Order/Ref ID:** `{entities.get('primary_order_id', 'N/A')}`")
                    st.markdown(f"**Identified Issue:** {entities.get('identified_issue', 'N/A')}")
                with col_e2:
                    st.markdown(f"**Monetary Value:** `{', '.join(entities.get('monetary_amounts', ['N/A']))}`")
                    st.markdown(f"**Stated Deadlines:** `{', '.join(entities.get('deadlines', ['Standard SLA']))}`")
                    st.markdown(f"**Recommended Action:** {entities.get('required_action', 'N/A')}")
            
            # Spam & Duplicate Signals
            st.markdown("#### 🛡️ Threat & Duplicate Diagnostics")
            c_dup, c_spam = st.columns(2)
            with c_dup:
                if email_data.get("is_duplicate"):
                    st.warning(f"⚠️ **Duplicate Submission Detected**\nOriginal: `{email_data.get('duplicate_of_id')}`")
                else:
                    st.success("✅ **Original Unique Message**")
            with c_spam:
                spam_sc = email_data.get("spam_score", 0.0)
                if email_data.get("is_spam"):
                    st.error(f"🚨 **Quarantined as Spam** ({spam_sc}% score)")
                else:
                    st.success(f"✅ **Clean Email** ({spam_sc}% spam score)")
                    
        # --- RIGHT COLUMN: Risk Engine, Routing, Response & Human Feedback ---
        with col_right:
            st.markdown("#### ⚡ AI Risk & Urgency Engine")
            risk_score = email_data.get("risk_score", 50.0)
            risk_factors = email_data.get("risk_factors", {})
            
            # Risk Gauge Meter
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=risk_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Triage Priority Risk Score (0 - 100)", 'font': {'size': 14, 'color': '#E2E8F0'}},
                number={'suffix': "/100", 'font': {'size': 24, 'color': '#F8FAFC'}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#64748B"},
                    'bar': {'color': "#6366F1"},
                    'bgcolor': "rgba(15, 23, 42, 0.4)",
                    'borderwidth': 1,
                    'bordercolor': "rgba(255,255,255,0.1)",
                    'steps': [
                        {'range': [0, 40], 'color': "rgba(16, 185, 129, 0.25)"},
                        {'range': [40, 60], 'color': "rgba(59, 130, 246, 0.25)"},
                        {'range': [60, 80], 'color': "rgba(249, 115, 22, 0.25)"},
                        {'range': [80, 100], 'color': "rgba(239, 68, 68, 0.3)"}
                    ],
                    'threshold': {
                        'line': {'color': "#EF4444", 'width': 3},
                        'thickness': 0.8,
                        'value': 80
                    }
                }
            ))
            fig_gauge.update_layout(
                height=180,
                margin=dict(l=20, r=20, t=30, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#F8FAFC")
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Risk Factor Factors Breakdown
            if isinstance(risk_factors, dict) and "factors" in risk_factors:
                f_dict = risk_factors["factors"]
                st.caption(
                    f"**Breakdown:** Urgency: `{f_dict.get('urgency')}` | "
                    f"Sentiment Stress: `{f_dict.get('sentiment')}` | "
                    f"Business Impact: `{f_dict.get('impact')}` | "
                    f"Deadline Pressure: `{f_dict.get('deadline')}`"
                )
                if risk_factors.get("escalation_flags"):
                    for flag in risk_factors["escalation_flags"]:
                        st.markdown(f"- ⚠️ *{flag}*")
                        
            st.markdown("---")
            
            # Suggested Response Assistant
            st.markdown("#### ✍️ AI-Generated Suggested Response")
            st.caption("Contextually drafted reply based on extracted issue and customer tone:")
            
            edited_response = st.text_area(
                "Response Draft Editor",
                value=email_data.get("suggested_response", ""),
                height=220,
                key=f"resp_edit_{email_data['id']}"
            )
            
            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1:
                if st.button("💾 Save Edits", use_container_width=True):
                    update_suggested_response(email_data["id"], edited_response)
                    st.success("Draft updated!")
            with col_b2:
                if st.button("✅ Approve & Resolve", use_container_width=True):
                    update_email_status(email_data["id"], "Resolved", actor="Agent")
                    st.success("Ticket marked as Resolved!")
                    st.rerun()
            with col_b3:
                if st.button("🚨 Escalate", use_container_width=True):
                    update_email_status(email_data["id"], "Escalated", actor="Agent")
                    st.warning("Ticket escalated to Senior Specialist!")
                    st.rerun()
                    
            st.markdown("---")
            
            # Human-in-the-Loop Reclassification & Retraining Feedback
            with st.expander("🛠️ Human-in-the-Loop Correction (Retraining Feedback)", expanded=False):
                st.caption("Found an incorrect category or priority? Correct it here. The local AI model will learn from your feedback.")
                
                with st.form(f"correction_form_{email_data['id']}"):
                    new_cat = st.selectbox(
                        "Correct Category",
                        CATEGORIES,
                        index=CATEGORIES.index(email_data["category"]) if email_data["category"] in CATEGORIES else 0
                    )
                    new_prio = st.selectbox(
                        "Correct Priority",
                        ["Critical", "High", "Medium", "Low"],
                        index=["Critical", "High", "Medium", "Low"].index(email_data["priority"])
                    )
                    new_dept = st.selectbox(
                        "Correct Department",
                        list(DEPARTMENTS.keys()),
                        index=list(DEPARTMENTS.keys()).index(email_data["department"]) if email_data["department"] in DEPARTMENTS else 0
                    )
                    fb_notes = st.text_input("Correction Reason / Feedback Notes", placeholder="e.g., Actually regarding contract dispute rather than technical")
                    
                    submitted = st.form_submit_button("Submit Correction to AI Model", use_container_width=True)
                    if submitted:
                        save_human_correction(
                            email_id=email_data["id"],
                            new_category=new_cat,
                            new_priority=new_prio,
                            new_department=new_dept,
                            feedback_notes=fb_notes,
                            corrected_by="Human Reviewer"
                        )
                        st.success("Feedback submitted and saved to continuous learning database!")
                        st.rerun()

# ==============================================================================
# VIEW 3: INGEST & TEST LAB
# ==============================================================================
elif menu == "🚀 Ingest & Test Lab":
    st.markdown("### 🚀 Email Ingestion & Simulation Laboratory")
    st.caption("Upload `.eml` files, paste manual email text, or fire one-click realistic test cases.")
    
    tab_manual, tab_upload, tab_presets = st.tabs(["✍️ Compose / Paste Email", "📁 Upload .EML / .TXT", "⚡ Instant Test Scenarios"])
    
    with tab_manual:
        with st.form("manual_ingest_form"):
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                sender_input = st.text_input("Sender Email", value="alice.morgan@enterprise-client.com")
                sender_name_input = st.text_input("Sender Name", value="Alice Morgan")
            with col_m2:
                subject_input = st.text_input("Subject Line", value="URGENT: Database latency causing transaction timeouts on EU-West")
                
            body_input = st.text_area(
                "Email Body",
                value="""Hi Support Team,

Our engineering lead noticed severe latency on database cluster eu-west-1 starting at 09:30 UTC. 
Our order processing queue has stalled and over 80 customer transactions failed with error code DB_TIMEOUT.

Order batch ref: #ORD-99412
Amount at risk: $14,500.00
Deadline: We need this restored before our 2:00 PM flash sale!

Please have your on-call SRE investigate immediately.

Thanks,
Alice Morgan
VP of Technology, Enterprise Client
Direct: (555) 782-9011""",
                height=180
            )
            
            submit_manual = st.form_submit_button("⚡ Run AI Classification & Routing Pipeline", use_container_width=True)
            if submit_manual:
                with st.spinner("Processing email through NLP, Risk Engine, and Routing rules..."):
                    res = ingest_single_email(
                        subject=subject_input,
                        body=body_input,
                        sender=sender_input,
                        sender_name=sender_name_input,
                        api_key=st.session_state.api_key
                    )
                    st.session_state.selected_email_id = res["id"]
                    st.success(f"Successfully processed email `{res['id']}`! Category: **{res['category']}**, Priority: **{res['priority']}**, Department: **{res['department']}**")
                    
    with tab_upload:
        st.markdown("#### Upload Email Files")
        uploaded_file = st.file_uploader("Upload `.eml`, `.txt`, or `.json` file", type=["eml", "txt", "json"])
        
        if uploaded_file is not None:
            file_bytes = uploaded_file.read()
            if uploaded_file.name.endswith(".eml"):
                parsed = parse_eml_bytes(file_bytes)
                u_subj = parsed["subject"]
                u_sender = parsed["sender"]
                u_name = parsed["sender_name"]
                u_body = parsed["body"]
            else:
                u_subj = uploaded_file.name
                u_sender = "uploader@domain.com"
                u_name = "Uploaded File"
                u_body = file_bytes.decode("utf-8", errors="ignore")
                
            st.write(f"**Parsed Subject:** {u_subj}")
            st.write(f"**Parsed Sender:** {u_sender}")
            st.text_area("Body Preview", u_body[:400], height=100)
            
            if st.button("Process Uploaded Email", key="btn_proc_upload", use_container_width=True):
                with st.spinner("Analyzing uploaded email..."):
                    res = ingest_single_email(
                        subject=u_subj,
                        body=u_body,
                        sender=u_sender,
                        sender_name=u_name,
                        api_key=st.session_state.api_key
                    )
                    st.session_state.selected_email_id = res["id"]
                    st.success(f"Ingested `{res['id']}` as {res['category']} to {res['department']}!")
                    
    with tab_presets:
        st.markdown("#### One-Click Realistic Scenario Triggers")
        st.caption("Click any scenario to instantly ingest and test AI triage:")
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            if st.button("💳 Billing: Double Charge ($249)", use_container_width=True):
                res = ingest_single_email(
                    subject="Charged twice for order #45892",
                    body="Hi, I was charged twice for my order #45892 in the amount of $249.99. Please refund the extra payment as soon as possible.",
                    sender="customer@gmail.com",
                    sender_name="Robert Smith",
                    api_key=st.session_state.api_key
                )
                st.session_state.selected_email_id = res["id"]
                st.success(f"Ingested `{res['id']}`! Category: {res['category']}")
                
            if st.button("💼 Sales: 600 Seats Enterprise Lead", use_container_width=True):
                res = ingest_single_email(
                    subject="Inquiry: Enterprise Pricing & Demo for 600 users",
                    body="Hello Sales Team, our procurement committee would like a 30-minute tailored demo and pricing quote for 600 enterprise seats.",
                    sender="director@globalco.com",
                    sender_name="Sarah Connor",
                    api_key=st.session_state.api_key
                )
                st.session_state.selected_email_id = res["id"]
                st.success(f"Ingested `{res['id']}`! Category: {res['category']}")

        with col_s2:
            if st.button("🔥 Tech: 500 Outage on Checkout", use_container_width=True):
                res = ingest_single_email(
                    subject="CRITICAL: 500 Internal Server Errors in production checkout API",
                    body="Urgent: Production outage on payment gateway. All EU transactions are currently failing with 500 Internal Server Error. Need on-call SRE immediately!",
                    sender="oncall@monitorservice.net",
                    sender_name="Monitoring Alert",
                    api_key=st.session_state.api_key
                )
                st.session_state.selected_email_id = res["id"]
                st.success(f"Ingested `{res['id']}`! Category: {res['category']}")
                
            if st.button("📄 Job App: Senior ML Engineer", use_container_width=True):
                res = ingest_single_email(
                    subject="Application for Senior Machine Learning Engineer - Sarah Lin",
                    body="Dear Talent Acquisition Team, I am submitting my resume and portfolio for the Senior Machine Learning Engineer position. Best regards, Sarah Lin.",
                    sender="sarah.lin.ai@outlook.com",
                    sender_name="Sarah Lin",
                    api_key=st.session_state.api_key
                )
                st.session_state.selected_email_id = res["id"]
                st.success(f"Ingested `{res['id']}`! Category: {res['category']}")

        with col_s3:
            if st.button("⚖️ Complaint: Threatening Legal Action", use_container_width=True):
                res = ingest_single_email(
                    subject="Unacceptable downtime - Breaching our SLA contract",
                    body="This is completely unacceptable. If our system is not back online by 5 PM today, I will have our attorneys file for breach of contract and damages.",
                    sender="executive@angryclient.com",
                    sender_name="David Sterling",
                    api_key=st.session_state.api_key
                )
                st.session_state.selected_email_id = res["id"]
                st.success(f"Ingested `{res['id']}`! Category: {res['category']}")
                
            if st.button("🎣 Spam: Lottery Winner $10M Phishing", use_container_width=True):
                res = ingest_single_email(
                    subject="CONGRATULATIONS: You have won $10,000,000 in international lottery",
                    body="Urgent wire transfer required! Claim your $10,000,000 inheritance. Send your bank details immediately to Barrister Charles.",
                    sender="lottery-winner@claims-scam.xyz",
                    sender_name="Scam Bot",
                    api_key=st.session_state.api_key
                )
                st.session_state.selected_email_id = res["id"]
                st.success(f"Ingested `{res['id']}`! Category: {res['category']}")

# ==============================================================================
# VIEW 4: ANALYTICS & SLA COMMAND CENTER
# ==============================================================================
elif menu == "📊 Analytics & SLA Command Center":
    st.markdown("### 📊 Enterprise Operations & SLA Command Center")
    metrics = get_analytics_metrics()
    
    col_ch1, col_ch2 = st.columns(2)
    
    # 1. Department Workload
    with col_ch1:
        st.markdown("#### 🏢 Active Tickets vs Department Workload")
        wl_data = metrics.get("department_workload", [])
        if wl_data:
            df_wl = pd.DataFrame(wl_data)
            fig_wl = px.bar(
                df_wl,
                x="department",
                y=["active", "total"],
                barmode="group",
                title="Active vs Total Volume by Department",
                labels={"value": "Ticket Count", "department": "Department"},
                color_discrete_sequence=["#6366F1", "#334155"]
            )
            fig_wl.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#F8FAFC"),
                margin=dict(l=10, r=10, t=40, b=10)
            )
            st.plotly_chart(fig_wl, use_container_width=True)
        else:
            st.info("No department data available yet.")
            
    # 2. Category Distribution
    with col_ch2:
        st.markdown("#### 🍩 Category Breakdown")
        cat_data = metrics.get("category_distribution", [])
        if cat_data:
            df_cat = pd.DataFrame(cat_data)
            fig_cat = px.pie(
                df_cat,
                names="category",
                values="count",
                hole=0.45,
                title="Email Inflow by Category",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_cat.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#F8FAFC"),
                margin=dict(l=10, r=10, t=40, b=10)
            )
            st.plotly_chart(fig_cat, use_container_width=True)
            
    col_ch3, col_ch4 = st.columns(2)
    
    # 3. Priority & Urgency Levels
    with col_ch3:
        st.markdown("#### ⚡ Priority Distribution")
        prio_data = metrics.get("priority_distribution", [])
        if prio_data:
            df_prio = pd.DataFrame(prio_data)
            color_map = {
                "Critical": "#EF4444",
                "High": "#F97316",
                "Medium": "#F59E0B",
                "Low": "#10B981"
            }
            fig_prio = px.bar(
                df_prio,
                x="priority",
                y="count",
                color="priority",
                color_discrete_map=color_map,
                title="Priority Triage Count"
            )
            fig_prio.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#F8FAFC"),
                margin=dict(l=10, r=10, t=40, b=10)
            )
            st.plotly_chart(fig_prio, use_container_width=True)
            
    # 4. Sentiment Analysis Breakdown
    with col_ch4:
        st.markdown("#### 🎭 Sentiment Polarity Distribution")
        sent_data = metrics.get("sentiment_distribution", [])
        if sent_data:
            df_sent = pd.DataFrame(sent_data)
            sent_colors = {
                "Positive": "#10B981",
                "Neutral": "#94A3B8",
                "Negative": "#F97316",
                "Highly Frustrated": "#EF4444"
            }
            fig_sent = px.pie(
                df_sent,
                names="sentiment",
                values="count",
                color="sentiment",
                color_discrete_map=sent_colors,
                title="Customer Emotional Sentiment"
            )
            fig_sent.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#F8FAFC"),
                margin=dict(l=10, r=10, t=40, b=10)
            )
            st.plotly_chart(fig_sent, use_container_width=True)

# ==============================================================================
# VIEW 5: ROUTING RULES, CONTINUOUS LEARNING & AUDIT LOGS
# ==============================================================================
elif menu == "⚙️ Routing Rules & Continuous Learning":
    st.markdown("### ⚙️ Automation Rules, Continuous Learning & Audit Trail")
    
    tab_rules, tab_feedback, tab_audit = st.tabs(["🔀 Dynamic Routing Rules", "🧠 AI Model Continuous Learning", "📜 System Audit Trail"])
    
    # 1. Routing Rules Manager
    with tab_rules:
        st.markdown("#### Automated Dynamic Routing Rules")
        st.caption("Custom conditional rules that intercept incoming emails before standard category routing.")
        
        current_rules = get_routing_rules()
        if current_rules:
            for r in current_rules:
                c_r1, c_r2, c_r3 = st.columns([4, 4, 1])
                with c_r1:
                    st.markdown(f"**{r['rule_name']}**")
                    st.caption(f"IF `{r['condition_field']}` {r['condition_operator']} `'{r['condition_value']}'`")
                with c_r2:
                    prio_info = f" | Override Priority: **{r['priority_override']}**" if r.get('priority_override') else ""
                    st.markdown(f"➡️ Route to: **{r['target_department']}** ({r.get('target_agent') or 'Auto-assign'}{prio_info})")
                with c_r3:
                    if st.button("Delete", key=f"del_rule_{r['id']}"):
                        delete_routing_rule(r["id"])
                        st.rerun()
                st.markdown("<hr style='border: none; border-top: 1px solid rgba(255,255,255,0.05); margin: 6px 0;'>", unsafe_allow_html=True)
        else:
            st.info("No custom dynamic rules configured. Using default AI category routing.")
            
        with st.expander("➕ Add New Routing Rule", expanded=False):
            with st.form("new_rule_form"):
                r_name = st.text_input("Rule Name", placeholder="e.g., VIP Account Routing")
                col_rf1, col_rf2, col_rf3 = st.columns(3)
                with col_rf1:
                    r_field = st.selectbox("If Field", ["subject", "body", "sender"])
                with col_rf2:
                    r_op = st.selectbox("Operator", ["contains", "starts_with", "equals"])
                with col_rf3:
                    r_val = st.text_input("Value to match", placeholder="e.g., Enterprise or lawyer")
                    
                col_rf4, col_rf5 = st.columns(2)
                with col_rf4:
                    r_dept = st.selectbox("Target Department", list(DEPARTMENTS.keys()))
                with col_rf5:
                    r_prio_ov = st.selectbox("Priority Override (Optional)", ["None", "Critical", "High", "Medium", "Low"])
                    
                submit_rule = st.form_submit_button("Save Automation Rule")
                if submit_rule and r_name and r_val:
                    add_routing_rule(
                        name=r_name,
                        field=r_field,
                        op=r_op,
                        value=r_val,
                        dept=r_dept,
                        priority_override=None if r_prio_ov == "None" else r_prio_ov
                    )
                    st.success("Rule added!")
                    st.rerun()

    # 2. Continuous Learning & Retraining
    with tab_feedback:
        st.markdown("#### Human Feedback Loop & Model Adaptation")
        st.caption("Review all human corrections made in the dashboard and trigger fine-tuning of the local classifier.")
        
        feedback_list = get_feedback_logs(limit=50)
        
        col_fb1, col_fb2 = st.columns([3, 1])
        with col_fb1:
            st.markdown(f"**Total Logged Human Corrections:** `{len(feedback_list)}`")
        with col_fb2:
            if st.button("🚀 Re-train Local ML Model Now", use_container_width=True):
                with st.spinner("Retraining Scikit-Learn TF-IDF + Logistic Regression model with human feedback..."):
                    res = local_classifier.retrain_with_feedback(feedback_list)
                    st.success(f"Retraining complete! Model now trained on {res['total_samples']} samples ({res['feedback_samples_added']} feedback examples incorporated).")
                    
        if feedback_list:
            df_fb = pd.DataFrame(feedback_list)[["email_id", "old_category", "new_category", "old_priority", "new_priority", "feedback_notes", "timestamp"]]
            st.dataframe(df_fb, use_container_width=True)
        else:
            st.info("No manual corrections logged yet. Correct an email in the 'Email Detail' tab to see it recorded here.")

    # 3. System Audit Trail
    with tab_audit:
        st.markdown("#### System Activity & Immutable Audit Log")
        audit_records = get_audit_logs(limit=50)
        if audit_records:
            df_audit = pd.DataFrame(audit_records)[["id", "email_id", "action", "details", "actor", "timestamp"]]
            st.dataframe(df_audit, use_container_width=True)
        else:
            st.info("No audit logs recorded yet.")
