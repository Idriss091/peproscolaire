"""
Vues API pour la gestion des tenants
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Tenant, TenantDomain, TenantSettings
from .serializers import (
    TenantSerializer, TenantCreateSerializer,
    TenantDomainSerializer, TenantSettingsSerializer,
    TenantStatsSerializer
)
from .utils import provision_tenant, execute_on_tenant
from .permissions import IsSuperAdmin, IsTenantAdmin
import logging

logger = logging.getLogger(__name__)


class TenantViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des tenants
    Accessible uniquement aux super-administrateurs
    """
    queryset = Tenant.objects.select_related('school').prefetch_related('domains')
    serializer_class = TenantSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TenantCreateSerializer
        elif self.action == 'stats':
            return TenantStatsSerializer
        return TenantSerializer
    
    @action(detail=True, methods=['post'])
    def provision(self, request, pk=None):
        """
        Provisionne un tenant (crée le schéma et applique les migrations)
        """
        tenant = self.get_object()
        
        if tenant.provisioned_at:
            return Response(
                {'error': 'Ce tenant est déjà provisionné'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            provision_tenant(tenant)
            return Response({
                'status': 'success',
                'message': f'Tenant {tenant.domain_url} provisionné avec succès'
            })
        except Exception as e:
            logger.error(f"Erreur lors du provisionnement du tenant {tenant.id}: {str(e)}")
            return Response(
                {'error': f'Erreur lors du provisionnement: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Active un tenant
        """
        tenant = self.get_object()
        tenant.is_active = True
        tenant.save()
        
        return Response({
            'status': 'success',
            'message': f'Tenant {tenant.domain_url} activé'
        })
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        Désactive un tenant
        """
        tenant = self.get_object()
        tenant.is_active = False
        tenant.save()
        
        return Response({
            'status': 'success',
            'message': f'Tenant {tenant.domain_url} désactivé'
        })
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """
        Récupère les statistiques détaillées d'un tenant
        """
        tenant = self.get_object()
        
        try:
            # Compter les utilisateurs
            from apps.authentication.models import User
            user_stats = execute_on_tenant(tenant, self._get_user_stats)
            
            # Calculer l'utilisation du stockage
            from .storage import tenant_storage
            storage_gb = execute_on_tenant(tenant, tenant_storage.get_tenant_usage_gb)
            storage_percentage = (storage_gb / tenant.max_storage_gb) * 100
            
            # Calculer les jours depuis le dernier accès
            days_since_access = None
            if tenant.last_accessed_at:
                delta = timezone.now() - tenant.last_accessed_at
                days_since_access = delta.days
            
            # Modules actifs/inactifs
            active_modules = [k for k, v in tenant.modules_enabled.items() if v]
            inactive_modules = [k for k, v in tenant.modules_enabled.items() if not v]
            
            stats = {
                'tenant_id': tenant.id,
                'tenant_name': tenant.school.name,
                'domain_url': tenant.domain_url,
                'is_active': tenant.is_active,
                **user_stats,
                'storage_used_gb': round(storage_gb, 2),
                'storage_limit_gb': tenant.max_storage_gb,
                'storage_percentage': round(storage_percentage, 2),
                'last_accessed': tenant.last_accessed_at,
                'days_since_last_access': days_since_access,
                'active_modules': active_modules,
                'inactive_modules': inactive_modules
            }
            
            serializer = TenantStatsSerializer(stats)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des stats pour {tenant.id}: {str(e)}")
            return Response(
                {'error': 'Erreur lors du calcul des statistiques'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_user_stats(self):
        """
        Calcule les statistiques utilisateurs
        """
        from apps.authentication.models import User
        from django.db.models import Count
        
        stats = User.objects.values('user_type').annotate(count=Count('id'))
        
        result = {
            'total_users': User.objects.count(),
            'student_count': 0,
            'teacher_count': 0,
            'parent_count': 0,
            'admin_count': 0
        }
        
        for item in stats:
            if item['user_type'] == 'student':
                result['student_count'] = item['count']
            elif item['user_type'] == 'teacher':
                result['teacher_count'] = item['count']
            elif item['user_type'] == 'parent':
                result['parent_count'] = item['count']
            elif item['user_type'] == 'admin':
                result['admin_count'] = item['count']
        
        return result
    
    @action(detail=True, methods=['post'])
    def update_modules(self, request, pk=None):
        """
        Met à jour les modules activés pour un tenant
        """
        tenant = self.get_object()
        modules = request.data.get('modules_enabled', {})
        
        # Valider les modules
        valid_modules = [
            'authentication', 'schools', 'timetable', 'attendance',
            'grades', 'homework', 'messaging', 'student_records',
            'ai_analytics'
        ]
        
        for module in modules:
            if module not in valid_modules:
                return Response(
                    {'error': f'Module invalide: {module}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        tenant.modules_enabled = modules
        tenant.save()
        
        return Response({
            'status': 'success',
            'modules_enabled': tenant.modules_enabled
        })
    
    @action(detail=True, methods=['post'])
    def add_domain(self, request, pk=None):
        """
        Ajoute un domaine alternatif à un tenant
        """
        tenant = self.get_object()
        domain = request.data.get('domain')
        is_primary = request.data.get('is_primary', False)
        
        if not domain:
            return Response(
                {'error': 'Le domaine est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier l'unicité
        if TenantDomain.objects.filter(domain=domain).exists():
            return Response(
                {'error': 'Ce domaine est déjà utilisé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Créer le domaine
        tenant_domain = TenantDomain.objects.create(
            tenant=tenant,
            domain=domain,
            is_primary=is_primary
        )
        
        serializer = TenantDomainSerializer(tenant_domain)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get', 'patch'])
    def settings(self, request, pk=None):
        """
        Gère les paramètres d'un tenant
        """
        tenant = self.get_object()
        
        if request.method == 'GET':
            settings_obj, created = TenantSettings.objects.get_or_create(tenant=tenant)
            serializer = TenantSettingsSerializer(settings_obj)
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            settings_obj, created = TenantSettings.objects.get_or_create(tenant=tenant)
            serializer = TenantSettingsSerializer(
                settings_obj,
                data=request.data,
                partial=True
            )
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class CurrentTenantView(viewsets.ViewSet):
    """
    Vue pour accéder aux informations du tenant actuel
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def info(self, request):
        """
        Retourne les informations du tenant actuel
        """
        if not hasattr(request, 'tenant') or not request.tenant:
            return Response(
                {'error': 'Aucun tenant actif'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = TenantSerializer(request.tenant)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def theme(self, request):
        """
        Retourne le thème du tenant actuel
        """
        if not hasattr(request, 'tenant') or not request.tenant:
            # Retourner le thème par défaut
            return Response({
                'primary_color': '#1976D2',
                'secondary_color': '#424242',
                'logo_url': '/static/img/default-logo.png',
                'favicon_url': '/static/img/favicon.ico',
                'school_name': 'PeproScolaire'
            })
        
        tenant = request.tenant
        return Response({
            'primary_color': tenant.primary_color,
            'secondary_color': tenant.secondary_color,
            'logo_url': tenant.logo_url or '/static/img/default-logo.png',
            'favicon_url': tenant.favicon_url or '/static/img/favicon.ico',
            'school_name': tenant.school.name
        })
    
    @action(detail=False, methods=['get'])
    def modules(self, request):
        """
        Retourne les modules activés pour le tenant actuel
        """
        if not hasattr(request, 'tenant') or not request.tenant:
            # Retourner tous les modules activés par défaut
            return Response({
                'authentication': True,
                'schools': True,
                'timetable': True,
                'attendance': True,
                'grades': True,
                'homework': True,
                'messaging': True,
                'student_records': True,
                'ai_analytics': True
            })
        
        return Response(request.tenant.modules_enabled)