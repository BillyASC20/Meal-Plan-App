#!/bin/bash
# Stop all Meal Plan App services

echo "🛑 Stopping Meal Plan App..."

# Try to read PIDs from files
if [ -f /tmp/meal-plan-backend.pid ]; then
    BACKEND_PID=$(cat /tmp/meal-plan-backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "   Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
    fi
    rm /tmp/meal-plan-backend.pid
fi

if [ -f /tmp/meal-plan-frontend.pid ]; then
    FRONTEND_PID=$(cat /tmp/meal-plan-frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "   Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
    fi
    rm /tmp/meal-plan-frontend.pid
fi

# Kill anything else on the ports
echo "   Cleaning up ports 5001 and 3000..."
lsof -ti :5001 2>/dev/null | xargs kill -9 2>/dev/null || true
lsof -ti :3000 2>/dev/null | xargs kill -9 2>/dev/null || true

echo "✅ All services stopped"
