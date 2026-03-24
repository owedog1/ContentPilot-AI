"""
Configuration module for ContentPilot AI agents.
Loads environment variables and provides configuration access.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration"""

    # Anthropic API
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

    # Email & Communication
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
    RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")

    # Social Media APIs
    TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "")
    TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "")
    LINKEDIN_API_KEY = os.getenv("LINKEDIN_API_KEY", "")

    # Payment Processing
    STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///contentpilot.db")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/orchestrator.log")

    # Agent Settings
    CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
    MAX_TOKENS = 2000

    # Business Settings
    TIMEZONE = "UTC"
    COMPANY_NAME = "ContentPilot"
    SUPPORT_EMAIL = "support@contentpilot.ai"

    # Refund Settings
    REFUND_AUTO_APPROVE_THRESHOLD = 50.0

    # Usage Limits
    STARTER_TOKENS_PER_MONTH = 100000
    PRO_TOKENS_PER_MONTH = 500000
    AGENCY_TOKENS_PER_MONTH = None  # Unlimited

    # Pricing (matches landing page and Stripe config)
    PRICING = {
        "starter": {
            "monthly": 29.0,
            "annual": 290.0,
            "generations_per_month": 50
        },
        "pro": {
            "monthly": 79.0,
            "annual": 790.0,
            "generations_per_month": 200
        },
        "agency": {
            "monthly": 199.0,
            "annual": 1990.0,
            "generations_per_month": None  # Unlimited
        }
    }


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = "INFO"


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    DATABASE_URL = "sqlite:///:memory:"
    LOG_LEVEL = "DEBUG"


def get_config(env: str = None) -> Config:
    """
    Get configuration based on environment.

    Args:
        env: Environment name (development, production, testing)

    Returns:
        Configuration object
    """
    if env is None:
        env = os.getenv("ENV", "development")

    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig()
