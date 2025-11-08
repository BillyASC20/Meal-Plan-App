#!/bin/bash
# Test deployment locally using Docker

echo "🧪 Testing Deployment Build Locally"
echo "==================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "Install from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Create .env with: OPENAI_API_KEY=your_key"
    exit 1
fi

# Load OPENAI_API_KEY from .env
export $(cat .env | grep OPENAI_API_KEY | xargs)

if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY not found in .env file!"
    exit 1
fi

echo "✅ Docker installed"
echo "✅ OPENAI_API_KEY found"
echo ""

# Stop any existing container
echo "🧹 Cleaning up existing containers..."
docker stop meal-plan-test 2>/dev/null
docker rm meal-plan-test 2>/dev/null

# Build the image
echo ""
echo "🔨 Building Docker image..."
echo "⏱️  This will take 10-15 minutes (downloads models)"
echo ""

if docker build -t meal-plan-backend-test .; then
    echo ""
    echo "✅ Build successful!"
else
    echo ""
    echo "❌ Build failed! Check errors above."
    exit 1
fi

# Run the container
echo ""
echo "🚀 Starting container..."
docker run -d \
    --name meal-plan-test \
    -p 5001:5001 \
    -e OPENAI_API_KEY="$OPENAI_API_KEY" \
    meal-plan-backend-test

# Wait for startup
echo ""
echo "⏳ Waiting for service to start..."
echo "   (Models need to load, this takes ~30 seconds)"

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

# Test health endpoint
echo ""
echo "🧪 Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:5001/health)
echo "Response: $HEALTH_RESPONSE"

if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "✅ Health check passed!"
else
    echo "❌ Health check failed!"
    echo ""
    echo "📋 Container logs:"
    docker logs meal-plan-test
    exit 1
fi

# Show container info
echo ""
echo "📊 Container Info:"
docker ps | grep meal-plan-test

echo ""
echo "=================================="
echo "✅ DEPLOYMENT TEST SUCCESSFUL!"
echo "=================================="
echo ""
echo "Your app works in Docker and will work when deployed!"
echo ""
echo "💡 Useful commands:"
echo "   View logs:    docker logs meal-plan-test"
echo "   Stop:         docker stop meal-plan-test"
echo "   Remove:       docker rm meal-plan-test"
echo "   Test API:     curl http://localhost:5001/health"
echo ""
echo "🧹 To cleanup when done:"
echo "   docker stop meal-plan-test && docker rm meal-plan-test"
