# ContentPilot AI - Installation & Setup Guide

## Quick Start (5 minutes)

### Prerequisites
- Python 3.8+ installed
- pip or poetry for dependency management
- (Optional) PostgreSQL 12+ for production

### Steps

1. **Navigate to project directory**
```bash
cd /sessions/ecstatic-intelligent-hypatia/mnt/Bussniess/ContentPilot-AI
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create environment file**
```bash
cp .env.example .env
```

5. **Edit `.env` with your API keys**
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-key-here
STRIPE_API_KEY=sk_test_your-key-here
SECRET_KEY=your-super-secret-key-minimum-32-chars
```

6. **Run the application**
```bash
python -m uvicorn app.main:app --reload
```

7. **Visit in browser**
```
http://localhost:8000
```

## Core Application Files

### Backend
- `app/main.py` - FastAPI application (505 lines)
  - 12+ API endpoints
  - JWT authentication
  - Rate limiting
  - Stripe webhooks
  - Error handling

- `app/models/database.py` - Database models (117 lines)
  - User model
  - Content model
  - Support ticket model
  - Subscription tier model

- `app/services/ai_service.py` - AI service (311 lines)
  - Blog post generation
  - Social media content
  - Email copy
  - Ad copy
  - SEO content
  - Product descriptions

- `app/services/stripe_service.py` - Payment service (219 lines)
  - Subscription management
  - Customer handling
  - Webhook processing
  - Usage tracking

### Frontend
- `app/templates/index.html` - Landing page (684 lines)
  - Marketing sections
  - Pricing table
  - FAQ section
  - Testimonials

- `app/templates/dashboard.html` - User dashboard (470 lines)
  - Content generation form
  - History view
  - Usage statistics
  - Account settings

## Configuration

### Required Environment Variables

```env
# Database
DATABASE_URL=sqlite:///./contentpilot.db
# For PostgreSQL: postgresql://user:password@localhost:5432/contentpilot

# API Keys (required for content generation)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...  # Optional, used as fallback

# Stripe (required for payment features)
STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_test_...

# Security
SECRET_KEY=your-super-secret-key-minimum-32-chars-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
APP_NAME=ContentPilot AI
APP_ENV=development
DEBUG=True
FRONTEND_URL=http://localhost:3000
```

## Running the Application

### Option 1: Direct Python
```bash
python -m uvicorn app.main:app --reload --port 8000
```

### Option 2: Using run.sh script
```bash
chmod +x run.sh
./run.sh
```

### Option 3: Docker
```bash
docker-compose up
```

## First Time Setup Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (pip install -r requirements.txt)
- [ ] .env file created with API keys
- [ ] Database configured (SQLite or PostgreSQL)
- [ ] Application starts without errors
- [ ] Landing page loads at http://localhost:8000
- [ ] Can register a new user
- [ ] Can generate content (with API keys configured)

## API Documentation

Once running, access interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing the Application

### Test User Registration
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123",
    "full_name": "Test User"
  }'
```

### Test Content Generation
```bash
curl -X POST http://localhost:8000/api/content/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "blog_post",
    "prompt": "Write about the benefits of AI in business",
    "additional_params": {"keywords": "artificial intelligence, automation"}
  }'
```

## Troubleshooting

### Port Already in Use
```bash
# Use a different port
python -m uvicorn app.main:app --reload --port 8001
```

### Database Error
```bash
# Reset database (development only)
rm contentpilot.db
# Then restart the app
```

### API Key Issues
- Verify keys are correct
- Check API key format
- Ensure keys have necessary permissions
- Check .env file is properly formatted

### Missing Dependencies
```bash
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

## File Structure

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
│   │   ├── ai_service.py       # Content generation
│   │   └── stripe_service.py   # Payment processing
│   ├── templates/
│   │   ├── index.html          # Landing page
│   │   └── dashboard.html      # User dashboard
│   └── static/                 # CSS, JS, images
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── Dockerfile                 # Container image
├── docker-compose.yml         # Full stack
├── run.sh                     # Startup script
├── README.md                  # Documentation
└── INSTALLATION_GUIDE.md      # This file
```

## Deployment

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Use strong `SECRET_KEY` (32+ random characters)
- [ ] Configure PostgreSQL database
- [ ] Set up HTTPS/SSL
- [ ] Configure proper CORS
- [ ] Set up monitoring and logging
- [ ] Configure email service
- [ ] Test Stripe webhooks
- [ ] Set up backups
- [ ] Configure CI/CD

### Deployment Platforms
- Heroku
- Railway
- Render
- AWS (EC2, ECS, Lambda)
- Google Cloud Run
- DigitalOcean
- Fly.io

## Next Steps

1. Read the `README.md` for full documentation
2. Check `IMPLEMENTATION_SUMMARY.md` for technical details
3. Explore the API at `/docs`
4. Configure your API keys
5. Create test user and generate content
6. Customize as needed

## Support

For issues or questions:
- Check README.md and IMPLEMENTATION_SUMMARY.md
- Review API documentation at /docs
- Check .env.example for all configuration options
- Review logs for error messages

---

**Happy building! 🚀**
