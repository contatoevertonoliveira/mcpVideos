from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "mcp_videos",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.core.tasks",
        "app.tasks.channel_sync",
        "app.tasks.channel_intelligence",
        "app.tasks.channel_dna",
        "app.tasks.channel_strategy",
        "app.tasks.opportunity_evaluation",
        "app.tasks.idea_generation",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)
