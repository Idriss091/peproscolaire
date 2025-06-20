"""
URLs pour l'application authentication
"""
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView
)
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    UserProfileView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    ChangePasswordView,
    verify_token,
    health_check
)

app_name = 'authentication'

urlpatterns = [
    # Health check
    path('health/', health_check, name='health'),
    
    # Inscription et connexion
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Gestion du profil
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # Gestion des mots de passe
    path('password/reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('password/change/', ChangePasswordView.as_view(), name='password-change'),
    
    # Tokens JWT
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token-verify'),
    path('verify/', verify_token, name='verify'),
]