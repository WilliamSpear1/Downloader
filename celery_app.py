import os

from celery import Celery
from celery.schedules import crontab


def make_celery_app():
    # Celery App initialization & configuration.
    app = Celery(
        "downloader",
        backend=os.environ['CELERY_RESULT_BACKEND'],
        broker=os.environ['CELERY_BROKER_URL']
    )

    app.conf.update(
        task_default_queue = "downloader_queue",
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True
    )

    return app

# Create a single shared app instance
celery_app = make_celery_app()