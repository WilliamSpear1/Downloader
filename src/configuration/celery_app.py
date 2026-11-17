from celery import Celery

from .celery_conf import Config

"""
Create and configure the Celery application instance for async task processing.

Returns:
    A configured Celery app connected to the Redis broker.
"""
def make_celery_app() -> Celery:
    app = Celery("downloader")
    app.config_from_object(Config)

    return app

# Create a single shared app instance
celery_app = make_celery_app()