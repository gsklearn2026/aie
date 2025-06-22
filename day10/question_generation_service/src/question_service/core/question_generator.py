"""Core question generation logic with retry mechanism"""

import asyncio
import json
from datetime import datetime
from typing import List, Optional

import structlog

from ..providers.ai_provider import AIProvider
from .job_manager import JobManager

logger = structlog.get_logger()


class QuestionGenerator:
    """Handles AI-powered question generation with retry logic"""

    MAX_RETRIES = 3
    RETRY_DELAYS = [5, 15, 45]  # Exponential backoff in seconds

    def __init__(self, ai_provider: AIProvider, job_manager: JobManager):
        self.ai_provider = ai_provider
        self.job_manager = job_manager

    async def process_job(
        self, job_id: str, topic: str, count: int = 5, difficulty: str = "medium"
    ):
        """Process question generation job with retry logic"""
        logger.info("Processing job", job_id=job_id, topic=topic)

        await self.job_manager.update_job_status(job_id, "processing")

        retry_count = 0

        while retry_count <= self.MAX_RETRIES:
            try:
                # Generate questions
                questions = await self._generate_questions(topic, count, difficulty)

                # Store results
                await self.job_manager.update_job_status(
                    job_id,
                    "completed",
                    questions=questions,
                    question_count=len(questions),
                )

                logger.info(
                    "Job completed successfully", job_id=job_id, count=len(questions)
                )
                return

            except Exception as e:
                retry_count += 1
                error_msg = str(e)

                logger.error(
                    "Job processing failed",
                    job_id=job_id,
                    error=error_msg,
                    retry_count=retry_count,
                )

                await self.job_manager.increment_retry_count(job_id)

                if retry_count <= self.MAX_RETRIES:
                    delay = self.RETRY_DELAYS[
                        min(retry_count - 1, len(self.RETRY_DELAYS) - 1)
                    ]
                    await self.job_manager.schedule_retry(job_id, delay)
                    await asyncio.sleep(delay)
                else:
                    # Max retries exceeded
                    await self.job_manager.update_job_status(
                        job_id,
                        "failed",
                        error_message=error_msg,
                        retry_count=retry_count,
                    )
                    break

    async def _generate_questions(
        self, topic: str, count: int, difficulty: str
    ) -> List[dict]:
        """Generate questions using AI provider"""
        prompt = self._build_prompt(topic, count, difficulty)

        response = await self.ai_provider.generate_content(prompt)

        questions = self._parse_questions(response, topic, difficulty)

        if len(questions) < count:
            logger.warning(
                "Generated fewer questions than requested",
                expected=count,
                actual=len(questions),
            )

        return questions[:count]

    def _build_prompt(self, topic: str, count: int, difficulty: str) -> str:
        """Build AI prompt for question generation"""
        return f"""Generate {count} {difficulty} level questions about "{topic}".

Requirements:
- Questions should be clear and specific
- Appropriate for {difficulty} difficulty level
- Cover different aspects of the topic
- Return as JSON array with format: {{"question": "...", "type": "multiple_choice|short_answer|essay"}}

Please provide exactly {count} questions in valid JSON format.

Topic: {topic}
Count: {count}
Difficulty: {difficulty}

Generate the questions as a JSON array:"""

    def _parse_questions(
        self, response: str, topic: str, difficulty: str
    ) -> List[dict]:
        """Parse AI response into structured questions"""
        try:
            # Try to extract JSON from response
            response = response.strip()

            # Find JSON array in response
            start_idx = response.find("[")
            end_idx = response.rfind("]") + 1

            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                questions_data = json.loads(json_str)
            else:
                # Fallback: parse as lines
                lines = [line.strip() for line in response.split("\n") if line.strip()]
                questions_data = [
                    {"question": line, "type": "short_answer"} for line in lines[:10]
                ]

            # Format questions
            questions = []
            for i, q_data in enumerate(questions_data):
                if isinstance(q_data, str):
                    q_data = {"question": q_data, "type": "short_answer"}

                question = {
                    "id": f"q_{i+1}",
                    "question": q_data.get("question", "").strip(),
                    "type": q_data.get("type", "short_answer"),
                    "difficulty": difficulty,
                    "topic": topic,
                    "generated_at": datetime.utcnow().isoformat(),
                }

                if question["question"]:
                    questions.append(question)

            return questions

        except Exception as e:
            logger.error(
                "Failed to parse questions", error=str(e), response=response[:200]
            )
            raise ValueError(f"Failed to parse AI response: {e}")
