import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("localhub")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

from common.sentry import init_sentry  # noqa: E402

init_sentry("worker")
