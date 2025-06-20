"""
Extensions de connexion à la base de données pour le multi-tenant
"""
from django.db import connection as django_connection
from django.db.backends.postgresql import base
from django.db.backends.utils import CursorWrapper
import logging

logger = logging.getLogger(__name__)


class TenantCursorWrapper(CursorWrapper):
    """
    Wrapper de curseur qui s'assure que le bon schéma est utilisé
    """
    def __init__(self, cursor, db):
        super().__init__(cursor, db)
        self._schema_name = None
    
    def set_schema(self, schema_name):
        """
        Définit le schéma pour ce curseur
        """
        if schema_name and schema_name != self._schema_name:
            self.execute(f"SET search_path TO {schema_name}, public")
            self._schema_name = schema_name


class TenantDatabaseWrapper(base.DatabaseWrapper):
    """
    Wrapper de base de données qui gère les schémas PostgreSQL
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tenant = None
        self._schema_name = 'public'
    
    def get_new_connection(self, conn_params):
        """
        Crée une nouvelle connexion avec le support des schémas
        """
        connection = super().get_new_connection(conn_params)
        return connection
    
    def init_connection_state(self):
        """
        Initialise l'état de la connexion
        """
        super().init_connection_state()
        
        # Définir le schéma initial
        if self._schema_name:
            with self.cursor() as cursor:
                cursor.execute(f"SET search_path TO {self._schema_name}, public")
    
    def set_tenant(self, tenant):
        """
        Définit le tenant actuel
        """
        self._tenant = tenant
        if tenant:
            self.set_schema(tenant.schema_name)
    
    def set_schema(self, schema_name):
        """
        Définit le schéma actuel
        """
        if schema_name != self._schema_name:
            self._schema_name = schema_name
            
            # Si la connexion est déjà ouverte, changer le schéma
            if self.connection:
                with self.cursor() as cursor:
                    cursor.execute(f"SET search_path TO {schema_name}, public")
                    logger.debug(f"Schéma changé vers: {schema_name}")
    
    def get_schema(self):
        """
        Retourne le schéma actuel
        """
        return self._schema_name
    
    def create_cursor(self, name=None):
        """
        Crée un curseur avec le support des schémas
        """
        cursor = super().create_cursor(name)
        return TenantCursorWrapper(cursor, self)
    
    # Propriétés pour la compatibilité
    @property
    def schema_name(self):
        return self._schema_name
    
    @schema_name.setter
    def schema_name(self, value):
        self.set_schema(value)
    
    @property
    def tenant(self):
        return self._tenant


def patch_connection():
    """
    Patche la connexion Django pour ajouter le support des tenants
    """
    # Ajouter les méthodes au wrapper existant
    wrapper_class = django_connection.__class__
    
    if not hasattr(wrapper_class, 'set_tenant'):
        wrapper_class.set_tenant = lambda self, tenant: self.set_schema(
            tenant.schema_name if tenant else 'public'
        )
    
    if not hasattr(wrapper_class, 'set_schema'):
        def set_schema(self, schema_name):
            with self.cursor() as cursor:
                cursor.execute(f"SET search_path TO {schema_name}, public")
                self.schema_name = schema_name
        
        wrapper_class.set_schema = set_schema
    
    if not hasattr(wrapper_class, 'schema_name'):
        wrapper_class.schema_name = 'public'


# Patcher la connexion au démarrage
patch_connection()


class SchemaManager:
    """
    Gestionnaire pour les opérations sur les schémas
    """
    @staticmethod
    def create_schema(schema_name):
        """
        Crée un nouveau schéma
        """
        with django_connection.cursor() as cursor:
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
            logger.info(f"Schéma {schema_name} créé")
    
    @staticmethod
    def drop_schema(schema_name, cascade=True):
        """
        Supprime un schéma
        """
        with django_connection.cursor() as cursor:
            cascade_clause = "CASCADE" if cascade else ""
            cursor.execute(f"DROP SCHEMA IF EXISTS {schema_name} {cascade_clause}")
            logger.warning(f"Schéma {schema_name} supprimé")
    
    @staticmethod
    def schema_exists(schema_name):
        """
        Vérifie si un schéma existe
        """
        with django_connection.cursor() as cursor:
            cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = %s)",
                [schema_name]
            )
            return cursor.fetchone()[0]
    
    @staticmethod
    def list_schemas():
        """
        Liste tous les schémas
        """
        with django_connection.cursor() as cursor:
            cursor.execute(
                "SELECT schema_name FROM information_schema.schemata "
                "WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')"
            )
            return [row[0] for row in cursor.fetchall()]
    
    @staticmethod
    def get_schema_size(schema_name):
        """
        Retourne la taille d'un schéma en bytes
        """
        with django_connection.cursor() as cursor:
            cursor.execute("""
                SELECT SUM(pg_total_relation_size(quote_ident(schemaname)||'.'||quote_ident(tablename)))::bigint
                FROM pg_tables
                WHERE schemaname = %s
            """, [schema_name])
            result = cursor.fetchone()[0]
            return result or 0
    
    @staticmethod
    def copy_schema(source_schema, target_schema):
        """
        Copie un schéma vers un autre
        """
        with django_connection.cursor() as cursor:
            # Créer le schéma cible
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {target_schema}")
            
            # Copier la structure et les données
            cursor.execute(f"""
                DO $$
                DECLARE
                    obj record;
                BEGIN
                    -- Copier les tables
                    FOR obj IN
                        SELECT tablename FROM pg_tables WHERE schemaname = '{source_schema}'
                    LOOP
                        EXECUTE format('CREATE TABLE %I.%I (LIKE %I.%I INCLUDING ALL)',
                            '{target_schema}', obj.tablename, '{source_schema}', obj.tablename);
                        EXECUTE format('INSERT INTO %I.%I SELECT * FROM %I.%I',
                            '{target_schema}', obj.tablename, '{source_schema}', obj.tablename);
                    END LOOP;
                END $$;
            """)
            
            logger.info(f"Schéma {source_schema} copié vers {target_schema}")