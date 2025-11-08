#!/bin/bash
# Quick deployment script

echo "🚀 Meal Plan App - Quick Deploy"
echo ""

# Check if git repo
if [ ! -d .git ]; then
    echo "❌ Not a git repository. Run: git init"
    exit 1
fi

# Check for uncommitted changes
if [[ -n $(git status -s) ]]; then
    echo "📝 You have uncommitted changes:"
    git status -s
    echo ""
    read -p "Commit and push? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .
        read -p "Commit message: " message
        git commit -m "$message"
        git push
        echo "✅ Changes pushed to GitHub"
    else
        echo "⏭️  Skipping commit"
    fi
else
    echo "✅ No uncommitted changes"
fi

echo ""
echo "📋 Deployment Options:"
echo ""
echo "1. Railway (Easiest)"
echo "   → Go to railway.app"
echo "   → New Project → Deploy from GitHub"
echo "   → Select this repo"
echo "   → Add env: OPENAI_API_KEY"
echo ""
echo "2. Render"
echo "   → Go to render.com"
echo "   → New → Blueprint"
echo "   → Connect this repo"
echo "   → Add env: OPENAI_API_KEY"
echo ""
echo "3. Docker (Self-host)"
echo "   → Run: docker build -t meal-plan-backend ."
echo "   → Run: docker run -p 5001:5001 -e OPENAI_API_KEY=key meal-plan-backend"
echo ""
echo "📖 Full guide: See DEPLOYMENT.md"
