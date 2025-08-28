from celery import current_task
from app.core.celery_app import celery_app
from app.services.ai_service import ai_service
from app.services.job_service import job_service
from app.core.database import SessionLocal
from app.models.job import JobStatus
import asyncio
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def generate_quiz_questions(self, job_id: str, topic: str, num_questions: int = 5, difficulty: str = "medium"):
    """Background task to generate quiz questions using AI"""
    
    async def _generate_quiz():
        async with SessionLocal() as session:
            try:
                # Update job status to processing
                await job_service.update_job_status(
                    session, job_id, JobStatus.PROCESSING
                )
                
                # Generate questions using AI service
                questions = await ai_service.generate_quiz_questions(
                    topic=topic,
                    num_questions=num_questions,
                    difficulty=difficulty
                )
                
                # Update job with results
                await job_service.update_job_status(
                    session, 
                    job_id, 
                    JobStatus.COMPLETED,
                    result_data={
                        "questions": questions,
                        "metadata": {
                            "topic": topic,
                            "num_questions": len(questions),
                            "difficulty": difficulty
                        }
                    }
                )
                
                logger.info(f"Successfully generated {len(questions)} questions for job {job_id}")
                return {"status": "success", "questions_generated": len(questions)}
                
            except Exception as e:
                logger.error(f"Error generating questions for job {job_id}: {str(e)}")
                
                # Update job with error
                await job_service.update_job_status(
                    session,
                    job_id,
                    JobStatus.FAILED,
                    error_message=str(e)
                )
                
                # Retry if we haven't exceeded max retries
                if self.request.retries < self.max_retries:
                    logger.info(f"Retrying job {job_id}, attempt {self.request.retries + 1}")
                    await job_service.update_job_status(
                        session, job_id, JobStatus.RETRYING
                    )
                    raise self.retry(countdown=60 * (2 ** self.request.retries))
                
                raise e
    
    # Run the async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_generate_quiz())
    finally:
        loop.close()

@celery_app.task(bind=True)
def process_batch_quiz(self, job_id: str, topics: list, num_questions_per_topic: int = 5):
    """Process multiple quiz generation requests in batch"""
    
    async def _process_batch():
        async with SessionLocal() as session:
            try:
                await job_service.update_job_status(
                    session, job_id, JobStatus.PROCESSING
                )
                
                all_questions = []
                for i, topic in enumerate(topics):
                    # Update progress
                    current_task.update_state(
                        state='PROGRESS',
                        meta={'current': i + 1, 'total': len(topics), 'status': f'Processing {topic}'}
                    )
                    
                    questions = await ai_service.generate_quiz_questions(
                        topic=topic,
                        num_questions=num_questions_per_topic
                    )
                    
                    all_questions.append({
                        "topic": topic,
                        "questions": questions
                    })
                
                await job_service.update_job_status(
                    session,
                    job_id,
                    JobStatus.COMPLETED,
                    result_data={
                        "batch_results": all_questions,
                        "total_topics": len(topics),
                        "total_questions": len(topics) * num_questions_per_topic
                    }
                )
                
                return {"status": "success", "topics_processed": len(topics)}
                
            except Exception as e:
                await job_service.update_job_status(
                    session, job_id, JobStatus.FAILED, error_message=str(e)
                )
                raise e
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_process_batch())
    finally:
        loop.close()
