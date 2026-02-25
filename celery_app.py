import os

from celery import Celery
from celery.schedules import crontab

from conf.celery_conf import Config


def make_celery_app():
    # Celery App initialization & configuration.
    app = Celery("downloader")
    app.config_from_object(Config)

    return app

# Create a single shared app instance
celery_app = make_celery_app()