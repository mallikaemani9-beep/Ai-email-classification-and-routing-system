# MailPulse AI: Enterprise Email Classification & Smart Routing System

![MailPulse AI](https://img.shields.io/badge/Status-Operational-brightgreen)
![Python](https://img.shields.io/badge/Python-3.13-blue)
![NLP](https://img.shields.io/badge/AI%20Engine-Gemini%202.5%20%2B%20Local%20ML-purple)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)

An enterprise-grade, end-to-end AI system that automatically reads, analyzes, categorizes, prioritizes, and routes incoming emails to the appropriate department and personnel in real time.

---

## 🌟 Key Features

1. **Multi-Tier AI Classification Engine**:
   - **GenAI Cloud Tier**: Native integration with Google Gemini 2.5 Flash via the official `google-genai` SDK for semantic reasoning, sentiment classification, entity extraction, and executive summaries.
   - **Local Calibrated ML Tier**: High-speed, offline-capable Scikit-Learn pipeline (`TfidfVectorizer` + `CalibratedClassifierCV` Logistic Regression) pre-trained on enterprise seeds. Runs with 100% reliability immediately with zero configuration!
   - **9 Enterprise Categories**: Customer Support, Billing, Technical Issues, Sales, Complaints, HR, Job Applications, General Queries, and Spam.

2. **⚡ Unique Feature: AI Risk & Urgency Engine**:
   - Goes far beyond static categorization by computing a dynamic composite **Risk Score (0–100)** and **Triage Rank** based on:
     - **Urgency Level** (Keywords, emergency alerts, outage tokens)
     - **Sentiment Intensity** (Angry customer vs. polite inquiry, legal escalation flags)
     - **Customer Impact** (Monetary amounts, VIP enterprise accounts, user breadth)
     - **Deadline Proximity** (Explicit time limits like "within 2 hours", "by 5pm today")
     - **Department Workload Pressure** (Live queue backlog compared to capacity thresholds)

3. **Smart Department & Agent Routing**:
   - Pre-mapped department routing (`Finance & Billing`, `Tech Support & IT Ops`, `Executive Escalations`, `Talent Acquisition`, etc.).
   - Dynamic Custom Automation Rules: Configure rules such as `IF subject CONTAINS 'VIP' THEN ROUTE TO Executive Escalations`.
   - Workload & Capacity Balancing: Monitors real-time department ticket volumes and assigns agents.
   - SLA Deadline Computation (Critical = 1h, High = 4h, Medium = 12h, Low = 24h).

4. **Information & Entity Extraction**:
   - Customer Names
   - Order IDs & Ticket Numbers (`#45892`, `INV-4921`, `ORD-8821`)
   - Monetary Amounts (`$249.99`, `$150,000`)
   - Phone Numbers & Contacts
   - Identified Core Issues & Required Next Steps

5. **Spam & Cryptographic Duplicate Detection**:
   - Normalized SHA-256 fingerprinting & Jaccard token similarity to catch repeated or resubmitted tickets.
   - Heuristic and token-based phishing/spam detector quarantining high-risk emails.

6. **Context-Aware Suggested Reply Drafter**:
   - Auto-generates empathetic, professional email response drafts tailored to the specific category, issue, order ID, and customer name.
   - Built-in live editor allowing agents to save edits or approve and mark resolved in 1 click.

7. **Human-in-the-Loop Feedback & Continuous Retraining**:
   - Triage agents can correct classifications, priorities, and assigned departments.
   - All corrections are stored in a dedicated `feedback_logs` table.
   - One-click model retraining dynamically fits the local Scikit-Learn classifier on human corrections.

8. **Enterprise Analytics & Audit Trail**:
   - Plotly interactive charts for department workload, category breakdown, sentiment analysis, and SLA status.
   - Immutable audit logs tracking every ingestion, classification, routing, and manual override event.

---

## 🏗️ System Architecture

```
Incoming Email (.eml, .txt, JSON, direct test)
         │
         ▼
[Ingestion & Normalization]
         │
         ├──► [Duplicate Check (SHA-256 & Jaccard Similarity)]
         ├──► [Spam & Phishing Detector (Heuristic Scoring)]
         │
         ▼
[AI Classification & Extraction]
   ├── Gemini 2.5 Flash API (Cloud GenAI)
   └── Scikit-Learn TF-IDF + Calibrated Logistic Regression (Local Fallback)
         │
         ├──► Sentiment & Emotion Analysis
         ├──► Entity Extraction (Names, Order IDs, Amounts, Deadlines)
         └──► Executive Summarization
         │
         ▼
[AI Risk & Urgency Engine]
   Calculates Composite Risk Score (0-100) based on:
   Urgency (30%) + Sentiment (25%) + Business Impact (25%) + Deadlines (10%) + Workload (10%)
         │
         ▼
[Smart Routing & SLA Engine]
   ├── Custom Dynamic Automation Rules
   ├── Department & Least-Burdened Agent Assignment
   └── SLA Deadline Clock Calculation
         │
         ▼
[Response Generation & Dispatch]
   Tailored contextual draft ready for human agent review
         │
         ▼
[Human-in-the-Loop Feedback Loop]
   Feedback Logs ──► Continuous Local Model Retraining
```

---

## 🚀 Quickstart Guide

### 1. Launch the Modern Web Dashboard (Recommended)
Run the dedicated, high-performance Web UI server (zero extra dependencies, opens in browser automatically):

```powershell
python run_ui.py
```
*(Or simply open [web/index.html](file:///c:/Users/malli/Desktop/Ai%20email%20classification/web/index.html) directly in any browser).*

### 2. Launch the Streamlit Application (Alternative)
Run the classic Streamlit app:

```powershell
python -m streamlit run app.py
```

### 2. Optional: Configure Gemini Cloud AI
In the sidebar, you can enter your `GEMINI_API_KEY`, or export it in your environment:
```powershell
$env:GEMINI_API_KEY="your-api-key-here"
python -m streamlit run app.py
```
*Note: If no API key is provided, the application automatically uses the built-in Scikit-Learn local ML engine with zero setup required!*

---

## 🧪 Testing the System

1. **Preloaded Scenarios**:
   The database automatically seeds 10 enterprise test cases covering duplicate charges, server crashes, legal complaints, sales leads, job applications, spam, and resubmitted duplicates.
2. **Instant Scenario Triggers**:
   Go to **"🚀 Ingest & Test Lab"** > **"⚡ Instant Test Scenarios"** and click any of the 1-click test buttons.
3. **Upload Real Files**:
   Upload `.eml` or text files in the Upload tab.
4. **Inspect & Edit**:
   Select any email in the **"🔍 Email Detail & AI Insights"** tab to review the AI risk breakdown gauge, edit the suggested response draft, or submit a human correction.
5. **Retrain the Model**:
   Go to **"⚙️ Routing Rules & Continuous Learning"** > **"🧠 AI Model Continuous Learning"** and click **"Re-train Local ML Model Now"** to watch the model incorporate agent feedback!
