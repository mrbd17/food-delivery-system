from datetime import timedelta

from .base import *

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "*.local"]

INSTALLED_APPS += [
    "django_extensions",
    "silk",
]

MIDDLEWARE.insert(3, "silk.middleware.SilkyMiddleware")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST"),
        "PORT": config("DB_PORT", cast=int),
        "CONN_MAX_AGE": int(config("DB_CONN_MAX_AGE", 600)),
        "OPTIONS": {
            "connect_timeout": 10,
            "application_name": "food_delivery",
        },
    }
}
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

CELERY_BROKER_URL = "redis://127.0.0.1:6379/1"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/2"
CELERY_ALWAYS_EAGER = True

CHANNEL_LAYERS["default"]["CONFIG"]["hosts"] = [("127.0.0.1", 6379)]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5500",
    "http://localhost:8000",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:8000",
]

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
]

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] = timedelta(days=7)


STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# LOGGING['loggers']['django']['level'] = 'DEBUG'
# LOGGING['loggers']['apps']['level'] = 'DEBUG'

INTERNAL_IPS = ["127.0.0.1", "localhost"]
