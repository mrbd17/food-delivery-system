# config/settings/development.py
from .base import *

DEBUG = True

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage"
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    }
}

INSTALLED_APPS += [
    "django_extensions",
    "silk",
]

# MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
MIDDLEWARE.insert(3, "silk.middleware.SilkyMiddleware")

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "*"]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

CORS_ALLOW_CREDENTIALS = True

SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] = timedelta(days=7)  # أطول في dev

CELERY_ALWAYS_EAGER = True 

SESSION_COOKIE_SECURE = False

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
]

INTERNAL_IPS = ["127.0.0.1", "localhost"]

# LOGGING["loggers"]["django"]["level"] = "DEBUG"
# LOGGING["loggers"]["apps"]["level"] = "DEBUG"