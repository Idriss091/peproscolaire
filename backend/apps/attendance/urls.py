"""
URLs pour l'application vie scolaire
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AttendanceViewSet, AbsencePeriodViewSet,
    SanctionViewSet, StudentBehaviorViewSet,
    AttendanceAlertViewSet
)

router = DefaultRouter()
router.register(r'attendances', AttendanceViewSet, basename='attendance')
router.register(r'absence-periods', AbsencePeriodViewSet, basename='absence-period')
router.register(r'sanctions', SanctionViewSet, basename='sanction')
router.register(r'behaviors', StudentBehaviorViewSet, basename='behavior')
router.register(r'alerts', AttendanceAlertViewSet, basename='alert')

app_name = 'attendance'

urlpatterns = [
    path('', include(router.urls)),
]