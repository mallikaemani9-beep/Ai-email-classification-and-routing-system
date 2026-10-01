"""
Suggested Response & Draft Generator
Constructs context-aware, empathetic, and actionable email drafts
for authorized agents to review and send with 1 click.
"""

from typing import Dict, Any

def generate_draft_response(
    category: str,
    sentiment: str,
    entities: Dict[str, Any],
    subject: str,
    body: str,
    assigned_agent: str = "Customer Support Team"
) -> str:
    """
    Generates tailored, high-converting, professional draft response.
    """
    customer_name = entities.get("customer_name") or "there"
    order_id = entities.get("primary_order_id")
    order_ref = f" regarding Order #{order_id}" if order_id and order_id != "N/A" else ""
    agent_signoff = assigned_agent.split("(")[0].strip() if assigned_agent else "MailPulse Support Team"
    
    if category == "Billing":
        return f"""Dear {customer_name},

Thank you for reaching out to our Finance & Billing team{order_ref}.

We understand you have encountered a billing discrepancy regarding your account. We take payment security and accuracy very seriously. Our team has already initiated a review of our payment gateway transaction logs for this charge.

Next Steps:
1. If this is verified as a duplicate charge, we will immediately initiate a full refund back to your original payment method (typically appearing in 2-4 business days).
2. We have temporarily placed a billing protection hold on your account so no further charges occur.

You will receive an automated confirmation with your refund receipt number within 24 hours. If you have any additional receipts or bank statement screenshots to attach, please reply directly to this thread.

Warm regards,
{agent_signoff}
Finance & Billing Operations
"""

    elif category == "Technical Issues":
        return f"""Hi {customer_name},

Thank you for reporting this technical issue to our Engineering & IT Ops team.

Our on-call engineering team has logged this incident and is currently investigating the error logs and telemetry. We understand how critical uninterrupted service is for your workflow, and we are treating this as high priority.

Incident Reference: {entities.get('primary_order_id', 'TKT-AUTO')}
Current Status: Under Active Investigation

Could you please confirm if this issue reproduces in an incognito window or if you noticed any specific HTTP status codes (such as 500 or 504)? Any browser console logs or error screenshots will help us resolve this even faster.

We will provide our next operational update within 60 minutes.

Best regards,
{agent_signoff}
Technical Support & Site Reliability
"""

    elif category == "Complaints":
        return f"""Dear {customer_name},

Thank you for contacting Executive Relations. I want to personally apologize for the frustrating experience you have had with our services.

Your feedback has been escalated directly to our leadership team. We recognize that we fell short of the high standards you deserve, and we are actively taking corrective measures to ensure this is remedied immediately.

A dedicated senior case specialist has been assigned to your ticket. We are currently conducting an internal review of what transpired and will be contacting you directly via telephone or email with a comprehensive resolution and appropriate account credits.

Thank you for your patience and for bringing this to our attention.

Sincerely,
{agent_signoff}
Office of Executive Escalations & Customer Care
"""

    elif category == "Sales":
        return f"""Hi {customer_name},

Thank you for your interest in our Enterprise platform solutions!

We would be delighted to learn more about your organization's technical requirements and demonstrate how our solution can streamline your team's workflows.

I have reserved priority calendar slots for a 25-minute tailored product demonstration and commercial overview. You can pick any convenient slot directly on my schedule here: [Schedule Enterprise Demo].

In the meantime, I've attached our Enterprise Architecture Overview and Security Whitepaper for your review.

Looking forward to speaking with you!

Best regards,
{agent_signoff}
Enterprise Sales & Solutions Architecture
"""

    elif category == "Job Applications":
        return f"""Dear {customer_name},

Thank you for your application and interest in joining our team!

We have successfully received your resume and application materials. Our Talent Acquisition team is currently reviewing your background and qualifications against the role requirements.

Due to a high volume of applicants, our review cycle typically takes 3-5 business days. If your profile matches what the hiring manager is seeking, our recruiter will reach out directly to schedule an introductory video call.

We appreciate the time you invested in applying to our company!

Best regards,
{agent_signoff}
Talent Acquisition & People Operations
"""

    elif category == "HR":
        return f"""Hi {customer_name},

Thank you for contacting People Operations.

We have received your HR inquiry regarding internal policy and benefits. Your request is being handled confidentially by our team.

We are reviewing the relevant policy guidelines and employee handbook documentation. A representative will provide you with the exact forms and next steps shortly.

Best regards,
{agent_signoff}
People Operations & Human Resources
"""

    elif category == "Spam":
        return """[Automated System Notice]
This email has been classified as unsolicited spam or security phishing. It has been quarantined by MailPulse SecOps. No automated response has been dispatched to the sender to prevent email address validation.
"""

    else:  # General Queries / Customer Support
        return f"""Hi {customer_name},

Thank you for reaching out to us{order_ref}!

We have received your message and a member of our Customer Support team has been assigned to assist you with: {entities.get('identified_issue', 'your inquiry')}.

Our standard response window is within a few hours. If you have any additional context or details you would like to append to this request, feel free to reply directly to this email.

Have a wonderful day!

Warm regards,
{agent_signoff}
Customer Experience Team
"""
