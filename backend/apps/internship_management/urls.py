from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CompanyViewSet,
    InternshipOfferViewSet,
    InternshipApplicationViewSet,
    InternshipViewSet,
    InternshipVisitViewSet,
    InternshipEvaluationViewSet,
    InternshipStatsViewSet
)

router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='internship-companies')
router.register(r'offers', InternshipOfferViewSet, basename='internship-offers')
router.register(r'applications', InternshipApplicationViewSet, basename='internship-applications')
router.register(r'internships', InternshipViewSet, basename='internships')
router.register(r'visits', InternshipVisitViewSet, basename='internship-visits')
router.register(r'evaluations', InternshipEvaluationViewSet, basename='internship-evaluations')
router.register(r'stats', InternshipStatsViewSet, basename='internship-stats')

app_name = 'internship_management'

urlpatterns = [
    path('', include(router.urls)),
]