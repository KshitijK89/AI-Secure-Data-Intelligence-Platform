#!/bin/bash

echo "🛡️  AI Secure Data Intelligence Platform"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.10 or higher."
    exit 1
fi

echo "✅ Python found: $(python --version)"

# Backend Setup
echo ""
echo "📦 Setting up Backend..."
cd backend || exit

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || source venv/Scripts/activate

# Install dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Backend setup complete!"
echo ""

# Frontend Setup
echo "📦 Setting up Frontend..."
cd ../frontend || exit

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

echo "✅ Node.js found: $(node --version)"
echo "✅ npm found: $(npm --version)"

# Install dependencies
echo "Installing frontend dependencies..."
npm install

echo ""
echo "✅ Frontend setup complete!"
echo ""
echo "========================================"
echo "🎉 Setup Complete!"
echo ""
echo "To start the application:"
echo "1. Backend:  cd backend && python -m uvicorn app.main:app --reload"
echo "2. Frontend: cd frontend && npm start"
echo ""
echo "Or use the start scripts provided."
echo "========================================"
