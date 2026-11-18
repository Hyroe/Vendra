from .base import *  # noqa: F401,F403

DEBUG = False
SECRET_KEY = "test-secret-key-not-for-production"  # nosec B105
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

FAKE_PAYMENT_ENABLED = True
CELERY_TASK_ALWAYS_EAGER = True

from .base import REST_FRAMEWORK as BASE_REST_FRAMEWORK  # noqa: E402

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

REST_FRAMEWORK = {
    **BASE_REST_FRAMEWORK,
    "DEFAULT_THROTTLE_RATES": {
        "anon": "1000/min",
        "user": "1000/min",
        "login": "1000/min",
        "register": "1000/min",
    },
}
