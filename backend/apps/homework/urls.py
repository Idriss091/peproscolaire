"""
URLs pour l'application cahier de textes et devoirs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LessonContentViewSet, HomeworkTypeViewSet,
    HomeworkViewSet, HomeworkResourceViewSet,
    StudentWorkViewSet, HomeworkTemplateViewSet,
    WorkloadAnalysisViewSet, teacher_dashboard,
    suggest_homework
)

router = DefaultRouter()
router.register(r'lesson-contents', LessonContentViewSet, basename='lesson-content')
router.register(r'homework-types', HomeworkTypeViewSet, basename='homework-type')
router.register(r'homework', HomeworkViewSet, basename='homework')
router.register(r'resources', HomeworkResourceViewSet, basename='resource')
router.register(r'student-works', StudentWorkViewSet, basename='student-work')
router.register(r'templates', HomeworkTemplateViewSet, basename='template')
router.register(r'workload-analysis', WorkloadAnalysisViewSet, basename='workload-analysis')

app_name = 'homework'

urlpatterns = [
    path('', include(router.urls)),
    path('teacher-dashboard/', teacher_dashboard, name='teacher-dashboard'),
    path('suggest-homework/', suggest_homework, name='suggest-homework'),
]