#!/usr/bin/env python3
"""
Script de test pour vérifier la structure du projet sans dépendances Django
"""
import os
import sys
import importlib.util
from pathlib import Path

def test_file_structure():
    """Test de la structure des fichiers"""
    print("📁 Test de la structure des fichiers...")
    
    base_dir = Path(__file__).parent
    
    required_files = [
        'manage.py',
        'config/settings.py',
        'config/urls.py',
        'config/wsgi.py',
        'config/asgi.py',
        'config/celery.py',
        'requirements.txt',
        '.env'
    ]
    
    required_dirs = [
        'apps/authentication',
        'apps/schools',
        'apps/timetable',
        'apps/attendance',
        'apps/grades',
        'apps/homework',
        'apps/messaging',
        'apps/student_records',
        'apps/ai_analytics',
        'apps/ai_modules'
    ]
    
    print("\n🔍 Fichiers requis:")
    for file_path in required_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MANQUANT")
            return False
    
    print("\n📂 Répertoires requis:")
    for dir_path in required_dirs:
        full_path = base_dir / dir_path
        if full_path.exists() and full_path.is_dir():
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} - MANQUANT")
            return False
    
    return True

def test_app_structure():
    """Test de la structure des applications"""
    print("\n🏗️ Test de la structure des applications...")
    
    base_dir = Path(__file__).parent
    apps_dir = base_dir / 'apps'
    
    required_app_files = ['models.py', 'views.py', 'serializers.py', 'urls.py']
    apps_to_check = [
        'authentication', 'schools', 'timetable', 'attendance',
        'grades', 'homework', 'messaging', 'student_records', 'ai_analytics'
    ]
    
    all_good = True
    
    for app_name in apps_to_check:
        app_dir = apps_dir / app_name
        print(f"\n📦 {app_name}:")
        
        for file_name in required_app_files:
            file_path = app_dir / file_name
            if file_path.exists():
                print(f"  ✅ {file_name}")
            else:
                print(f"  ❌ {file_name} - MANQUANT")
                all_good = False
    
    return all_good

def test_imports():
    """Test des imports de base Python"""
    print("\n🐍 Test des imports Python...")
    
    base_dir = Path(__file__).parent
    sys.path.insert(0, str(base_dir))
    
    import_tests = [
        ('config.settings', 'Configuration Django'),
        ('config.urls', 'URLs principales'),
        ('apps.authentication.models', 'Modèles authentication'),
        ('apps.schools.models', 'Modèles schools'),
        ('apps.ai_analytics.models', 'Modèles ai_analytics')
    ]
    
    success_count = 0
    
    for module_name, description in import_tests:
        try:
            spec = importlib.util.find_spec(module_name)
            if spec is not None:
                print(f"✅ {description}")
                success_count += 1
            else:
                print(f"❌ {description} - Module non trouvé")
        except Exception as e:
            print(f"❌ {description} - Erreur: {e}")
    
    return success_count == len(import_tests)

def test_urls_configuration():
    """Test de la configuration des URLs"""
    print("\n🌐 Test de la configuration des URLs...")
    
    base_dir = Path(__file__).parent
    config_urls = base_dir / 'config' / 'urls.py'
    
    if not config_urls.exists():
        print("❌ config/urls.py n'existe pas")
        return False
    
    try:
        with open(config_urls, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_patterns = [
            "path('api/v1/auth/', include('apps.authentication.urls'))",
            "path('api/v1/schools/', include('apps.schools.urls'))",
            "path('api/v1/timetable/', include('apps.timetable.urls'))",
            "path('api/v1/attendance/', include('apps.attendance.urls'))",
            "path('api/v1/grades/', include('apps.grades.urls'))",
            "path('api/v1/homework/', include('apps.homework.urls'))",
            "path('api/v1/messaging/', include('apps.messaging.urls'))",
            "path('api/v1/student-records/', include('apps.student_records.urls'))",
            "path('api/v1/ai-analytics/', include('apps.ai_analytics.urls'))"
        ]
        
        success_count = 0
        for pattern in required_patterns:
            if pattern in content:
                module_name = pattern.split("'")[3].replace('apps.', '').replace('.urls', '')
                print(f"✅ API {module_name}")
                success_count += 1
            else:
                module_name = pattern.split("'")[1].replace('api/v1/', '')
                print(f"❌ API {module_name} - MANQUANT")
        
        return success_count == len(required_patterns)
        
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier URLs: {e}")
        return False

def test_environment_config():
    """Test de la configuration d'environnement"""
    print("\n⚙️ Test de la configuration d'environnement...")
    
    base_dir = Path(__file__).parent
    env_file = base_dir / '.env'
    
    if not env_file.exists():
        print("❌ Fichier .env manquant")
        return False
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_vars = [
            'SECRET_KEY',
            'DEBUG',
            'ALLOWED_HOSTS',
            'DATABASE_URL',
            'REDIS_URL',
            'CORS_ALLOWED_ORIGINS'
        ]
        
        success_count = 0
        for var in required_vars:
            if f"{var}=" in content:
                print(f"✅ {var}")
                success_count += 1
            else:
                print(f"❌ {var} - MANQUANT")
        
        return success_count == len(required_vars)
        
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier .env: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 PeproScolaire - Test de Structure Backend")
    print("=" * 50)
    
    tests = [
        ("Structure des fichiers", test_file_structure),
        ("Structure des applications", test_app_structure),
        ("Imports Python", test_imports),
        ("Configuration URLs", test_urls_configuration),
        ("Configuration environnement", test_environment_config)
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
        print("🎉 Tous les tests sont réussis ! Structure prête.")
        print("\n📝 CORRECTIONS APPLIQUÉES:")
        print("✅ Module ai_analytics ajouté aux URLs principales")
        print("✅ Module schools avec views et URLs créés")
        print("✅ Fichiers manage.py, wsgi.py, asgi.py créés")
        print("✅ Configuration .env mise à jour")
        print("\n🚀 PROCHAINES ÉTAPES:")
        print("1. Construire et lancer les conteneurs Docker")
        print("2. Exécuter les migrations de base de données")
        print("3. Créer les fixtures de données de test")
        print("4. Tester les endpoints API")
        return 0
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez la structure.")
        return 1

if __name__ == '__main__':
    sys.exit(main())