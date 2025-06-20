"""
Configuration de l'interface admin pour l'authentification
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile, PasswordResetToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin personnalisé pour le modèle User"""
    list_display = ['email', 'username', 'first_name', 'last_name', 'user_type', 'is_active', 'created_at']
    list_filter = ['user_type', 'is_active', 'is_verified', 'is_staff', 'created_at']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('Informations personnelles'), {'fields': ('first_name', 'last_name', 'phone_number')}),
        (_('Type et statut'), {'fields': ('user_type', 'is_verified')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Dates importantes'), {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'first_name', 'last_name', 'user_type'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin pour les profils utilisateur"""
    list_display = ['user', 'city', 'email_notifications', 'sms_notifications', 'created_at']
    list_filter = ['email_notifications', 'sms_notifications', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'city']
    raw_id_fields = ['user']


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """Admin pour les tokens de réinitialisation"""
    list_display = ['user', 'token', 'created_at', 'is_used']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__email', 'token']
    raw_id_fields = ['user']
    readonly_fields = ['token', 'created_at']