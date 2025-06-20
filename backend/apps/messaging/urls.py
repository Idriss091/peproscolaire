"""
URLs pour l'application messagerie
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MessageViewSet, MessageTemplateViewSet, MessageGroupViewSet,
    email_forwarding_settings, notification_preferences,
    message_statistics
)

router = DefaultRouter()
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'templates', MessageTemplateViewSet, basename='template')
router.register(r'groups', MessageGroupViewSet, basename='group')

app_name = 'messaging'

urlpatterns = [
    path('', include(router.urls)),
    path('settings/email-forwarding/', email_forwarding_settings, name='email-forwarding'),
    path('settings/notifications/', notification_preferences, name='notifications'),
    path('statistics/', message_statistics, name='statistics'),
]