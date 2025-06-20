"""
Tests pour le système multi-tenant
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.db import connection
from .models import Tenant, TenantDomain, TenantSettings
from .middleware import TenantMiddleware
from .utils import create_schema, schema_exists, set_schema
from apps.schools.models import School

User = get_user_model()


class TenantModelTest(TestCase):
    """
    Tests pour le modèle Tenant
    """
    
    def setUp(self):
        """Configuration initiale des tests"""
        self.school = School.objects.create(
            name="Lycée Test",
            school_type="lycee",
            email="test@lycee.fr",
            phone="0123456789",
            address="123 rue Test",
            postal_code="75001",
            city="Paris",
            subdomain="lycee-test"
        )
    
    def test_tenant_creation(self):
        """Test de création d'un tenant"""
        tenant = Tenant.objects.create(
            schema_name="lycee_test",
            domain_url="lycee-test.peproscolaire.fr",
            school=self.school,
            primary_color="#FF0000",
            secondary_color="#00FF00"
        )
        
        self.assertEqual(tenant.schema_name, "lycee_test")
        self.assertEqual(tenant.domain_url, "lycee-test.peproscolaire.fr")
        self.assertEqual(tenant.school, self.school)
        self.assertTrue(tenant.is_active)
        self.assertEqual(tenant.max_students, 1000)
        self.assertEqual(tenant.max_storage_gb, 50)
    
    def test_default_modules(self):
        """Test des modules par défaut"""
        tenant = Tenant.objects.create(
            schema_name="lycee_test2",
            domain_url="lycee-test2.peproscolaire.fr",
            school=self.school
        )
        
        # Vérifier que les modules par défaut sont activés
        self.assertTrue(tenant.is_module_enabled('authentication'))
        self.assertTrue(tenant.is_module_enabled('schools'))
        self.assertTrue(tenant.is_module_enabled('timetable'))
        self.assertFalse(tenant.is_module_enabled('ai_analytics'))
    
    def test_tenant_domain(self):
        """Test des domaines alternatifs"""
        tenant = Tenant.objects.create(
            schema_name="lycee_test3",
            domain_url="lycee-test3.peproscolaire.fr",
            school=self.school
        )
        
        # Ajouter un domaine alternatif
        alt_domain = TenantDomain.objects.create(
            tenant=tenant,
            domain="lycee-test.ac-paris.fr",
            is_primary=False
        )
        
        self.assertEqual(alt_domain.tenant, tenant)
        self.assertEqual(alt_domain.domain, "lycee-test.ac-paris.fr")
        self.assertFalse(alt_domain.is_primary)


class TenantMiddlewareTest(TestCase):
    """
    Tests pour le middleware multi-tenant
    """
    
    def setUp(self):
        """Configuration initiale"""
        self.factory = RequestFactory()
        self.middleware = TenantMiddleware(lambda r: r)
        
        # Créer un tenant de test
        self.school = School.objects.create(
            name="Collège Test",
            school_type="college",
            email="test@college.fr",
            phone="0123456789",
            address="456 rue Test",
            postal_code="75002",
            city="Paris",
            subdomain="college-test"
        )
        
        self.tenant = Tenant.objects.create(
            schema_name="college_test",
            domain_url="college-test.peproscolaire.fr",
            school=self.school
        )
    
    def test_tenant_resolution(self):
        """Test de résolution du tenant depuis le domaine"""
        # Créer une requête avec le bon domaine
        request = self.factory.get('/')
        request.META['HTTP_HOST'] = 'college-test.peproscolaire.fr'
        
        # Appeler le middleware
        self.middleware.process_request(request)
        
        # Vérifier que le tenant est attaché à la requête
        self.assertTrue(hasattr(request, 'tenant'))
        self.assertEqual(request.tenant, self.tenant)
    
    def test_invalid_domain(self):
        """Test avec un domaine invalide"""
        request = self.factory.get('/')
        request.META['HTTP_HOST'] = 'inexistant.peproscolaire.fr'
        
        # Le middleware devrait lever une 404
        from django.http import Http404
        with self.assertRaises(Http404):
            self.middleware.process_request(request)
    
    def test_main_domain(self):
        """Test avec le domaine principal"""
        request = self.factory.get('/')
        request.META['HTTP_HOST'] = 'peproscolaire.fr'
        
        # Le middleware ne devrait pas lever d'erreur
        response = self.middleware.process_request(request)
        
        # Pas de tenant pour le domaine principal
        self.assertIsNone(response)
        self.assertIsNone(getattr(request, 'tenant', None))


class TenantSchemaTest(TestCase):
    """
    Tests pour la gestion des schémas PostgreSQL
    """
    
    def test_schema_creation(self):
        """Test de création de schéma"""
        schema_name = "test_schema"
        
        # Créer le schéma
        create_schema(schema_name)
        
        # Vérifier qu'il existe
        self.assertTrue(schema_exists(schema_name))
        
        # Nettoyer
        with connection.cursor() as cursor:
            cursor.execute(f"DROP SCHEMA IF EXISTS {schema_name}")
    
    def test_schema_switching(self):
        """Test de changement de schéma"""
        # Créer un schéma de test
        schema_name = "test_switch"
        create_schema(schema_name)
        
        try:
            # Changer vers le nouveau schéma
            set_schema(schema_name)
            
            # Vérifier le schéma actuel
            with connection.cursor() as cursor:
                cursor.execute("SELECT current_schema()")
                current = cursor.fetchone()[0]
                self.assertEqual(current, schema_name)
            
            # Revenir au schéma public
            set_schema('public')
            
        finally:
            # Nettoyer
            with connection.cursor() as cursor:
                cursor.execute(f"DROP SCHEMA IF EXISTS {schema_name}")


class TenantSettingsTest(TestCase):
    """
    Tests pour les paramètres des tenants
    """
    
    def setUp(self):
        """Configuration initiale"""
        self.school = School.objects.create(
            name="Lycée Settings",
            school_type="lycee",
            email="settings@lycee.fr",
            phone="0123456789",
            address="789 rue Settings",
            postal_code="75003",
            city="Paris",
            subdomain="lycee-settings"
        )
        
        self.tenant = Tenant.objects.create(
            schema_name="lycee_settings",
            domain_url="lycee-settings.peproscolaire.fr",
            school=self.school
        )
    
    def test_settings_creation(self):
        """Test de création des paramètres"""
        settings = TenantSettings.objects.create(
            tenant=self.tenant,
            enable_sms_notifications=True,
            password_min_length=10,
            timezone='Europe/London'
        )
        
        self.assertEqual(settings.tenant, self.tenant)
        self.assertTrue(settings.enable_email_notifications)  # Par défaut
        self.assertTrue(settings.enable_sms_notifications)
        self.assertEqual(settings.password_min_length, 10)
        self.assertEqual(settings.timezone, 'Europe/London')
        self.assertEqual(settings.language, 'fr')  # Par défaut


class TenantPermissionsTest(TestCase):
    """
    Tests pour les permissions multi-tenant
    """
    
    def setUp(self):
        """Configuration initiale"""
        # Créer des utilisateurs de test
        self.superadmin = User.objects.create_user(
            username='superadmin',
            email='super@admin.com',
            password='test123',
            user_type='superadmin'
        )
        
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='test123',
            user_type='admin'
        )
        
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            password='test123',
            user_type='teacher'
        )
    
    def test_superadmin_permissions(self):
        """Test des permissions super-admin"""
        from .permissions import IsSuperAdmin
        
        permission = IsSuperAdmin()
        
        # Créer une requête factice
        request = RequestFactory().get('/')
        
        # Super-admin devrait avoir la permission
        request.user = self.superadmin
        self.assertTrue(permission.has_permission(request, None))
        
        # Admin normal ne devrait pas avoir la permission
        request.user = self.admin
        self.assertFalse(permission.has_permission(request, None))
        
        # Professeur ne devrait pas avoir la permission
        request.user = self.teacher
        self.assertFalse(permission.has_permission(request, None))