/**
 * MailPulse AI - Enterprise Email Triage & Classification Web Engine
 * Fully interactive client controller with risk engine, entity extractor,
 * search filtering, radial SVG gauge animations, and draft generation.
 */

// --- 1. CONFIGURATION & CONSTANTS ---
const CATEGORIES = [
  { name: "Customer Support", color: "#3B82F6", icon: "🎧" },
  { name: "Billing", color: "#10B981", icon: "💳" },
  { name: "Technical Issues", color: "#EF4444", icon: "🛠️" },
  { name: "Sales", color: "#8B5CF6", icon: "💼" },
  { name: "Complaints", color: "#F43F5E", icon: "⚠️" },
  { name: "HR", color: "#06B6D4", icon: "👥" },
  { name: "Job Applications", color: "#F59E0B", icon: "📄" },
  { name: "General Queries", color: "#64748B", icon: "ℹ️" },
  { name: "Spam", color: "#94A3B8", icon: "🛡️" }
];

const DEPARTMENTS = {
  "Finance & Billing": { agents: ["Sarah Jenkins (Lead)", "David Vance", "Elena Rostova"], max: 25 },
  "Tech Support & IT Ops": { agents: ["Alex Rivera (Lead)", "Kiran Patel", "Chen Wei"], max: 30 },
  "Executive Escalations": { agents: ["Victoria Sterling (VP)", "Marcus Vance"], max: 10 },
  "Enterprise Sales": { agents: ["Jordan Bell (Director)", "Rachel Green"], max: 20 },
  "HR & People Ops": { agents: ["Amanda Cole", "Carlos Mendez"], max: 15 },
  "Talent Acquisition": { agents: ["Jessica Taylor", "Liam Smith"], max: 20 },
  "General Inquiries & Reception": { agents: ["Emily Watson", "Front Desk Bot"], max: 30 },
  "Spam & Security Quarantine": { agents: ["SecOps Automated Sentinel"], max: 100 }
};

const CATEGORY_TO_DEPT = {
  "Billing": "Finance & Billing",
  "Technical Issues": "Tech Support & IT Ops",
  "Complaints": "Executive Escalations",
  "Sales": "Enterprise Sales",
  "HR": "HR & People Ops",
  "Job Applications": "Talent Acquisition",
  "Customer Support": "Tech Support & IT Ops",
  "General Queries": "General Inquiries & Reception",
  "Spam": "Spam & Security Quarantine"
};

// --- 2. PRELOADED ENTERPRISE EMAIL DATASET ---
let emailsData = [
  {
    id: "EML-1002",
    sender_name: "Elena Rostova",
    sender: "devops-alerts@fintechscale.io",
    subject: "CRITICAL OUTAGE: Production API 500 Errors on Checkout Gateway",
    body: "EMERGENCY INCIDENT:\nOur production monitoring systems are reporting sustained 500 Internal Server Errors across the core payment checkout endpoint: https://api.service.com/v2/checkout.\n\nError spike started at 11:42 AM UTC. Over 4,200 active customer transactions have failed. Database connection pool exhaustion reported on cluster shard-04.\n\nThis is currently blocking all EU transactions. We need on-call SRE and database engineering immediately!\n\nElena Rostova\nHead of Infrastructure, FintechScale",
    category: "Technical Issues",
    priority: "Critical",
    department: "Tech Support & IT Ops",
    agent: "Alex Rivera (Lead)",
    risk_score: 94,
    risk_tier: "Severe Operational Risk",
    sla_clock: "⏱️ 38m remaining",
    status: "Pending",
    confidence: 98.4,
    factors: { urgency: 98, sentiment: 85, impact: 95, deadline: 94 },
    entities: {
      customer: "Elena Rostova",
      order_id: "SHARD-04",
      amount: "4,200 transactions",
      deadline: "Immediate on-call",
      phone: "+1 (555) 940-2211"
    }
  },
  {
    id: "EML-1003",
    sender_name: "Marcus Vance",
    sender: "marcus.vance@megacorp-holdings.com",
    subject: "Unacceptable service - Formal complaint regarding Breach of Enterprise SLA",
    body: "To the Executive Team and VP of Customer Relations,\n\nThis is completely unacceptable. This is the third time our enterprise dashboard has frozen during our monthly investor reporting period.\n\nWe pay over $150,000 annually for 99.99% uptime and dedicated support, yet our tickets submitted over 48 hours ago have been ignored. If this issue is not fully resolved and a root-cause explanation provided by today 5:00 PM EST, I will have our legal counsel terminate our contract immediately and pursue compensation for business damages.\n\nI demand a call with your VP of Engineering today.\n\nMarcus Vance\nChief Technology Officer, MegaCorp Holdings\nOffice: (555) 901-2244",
    category: "Complaints",
    priority: "Critical",
    department: "Executive Escalations",
    agent: "Victoria Sterling (VP)",
    risk_score: 89,
    risk_tier: "Legal Escalation Risk",
    sla_clock: "⏱️ 52m remaining",
    status: "Pending",
    confidence: 96.8,
    factors: { urgency: 92, sentiment: 96, impact: 92, deadline: 88 },
    entities: {
      customer: "Marcus Vance",
      order_id: "SLA-48H",
      amount: "$150,000 / year",
      deadline: "Today 5:00 PM EST",
      phone: "(555) 901-2244"
    }
  },
  {
    id: "EML-1001",
    sender_name: "Robert Langdon",
    sender: "robert.langdon@acmepartners.com",
    subject: "Urgent: Charged twice for my order #45892",
    body: "Hi Support Team,\n\nI was charged twice on my American Express card for my order #45892 in the amount of $249.99 each. This happened during the checkout error yesterday morning.\n\nPlease refund the extra payment of $249.99 as soon as possible. My bank account is showing both charges pending.\n\nThanks,\nRobert Langdon\nAcme Partners\nDirect: (555) 234-8891",
    category: "Billing",
    priority: "High",
    department: "Finance & Billing",
    agent: "Sarah Jenkins (Lead)",
    risk_score: 74,
    risk_tier: "High Financial Urgency",
    sla_clock: "⏱️ 2h 45m remaining",
    status: "Pending",
    confidence: 97.2,
    factors: { urgency: 78, sentiment: 60, impact: 75, deadline: 70 },
    entities: {
      customer: "Robert Langdon",
      order_id: "#45892",
      amount: "$249.99",
      deadline: "ASAP",
      phone: "(555) 234-8891"
    }
  },
  {
    id: "EML-1004",
    sender_name: "David Vance",
    sender: "david.vance@aerospace-global.com",
    subject: "Enterprise License Inquiry - 500 Seats & Custom Deployment",
    body: "Hello Enterprise Sales Team,\n\nOur procurement department is currently evaluating alternatives to replace our legacy communication stack. We are interested in obtaining pricing and compliance documentation for 500 enterprise seats of your platform.\n\nKey requirements include FedRAMP or SOC-2 Type II audit reports, SSO/SAML integration, and custom data retention policies.\n\nCould we schedule an introductory 30-minute demonstration call next Tuesday at 2:00 PM EST?\n\nBest regards,\nDavid Vance\nDirector of IT Procurement, Aerospace Global",
    category: "Sales",
    priority: "Medium",
    department: "Enterprise Sales",
    agent: "Jordan Bell (Director)",
    risk_score: 42,
    risk_tier: "Commercial Opportunity",
    sla_clock: "⏱️ 8h 15m remaining",
    status: "Pending",
    confidence: 95.1,
    factors: { urgency: 35, sentiment: 20, impact: 65, deadline: 40 },
    entities: {
      customer: "David Vance",
      order_id: "RFP-500",
      amount: "500 Seats",
      deadline: "Next Tuesday 2:00 PM EST",
      phone: "(555) 332-1100"
    }
  },
  {
    id: "EML-1005",
    sender_name: "Samantha Reed",
    sender: "samantha.reed@clientmail.net",
    subject: "Delivery status update for replacement unit #ORD-99120",
    body: "Hi there,\n\nI received an email stating that my replacement part for order #ORD-99120 was shipped via FedEx, but the tracking number shows label created with no progress for 3 days.\n\nCan someone please check with the warehouse dispatch team to confirm if the package has actually left the facility?\n\nThank you for your help,\nSamantha Reed",
    category: "Customer Support",
    priority: "Low",
    department: "Tech Support & IT Ops",
    agent: "Kiran Patel",
    risk_score: 28,
    risk_tier: "Standard Inquiry",
    sla_clock: "⏱️ 18h remaining",
    status: "Pending",
    confidence: 93.6,
    factors: { urgency: 25, sentiment: 15, impact: 20, deadline: 10 },
    entities: {
      customer: "Samantha Reed",
      order_id: "#ORD-99120",
      amount: "N/A",
      deadline: "Standard",
      phone: "(555) 789-0122"
    }
  },
  {
    id: "EML-1006",
    sender_name: "Michael Chang",
    sender: "m.chang@internal-corp.com",
    subject: "Confidential: Parental leave policy & 401k match questions",
    body: "Hi HR Team,\n\nMy spouse and I are expecting our first child this coming autumn. I would like to review the company parental leave schedule and understand how benefits continue during leave.\n\nAlso, could you clarify whether 401k employee matching deductions continue automatically or need to be adjusted?\n\nThanks,\nMichael Chang\nEngineering Team",
    category: "HR",
    priority: "Medium",
    department: "HR & People Ops",
    agent: "Amanda Cole",
    risk_score: 31,
    risk_tier: "Internal Benefits",
    sla_clock: "⏱️ 9h 40m remaining",
    status: "Pending",
    confidence: 96.0,
    factors: { urgency: 20, sentiment: 10, impact: 30, deadline: 25 },
    entities: {
      customer: "Michael Chang",
      order_id: "HR-BEN",
      amount: "401k Match",
      deadline: "Autumn Planning",
      phone: "Ext. 4091"
    }
  },
  {
    id: "EML-1007",
    sender_name: "Priya Sharma",
    sender: "priya.sharma.ai@gmail.com",
    subject: "Application: Senior Machine Learning Engineer - Priya Sharma",
    body: "Dear Hiring Team,\n\nI am writing to express my enthusiastic interest in the Senior Machine Learning Engineer position at your company. With 7 years of production experience fine-tuning LLMs, scaling vector retrieval systems, and deploying low-latency inference pipelines, I believe I can make an immediate contribution to your AI engineering team.\n\nMy resume and GitHub portfolio links are enclosed. I look forward to hearing from you regarding potential interview next steps.\n\nSincerely,\nPriya Sharma\nPortfolio: github.com/priyasharma-ml",
    category: "Job Applications",
    priority: "Medium",
    department: "Talent Acquisition",
    agent: "Jessica Taylor",
    risk_score: 29,
    risk_tier: "Talent Acquisition",
    sla_clock: "⏱️ 11h remaining",
    status: "Pending",
    confidence: 97.5,
    factors: { urgency: 20, sentiment: 10, impact: 35, deadline: 15 },
    entities: {
      customer: "Priya Sharma",
      order_id: "JOB-MLE",
      amount: "7 Yrs Experience",
      deadline: "Open Recruitment",
      phone: "(555) 678-9900"
    }
  },
  {
    id: "EML-1008",
    sender_name: "Crypto Rewards System",
    sender: "crypto-rewards@fast-bitcoins.biz",
    subject: "CLAIM $10,000,000 BITCOIN LOTTERY PRIZE IMMEDIATELY",
    body: "CONGRATULATIONS VALUED USER!\n\nYour email was selected as the 1st prize winner of $10,000,000 USD in our international cryptocurrency raffle. To claim your Bitcoin settlement, reply immediately with your passport copy, wallet address, and bank routing credentials.\n\nFAILURE TO CLAIM WITHIN 24 HOURS WILL FORFEIT PRIZE!",
    category: "Spam",
    priority: "Low",
    department: "Spam & Security Quarantine",
    agent: "SecOps Automated Sentinel",
    risk_score: 82,
    risk_tier: "Phishing / Security Threat",
    sla_clock: "🛡️ Quarantined",
    status: "Resolved",
    confidence: 99.8,
    factors: { urgency: 95, sentiment: 40, impact: 90, deadline: 90 },
    entities: {
      customer: "Unknown Scammer",
      order_id: "MALICIOUS",
      amount: "$10,000,000",
      deadline: "24 Hours Bait",
      phone: "Blocked"
    }
  },
  {
    id: "EML-1009",
    sender_name: "Clara Oswald",
    sender: "clara.oswald@press-wire.org",
    subject: "Press inquiry regarding AI product announcement",
    body: "Hello Media Relations,\n\nI am a senior technology reporter writing a feature on the evolution of automated AI triage systems in financial technology. Could we arrange a brief interview with your Chief Product Officer or receive a copy of your press kit before our Thursday publication deadline?\n\nThank you,\nClara Oswald\nSenior Tech Correspondent, PressWire",
    category: "General Queries",
    priority: "Low",
    department: "General Inquiries & Reception",
    agent: "Emily Watson",
    risk_score: 22,
    risk_tier: "Media Inquiry",
    sla_clock: "⏱️ 22h remaining",
    status: "Pending",
    confidence: 94.2,
    factors: { urgency: 15, sentiment: 10, impact: 25, deadline: 30 },
    entities: {
      customer: "Clara Oswald",
      order_id: "PRESS-PR",
      amount: "N/A",
      deadline: "Thursday Media Cutoff",
      phone: "(555) 441-2993"
    }
  },
  {
    id: "EML-1010",
    sender_name: "Robert Langdon",
    sender: "robert.langdon@acmepartners.com",
    subject: "RE: Charged twice for my order #45892 (Resubmitted)",
    body: "Resubmitting my previous inquiry about the duplicate charge of $249.99 on order #45892. Please expedite.",
    category: "Billing",
    priority: "High",
    department: "Finance & Billing",
    agent: "Sarah Jenkins (Lead)",
    risk_score: 68,
    risk_tier: "Cryptographic Duplicate Detected",
    sla_clock: "🔗 Linked to EML-1001",
    status: "Resolved",
    confidence: 99.1,
    factors: { urgency: 70, sentiment: 55, impact: 65, deadline: 50 },
    entities: {
      customer: "Robert Langdon",
      order_id: "#45892",
      amount: "$249.99",
      deadline: "Duplicate Jaccard > 0.85",
      phone: "(555) 234-8891"
    }
  }
];

// Active State
let currentSelectedId = "EML-1002";
let currentPriorityFilter = "all";
let currentCategoryFilter = "all";
let currentView = "all";
let searchQuery = "";

// --- 3. DOM ELEMENTS ---
const elements = {
  feedContainer: document.getElementById("email-feed-container"),
  categoryFilterList: document.getElementById("category-filter-list"),
  deptHealthContainer: document.getElementById("dept-health-container"),
  searchInput: document.getElementById("search-input"),
  priorityTabs: document.getElementById("feed-priority-tabs"),
  navViewsMenu: document.getElementById("nav-views-menu"),
  resetCatFilter: document.getElementById("reset-cat-filter"),

  // Details
  detailSubject: document.getElementById("detail-subject"),
  detailSender: document.getElementById("detail-sender"),
  detailEmail: document.getElementById("detail-email"),
  detailDept: document.getElementById("detail-dept"),
  detailAgent: document.getElementById("detail-agent"),
  detailPriorityBadge: document.getElementById("detail-priority-badge"),
  detailCategoryBadge: document.getElementById("detail-category-badge"),
  detailSlaClock: document.getElementById("detail-sla-clock"),
  detailStatusPill: document.getElementById("detail-status-pill"),
  detailBodyText: document.getElementById("detail-body-text"),
  entitiesContainer: document.getElementById("entities-container"),

  // Risk Gauge
  riskGaugeCircle: document.getElementById("risk-gauge-circle"),
  riskScoreValue: document.getElementById("risk-score-value"),
  riskTierBadge: document.getElementById("risk-tier-badge"),
  scoreUrgency: document.getElementById("score-urgency"),
  barUrgency: document.getElementById("bar-urgency"),
  scoreSentiment: document.getElementById("score-sentiment"),
  barSentiment: document.getElementById("bar-sentiment"),
  scoreImpact: document.getElementById("score-impact"),
  barImpact: document.getElementById("bar-impact"),
  scoreDeadline: document.getElementById("score-deadline"),
  barDeadline: document.getElementById("bar-deadline"),

  // Draft
  draftReplyText: document.getElementById("draft-reply-text"),
  draftCategoryBadge: document.getElementById("draft-category-badge"),
  btnCopyDraft: document.getElementById("btn-copy-draft"),
  btnRegenerateDraft: document.getElementById("btn-regenerate-draft"),
  btnDispatchDraft: document.getElementById("btn-dispatch-draft"),

  // Human Override
  overrideCategory: document.getElementById("override-category"),
  overridePriority: document.getElementById("override-priority"),
  overrideDept: document.getElementById("override-dept"),
  btnSaveOverride: document.getElementById("btn-save-override"),

  // KPIs
  kpiTotalEmails: document.getElementById("kpi-total-emails"),
  kpiUrgentCount: document.getElementById("kpi-urgent-count"),
  kpiAvgConfidence: document.getElementById("kpi-avg-confidence"),
  countAll: document.getElementById("count-all"),
  countCritical: document.getElementById("count-critical"),
  countPending: document.getElementById("count-pending"),
  countResolved: document.getElementById("count-resolved"),

  // Modals
  btnOpenScenarios: document.getElementById("btn-open-scenarios"),
  btnOpenAnalytics: document.getElementById("btn-open-analytics"),
  btnOpenIngest: document.getElementById("btn-open-ingest"),
  modalIngest: document.getElementById("modal-ingest"),
  modalAnalytics: document.getElementById("modal-analytics"),
  btnCloseModalIngest: document.getElementById("btn-close-modal-ingest"),
  btnCloseModalAnalytics: document.getElementById("btn-close-modal-analytics"),
  btnCancelCustomIngest: document.getElementById("btn-cancel-custom-ingest"),
  customIngestForm: document.getElementById("custom-ingest-form"),
  scenariosGrid: document.getElementById("scenarios-grid"),
  toastContainer: document.getElementById("toast-container")
};

// --- 4. TOAST NOTIFICATIONS ---
function showToast(message, type = "success") {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span>${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span>
    <span>${message}</span>
  `;
  elements.toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(50px)";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// --- 5. INITIALIZATION & RENDERING ---
function initApp() {
  populateDropdowns();
  renderSidebarCategories();
  renderDepartmentHealth();
  renderScenarioButtons();
  updateKPIs();
  renderEmailFeed();
  selectEmail(currentSelectedId);
  setupEventListeners();
  tryBackendSync();
}

function populateDropdowns() {
  // Populate Override Category
  elements.overrideCategory.innerHTML = CATEGORIES.map(
    c => `<option value="${c.name}">${c.icon} ${c.name}</option>`
  ).join("");

  // Populate Override Department
  elements.overrideDept.innerHTML = Object.keys(DEPARTMENTS).map(
    d => `<option value="${d}">${d}</option>`
  ).join("");
}

function updateKPIs() {
  const total = emailsData.length;
  const critical = emailsData.filter(e => e.priority === "Critical" && e.status !== "Resolved").length;
  const pending = emailsData.filter(e => e.status !== "Resolved").length;
  const resolved = emailsData.filter(e => e.status === "Resolved").length;
  const avgConf = (emailsData.reduce((acc, e) => acc + (e.confidence || 95), 0) / (total || 1)).toFixed(1);

  elements.kpiTotalEmails.textContent = total;
  elements.kpiUrgentCount.textContent = critical;
  elements.kpiAvgConfidence.textContent = `${avgConf}%`;

  elements.countAll.textContent = total;
  elements.countCritical.textContent = critical;
  elements.countPending.textContent = pending;
  elements.countResolved.textContent = resolved;
}

function renderSidebarCategories() {
  elements.categoryFilterList.innerHTML = CATEGORIES.map(cat => {
    const count = emailsData.filter(e => e.category === cat.name).length;
    const isActive = currentCategoryFilter === cat.name;
    return `
      <div class="category-filter-item ${isActive ? 'active' : ''}" data-category="${cat.name}">
        <div>
          <span class="cat-indicator" style="background-color: ${cat.color};"></span>
          <span>${cat.name}</span>
        </div>
        <span class="nav-count">${count}</span>
      </div>
    `;
  }).join("");

  // Attach click listener
  elements.categoryFilterList.querySelectorAll(".category-filter-item").forEach(item => {
    item.addEventListener("click", () => {
      const cat = item.getAttribute("data-category");
      currentCategoryFilter = (currentCategoryFilter === cat) ? "all" : cat;
      renderSidebarCategories();
      renderEmailFeed();
    });
  });
}

function renderDepartmentHealth() {
  elements.deptHealthContainer.innerHTML = Object.keys(DEPARTMENTS).slice(0, 4).map(dept => {
    const count = emailsData.filter(e => e.department === dept && e.status !== "Resolved").length;
    const max = DEPARTMENTS[dept].max;
    const pct = Math.min(100, Math.round((count / max) * 100));
    const statusClass = pct > 80 ? "danger" : pct > 50 ? "warn" : "";
    return `
      <div class="dept-health-card">
        <div class="dept-title">
          <span>${dept}</span>
          <span class="dept-cap">${count}/${max} (${pct}%)</span>
        </div>
        <div class="progress-track">
          <div class="progress-fill ${statusClass}" style="width: ${pct}%;"></div>
        </div>
      </div>
    `;
  }).join("");
}

// --- 6. EMAIL FEED RENDERING ---
function renderEmailFeed() {
  let filtered = [...emailsData];

  // 1. View filter
  if (currentView === "critical") {
    filtered = filtered.filter(e => e.priority === "Critical" && e.status !== "Resolved");
  } else if (currentView === "pending") {
    filtered = filtered.filter(e => e.status !== "Resolved");
  } else if (currentView === "resolved") {
    filtered = filtered.filter(e => e.status === "Resolved");
  }

  // 2. Priority Tab filter
  if (currentPriorityFilter !== "all") {
    filtered = filtered.filter(e => e.priority.toLowerCase() === currentPriorityFilter.toLowerCase());
  }

  // 3. Category Filter
  if (currentCategoryFilter !== "all") {
    filtered = filtered.filter(e => e.category === currentCategoryFilter);
  }

  // 4. Search Filter
  if (searchQuery.trim()) {
    const q = searchQuery.toLowerCase();
    filtered = filtered.filter(e => 
      e.subject.toLowerCase().includes(q) ||
      e.sender_name.toLowerCase().includes(q) ||
      e.sender.toLowerCase().includes(q) ||
      e.body.toLowerCase().includes(q) ||
      (e.entities && e.entities.order_id && e.entities.order_id.toLowerCase().includes(q))
    );
  }

  if (filtered.length === 0) {
    elements.feedContainer.innerHTML = `
      <div style="text-align: center; padding: 40px 20px; color: var(--text-muted);">
        <div style="font-size: 28px; margin-bottom: 8px;">🔍</div>
        <div style="font-size: 14px; font-weight: 600; color: var(--text-secondary);">No matching emails found</div>
        <div style="font-size: 12px; margin-top: 4px;">Try clearing filters or search query</div>
      </div>
    `;
    return;
  }

  elements.feedContainer.innerHTML = filtered.map(item => {
    const isSelected = item.id === currentSelectedId;
    const initial = (item.sender_name || item.sender)[0].toUpperCase();
    const prioColor = item.priority === "Critical" ? "var(--priority-critical)" :
                     item.priority === "High" ? "var(--priority-high)" :
                     item.priority === "Medium" ? "var(--priority-medium)" : "var(--priority-low)";

    const riskClass = item.risk_score >= 80 ? "risk-pill-critical" :
                      item.risk_score >= 60 ? "risk-pill-high" :
                      item.risk_score >= 35 ? "risk-pill-medium" : "risk-pill-low";

    return `
      <div class="email-card ${isSelected ? 'selected' : ''}" data-id="${item.id}" id="card-${item.id}">
        <div class="card-top-row">
          <div class="sender-info">
            <div class="sender-avatar">${initial}</div>
            <div class="sender-meta">
              <div class="sender-name">${item.sender_name || item.sender}</div>
              <div class="sender-time">${item.sla_clock || 'Just now'}</div>
            </div>
          </div>
          <div class="card-risk-pill ${riskClass}">
            <span>⚡</span>
            <span>${item.risk_score}/100</span>
          </div>
        </div>

        <div class="email-subject" title="${item.subject}">${item.subject}</div>
        <div class="email-snippet">${item.body.replace(/\n+/g, ' ')}</div>

        <div class="card-tags-row">
          <span class="badge-tag">${item.category}</span>
          <span class="badge-priority" style="color: ${prioColor}; background: rgba(255,255,255,0.06);">
            ${item.priority}
          </span>
          <span style="font-size: 11px; color: var(--text-muted); margin-left: auto;">
            ${item.status === 'Resolved' ? '✅ Resolved' : '⏳ Pending'}
          </span>
        </div>
      </div>
    `;
  }).join("");

  // Attach card click handlers
  elements.feedContainer.querySelectorAll(".email-card").forEach(card => {
    card.addEventListener("click", () => {
      const emailId = card.getAttribute("data-id");
      selectEmail(emailId);
    });
  });
}

// --- 7. SELECT & INSPECT EMAIL ---
function selectEmail(id) {
  const item = emailsData.find(e => e.id === id);
  if (!item) return;

  currentSelectedId = id;

  // Highlight in feed
  document.querySelectorAll(".email-card").forEach(c => c.classList.remove("selected"));
  const activeCard = document.getElementById(`card-${id}`);
  if (activeCard) activeCard.classList.add("selected");

  // 1. Header Details
  elements.detailSubject.textContent = item.subject;
  elements.detailSender.textContent = item.sender_name || "Enterprise Customer";
  elements.detailEmail.textContent = item.sender;
  elements.detailDept.textContent = item.department;
  elements.detailAgent.textContent = item.agent || "Unassigned";

  const prioColor = item.priority === "Critical" ? "var(--priority-critical)" :
                   item.priority === "High" ? "var(--priority-high)" :
                   item.priority === "Medium" ? "var(--priority-medium)" : "var(--priority-low)";

  elements.detailPriorityBadge.textContent = `${item.priority === 'Critical' ? '🚨' : item.priority === 'High' ? '⚡' : '⏳'} ${item.priority}`;
  elements.detailPriorityBadge.style.color = prioColor;
  elements.detailCategoryBadge.textContent = item.category;
  elements.detailSlaClock.textContent = item.sla_clock || "⏱️ Under SLA";

  if (item.status === "Resolved") {
    elements.detailStatusPill.innerHTML = `<span class="badge-tag" style="background: rgba(16, 185, 129, 0.2); color: #34D399;">✅ Resolved</span>`;
  } else {
    elements.detailStatusPill.innerHTML = `<span class="badge-tag" style="background: rgba(239, 68, 68, 0.15); color: #F87171;">Triage Pending</span>`;
  }

  // 2. Animated Circular Risk Gauge
  elements.riskScoreValue.textContent = item.risk_score;
  elements.riskTierBadge.textContent = item.risk_tier || "Operational Risk";

  // Calculate SVG stroke offset: circumference = 2 * PI * 60 ≈ 377
  const circumference = 377;
  const progressOffset = circumference - (circumference * (item.risk_score / 100));
  elements.riskGaugeCircle.style.strokeDashoffset = progressOffset;

  // Breakdown Bars
  const f = item.factors || { urgency: 65, sentiment: 50, impact: 60, deadline: 50 };
  elements.scoreUrgency.textContent = `${f.urgency}%`;
  elements.barUrgency.style.width = `${f.urgency}%`;

  elements.scoreSentiment.textContent = `${f.sentiment}%`;
  elements.barSentiment.style.width = `${f.sentiment}%`;

  elements.scoreImpact.textContent = `${f.impact}%`;
  elements.barImpact.style.width = `${f.impact}%`;

  elements.scoreDeadline.textContent = `${f.deadline}%`;
  elements.barDeadline.style.width = `${f.deadline}%`;

  // 3. Extracted Entities
  const ent = item.entities || {};
  elements.entitiesContainer.innerHTML = `
    <div class="entity-pill">
      <span class="entity-icon">👤</span>
      <span class="entity-key">Customer:</span>
      <span class="entity-val">${ent.customer || item.sender_name || 'N/A'}</span>
    </div>
    <div class="entity-pill">
      <span class="entity-icon">🆔</span>
      <span class="entity-key">Order/Ticket:</span>
      <span class="entity-val">${ent.order_id || 'N/A'}</span>
    </div>
    <div class="entity-pill">
      <span class="entity-icon">💰</span>
      <span class="entity-key">Impact/Value:</span>
      <span class="entity-val">${ent.amount || 'N/A'}</span>
    </div>
    <div class="entity-pill">
      <span class="entity-icon">⏱️</span>
      <span class="entity-key">Deadline:</span>
      <span class="entity-val">${ent.deadline || 'Standard'}</span>
    </div>
    <div class="entity-pill">
      <span class="entity-icon">📞</span>
      <span class="entity-key">Phone:</span>
      <span class="entity-val">${ent.phone || 'N/A'}</span>
    </div>
  `;

  // 4. Original Body Text
  elements.detailBodyText.textContent = item.body;

  // 5. Generate Dynamic Suggested Reply
  generateSuggestedDraft(item);

  // 6. Pre-select Override Dropdowns
  elements.overrideCategory.value = item.category;
  elements.overridePriority.value = item.priority;
  elements.overrideDept.value = item.department;
}

// --- 8. AI SUGGESTED REPLY DRAFTER ---
function generateSuggestedDraft(item) {
  const customerName = item.sender_name ? item.sender_name.split(" ")[0] : "there";
  let draft = "";

  if (item.category === "Technical Issues") {
    draft = `Hi ${customerName},\n\nThank you for alerting our technical operations team. We have identified the service disruption and escalated incident ticket ${item.entities?.order_id || '#INC-ALERT'} directly to our on-call SRE and database engineering leads.\n\nOur incident management team is actively rolling out remediation measures to restore normal gateway operations. We will provide a status follow-up within 30 minutes.\n\nSincerely,\n${item.agent || 'Alex Rivera'}\nTech Support & IT Ops`;
  } else if (item.category === "Complaints") {
    draft = `Dear ${item.sender_name || 'Customer'},\n\nI am contacting you directly from Executive Leadership regarding your formal complaint. We take your SLA terms and experience with our enterprise platform with utmost seriousness.\n\nI have scheduled a dedicated technical review with our VP of Engineering to address the root-cause of this disruption immediately. Can we arrange a direct phone call today at your convenience?\n\nSincerely,\n${item.agent || 'Victoria Sterling (VP)'}\nExecutive Escalations Team`;
  } else if (item.category === "Billing") {
    draft = `Hello ${customerName},\n\nThank you for reaching out to Finance & Billing. I have investigated your transaction regarding order ${item.entities?.order_id || 'in question'} and confirmed the duplicate charge of ${item.entities?.amount || 'the specified amount'}.\n\nI have initiated a full refund back to your original payment method. The credit should reflect on your statement within 2-3 business days.\n\nBest regards,\n${item.agent || 'Sarah Jenkins'}\nFinance & Billing Department`;
  } else if (item.category === "Sales") {
    draft = `Hi ${customerName},\n\nThank you for your interest in our Enterprise platform! We would be delighted to provide customized enterprise pricing, security documentation, and schedule the 30-minute demonstration call for your team.\n\nI will send an invite shortly with our product architect.\n\nBest regards,\n${item.agent || 'Jordan Bell'}\nEnterprise Sales`;
  } else if (item.category === "Spam") {
    draft = `[Automated Quarantine Response]\nThis message has been quarantined by our security filters and marked as unsolicited / suspicious phishing communication. No agent dispatch required.`;
  } else {
    draft = `Hi ${customerName},\n\nThank you for reaching out to us. We have received your inquiry regarding "${item.subject}" and routed it to ${item.department}.\n\nOur specialist is reviewing your request and will follow up shortly.\n\nBest regards,\n${item.agent || 'Customer Support Team'}`;
  }

  elements.draftReplyText.value = draft;
  elements.draftCategoryBadge.textContent = `Tailored for ${item.category}`;
}

// --- 9. EVENT LISTENERS & ACTIONS ---
function setupEventListeners() {
  // Search
  elements.searchInput.addEventListener("input", (e) => {
    searchQuery = e.target.value;
    renderEmailFeed();
  });

  // Priority Filter Tabs
  elements.priorityTabs.querySelectorAll(".filter-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      elements.priorityTabs.querySelectorAll(".filter-tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      currentPriorityFilter = tab.getAttribute("data-priority");
      renderEmailFeed();
    });
  });

  // Navigation Views
  elements.navViewsMenu.querySelectorAll(".nav-item").forEach(item => {
    item.addEventListener("click", () => {
      elements.navViewsMenu.querySelectorAll(".nav-item").forEach(i => i.classList.remove("active"));
      item.classList.add("active");
      currentView = item.getAttribute("data-view");
      renderEmailFeed();
    });
  });

  // Reset Category Filter
  elements.resetCatFilter.addEventListener("click", () => {
    currentCategoryFilter = "all";
    renderSidebarCategories();
    renderEmailFeed();
  });

  // Copy Draft Action
  elements.btnCopyDraft.addEventListener("click", () => {
    navigator.clipboard.writeText(elements.draftReplyText.value);
    showToast("Suggested reply copied to clipboard!", "success");
  });

  // Regenerate Draft
  elements.btnRegenerateDraft.addEventListener("click", () => {
    const item = emailsData.find(e => e.id === currentSelectedId);
    if (item) {
      generateSuggestedDraft(item);
      showToast("Draft refreshed with contextual template", "info");
    }
  });

  // Approve & Dispatch Draft
  elements.btnDispatchDraft.addEventListener("click", () => {
    const item = emailsData.find(e => e.id === currentSelectedId);
    if (item) {
      item.status = "Resolved";
      selectEmail(item.id);
      renderEmailFeed();
      updateKPIs();
      renderDepartmentHealth();
      showToast(`Email ${item.id} resolved and response dispatched to ${item.sender}!`, "success");
    }
  });

  // Human Override Save
  elements.btnSaveOverride.addEventListener("click", () => {
    const item = emailsData.find(e => e.id === currentSelectedId);
    if (item) {
      const oldCat = item.category;
      item.category = elements.overrideCategory.value;
      item.priority = elements.overridePriority.value;
      item.department = elements.overrideDept.value;
      item.agent = DEPARTMENTS[item.department]?.agents[0] || "Assigned Specialist";

      selectEmail(item.id);
      renderEmailFeed();
      renderSidebarCategories();
      renderDepartmentHealth();
      updateKPIs();

      showToast(`Human correction saved! Re-routed from ${oldCat} to ${item.category}`, "success");
    }
  });

  // Modal open / close handlers
  elements.btnOpenScenarios.addEventListener("click", () => elements.modalIngest.classList.add("active"));
  elements.btnOpenIngest.addEventListener("click", () => elements.modalIngest.classList.add("active"));
  elements.btnCloseModalIngest.addEventListener("click", () => elements.modalIngest.classList.remove("active"));
  elements.btnCancelCustomIngest.addEventListener("click", () => elements.modalIngest.classList.remove("active"));

  elements.btnOpenAnalytics.addEventListener("click", () => {
    renderAnalyticsCharts();
    elements.modalAnalytics.classList.add("active");
  });
  elements.btnCloseModalAnalytics.addEventListener("click", () => elements.modalAnalytics.classList.remove("active"));

  // Close modals on backdrop click
  window.addEventListener("click", (e) => {
    if (e.target === elements.modalIngest) elements.modalIngest.classList.remove("active");
    if (e.target === elements.modalAnalytics) elements.modalAnalytics.classList.remove("active");
  });

  // Custom Ingest Form Submit
  elements.customIngestForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const sender = document.getElementById("input-sender").value.trim();
    const subject = document.getElementById("input-subject").value.trim();
    const body = document.getElementById("input-body").value.trim();

    if (!subject || !body) return;

    ingestCustomEmail(sender, subject, body);
    elements.modalIngest.classList.remove("active");
    elements.customIngestForm.reset();
  });
}

// --- 10. SCENARIOS TRIGGER ENGINE ---
function renderScenarioButtons() {
  const scenarios = [
    {
      title: "🚨 Production DB Outage & Contract Breach",
      desc: "Critical severity, $150,000 SLA penalty risk, immediate routing to Executive Escalations",
      sender: "Marcus Vance <marcus.vance@megacorp-holdings.com>",
      subject: "URGENT: Third DB outage breach of contract - canceling subscription",
      body: "Our system has frozen for the 3rd time this month during audit season. Canceling our $150k enterprise contract unless resolved today 5pm."
    },
    {
      title: "💳 Double Charge & Refund Request",
      desc: "High priority billing dispute, order #45892 extraction, routed to Finance & Billing",
      sender: "Robert Langdon <robert.langdon@acmepartners.com>",
      subject: "Charged twice for order #45892 on American Express",
      body: "I was charged twice $249.99 on my Amex card for order #45892. Please refund the duplicate payment immediately."
    },
    {
      title: "💼 Enterprise Sales RFP (500 Seats)",
      desc: "Commercial expansion inquiry, routed to Enterprise Sales Director",
      sender: "David Vance <david.vance@aerospace-global.com>",
      subject: "RFP Inquiry: Enterprise Platform 500 Seats",
      body: "We are evaluating alternatives for 500 employee seats. Please send your SOC-2 report and pricing tiers for an introductory demo."
    },
    {
      title: "📄 Senior AI Engineer Job Application",
      desc: "Talent inquiry with CV and GitHub portfolio, routed to Talent Acquisition",
      sender: "Priya Sharma <priya.sharma.ai@gmail.com>",
      subject: "Application: Senior Machine Learning Engineer - Priya Sharma",
      body: "Attached is my resume for the Senior ML Engineer role. 7 years experience with transformer fine-tuning and vector databases."
    },
    {
      title: "🛡️ Crypto Phishing Scam Attempt",
      desc: "Malicious spam detection, zero agent dispatch, quarantined automatically",
      sender: "Barrister Charles <wire@nigerian-claim.org>",
      subject: "CONGRATULATIONS: You have won $10,000,000 wire transfer",
      body: "Reply with bank account routing details to receive $10,000,000 lottery award fund."
    }
  ];

  elements.scenariosGrid.innerHTML = scenarios.map((sc, idx) => `
    <div class="scenario-card-btn" data-scenario-idx="${idx}">
      <span class="sc-title">${sc.title}</span>
      <span class="sc-desc">${sc.desc}</span>
    </div>
  `).join("");

  elements.scenariosGrid.querySelectorAll(".scenario-card-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const idx = btn.getAttribute("data-scenario-idx");
      const sc = scenarios[idx];
      ingestCustomEmail(sc.sender, sc.subject, sc.body);
      elements.modalIngest.classList.remove("active");
    });
  });
}

// --- 11. CLIENT AI INGESTION & CLASSIFICATION LOGIC ---
function ingestCustomEmail(senderRaw, subject, body) {
  // Extract Name & Address
  let senderName = senderRaw;
  let senderEmail = senderRaw;
  const match = senderRaw.match(/(.*?)\s*<(.+?)>/);
  if (match) {
    senderName = match[1].trim();
    senderEmail = match[2].trim();
  }

  // Real-time Client Classifier (Rule-based + Keyword Vectors)
  const fullText = `${subject} ${body}`.toLowerCase();

  let category = "General Queries";
  let priority = "Medium";

  if (fullText.includes("outage") || fullText.includes("500") || fullText.includes("crash") || fullText.includes("bug") || fullText.includes("error")) {
    category = "Technical Issues";
    priority = "Critical";
  } else if (fullText.includes("charged") || fullText.includes("refund") || fullText.includes("invoice") || fullText.includes("billing") || fullText.includes("credit card")) {
    category = "Billing";
    priority = "High";
  } else if (fullText.includes("breach") || fullText.includes("unacceptable") || fullText.includes("complaint") || fullText.includes("lawyer") || fullText.includes("sue")) {
    category = "Complaints";
    priority = "Critical";
  } else if (fullText.includes("seats") || fullText.includes("pricing") || fullText.includes("rfp") || fullText.includes("demo") || fullText.includes("contract")) {
    category = "Sales";
    priority = "Medium";
  } else if (fullText.includes("lottery") || fullText.includes("won") || fullText.includes("wire transfer") || fullText.includes("crypto") || fullText.includes("bitcoin")) {
    category = "Spam";
    priority = "Low";
  } else if (fullText.includes("resume") || fullText.includes("cv") || fullText.includes("apply") || fullText.includes("job application") || fullText.includes("interview")) {
    category = "Job Applications";
    priority = "Medium";
  } else if (fullText.includes("shipping") || fullText.includes("order #") || fullText.includes("tracking") || fullText.includes("package")) {
    category = "Customer Support";
    priority = "Medium";
  }

  // Calculate Dynamic Risk Score (0-100)
  let riskScore = 30;
  if (priority === "Critical") riskScore = 88 + Math.floor(Math.random() * 8);
  else if (priority === "High") riskScore = 68 + Math.floor(Math.random() * 10);
  else if (category === "Spam") riskScore = 80;
  else riskScore = 25 + Math.floor(Math.random() * 20);

  // Extract Order ID or Money
  const orderMatch = fullText.match(/(#[a-z0-9\-_]+|ord-\d+|inv-\d+)/i);
  const moneyMatch = fullText.match(/(\$\d+[\d,]*(?:\.\d{2})?)/);

  const newId = `EML-${1000 + emailsData.length + 1}`;
  const assignedDept = CATEGORY_TO_DEPT[category] || "General Inquiries & Reception";
  const assignedAgent = DEPARTMENTS[assignedDept]?.agents[0] || "Assigned Specialist";

  const newEmail = {
    id: newId,
    sender_name: senderName || "Enterprise Sender",
    sender: senderEmail || "sender@enterprise.com",
    subject: subject,
    body: body,
    category: category,
    priority: priority,
    department: assignedDept,
    agent: assignedAgent,
    risk_score: riskScore,
    risk_tier: riskScore >= 80 ? "Severe Operational Risk" : riskScore >= 60 ? "High Priority SLA" : "Standard Review",
    sla_clock: priority === "Critical" ? "⏱️ 59m remaining" : "⏱️ 3h 55m remaining",
    status: category === "Spam" ? "Resolved" : "Pending",
    confidence: 96.5,
    factors: {
      urgency: priority === "Critical" ? 95 : 60,
      sentiment: category === "Complaints" ? 92 : 45,
      impact: moneyMatch ? 85 : 50,
      deadline: priority === "Critical" ? 90 : 40
    },
    entities: {
      customer: senderName || "Enterprise Contact",
      order_id: orderMatch ? orderMatch[0].toUpperCase() : "N/A",
      amount: moneyMatch ? moneyMatch[0] : "N/A",
      deadline: priority === "Critical" ? "Immediate SLA (1 hr)" : "Standard SLA",
      phone: "Logged via Gateway"
    }
  };

  // Prepend to feed
  emailsData.unshift(newEmail);
  renderEmailFeed();
  renderSidebarCategories();
  renderDepartmentHealth();
  updateKPIs();
  selectEmail(newId);

  showToast(`Ingested & Triaged: ${newId} -> ${category} (${priority})`, "success");
}

// --- 12. ANALYTICS CHARTS GENERATOR ---
function renderAnalyticsCharts() {
  const catChart = document.getElementById("analytics-cat-chart");
  const slaChart = document.getElementById("analytics-sla-chart");

  // Category counts
  const catCounts = {};
  CATEGORIES.forEach(c => catCounts[c.name] = 0);
  emailsData.forEach(e => {
    if (catCounts[e.category] !== undefined) catCounts[e.category]++;
  });

  const total = emailsData.length || 1;
  catChart.innerHTML = CATEGORIES.map(cat => {
    const count = catCounts[cat.name] || 0;
    const pct = Math.round((count / total) * 100);
    return `
      <div>
        <div style="display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 2px;">
          <span>${cat.icon} ${cat.name}</span>
          <span style="font-family: var(--font-mono); font-weight: 700;">${count} (${pct}%)</span>
        </div>
        <div class="progress-track">
          <div class="progress-fill" style="width: ${pct}%; background-color: ${cat.color};"></div>
        </div>
      </div>
    `;
  }).join("");

  // Priority counts
  const prioCounts = { Critical: 0, High: 0, Medium: 0, Low: 0 };
  emailsData.forEach(e => {
    if (prioCounts[e.priority] !== undefined) prioCounts[e.priority]++;
  });

  slaChart.innerHTML = Object.keys(prioCounts).map(prio => {
    const count = prioCounts[prio];
    const pct = Math.round((count / total) * 100);
    const color = prio === "Critical" ? "var(--priority-critical)" :
                  prio === "High" ? "var(--priority-high)" :
                  prio === "Medium" ? "var(--priority-medium)" : "var(--priority-low)";
    return `
      <div>
        <div style="display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 2px;">
          <span style="color: ${color}; font-weight: 600;">${prio} SLA</span>
          <span style="font-family: var(--font-mono); font-weight: 700;">${count} (${pct}%)</span>
        </div>
        <div class="progress-track">
          <div class="progress-fill" style="width: ${pct}%; background-color: ${color};"></div>
        </div>
      </div>
    `;
  }).join("");
}

// --- 13. OPTIONAL BACKEND SYNC ---
async function tryBackendSync() {
  try {
    const res = await fetch("/api/emails");
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data) && data.length > 0) {
        emailsData = data;
        renderEmailFeed();
        renderSidebarCategories();
        renderDepartmentHealth();
        updateKPIs();
        selectEmail(emailsData[0].id);
        const engineMode = document.getElementById("kpi-engine-mode");
        if (engineMode) engineMode.textContent = "Live SQLite Backend";
      }
    }
  } catch (err) {
    // Graceful offline fallback: run with embedded high-fidelity dataset
    console.log("Running in standalone client mode with embedded high-fidelity dataset.");
  }
}

// Start Application on Load
document.addEventListener("DOMContentLoaded", initApp);
