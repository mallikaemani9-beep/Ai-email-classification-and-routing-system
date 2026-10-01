"""
Curated Enterprise Email Dataset & Test Scenarios
Covers all 9 categories, diverse priorities, sentiment extremes, and edge cases.
"""

SAMPLE_EMAILS = [
    {
        "id": "EML-1001",
        "sender": "robert.langdon@acmepartners.com",
        "sender_name": "Robert Langdon",
        "subject": "Urgent: Charged twice for my order #45892",
        "body": """Hi Support Team,

I was charged twice on my American Express card for my order #45892 in the amount of $249.99 each. 
This happened during the checkout error yesterday morning.

Please refund the extra payment of $249.99 as soon as possible. My bank account is showing both charges pending.

Thanks,
Robert Langdon
Acme Partners
Direct: (555) 234-8891""",
        "expected_category": "Billing",
        "expected_priority": "High"
    },
    {
        "id": "EML-1002",
        "sender": "devops-alerts@fintechscale.io",
        "sender_name": "Elena Rostova",
        "subject": "CRITICAL OUTAGE: Production API 500 Errors on Checkout Gateway",
        "body": """EMERGENCY INCIDENT:
Our production monitoring systems are reporting sustained 500 Internal Server Errors across the core payment checkout endpoint: https://api.service.com/v2/checkout.

Error spike started at 11:42 AM UTC. Over 4,200 active customer transactions have failed. Database connection pool exhaustion reported on cluster shard-04. 

This is currently blocking all EU transactions. We need on-call SRE and database engineering immediately!

Elena Rostova
Head of Infrastructure, FintechScale""",
        "expected_category": "Technical Issues",
        "expected_priority": "Critical"
    },
    {
        "id": "EML-1003",
        "sender": "marcus.vance@megacorp-holdings.com",
        "sender_name": "Marcus Vance",
        "subject": "Unacceptable service - Formal complaint regarding Breach of Enterprise SLA",
        "body": """To the Executive Team and VP of Customer Relations,

This is completely unacceptable. This is the third time our enterprise dashboard has frozen during our monthly investor reporting period. 

We pay over $150,000 annually for 99.99% uptime and dedicated support, yet our tickets submitted over 48 hours ago have been ignored. If this issue is not fully resolved and a root-cause explanation provided by today 5:00 PM EST, I will have our legal counsel terminate our contract immediately and pursue compensation for business damages.

I demand a call with your VP of Engineering today.

Marcus Vance
Chief Technology Officer
MegaCorp Holdings
Office: (555) 901-2244""",
        "expected_category": "Complaints",
        "expected_priority": "Critical"
    },
    {
        "id": "EML-1004",
        "sender": "jessica.hart@globallogistics.com",
        "sender_name": "Jessica Hart",
        "subject": "Enterprise Plan Demo & Commercial Quote for 600 Seats",
        "body": """Hello Sales Team,

I am the Director of Digital Transformation at Global Logistics Inc. We are currently evaluating alternatives to replace our legacy communication stack across 600 employee seats in North America.

We were impressed by your product feature list and would like to schedule a 30-minute tailored product demo next Tuesday for our procurement committee. Additionally, please provide an indicative enterprise tier pricing quote and information on SSO / SOC2 compliance.

Looking forward to hearing from your account executive.

Best regards,
Jessica Hart
Director of Digital Transformation
Global Logistics Inc.""",
        "expected_category": "Sales",
        "expected_priority": "Medium"
    },
    {
        "id": "EML-1005",
        "sender": "daniel.kim.ai@gmail.com",
        "sender_name": "Daniel Kim",
        "subject": "Application for Senior Machine Learning Engineer - Daniel Kim",
        "body": """Dear Talent Acquisition Team,

I am writing to express my strong interest in the Senior Machine Learning Engineer position recently posted on your careers portal.

With 7 years of hands-on experience building large-scale NLP pipelines, Transformer models, and deploying ML microservices at scale, I believe my background aligns directly with your mission. At my previous role, I reduced latency of our recommendation engine by 42% while scaling to 15 million daily requests.

I have attached my resume and link to my open-source GitHub projects: https://github.com/danielkim-ai.

Thank you for your time and consideration.

Warm regards,
Daniel Kim
Phone: (555) 782-9011""",
        "expected_category": "Job Applications",
        "expected_priority": "Low"
    },
    {
        "id": "EML-1006",
        "sender": "samantha.mills@gmail.com",
        "sender_name": "Samantha Mills",
        "subject": "Delivery tracking inquiry for order #88412",
        "body": """Hi,

I ordered a pair of noise-canceling headphones last Thursday under order #88412. The tracking link emailed to me still says 'Label Created - Awaiting Carrier Pickup'. 

Could someone please check with the warehouse when this will actually ship out? I need this item before my flight this coming Friday.

Thank you so much for your help!

Cheers,
Samantha Mills""",
        "expected_category": "Customer Support",
        "expected_priority": "Medium"
    },
    {
        "id": "EML-1007",
        "sender": "internal.staff@ourcompany.internal",
        "sender_name": "Carlos Gomez",
        "subject": "Inquiry regarding paternity leave policy and health benefit addition",
        "body": """Hi HR Team,

My spouse and I are expecting a new child next month! I wanted to check the current employee handbook guidelines regarding paid parental leave duration and how many weeks in advance I should submit the formal request.

Also, what documentation is required to add our newborn dependent to the Cigna health insurance plan?

Thanks for your guidance,
Carlos Gomez
Design Team""",
        "expected_category": "HR",
        "expected_priority": "Low"
    },
    {
        "id": "EML-1008",
        "sender": "press-inquiry@techherald.org",
        "sender_name": "Audrey Palmer",
        "subject": "Media Inquiry: Bloomberg Tech Herald article on Enterprise AI",
        "body": """Hello Media Relations Team,

I am Audrey Palmer, senior technology correspondent at Tech Herald. We are publishing an in-depth feature next Wednesday covering modern AI deployment in customer operations.

We would love to feature a 15-minute commentary from your Chief Product Officer or Founder regarding the trends in automated workflow triage.

Could you let me know if someone is available for a brief phone or email interview by this Friday 2:00 PM?

Best regards,
Audrey Palmer
Tech Herald""",
        "expected_category": "General Queries",
        "expected_priority": "Medium"
    },
    {
        "id": "EML-1009",
        "sender": "barrister.okafor772@yahoo-mail-claims.xyz",
        "sender_name": "Barrister Charles Okafor",
        "subject": "URGENT CONFIDENTIAL INHERITANCE TRANSFER: $12.5 MILLION USD",
        "body": """ATTENTION: BENEFICIARY,

I am Barrister Charles Okafor, legal solicitor to late Mr. Richard Henderson who died in an offshore accident leaving $12,500,000 USD deposited in a top security escrow bank. 

Because you share the same surname, I am authorized to present you as the rightful next-of-kin beneficiary to claim these funds. You will receive 40% of the total amount.

ACT NOW IMMEDIATELY. Send your full passport copy, home address, and direct banking routing number to wire the initial deposit. Reply urgently to this email address!

Yours faithfully,
Barrister Charles Okafor""",
        "expected_category": "Spam",
        "expected_priority": "Low"
    },
    {
        "id": "EML-1010",
        "sender": "robert.langdon@acmepartners.com",
        "sender_name": "Robert Langdon",
        "subject": "Urgent: Charged twice for my order #45892",
        "body": """Hi Support Team,

I was charged twice on my American Express card for my order #45892 in the amount of $249.99 each. 
This happened during the checkout error yesterday morning.

Please refund the extra payment of $249.99 as soon as possible. My bank account is showing both charges pending.

Thanks,
Robert Langdon
Acme Partners
Direct: (555) 234-8891""",
        "expected_category": "Billing",
        "expected_priority": "High"
    }
]
