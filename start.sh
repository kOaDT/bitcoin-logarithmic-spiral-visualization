#!/bin/bash
echo "Bitcoin Logarithmic Spiral API"
echo "=============================="

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    echo "Warning: .env file not found!"
    echo "Please create a .env file with your database configuration."
    echo "You can use .env.example as a template."
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Starting Bitcoin Logarithmic Spiral API..."
echo "Open http://localhost:8000 in your browser"
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 