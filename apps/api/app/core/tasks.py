from app.core.celery_app import celery_app


@celery_app.task(name="foundation.ping")
def ping() -> str:
    """Fake task used only to prove the Celery/Redis/worker wiring works.

    Real workflow tasks arrive with the Workflow & Agent Engine (Fase 11).
    """
    return "pong"
