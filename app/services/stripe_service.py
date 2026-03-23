"""
Stripe Payment Integration Service
Handles subscription management, payment processing, and webhooks
"""
import logging
import os
from typing import Optional, Dict, Any
import stripe
from sqlalchemy.orm import Session
from app.models.database import User, SubscriptionTierEnum

logger = logging.getLogger(__name__)

# Initialize Stripe with API key
stripe.api_key = os.getenv("STRIPE_API_KEY")


class StripeService:
    """Service for Stripe payment integration"""

    # Subscription pricing configuration
    TIER_CONFIG = {
        "starter": {
            "price": 29.00,
            "limit": 50,
            "stripe_price_id": os.getenv("STRIPE_STARTER_PRICE_ID", "price_starter_test"),
            "features": ["50 generations/month", "Basic support", "API access"]
        },
        "pro": {
            "price": 79.00,
            "limit": 200,
            "stripe_price_id": os.getenv("STRIPE_PRO_PRICE_ID", "price_pro_test"),
            "features": ["200 generations/month", "Priority support", "Advanced analytics", "API access"]
        },
        "agency": {
            "price": 199.00,
            "limit": 0,  # unlimited
            "stripe_price_id": os.getenv("STRIPE_AGENCY_PRICE_ID", "price_agency_test"),
            "features": ["Unlimited generations", "Dedicated support", "Advanced analytics", "Team management", "API access"]
        }
    }

    @staticmethod
    def create_customer(email: str, name: str) -> str:
        """
        Create a Stripe customer
        Returns: stripe_customer_id
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={
                    "service": "ContentPilot AI"
                }
            )
            logger.info(f"Stripe customer created: {customer.id} for {email}")
            return customer.id
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer: {str(e)}")
            raise

    @staticmethod
    def create_subscription(
        customer_id: str,
        tier: str,
        db: Session,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Create a Stripe subscription
        Returns: subscription details
        """
        if tier not in StripeService.TIER_CONFIG:
            raise ValueError(f"Invalid subscription tier: {tier}")

        try:
            price_id = StripeService.TIER_CONFIG[tier]["stripe_price_id"]

            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                payment_behavior="default_incomplete",
                expand=["latest_invoice.payment_intent"],
                metadata={
                    "user_id": user_id,
                    "tier": tier
                }
            )

            # Update user in database
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.stripe_subscription_id = subscription.id
                user.subscription_tier = SubscriptionTierEnum(tier)
                user.usage_limit = StripeService.TIER_CONFIG[tier]["limit"]
                user.usage_count = 0
                db.commit()

            logger.info(f"Subscription created: {subscription.id} for user {user_id} on tier {tier}")
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create subscription: {str(e)}")
            raise

    @staticmethod
    def handle_subscription_updated(subscription_id: str, db: Session) -> bool:
        """Handle subscription.updated webhook"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)

            if subscription.status == "active":
                # Get user by stripe subscription ID
                user = db.query(User).filter(
                    User.stripe_subscription_id == subscription_id
                ).first()

                if user and subscription.metadata.get("tier"):
                    tier = subscription.metadata["tier"]
                    user.subscription_tier = SubscriptionTierEnum(tier)
                    user.usage_limit = StripeService.TIER_CONFIG[tier]["limit"]
                    db.commit()
                    logger.info(f"Subscription updated for user {user.id}")
                    return True
        except stripe.error.StripeError as e:
            logger.error(f"Failed to handle subscription update: {str(e)}")
        return False

    @staticmethod
    def handle_subscription_deleted(subscription_id: str, db: Session) -> bool:
        """Handle subscription.deleted webhook - downgrade to free tier"""
        try:
            user = db.query(User).filter(
                User.stripe_subscription_id == subscription_id
            ).first()

            if user:
                user.subscription_tier = SubscriptionTierEnum.FREE
                user.usage_limit = 0
                user.stripe_subscription_id = None
                db.commit()
                logger.info(f"User {user.id} downgraded to free tier")
                return True
        except Exception as e:
            logger.error(f"Failed to handle subscription deletion: {str(e)}")
        return False

    @staticmethod
    def handle_payment_intent_failed(payment_intent_id: str, db: Session) -> bool:
        """Handle payment failure - notify user, suspend service if needed"""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            # Find subscription by payment intent
            subscriptions = stripe.Subscription.list(limit=1)

            logger.warning(f"Payment failed for intent {payment_intent_id}")
            # In production, send email notification to user
            return True
        except stripe.error.StripeError as e:
            logger.error(f"Failed to handle payment failure: {str(e)}")
        return False

    @staticmethod
    def check_usage_limit(user: User) -> bool:
        """
        Check if user has exceeded usage limit
        Returns: True if user can generate content, False otherwise
        """
        if user.subscription_tier == SubscriptionTierEnum.AGENCY:
            return True  # Unlimited

        if user.usage_limit == 0:
            return False  # Free tier or no limit set

        return user.usage_count < user.usage_limit

    @staticmethod
    def get_usage_stats(user: User) -> Dict[str, Any]:
        """Get user's usage statistics"""
        tier_config = StripeService.TIER_CONFIG.get(user.subscription_tier.value, {})

        return {
            "tier": user.subscription_tier.value,
            "usage_count": user.usage_count,
            "usage_limit": user.usage_limit or tier_config.get("limit", 0),
            "remaining": max(0, (user.usage_limit or tier_config.get("limit", 0)) - user.usage_count),
            "is_unlimited": user.subscription_tier == SubscriptionTierEnum.AGENCY
        }

    @staticmethod
    def get_tier_info(tier: str) -> Optional[Dict[str, Any]]:
        """Get tier configuration information"""
        return StripeService.TIER_CONFIG.get(tier)

    @staticmethod
    def get_all_tiers() -> Dict[str, Dict[str, Any]]:
        """Get all tier configurations"""
        return StripeService.TIER_CONFIG

    @staticmethod
    def validate_webhook_signature(payload: bytes, sig_header: str) -> bool:
        """
        Validate Stripe webhook signature
        Returns: True if signature is valid
        """
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        try:
            stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
            return True
        except ValueError:
            logger.error("Invalid webhook payload")
            return False
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid webhook signature")
            return False
