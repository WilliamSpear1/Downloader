import os

class Config:
    broker_url = os.environ.get('CELERY_BROKER_URL')
    result_backend = os.environ.get('CELERY_RESULT_BACKEND')
    task_default_queue = 'downloader_queue'
    task_serializer = 'json'
    result_serializer = 'json'
    accept_content = ['json']
    timezone = 'UTC'
    enable_utc = True
    worker_prefetch_multiplier = 1
    task_acks_late = True
