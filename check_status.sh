#!/bin/bash
# Monitor backend logs to see what's happening during detection

echo "=========================================="
echo "🔍 DETECTION SYSTEM STATUS"
echo "=========================================="
echo ""

# Check if backend is running
if lsof -ti:5000 > /dev/null; then
    echo "✅ Backend: Running on port 5000"
else
    echo "❌ Backend: NOT running!"
    exit 1
fi

# Check if frontend is running  
if lsof -ti:3002 > /dev/null; then
    echo "✅ Frontend: Running on port 3002"
else
    echo "⚠️  Frontend: NOT running on port 3002"
fi

echo ""
echo "🌐 URLs:"
echo "   Frontend: http://localhost:3002"
echo "   Backend:  http://localhost:5000"
echo ""
echo "📝 Recent backend activity:"
echo "=========================================="
tail -30 /tmp/backend.log | grep -E "\[detect\]|\[vision_service\]|POST|GET" || echo "No recent activity"
echo "=========================================="
echo ""
echo "💡 Try uploading an image in the frontend now!"
echo "   Then run this script again to see the detection logs."
