from .base import *
import ssl

DEBUG = False

ALLOWED_HOSTS = [h.strip() for h in config('ALLOWED_HOSTS', 'localhost').split(',')]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config('DB_NAME'),
        "USER": config('DB_USER'),
        "PASSWORD": config('DB_PASSWORD'),
        "HOST": config('DB_HOST'),
        "PORT": config('DB_PORT', cast=int),
        "CONN_MAX_AGE": int(config('DB_CONN_MAX_AGE', 600)),
        "OPTIONS": {
            "connect_timeout": 10,
            "application_name": "food_delivery",
        }
    }
}
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 10,
            'SOCKET_TIMEOUT': 10,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        }
    }
}

CELERY_BROKER_URL = config('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND')
CELERY_ALWAYS_EAGER = False

REDIS_HOST = config('REDIS_HOST', 'localhost')
REDIS_PORT = config('REDIS_PORT', '6379')
CHANNEL_LAYERS['default']['CONFIG']['hosts'] = [(REDIS_HOST, int(REDIS_PORT))]

CORS_ALLOWED_ORIGINS = [h.strip() for h in config('CORS_ALLOWED_ORIGINS', '').split(',') if h]
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [h.strip() for h in config('CSRF_TRUSTED_ORIGINS', '').split(',') if h]

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
    'script-src': ("'self'", "'unsafe-inline'"),
    'style-src': ("'self'", "'unsafe-inline'"),
    'img-src': ("'self'", "data:", "https:"),
    'font-src': ("'self'",),
}

SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
X_FRAME_OPTIONS = 'DENY'

MIDDLEWARE.insert(
    1,
    'whitenoise.middleware.WhiteNoiseMiddleware',
)

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage"
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# LOGGING['handlers']['file']['filename'] = '/var/log/django/app.log'
# LOGGING['loggers']['django']['level'] = 'WARNING'
# LOGGING['loggers']['apps']['level'] = 'INFO'
# LOGGING['loggers']['django']['handlers'] = ['file']
# LOGGING['loggers']['apps']['handlers'] = ['file']