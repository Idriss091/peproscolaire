"""
Middleware pour la gestion multi-tenant
"""
import logging
from django.http import Http404, HttpResponseRedirect
from django.db import connection
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from .models import Tenant, TenantDomain

logger = logging.getLogger(__name__)


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware pour identifier et activer le tenant basé sur le sous-domaine
    """
    
    def process_request(self, request):
        """
        Identifie le tenant à partir du domaine et configure la connexion
        """
        # Extraire le hostname
        hostname = request.get_host().split(':')[0].lower()
        
        # Vérifier le cache d'abord
        cache_key = f'tenant:{hostname}'
        tenant = cache.get(cache_key)
        
        if not tenant:
            try:
                # Chercher d'abord dans les domaines principaux
                tenant = Tenant.objects.select_related('school').get(
                    domain_url=hostname,
                    is_active=True
                )
            except Tenant.DoesNotExist:
                # Chercher dans les domaines alternatifs
                try:
                    tenant_domain = TenantDomain.objects.select_related('tenant__school').get(
                        domain=hostname
                    )
                    tenant = tenant_domain.tenant
                except TenantDomain.DoesNotExist:
                    # Si c'est le domaine principal, rediriger vers la page d'accueil
                    if hostname in ['peproscolaire.fr', 'www.peproscolaire.fr', 'localhost']:
                        request.tenant = None
                        return None
                    
                    # Sinon, erreur 404
                    logger.warning(f"Tenant non trouvé pour le domaine: {hostname}")
                    raise Http404("Établissement non trouvé")
            
            # Mettre en cache pour 5 minutes
            if tenant:
                cache.set(cache_key, tenant, 300)
        
        # Vérifier que le tenant est actif
        if not tenant.is_active:
            logger.warning(f"Tentative d'accès à un tenant inactif: {tenant.schema_name}")
            raise Http404("Cet établissement n'est pas accessible actuellement")
        
        # Attacher le tenant à la requête
        request.tenant = tenant
        
        # Configurer la connexion pour utiliser le schéma du tenant
        connection.set_schema(tenant.schema_name)
        
        # Ajouter le tenant au contexte de logging
        logger.info(f"Tenant activé: {tenant.schema_name} pour {hostname}")
        
        return None
    
    def process_response(self, request, response):
        """
        Nettoie la connexion après la requête
        """
        # Réinitialiser le schéma à public
        if hasattr(request, 'tenant') and request.tenant:
            connection.set_schema('public')
        
        return response
    
    def process_exception(self, request, exception):
        """
        Gère les exceptions en réinitialisant le schéma
        """
        # Réinitialiser le schéma en cas d'erreur
        if hasattr(request, 'tenant') and request.tenant:
            connection.set_schema('public')
        
        return None


class TenantSchemaMiddleware(MiddlewareMixin):
    """
    Middleware alternatif qui utilise django-tenants si installé
    """
    
    def process_request(self, request):
        """
        Configure le schéma pour django-tenants
        """
        try:
            from django_tenants.utils import get_tenant_model, get_tenant_domain_model
            
            hostname = request.get_host().split(':')[0].lower()
            
            # Utiliser django-tenants pour la résolution
            domain_model = get_tenant_domain_model()
            try:
                tenant = domain_model.objects.select_related('tenant').get(
                    domain=hostname
                ).tenant
                
                request.tenant = tenant
                connection.set_tenant(tenant)
                
            except domain_model.DoesNotExist:
                raise Http404("Tenant non trouvé")
                
        except ImportError:
            # django-tenants n'est pas installé, utiliser notre implémentation
            return None


class TenantContextMiddleware(MiddlewareMixin):
    """
    Middleware pour ajouter le contexte du tenant aux templates
    """
    
    def process_template_response(self, request, response):
        """
        Ajoute les informations du tenant au contexte
        """
        if hasattr(request, 'tenant') and request.tenant:
            if hasattr(response, 'context_data'):
                response.context_data['tenant'] = request.tenant
                response.context_data['tenant_theme'] = {
                    'primary_color': request.tenant.primary_color,
                    'secondary_color': request.tenant.secondary_color,
                    'logo_url': request.tenant.logo_url,
                    'favicon_url': request.tenant.favicon_url,
                    'school_name': request.tenant.school.name,
                }
        
        return response


class TenantSecurityMiddleware(MiddlewareMixin):
    """
    Middleware de sécurité pour s'assurer que les requêtes cross-tenant sont bloquées
    """
    
    def process_request(self, request):
        """
        Vérifie que l'utilisateur appartient bien au tenant
        """
        if hasattr(request, 'tenant') and request.tenant and request.user.is_authenticated:
            # Vérifier que l'utilisateur appartient au bon établissement
            if hasattr(request.user, 'school_users'):
                user_schools = request.user.school_users.all()
                if user_schools and request.tenant.school not in [us.school for us in user_schools]:
                    logger.warning(
                        f"Tentative d'accès cross-tenant: User {request.user.id} "
                        f"essaie d'accéder au tenant {request.tenant.schema_name}"
                    )
                    # Déconnecter l'utilisateur
                    from django.contrib.auth import logout
                    logout(request)
                    return HttpResponseRedirect('/login/')
        
        return None