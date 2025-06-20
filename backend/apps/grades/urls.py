"""
URLs pour l'application notes et évaluations
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EvaluationTypeViewSet, GradingPeriodViewSet,
    EvaluationViewSet, SubjectAverageViewSet,
    GeneralAverageViewSet, CompetenceViewSet,
    CompetenceEvaluationViewSet, student_report_card
)

router = DefaultRouter()
router.register(r'evaluation-types', EvaluationTypeViewSet, basename='evaluation-type')
router.register(r'grading-periods', GradingPeriodViewSet, basename='grading-period')
router.register(r'evaluations', EvaluationViewSet, basename='evaluation')
router.register(r'subject-averages', SubjectAverageViewSet, basename='subject-average')
router.register(r'general-averages', GeneralAverageViewSet, basename='general-average')
router.register(r'competences', CompetenceViewSet, basename='competence')
router.register(r'competence-evaluations', CompetenceEvaluationViewSet, basename='competence-evaluation')

app_name = 'grades'

urlpatterns = [
    path('', include(router.urls)),
    path('report-card/', student_report_card, name='report-card'),
]