from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import google.generativeai as genai
import json
import os
import re

from app.models.models import Question
from app.schemas.schemas import QuestionCreate, QualityMetrics

class QuestionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        api_key = os.getenv("GEMINI_API_KEY", "AIzaSyDGswqDT4wQw_bd4WZtIgYAawRDZ0Gisn8")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    async def create_question(self, question_data: QuestionCreate) -> Question:
        """Create a new question"""
        question = Question(
            text=question_data.text,
            options=question_data.options,
            correct_answer=question_data.correct_answer,
            explanation=question_data.explanation,
            topic=question_data.topic,
            difficulty=question_data.difficulty,
            source_model=question_data.source_model
        )
        self.db.add(question)
        await self.db.commit()
        await self.db.refresh(question)
        return question
    
    async def generate_question(self, topic: str, difficulty: str) -> tuple[Question, QualityMetrics]:
        """Generate a question using Gemini AI"""
        prompt = f"""Generate a multiple choice quiz question about {topic} at {difficulty} difficulty level.

Return a JSON object with this exact structure:
{{
    "text": "The question text",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0,
    "explanation": "Why this answer is correct",
    "quality_metrics": {{
        "readability_score": 0.85,
        "factual_confidence": 0.90,
        "distractor_quality": 0.80,
        "topic_alignment": 0.95,
        "difficulty_match": 0.85
    }}
}}

The correct_answer should be the index (0-3) of the correct option.
Ensure quality_metrics values are between 0 and 1.
Return only valid JSON, no additional text."""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up response
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            data = json.loads(response_text)
            
            question = Question(
                text=data["text"],
                options=data["options"],
                correct_answer=data["correct_answer"],
                explanation=data.get("explanation", ""),
                topic=topic,
                difficulty=difficulty,
                source_model="gemini-2.0-flash"
            )
            self.db.add(question)
            await self.db.commit()
            await self.db.refresh(question)
            
            metrics = QualityMetrics(**data.get("quality_metrics", {
                "readability_score": 0.8,
                "factual_confidence": 0.85,
                "distractor_quality": 0.75,
                "topic_alignment": 0.9,
                "difficulty_match": 0.8
            }))
            
            return question, metrics
            
        except Exception as e:
            raise ValueError(f"Failed to generate question: {str(e)}")
    
    async def regenerate_with_feedback(
        self, 
        question_id: str, 
        feedback: str
    ) -> tuple[Question, QualityMetrics]:
        """Regenerate question incorporating human feedback"""
        original = await self.get_question(question_id)
        if not original:
            raise ValueError("Original question not found")
        
        prompt = f"""The following quiz question needs improvement based on this feedback:
"{feedback}"

Original question:
{original.text}

Options: {json.dumps(original.options)}
Topic: {original.topic}
Difficulty: {original.difficulty}

Generate an improved version addressing the feedback.
Return a JSON object with this exact structure:
{{
    "text": "The improved question text",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0,
    "explanation": "Why this answer is correct",
    "quality_metrics": {{
        "readability_score": 0.85,
        "factual_confidence": 0.90,
        "distractor_quality": 0.80,
        "topic_alignment": 0.95,
        "difficulty_match": 0.85
    }}
}}

Return only valid JSON, no additional text."""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            data = json.loads(response_text)
            
            question = Question(
                text=data["text"],
                options=data["options"],
                correct_answer=data["correct_answer"],
                explanation=data.get("explanation", ""),
                topic=original.topic,
                difficulty=original.difficulty,
                source_model="gemini-2.0-flash"
            )
            self.db.add(question)
            await self.db.commit()
            await self.db.refresh(question)
            
            metrics = QualityMetrics(**data.get("quality_metrics", {
                "readability_score": 0.85,
                "factual_confidence": 0.88,
                "distractor_quality": 0.82,
                "topic_alignment": 0.92,
                "difficulty_match": 0.85
            }))
            
            return question, metrics
            
        except Exception as e:
            raise ValueError(f"Failed to regenerate question: {str(e)}")
    
    async def get_question(self, question_id: str) -> Optional[Question]:
        """Get question by ID"""
        query = select(Question).where(Question.id == question_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_approved_questions(self, topic: Optional[str] = None) -> List[Question]:
        """Get all approved questions, optionally filtered by topic"""
        from app.models.models import ContentCuration, CurationStatus
        
        query = select(Question).join(ContentCuration).where(
            ContentCuration.status == CurationStatus.APPROVED.value
        )
        if topic:
            query = query.where(Question.topic == topic)
        
        result = await self.db.execute(query)
        return result.scalars().all()
