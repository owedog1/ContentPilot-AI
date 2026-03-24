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
def _init_stripe():
    key = os.getenv("STRIPE_API_KEY", "")
    if key:
        stripe.api_key = key
    return key

_init_stripe()


class StripeService:
    """Service for Stripe payment integration"""

    # Subscription pricing configuration
    TIER_CONFIG = {
        "starter": {
            "price": 29.00,
            "limit": 50,
            "features": ["50 generations/month", "Basic support", "API access"]
        },
        "pro": {
            "price": 79.00,
            "limit": 200,
            "features": ["200 generations/month", "Priority support", "Advanced analytics", "API access"]
        },
        "agency": {
            "price": 199.00,
            "limit": 0,  # unlimited
            "features": ["Unlimited generations", "Dedicated support", "Advanced analytics", "Team management", "API access"]
        }
    }

    # Cache for Stripe price IDs (created on demand)
    _price_cache: Dict[str, str] = {}

    @staticmethod
    def _get_or_create_price(tier: str) -> str:
        """Get or create a Stripe Price for the given tier."""
        # Ensure API key is set
        if not stripe.api_key:
            stripe.api_key = os.getenv("STRIPE_API_KEY", "")

        if tier in StripeService._price_cache:
            return StripeService._price_cache[tier]

        config = StripeService.TIER_CONFIG[tier]

        # Search for existing product
        try:
            products = stripe.Product.list(limit=10)
            for product in products.data:
                if product.metadata.get("contentpilot_tier") == tier and product.active:
                    # Found existing product, get its price
                    prices = stripe.Price.list(product=product.id, active=True, limit=1)
                    if prices.data:
                        StripeService._price_cache[tier] = prices.data[0].id
                        return prices.data[0].id
        except Exception as e:
            logger.warning(f"Error searching for existing products: {e}")
            pass

        # Create new product and price
        try:
            product = stripe.Product.create(
                name=f"ContentPilot AI - {tier.title()} Plan",
                description=", ".join(config["features"]),
                metadata={"contentpilot_tier": tier}
            )

            price = stripe.Price.create(
                product=product.id,
                unit_amount=int(config["price"] * 100),  # cents
                currency="usd",
                recurring={"interval": "month"},
                metadata={"contentpilot_tier": tier}
            )

            StripeService._price_cache[tier] = price.id
            logger.info(f"Created Stripe product/price for tier {tier}: {price.id}")
            return price.id

        except Exception as e:
            logger.error(f"Failed to create Stripe product/price: {str(e)}")
            raise

    @staticmethod
    def create_checkout_session(
        customer_id: str,
        tier: str,
        user_id: int,
        success_url: str,
        cancel_url: str
    ) -> Dict[str, Any]:
        """
        Create a Stripe Checkout Session for subscription.
        Returns: checkout session URL and ID
        """
        if tier not in StripeService.TIER_CONFIG:
            raise ValueError(f"Invalid subscription tier: {tier}")

        # Ensure API key is set
        if not stripe.api_key:
            stripe.api_key = os.getenv("STRIPE_API_KEY", "")

        try:
            price_id = StripeService._get_or_create_price(tier)
            logger.info(f"Using price_id: {price_id} for tier: {tier}")

            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[{
                    "price": price_id,
                    "quantity": 1,
                }],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "user_id": str(user_id),
                    "tier": tier
                },
                subscription_data={
                    "metadata": {
                        "user_id": str(user_id),
                        "tier": tier
                    }
                }
            )

            logger.info(f"Checkout session created: {session.id} for user {user_id} tier {tier}")
            return {
                "checkout_url": session.url,
                "session_id": session.id
            }

        except Exception as e:
            logger.error(f"Failed to create checkout session: {type(e).__name__}: {str(e)}")
            raise

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
        except Exception as e:
            logger.error(f"Failed to create Stripe customer: {str(e)}")
            raise

    @staticmethod
    def handle_checkout_completed(session_id: str, db: Session) -> bool:
        """Handle checkout.session.completed webhook - activate subscription"""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            user_id = session.metadata.get("user_id")
            tier = session.metadata.get("tier")

            if user_id and tier:
                user = db.query(User).filter(User.id == int(user_id)).first()
                if user:
                    user.subscription_tier = SubscriptionTierEnum(tier)
                    user.usage_limit = StripeService.TIER_CONFIG[tier]["limit"]
                    user.stripe_subscription_id = session.subscription
                    user.stripe_customer_id = session.customer
                    user.usage_count = 0  # Reset on upgrade
                    db.commit()
                    logger.info(f"User {user_id} upgraded to {tier}")
                    return True
        except Exception as e:
            logger.error(f"Failed to handle checkout completed: {str(e)}")
        return False

    @staticmethod
    def handle_subscription_updated(subscription_id: str, db: Session) -> bool:
        """Handle subscription.updated webhook"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)

            if subscription.status == "active":
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
        except Exception as e:
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
                user.usage_limit = 50
                user.stripe_subscription_id = None
                db.commit()
                logger.info(f"User {user.id} downgraded to free tier")
                return True
        except Exception as e:
            logger.error(f"Failed to handle subscription deletion: {str(e)}")
        return False

    @staticmethod
    def check_usage_limit(user: User) -> bool:
        """
        Check if user has exceeded usage limit
        Returns: True if user can generate content, False otherwise
        """
        if user.subscription_tier == SubscriptionTierEnum.AGENCY:
            return True  # Unlimited

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
        if not webhook_secret:
            logger.warning("No STRIPE_WEBHOOK_SECRET set, skipping signature validation")
            return True  # Allow in dev mode
        try:
            stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
            return True
        except ValueError:
            logger.error("Invalid webhook payload")
            return False
        except Exception:
            logger.error("Invalid webhook signature")
            return False
