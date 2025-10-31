import google.generativeai as genai
import os
import json
from typing import Dict, Any
import asyncio

class AIInsightsGenerator:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY", "your-gemini-api-key-here")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def generate_insights(self, quiz_record: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI insights for quiz record"""
        try:
            prompt = f"""
            Analyze this quiz performance data and provide insights:
            
            User Score: {quiz_record['score']}
            Total Questions: {quiz_record['total_questions']}
            Correct Answers: {quiz_record['correct_answers']}
            Time Taken: {quiz_record['time_taken']} seconds
            Difficulty Level: {quiz_record['difficulty_level']}
            Subject Area: {quiz_record['subject_area']}
            
            Provide a JSON response with:
            1. performance_category (excellent/good/needs_improvement)
            2. time_efficiency_rating (fast/average/slow)
            3. suggested_difficulty_adjustment (increase/maintain/decrease)
            4. key_insights (2-3 bullet points)
            5. improvement_recommendations (specific actionable advice)
            
            Return only valid JSON.
            """
            
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )
            
            # Parse AI response
            ai_data = json.loads(response.text)
            
            return {
                'ai_performance_category': ai_data.get('performance_category', 'unknown'),
                'ai_time_efficiency': ai_data.get('time_efficiency_rating', 'average'),
                'ai_difficulty_suggestion': ai_data.get('suggested_difficulty_adjustment', 'maintain'),
                'ai_insights': json.dumps(ai_data.get('key_insights', [])),
                'ai_recommendations': json.dumps(ai_data.get('improvement_recommendations', []))
            }
            
        except Exception as e:
            # Return default insights if AI fails
            return {
                'ai_performance_category': 'unknown',
                'ai_time_efficiency': 'average', 
                'ai_difficulty_suggestion': 'maintain',
                'ai_insights': '["AI analysis unavailable"]',
                'ai_recommendations': '["Continue practicing regularly"]'
            }
