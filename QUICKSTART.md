# ContentPilot AI - Quick Start Guide

Get the autonomous AI workforce up and running in 5 minutes.

## Prerequisites

- Python 3.9+
- Anthropic API key (get at https://console.anthropic.com)
- Optional: Stripe, SendGrid, Twitter, LinkedIn API keys

## Installation

### 1. Clone and Setup

```bash
cd /path/to/ContentPilot-AI

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

**Minimum Required:**
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 3. Create Logs Directory

```bash
mkdir -p logs
```

## Running the Agents

### Run Individual Agent

**Support Agent Example:**
```bash
python app/agents/support_agent.py
```

**Marketing Agent Example:**
```bash
python app/agents/marketing_agent.py
```

**Sales Agent Example:**
```bash
python app/agents/sales_agent.py
```

**Analytics Agent Example:**
```bash
python app/agents/analytics_agent.py
```

**Billing Agent Example:**
```bash
python app/agents/billing_agent.py
```

### Run Master Orchestrator

```bash
python -m app.agents.orchestrator
```

This will:
1. Check health of all agents
2. Run support workflow
3. Run billing workflow
4. Run sales workflow
5. Run marketing workflow
6. Run analytics workflow
7. Log everything to `logs/orchestrator.log`

## Example Usage in Python

### Support Agent

```python
from app.agents.support_agent import SupportAgent

agent = SupportAgent()

# Process a support ticket
tickets = [
    {
        "id": "TICKET_001",
        "text": "How do I cancel my subscription?"
    }
]

results = agent.run(tickets)
print(results[0]["response"])
```

### Marketing Agent

```python
from app.agents.marketing_agent import MarketingAgent

agent = MarketingAgent()

# Generate a blog post
blog = agent.generate_blog_post(
    topic="AI Automation in 2026",
    keywords=["AI", "automation", "2026"],
    target_audience="business leaders"
)

print(blog["title"])
print(blog["content"][:500])
```

### Sales Agent

```python
from app.agents.sales_agent import SalesAgent

agent = SalesAgent()

# Generate welcome email
user = {
    "id": "user_123",
    "name": "Jane Doe",
    "company": "TechCorp",
    "industry": "SaaS"
}

welcome = agent.generate_welcome_email(user)
print(welcome["subject"])
print(welcome["body"][:200])
```

### Analytics Agent

```python
from app.agents.analytics_agent import AnalyticsAgent

agent = AnalyticsAgent()

# Calculate KPIs
business_data = {
    "mrr": 50000,
    "total_customers": 500,
    "new_customers_this_month": 45,
    "churned_customers": 8
}

kpis = agent.calculate_kpis(business_data)
print(f"MRR: ${kpis['mrr']['current']}")
print(f"Health Score: {kpis['health_score']}")
```

### Billing Agent

```python
from app.agents.billing_agent import BillingAgent

agent = BillingAgent()

# Handle failed payment
payment = {
    "customer_id": "cust_123",
    "customer_name": "Acme Corp",
    "amount": 299,
    "plan": "Pro"
}

recovery = agent.handle_failed_payment(payment)
print(f"Recovery sequence: {recovery['sequence']}")
```

### Orchestrator

```python
from app.agents.orchestrator import Orchestrator

orchestrator = Orchestrator()

# Prepare business data
business_state = {
    "support_tickets": [
        {"id": "TICKET_001", "text": "Help with pricing"}
    ],
    "signups": [
        {"id": "user_001", "name": "John Doe", "company": "StartupXYZ"}
    ],
    "billing_events": [
        {"type": "failed_payment", "customer_id": "cust_123", "amount": 299}
    ],
    "business_data": {
        "business_data": {"mrr": 50000, "total_customers": 500},
        "weekly_data": {"new_customers": 45}
    }
}

# Run all workflows
results = orchestrator.run_all_workflows(business_state)

print("Health Status:", results["health_status"])
print("Support Results:", results["workflows"]["support"])
print("Sales Results:", results["workflows"]["sales"])
```

## Docker Setup (Optional)

### Build and Run with Docker Compose

```bash
# Create .env file
cp .env.example .env
# Edit .env with your API keys

# Start services
docker-compose up

# Run orchestrator in container
docker-compose run app python -m app.agents.orchestrator
```

### Individual Container

```bash
# Build image
docker build -t contentpilot-ai .

# Run container
docker run --env-file .env contentpilot-ai python -m app.agents.orchestrator
```

## Monitoring & Logs

### View Logs

```bash
# Real-time logs
tail -f logs/orchestrator.log

# Last 50 lines
tail -50 logs/orchestrator.log

# Grep for errors
grep ERROR logs/orchestrator.log

# Grep for specific agent
grep "Support Agent" logs/orchestrator.log
```

### Check Agent Health

```python
from app.agents.orchestrator import Orchestrator

orchestrator = Orchestrator()
health = orchestrator.check_agent_health()
print(health)
```

## Common Issues & Solutions

### Issue: "ANTHROPIC_API_KEY not set"

**Solution:** Make sure `.env` file exists and has your API key:
```bash
echo "ANTHROPIC_API_KEY=sk-ant-your-key" >> .env
```

### Issue: ImportError when running agents

**Solution:** Make sure you're in the project root and have activated venv:
```bash
source venv/bin/activate
python -m app.agents.support_agent
```

### Issue: "ModuleNotFoundError: No module named 'anthropic'"

**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: Logs directory not found

**Solution:** Create logs directory:
```bash
mkdir -p logs
```

## Next Steps

1. **Read Full Documentation**: See `README.md` for detailed agent descriptions
2. **API Reference**: See `AGENTS_API.md` for complete API documentation
3. **Configure Integrations**: Add Stripe, SendGrid, Twitter, LinkedIn keys to `.env`
4. **Set Up Scheduling**: Configure cron jobs or APScheduler for regular runs
5. **Integrate with Database**: Connect to PostgreSQL for persistence

## Scheduled Execution

### Cron Jobs (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Support agent - every 30 minutes
*/30 * * * * cd /path/to/ContentPilot-AI && source venv/bin/activate && python -m app.agents.support_agent >> logs/support.log 2>&1

# Marketing agent - daily at 9 AM
0 9 * * * cd /path/to/ContentPilot-AI && source venv/bin/activate && python -m app.agents.marketing_agent >> logs/marketing.log 2>&1

# Analytics agent - daily at 8 AM
0 8 * * * cd /path/to/ContentPilot-AI && source venv/bin/activate && python -m app.agents.analytics_agent >> logs/analytics.log 2>&1

# Orchestrator - twice daily (8 AM and 6 PM)
0 8,18 * * * cd /path/to/ContentPilot-AI && source venv/bin/activate && python -m app.agents.orchestrator >> logs/orchestrator.log 2>&1
```

### Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set Trigger (e.g., daily at 8 AM)
4. Set Action: `python -m app.agents.orchestrator`
5. Set "Start in" folder to project root

## Performance Tips

- **Batch Processing**: Process tickets/events in batches for better throughput
- **Token Optimization**: Use concise prompts to reduce token usage
- **Caching**: Implement Redis caching for FAQ lookups
- **Async Processing**: Use task queues (Celery, RQ) for long-running tasks
- **Rate Limiting**: Respect API rate limits with backoff strategies

## Testing

```bash
# Test support agent with sample data
python app/agents/support_agent.py

# Test marketing agent
python app/agents/marketing_agent.py

# Test orchestrator
python -m app.agents.orchestrator
```

## Production Deployment

### Requirements Checklist

- [ ] All API keys configured in secure environment variables
- [ ] PostgreSQL database set up and migrated
- [ ] Redis cache configured
- [ ] Logging configured to centralized service
- [ ] Error monitoring (Sentry, etc.) configured
- [ ] Scheduled tasks configured with APScheduler or cron
- [ ] API rate limits configured
- [ ] Database backups automated
- [ ] Monitoring and alerting set up

### Recommended Setup

```
Production Structure:
├── ContentPilot-AI/
│   ├── app/
│   ├── logs/
│   ├── config.py
│   └── ...
├── systemd service (Linux)
├── nginx reverse proxy
├── PostgreSQL database
├── Redis cache
└── Monitoring (Prometheus, Grafana)
```

### Systemd Service (Linux)

Create `/etc/systemd/system/contentpilot.service`:

```ini
[Unit]
Description=ContentPilot AI Orchestrator
After=network.target

[Service]
Type=simple
User=contentpilot
WorkingDirectory=/opt/contentpilot
Environment="PATH=/opt/contentpilot/venv/bin"
ExecStart=/opt/contentpilot/venv/bin/python -m app.agents.orchestrator
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable contentpilot
sudo systemctl start contentpilot
sudo systemctl status contentpilot
```

## Support & Resources

- **Anthropic API Docs**: https://docs.anthropic.com
- **Stripe API**: https://stripe.com/docs/api
- **SendGrid API**: https://docs.sendgrid.com/api-reference

---

**Ready to go!** Start with:
```bash
python -m app.agents.orchestrator
```

For detailed agent APIs, see `AGENTS_API.md`
