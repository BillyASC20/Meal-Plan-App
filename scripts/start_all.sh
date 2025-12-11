#!/usr/bin/env bash
set -euo pipefail

# start_all.sh
# - Deletes backend venv
# - Creates fresh backend venv and installs all packages from backend/requirements.txt
# - Starts backend (background), waits for /health
# - Installs frontend deps (npm ci or npm install) and starts frontend (background)
# Logs are written to .dev-logs/backend.log and .dev-logs/frontend.log

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$PROJECT_ROOT/.dev-logs"
mkdir -p "$LOG_DIR"

echo "Project root: $PROJECT_ROOT"

########################################
# Backend: recreate venv + install reqs
########################################
BACKEND_DIR="$PROJECT_ROOT/backend"
VENV_DIR="$BACKEND_DIR/.venv"
REQ_FILE="$BACKEND_DIR/requirements.txt"

echo "\n== Backend: removing old venv (if exists) =="
if [ -d "$VENV_DIR" ]; then
  echo "Removing $VENV_DIR"
  rm -rf "$VENV_DIR"
fi

echo "Creating venv at $VENV_DIR"
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel

echo "Installing backend requirements from $REQ_FILE"
# Try normal install first (follows exactly requirements.txt)
if "$VENV_DIR/bin/pip" install -r "$REQ_FILE"; then
  echo "Installed backend requirements successfully"
else
  echo "pip install failed. Trying fallback: install all but pillow, then binary pillow"
  TMP_REQS=$(mktemp)
  grep -v -E '^\s*pillow' "$REQ_FILE" > "$TMP_REQS"
  if ! "$VENV_DIR/bin/pip" install -r "$TMP_REQS"; then
    echo "Failed installing backend requirements without pillow. See pip output above." 
    rm -f "$TMP_REQS"
    exit 1
  fi
  # Try installing a binary wheel of pillow (may still fail if wheel unavailable for your Python/OS)
  if ! "$VENV_DIR/bin/pip" install --only-binary=:all: pillow; then
    echo "Binary pillow install failed. To fix, install system image libraries and try again:"
    echo "  brew install libjpeg libtiff libpng zlib little-cms2"
    echo "Then re-run: $0"
    rm -f "$TMP_REQS"
    exit 1
  fi
  rm -f "$TMP_REQS"
fi

########################################
# Start backend
########################################
BACKEND_LOG="$LOG_DIR/backend.log"
BACKEND_PIDFILE="$BACKEND_DIR/.pid"

echo "Starting backend: logs -> $BACKEND_LOG"
nohup "$VENV_DIR/bin/python" "$BACKEND_DIR/app.py" > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "$BACKEND_PIDFILE"

# wait for health endpoint to become available (try ports 5000 and 5001)
echo "Waiting for backend /health (up to 30s)"
HEALTH_OK=0
for i in {1..30}; do
  for PORT in 5000 5001 8000; do
    if curl -sS "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
      echo "Backend healthy on port $PORT"
      HEALTH_OK=1
      break 2
    fi
  done
  sleep 1
done

if [ "$HEALTH_OK" -ne 1 ]; then
  echo "Backend did not respond to /health after 30s. Check $BACKEND_LOG"
else
  echo "Backend started and healthy. PID=$BACKEND_PID"
fi

########################################
# Frontend: install deps and start
########################################
FRONTEND_DIR="$PROJECT_ROOT/frontend"
FRONTEND_LOG="$LOG_DIR/frontend.log"
FRONTEND_PIDFILE="$FRONTEND_DIR/.pid"

echo "\n== Frontend: checking for node & npm =="
if ! command -v node >/dev/null 2>&1; then
  echo "node is not installed. Please install node (via Homebrew or nvm) and re-run script. Skipping frontend start."
  exit 0
fi

cd "$FRONTEND_DIR"
if [ -f package-lock.json ]; then
  echo "Running npm ci (reproducible install)"
  npm ci --loglevel=error || { echo "npm ci failed, trying npm install"; npm install; }
else
  echo "Running npm install"
  npm install
fi

# Start frontend dev server
echo "Starting frontend dev server: logs -> $FRONTEND_LOG"
# Use npm run dev which typically runs vite
nohup npm run dev > "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$FRONTEND_PIDFILE"

# wait briefly for vite (default port 5173)
echo "Waiting for frontend (port 5173)"
FRONT_OK=0
for i in {1..20}; do
  if curl -sS "http://127.0.0.1:5173/" >/dev/null 2>&1; then
    FRONT_OK=1
    break
  fi
  sleep 1
done

if [ "$FRONT_OK" -eq 1 ]; then
  echo "Frontend started and responsive. PID=$FRONTEND_PID"
else
  echo "Frontend may not be ready yet. Check $FRONTEND_LOG"
fi

echo "\nDone. Backend log: $BACKEND_LOG, Frontend log: $FRONTEND_LOG"
echo "Backend PID: $BACKEND_PID (stored in $BACKEND_PIDFILE)"
echo "Frontend PID: $FRONTEND_PID (stored in $FRONTEND_PIDFILE)"

exit 0
