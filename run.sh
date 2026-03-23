#!/bin/bash

# ContentPilot AI - Startup Script

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please configure your API keys in .env"
fi

# Run the application
echo "Starting ContentPilot AI..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
