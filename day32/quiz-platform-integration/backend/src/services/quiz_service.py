from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from models.database import Quiz, Question, User
from typing import List, Dict, Optional
import json
import google.generativeai as genai
import os

class QuizService:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-pro')

    async def create_quiz(self, db: AsyncSession, title: str, description: str, creator_id: int) -> Dict:
        quiz = Quiz(title=title, description=description, creator_id=creator_id)
        db.add(quiz)
        await db.flush()
        await db.refresh(quiz)
        return {
            "id": quiz.id,
            "title": quiz.title,
            "description": quiz.description,
            "creator_id": quiz.creator_id,
            "created_at": quiz.created_at.isoformat()
        }

    async def get_quiz(self, db: AsyncSession, quiz_id: int) -> Optional[Dict]:
        result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
        quiz = result.scalar_one_or_none()
        if not quiz:
            return None
        
        # Get questions
        questions_result = await db.execute(
            select(Question).where(Question.quiz_id == quiz_id)
        )
        questions = questions_result.scalars().all()
        
        return {
            "id": quiz.id,
            "title": quiz.title,
            "description": quiz.description,
            "creator_id": quiz.creator_id,
            "created_at": quiz.created_at.isoformat(),
            "questions": [
                {
                    "id": q.id,
                    "question_text": q.question_text,
                    "correct_answer": q.correct_answer,
                    "options": json.loads(q.options)
                } for q in questions
            ]
        }

    async def generate_questions(self, topic: str, count: int = 5) -> List[Dict]:
        prompt = f"""
        Generate {count} multiple choice questions about {topic}.
        Return as JSON array with this format:
        [{{"question": "Question text?", "options": ["A", "B", "C", "D"], "correct": "A"}}]
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Parse response (simplified for demo)
            questions_data = json.loads(response.text.strip())
            return questions_data
        except Exception as e:
            # Fallback questions for demo
            return [
                {
                    "question": f"Sample question about {topic}?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct": "Option A"
                }
            ]

    async def add_questions_to_quiz(self, db: AsyncSession, quiz_id: int, questions_data: List[Dict]):
        for q_data in questions_data:
            question = Question(
                quiz_id=quiz_id,
                question_text=q_data["question"],
                correct_answer=q_data["correct"],
                options=json.dumps(q_data["options"])
            )
            db.add(question)
        await db.commit()

    async def delete_quiz(self, db: AsyncSession, quiz_id: int) -> bool:
        # Delete questions first
        await db.execute(delete(Question).where(Question.quiz_id == quiz_id))
        # Delete quiz
        result = await db.execute(delete(Quiz).where(Quiz.id == quiz_id))
        await db.commit()
        return result.rowcount > 0
