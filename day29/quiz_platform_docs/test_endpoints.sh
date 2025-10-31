#!/bin/bash

echo "🧪 Testing Quiz Platform API Endpoints"
echo "======================================"

BASE_URL="http://localhost:5000"
API_URL="$BASE_URL/api/v1"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local method=$1
    local url=$2
    local data=$3
    local description=$4
    
    echo -e "\n${YELLOW}Testing: $description${NC}"
    echo "URL: $method $url"
    
    if [ -n "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method "$url" \
            -H "Content-Type: application/json" \
            -d "$data")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$url")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [[ $http_code =~ ^[23][0-9][0-9]$ ]]; then
        echo -e "${GREEN}✅ Success (HTTP $http_code)${NC}"
        echo "$body" | jq . 2>/dev/null || echo "$body"
    else
        echo -e "${RED}❌ Failed (HTTP $http_code)${NC}"
        echo "$body"
    fi
}

# 1. Health Check
test_endpoint "GET" "$BASE_URL/health" "" "Health Check"

# 2. Get All Quizzes
test_endpoint "GET" "$API_URL/quizzes/" "" "Get All Quizzes"

# 3. Create New Quiz
quiz_data='{
    "title": "API Testing Quiz",
    "description": "Test your API knowledge",
    "difficulty": "medium",
    "category": "Testing",
    "questions": [
        {
            "text": "What does REST stand for?",
            "options": ["Representational State Transfer", "Remote State Transfer", "Rapid State Transfer", "Resource State Transfer"],
            "correct_answer": "Representational State Transfer"
        }
    ]
}'
test_endpoint "POST" "$API_URL/quizzes/" "$quiz_data" "Create New Quiz"

# 4. Get Specific Quiz
test_endpoint "GET" "$API_URL/quizzes/quiz_1" "" "Get Specific Quiz"

# 5. Update Quiz
update_data='{
    "title": "Updated API Testing Quiz",
    "description": "Enhanced API knowledge test",
    "difficulty": "hard"
}'
test_endpoint "PUT" "$API_URL/quizzes/quiz_1" "$update_data" "Update Quiz"

# 6. Get All Users
test_endpoint "GET" "$API_URL/users/" "" "Get All Users"

# 7. Get Specific User
test_endpoint "GET" "$API_URL/users/user_1" "" "Get Specific User"

# 8. Get Quiz Results
test_endpoint "GET" "$API_URL/analytics/results" "" "Get Quiz Results"

# 9. Get Platform Statistics
test_endpoint "GET" "$API_URL/analytics/stats" "" "Get Platform Statistics"

# 10. Generate AI Questions
ai_data='{
    "topic": "Web Development",
    "difficulty": "medium",
    "count": 3
}'
test_endpoint "POST" "$API_URL/ai/generate-questions" "$ai_data" "Generate AI Questions"

# 11. Get Swagger JSON
test_endpoint "GET" "$BASE_URL/swagger.json" "" "Get Swagger JSON"

echo -e "\n${GREEN}🎉 All tests completed!${NC}"
echo -e "\n📚 Access the interactive documentation at:"
echo -e "   Swagger UI: http://localhost:3000"
echo -e "   API Docs: http://localhost:5000/docs/"

