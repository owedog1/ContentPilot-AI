# ContentPilot AI - AI-Powered Content Generation SaaS

A complete, production-ready FastAPI application for AI-powered content generation. Generate blog posts, social media posts, email copy, ad copy, SEO content, and product descriptions using Claude AI.

## Features

- **Multiple Content Types**
  - Blog Posts (with SEO optimization)
  - Social Media Posts (Twitter, LinkedIn, Instagram)
  - Email Copy (high-converting templates)
  - Ad Copy (Google, Facebook, LinkedIn ads)
  - SEO Content (keyword-optimized articles)
  - Product Descriptions (e-commerce focused)

- **Authentication & Authorization**
  - User registration and login
  - JWT token-based authentication
  - API key authentication for integrations

- **Subscription Management**
  - Three-tier pricing (Starter, Pro, Agency)
  - Usage-based rate limiting
  - Stripe payment integration
  - Webhook handling for subscription events

- **Content Generation**
  - AI-powered generation using Claude 3.5 Sonnet (primary) with GPT-3.5 Turbo fallback
  - Token usage tracking
  - Generation history
  - Content storage and retrieval

- **Dashboard**
  - Beautiful, responsive UI
  - Real-time usage statistics
  - Generation history
  - Account settings
  - Subscription management

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Database**: PostgreSQL (or SQLite for development)
- **Authentication**: JWT, OAuth, bcrypt
- **AI**: Anthropic Claude API, OpenAI API
- **Payments**: Stripe
- **Frontend**: Tailwind CSS, HTML5, JavaScript
- **Rate Limiting**: SlowAPI

## Project Structure

```
ContentPilot-AI/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── models/
│   │   ├── __init__.py
│   │   └── database.py         # SQLAlchemy models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py       # AI content generation
│   │   └── stripe_service.py   # Stripe integration
│   ├── templates/
│   │   ├── index.html          # Landing page
│   │   └── dashboard.html      # User dashboard
│   └── static/                 # Static files
├── requirements.txt
├── .env.example
└── README.md
```

## Quick Start

```bash
# Clone and setup
git clone <repo>
cd ContentPilot-AI
python -m venv venv
source venv/bin/activate

# Configure
cp .env.example .env
# Edit .env with your API keys

# Install and run
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register
- `POST /api/auth/login` - Login

### Content
- `POST /api/content/generate` - Generate content
- `GET /api/content/history` - Get history

### Subscriptions
- `GET /api/subscriptions` - Get plans
- `POST /api/subscriptions/create-checkout-session` - Checkout

### User
- `GET /api/user/profile` - Profile
- `GET /api/user/usage` - Usage stats

## Subscription Tiers

| Tier | Price | Limit |
|------|-------|-------|
| Free | $0 | 0 |
| Starter | $29/mo | 50 |
| Pro | $79/mo | 200 |
| Agency | $199/mo | Unlimited |

## Environment Setup

Create `.env` file:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/contentpilot
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
STRIPE_API_KEY=sk_test_...
SECRET_KEY=your-secret-key
```

## Documentation

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- Full documentation in this README

## License

MIT License
