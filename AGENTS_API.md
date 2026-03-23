# ContentPilot AI - Agents API Documentation

Complete API reference for all ContentPilot AI agents.

## Table of Contents

1. [Support Agent](#support-agent)
2. [Marketing Agent](#marketing-agent)
3. [Sales Agent](#sales-agent)
4. [Analytics Agent](#analytics-agent)
5. [Billing Agent](#billing-agent)
6. [Orchestrator](#orchestrator)

---

## Support Agent

Handles customer support tickets with AI-powered classification and response generation.

### Class: `SupportAgent`

```python
from app.agents.support_agent import SupportAgent

agent = SupportAgent(config={
    "anthropic_api_key": "your-key"
})
```

### Methods

#### `classify_ticket(ticket_text: str) -> dict`

Classifies incoming support tickets.

**Parameters:**
- `ticket_text` (str): The support ticket content

**Returns:**
```python
{
    "category": "billing|technical|feature_request|bug_report|general",
    "confidence": 0.85,  # 0.0-1.0
    "urgency": "low|medium|high|critical",
    "summary": "Brief classification summary"
}
```

**Example:**
```python
ticket = "I can't log into my account"
result = agent.classify_ticket(ticket)
print(result["category"])  # "technical"
print(result["urgency"])   # "high"
```

#### `generate_response(ticket: dict) -> str`

Generates an AI response to a ticket.

**Parameters:**
- `ticket` (dict): Ticket dictionary with keys: text, category, urgency

**Returns:**
- `str`: Generated response text

**Example:**
```python
response = agent.generate_response({
    "text": "What's your refund policy?",
    "category": "billing",
    "urgency": "low"
})
```

#### `process_ticket(ticket: dict) -> dict`

Complete ticket processing workflow.

**Parameters:**
- `ticket` (dict): Ticket with keys: id, text

**Returns:**
```python
{
    "ticket_id": "TICKET_001",
    "classification": {...},
    "response": "Generated response text",
    "needs_escalation": False,
    "processed_at": "2026-03-23T15:00:00",
    "status": "auto_responded|escalated"
}
```

#### `escalate_ticket(ticket: dict, classification: dict) -> bool`

Determines if ticket should be escalated.

**Rules:**
- Confidence < 0.7
- Urgency is "high" or "critical"
- Ticket marked as escalated

#### `run(tickets: list) -> list`

Process multiple tickets.

**Parameters:**
- `tickets` (list): List of ticket dictionaries

**Returns:**
- `list`: List of processed results

#### `get_statistics() -> dict`

Get support agent statistics.

**Returns:**
```python
{
    "total_tickets_processed": 150,
    "auto_responded": 135,
    "escalated": 15,
    "escalation_rate": 0.1
}
```

### FAQ Knowledge Base

Built-in FAQs covering:
- Pricing information
- Billing and subscription
- Account management
- API keys and security
- Rate limits
- Data retention
- Compliance (GDPR, CCPA, SOC2)

---

## Marketing Agent

Generates content, manages campaigns, and optimizes for SEO.

### Class: `MarketingAgent`

```python
from app.agents.marketing_agent import MarketingAgent

agent = MarketingAgent(config={
    "anthropic_api_key": "your-key"
})
```

### Methods

#### `generate_blog_post(topic: str, keywords: List[str], target_audience: str = "developers") -> dict`

Generates SEO-optimized blog posts.

**Parameters:**
- `topic` (str): Main blog topic
- `keywords` (List[str]): SEO keywords
- `target_audience` (str): Target audience (default: "developers")

**Returns:**
```python
{
    "title": "10 Ways to Automate Your Workflow",
    "meta_description": "Learn how to save time...",
    "slug": "10-ways-automate-workflow",
    "content": "Full blog post content (1500-2000 words)",
    "keywords": ["automation", "workflow", "productivity"],
    "estimated_read_time": "8 minutes",
    "generated_at": "2026-03-23T15:00:00",
    "type": "blog_post"
}
```

**Example:**
```python
blog = agent.generate_blog_post(
    topic="AI Automation Trends",
    keywords=["AI", "automation", "2026", "trends"],
    target_audience="business leaders"
)
print(blog["title"])
print(blog["content"][:500])
```

#### `generate_social_media_posts(content_topic: str, platforms: List[str] = None) -> dict`

Generates posts for multiple social platforms.

**Parameters:**
- `content_topic` (str): Topic for posts
- `platforms` (List[str]): Platforms to generate for (default: ["twitter", "linkedin"])

**Returns:**
```python
{
    "twitter": {
        "thread": ["Tweet 1", "Tweet 2", "Tweet 3"],
        "hashtags": ["#AI", "#Automation"]
    },
    "linkedin": {
        "post": "Professional post content",
        "hashtags": ["#Innovation", "#Business"]
    },
    "instagram": {
        "caption": "Caption with emojis 📱",
        "hashtags": ["#Tech", "#AI"]
    },
    "generated_at": "2026-03-23T15:00:00",
    "topic": "content_topic"
}
```

#### `create_email_campaign(campaign_type: str, segment: str) -> dict`

Creates email marketing campaigns.

**Parameters:**
- `campaign_type` (str): "welcome", "feature_announcement", or "tips_newsletter"
- `segment` (str): Target customer segment

**Returns:**
```python
{
    "campaign_name": "New User Welcome Series",
    "type": "welcome",
    "segment": "new_users",
    "emails": [
        {
            "sequence": 1,
            "subject_line_a": "Welcome to ContentPilot! 🎉",
            "subject_line_b": "Get started with ContentPilot",
            "preview_text": "Here's how to make the most...",
            "body": "HTML email content",
            "cta": "Start Tour",
            "schedule": "Day 1"
        }
    ],
    "generated_at": "2026-03-23T15:00:00",
    "status": "draft"
}
```

**Campaign Types:**
- `welcome`: 3-email onboarding sequence
- `feature_announcement`: New feature launch
- `tips_newsletter`: Weekly tips and best practices

#### `generate_seo_metadata(title: str, content_snippet: str) -> dict`

Generates SEO metadata for content.

**Returns:**
```python
{
    "meta_title": "AI Automation Guide - ContentPilot",
    "meta_description": "Learn how to automate your...",
    "h1": "The Complete Guide to AI Automation",
    "keywords": ["AI", "automation", "guide"],
    "slug": "ai-automation-guide",
    "focus_keyword": "AI automation",
    "related_keywords": ["workflow automation", "AI tools"]
}
```

#### `plan_content_calendar(weeks_ahead: int = 4, topics: List[str] = None) -> dict`

Plans content calendar for coming weeks.

**Returns:**
```python
{
    "calendar": [
        {
            "week": 1,
            "start_date": "2026-03-24",
            "blog_post": {
                "topic": "Q2 Product Roadmap",
                "keywords": ["product", "roadmap"]
            },
            "social_media": ["Topic 1", "Topic 2"],
            "email_campaign": "tips_newsletter",
            "notes": "Align with product launch"
        }
    ],
    "performance_targets": {
        "blog_views": "2000 per post",
        "social_engagement": "5%",
        "email_open_rate": "35%"
    }
}
```

#### `track_performance(content_id: str, metrics: dict) -> None`

Track performance metrics for content.

**Parameters:**
```python
metrics = {
    "views": 5000,
    "clicks": 250,
    "ctr": 0.05,
    "social_shares": 120
}
agent.track_performance("blog_post_001", metrics)
```

#### `run(content_plan: dict = None) -> dict`

Run marketing agent with optional content plan.

---

## Sales Agent

Manages customer acquisition and conversion sequences.

### Class: `SalesAgent`

```python
from app.agents.sales_agent import SalesAgent

agent = SalesAgent(config={
    "anthropic_api_key": "your-key"
})
```

### Methods

#### `generate_welcome_email(user_profile: dict) -> dict`

Creates personalized welcome email for new signups.

**Parameters:**
```python
user_profile = {
    "id": "user_123",
    "name": "Jane Doe",
    "company": "TechCorp",
    "industry": "SaaS",
    "signup_date": "2026-03-23"
}
```

**Returns:**
```python
{
    "subject": "Welcome to ContentPilot!",
    "preview_text": "Let's get you started...",
    "body": "HTML email content",
    "cta_button": "Get Started",
    "cta_link": "/get-started",
    "type": "welcome",
    "user_id": "user_123",
    "sent_at": "2026-03-23T15:00:00"
}
```

#### `create_trial_conversion_sequence(user_profile: dict, trial_days: int = 14) -> dict`

Creates trial-to-paid conversion email sequence.

**Sequence:**
1. Day 1: Welcome & quick-start
2. Day 3-5: Feature showcase
3. Day 7: Aha moment / case study
4. Day 10-12: Limited-time offer (20% off)

**Returns:**
```python
{
    "sequence_name": "Trial Conversion Sequence",
    "emails": [
        {
            "day": 1,
            "subject": "Welcome to your trial",
            "preview_text": "...",
            "body": "HTML content",
            "cta": "Get Started"
        }
    ],
    "expected_conversion_rate": "25%"
}
```

#### `identify_at_risk_customers(customer_data: List[dict]) -> List[dict]`

Identifies customers at risk of churn.

**Parameters:**
```python
customer_data = [
    {
        "id": "cust_001",
        "name": "Acme Corp",
        "last_login": "2026-03-01",
        "api_calls_last_week": 100,
        "plan": "Pro"
    }
]
```

**Returns:**
```python
[
    {
        "customer_id": "cust_001",
        "name": "Acme Corp",
        "risk_level": "high",
        "reason": "No activity in 3 weeks",
        "last_active": "2026-03-01",
        "recommended_action": "Send re-engagement email"
    }
]
```

#### `create_reengagement_email(customer_profile: dict) -> dict`

Creates re-engagement email for at-risk customers.

**Parameters:**
```python
customer = {
    "id": "cust_001",
    "name": "John Smith",
    "reason": "Low API usage",
    "plan": "Pro"
}
```

**Returns:**
```python
{
    "subject": "We miss you!",
    "preview_text": "Let's talk...",
    "body": "HTML content",
    "incentive": "20% discount on annual plan",
    "cta": "Let's talk",
    "type": "reengagement",
    "customer_id": "cust_001"
}
```

#### `create_upsell_sequence(customer_profile: dict, current_plan: str) -> dict`

Creates upsell sequence for plan upgrades.

**Upgrades:**
- Starter → Pro
- Pro → Agency

**Returns:**
```python
{
    "sequence_name": "Upsell to Pro",
    "emails": [
        {
            "day": 1,
            "subject": "You're using 85% of your limit",
            "body": "HTML content",
            "cta": "View upgrade options"
        }
    ],
    "expected_value": "Additional MRR if successful"
}
```

#### `create_winback_campaign(churned_customer: dict) -> dict`

Creates win-back campaign for churned customers.

**3-Email Sequence:**
1. Day 1: Personal "we miss you"
2. Day 5: Address churn reason
3. Day 10: Special win-back offer (30% off, free trial, etc.)

#### `track_conversion_metrics(sequence_id: str, metrics: dict) -> None`

Tracks conversion metrics.

**Example:**
```python
metrics = {
    "opened": 450,
    "clicked": 125,
    "converted": 30,
    "open_rate": 0.75,
    "click_rate": 0.28,
    "conversion_rate": 0.067
}
agent.track_conversion_metrics("seq_001", metrics)
```

#### `run(action: str, **kwargs) -> dict`

Run sales agent with specific action.

**Actions:**
- `welcome` - Generate welcome email
- `trial_sequence` - Create trial conversion
- `identify_atrisk` - Find at-risk customers
- `upsell` - Create upsell sequence
- `winback` - Create win-back campaign

---

## Analytics Agent

Generates reports, tracks KPIs, and provides recommendations.

### Class: `AnalyticsAgent`

```python
from app.agents.analytics_agent import AnalyticsAgent

agent = AnalyticsAgent(config={
    "anthropic_api_key": "your-key"
})
```

### Methods

#### `calculate_kpis(business_data: dict) -> dict`

Calculates key performance indicators.

**Parameters:**
```python
business_data = {
    "mrr": 50000,
    "total_customers": 500,
    "new_customers_this_month": 45,
    "churned_customers": 8,
    "free_to_paid_conversions": 25,
    "cac": 300,
    "ltv": 3000,
    "api_calls_this_month": 5000000,
    "api_limit": 10000000,
    "api_cost": 1500
}
```

**Returns:**
```python
{
    "mrr": {
        "current": 50000,
        "change_percent": 5.0,
        "status": "up|down|stable"
    },
    "churn_rate": {
        "percent": 1.6,
        "status": "low|medium|high"
    },
    "conversion_rate": {
        "percent": 5.0,
        "target": 8.0
    },
    "cac": {
        "amount": 300,
        "roi": 10.0
    },
    "ltv": {
        "amount": 3000,
        "ltv_to_cac_ratio": 10.0
    },
    "api_usage": {
        "calls_this_month": 5000000,
        "percent_of_limit": 50.0
    },
    "growth_rate": {
        "percent": 9.0,
        "trend": "accelerating|stable|decelerating"
    },
    "health_score": 85
}
```

**Key Metrics:**
- **MRR**: Monthly Recurring Revenue
- **Churn Rate**: % of customers lost monthly
- **Conversion Rate**: Free to paid conversion %
- **CAC**: Customer Acquisition Cost
- **LTV**: Customer Lifetime Value
- **LTV:CAC Ratio**: Should be > 3.0 (ideal)

#### `generate_daily_report(daily_metrics: dict) -> dict`

Generates daily business report.

**Returns:**
```python
{
    "date": "2026-03-23",
    "type": "daily",
    "executive_summary": "Summary of daily performance",
    "highlights": ["Achievement 1", "Achievement 2"],
    "concerns": ["Issue 1"],
    "metrics": {
        "new_signups": 12,
        "api_calls": 500000,
        "active_users": 1200,
        "revenue": 1667
    },
    "api_health": "healthy|degraded|down"
}
```

#### `generate_weekly_report(weekly_data: dict) -> dict`

Generates comprehensive weekly report.

**Includes:**
- Revenue trends
- Growth metrics
- Churn analysis
- Product usage patterns
- Customer satisfaction
- Operational metrics

**Returns:**
```python
{
    "week": "2026-W12",
    "period": "2026-03-16 to 2026-03-22",
    "summary": "Overall business summary",
    "sections": {
        "revenue": {"mrr": 50000, "growth": "5%", "status": "on_track"},
        "growth": {"new_customers": 45, "signups": 320, "conversion": "8%"},
        "churn": {"customers_lost": 8, "rate": "1.6%", "main_reasons": []},
        "product_usage": {"daily_active_users": 1200, "api_calls": 5000000},
        "support": {"tickets": 25, "avg_response_time": "2 hours"},
        "operations": {"api_costs": 1500, "uptime": "99.9%", "error_rate": "0.1%"}
    },
    "recommendations": [
        {
            "priority": "high",
            "action": "Increase marketing spend - conversion trending up"
        }
    ]
}
```

#### `identify_trends_and_anomalies(historical_data: List[dict]) -> dict`

Identifies patterns in data.

**Returns:**
```python
{
    "trends": [
        {
            "metric": "MRR",
            "direction": "increasing",
            "rate": "5% per week"
        }
    ],
    "anomalies": [
        {
            "date": "2026-03-20",
            "metric": "API Calls",
            "value": 750000,
            "deviation": "50% above average",
            "possible_cause": "Marketing campaign"
        }
    ],
    "correlations": [
        {
            "metric1": "New Signups",
            "metric2": "API Calls",
            "correlation": "0.85 (strong positive)"
        }
    ],
    "forecast": {
        "mrr_next_week": 52500,
        "churn_next_week": "1.5%",
        "confidence": "85%"
    }
}
```

#### `generate_recommendations(current_kpis: dict, trends: dict) -> List[dict]`

Generates data-driven business recommendations.

**Returns:**
```python
[
    {
        "title": "Increase marketing investment",
        "description": "Conversion rate trending up, reduce CAC",
        "priority": "high",
        "expected_impact": {"metric": "MRR", "change": "+10%"},
        "effort": "medium",
        "timeline": "2 weeks"
    }
]
```

#### `generate_dashboard_data(kpis: dict, historical_data: List[dict]) -> dict`

Generates chart-ready data for dashboards.

**Returns data for:**
- MRR Chart (line chart)
- Churn Rate Gauge
- Conversion Funnel
- Customer Growth
- API Usage
- Revenue Breakdown by Plan

#### `monitor_api_costs(usage_data: dict) -> dict`

Monitors API costs and provides alerts.

**Returns:**
```python
{
    "daily_cost": 50.00,
    "monthly_projected": 1500.00,
    "monthly_budget": 2000.00,
    "budget_percent_used": 75.0,
    "cost_trend": "increasing|stable|decreasing",
    "cost_per_customer": 3.0,
    "alerts": [
        {
            "type": "budget_warning",
            "message": "75% of monthly budget spent"
        }
    ],
    "optimization_opportunities": [
        {
            "suggestion": "Batch API calls",
            "potential_savings": "15%"
        }
    ]
}
```

#### `run(report_type: str = "weekly", data: dict = None) -> dict`

Run analytics agent.

**Report Types:**
- `daily` - Daily summary
- `weekly` - Comprehensive analysis
- `summary` - Quick snapshot

---

## Billing Agent

Handles payments, subscriptions, and financial reconciliation.

### Class: `BillingAgent`

```python
from app.agents.billing_agent import BillingAgent

agent = BillingAgent(config={
    "anthropic_api_key": "your-key",
    "stripe_api_key": "sk_..."
})
```

### Configuration

```python
REFUND_AUTO_APPROVE_THRESHOLD = 50.0  # Auto-approve refunds < $50
```

### Methods

#### `handle_failed_payment(payment_event: dict) -> dict`

Handles failed payment and creates recovery sequence.

**Parameters:**
```python
payment_event = {
    "customer_id": "cust_123",
    "customer_name": "Acme Corp",
    "amount": 299,
    "plan": "Pro",
    "reason": "Card declined",
    "failed_at": "2026-03-23T15:00:00"
}
```

**3-Email Recovery Sequence:**
1. Day 1: Payment failed, easy retry
2. Day 4: Friendly reminder, offer help
3. Day 7: Last attempt before suspension

**Returns:**
```python
{
    "sequence": "failed_payment_recovery",
    "customer_id": "cust_123",
    "amount": 299,
    "emails": [
        {
            "day": 1,
            "subject": "Your payment didn't go through",
            "cta": "Retry Payment"
        }
    ],
    "expected_recovery_rate": "65%"
}
```

#### `handle_subscription_change(change_event: dict) -> dict`

Handles subscription upgrades and downgrades.

**Parameters:**
```python
change_event = {
    "customer_id": "cust_456",
    "customer_name": "TechCorp",
    "type": "upgrade",  # or "downgrade"
    "from_plan": "Starter",
    "to_plan": "Pro",
    "effective_date": "2026-03-23",
    "proration_amount": 50.00
}
```

**Returns:**
```python
{
    "change_id": "change_uuid",
    "type": "subscription_upgrade",
    "billing_summary": {
        "old_plan": "Starter",
        "new_plan": "Pro",
        "old_price": 99.0,
        "new_price": 299.0,
        "price_change": 200.0,
        "proration": 50.0
    },
    "confirmation_email": {
        "subject": "Subscription Upgrade Confirmation",
        "body": "HTML content",
        "cta": "View Billing"
    },
    "next_billing_date": "2026-04-23"
}
```

#### `send_usage_limit_warning(customer: dict) -> dict`

Sends usage limit warnings at 80%, 95%, 100%.

**Parameters:**
```python
customer = {
    "id": "cust_789",
    "name": "Startup Inc",
    "plan": "Pro",
    "usage_percent": 85,  # % of monthly limit
    "monthly_limit": 500000,  # tokens
    "days_in_billing": 15
}
```

**Returns:**
```python
{
    "warning_level": "85%",
    "subject": "You're at 85% of your usage limit",
    "urgency": "medium",
    "cta": "Upgrade Plan",
    "body": "HTML content"
}
```

#### `generate_invoice(invoice_data: dict) -> dict`

Generates professional invoices.

**Parameters:**
```python
invoice_data = {
    "customer_id": "cust_001",
    "customer_name": "Acme Corp",
    "invoice_date": "2026-03-23",
    "due_date": "2026-04-06",
    "line_items": [
        {"description": "Pro Plan", "amount": 299.0}
    ],
    "subtotal": 299.0,
    "tax": 29.90,
    "total": 328.90
}
```

**Returns:**
```python
{
    "invoice_number": "INV-2026-001",
    "invoice_date": "2026-03-23",
    "due_date": "2026-04-06",
    "html_content": "<html>Invoice</html>",
    "text_summary": "Text version",
    "total": 328.90
}
```

#### `handle_refund_request(refund_request: dict) -> dict`

Handles refund requests with auto-approval logic.

**Auto-Approval Rules:**
- Automatically approve if < $50
- Flag for manual review if >= $50

**Parameters:**
```python
refund_request = {
    "customer_id": "cust_123",
    "customer_name": "Jane Doe",
    "amount": 35.0,  # Will auto-approve
    "reason": "Accidental charge",
    "invoice_date": "2026-03-20",
    "days_since_purchase": 3,
    "customer_history": "Good customer"
}
```

**Returns:**
```python
{
    "refund_id": "refund_uuid",
    "customer_id": "cust_123",
    "amount": 35.0,
    "status": "approved",  # or "pending_review"
    "reason": "Auto-approved (under $50 threshold)",
    "response_email": {
        "subject": "Your refund has been processed",
        "body": "HTML content",
        "tone": "apologetic"
    },
    "processed_at": "2026-03-23"
}
```

#### `reconcile_monthly_revenue(transactions: List[dict]) -> dict`

Reconciles monthly revenue.

**Returns:**
```python
{
    "period": "2026-03",
    "revenue": {
        "gross": 50000.0,
        "refunds": -500.0,
        "net": 49500.0
    },
    "by_plan": {
        "starter": 10000.0,
        "pro": 30000.0,
        "agency": 10000.0
    },
    "metrics": {
        "arpu": 99.0,  # Average Revenue Per User
        "mrr": 49500.0,
        "refund_rate": 0.01
    },
    "reconciliation": {
        "status": "balanced",
        "difference": 0.0
    }
}
```

#### `run(action: str, **kwargs) -> dict`

Run billing agent with specific action.

**Actions:**
- `handle_failed_payment` - Payment recovery
- `subscription_change` - Plan upgrades/downgrades
- `usage_warning` - Usage alerts
- `generate_invoice` - Invoice creation
- `handle_refund` - Refund processing
- `reconcile_revenue` - Monthly reconciliation

---

## Orchestrator

Master coordinator for all agents.

### Class: `Orchestrator`

```python
from app.agents.orchestrator import Orchestrator

orchestrator = Orchestrator(config={
    "anthropic_api_key": "your-key"
})
```

### Methods

#### `check_agent_health() -> Dict[str, bool]`

Performs health checks on all agents.

**Returns:**
```python
{
    "support": True,
    "marketing": True,
    "sales": True,
    "analytics": True,
    "billing": True
}
```

#### `run_support_workflow(tickets: List[dict]) -> dict`

Runs support agent workflow.

#### `run_marketing_workflow() -> dict`

Runs marketing agent workflow.

#### `run_sales_workflow(signups: List[dict], at_risk_customers: List[dict]) -> dict`

Runs sales agent workflow.

#### `run_analytics_workflow(business_data: dict) -> dict`

Runs analytics agent workflow.

#### `run_billing_workflow(events: List[dict]) -> dict`

Runs billing agent workflow.

#### `get_execution_summary() -> dict`

Gets execution summary.

**Returns:**
```python
{
    "total_executions": 150,
    "agents_status": {
        "support": True,
        "marketing": True,
        "sales": True,
        "analytics": True,
        "billing": True
    },
    "last_runs": {
        "support": "2026-03-23T15:00:00",
        "marketing": "2026-03-23T14:30:00"
    },
    "recent_activity": [...]
}
```

#### `run_all_workflows(business_state: dict) -> dict`

Runs all workflows in coordinated fashion.

**Parameters:**
```python
business_state = {
    "support_tickets": [...],
    "billing_events": [...],
    "signups": [...],
    "at_risk_customers": [...],
    "business_data": {...}
}
```

**Returns:**
```python
{
    "timestamp": "2026-03-23T15:00:00",
    "health_status": {...},
    "workflows": {
        "support": {...},
        "billing": {...},
        "sales": {...},
        "marketing": {...},
        "analytics": {...}
    }
}
```

### Usage Example

```python
# Initialize orchestrator
orchestrator = Orchestrator()

# Prepare business state
business_state = {
    "support_tickets": [
        {"id": "TICKET_001", "text": "I need help..."}
    ],
    "signups": [
        {"id": "user_001", "name": "Jane Doe", "company": "Acme"}
    ],
    "billing_events": [
        {"type": "failed_payment", "customer_id": "cust_123"}
    ],
    "business_data": {...}
}

# Run all workflows
results = orchestrator.run_all_workflows(business_state)

# Check results
print(results["health_status"])
print(results["workflows"]["support"])
```

---

## Error Handling

All agents handle errors gracefully:

```python
{
    "error": "Error message",
    "timestamp": "2026-03-23T15:00:00"
}
```

Check logs for detailed error information:
```bash
tail -f logs/orchestrator.log
```

## Rate Limiting

Default: 500 requests per minute per agent

## Response Times

- Support classification: 1-2 seconds
- Email generation: 3-5 seconds
- Report generation: 10-30 seconds
- Blog post creation: 20-60 seconds

---

*For updates and additional documentation, see README.md*
