# core/settings/development.py
"""
Development settings for Django Movie App
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False  # Changed to True for development

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*', 'picksies.app', 'www.picksies.app']

CSRF_TRUSTED_ORIGINS = [
    'https://picksies.app',
    'https://www.picksies.app',
    'https://localhost',
    'https://127.0.0.1',
    'http://localhost:8001',
    'http://127.0.0.1:8001',
]

# Development apps
INSTALLED_APPS += [
    'debug_toolbar',
]

# Add WhiteNoise for static files in development Docker environment
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Development middleware
MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Database for development (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'movie_app'),
        'USER': os.environ.get('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
        'HOST': os.environ.get('POSTGRES_HOST', 'db'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}

# Static files configuration for development
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Django Debug Toolbar
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Cache for development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Disable some security settings for development
SECURE_SSL_REDIRECT = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False