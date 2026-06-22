from .base import *
from datetime import timedelta

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS += [
    'django_extensions',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB'),      
        'USER': config('POSTGRES_USER'),    
        'PASSWORD': config('POSTGRES_PASSWORD'),
        'HOST': config('DB_HOST', default='db'),
        'PORT': config('DB_PORT', default=5432),
        'CONN_MAX_AGE': config('DB_CONN_MAX_AGE', default=600, cast=int),
    }
}
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

CELERY_BROKER_URL = 'redis://redis:6379/1'
CELERY_RESULT_BACKEND = 'redis://redis:6379/2'
CELERY_ALWAYS_EAGER = False

CHANNEL_LAYERS['default']['CONFIG']['hosts'] = [('redis', 6379)]

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8000',
    'http://frontend:3000',
    'http://django:8000',
]

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8000',
    'http://frontend:3000',
]

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'] = timedelta(days=7)


STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage"
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# LOGGING['loggers']['django']['level'] = 'INFO'
# LOGGING['loggers']['apps']['level'] = 'INFO'