"""
URLs pour l'API de gestion des tenants
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TenantViewSet, CurrentTenantView

app_name = 'tenants'

# Router pour les ViewSets
router = DefaultRouter()
router.register(r'tenants', TenantViewSet, basename='tenant')
router.register(r'current-tenant', CurrentTenantView, basename='current-tenant')

urlpatterns = [
    path('', include(router.urls)),
]