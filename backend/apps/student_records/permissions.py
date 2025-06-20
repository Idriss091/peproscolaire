"""
Permissions personnalisées pour les dossiers élèves
"""
from rest_framework import permissions


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Permission pour accéder à son propre dossier ou être staff
    """
    
    def has_object_permission(self, request, view, obj):
        # Staff peut tout voir
        if request.user.user_type in ['admin', 'superadmin']:
            return True
        
        # L'élève peut voir son propre dossier
        if hasattr(obj, 'student'):
            return obj.student == request.user
        
        return False


class CanAccessStudentRecord(permissions.BasePermission):
    """
    Permission pour accéder aux dossiers élèves selon le rôle
    """
    
    def has_permission(self, request, view):
        # Tout utilisateur authentifié peut accéder à la vue
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Admin peut tout
        if user.user_type in ['admin', 'superadmin']:
            return True
        
        # L'élève peut voir son propre dossier
        if user.user_type == 'student':
            return obj.student == user
        
        # Parent peut voir les dossiers de ses enfants
        if user.user_type == 'parent':
            return obj.guardians.filter(
                user=user,
                has_custody=True
            ).exists()
        
        # Professeur peut voir les dossiers de ses élèves
        if user.user_type == 'teacher':
            # Professeur principal
            if obj.student.enrollments.filter(
                class_group__main_teacher=user,
                is_active=True
            ).exists():
                return True
            
            # Professeur de la classe
            return obj.student.enrollments.filter(
                class_group__schedules__teacher=user,
                is_active=True
            ).exists()
        
        return False


class CanModifyMedicalRecord(permissions.BasePermission):
    """
    Permission pour modifier le dossier médical
    """
    
    def has_permission(self, request, view):
        # Lecture pour tous les authentifiés
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Modification réservée au personnel médical et admin
        return request.user.user_type in ['admin', 'superadmin']
    
    def has_object_permission(self, request, view, obj):
        # Lecture selon les permissions du dossier élève
        if request.method in permissions.SAFE_METHODS:
            student_record = obj.student_record
            return CanAccessStudentRecord().has_object_permission(
                request, view, student_record
            )
        
        # Modification réservée
        return request.user.user_type in ['admin', 'superadmin']