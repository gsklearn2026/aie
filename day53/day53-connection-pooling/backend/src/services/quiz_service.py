from pools.database_pool import get_db_pool
from pools.gemini_pool import get_gemini_pool
import json
import logging

logger = logging.getLogger(__name__)

class QuizService:
    @staticmethod
    def create_quiz_table():
        pool = get_db_pool()
        conn = None
        try:
            conn = pool.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quizzes (
                    id SERIAL PRIMARY KEY,
                    topic VARCHAR(255),
                    difficulty VARCHAR(50),
                    question TEXT,
                    options JSONB,
                    correct_answer VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            cursor.close()
            logger.info("✅ Quiz table created/verified")
        except Exception as e:
            logger.error(f"❌ Error creating table: {e}")
            raise
        finally:
            if conn:
                pool.return_connection(conn)
    
    @staticmethod
    def generate_and_store_quiz(topic: str, difficulty: str = "medium"):
        gemini_pool = get_gemini_pool()
        conn = None

        try:
            conn = gemini_pool.get_connection()

            prompt = f"""Create a {difficulty} multiple-choice quiz about {topic}.

Return ONLY valid JSON in this exact format (no markdown, no commentary):
{{
  "questions": [
    {{
      "question": "Question text?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A"
    }},
    ... exactly 5 total questions ...
  ]
}}

Every question must have exactly 4 distinct options and only one correct answer.
Each question must be unique and cover a different facet of {topic}.
Do not include explanations or additional fields."""

            response_text = conn.generate(prompt)
            response_text = QuizService._sanitize_response_text(response_text)
            quiz_payload = QuizService._parse_quiz_payload(response_text)
            processed_questions = QuizService._validate_and_normalize_questions(quiz_payload["questions"])

            db_pool = get_db_pool()
            db_conn = None

            try:
                db_conn = db_pool.get_connection()
                cursor = db_conn.cursor()

                cursor.execute("""
                    INSERT INTO quizzes (topic, difficulty, question, options, correct_answer)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    topic,
                    difficulty,
                    processed_questions[0]["question"],
                    json.dumps(processed_questions),
                    json.dumps([q["correct_answer"] for q in processed_questions])
                ))

                row = cursor.fetchone()
                quiz_id = row[0] if row else None
                db_conn.commit()
                cursor.close()

                return {
                    "id": quiz_id,
                    "topic": topic,
                    "difficulty": difficulty,
                    "questions": processed_questions
                }
            finally:
                if db_conn:
                    db_pool.return_connection(db_conn)

        finally:
            if conn:
                gemini_pool.return_connection(conn)
    
    @staticmethod
    def get_all_quizzes():
        pool = get_db_pool()
        conn = None

        try:
            conn = pool.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, topic, difficulty, question, options, correct_answer, created_at
                FROM quizzes
                ORDER BY created_at DESC
                LIMIT 50
            """)

            rows = cursor.fetchall()
            cursor.close()

            quizzes = []
            for row in rows:
                raw_questions = row[4]
                try:
                    questions = json.loads(raw_questions) if raw_questions else []
                except (TypeError, json.JSONDecodeError):
                    questions = []
                quizzes.append({
                    "id": row[0],
                    "topic": row[1],
                    "difficulty": row[2],
                    "question": row[3],
                    "questions": questions,
                    "created_at": row[6].isoformat() if hasattr(row[6], "isoformat") else row[6]
                })

            return quizzes

        finally:
            if conn:
                pool.return_connection(conn)

    @staticmethod
    def _sanitize_response_text(response_text: str) -> str:
        cleaned = response_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return cleaned.strip()

    @staticmethod
    def _parse_quiz_payload(response_text: str):
        data = json.loads(response_text)
        if isinstance(data, list):
            data = {"questions": data}
        if "questions" not in data or not isinstance(data["questions"], list):
            raise ValueError("Invalid quiz payload: missing questions array")
        return data

    @staticmethod
    def _validate_and_normalize_questions(questions):
        if not questions or len(questions) < 5:
            raise ValueError("Quiz must contain at least 5 questions")
        normalized = []
        seen_questions = set()
        for idx, question in enumerate(questions):
            if not isinstance(question, dict):
                raise ValueError(f"Question {idx + 1} is not an object")
            text = question.get("question")
            options = question.get("options")
            answer = question.get("correct_answer")
            if not text or not isinstance(text, str):
                raise ValueError(f"Question {idx + 1} missing text")
            canonical_text = text.strip()
            if canonical_text.lower() in seen_questions:
                raise ValueError(f"Question {idx + 1} duplicates another question")
            if not options or not isinstance(options, list) or len(options) != 4:
                raise ValueError(f"Question {idx + 1} must include exactly 4 options")
            if answer not in options:
                raise ValueError(f"Question {idx + 1} has invalid correct answer")
            normalized.append({
                "question": canonical_text,
                "options": [opt.strip() for opt in options],
                "correct_answer": answer.strip()
            })
            seen_questions.add(canonical_text.lower())
        return normalized[:5]
