import google.generativeai as genai
import os
import json
from typing import Dict, List, Optional

class GoogleAIService:
    def __init__(self):
        """Initialize Google AI service with API key"""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def generate_question(self, category: str, difficulty: float, topic: Optional[str] = None) -> Dict:
        """Generate a question using Google AI based on category and difficulty"""
        try:
            # Create prompt based on difficulty and category
            difficulty_description = self._get_difficulty_description(difficulty)
            
            prompt = f"""
            Generate a multiple choice question for a quiz platform with the following specifications:
            
            Category: {category}
            Difficulty Level: {difficulty_description} (difficulty score: {difficulty})
            Topic: {topic if topic else 'General knowledge in the category'}
            
            Requirements:
            1. Create a clear, well-formatted question
            2. Provide 4 multiple choice options (A, B, C, D)
            3. Mark the correct answer clearly
            4. Make sure the difficulty matches the specified level
            5. Ensure the question is educational and engaging
            
            Format your response as JSON with the following structure:
            {{
                "content": "Your question here?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Correct option text",
                "difficulty_score": {difficulty},
                "category": "{category}",
                "explanation": "Brief explanation of why this is the correct answer"
            }}
            
            Only return the JSON response, no additional text.
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse the response
            try:
                # Extract JSON from the response
                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                question_data = json.loads(response_text.strip())
                return question_data
                
            except json.JSONDecodeError as e:
                # Fallback: try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    question_data = json.loads(json_match.group())
                    return question_data
                else:
                    raise ValueError(f"Could not parse JSON from AI response: {response_text}")
                    
        except Exception as e:
            raise Exception(f"Error generating question with Google AI: {str(e)}")
    
    def _get_difficulty_description(self, difficulty: float) -> str:
        """Convert difficulty score to human-readable description"""
        if difficulty <= 1.0:
            return "Very Easy"
        elif difficulty <= 2.0:
            return "Easy"
        elif difficulty <= 3.0:
            return "Medium"
        elif difficulty <= 4.0:
            return "Hard"
        elif difficulty <= 5.0:
            return "Very Hard"
        else:
            return "Expert"
    
    async def generate_adaptive_question(self, user_performance: Dict, category: str) -> Dict:
        """Generate a question adapted to user performance"""
        # Analyze user performance to determine optimal difficulty
        success_rate = user_performance.get('success_rate', 0.7)
        current_difficulty = user_performance.get('current_difficulty', 2.0)
        
        # Adjust difficulty based on success rate
        if success_rate > 0.8:
            # User is doing well, increase difficulty
            target_difficulty = min(5.0, current_difficulty + 0.5)
        elif success_rate < 0.4:
            # User is struggling, decrease difficulty
            target_difficulty = max(0.5, current_difficulty - 0.5)
        else:
            # User is in the sweet spot, maintain current difficulty
            target_difficulty = current_difficulty
        
        return await self.generate_question(category, target_difficulty) 