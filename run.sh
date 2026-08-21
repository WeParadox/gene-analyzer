#!/bin/bash

echo "🧬 Gene Analyzer - Starting services..."

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "Using Docker Compose..."
    docker-compose up --build
else
    echo "Docker not found. Starting in development mode..."
    
    # Start backend
    echo "Starting backend on http://localhost:8000..."
    cd backend
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    cd ..
    
    # Start frontend if node is available
    if command -v node &> /dev/null; then
        echo "Starting frontend on http://localhost:5173..."
        cd frontend
        npm run dev &
        FRONTEND_PID=$!
        cd ..
    else
        echo "Node.js not found. Frontend not started."
        echo "API docs available at http://localhost:8000/docs"
    fi
    
    # Wait for interrupt
    echo ""
    echo "Press Ctrl+C to stop all services"
    trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
    wait
fi
