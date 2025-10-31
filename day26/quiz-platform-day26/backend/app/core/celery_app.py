from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "quiz_platform",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.ai_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_routes={
        "app.workers.ai_tasks.generate_quiz_questions": {"queue": "ai_generation"},
        "app.workers.ai_tasks.process_batch_quiz": {"queue": "batch_processing"},
    },
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
)
