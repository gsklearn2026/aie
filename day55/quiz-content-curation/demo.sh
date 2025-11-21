#!/bin/bash

echo "=========================================="
echo "Content Curation System Demo"
echo "=========================================="

API_URL="http://localhost:8000"

# Wait for backend
echo "Waiting for backend..."
for i in {1..30}; do
    if curl -s "$API_URL/health" > /dev/null; then
        echo "Backend is ready!"
        break
    fi
    sleep 1
done

echo ""
echo "1. Generating sample questions..."
echo ""

# Generate questions
for topic in "Mathematics" "Science" "History"; do
    echo "Generating $topic question..."
    curl -s -X POST "$API_URL/api/questions/generate?topic=$topic&difficulty=medium" | python3 -m json.tool | head -20
    echo ""
done

echo "2. Checking curation queue..."
curl -s "$API_URL/api/curation/queue?status=pending" | python3 -m json.tool

echo ""
echo "3. Demonstrating review workflow..."

# Get first item from queue
CURATION_ID=$(curl -s "$API_URL/api/curation/queue?status=pending" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['items'][0]['id'] if data['items'] else '')")

if [ -n "$CURATION_ID" ]; then
    echo "Claiming item $CURATION_ID..."
    curl -s -X POST "$API_URL/api/curation/$CURATION_ID/claim" \
        -H "Content-Type: application/json" \
        -d '{"reviewer_id": "demo_admin"}' | python3 -m json.tool | head -10
    
    echo ""
    echo "Approving content..."
    curl -s -X POST "$API_URL/api/curation/$CURATION_ID/approve" \
        -H "Content-Type: application/json" \
        -d '{"reviewer_id": "demo_admin"}' | python3 -m json.tool | head -10
    
    echo ""
    echo "Checking audit logs..."
    curl -s "$API_URL/api/curation/$CURATION_ID/audit" | python3 -m json.tool
fi

echo ""
echo "4. Getting analytics..."
curl -s "$API_URL/api/analytics/curation?days=7" | python3 -m json.tool

echo ""
echo "=========================================="
echo "Demo Complete!"
echo ""
echo "Access the dashboard at: http://localhost:3000"
echo "API documentation at: http://localhost:8000/docs"
echo "=========================================="
