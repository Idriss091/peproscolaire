"""
Router de base de données pour la gestion multi-tenant
"""
from django.db import connection


class TenantDatabaseRouter:
    """
    Router pour diriger les requêtes vers le bon schéma PostgreSQL
    """
    
    # Applications qui doivent toujours utiliser le schéma public
    SHARED_APPS = [
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'django.contrib.sessions',
        'django.contrib.admin',
        'django.contrib.messages',
        'tenants',  # L'app tenants elle-même est partagée
    ]
    
    # Applications spécifiques au tenant
    TENANT_APPS = [
        'authentication',
        'schools',
        'timetable',
        'attendance',
        'grades',
        'homework',
        'messaging',
        'student_records',
        'ai_analytics',
        'core',
    ]
    
    def db_for_read(self, model, **hints):
        """
        Détermine quelle base de données utiliser pour la lecture
        """
        # Si le modèle a un attribut _meta.tenant_aware, il est spécifique au tenant
        if hasattr(model._meta, 'tenant_aware') and model._meta.tenant_aware:
            return self._get_tenant_db()
        
        # Vérifier par nom d'application
        app_label = model._meta.app_label
        
        if app_label in self.SHARED_APPS:
            return 'default'  # Utilise le schéma public
        elif app_label in self.TENANT_APPS:
            return self._get_tenant_db()
        
        return None
    
    def db_for_write(self, model, **hints):
        """
        Détermine quelle base de données utiliser pour l'écriture
        """
        # Même logique que pour la lecture
        return self.db_for_read(model, **hints)
    
    def allow_relation(self, obj1, obj2, **hints):
        """
        Détermine si une relation entre deux objets est autorisée
        """
        # Récupérer les labels d'application
        app1_label = obj1._meta.app_label
        app2_label = obj2._meta.app_label
        
        # Les relations sont autorisées si les deux objets sont dans le même groupe
        if (app1_label in self.SHARED_APPS and app2_label in self.SHARED_APPS):
            return True
        elif (app1_label in self.TENANT_APPS and app2_label in self.TENANT_APPS):
            return True
        
        # Autoriser les relations entre shared et tenant apps dans certains cas
        # Par exemple, User (shared) peut avoir des relations avec des modèles tenant
        if (app1_label == 'auth' and app2_label in self.TENANT_APPS) or \
           (app2_label == 'auth' and app1_label in self.TENANT_APPS):
            return True
        
        return False
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Détermine si une migration est autorisée sur une base de données
        """
        if db == 'default':
            # Sur la base par défaut, on ne migre que les apps partagées
            return app_label in self.SHARED_APPS
        else:
            # Sur les autres bases (tenants), on migre les apps tenant
            return app_label in self.TENANT_APPS
    
    def _get_tenant_db(self):
        """
        Retourne l'alias de base de données pour le tenant actuel
        """
        # Dans notre cas, on utilise toujours 'default' mais avec des schémas différents
        # Le schéma est géré par le middleware
        return 'default'


class TenantSchemaRouter:
    """
    Router alternatif qui gère les schémas PostgreSQL directement
    """
    
    def __init__(self):
        self.tenant_apps = set(TenantDatabaseRouter.TENANT_APPS)
        self.shared_apps = set(TenantDatabaseRouter.SHARED_APPS)
    
    def get_schema(self, model):
        """
        Détermine le schéma à utiliser pour un modèle
        """
        app_label = model._meta.app_label
        
        # Si on a un tenant dans la connexion, l'utiliser
        if hasattr(connection, 'tenant') and connection.tenant:
            if app_label in self.tenant_apps:
                return connection.tenant.schema_name
        
        # Sinon, utiliser le schéma public
        return 'public'
    
    def allow_migrate_schema(self, schema_name, app_label):
        """
        Détermine si une app peut être migrée dans un schéma donné
        """
        if schema_name == 'public':
            return app_label in self.shared_apps
        else:
            return app_label in self.tenant_apps