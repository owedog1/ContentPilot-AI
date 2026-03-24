"""
Master Orchestrator Agent
Coordinates all other agents, manages scheduling, and provides unified logging.
"""

import logging
import json
import sys
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import anthropic

# Import all agents
from .support_agent import SupportAgent
from .marketing_agent import MarketingAgent
from .sales_agent import SalesAgent
from .analytics_agent import AnalyticsAgent
from .billing_agent import BillingAgent

# Configure logging
logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Master orchestrator that:
    - Coordinates all other agents
    - Manages scheduling and execution
    - Provides unified logging and monitoring
    - Handles inter-agent communication
    - Performs health checks
    - Can be run via: python -m app.agents.orchestrator
    """

    def __init__(self, config: Optional[dict] = None):
        """
        Initialize the Orchestrator.

        Args:
            config: Configuration dictionary with API keys and settings
        """
        self.config = config or self._load_config()
        self.client = anthropic.Anthropic(
            api_key=self.config.get("anthropic_api_key", "")
        )
        self.model = "claude-3-5-sonnet-20241022"

        # Initialize all agents
        self.agents = {
            "support": SupportAgent(self.config),
            "marketing": MarketingAgent(self.config),
            "sales": SalesAgent(self.config),
            "analytics": AnalyticsAgent(self.config),
            "billing": BillingAgent(self.config)
        }

        self.execution_log = []
        self.health_status = {}
        self.last_run = {}

        logger.info("Orchestrator initialized with all agents")

    def _load_config(self) -> dict:
        """
        Load configuration from environment or config file.

        Returns:
            Configuration dictionary
        """
        config = {
            "anthropic_api_key": "",
            "sendgrid_api_key": "",
            "twitter_api_key": "",
            "linkedin_api_key": "",
            "stripe_api_key": ""
        }
        # In production, load from environment variables or config file
        logger.info("Configuration loaded")
        return config

    def check_agent_health(self) -> Dict[str, bool]:
        """
        Perform health checks on all agents.

        Returns:
            Dictionary with health status for each agent
        """
        logger.info("Performing health checks on all agents...")

        for agent_name, agent in self.agents.items():
            try:
                # Perform a simple test to verify agent is functional
                health_check_prompt = "Respond with 'healthy' if you can understand this message."
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=10,
                    messages=[{"role": "user", "content": health_check_prompt}]
                )

                self.health_status[agent_name] = True
                logger.info(f"✓ {agent_name.upper()} agent is healthy")
            except Exception as e:
                self.health_status[agent_name] = False
                logger.error(f"✗ {agent_name.upper()} agent health check failed: {e}")

        return self.health_status

    def run_support_workflow(self, tickets: List[dict]) -> dict:
        """
        Run the support agent workflow.

        Args:
            tickets: List of support tickets

        Returns:
            Dictionary with support workflow results
        """
        logger.info(f"Starting support workflow with {len(tickets)} tickets")

        try:
            results = self.agents["support"].run(tickets)

            execution_record = {
                "agent": "support",
                "action": "process_tickets",
                "timestamp": datetime.now().isoformat(),
                "tickets_processed": len(results),
                "status": "completed"
            }
            self.execution_log.append(execution_record)
            self.last_run["support"] = datetime.now().isoformat()

            logger.info(f"Support workflow completed: {len(results)} tickets processed")
            return {"agent": "support", "results": results}
        except Exception as e:
            logger.error(f"Support workflow error: {e}")
            return {"agent": "support", "error": str(e)}

    def run_marketing_workflow(self) -> dict:
        """
        Run the marketing agent workflow.

        Returns:
            Dictionary with marketing workflow results
        """
        logger.info("Starting marketing workflow")

        try:
            content_plan = {
                "blog_topics": [
                    {"topic": "Latest AI Trends in 2026", "keywords": ["AI", "trends", "2026"]},
                    {"topic": "Automation ROI Guide", "keywords": ["automation", "ROI", "cost-benefit"]},
                ],
                "social_topics": [
                    "Tips for Automating Your Workflow",
                    "Customer Success Story: 10x Productivity"
                ],
                "campaigns": [
                    {"type": "welcome", "segment": "new_users"},
                    {"type": "tips_newsletter", "segment": "active_users"}
                ]
            }

            results = self.agents["marketing"].run(content_plan)

            execution_record = {
                "agent": "marketing",
                "action": "generate_content",
                "timestamp": datetime.now().isoformat(),
                "content_pieces": (
                    len(results.get("blog_posts", [])) +
                    len(results.get("social_posts", [])) +
                    len(results.get("campaigns", []))
                ),
                "status": "completed"
            }
            self.execution_log.append(execution_record)
            self.last_run["marketing"] = datetime.now().isoformat()

            logger.info("Marketing workflow completed")
            return {"agent": "marketing", "results": results}
        except Exception as e:
            logger.error(f"Marketing workflow error: {e}")
            return {"agent": "marketing", "error": str(e)}

    def run_sales_workflow(self, signups: List[dict], at_risk_customers: List[dict]) -> dict:
        """
        Run the sales agent workflow.

        Args:
            signups: List of new signups
            at_risk_customers: List of at-risk customers

        Returns:
            Dictionary with sales workflow results
        """
        logger.info("Starting sales workflow")

        try:
            results = {
                "welcome_emails": [],
                "trial_sequences": [],
                "reengagement_emails": [],
                "upsell_campaigns": []
            }

            # Process new signups
            for signup in signups:
                welcome = self.agents["sales"].generate_welcome_email(signup)
                results["welcome_emails"].append(welcome)

                trial_seq = self.agents["sales"].create_trial_conversion_sequence(signup)
                results["trial_sequences"].append(trial_seq)

            # Process at-risk customers
            for customer in at_risk_customers:
                reengagement = self.agents["sales"].create_reengagement_email(customer)
                results["reengagement_emails"].append(reengagement)

            execution_record = {
                "agent": "sales",
                "action": "manage_sequences",
                "timestamp": datetime.now().isoformat(),
                "signups_processed": len(signups),
                "atrisk_processed": len(at_risk_customers),
                "status": "completed"
            }
            self.execution_log.append(execution_record)
            self.last_run["sales"] = datetime.now().isoformat()

            logger.info("Sales workflow completed")
            return {"agent": "sales", "results": results}
        except Exception as e:
            logger.error(f"Sales workflow error: {e}")
            return {"agent": "sales", "error": str(e)}

    def run_analytics_workflow(self, business_data: dict) -> dict:
        """
        Run the analytics agent workflow.

        Args:
            business_data: Dictionary with business metrics

        Returns:
            Dictionary with analytics workflow results
        """
        logger.info("Starting analytics workflow")

        try:
            results = self.agents["analytics"].run("weekly", business_data)

            execution_record = {
                "agent": "analytics",
                "action": "generate_reports",
                "timestamp": datetime.now().isoformat(),
                "report_type": "weekly",
                "status": "completed"
            }
            self.execution_log.append(execution_record)
            self.last_run["analytics"] = datetime.now().isoformat()

            logger.info("Analytics workflow completed")
            return {"agent": "analytics", "results": results}
        except Exception as e:
            logger.error(f"Analytics workflow error: {e}")
            return {"agent": "analytics", "error": str(e)}

    def run_billing_workflow(self, events: List[dict]) -> dict:
        """
        Run the billing agent workflow.

        Args:
            events: List of billing events (failed payments, refunds, etc.)

        Returns:
            Dictionary with billing workflow results
        """
        logger.info("Starting billing workflow")

        try:
            results = {
                "payment_recovery": [],
                "subscription_changes": [],
                "usage_warnings": [],
                "invoices": [],
                "refunds": []
            }

            for event in events:
                event_type = event.get("type", "unknown")

                if event_type == "failed_payment":
                    recovery = self.agents["billing"].handle_failed_payment(event)
                    results["payment_recovery"].append(recovery)
                elif event_type == "subscription_change":
                    change = self.agents["billing"].handle_subscription_change(event)
                    results["subscription_changes"].append(change)
                elif event_type == "usage_warning":
                    warning = self.agents["billing"].send_usage_limit_warning(event.get("customer", {}))
                    results["usage_warnings"].append(warning)
                elif event_type == "refund":
                    refund = self.agents["billing"].handle_refund_request(event)
                    results["refunds"].append(refund)

            execution_record = {
                "agent": "billing",
                "action": "process_events",
                "timestamp": datetime.now().isoformat(),
                "events_processed": len(events),
                "status": "completed"
            }
            self.execution_log.append(execution_record)
            self.last_run["billing"] = datetime.now().isoformat()

            logger.info("Billing workflow completed")
            return {"agent": "billing", "results": results}
        except Exception as e:
            logger.error(f"Billing workflow error: {e}")
            return {"agent": "billing", "error": str(e)}

    def get_execution_summary(self) -> dict:
        """
        Get a summary of execution history.

        Returns:
            Dictionary with execution summary
        """
        summary = {
            "total_executions": len(self.execution_log),
            "agents_status": self.health_status,
            "last_runs": self.last_run,
            "recent_activity": self.execution_log[-10:] if self.execution_log else []
        }
        return summary

    def run_all_workflows(self, business_state: dict) -> dict:
        """
        Run all workflows in coordination.

        Args:
            business_state: Dictionary with current business state and data

        Returns:
            Dictionary with all workflow results
        """
        logger.info("="*60)
        logger.info("ORCHESTRATOR: Starting coordinated AI workforce execution")
        logger.info("="*60)

        # Check health first
        health = self.check_agent_health()
        if not all(health.values()):
            logger.warning("Some agents are unhealthy, proceeding with caution")

        results = {
            "timestamp": datetime.now().isoformat(),
            "health_status": health,
            "workflows": {}
        }

        # Run all workflows in logical order
        try:
            # 1. Support workflow
            if "support_tickets" in business_state:
                results["workflows"]["support"] = self.run_support_workflow(
                    business_state["support_tickets"]
                )

            # 2. Billing workflow
            if "billing_events" in business_state:
                results["workflows"]["billing"] = self.run_billing_workflow(
                    business_state["billing_events"]
                )

            # 3. Sales workflow
            if "signups" in business_state or "at_risk_customers" in business_state:
                results["workflows"]["sales"] = self.run_sales_workflow(
                    business_state.get("signups", []),
                    business_state.get("at_risk_customers", [])
                )

            # 4. Marketing workflow
            results["workflows"]["marketing"] = self.run_marketing_workflow()

            # 5. Analytics workflow (runs last, uses data from other agents)
            if "business_data" in business_state:
                results["workflows"]["analytics"] = self.run_analytics_workflow(
                    business_state["business_data"]
                )

            # Log execution summary
            summary = self.get_execution_summary()
            logger.info("="*60)
            logger.info(f"Orchestrator Execution Summary:")
            logger.info(f"Total Executions: {summary['total_executions']}")
            logger.info(f"Health Status: {summary['agents_status']}")
            logger.info("="*60)

            return results
        except Exception as e:
            logger.error(f"Orchestrator execution error: {e}")
            results["error"] = str(e)
            return results


def main():
    """
    Main entry point for orchestrator execution.
    """
    logger.info("ContentPilot AI Orchestrator Started")

    # Initialize orchestrator
    orchestrator = Orchestrator()

    # Sample business state (in production, this would come from database/API)
    business_state = {
        "support_tickets": [
            {
                "id": "TICKET_001",
                "text": "What's the pricing for the Pro plan?"
            }
        ],
        "billing_events": [
            {
                "type": "failed_payment",
                "customer_id": "cust_123",
                "customer_name": "Acme Corp",
                "amount": 299,
                "plan": "Pro"
            }
        ],
        "signups": [
            {
                "id": "user_new_001",
                "name": "Sarah Johnson",
                "company": "StartupXYZ",
                "industry": "SaaS"
            }
        ],
        "at_risk_customers": [
            {
                "id": "cust_456",
                "name": "John Smith",
                "reason": "Low API usage"
            }
        ],
        "business_data": {
            "business_data": {
                "mrr": 50000,
                "total_customers": 500,
                "new_customers_this_month": 45
            },
            "weekly_data": {
                "new_customers": 45,
                "churned_customers": 8
            },
            "api_usage": {
                "daily_cost": 50.00,
                "daily_api_calls": 500000
            }
        }
    }

    # Run all workflows
    results = orchestrator.run_all_workflows(business_state)

    # Output results
    print("\n" + "="*60)
    print("EXECUTION RESULTS")
    print("="*60)
    print(json.dumps(results, indent=2, default=str))

    logger.info("ContentPilot AI Orchestrator Execution Complete")


if __name__ == "__main__":
    main()
