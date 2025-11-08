#!/bin/bash
# Quick Start Script for Meal Plan App
# Run this to start both backend and frontend

echo "🚀 Starting Meal Plan App..."
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this from the Meal-Plan-App root directory"
    exit 1
fi

# Start backend
echo "📡 Starting backend server..."
cd backend
python3 app.py &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"
cd ..

# Wait a moment for backend to initialize
sleep 2

# Start frontend
echo ""
echo "🎨 Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"
cd ..

echo ""
echo "=" * 60
echo "✅ Meal Plan App is running!"
echo "=" * 60
echo "📡 Backend:  http://127.0.0.1:5000"
echo "🎨 Frontend: http://localhost:5173"
echo ""
echo "🔍 Model: 225 classes loaded"
echo "📸 Upload images to detect ingredients"
echo ""
echo "To stop the servers:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo "=" * 60

# Keep script running
wait
