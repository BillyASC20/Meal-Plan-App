#!/bin/bash
# Simple startup script for Meal Plan App

echo "🚀 Starting Meal Plan App..."
echo ""

# Check for .env file
if [ ! -f backend/.env ]; then
    echo "⚠️  Warning: backend/.env not found!"
    echo "📝 Creating .env from .env.example..."
    if [ -f backend/.env.example ]; then
        cp backend/.env.example backend/.env
        echo "✅ Created backend/.env - Please add your OPENAI_API_KEY"
        echo ""
    else
        echo "❌ Error: backend/.env.example not found!"
        exit 1
    fi
fi

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
lsof -ti :5001 | xargs kill -9 2>/dev/null
lsof -ti :3000 | xargs kill -9 2>/dev/null
sleep 1

# Start backend
echo "🔧 Starting backend on port 5001..."
cd "$(dirname "$0")/backend" && python3 app.py > /tmp/meal-plan-backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to initialize
echo "⏳ Waiting for models to load..."
sleep 12

# Check if backend is running
if ! curl -s http://localhost:5001/health > /dev/null 2>&1; then
    echo "❌ Backend failed to start. Check logs: tail -f /tmp/meal-plan-backend.log"
    exit 1
fi

# Start frontend
echo "🎨 Starting frontend on port 3000..."
cd "$(dirname "$0")/frontend" && npm run dev > /tmp/meal-plan-frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

sleep 3

echo ""
echo "✅ App started successfully!"
echo "📱 Frontend: http://localhost:3000"
echo "🔌 Backend: http://localhost:5001"
echo ""
echo "📋 Backend PID: $BACKEND_PID"
echo "📋 Frontend PID: $FRONTEND_PID"
echo ""
echo "💡 To stop: kill $BACKEND_PID $FRONTEND_PID"
echo "💡 View backend logs: tail -f /tmp/meal-plan-backend.log"
echo "💡 View frontend logs: tail -f /tmp/meal-plan-frontend.log"
