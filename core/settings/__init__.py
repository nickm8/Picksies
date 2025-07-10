# core/settings/__init__.py
"""
Django settings module selector
"""
import os

# Determine which settings to use based on environment
DJANGO_SETTINGS_MODULE = os.getenv('DJANGO_SETTINGS_MODULE', 'core.settings.development')

if 'production' in DJANGO_SETTINGS_MODULE:
    from .production import *
elif 'development' in DJANGO_SETTINGS_MODULE:
    from .development import *
else:
    from .base import *
