"""
Permissions personnalisées pour la gestion des tenants
"""
from rest_framework import permissions


class IsSuperAdmin(permissions.BasePermission):
    """
    Permission qui vérifie que l'utilisateur est un super-administrateur
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'superadmin'
        )


class IsTenantAdmin(permissions.BasePermission):
    """
    Permission qui vérifie que l'utilisateur est un administrateur du tenant actuel
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Super-admin a tous les droits
        if request.user.user_type == 'superadmin':
            return True
        
        # Admin du tenant actuel
        if request.user.user_type == 'admin':
            # Vérifier que l'utilisateur appartient au tenant actuel
            if hasattr(request, 'tenant') and request.tenant:
                # Vérifier via l'école de l'utilisateur
                if hasattr(request.user, 'school_users'):
                    user_schools = request.user.school_users.filter(
                        school=request.tenant.school,
                        is_active=True
                    )
                    return user_schools.exists()
        
        return False


class IsTenantMember(permissions.BasePermission):
    """
    Permission qui vérifie que l'utilisateur appartient au tenant actuel
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Super-admin a accès à tout
        if request.user.user_type == 'superadmin':
            return True
        
        # Vérifier l'appartenance au tenant
        if hasattr(request, 'tenant') and request.tenant:
            if hasattr(request.user, 'school_users'):
                user_schools = request.user.school_users.filter(
                    school=request.tenant.school,
                    is_active=True
                )
                return user_schools.exists()
        
        return False


class CanAccessModule(permissions.BasePermission):
    """
    Permission qui vérifie que le module est activé pour le tenant
    """
    module_name = None  # À définir dans les sous-classes
    
    def has_permission(self, request, view):
        # D'abord vérifier l'authentification
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Super-admin a accès à tout
        if request.user.user_type == 'superadmin':
            return True
        
        # Vérifier que le module est activé pour le tenant
        if hasattr(request, 'tenant') and request.tenant:
            if self.module_name:
                return request.tenant.is_module_enabled(self.module_name)
        
        return True  # Par défaut, autoriser si pas de tenant


class CanAccessAIModule(CanAccessModule):
    """Permission pour accéder au module IA"""
    module_name = 'ai_analytics'


class CanAccessMessagingModule(CanAccessModule):
    """Permission pour accéder au module messagerie"""
    module_name = 'messaging'


class CanAccessAttendanceModule(CanAccessModule):
    """Permission pour accéder au module vie scolaire"""
    module_name = 'attendance'


class CanAccessGradesModule(CanAccessModule):
    """Permission pour accéder au module notes"""
    module_name = 'grades'


class CanAccessTimetableModule(CanAccessModule):
    """Permission pour accéder au module emploi du temps"""
    module_name = 'timetable'


class CanAccessHomeworkModule(CanAccessModule):
    """Permission pour accéder au module devoirs"""
    module_name = 'homework'