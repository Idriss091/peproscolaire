"""
Configuration Django pour PeproScolaire
Gère les paramètres de développement et production
"""

from pathlib import Path
from datetime import timedelta
import environ
import os

# Initialisation des variables d'environnement
env = environ.Env(
    DEBUG=(bool, False)
)

# Répertoire de base du projet
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Configuration de sécurité
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost'])

# Applications installées
INSTALLED_APPS = [
    # Apps Django par défaut
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Apps tierces
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_yasg',
    
    # Apps locales
    'apps.tenants',  # IMPORTANT: Doit être en premier pour le multi-tenant
    'apps.authentication',
    'apps.core',
    'apps.schools',
    'apps.timetable',
    'apps.attendance',
    'apps.grades',
    'apps.homework',
    'apps.messaging',
    'apps.student_records',
    'apps.ai_analytics',
    'apps.chatbot',
    'apps.internship_management',
]

# Taille maximale des fichiers uploadés (en bytes)
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB

# Configuration des types de fichiers autorisés
ALLOWED_FILE_EXTENSIONS = [
    'pdf', 'doc', 'docx', 'odt',
    'xls', 'xlsx', 'ods',
    'ppt', 'pptx', 'odp',
    'jpg', 'jpeg', 'png', 'gif',
    'mp4', 'avi', 'mov',
    'zip', 'rar'
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.tenants.middleware.TenantMiddleware',  # Middleware multi-tenant
    'apps.tenants.middleware.TenantSecurityMiddleware',  # Sécurité multi-tenant
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# Configuration des templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.tenants.context_processors.tenant_context',  # Contexte tenant
                'apps.tenants.context_processors.tenant_urls',  # URLs tenant
                'apps.tenants.context_processors.tenant_features',  # Fonctionnalités tenant
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Base de données PostgreSQL
DATABASES = {
    'default': env.db()
}

# Router de base de données pour le multi-tenant
DATABASE_ROUTERS = [
    'apps.tenants.db_router.TenantDatabaseRouter',
]

# Redis pour le cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Validation des mots de passe
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalisation
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

# Fichiers statiques et media
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'

# Stockage personnalisé pour le multi-tenant
DEFAULT_FILE_STORAGE = 'apps.tenants.storage.TenantFileSystemStorage'

# Modèle utilisateur personnalisé
AUTH_USER_MODEL = 'authentication.User'

# Configuration REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# Configuration JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=env.int('JWT_ACCESS_TOKEN_LIFETIME', default=60)),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=env.int('JWT_REFRESH_TOKEN_LIFETIME', default=1440)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# Configuration CORS
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])
CORS_ALLOW_CREDENTIALS = True

# Ajouter le support des sous-domaines pour CORS
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://\w+\.peproscolaire\.fr$",  # Tous les sous-domaines de peproscolaire.fr
]

# Configuration Email
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = 'PeproScolaire <noreply@peproscolaire.fr>'

# Clé primaire par défaut
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Configuration Celery pour les tâches asynchrones
CELERY_BROKER_URL = env('REDIS_URL', default='redis://localhost:6379/1')
CELERY_RESULT_BACKEND = env('REDIS_URL', default='redis://localhost:6379/1')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Tâches périodiques
try:
    from celery.schedules import crontab
except ImportError:
    # Celery n'est pas installé, utiliser une configuration par défaut
    crontab = lambda **kwargs: None

CELERY_BEAT_SCHEDULE = {
    'check-attendance-alerts': {
        'task': 'apps.attendance.tasks.check_attendance_alerts',
        'schedule': crontab(hour=16, minute=0),  # Tous les jours à 16h
    },
    'generate-monthly-report': {
        'task': 'apps.attendance.tasks.generate_monthly_attendance_report',
        'schedule': crontab(day_of_month=1, hour=8, minute=0),  # Le 1er de chaque mois
    },
    'auto-justify-absences': {
        'task': 'apps.attendance.tasks.auto_justify_medical_absences',
        'schedule': crontab(hour=9, minute=0),  # Tous les jours à 9h
    },
}

# Configuration Multi-Tenant
TENANT_APPS = [
    'apps.authentication',
    'apps.schools',
    'apps.timetable',
    'apps.attendance',
    'apps.grades',
    'apps.homework',
    'apps.messaging',
    'apps.student_records',
    'apps.ai_analytics',
    'apps.core',
]

SHARED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_yasg',
    'apps.tenants',  # L'app tenants est partagée
]

# Domaine principal (sans tenant)
PUBLIC_SCHEMA_NAME = 'public'