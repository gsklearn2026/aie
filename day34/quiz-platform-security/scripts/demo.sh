#!/bin/bash

echo "🎭 Running Security Testing Demo..."

# Check if services are running
if ! curl -s http://localhost:8000/api/health > /dev/null; then
    echo "❌ Backend is not running. Please start services first with ./scripts/start.sh"
    exit 1
fi

echo "🔐 Running authentication security tests..."
curl -X POST http://localhost:8000/api/security/test/authentication \
  -H "Content-Type: application/json" \
  -d '{
    "passwords": ["password123", "12345678", "Password123!", "weak"],
    "tokens": ["eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test"],
    "session_tokens": ["abcd1234567890abcd1234567890abcd"],
    "test_username": "testuser@example.com"
  }'

echo -e "\n🛡️ Running authorization security tests..."
curl -X POST http://localhost:8000/api/security/test/authorization \
  -H "Content-Type: application/json" \
  -d '[
    {"user_role": "student", "user_id": "user1", "target_user_id": "user2"},
    {"user_role": "teacher", "user_id": "teacher1", "target_user_id": "student1"},
    {"user_role": "admin", "user_id": "admin1", "target_user_id": "user1"}
  ]'

echo -e "\n🔍 Running vulnerability scan..."
curl -X POST http://localhost:8000/api/security/scan/vulnerabilities \
  -H "Content-Type: application/json" \
  -d '{"target_url": "http://localhost:8000"}'

echo -e "\n🚀 Running comprehensive security audit..."
AUDIT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/security/audit/run \
  -H "Content-Type: application/json" \
  -d '{
    "auth_test_data": {
      "passwords": ["password123", "Password123!"],
      "tokens": ["test_token"],
      "session_tokens": ["test_session"],
      "test_username": "demo_user"
    },
    "authz_scenarios": [
      {"user_role": "student", "user_id": "user1", "target_user_id": "user2"},
      {"user_role": "admin", "user_id": "admin1", "target_user_id": "user1"}
    ]
  }')

echo "Audit started: $AUDIT_RESPONSE"

# Extract audit ID and poll for results
AUDIT_ID=$(echo $AUDIT_RESPONSE | grep -o '"audit_id":"[^"]*"' | cut -d'"' -f4)

if [ ! -z "$AUDIT_ID" ]; then
    echo "⏳ Polling for audit results (ID: $AUDIT_ID)..."
    
    for i in {1..30}; do
        RESULT=$(curl -s http://localhost:8000/api/security/audit/$AUDIT_ID)
        STATUS=$(echo $RESULT | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
        
        if [ "$STATUS" = "completed" ]; then
            echo "✅ Audit completed!"
            echo "Results: $RESULT"
            break
        elif [ "$STATUS" = "failed" ]; then
            echo "❌ Audit failed!"
            echo "Error: $RESULT"
            break
        fi
        
        echo "⏳ Waiting for audit completion... ($i/30)"
        sleep 5
    done
fi

echo -e "\n📊 Checking dashboard metrics..."
curl -s http://localhost:8000/api/security/dashboard/metrics | jq '.'

echo -e "\n🎉 Demo completed! Check the dashboard at http://localhost:3000"
