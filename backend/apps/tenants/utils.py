"""
Utilitaires pour la gestion multi-tenant
"""
import os
from django.db import connection, transaction
from django.core.management import call_command
from django.conf import settings
from django.core.files.storage import default_storage
import logging

logger = logging.getLogger(__name__)


def set_schema(schema_name):
    """
    Change le schéma actuel de la connexion PostgreSQL
    """
    with connection.cursor() as cursor:
        cursor.execute(f"SET search_path TO {schema_name}, public")
    
    # Stocker le schéma actuel dans la connexion
    connection.schema_name = schema_name


def get_current_schema():
    """
    Récupère le schéma actuel
    """
    if hasattr(connection, 'schema_name'):
        return connection.schema_name
    
    with connection.cursor() as cursor:
        cursor.execute("SHOW search_path")
        result = cursor.fetchone()
        if result:
            # Le search_path peut contenir plusieurs schémas, on prend le premier
            schemas = result[0].split(',')
            return schemas[0].strip().strip('"')
    
    return 'public'


def create_schema(schema_name, check_exists=True):
    """
    Crée un nouveau schéma PostgreSQL
    """
    with connection.cursor() as cursor:
        if check_exists:
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
        else:
            cursor.execute(f"CREATE SCHEMA {schema_name}")
    
    logger.info(f"Schéma {schema_name} créé avec succès")


def drop_schema(schema_name, cascade=True):
    """
    Supprime un schéma PostgreSQL
    ATTENTION: Cette opération est irréversible!
    """
    with connection.cursor() as cursor:
        if cascade:
            cursor.execute(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE")
        else:
            cursor.execute(f"DROP SCHEMA IF EXISTS {schema_name}")
    
    logger.warning(f"Schéma {schema_name} supprimé")


def schema_exists(schema_name):
    """
    Vérifie si un schéma existe
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s",
            [schema_name]
        )
        return cursor.fetchone() is not None


def migrate_schema(schema_name, app_labels=None):
    """
    Applique les migrations pour un schéma spécifique
    """
    # Sauvegarder le schéma actuel
    original_schema = get_current_schema()
    
    try:
        # Changer vers le schéma cible
        set_schema(schema_name)
        
        # Appliquer les migrations
        if app_labels:
            for app_label in app_labels:
                call_command('migrate', app_label, verbosity=0)
        else:
            call_command('migrate', verbosity=0)
        
        logger.info(f"Migrations appliquées pour le schéma {schema_name}")
        
    finally:
        # Restaurer le schéma original
        set_schema(original_schema)


def get_tenant_storage_path(tenant, base_path=''):
    """
    Retourne le chemin de stockage pour un tenant
    """
    return os.path.join('tenants', str(tenant.id), base_path)


def get_tenant_media_url(tenant, filename):
    """
    Retourne l'URL media pour un fichier d'un tenant
    """
    path = get_tenant_storage_path(tenant, filename)
    return default_storage.url(path)


def clone_schema(source_schema, target_schema):
    """
    Clone un schéma existant vers un nouveau schéma
    Utile pour créer des tenants de test ou des backups
    """
    with connection.cursor() as cursor:
        # Créer le nouveau schéma
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {target_schema}")
        
        # Obtenir la liste des tables du schéma source
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = %s
        """, [source_schema])
        
        tables = cursor.fetchall()
        
        # Copier chaque table
        for (table_name,) in tables:
            cursor.execute(f"""
                CREATE TABLE {target_schema}.{table_name} 
                (LIKE {source_schema}.{table_name} INCLUDING ALL)
            """)
            
            # Copier les données
            cursor.execute(f"""
                INSERT INTO {target_schema}.{table_name} 
                SELECT * FROM {source_schema}.{table_name}
            """)
    
    logger.info(f"Schéma {source_schema} cloné vers {target_schema}")


def get_tenant_from_request(request):
    """
    Récupère le tenant depuis la requête
    """
    if hasattr(request, 'tenant'):
        return request.tenant
    return None


def get_tenant_from_schema_name(schema_name):
    """
    Récupère le tenant à partir du nom du schéma
    """
    from .models import Tenant
    
    try:
        return Tenant.objects.get(schema_name=schema_name)
    except Tenant.DoesNotExist:
        return None


def execute_on_tenant(tenant, func, *args, **kwargs):
    """
    Exécute une fonction dans le contexte d'un tenant spécifique
    """
    original_schema = get_current_schema()
    
    try:
        set_schema(tenant.schema_name)
        return func(*args, **kwargs)
    finally:
        set_schema(original_schema)


def get_tenant_aware_model(model_class, tenant):
    """
    Retourne une version du modèle qui opère dans le contexte du tenant
    """
    class TenantAwareModelProxy(model_class):
        class Meta:
            proxy = True
            
        def save(self, *args, **kwargs):
            return execute_on_tenant(tenant, super().save, *args, **kwargs)
        
        def delete(self, *args, **kwargs):
            return execute_on_tenant(tenant, super().delete, *args, **kwargs)
        
        @classmethod
        def objects_for_tenant(cls):
            """Retourne un queryset filtré pour le tenant"""
            return execute_on_tenant(tenant, lambda: cls.objects.all())
    
    return TenantAwareModelProxy


class TenantContextManager:
    """
    Context manager pour exécuter du code dans le contexte d'un tenant
    """
    def __init__(self, tenant):
        self.tenant = tenant
        self.original_schema = None
    
    def __enter__(self):
        self.original_schema = get_current_schema()
        set_schema(self.tenant.schema_name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        set_schema(self.original_schema)
        return False


def provision_tenant(tenant):
    """
    Provisionne complètement un nouveau tenant
    """
    from .models import TenantSettings
    
    # Créer le schéma
    create_schema(tenant.schema_name)
    
    # Appliquer les migrations
    with TenantContextManager(tenant):
        # Migrer les apps tenant
        from .db_router import TenantDatabaseRouter
        for app_label in TenantDatabaseRouter.TENANT_APPS:
            try:
                call_command('migrate', app_label, verbosity=0)
            except Exception as e:
                logger.error(f"Erreur lors de la migration de {app_label}: {e}")
    
    # Créer les paramètres par défaut
    TenantSettings.objects.create(tenant=tenant)
    
    # Créer les répertoires de stockage
    storage_path = get_tenant_storage_path(tenant)
    os.makedirs(os.path.join(settings.MEDIA_ROOT, storage_path), exist_ok=True)
    
    # Marquer comme provisionné
    from django.utils import timezone
    tenant.provisioned_at = timezone.now()
    tenant.save()
    
    logger.info(f"Tenant {tenant.schema_name} provisionné avec succès")