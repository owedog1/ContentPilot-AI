"""
Sales AI Agent
Monitors signups, manages email sequences, and drives conversions.
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


class SalesAgent:
    """
    Autonomous sales agent that:
    - Monitors new signups
    - Sends personalized welcome emails
    - Manages trial-to-paid conversion sequences
    - Identifies and re-engages at-risk customers
    - Manages upsell sequences
    - Runs win-back campaigns
    - Tracks conversion metrics
    """

    def __init__(self, config: Optional[dict] = None):
        """
        Initialize the Sales Agent.

        Args:
            config: Configuration dictionary with API keys and settings
        """
        self.config = config or {}
        self.client = anthropic.Anthropic(
            api_key=self.config.get("anthropic_api_key", "")
        )
        self.model = "claude-3-5-sonnet-20241022"
        self.sequence_history = []
        self.conversion_metrics = {}
        logger.info("Sales Agent initialized")

    def generate_welcome_email(self, user_profile: dict) -> dict:
        """
        Generate a personalized welcome email for new signup.

        Args:
            user_profile: Dictionary with user info (name, company, signup_date)

        Returns:
            Dictionary with welcome email content
        """
        welcome_prompt = f"""Create a personalized welcome email for a new user.

User Profile:
- Name: {user_profile.get('name', 'User')}
- Company: {user_profile.get('company', 'Unknown')}
- Industry: {user_profile.get('industry', 'General')}
- Sign-up Date: {user_profile.get('signup_date', 'Today')}

Create a warm, engaging welcome email that:
1. Thanks them for signing up
2. Highlights key features they'll want to explore
3. Suggests first steps
4. Includes a CTA to explore the product

Format as JSON:
{{
    "subject": "Email subject line",
    "preview_text": "Preview text",
    "body": "Email HTML content",
    "cta_button": "Button text",
    "cta_link": "/get-started"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": welcome_prompt}]
            )

            result = json.loads(response.content[0].text)
            result["type"] = "welcome"
            result["user_id"] = user_profile.get("id")
            result["sent_at"] = datetime.now().isoformat()

            logger.info(f"Welcome email generated for {user_profile.get('name', 'user')}")
            return result
        except Exception as e:
            logger.error(f"Welcome email generation error: {e}")
            return {"error": str(e)}

    def create_trial_conversion_sequence(self, user_profile: dict, trial_days: int = 14) -> dict:
        """
        Create a trial-to-paid conversion email sequence.

        Args:
            user_profile: Dictionary with user info
            trial_days: Number of trial days (default 14)

        Returns:
            Dictionary with email sequence
        """
        sequence_prompt = f"""Create a trial-to-paid conversion email sequence.

User: {user_profile.get('name', 'User')}
Company: {user_profile.get('company', 'Company')}
Trial Duration: {trial_days} days
Plan Recommended: Pro Plan ($299/month)

Create a 4-email sequence:
1. Day 1: Welcome & quick-start guide
2. Day 3-5: Feature showcase email (timely benefit)
3. Day 7: "Aha moment" email (case study or success story)
4. Day 10-12: Limited-time offer (20% off first month, expires in 48 hours)

For each email provide: subject, preview, body, CTA

Format as JSON:
{{
    "sequence_name": "Trial Conversion Sequence",
    "emails": [
        {{
            "day": 1,
            "subject": "Welcome to your ContentPilot AI trial",
            "preview_text": "Preview",
            "body": "Email content",
            "cta": "Get Started",
            "cta_link": "/app/dashboard"
        }}
    ],
    "expected_conversion_rate": "X%"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2500,
                messages=[{"role": "user", "content": sequence_prompt}]
            )

            result = json.loads(response.content[0].text)
            result["user_id"] = user_profile.get("id")
            result["start_date"] = datetime.now().isoformat()

            logger.info(f"Trial conversion sequence created for {user_profile.get('name')}")
            self.sequence_history.append(result)
            return result
        except Exception as e:
            logger.error(f"Conversion sequence creation error: {e}")
            return {"error": str(e)}

    def identify_at_risk_customers(self, customer_data: List[dict]) -> List[dict]:
        """
        Identify customers at risk of churn based on usage patterns.

        Args:
            customer_data: List of customer dictionaries with usage metrics

        Returns:
            List of at-risk customer profiles
        """
        risk_analysis_prompt = f"""Analyze these customers and identify at-risk profiles.

Customer Data:
{json.dumps(customer_data, indent=2)}

For each customer, determine risk level based on:
- Days since last login
- API call frequency trend
- Feature usage breadth
- Support ticket sentiment

Return JSON:
{{
    "at_risk_customers": [
        {{
            "customer_id": "id",
            "name": "name",
            "risk_level": "high|medium|low",
            "reason": "Primary reason for risk",
            "last_active": "date",
            "recommended_action": "Re-engagement strategy"
        }}
    ]
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": risk_analysis_prompt}]
            )

            result = json.loads(response.content[0].text)
            at_risk = result.get("at_risk_customers", [])
            logger.info(f"Identified {len(at_risk)} at-risk customers")
            return at_risk
        except Exception as e:
            logger.error(f"At-risk customer analysis error: {e}")
            return []

    def create_reengagement_email(self, customer_profile: dict) -> dict:
        """
        Create a re-engagement email for at-risk customers.

        Args:
            customer_profile: Dictionary with customer info and risk reason

        Returns:
            Dictionary with re-engagement email
        """
        reengagement_prompt = f"""Create a re-engagement email for an at-risk customer.

Customer: {customer_profile.get('name', 'User')}
Risk Reason: {customer_profile.get('reason', 'Low engagement')}
Last Active: {customer_profile.get('last_active', 'Unknown')}
Current Plan: {customer_profile.get('plan', 'Pro')}

Create an email that:
1. Acknowledges their absence warmly
2. Reminds them of key value they're missing
3. Offers to help resolve any issues
4. Provides a special incentive (discount, free consultation)

Format as JSON:
{{
    "subject": "Subject line",
    "preview_text": "Preview",
    "body": "Email HTML",
    "incentive": "20% discount on annual plan",
    "cta": "Let's talk",
    "cta_link": "/contact-sales"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": reengagement_prompt}]
            )

            result = json.loads(response.content[0].text)
            result["type"] = "reengagement"
            result["customer_id"] = customer_profile.get("id")

            logger.info(f"Re-engagement email created for {customer_profile.get('name')}")
            return result
        except Exception as e:
            logger.error(f"Re-engagement email error: {e}")
            return {"error": str(e)}

    def create_upsell_sequence(self, customer_profile: dict, current_plan: str) -> dict:
        """
        Create an upsell sequence (Starter→Pro, Pro→Agency).

        Args:
            customer_profile: Dictionary with customer info
            current_plan: Customer's current plan

        Returns:
            Dictionary with upsell sequence
        """
        upsell_prompt = f"""Create an upsell sequence for a {current_plan} customer.

Customer: {customer_profile.get('name', 'User')}
Company Size: {customer_profile.get('company_size', 'Small')}
Current Usage: {customer_profile.get('usage_percent', '60')}% of plan limit

Recommend upgrade to: {"Pro" if current_plan == "Starter" else "Agency"}
Benefits to highlight: More tokens, higher API limits, priority support, advanced features

Create a 2-email sequence:
1. Email 1: Gentle notification that they're using X% of their limit
2. Email 2: Showcase new features in higher tier, special upgrade discount

Format as JSON:
{{
    "sequence_name": "Upsell to {\"Pro\" if current_plan == \"Starter\" else \"Agency\"}",
    "emails": [
        {{
            "day": 1,
            "subject": "Subject",
            "body": "Content",
            "cta": "View upgrade options"
        }}
    ],
    "expected_value": "Additional MRR if successful"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": upsell_prompt}]
            )

            result = json.loads(response.content[0].text)
            result["customer_id"] = customer_profile.get("id")
            result["current_plan"] = current_plan

            logger.info(f"Upsell sequence created for {customer_profile.get('name')}")
            return result
        except Exception as e:
            logger.error(f"Upsell sequence error: {e}")
            return {"error": str(e)}

    def create_winback_campaign(self, churned_customer: dict) -> dict:
        """
        Create a win-back campaign for churned customers.

        Args:
            churned_customer: Dictionary with churned customer info

        Returns:
            Dictionary with win-back campaign
        """
        winback_prompt = f"""Create a win-back campaign for a churned customer.

Customer: {churned_customer.get('name', 'User')}
Churn Date: {churned_customer.get('churn_date', 'Recently')}
Reason for Churn: {churned_customer.get('churn_reason', 'Unknown')}
Previous Plan: {churned_customer.get('previous_plan', 'Pro')}

Create a 3-email win-back sequence:
1. Email 1 (Day 1): "We miss you" - personal touch, ask for feedback
2. Email 2 (Day 5): Address their churn reason, show improvements made
3. Email 3 (Day 10): Special win-back offer (30% off annual, 3-month free trial, etc.)

Format as JSON:
{{
    "campaign_name": "Win-back Campaign",
    "emails": [
        {{
            "day": 1,
            "subject": "We miss you",
            "body": "Email content",
            "tone": "Empathetic"
        }}
    ],
    "offer": "30% off first year",
    "success_metric": "Expected reactivation rate %"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": winback_prompt}]
            )

            result = json.loads(response.content[0].text)
            result["customer_id"] = churned_customer.get("id")
            result["type"] = "winback"

            logger.info(f"Win-back campaign created for {churned_customer.get('name')}")
            return result
        except Exception as e:
            logger.error(f"Win-back campaign error: {e}")
            return {"error": str(e)}

    def track_conversion_metrics(self, sequence_id: str, metrics: dict) -> None:
        """
        Track metrics for email sequences.

        Args:
            sequence_id: Identifier for the sequence
            metrics: Dictionary with conversion metrics (open_rate, click_rate, conversion_rate, etc.)
        """
        self.conversion_metrics[sequence_id] = {
            "tracked_at": datetime.now().isoformat(),
            "metrics": metrics
        }
        logger.info(f"Metrics tracked for {sequence_id}: {metrics}")

    def run(self, action: str, **kwargs) -> dict:
        """
        Run the sales agent with specific actions.

        Args:
            action: Action to perform ('welcome', 'trial_sequence', 'identify_atrisk', 'upsell', 'winback')
            **kwargs: Additional parameters for the action

        Returns:
            Dictionary with action results
        """
        logger.info(f"Running sales agent - action: {action}")

        if action == "welcome":
            return self.generate_welcome_email(kwargs.get("user_profile", {}))
        elif action == "trial_sequence":
            return self.create_trial_conversion_sequence(kwargs.get("user_profile", {}))
        elif action == "identify_atrisk":
            return {"at_risk_customers": self.identify_at_risk_customers(kwargs.get("customer_data", []))}
        elif action == "upsell":
            return self.create_upsell_sequence(kwargs.get("customer_profile", {}), kwargs.get("current_plan", "Starter"))
        elif action == "winback":
            return self.create_winback_campaign(kwargs.get("churned_customer", {}))
        else:
            logger.warning(f"Unknown action: {action}")
            return {"error": f"Unknown action: {action}"}


if __name__ == "__main__":
    # Example usage
    agent = SalesAgent()

    print("=== Sales Agent Demo ===\n")

    # Generate welcome email
    user = {
        "id": "user_123",
        "name": "Jane Doe",
        "company": "TechCorp",
        "industry": "SaaS",
        "signup_date": datetime.now().isoformat()
    }
    welcome = agent.generate_welcome_email(user)
    print(f"Welcome Email Subject: {welcome.get('subject', 'N/A')}\n")

    # Create trial conversion sequence
    sequence = agent.create_trial_conversion_sequence(user)
    print(f"Trial Conversion Sequence: {sequence.get('sequence_name', 'N/A')}")
    print(f"Number of emails: {len(sequence.get('emails', []))}\n")

    # Create upsell sequence
    customer = {
        "id": "cust_456",
        "name": "John Smith",
        "company": "DataCorp",
        "company_size": "50-100",
        "usage_percent": 85
    }
    upsell = agent.create_upsell_sequence(customer, "Starter")
    print(f"Upsell Campaign: {upsell.get('sequence_name', 'N/A')}")
