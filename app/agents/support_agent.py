"""
Customer Support AI Agent
Monitors and responds to support tickets with intelligent classification and escalation.
"""

import logging
import json
from datetime import datetime
from typing import Optional
import anthropic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SupportAgent:
    """
    Autonomous customer support agent that:
    - Monitors incoming support emails/tickets
    - Classifies tickets by type
    - Generates contextual responses
    - Escalates low-confidence issues
    - Auto-responds to common questions
    - Maintains FAQ knowledge base
    """

    # FAQ Knowledge Base
    FAQ_KNOWLEDGE_BASE = {
        "pricing": "ContentPilot AI pricing: Starter ($99/mo, 100k tokens/month), Pro ($299/mo, 500k tokens/month), Agency ($999/mo, unlimited tokens)",
        "billing": "Billing is monthly on the same date you signed up. You can change your plan anytime, and billing prorates.",
        "cancel_subscription": "Go to Settings > Billing > Manage Subscription and click 'Cancel Subscription'. Your access continues until the end of your billing period.",
        "api_keys": "Find API keys in Settings > API Keys. Keep them secret! Rotate them regularly for security.",
        "rate_limits": "Starter plan: 100 requests/min, Pro: 500 requests/min, Agency: unlimited",
        "data_retention": "We retain logs for 90 days. Custom retention available on Agency plan.",
        "gdpr_compliant": "Yes, ContentPilot AI is GDPR, CCPA, and SOC2 compliant.",
    }

    TICKET_CATEGORIES = ["billing", "technical", "feature_request", "bug_report", "general"]

    def __init__(self, config: Optional[dict] = None):
        """
        Initialize the Support Agent.

        Args:
            config: Configuration dictionary with API keys and settings
        """
        self.config = config or {}
        self.client = anthropic.Anthropic(
            api_key=self.config.get("anthropic_api_key", "")
        )
        self.interaction_log = []
        self.model = "claude-3-5-sonnet-20241022"
        logger.info("Support Agent initialized")

    def classify_ticket(self, ticket_text: str) -> dict:
        """
        Use Claude to classify incoming support tickets.

        Args:
            ticket_text: The support ticket text

        Returns:
            Dictionary with classification results
        """
        classification_prompt = f"""Analyze this support ticket and classify it. Respond ONLY with valid JSON.

Ticket:
{ticket_text}

Categories: {', '.join(self.TICKET_CATEGORIES)}

Return JSON:
{{
    "category": "one of {self.TICKET_CATEGORIES}",
    "confidence": 0.0-1.0,
    "urgency": "low|medium|high|critical",
    "summary": "brief summary"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": classification_prompt}]
            )

            # Parse JSON response
            response_text = response.content[0].text
            classification = json.loads(response_text)
            logger.info(f"Ticket classified: {classification['category']} (confidence: {classification['confidence']})")
            return classification
        except Exception as e:
            logger.error(f"Classification error: {e}")
            return {
                "category": "general",
                "confidence": 0.0,
                "urgency": "medium",
                "summary": "Classification error"
            }

    def generate_response(self, ticket: dict) -> str:
        """
        Generate an AI response to the support ticket.

        Args:
            ticket: Dictionary containing ticket info

        Returns:
            Generated response text
        """
        # Check FAQ knowledge base first
        faq_context = self._check_faq(ticket.get("text", ""))

        response_prompt = f"""You are a helpful customer support agent for ContentPilot AI.

Customer Ticket:
{ticket.get('text', '')}

Category: {ticket.get('category', 'general')}
Urgency: {ticket.get('urgency', 'medium')}

Relevant FAQ Context:
{faq_context if faq_context else 'No direct FAQ match, provide general helpful response'}

Generate a professional, friendly, and helpful response. Keep it concise (under 300 words).
Be empathetic and solution-focused."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=800,
                messages=[{"role": "user", "content": response_prompt}]
            )

            generated_response = response.content[0].text
            logger.info("Support response generated successfully")
            return generated_response
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            return "Thank you for contacting us. A support team member will review your request shortly."

    def _check_faq(self, ticket_text: str) -> str:
        """
        Check if ticket matches any FAQ topics.

        Args:
            ticket_text: The ticket text

        Returns:
            Relevant FAQ content or empty string
        """
        ticket_lower = ticket_text.lower()
        matches = []

        for faq_key, faq_content in self.FAQ_KNOWLEDGE_BASE.items():
            if faq_key.replace("_", " ") in ticket_lower or faq_key in ticket_lower:
                matches.append(faq_content)

        return "\n".join(matches) if matches else ""

    def escalate_ticket(self, ticket: dict, classification: dict) -> bool:
        """
        Determine if ticket should be escalated to human review.

        Args:
            ticket: Ticket data
            classification: Classification results

        Returns:
            True if escalation needed
        """
        escalation_needed = (
            classification.get("confidence", 1.0) < 0.7 or
            classification.get("urgency") in ["high", "critical"] or
            ticket.get("escalated", False)
        )

        if escalation_needed:
            logger.warning(f"Ticket escalated: {ticket.get('id', 'unknown')} - Confidence: {classification.get('confidence')}")

        return escalation_needed

    def process_ticket(self, ticket: dict) -> dict:
        """
        Process a complete support ticket.

        Args:
            ticket: Support ticket dictionary with 'id' and 'text' keys

        Returns:
            Dictionary with processed results
        """
        logger.info(f"Processing ticket: {ticket.get('id', 'unknown')}")

        # Classify the ticket
        classification = self.classify_ticket(ticket.get("text", ""))

        # Generate response
        response = self.generate_response({**ticket, **classification})

        # Determine if escalation is needed
        needs_escalation = self.escalate_ticket(ticket, classification)

        result = {
            "ticket_id": ticket.get("id"),
            "classification": classification,
            "response": response,
            "needs_escalation": needs_escalation,
            "processed_at": datetime.now().isoformat(),
            "status": "escalated" if needs_escalation else "auto_responded"
        }

        # Log the interaction
        self.interaction_log.append(result)
        logger.info(f"Ticket processed: {result['status']}")

        return result

    def run(self, tickets: list) -> list:
        """
        Run the support agent on a batch of tickets.

        Args:
            tickets: List of ticket dictionaries

        Returns:
            List of processed results
        """
        logger.info(f"Running support agent on {len(tickets)} tickets")
        results = [self.process_ticket(ticket) for ticket in tickets]
        return results

    def get_statistics(self) -> dict:
        """
        Get support agent statistics.

        Returns:
            Dictionary with agent statistics
        """
        total = len(self.interaction_log)
        escalated = sum(1 for log in self.interaction_log if log.get("needs_escalation"))
        auto_responded = total - escalated

        return {
            "total_tickets_processed": total,
            "auto_responded": auto_responded,
            "escalated": escalated,
            "escalation_rate": escalated / total if total > 0 else 0.0
        }


if __name__ == "__main__":
    # Example usage
    agent = SupportAgent()

    test_tickets = [
        {
            "id": "TICKET_001",
            "text": "What is the pricing for ContentPilot AI? How many tokens do I get?"
        },
        {
            "id": "TICKET_002",
            "text": "I'm getting an error 500 when trying to call the API. It says 'Internal server error'. This is critical, my production is down!"
        },
        {
            "id": "TICKET_003",
            "text": "Can you add a feature to export reports as PDF?"
        }
    ]

    results = agent.run(test_tickets)

    print("\n=== Support Agent Results ===")
    for result in results:
        print(f"\nTicket: {result['ticket_id']}")
        print(f"Status: {result['status']}")
        print(f"Category: {result['classification']['category']}")
        print(f"Response: {result['response'][:200]}...")

    print(f"\nStatistics: {agent.get_statistics()}")
