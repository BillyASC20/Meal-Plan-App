#!/bin/bash
# Rebuild & redeploy helper for Meal Plan App
# Usage:
#   ./rebuild.sh            # Clean caches and rebuild frontend
#   ./rebuild.sh --full     # Also reinstall frontend deps & recreate backend venv
#   ./rebuild.sh --docker   # Also rebuild backend docker image
#   ./rebuild.sh --all      # Full + docker
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

FULL=0
DOCKER=0
for arg in "$@"; do
  case "$arg" in
    --full) FULL=1 ;;
    --docker) DOCKER=1 ;;
    --all) FULL=1; DOCKER=1 ;;
  esac
done

BACKEND_ENV_FILE="backend/.env"
if [ ! -f "$BACKEND_ENV_FILE" ]; then
  echo "❌ backend/.env not found. Create it from backend/.env.example and add OPENAI_API_KEY"
  exit 1
fi

OPENAI_KEY_LINE=$(grep -E '^OPENAI_API_KEY=' "$BACKEND_ENV_FILE" || true)
OPENAI_KEY_VALUE=${OPENAI_KEY_LINE#OPENAI_API_KEY=}
if [ -z "$OPENAI_KEY_VALUE" ]; then
  echo "❌ OPENAI_API_KEY value empty in $BACKEND_ENV_FILE"
  exit 1
fi
if echo "$OPENAI_KEY_VALUE" | grep -qiE 'your_openai_api_key_here|your_openai_key_here'; then
  echo "❌ Placeholder OPENAI_API_KEY detected. Edit $BACKEND_ENV_FILE and insert your real key (no quotes)."
  exit 1
fi
if echo "$OPENAI_KEY_VALUE" | grep -q '"'; then
  echo "⚠️  Detected quotes around key. Removing them is recommended. Current: $OPENAI_KEY_VALUE"
fi

echo "🔑 OPENAI_API_KEY appears set (length ${#OPENAI_KEY_VALUE})."

# Kill existing processes on ports
echo "🧹 Stopping existing processes on ports 5001 & 3000 (if any)..."
lsof -ti :5001 2>/dev/null | xargs kill -9 2>/dev/null || true
lsof -ti :3000 2>/dev/null | xargs kill -9 2>/dev/null || true

# Clean Python caches
echo "🧼 Cleaning Python __pycache__ directories..."
find backend -type d -name '__pycache__' -prune -exec rm -rf {} + || true

# Optionally recreate venv
if [ $FULL -eq 1 ]; then
  echo "🐍 Recreating backend virtual environment (venv)..."
  rm -rf backend/venv
  python3 -m venv backend/venv
  source backend/venv/bin/activate
  pip install --upgrade pip wheel
  pip install -r backend/requirements.txt
else
  # Lightweight dependency check
  if ! python3 -c 'import flask, openai' 2>/dev/null; then
    echo "⚠️  Python deps missing; installing..."
    pip install -r backend/requirements.txt
  fi
fi

# Frontend cleanup
echo "🧼 Cleaning frontend build artifacts..."
rm -rf frontend/dist
if [ $FULL -eq 1 ]; then
  echo "📦 Removing node_modules for full reinstall..."
  rm -rf frontend/node_modules
fi

# Reinstall frontend deps if missing or full
if [ $FULL -eq 1 ] || [ ! -d frontend/node_modules ]; then
  echo "📦 Installing frontend dependencies..."
  (cd frontend && npm install)
fi

# Build frontend production bundle
echo "🏗️ Building frontend (npm run build)..."
(cd frontend && npm run build)

# Docker rebuild if requested
if [ $DOCKER -eq 1 ]; then
  echo "🐳 Rebuilding backend Docker image (no cache)..."
  docker build --no-cache -t meal-plan-backend .
  echo "✅ Docker image meal-plan-backend rebuilt"
fi

# Start backend and frontend (dev mode)
echo "🚀 Starting backend (port 5001) in background..."
( cd backend && python3 app.py > /tmp/meal-plan-backend.log 2>&1 & echo $! > /tmp/meal-plan-backend.pid )

# Wait for backend health
echo -n "⏳ Waiting for backend health"
for i in {1..25}; do
  if curl -s http://localhost:5001/health >/dev/null 2>&1; then
    echo " -> ✅"
    break
  fi
  echo -n "."
  sleep 1
  if [ $i -eq 25 ]; then
    echo "\n❌ Backend failed to become healthy. Check /tmp/meal-plan-backend.log"
  fi
done

echo "🎨 Starting frontend dev server (port 3000) in background..."
( cd frontend && npm run dev > /tmp/meal-plan-frontend.log 2>&1 & echo $! > /tmp/meal-plan-frontend.pid )

sleep 3

echo "\n✅ Rebuild complete"
BACKEND_PID=$(cat /tmp/meal-plan-backend.pid 2>/dev/null || echo '?')
FRONTEND_PID=$(cat /tmp/meal-plan-frontend.pid 2>/dev/null || echo '?')

echo "📱 Frontend:  http://localhost:3000"
echo "🔌 Backend:   http://localhost:5001"
echo "📄 Logs: tail -f /tmp/meal-plan-backend.log | /tmp/meal-plan-frontend.log"
echo "🛑 Stop: kill $BACKEND_PID $FRONTEND_PID  (or use ./stop.sh if present)"

echo "🔍 Validate API key inside Python:"
echo "    python3 -c 'import os; from dotenv import load_dotenv; load_dotenv("backend/.env"); print(os.getenv("OPENAI_API_KEY")[:10])'"

