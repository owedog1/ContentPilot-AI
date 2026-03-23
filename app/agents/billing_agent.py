"""
Billing AI Agent
Handles payment events, subscription management, usage limits, and revenue reconciliation.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Optional, List
import anthropic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BillingAgent:
    """
    Autonomous billing agent that:
    - Monitors Stripe webhooks
    - Handles failed payment recovery
    - Manages subscription upgrades/downgrades
    - Sends usage limit warnings
    - Generates and sends invoices
    - Handles refund requests
    - Reconciles monthly revenue
    """

    REFUND_AUTO_APPROVE_THRESHOLD = 50.0  # Auto-approve refunds under $50

    def __init__(self, config: Optional[dict] = None):
        """
        Initialize the Billing Agent.

        Args:
            config: Configuration dictionary with API keys and settings
        """
        self.config = config or {}
        self.client = anthropic.Anthropic(
            api_key=self.config.get("anthropic_api_key", "")
        )
        self.model = "claude-3-5-sonnet-20241022"
        self.transaction_log = []
        self.pending_refunds = []
        logger.info("Billing Agent initialized")

    def handle_failed_payment(self, payment_event: dict) -> dict:
        """
        Handle failed payment and create recovery sequence.

        Args:
            payment_event: Payment failure event from Stripe

        Returns:
            Dictionary with recovery sequence
        """
        recovery_prompt = f"""Create a payment recovery email sequence for a failed payment.

Payment Details:
- Customer: {payment_event.get('customer_name', 'Customer')}
- Amount: ${payment_event.get('amount', '0')}
- Plan: {payment_event.get('plan', 'Pro')}
- Last Attempt: {payment_event.get('failed_at', 'Unknown')}
- Failure Reason: {payment_event.get('reason', 'Declined')}

Create a 3-email recovery sequence sent over 7 days:
1. Day 1: Payment failed notification + easy retry link
2. Day 4: Friendly reminder + offer to help with payment issues
3. Day 7: Last attempt before suspension + flexible payment options

For each email, include: subject, preview text, body, and CTA

Format as JSON:
{{
    "sequence": "failed_payment_recovery",
    "customer_id": "{payment_event.get('customer_id', 'unknown')}",
    "amount": {payment_event.get('amount', 0)},
    "emails": [
        {{
            "day": 1,
            "subject": "Your payment didn't go through",
            "preview_text": "Preview",
            "body": "Email HTML",
            "cta": "Retry Payment",
            "cta_link": "/retry-payment"
        }}
    ],
    "expected_recovery_rate": "X%"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": recovery_prompt}]
            )

            result = json.loads(response.content[0].text)
            result["initiated_at"] = datetime.now().isoformat()
            result["type"] = "payment_recovery"

            logger.info(f"Payment recovery sequence created for {payment_event.get('customer_id')}")
            self.transaction_log.append(result)
            return result
        except Exception as e:
            logger.error(f"Failed payment handling error: {e}")
            return {"error": str(e)}

    def handle_subscription_change(self, change_event: dict) -> dict:
        """
        Handle subscription upgrade or downgrade.

        Args:
            change_event: Subscription change event

        Returns:
            Dictionary with change details and confirmation email
        """
        change_type = change_event.get("type", "upgrade")  # upgrade, downgrade
        from_plan = change_event.get("from_plan", "Starter")
        to_plan = change_event.get("to_plan", "Pro")

        change_prompt = f"""Process a subscription {change_type} and generate confirmation email.

Subscription Change:
- Customer: {change_event.get('customer_name', 'Customer')}
- Change Type: {change_type}
- From Plan: {from_plan}
- To Plan: {to_plan}
- Effective Date: {change_event.get('effective_date', 'Immediately')}
- Proration: {change_event.get('proration_amount', 'N/A')}

Generate:
1. Billing Summary (old plan, new plan, price difference, proration)
2. Confirmation Email
3. Updated Invoice
4. Next Billing Date information

Format as JSON:
{{
    "change_id": "change_uuid",
    "customer_id": "{change_event.get('customer_id', 'unknown')}",
    "type": "{change_type}",
    "billing_summary": {{
        "old_plan": "{from_plan}",
        "new_plan": "{to_plan}",
        "old_price": 0.0,
        "new_price": 0.0,
        "price_change": 0.0,
        "proration": 0.0
    }},
    "confirmation_email": {{
        "subject": "Subscription {change_type.title()} Confirmation",
        "body": "Email content",
        "cta": "View Billing"
    }},
    "next_billing_date": "YYYY-MM-DD"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": change_prompt}]
            )

            result = json.loads(response.content[0].text)
            result["processed_at"] = datetime.now().isoformat()
            result["type"] = f"subscription_{change_type}"

            logger.info(f"Subscription change processed: {change_type} from {from_plan} to {to_plan}")
            self.transaction_log.append(result)
            return result
        except Exception as e:
            logger.error(f"Subscription change error: {e}")
            return {"error": str(e)}

    def send_usage_limit_warning(self, customer: dict) -> dict:
        """
        Send usage limit warning emails at 80%, 95%, and 100%.

        Args:
            customer: Customer dictionary with usage info

        Returns:
            Dictionary with warning email details
        """
        usage_percent = customer.get("usage_percent", 100)

        if usage_percent >= 100:
            subject_template = "You've hit your usage limit"
            urgency = "critical"
        elif usage_percent >= 95:
            subject_template = "You're at 95% of your usage limit"
            urgency = "high"
        else:
            subject_template = "You're at 80% of your usage limit"
            urgency = "medium"

        warning_prompt = f"""Generate a usage limit warning email.

Customer: {customer.get('name', 'Customer')}
Plan: {customer.get('plan', 'Pro')}
Usage: {usage_percent}% of {customer.get('monthly_limit', '500k')} tokens
Days Left in Billing: {customer.get('days_in_billing', '15')}

Urgency: {urgency}

Create an email that:
1. Alerts them to their current usage level
2. Shows usage breakdown by product feature
3. Explains what happens at 100% (service pause if applicable)
4. Offers upgrade or purchase options
5. Includes helpful tips for reducing usage

Format as JSON:
{{
    "warning_level": "{usage_percent}%",
    "subject": "{subject_template}",
    "preview_text": "Preview",
    "body": "Email content",
    "urgency": "{urgency}",
    "cta": "Upgrade Plan|Purchase Additional Tokens",
    "cta_link": "/billing/upgrade"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": warning_prompt}]
            )

            result = json.loads(response.content[0].text)
            result["customer_id"] = customer.get("id")
            result["sent_at"] = datetime.now().isoformat()
            result["type"] = "usage_limit_warning"

            logger.info(f"Usage warning sent to {customer.get('name')} at {usage_percent}% usage")
            return result
        except Exception as e:
            logger.error(f"Usage limit warning error: {e}")
            return {"error": str(e)}

    def generate_invoice(self, invoice_data: dict) -> dict:
        """
        Generate and format an invoice.

        Args:
            invoice_data: Dictionary with invoice details

        Returns:
            Dictionary with invoice content
        """
        invoice_prompt = f"""Generate a professional invoice.

Invoice Data:
{json.dumps(invoice_data, indent=2)}

Create:
1. Invoice HTML (professional formatting)
2. Invoice text for email
3. Summary for accounting

Include:
- Invoice number and date
- Customer details
- Itemized charges (subscription, add-ons, adjustments)
- Subtotal, tax, total
- Payment terms
- Due date
- PDF-ready HTML

Format as JSON:
{{
    "invoice_number": "INV-2026-001",
    "invoice_date": "2026-03-23",
    "due_date": "2026-04-06",
    "customer_id": "cust_123",
    "customer_name": "Company Name",
    "amount": 0.0,
    "currency": "USD",
    "html_content": "<html>Invoice HTML</html>",
    "text_summary": "Text version",
    "line_items": [
        {{"description": "Pro Plan", "amount": 0.0}}
    ],
    "subtotal": 0.0,
    "tax": 0.0,
    "total": 0.0
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": invoice_prompt}]
            )

            result = json.loads(response.content[0].text)
            result["type"] = "invoice"
            result["generated_at"] = datetime.now().isoformat()

            logger.info(f"Invoice generated: {result.get('invoice_number', 'N/A')}")
            return result
        except Exception as e:
            logger.error(f"Invoice generation error: {e}")
            return {"error": str(e)}

    def handle_refund_request(self, refund_request: dict) -> dict:
        """
        Handle refund requests with auto-approval for < $50.

        Args:
            refund_request: Refund request dictionary

        Returns:
            Dictionary with refund decision and details
        """
        amount = refund_request.get("amount", 0)

        # Auto-approve small refunds
        if amount < self.REFUND_AUTO_APPROVE_THRESHOLD:
            auto_approve = True
            reason = "Auto-approved (under threshold)"
        else:
            auto_approve = False
            reason = "Flagged for manual review (over threshold)"

        refund_prompt = f"""Analyze and provide recommendation for a refund request.

Refund Request:
- Customer: {refund_request.get('customer_name', 'Customer')}
- Amount: ${amount}
- Reason: {refund_request.get('reason', 'Not specified')}
- Invoice Date: {refund_request.get('invoice_date', 'Unknown')}
- Days Since Purchase: {refund_request.get('days_since_purchase', '0')}
- Customer History: {refund_request.get('customer_history', 'New customer')}

Auto-Approve: {auto_approve}
Initial Reason: {reason}

Analyze:
1. Legitimacy of refund request
2. Customer value and history
3. Refund recommendation
4. Response email template

Format as JSON:
{{
    "refund_id": "refund_uuid",
    "customer_id": "{refund_request.get('customer_id', 'unknown')}",
    "amount": {amount},
    "status": "approved|pending_review|denied",
    "reason": "Explanation",
    "recommendation": "Auto-approved|Recommend approval|Recommend denial",
    "response_email": {{
        "subject": "Refund Status",
        "body": "Email content",
        "tone": "apologetic|neutral|firm"
    }},
    "processed_at": "YYYY-MM-DD"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": refund_prompt}]
            )

            result = json.loads(response.content[0].text)
            result["type"] = "refund_request"
            result["received_at"] = datetime.now().isoformat()

            if auto_approve:
                result["status"] = "approved"
                logger.info(f"Refund auto-approved: ${amount}")
            else:
                self.pending_refunds.append(result)
                logger.info(f"Refund flagged for review: ${amount}")

            return result
        except Exception as e:
            logger.error(f"Refund handling error: {e}")
            return {"error": str(e)}

    def reconcile_monthly_revenue(self, transactions: List[dict]) -> dict:
        """
        Reconcile monthly revenue and generate financial report.

        Args:
            transactions: List of monthly transactions

        Returns:
            Dictionary with reconciliation results
        """
        reconciliation_prompt = f"""Reconcile monthly revenue and provide financial summary.

Transactions (sample):
{json.dumps(transactions[:10], indent=2)}
Total transactions: {len(transactions)}

Calculate and analyze:
1. Total Revenue (subscriptions + add-ons)
2. Total Refunds
3. Net Revenue
4. Revenue by Plan (Starter, Pro, Agency breakdown)
5. Average Revenue Per User (ARPU)
6. MRR reconciliation
7. Discrepancies or anomalies

Format as JSON:
{{
    "period": "2026-03",
    "total_transactions": 0,
    "revenue": {{
        "gross": 0.0,
        "refunds": 0.0,
        "net": 0.0
    }},
    "by_plan": {{
        "starter": 0.0,
        "pro": 0.0,
        "agency": 0.0
    }},
    "metrics": {{
        "arpu": 0.0,
        "mrr": 0.0,
        "transaction_count": 0,
        "refund_rate": "0%"
    }},
    "reconciliation": {{
        "status": "balanced|discrepancy_found",
        "difference": 0.0,
        "notes": "Any issues identified"
    }}
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": reconciliation_prompt}]
            )

            result = json.loads(response.content[0].text)
            result["type"] = "revenue_reconciliation"
            result["reconciled_at"] = datetime.now().isoformat()

            logger.info(f"Monthly revenue reconciled: ${result.get('revenue', {}).get('net', 0)}")
            return result
        except Exception as e:
            logger.error(f"Revenue reconciliation error: {e}")
            return {"error": str(e)}

    def run(self, action: str, **kwargs) -> dict:
        """
        Run the billing agent with specific actions.

        Args:
            action: Action to perform
            **kwargs: Additional parameters

        Returns:
            Dictionary with action results
        """
        logger.info(f"Running billing agent - action: {action}")

        if action == "handle_failed_payment":
            return self.handle_failed_payment(kwargs.get("payment_event", {}))
        elif action == "subscription_change":
            return self.handle_subscription_change(kwargs.get("change_event", {}))
        elif action == "usage_warning":
            return self.send_usage_limit_warning(kwargs.get("customer", {}))
        elif action == "generate_invoice":
            return self.generate_invoice(kwargs.get("invoice_data", {}))
        elif action == "handle_refund":
            return self.handle_refund_request(kwargs.get("refund_request", {}))
        elif action == "reconcile_revenue":
            return self.reconcile_monthly_revenue(kwargs.get("transactions", []))
        else:
            logger.warning(f"Unknown action: {action}")
            return {"error": f"Unknown action: {action}"}


if __name__ == "__main__":
    # Example usage
    agent = BillingAgent()

    print("=== Billing Agent Demo ===\n")

    # Test failed payment
    payment_event = {
        "customer_id": "cust_123",
        "customer_name": "Acme Corp",
        "amount": 299,
        "plan": "Pro",
        "reason": "Card declined",
        "failed_at": datetime.now().isoformat()
    }
    recovery = agent.handle_failed_payment(payment_event)
    print(f"Recovery Sequence: {recovery.get('sequence', 'N/A')}\n")

    # Test subscription upgrade
    change_event = {
        "customer_id": "cust_456",
        "customer_name": "TechCorp Inc",
        "type": "upgrade",
        "from_plan": "Starter",
        "to_plan": "Pro",
        "proration_amount": 50.00
    }
    upgrade = agent.handle_subscription_change(change_event)
    print(f"Subscription Change: {upgrade.get('type', 'N/A')}")
