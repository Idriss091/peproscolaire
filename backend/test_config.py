#!/usr/bin/env python
"""
Script de test pour vérifier la configuration Django
"""
import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

# Configuration de base pour les tests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Variables d'environnement de test
test_env = {
    'SECRET_KEY': 'test-secret-key-for-configuration-check',
    'DEBUG': 'True',
    'ALLOWED_HOSTS': 'localhost,127.0.0.1',
    'DATABASE_URL': 'sqlite:///test.db',
    'REDIS_URL': 'redis://localhost:6379/0',
    'CORS_ALLOWED_ORIGINS': 'http://localhost:3000,http://127.0.0.1:3000'
}

# Appliquer les variables d'environnement de test
for key, value in test_env.items():
    os.environ[key] = value

def test_django_setup():
    """Test de la configuration Django"""
    print("🔧 Test de la configuration Django...")
    
    try:
        django.setup()
        print("✅ Django configuré avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur de configuration Django: {e}")
        return False

def test_apps_loading():
    """Test du chargement des applications"""
    print("\n📦 Test du chargement des applications...")
    
    try:
        from django.apps import apps
        
        required_apps = [
            'apps.authentication',
            'apps.schools',
            'apps.timetable',
            'apps.attendance',
            'apps.grades',
            'apps.homework',
            'apps.messaging',
            'apps.student_records',
            'apps.ai_analytics'
        ]
        
        loaded_apps = [app.name for app in apps.get_app_configs()]
        
        for app_name in required_apps:
            if app_name in loaded_apps:
                print(f"✅ {app_name}")
            else:
                print(f"❌ {app_name} - Non trouvée")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Erreur lors du chargement des apps: {e}")
        return False

def test_models():
    """Test des modèles"""
    print("\n🗄️  Test des modèles...")
    
    try:
        # Test des imports de modèles
        from apps.authentication.models import User
        from apps.schools.models import School, Class
        from apps.ai_analytics.models import RiskProfile
        
        print("✅ Modèles importés avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur d'import des modèles: {e}")
        return False

def test_urls():
    """Test de la configuration des URLs"""
    print("\n🌐 Test de la configuration des URLs...")
    
    try:
        from django.urls import reverse
        from config.urls import urlpatterns
        
        print(f"✅ {len(urlpatterns)} patterns d'URL configurés")
        
        # Test de résolution d'URLs de base
        test_patterns = [
            'schema-swagger-ui',
            'schema-redoc'
        ]
        
        for pattern in test_patterns:
            try:
                url = reverse(pattern)
                print(f"✅ {pattern}: {url}")
            except Exception as e:
                print(f"⚠️  {pattern}: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur de configuration URLs: {e}")
        return False

def test_api_routes():
    """Test des routes API"""
    print("\n🔗 Test des routes API...")
    
    api_modules = [
        ('auth', 'apps.authentication.urls'),
        ('schools', 'apps.schools.urls'),
        ('timetable', 'apps.timetable.urls'),
        ('attendance', 'apps.attendance.urls'),
        ('grades', 'apps.grades.urls'),
        ('homework', 'apps.homework.urls'),
        ('messaging', 'apps.messaging.urls'),
        ('student-records', 'apps.student_records.urls'),
        ('ai-analytics', 'apps.ai_analytics.urls')
    ]
    
    success_count = 0
    
    for api_name, module_path in api_modules:
        try:
            __import__(module_path)
            print(f"✅ API {api_name}: {module_path}")
            success_count += 1
        except Exception as e:
            print(f"❌ API {api_name}: {e}")
    
    print(f"\n📊 {success_count}/{len(api_modules)} modules API configurés correctement")
    return success_count == len(api_modules)

def main():
    """Fonction principale de test"""
    print("🧪 PeproScolaire - Test de Configuration Backend")
    print("=" * 50)
    
    tests = [
        ("Configuration Django", test_django_setup),
        ("Chargement des applications", test_apps_loading),
        ("Modèles de données", test_models),
        ("Configuration URLs", test_urls),
        ("Routes API", test_api_routes)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * len(test_name))
        success = test_func()
        results.append((test_name, success))
    
    # Résumé
    print("\n" + "=" * 50)
    print("📋 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    success_count = 0
    for test_name, success in results:
        status = "✅ RÉUSSI" if success else "❌ ÉCHEC"
        print(f"{status:12} {test_name}")
        if success:
            success_count += 1
    
    print(f"\n🎯 Score: {success_count}/{len(results)} tests réussis")
    
    if success_count == len(results):
        print("🎉 Tous les tests sont réussis ! Configuration prête.")
        return 0
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez la configuration.")
        return 1

if __name__ == '__main__':
    sys.exit(main())