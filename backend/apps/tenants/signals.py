"""
Signaux Django pour la gestion des tenants
"""
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Tenant, TenantDomain
from .utils import create_schema, drop_schema
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Tenant)
def handle_tenant_created(sender, instance, created, **kwargs):
    """
    Signal déclenché après la création d'un tenant
    """
    if created:
        logger.info(f"Nouveau tenant créé: {instance.domain_url}")
        
        # Invalider le cache
        cache_key = f'tenant:{instance.domain_url}'
        cache.delete(cache_key)
        
        # Note: Le provisionnement (création du schéma) est fait séparément
        # via la méthode provision() ou la commande de gestion


@receiver(pre_delete, sender=Tenant)
def handle_tenant_deletion(sender, instance, **kwargs):
    """
    Signal déclenché avant la suppression d'un tenant
    """
    logger.warning(f"Suppression du tenant: {instance.domain_url}")
    
    # Invalider le cache
    cache_key = f'tenant:{instance.domain_url}'
    cache.delete(cache_key)
    
    # Supprimer le schéma si demandé
    if hasattr(instance, '_delete_schema') and instance._delete_schema:
        try:
            drop_schema(instance.schema_name, cascade=True)
            logger.info(f"Schéma {instance.schema_name} supprimé")
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du schéma: {e}")


@receiver(post_save, sender=TenantDomain)
def handle_domain_created(sender, instance, created, **kwargs):
    """
    Signal déclenché après l'ajout d'un domaine alternatif
    """
    if created:
        logger.info(f"Nouveau domaine ajouté: {instance.domain} -> {instance.tenant.schema_name}")
        
        # Invalider le cache pour ce domaine
        cache_key = f'tenant:{instance.domain}'
        cache.delete(cache_key)


@receiver(pre_delete, sender=TenantDomain)
def handle_domain_deletion(sender, instance, **kwargs):
    """
    Signal déclenché avant la suppression d'un domaine
    """
    # Invalider le cache
    cache_key = f'tenant:{instance.domain}'
    cache.delete(cache_key)