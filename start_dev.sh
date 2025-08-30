#!/bin/bash

# Portfolio Dashboard Development Startup Script

echo "🚀 Starting Portfolio Dashboard Development Environment"
echo "=================================================="

# Function to cleanup background processes on exit
cleanup() {
    echo "🛑 Shutting down development servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo "📊 Starting FastAPI Backend..."
echo "   Backend will be available at: http://localhost:8000"
echo "   API docs will be available at: http://localhost:8000/docs"
echo ""

# Start FastAPI backend in background
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

echo "⚛️  Starting React Frontend..."
echo "   Frontend will be available at: http://localhost:3000"
echo ""

# Start React frontend in background
cd frontend && npm start &
FRONTEND_PID=$!

echo "✅ Both servers are starting up..."
echo "   Backend PID: $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""
echo "🌐 Open your browser to:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for both processes
wait
