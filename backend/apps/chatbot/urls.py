from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ChatbotConversationViewSet,
    ChatbotMessageViewSet,
    ChatbotKnowledgeBaseViewSet,
    ChatbotAnalyticsViewSet,
    ChatbotQuickActionsViewSet
)

router = DefaultRouter()
router.register(r'conversations', ChatbotConversationViewSet, basename='chatbot-conversations')
router.register(r'messages', ChatbotMessageViewSet, basename='chatbot-messages')
router.register(r'knowledge-base', ChatbotKnowledgeBaseViewSet, basename='chatbot-knowledge')
router.register(r'analytics', ChatbotAnalyticsViewSet, basename='chatbot-analytics')
router.register(r'actions', ChatbotQuickActionsViewSet, basename='chatbot-actions')

app_name = 'chatbot'

urlpatterns = [
    path('', include(router.urls)),
]