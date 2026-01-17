import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = os.getenv("REDIS_PORT", "6379")
app.conf.broker_url = f"redis://{redis_host}:{redis_port}/0"

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
