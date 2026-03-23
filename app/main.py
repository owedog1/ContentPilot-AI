"""
ContentPilot AI - FastAPI Application
AI-powered content generation SaaS platform
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
import os
from functools import lru_cache
import time
from collections import defaultdict

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from jose import JWTError, jwt
import stripe

from app.models import Base, User, Content, SupportTicket, SubscriptionTierEnum, ContentTypeEnum
from app.services.ai_service import AIService
from app.services.stripe_service import StripeService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
class Settings:
    app_name: str = "ContentPilot AI"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./contentpilot.db")
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    def __init__(self):
        """Initialize settings from environment variables"""
        pass

@lru_cache()
def get_settings():
    return Settings()

# Database setup
settings = get_settings()
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory rate limiter for serverless deployment
class SimpleRateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
        self.limit = 100
        self.window = 60  # 1 minute window

    def is_allowed(self, client_id: str) -> bool:
        """Check if client is within rate limit"""
        now = time.time()
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < self.window
        ]
        # Check limit
        if len(self.requests[client_id]) >= self.limit:
            return False
        self.requests[client_id].append(now)
        return True

rate_limiter = SimpleRateLimiter()

# FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI-powered content generation platform",
    version="1.0.0"
)

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ai_service = AIService()

# Pydantic models
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int

class ContentGenerationRequest(BaseModel):
    content_type: str = Field(..., description="Type of content to generate")
    prompt: str = Field(..., min_length=10)
    additional_params: Optional[dict] = None

class ContentResponse(BaseModel):
    id: int
    content_type: str
    output: str
    tokens_used: int
    created_at: datetime

class SubscriptionInfo(BaseModel):
    tier: str
    price: float
    limit: int
    features: list

class UsageStats(BaseModel):
    tier: str
    usage_count: int
    usage_limit: int
    remaining: int
    is_unlimited: bool

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Security functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    # jose requires 'sub' to be a string
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = int(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception
    return user_id

# Authentication
async def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Get current authenticated user from token or API key"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Try to get authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
        user_id = verify_token(token, credentials_exception)
    else:
        # Try API key
        api_key = request.headers.get("X-API-Key")
        if api_key:
            user = db.query(User).filter(User.api_key == api_key).first()
            if not user:
                raise credentials_exception
            return user
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

# Routes

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve landing page"""
    with open("app/templates/index.html", "r") as f:
        return f.read()

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Serve dashboard page"""
    with open("app/templates/dashboard.html", "r") as f:
        return f.read()

@app.post("/api/auth/register", response_model=Token)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user with 10 free generations"""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user with free tier and 10 generations limit
    hashed_password = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        subscription_tier=SubscriptionTierEnum.FREE,
        usage_limit=10
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"New user registered: {user_data.email}")

    access_token = create_access_token(data={"sub": new_user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": new_user.id
    }

@app.post("/api/auth/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(data={"sub": user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id
    }

@app.get("/api/user/profile")
async def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user profile"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "subscription_tier": current_user.subscription_tier.value,
        "created_at": current_user.created_at
    }

@app.post("/api/content/generate", response_model=ContentResponse)
async def generate_content(
    request: Request,
    content_req: ContentGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate content"""
    # Simple rate limiting check
    client_id = request.client.host if request.client else "unknown"
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 100 requests per minute."
        )

    # Check usage limit
    if not StripeService.check_usage_limit(current_user):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Usage limit exceeded. Please upgrade your plan."
        )

    try:
        # Route to appropriate generation method
        if content_req.content_type == "blog_post":
            keywords = content_req.additional_params.get("keywords") if content_req.additional_params else None
            result, tokens = await ai_service.generate_blog_post(content_req.prompt, keywords)
        elif content_req.content_type == "social_media":
            platform = content_req.additional_params.get("platform", "twitter") if content_req.additional_params else "twitter"
            result, tokens = await ai_service.generate_social_media(content_req.prompt, platform)
        elif content_req.content_type == "email_copy":
            purpose = content_req.additional_params.get("purpose", "promotional") if content_req.additional_params else "promotional"
            result, tokens = await ai_service.generate_email_copy(content_req.prompt, purpose)
        elif content_req.content_type == "ad_copy":
            audience = content_req.additional_params.get("audience", "") if content_req.additional_params else ""
            result, tokens = await ai_service.generate_ad_copy(content_req.prompt, audience)
        elif content_req.content_type == "seo_content":
            keywords = content_req.additional_params.get("keywords", "") if content_req.additional_params else ""
            result, tokens = await ai_service.generate_seo_content(content_req.prompt, keywords)
        elif content_req.content_type == "product_description":
            features = content_req.additional_params.get("features", "") if content_req.additional_params else ""
            result, tokens = await ai_service.generate_product_description(content_req.prompt, features)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid content type"
            )

        # Save to database
        content = Content(
            user_id=current_user.id,
            content_type=content_req.content_type,
            prompt=content_req.prompt,
            output=str(result),
            tokens_used=tokens
        )
        db.add(content)

        # Update usage count
        current_user.usage_count += 1
        db.commit()
        db.refresh(content)

        logger.info(f"Content generated for user {current_user.id}: {content_req.content_type}")

        return ContentResponse(
            id=content.id,
            content_type=content.content_type,
            output=content.output,
            tokens_used=content.tokens_used,
            created_at=content.created_at
        )

    except Exception as e:
        logger.error(f"Content generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Content generation failed"
        )

@app.get("/api/content/history")
async def get_content_history(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's content generation history"""
    contents = db.query(Content).filter(
        Content.user_id == current_user.id
    ).order_by(Content.created_at.desc()).offset(skip).limit(limit).all()

    return [
        {
            "id": c.id,
            "content_type": c.content_type,
            "prompt": c.prompt,
            "tokens_used": c.tokens_used,
            "created_at": c.created_at
        }
        for c in contents
    ]

@app.get("/api/user/usage")
async def get_usage(current_user: User = Depends(get_current_user)):
    """Get user usage statistics"""
    return StripeService.get_usage_stats(current_user)

@app.get("/api/subscriptions")
async def get_subscriptions():
    """Get available subscription tiers"""
    tiers = StripeService.get_all_tiers()
    return {
        tier: {
            "name": tier,
            "price": config["price"],
            "limit": config["limit"],
            "features": config["features"]
        }
        for tier, config in tiers.items()
    }

@app.post("/api/subscriptions/create-checkout-session")
async def create_checkout_session(
    tier: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create Stripe checkout session"""
    if tier not in StripeService.TIER_CONFIG:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid subscription tier"
        )

    try:
        # Create or get Stripe customer
        if not current_user.stripe_customer_id:
            current_user.stripe_customer_id = StripeService.create_customer(
                current_user.email,
                current_user.full_name or current_user.email
            )
            db.commit()

        # Create subscription
        sub_result = StripeService.create_subscription(
            current_user.stripe_customer_id,
            tier,
            db,
            current_user.id
        )

        return sub_result

    except Exception as e:
        logger.error(f"Subscription creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create subscription"
        )

@app.post("/api/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhooks"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not StripeService.validate_webhook_signature(payload, sig_header):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature"
        )

    event = stripe.Event.construct_from(
        JSONResponse({"raw": payload}).body, settings.secret_key
    )

    # Handle different webhook events
    if event["type"] == "customer.subscription.updated":
        StripeService.handle_subscription_updated(
            event["data"]["object"]["id"],
            db
        )
    elif event["type"] == "customer.subscription.deleted":
        StripeService.handle_subscription_deleted(
            event["data"]["object"]["id"],
            db
        )
    elif event["type"] == "payment_intent.payment_failed":
        StripeService.handle_payment_intent_failed(
            event["data"]["object"]["id"],
            db
        )

    return {"status": "received"}

@app.post("/api/support/create-ticket")
async def create_support_ticket(
    subject: str,
    message: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a support ticket"""
    ticket = SupportTicket(
        user_id=current_user.id,
        subject=subject,
        message=message
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    logger.info(f"Support ticket created: {ticket.id} for user {current_user.id}")

    return {
        "id": ticket.id,
        "status": ticket.status.value,
        "created_at": ticket.created_at
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }

# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.debug
    )
