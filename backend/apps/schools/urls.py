"""
URLs pour le module schools
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SchoolViewSet, AcademicYearViewSet, LevelViewSet,
    ClassViewSet, StudentClassEnrollmentViewSet
)

router = DefaultRouter()
router.register(r'schools', SchoolViewSet)
router.register(r'academic-years', AcademicYearViewSet)
router.register(r'levels', LevelViewSet)
router.register(r'classes', ClassViewSet)
router.register(r'enrollments', StudentClassEnrollmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]