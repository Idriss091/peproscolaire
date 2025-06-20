#!/usr/bin/env python3
"""
Test de l'environnement local sans Docker
Utilise SQLite pour les tests rapides
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

# Ajouter le chemin du backend au PYTHONPATH
backend_path = Path("/home/walid/peproscolaire/backend")
sys.path.insert(0, str(backend_path))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Couleurs pour les logs
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'

def log(message, level="INFO"):
    color = {
        "INFO": Colors.GREEN,
        "ERROR": Colors.RED,
        "WARN": Colors.YELLOW,
        "TEST": Colors.BLUE
    }.get(level, Colors.NC)
    
    print(f"{color}[{level}]{Colors.NC} {message}")

def setup_test_environment():
    """Configure l'environnement de test local"""
    log("Configuration de l'environnement de test local...")
    
    os.chdir(backend_path)
    
    # Créer un fichier .env pour les tests
    test_env_content = """
# Configuration de test locale
DEBUG=True
SECRET_KEY=test-secret-key-for-local-testing
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# CORS pour le frontend
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
CORS_ALLOW_CREDENTIALS=True

# Base de données SQLite pour les tests
DATABASE_URL=sqlite:///test_peproscolaire.db

# Cache en mémoire
CACHE_URL=locmem://

# Email de test
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Désactiver Celery pour les tests
USE_CELERY=False
"""
    
    with open('.env.test', 'w') as f:
        f.write(test_env_content)
    
    # Pointer vers le fichier .env de test
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    os.environ['ENV_FILE'] = '.env.test'
    
    log("✅ Environnement de test configuré")

def install_dependencies():
    """Installe les dépendances Python"""
    log("Vérification des dépendances Python...")
    
    # Vérifier si l'environnement virtuel existe
    venv_path = backend_path / "backend_env"
    if not venv_path.exists():
        log("Création de l'environnement virtuel...")
        result = subprocess.run([
            sys.executable, "-m", "venv", "backend_env"
        ], cwd=backend_path, capture_output=True, text=True)
        
        if result.returncode != 0:
            log(f"❌ Échec de création de l'environnement virtuel: {result.stderr}", "ERROR")
            return False
    
    # Activer l'environnement virtuel et installer les dépendances
    if os.name == 'nt':  # Windows
        pip_path = venv_path / "Scripts" / "pip"
        python_path = venv_path / "Scripts" / "python"
    else:  # Unix
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    # Installer les dépendances de base pour les tests
    basic_requirements = [
        "Django==5.0.1",
        "djangorestframework==3.14.0", 
        "django-cors-headers==4.3.1",
        "django-environ==0.11.2",
        "djangorestframework-simplejwt==5.3.1",
        "requests==2.31.0"
    ]
    
    for package in basic_requirements:
        log(f"Installation de {package}...")
        result = subprocess.run([
            str(pip_path), "install", package
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            log(f"❌ Échec d'installation de {package}: {result.stderr}", "ERROR")
            return False
    
    log("✅ Dépendances installées")
    return True

def run_django_setup():
    """Configure Django pour les tests"""
    log("Configuration de Django...")
    
    # Chemin vers Python dans l'environnement virtuel
    venv_path = backend_path / "backend_env"
    if os.name == 'nt':  # Windows
        python_path = venv_path / "Scripts" / "python"
    else:  # Unix
        python_path = venv_path / "bin" / "python"
    
    # Créer les migrations
    log("Création des migrations...")
    result = subprocess.run([
        str(python_path), "manage.py", "makemigrations"
    ], cwd=backend_path, capture_output=True, text=True, env={
        **os.environ,
        'ENV_FILE': '.env.test'
    })
    
    if result.returncode != 0:
        log(f"⚠️  Avertissement makemigrations: {result.stderr}", "WARN")
    
    # Appliquer les migrations
    log("Application des migrations...")
    result = subprocess.run([
        str(python_path), "manage.py", "migrate"
    ], cwd=backend_path, capture_output=True, text=True, env={
        **os.environ,
        'ENV_FILE': '.env.test'
    })
    
    if result.returncode != 0:
        log(f"❌ Échec des migrations: {result.stderr}", "ERROR")
        return False
    
    # Créer un superutilisateur de test
    log("Création du superutilisateur de test...")
    create_user_script = """
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@test.fr').exists():
    User.objects.create_superuser(
        email='admin@test.fr',
        password='admin123',
        first_name='Admin',
        last_name='Test',
        user_type='super_admin'
    )
    print('Superutilisateur créé')
else:
    print('Superutilisateur existe déjà')
"""
    
    result = subprocess.run([
        str(python_path), "manage.py", "shell", "-c", create_user_script
    ], cwd=backend_path, capture_output=True, text=True, env={
        **os.environ,
        'ENV_FILE': '.env.test'
    })
    
    log("✅ Django configuré")
    return True

def start_django_server():
    """Démarre le serveur Django en arrière-plan"""
    log("Démarrage du serveur Django...")
    
    venv_path = backend_path / "backend_env"
    if os.name == 'nt':  # Windows
        python_path = venv_path / "Scripts" / "python"
    else:  # Unix
        python_path = venv_path / "bin" / "python"
    
    # Démarrer le serveur en arrière-plan
    process = subprocess.Popen([
        str(python_path), "manage.py", "runserver", "127.0.0.1:8000"
    ], cwd=backend_path, env={
        **os.environ,
        'ENV_FILE': '.env.test'
    }, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Attendre que le serveur soit prêt
    log("Attente du démarrage du serveur...")
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://127.0.0.1:8000/api/v1/auth/health/", timeout=2)
            if response.status_code == 200:
                log("✅ Serveur Django démarré")
                return process
        except:
            pass
        
        time.sleep(1)
    
    log("❌ Le serveur Django n'a pas démarré dans les temps", "ERROR")
    process.kill()
    return None

def test_api_endpoints():
    """Teste les endpoints API de base"""
    log("Test des endpoints API...")
    
    # Test du health check
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/auth/health/")
        if response.status_code == 200:
            log("✅ Health check: OK")
        else:
            log(f"❌ Health check: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log(f"❌ Erreur health check: {e}", "ERROR")
        return False
    
    # Test d'authentification
    try:
        auth_data = {
            "email": "admin@test.fr",
            "password": "admin123"
        }
        response = requests.post("http://127.0.0.1:8000/api/v1/auth/login/", json=auth_data)
        if response.status_code == 200:
            data = response.json()
            if "access" in data:
                log("✅ Authentification: OK")
                token = data["access"]
                
                # Test d'un endpoint protégé
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get("http://127.0.0.1:8000/api/v1/auth/profile/", headers=headers)
                if response.status_code == 200:
                    log("✅ Endpoint protégé: OK")
                else:
                    log(f"❌ Endpoint protégé: {response.status_code}", "ERROR")
            else:
                log("❌ Token non reçu", "ERROR")
                return False
        else:
            log(f"❌ Authentification: {response.status_code} - {response.text}", "ERROR")
            return False
    except Exception as e:
        log(f"❌ Erreur authentification: {e}", "ERROR")
        return False
    
    return True

def run_full_test():
    """Exécute le test complet"""
    log("🧪 Test complet de l'environnement local PeproScolaire", "INFO")
    print("=" * 70)
    
    # Étapes du test
    steps = [
        ("Configuration de l'environnement", setup_test_environment),
        ("Installation des dépendances", install_dependencies),
        ("Configuration Django", run_django_setup),
    ]
    
    # Exécuter les étapes de préparation
    for step_name, step_func in steps:
        log(f"📋 {step_name}...")
        if not step_func():
            log(f"❌ Échec: {step_name}", "ERROR")
            return False
        log(f"✅ {step_name}: Terminé")
    
    # Démarrer le serveur
    server_process = start_django_server()
    if not server_process:
        return False
    
    try:
        # Tester les APIs
        if test_api_endpoints():
            log("🎉 Tous les tests ont réussi !", "INFO")
            return True
        else:
            log("❌ Certains tests API ont échoué", "ERROR")
            return False
    
    finally:
        # Arrêter le serveur
        log("Arrêt du serveur Django...")
        server_process.kill()
        log("✅ Serveur arrêté")

if __name__ == "__main__":
    success = run_full_test()
    sys.exit(0 if success else 1)