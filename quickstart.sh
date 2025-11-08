#!/bin/bash
# Quick Start Script for Meal Plan App
# This script starts both frontend and backend in separate terminals

set -e

echo "🚀 Meal Plan App - Quick Start"
echo "================================"
echo ""

# Check if we're in the right directory
if [ ! -f "start.sh" ]; then
    echo "❌ Error: Please run this script from the Meal-Plan-App root directory"
    exit 1
fi

# Check for .env file
if [ ! -f "backend/.env" ]; then
    echo "⚠️  backend/.env not found!"
    if [ -f "backend/.env.example" ]; then
        echo "📝 Creating backend/.env from example..."
        cp backend/.env.example backend/.env
        echo ""
        echo "⚠️  IMPORTANT: Edit backend/.env and add your OPENAI_API_KEY"
        echo "   Get your key from: https://platform.openai.com/api-keys"
        echo ""
        read -p "Press Enter after you've added your API key..."
    fi
fi

# Kill any existing processes
echo "🧹 Cleaning up existing processes on ports 5001 and 3000..."
lsof -ti :5001 2>/dev/null | xargs kill -9 2>/dev/null || true
lsof -ti :3000 2>/dev/null | xargs kill -9 2>/dev/null || true
sleep 1

echo ""
echo "📋 Starting services..."
echo "   Backend will start on: http://localhost:5001"
echo "   Frontend will start on: http://localhost:3000"
echo ""

# Start backend in background
echo "🔧 Starting backend (this takes 10-15 seconds to load models)..."
cd backend
python3 app.py > /tmp/meal-plan-backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to be ready
echo "⏳ Waiting for backend to load AI models..."
for i in {1..30}; do
    if curl -s http://localhost:5001/health > /dev/null 2>&1; then
        echo "✅ Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start. Check logs:"
        echo "   tail -f /tmp/meal-plan-backend.log"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
    echo -n "."
done
echo ""

# Start frontend in background
echo "🎨 Starting frontend..."
cd frontend
npm run dev > /tmp/meal-plan-frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to be ready
sleep 3
if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "⚠️  Frontend may not be ready yet, check logs if needed"
fi

echo ""
echo "✅ App is running!"
echo "================================"
echo "📱 Frontend: http://localhost:3000"
echo "🔌 Backend:  http://localhost:5001"
echo ""
echo "📋 Process IDs:"
echo "   Backend:  $BACKEND_PID"
echo "   Frontend: $FRONTEND_PID"
echo ""
echo "📄 View logs:"
echo "   Backend:  tail -f /tmp/meal-plan-backend.log"
echo "   Frontend: tail -f /tmp/meal-plan-frontend.log"
echo ""
echo "🛑 To stop the app:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo "   OR use: ./stop.sh"
echo ""
echo "💡 Press Ctrl+C to stop monitoring, services will keep running"
echo ""

# Save PIDs for stop script
echo "$BACKEND_PID" > /tmp/meal-plan-backend.pid
echo "$FRONTEND_PID" > /tmp/meal-plan-frontend.pid

# Monitor both processes
trap "echo ''; echo '⚠️  Monitoring stopped. Services still running.'; exit 0" INT

echo "📊 Monitoring services (Ctrl+C to stop monitoring)..."
while true; do
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "❌ Backend crashed! Check logs: tail -f /tmp/meal-plan-backend.log"
        break
    fi
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ Frontend crashed! Check logs: tail -f /tmp/meal-plan-frontend.log"
        break
    fi
    sleep 2
done
