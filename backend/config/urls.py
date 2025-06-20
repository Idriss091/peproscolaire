"""
Configuration des URLs principales du projet
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Configuration de la documentation API
schema_view = get_schema_view(
    openapi.Info(
        title="PeproScolaire API",
        default_version='v1',
        description="API pour la gestion scolaire intelligente",
        terms_of_service="https://peproscolaire.fr/terms/",
        contact=openapi.Contact(email="contact@peproscolaire.fr"),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Admin Django
    path('admin/', admin.site.urls),
    
    # API v1 - Modules principaux
    path('api/v1/auth/', include('apps.authentication.urls')),
    path('api/v1/schools/', include('apps.schools.urls')),
    path('api/v1/timetable/', include('apps.timetable.urls')),
    path('api/v1/attendance/', include('apps.attendance.urls')),
    path('api/v1/grades/', include('apps.grades.urls')),
    path('api/v1/homework/', include('apps.homework.urls')),
    path('api/v1/messaging/', include('apps.messaging.urls')),
    path('api/v1/student-records/', include('apps.student_records.urls')),
    path('api/v1/ai-analytics/', include('apps.ai_analytics.urls')),
    path('api/v1/chatbot/', include('apps.chatbot.urls')),
    path('api/v1/internships/', include('apps.internship_management.urls')),
    
    # API Multi-tenant (accessible uniquement aux super-admins)
    path('api/v1/', include('apps.tenants.urls')),
    
    # Documentation API
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Servir les fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)