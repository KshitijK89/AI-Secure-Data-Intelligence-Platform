#!/bin/bash
echo "Starting Backend Server..."
cd backend
source venv/bin/activate || source venv/Scripts/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
