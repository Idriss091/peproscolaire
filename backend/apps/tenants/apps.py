"""
Configuration de l'application tenants
"""
from django.apps import AppConfig


class TenantsConfig(AppConfig):
    """
    Configuration de l'application de gestion multi-tenant
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tenants'
    verbose_name = 'Gestion Multi-Tenant'
    
    def ready(self):
        """
        Initialisation de l'application
        """
        # Importer les signaux
        from . import signals
        
        # Patcher la connexion pour le support des schémas
        from .db import patch_connection
        patch_connection()