"""
Configuration des URLs minimale pour démarrage rapide
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

# Importer nos vues API temporaires
from api_auth_simple import login_api, current_user_api
from api_data_simple import homework_list_api, grades_list_api, timetable_api, messages_list_api

def home_view(request):
    """Vue pour la page d'accueil"""
    return JsonResponse({
        'message': 'PeproScolaire Backend API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'admin': '/admin/',
            'auth_login': '/api/v1/auth/login/',
            'auth_me': '/api/v1/auth/me/',
        }
    })

urlpatterns = [
    # Page d'accueil
    path('', home_view, name='home'),
    
    # Admin Django
    path('admin/', admin.site.urls),
    
    # API endpoints temporaires pour tests
    path('api/v1/auth/login/', login_api, name='api_login'),
    path('api/v1/auth/me/', current_user_api, name='api_current_user'),
    
    # Endpoints de données temporaires
    path('api/v1/homework/', homework_list_api, name='api_homework'),
    path('api/v1/grades/', grades_list_api, name='api_grades'),
    path('api/v1/timetable/', timetable_api, name='api_timetable'),
    path('api/v1/messaging/messages/', messages_list_api, name='api_messages'),
    
    # API de base
    path('api/v1/auth/', include('apps.authentication.urls')),
    path('api/v1/schools/', include('apps.schools.urls')),
    path('api/v1/homework/', include('apps.homework.urls')),
    path('api/v1/timetable/', include('apps.timetable.urls')),
    path('api/v1/grades/', include('apps.grades.urls')),
    path('api/v1/attendance/', include('apps.attendance.urls')),
]

# Servir les fichiers média en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)