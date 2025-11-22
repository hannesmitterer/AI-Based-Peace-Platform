#!/bin/bash

# ALO-001 Backend Verification Script
# This script verifies the backend implementation

echo "======================================"
echo "ALO-001 Backend Verification"
echo "======================================"
echo ""

# Check if server is running
echo "1. Testing health check endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8080/health)
if [ $? -eq 0 ]; then
    echo "✓ Health check passed"
    echo "  Response: $HEALTH_RESPONSE"
else
    echo "✗ Health check failed - is the server running?"
    exit 1
fi
echo ""

# Test authentication requirement
echo "2. Testing authentication requirement (should fail without token)..."
AUTH_RESPONSE=$(curl -s http://localhost:8080/sfi)
if echo "$AUTH_RESPONSE" | grep -q "Missing or invalid Authorization header"; then
    echo "✓ Authentication is properly enforced"
    echo "  Response: $AUTH_RESPONSE"
else
    echo "✗ Authentication check failed"
    echo "  Response: $AUTH_RESPONSE"
    exit 1
fi
echo ""

# Test rate limiting
echo "3. Testing rate limiting headers..."
RATE_LIMIT_HEADERS=$(curl -sI http://localhost:8080/health | grep -i RateLimit)
if [ -n "$RATE_LIMIT_HEADERS" ]; then
    echo "✓ Rate limiting is active"
    echo "$RATE_LIMIT_HEADERS"
else
    echo "✗ Rate limiting headers not found"
    exit 1
fi
echo ""

# Test CORS headers
echo "4. Testing CORS configuration..."
CORS_HEADER=$(curl -sI http://localhost:8080/health | grep -i "Access-Control-Allow-Origin")
if [ -n "$CORS_HEADER" ]; then
    echo "✓ CORS is configured"
    echo "  $CORS_HEADER"
else
    echo "✗ CORS headers not found"
    exit 1
fi
echo ""

echo "======================================"
echo "All backend checks passed! ✓"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Configure Google OAuth Client ID in .env and public/pbl-001/index.html"
echo "2. Deploy the backend to your server"
echo "3. Update CORS_ALLOW_ORIGIN in .env to your production domain"
echo "4. Test with the frontend at public/pbl-001/index.html"
echo ""
