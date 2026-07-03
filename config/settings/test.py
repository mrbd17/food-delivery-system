import os
from .base import *

import tempfile

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # الـ colon = memory, not disk
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',  # معرّف الـ cache
        'TIMEOUT': 300,
    }
}

CELERY_BROKER_URL = 'memory://'  # In-memory broker (للـ testing)
CELERY_RESULT_BACKEND = 'cache+locmem://'  # Store results in cache
CELERY_TASK_ALWAYS_EAGER = True  # Run tasks synchronously
CELERY_TASK_EAGER_PROPAGATES = True  # Propagate exceptions from tasks

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'localhost'  # Dummy values
EMAIL_PORT = 1025
EMAIL_HOST_USER = 'test@example.com'  # Hardcoded fake values
EMAIL_HOST_PASSWORD = 'test-password'
EMAIL_USE_TLS = False


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': [],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}


ALLOWED_HOSTS = ['*']  # Accept any host في testing
DEBUG = False  # لكن DEBUG = False (تجنب information leaks في testing أيضاً)
SECRET_KEY = 'test-secret-key-only-for-ci-cd'  # Hardcoded safe


REDIS_URL = 'redis://localhost:6379/0'  # Hardcoded، لا يُستخدم فعلاً في testing
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0


AUTH_PASSWORD_VALIDATORS = []  # Disable password complexity في testing


MEDIA_ROOT = tempfile.mkdtemp()  # Temporary directory، يُحذف بعد tests
MEDIA_URL = '/media/'

STATIC_URL = '/static/'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'


FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB


FIXTURE_DIRS = ['tests/fixtures']  # Directory لـ test fixtures
TEST_RUNNER = 'pytest'


PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',  # Fast (لا تستخدم في production!)
]

CORS_ALLOWED_ORIGINS = ['http://localhost:3000', 'http://localhost:8000']


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',  # في-memory لـ testing
    }
}