"""
Managers personnalisés pour la gestion multi-tenant
"""
from django.db import models
from django.db import connection


class TenantAwareManager(models.Manager):
    """
    Manager qui filtre automatiquement les requêtes par tenant
    """
    def get_queryset(self):
        """
        Override pour filtrer par le tenant actuel
        """
        queryset = super().get_queryset()
        
        # Récupérer le tenant actuel depuis la connexion
        if hasattr(connection, 'tenant'):
            # Le filtrage se fait au niveau du schéma PostgreSQL
            # donc pas besoin de filtrer explicitement ici
            pass
            
        return queryset
    
    def get_for_tenant(self, tenant):
        """
        Récupère les objets pour un tenant spécifique
        """
        # Changer temporairement le schéma
        original_schema = connection.schema_name if hasattr(connection, 'schema_name') else 'public'
        
        try:
            connection.set_schema(tenant.schema_name)
            return self.get_queryset()
        finally:
            # Restaurer le schéma original
            connection.set_schema(original_schema)


class CrossTenantManager(models.Manager):
    """
    Manager pour les modèles qui doivent être accessibles à travers tous les tenants
    (par exemple, pour les super-administrateurs)
    """
    def get_all_tenants_data(self):
        """
        Récupère les données de tous les tenants
        """
        from .models import Tenant
        
        all_data = {}
        for tenant in Tenant.objects.filter(is_active=True):
            try:
                connection.set_schema(tenant.schema_name)
                all_data[tenant.schema_name] = list(self.get_queryset())
            except Exception as e:
                all_data[tenant.schema_name] = {'error': str(e)}
        
        # Restaurer le schéma public
        connection.set_schema('public')
        
        return all_data