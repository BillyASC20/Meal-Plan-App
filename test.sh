#!/bin/bash
# Quick local test without Docker

echo "🧪 Quick Local Test"
echo "==================="
echo ""

# Check Python
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "❌ Python not found!"
    exit 1
fi

PYTHON_CMD=$(command -v python3 || command -v python)
echo "✅ Python: $PYTHON_CMD"

# Check .env
if [ ! -f .env ]; then
    echo "❌ .env file missing! Copy from .env.template"
    exit 1
fi

export $(cat .env | grep OPENAI_API_KEY | xargs)
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY not set in .env"
    exit 1
fi
echo "✅ OPENAI_API_KEY found"

# Check requirements
echo ""
echo "📦 Checking Python packages..."
cd backend

MISSING_PACKAGES=()
while IFS= read -r line; do
    # Skip comments and empty lines
    [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
    
    # Extract package name (before ==, >=, etc.)
    PACKAGE=$(echo "$line" | sed -E 's/([a-zA-Z0-9_-]+).*/\1/')
    
    if ! $PYTHON_CMD -c "import $PACKAGE" 2>/dev/null; then
        MISSING_PACKAGES+=("$line")
    fi
done < requirements.txt

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo "⚠️  Missing packages:"
    printf '   - %s\n' "${MISSING_PACKAGES[@]}"
    echo ""
    echo "Install with:"
    echo "   cd backend && pip install -r requirements.txt"
    echo "   pip install git+https://github.com/IDEA-Research/GroundingDINO.git"
    echo "   pip install git+https://github.com/facebookresearch/segment-anything.git"
    exit 1
fi
echo "✅ All packages installed"

# Check models
echo ""
echo "🤖 Checking model files..."
if [ ! -f "models/grounded_sam/groundingdino_swint_ogc.pth" ]; then
    echo "❌ Missing: groundingdino_swint_ogc.pth"
    echo "   Run: curl -L -o backend/models/grounded_sam/groundingdino_swint_ogc.pth https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth"
    exit 1
fi

if [ ! -f "models/grounded_sam/sam_vit_b_01ec64.pth" ]; then
    echo "❌ Missing: sam_vit_b_01ec64.pth"
    echo "   Run: curl -L -o backend/models/grounded_sam/sam_vit_b_01ec64.pth https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"
    exit 1
fi
echo "✅ Model files present"

# Test import
echo ""
echo "🔍 Testing service imports..."
if $PYTHON_CMD -c "from grounded_sam_service import grounded_sam_service; print(f'Service ready: {grounded_sam_service.is_ready}')" 2>/dev/null; then
    echo "✅ Grounded-SAM service loads successfully"
else
    echo "❌ Failed to load Grounded-SAM service"
    echo ""
    echo "Try running:"
    echo "   cd backend && python -c 'from grounded_sam_service import grounded_sam_service'"
    exit 1
fi

# Kill any existing backend
echo ""
echo "🧹 Cleaning up old processes..."
lsof -ti :5001 | xargs kill -9 2>/dev/null
sleep 1

# Start backend
echo "🚀 Starting backend..."
$PYTHON_CMD app.py > /tmp/test-backend.log 2>&1 &
BACKEND_PID=$!
echo "   PID: $BACKEND_PID"

# Wait and test
echo ""
echo "⏳ Waiting for service to start (30s)..."
for i in {1..30}; do
    sleep 1
    if curl -s http://localhost:5001/health > /dev/null 2>&1; then
        echo ""
        echo "✅ Service is UP!"
        break
    fi
    echo -n "."
done
echo ""

# Test health
echo ""
echo "🧪 Testing health endpoint..."
HEALTH=$(curl -s http://localhost:5001/health)
echo "Response: $HEALTH"

if echo "$HEALTH" | grep -q "healthy"; then
    echo ""
    echo "================================"
    echo "✅ ALL TESTS PASSED!"
    echo "================================"
    echo ""
    echo "Backend is running on http://localhost:5001"
    echo "Backend PID: $BACKEND_PID"
    echo ""
    echo "View logs: tail -f /tmp/test-backend.log"
    echo "Stop backend: kill $BACKEND_PID"
    echo ""
    echo "Ready to deploy! 🚀"
else
    echo ""
    echo "❌ Health check failed!"
    echo ""
    echo "Check logs:"
    echo "   tail -f /tmp/test-backend.log"
    echo ""
    echo "Kill process:"
    echo "   kill $BACKEND_PID"
    exit 1
fi
