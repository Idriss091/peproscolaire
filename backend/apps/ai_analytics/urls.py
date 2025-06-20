"""
URLs pour le module d'analyse IA et détection des risques
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RiskProfileViewSet,
    RiskIndicatorViewSet,
    InterventionPlanViewSet,
    InterventionActionViewSet,
    AlertConfigurationViewSet,
    AlertViewSet,
    trigger_risk_analysis,
    risk_dashboard,
    student_risk_history,
    class_risk_report,
    bulk_risk_analysis,
    risk_statistics,
    # Nouveaux endpoints IA
    generate_appreciation,
    generate_multiple_appreciations,
    train_ai_model,
    ai_model_status,
    predict_student_risk,
    ai_dashboard_metrics
)

# Router pour les ViewSets
router = DefaultRouter()
router.register(r'risk-profiles', RiskProfileViewSet, basename='risk-profiles')
router.register(r'risk-indicators', RiskIndicatorViewSet, basename='risk-indicators')
router.register(r'intervention-plans', InterventionPlanViewSet, basename='intervention-plans')
router.register(r'intervention-actions', InterventionActionViewSet, basename='intervention-actions')
router.register(r'alert-configurations', AlertConfigurationViewSet, basename='alert-configurations')
router.register(r'alerts', AlertViewSet, basename='alerts')

urlpatterns = [
    # Routes du router
    path('', include(router.urls)),
    
    # Endpoints spéciaux
    path('analysis/trigger/', trigger_risk_analysis, name='trigger-risk-analysis'),
    path('dashboard/', risk_dashboard, name='risk-dashboard'),
    path('analysis/bulk/', bulk_risk_analysis, name='bulk-risk-analysis'),
    path('statistics/', risk_statistics, name='risk-statistics'),
    
    # Endpoints pour l'historique et rapports
    path('students/<uuid:student_id>/history/', student_risk_history, name='student-risk-history'),
    path('classes/<uuid:class_id>/report/', class_risk_report, name='class-risk-report'),
    
    # Nouveaux endpoints IA
    path('ai/appreciation/generate/', generate_appreciation, name='generate-appreciation'),
    path('ai/appreciation/generate-multiple/', generate_multiple_appreciations, name='generate-multiple-appreciations'),
    path('ai/model/train/', train_ai_model, name='train-ai-model'),
    path('ai/model/status/', ai_model_status, name='ai-model-status'),
    path('ai/prediction/risk/', predict_student_risk, name='predict-student-risk'),
    path('ai/dashboard/metrics/', ai_dashboard_metrics, name='ai-dashboard-metrics'),
]

app_name = 'ai_analytics'