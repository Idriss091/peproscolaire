"""
URLs pour l'application dossiers élèves
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StudentRecordViewSet, GuardianViewSet,
    MedicalRecordViewSet, StudentDocumentViewSet,
    DisciplinaryRecordViewSet, OrientationRecordViewSet,
    parent_dashboard, search_students
)

router = DefaultRouter()
router.register(r'records', StudentRecordViewSet, basename='student-record')
router.register(r'guardians', GuardianViewSet, basename='guardian')
router.register(r'medical', MedicalRecordViewSet, basename='medical-record')
router.register(r'documents', StudentDocumentViewSet, basename='student-document')
router.register(r'disciplinary', DisciplinaryRecordViewSet, basename='disciplinary')
router.register(r'orientation', OrientationRecordViewSet, basename='orientation')

app_name = 'student_records'

urlpatterns = [
    path('', include(router.urls)),
    path('parent-dashboard/', parent_dashboard, name='parent-dashboard'),
    path('search/', search_students, name='search-students'),
]