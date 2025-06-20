"""
Classes de stockage personnalisées pour l'isolation des fichiers par tenant
"""
import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.utils.functional import cached_property


class TenantFileSystemStorage(FileSystemStorage):
    """
    Stockage isolé par tenant
    Les fichiers sont organisés par tenant_id pour garantir l'isolation
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tenant = None
    
    @property
    def tenant(self):
        """
        Récupère le tenant actuel depuis le thread local storage
        """
        if self._tenant is None:
            from .utils import get_current_schema, get_tenant_from_schema_name
            schema = get_current_schema()
            if schema and schema != 'public':
                self._tenant = get_tenant_from_schema_name(schema)
        return self._tenant
    
    def _get_tenant_path(self, name):
        """
        Préfixe le chemin avec l'ID du tenant
        """
        if self.tenant:
            return os.path.join(f'tenant_{self.tenant.id}', name)
        return os.path.join('shared', name)
    
    def _save(self, name, content):
        """
        Sauvegarde le fichier dans le répertoire du tenant
        """
        name = self._get_tenant_path(name)
        return super()._save(name, content)
    
    def exists(self, name):
        """
        Vérifie si le fichier existe dans le répertoire du tenant
        """
        name = self._get_tenant_path(name)
        return super().exists(name)
    
    def url(self, name):
        """
        Retourne l'URL du fichier avec le préfixe du tenant
        """
        if self.tenant:
            # Inclure le domaine du tenant dans l'URL si nécessaire
            base_url = f"https://{self.tenant.domain_url}"
            return f"{base_url}{settings.MEDIA_URL}{self._get_tenant_path(name)}"
        return super().url(name)
    
    def path(self, name):
        """
        Retourne le chemin absolu du fichier
        """
        name = self._get_tenant_path(name)
        return super().path(name)
    
    def delete(self, name):
        """
        Supprime le fichier du répertoire du tenant
        """
        name = self._get_tenant_path(name)
        return super().delete(name)
    
    def listdir(self, path):
        """
        Liste les fichiers dans le répertoire du tenant
        """
        path = self._get_tenant_path(path)
        return super().listdir(path)
    
    def size(self, name):
        """
        Retourne la taille du fichier
        """
        name = self._get_tenant_path(name)
        return super().size(name)
    
    def get_tenant_usage(self):
        """
        Calcule l'espace utilisé par le tenant en bytes
        """
        if not self.tenant:
            return 0
        
        total_size = 0
        tenant_root = self.path(f'tenant_{self.tenant.id}')
        
        if os.path.exists(tenant_root):
            for dirpath, dirnames, filenames in os.walk(tenant_root):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
        
        return total_size
    
    def get_tenant_usage_gb(self):
        """
        Calcule l'espace utilisé par le tenant en GB
        """
        return self.get_tenant_usage() / (1024 ** 3)
    
    def check_tenant_quota(self, file_size):
        """
        Vérifie si le tenant a assez d'espace pour stocker un nouveau fichier
        """
        if not self.tenant:
            return True
        
        current_usage_gb = self.get_tenant_usage_gb()
        file_size_gb = file_size / (1024 ** 3)
        
        return (current_usage_gb + file_size_gb) <= self.tenant.max_storage_gb


class TenantStaticFileStorage(FileSystemStorage):
    """
    Stockage pour les fichiers statiques personnalisés par tenant
    (logos, CSS personnalisé, etc.)
    """
    
    def __init__(self, *args, **kwargs):
        # Définir le répertoire de base pour les fichiers statiques des tenants
        location = kwargs.pop('location', os.path.join(settings.STATIC_ROOT, 'tenants'))
        base_url = kwargs.pop('base_url', f'{settings.STATIC_URL}tenants/')
        
        super().__init__(location=location, base_url=base_url, *args, **kwargs)
    
    def get_tenant_static_path(self, tenant, filename=''):
        """
        Retourne le chemin pour les fichiers statiques d'un tenant
        """
        return os.path.join(str(tenant.id), filename)
    
    def save_tenant_logo(self, tenant, logo_file):
        """
        Sauvegarde le logo d'un tenant
        """
        filename = f'logo_{tenant.id}.{logo_file.name.split(".")[-1]}'
        path = self.get_tenant_static_path(tenant, filename)
        
        saved_path = self.save(path, logo_file)
        return self.url(saved_path)
    
    def save_tenant_favicon(self, tenant, favicon_file):
        """
        Sauvegarde le favicon d'un tenant
        """
        filename = f'favicon_{tenant.id}.ico'
        path = self.get_tenant_static_path(tenant, filename)
        
        saved_path = self.save(path, favicon_file)
        return self.url(saved_path)


# Instance globale pour le stockage des fichiers tenant
tenant_storage = TenantFileSystemStorage()
tenant_static_storage = TenantStaticFileStorage()