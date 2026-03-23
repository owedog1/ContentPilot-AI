# ContentPilot AI Deployment Guide

This guide provides step-by-step instructions for deploying ContentPilot AI to production environments.

## Prerequisites

- Python 3.11.7 or higher
- Git (for GitHub deployment options)
- An Anthropic API key

## Option A: Deploy to Railway (Recommended - Free Tier)

Railway is the recommended deployment platform with a free tier suitable for getting started.

### Step 1: Create a Railway Account
Visit [railway.com](https://railway.com) and create a free account. You can sign up with GitHub for quick authentication.

### Step 2: Install Railway CLI
Railway CLI is required to deploy from your local machine.

```bash
npm i -g @railway/cli
```

Ensure Node.js and npm are installed on your system.

### Step 3: Login to Railway
Authenticate with your Railway account:

```bash
railway login
```

This will open a browser window to complete the authentication flow.

### Step 4: Initialize Railway Project
From your ContentPilot-AI project directory, initialize Railway:

```bash
railway init
```

Follow the prompts to create a new Railway project or select an existing one.

### Step 5: Set Environment Variables
Configure required environment variables:

```bash
railway variables set ANTHROPIC_API_KEY=your_actual_api_key
railway variables set SECRET_KEY=your_secure_random_secret
```

Replace `your_actual_api_key` with your Anthropic API key and `your_secure_random_secret` with a strong random string.

### Step 6: Deploy to Railway
Deploy your application:

```bash
railway up
```

Railway will automatically:
- Detect your Python project
- Install dependencies from requirements.txt
- Build using Nixpacks
- Deploy using the command from railway.json
- Monitor health checks at /api/health

### Step 7: Get Your Deployment URL
Retrieve your application's public URL:

```bash
railway domain
```

This will display your application's live URL.

### Monitoring and Logs
View application logs:

```bash
railway logs
```

View deployed services:

```bash
railway status
```

---

## Option B: Deploy to Render (Alternative - Free Tier)

Render offers an alternative free tier deployment option with GitHub integration.

### Prerequisites
- Your project must be pushed to a GitHub repository

### Deployment Steps

1. Visit [render.com](https://render.com) and create a free account

2. Connect your GitHub account to Render

3. In the Render dashboard, click "New +" and select "Web Service"

4. Connect your GitHub repository containing ContentPilot-AI

5. Configure the deployment:
   - **Name**: contentpilot-ai
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

6. Add environment variables in the Render dashboard:
   - `ANTHROPIC_API_KEY`: Your Anthropic API key
   - `SECRET_KEY`: A strong random secret
   - `DATABASE_URL`: `sqlite:///./contentpilot.db` (default)

7. Click "Create Web Service" to deploy

Render will automatically redeploy whenever you push changes to your GitHub repository.

---

## Option C: Run Locally for Development

For local development and testing:

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Set Up Environment Variables
Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` and add:
```
ANTHROPIC_API_KEY=your_actual_api_key
SECRET_KEY=your_secure_random_secret
DATABASE_URL=sqlite:///./contentpilot.db
```

### Step 3: Run the Application
Start the development server with auto-reload enabled:

```bash
python -m uvicorn app.main:app --reload
```

The application will be available at `http://localhost:8000`.

### Accessing the API
- API Documentation (interactive): `http://localhost:8000/docs`
- Alternative API Documentation: `http://localhost:8000/redoc`
- Health Check: `http://localhost:8000/api/health`

---

## Deployment Comparison

| Feature | Railway | Render | Local |
|---------|---------|--------|-------|
| Free Tier | Yes | Yes | N/A |
| Automatic Deploys | Manual CLI | GitHub Integration | N/A |
| Database Support | SQLite | SQLite | SQLite |
| Custom Domain | Yes | Yes | N/A |
| Monitoring | Built-in | Built-in | Manual |
| Environment Management | Dashboard/CLI | Dashboard | .env file |

---

## Environment Variables Reference

Essential environment variables for all deployment options:

- **ANTHROPIC_API_KEY** (required): Your Anthropic API key for Claude integration
- **SECRET_KEY** (required): Secret key for session management and security (use a strong random value)
- **DATABASE_URL** (optional): Database connection string. Defaults to SQLite at `sqlite:///./contentpilot.db`

---

## Health Checks and Monitoring

The application provides a health check endpoint at `/api/health` that returns:

```json
{
  "status": "healthy",
  "timestamp": "2026-03-23T12:00:00Z"
}
```

Both Railway and Render are configured to monitor this endpoint and restart the application if it becomes unhealthy.

---

## Troubleshooting

### Application Won't Start
- Check that all environment variables are set correctly
- Verify Python 3.11.7+ is available
- Ensure all dependencies in requirements.txt can be installed

### Database Issues
- SQLite database files are stored locally in the deployment environment
- For persistent data, consider migrating to PostgreSQL after initial deployment
- Current setup suitable for small to medium deployments

### API Key Errors
- Verify your ANTHROPIC_API_KEY is valid and active
- Check that the key hasn't reached its usage limit
- Ensure the key is in the correct format (should start with `sk-`)

### Port Binding Issues
- Railway and Render automatically set the PORT environment variable
- The application reads this via `${PORT:-8000}` syntax
- Local development defaults to port 8000 if PORT is not set

---

## Next Steps

After successful deployment:

1. Test your API endpoints using the interactive documentation at `/docs`
2. Set up a custom domain (Railway/Render dashboards)
3. Configure monitoring alerts (optional)
4. Plan database migration strategy for production data volume
5. Set up CI/CD pipeline for automated deployments
6. Consider API rate limiting and authentication tokens

---

## Support and Resources

- [Railway Documentation](https://docs.railway.app/)
- [Render Documentation](https://render.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Anthropic API Documentation](https://docs.anthropic.com/)
