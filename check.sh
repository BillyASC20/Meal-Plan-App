#!/bin/bash
# Pre-deployment checklist - Run this before deploying!

echo "✈️  PRE-DEPLOYMENT CHECKLIST"
echo "============================"
echo ""

ERRORS=0
WARNINGS=0

# 1. Check Git
echo "1️⃣  Checking Git repository..."
if [ -d .git ]; then
    echo "   ✅ Git repository exists"
    
    # Check for uncommitted changes
    if [[ -n $(git status -s) ]]; then
        echo "   ⚠️  WARNING: Uncommitted changes detected"
        WARNINGS=$((WARNINGS + 1))
        git status -s | head -5
    else
        echo "   ✅ No uncommitted changes"
    fi
    
    # Check remote
    if git remote -v | grep -q origin; then
        echo "   ✅ Git remote configured"
    else
        echo "   ❌ ERROR: No git remote! Run: git remote add origin <url>"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "   ❌ ERROR: Not a git repository! Run: git init"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# 2. Check .env file
echo "2️⃣  Checking environment variables..."
if [ -f .env ]; then
    echo "   ✅ .env file exists"
    
    # Check for OPENAI_API_KEY
    if grep -q "OPENAI_API_KEY=" .env; then
        KEY_VALUE=$(grep "OPENAI_API_KEY=" .env | cut -d'=' -f2)
        if [ "$KEY_VALUE" = "your_openai_key_here" ] || [ -z "$KEY_VALUE" ] || [ "$KEY_VALUE" = "your" ]; then
            echo "   ⚠️  WARNING: OPENAI_API_KEY has placeholder value"
            echo "      Set your real API key before deploying!"
            WARNINGS=$((WARNINGS + 1))
        else
            echo "   ✅ OPENAI_API_KEY is set"
        fi
    else
        echo "   ⚠️  WARNING: OPENAI_API_KEY not found in .env"
        echo "      You'll need to set it in your deployment platform"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo "   ℹ️  .env file missing (okay if using platform env vars)"
fi
echo ""

# 3. Check Dockerfile
echo "3️⃣  Checking Docker configuration..."
if [ -f Dockerfile ]; then
    echo "   ✅ Dockerfile exists"
    
    # Check if it has the model downloads
    if grep -q "groundingdino_swint_ogc.pth" Dockerfile && grep -q "sam_vit_b_01ec64.pth" Dockerfile; then
        echo "   ✅ Model downloads configured in Dockerfile"
    else
        echo "   ⚠️  WARNING: Model downloads might be missing from Dockerfile"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo "   ❌ ERROR: Dockerfile missing!"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# 4. Check deployment configs
echo "4️⃣  Checking deployment configurations..."
CONFIGS=0
[ -f railway.toml ] && echo "   ✅ railway.toml" && CONFIGS=$((CONFIGS + 1))
[ -f render.yaml ] && echo "   ✅ render.yaml" && CONFIGS=$((CONFIGS + 1))
[ -f Procfile ] && echo "   ✅ Procfile" && CONFIGS=$((CONFIGS + 1))

if [ $CONFIGS -eq 0 ]; then
    echo "   ❌ ERROR: No deployment configs found!"
    ERRORS=$((ERRORS + 1))
else
    echo "   ✅ Found $CONFIGS deployment config(s)"
fi
echo ""

# 5. Check backend files
echo "5️⃣  Checking backend files..."
REQUIRED_FILES=("backend/app.py" "backend/grounded_sam_service.py" "backend/requirements.txt")
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ ERROR: Missing $file"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check for health endpoint
if grep -q "def health_check" backend/app.py; then
    echo "   ✅ Health endpoint configured"
else
    echo "   ⚠️  WARNING: Health endpoint might be missing"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# 6. Check frontend
echo "6️⃣  Checking frontend..."
if [ -d frontend ]; then
    echo "   ✅ Frontend directory exists"
    
    if [ -f frontend/package.json ]; then
        echo "   ✅ package.json exists"
    else
        echo "   ❌ ERROR: frontend/package.json missing"
        ERRORS=$((ERRORS + 1))
    fi
    
    # Check for API URL configuration
    if [ -f frontend/src/components/api.ts ]; then
        echo "   ✅ API client exists"
        
        if grep -q "localhost:5001" frontend/src/components/api.ts; then
            echo "   ⚠️  WARNING: API URL still points to localhost"
            echo "      Update this after backend is deployed!"
            WARNINGS=$((WARNINGS + 1))
        fi
    else
        echo "   ⚠️  WARNING: API client not found"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo "   ❌ ERROR: Frontend directory missing"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# 7. Check model files (local only)
echo "7️⃣  Checking model files (for local testing)..."
if [ -f backend/models/grounded_sam/groundingdino_swint_ogc.pth ]; then
    echo "   ✅ Grounding DINO model present"
else
    echo "   ⚠️  Model will be downloaded during Docker build"
fi

if [ -f backend/models/grounded_sam/sam_vit_b_01ec64.pth ]; then
    echo "   ✅ SAM model present"
else
    echo "   ⚠️  Model will be downloaded during Docker build"
fi
echo ""

# Summary
echo "============================"
echo "📊 SUMMARY"
echo "============================"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✅ ALL CHECKS PASSED!"
    echo ""
    echo "🚀 Ready to deploy!"
    echo ""
    echo "Next steps:"
    echo "1. Test locally:        ./test-deployment.sh"
    echo "2. Push to GitHub:      git push origin main"
    echo "3. Deploy on Railway:   https://railway.app"
    echo ""
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "⚠️  $WARNINGS WARNING(S) - Review above"
    echo ""
    echo "You can still deploy, but review warnings first."
    echo ""
    echo "Test before deploying:"
    echo "   ./test-deployment.sh"
    echo ""
    exit 0
else
    echo "❌ $ERRORS ERROR(S) and $WARNINGS WARNING(S)"
    echo ""
    echo "Fix errors above before deploying!"
    echo ""
    exit 1
fi
