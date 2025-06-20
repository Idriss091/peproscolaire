"""
Configuration des URLs minimale pour démarrage rapide
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Importer nos vues API temporaires
from api_auth_simple import login_api, current_user_api

urlpatterns = [
    # Admin Django
    path('admin/', admin.site.urls),
    
    # API endpoints temporaires pour tests
    path('api/v1/auth/login/', login_api, name='api_login'),
    path('api/v1/auth/me/', current_user_api, name='api_current_user'),
    
    # API de base (si les apps sont prêtes)
    # path('api/v1/schools/', include('apps.schools.urls')),
]

# Servir les fichiers média en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)