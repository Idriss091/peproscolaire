"""
Configuration Django pour les tests
"""

from .settings import *

# Base de données pour les tests
import os
import dj_database_url

# Utiliser PostgreSQL si DATABASE_URL est défini (CI), sinon SQLite
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }

# Désactiver les migrations pour les tests locaux uniquement
# En CI, nous voulons tester avec une vraie base de données
if not os.environ.get('CI') and not DATABASE_URL:
    class DisableMigrations:
        def __contains__(self, item):
            return True
        
        def __getitem__(self, item):
            return None

    MIGRATION_MODULES = DisableMigrations()

# Configuration spécifique aux tests
DEBUG = False
TESTING = True
SECRET_KEY = 'test-secret-key-for-ci'

# Désactiver le cache pour les tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Désactiver Celery pour les tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Configuration de logging pour les tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
    },
}

# Désactiver les emails pour les tests
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'