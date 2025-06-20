#!/usr/bin/env python3
"""
Test rapide de validation de l'environnement PeproScolaire
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

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

def run_command(command, cwd=None, timeout=30):
    """Exécute une commande et retourne le résultat"""
    try:
        result = subprocess.run(
            command.split(),
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_docker():
    """Vérifie que Docker est disponible"""
    log("Vérification de Docker...")
    success, stdout, stderr = run_command("docker --version")
    if success:
        log(f"✅ Docker disponible: {stdout.strip()}")
        return True
    else:
        log(f"❌ Docker non disponible: {stderr}")
        return False

def check_docker_compose():
    """Vérifie que Docker Compose est disponible"""
    log("Vérification de Docker Compose...")
    success, stdout, stderr = run_command("docker-compose --version")
    if success:
        log(f"✅ Docker Compose disponible: {stdout.strip()}")
        return True
    else:
        log(f"❌ Docker Compose non disponible: {stderr}")
        return False

def check_node():
    """Vérifie que Node.js est disponible"""
    log("Vérification de Node.js...")
    success, stdout, stderr = run_command("node --version")
    if success:
        log(f"✅ Node.js disponible: {stdout.strip()}")
        return True
    else:
        log(f"❌ Node.js non disponible: {stderr}")
        return False

def check_python():
    """Vérifie que Python est disponible"""
    log("Vérification de Python...")
    log(f"✅ Python disponible: {sys.version}")
    return True

def check_backend_structure():
    """Vérifie la structure du backend"""
    log("Vérification de la structure du backend...")
    
    backend_path = Path("/home/walid/peproscolaire/backend")
    required_files = [
        "manage.py",
        "requirements.txt",
        "config/settings.py",
        "config/urls.py",
    ]
    
    required_dirs = [
        "apps/authentication",
        "apps/schools",
        "apps/grades",
        "apps/timetable",
        "apps/attendance",
        "apps/homework",
        "apps/messaging",
        "apps/student_records",
        "apps/ai_analytics"
    ]
    
    all_good = True
    
    for file_path in required_files:
        full_path = backend_path / file_path
        if full_path.exists():
            log(f"✅ Fichier trouvé: {file_path}")
        else:
            log(f"❌ Fichier manquant: {file_path}")
            all_good = False
    
    for dir_path in required_dirs:
        full_path = backend_path / dir_path
        if full_path.exists():
            log(f"✅ Module trouvé: {dir_path}")
        else:
            log(f"❌ Module manquant: {dir_path}")
            all_good = False
    
    return all_good

def check_frontend_structure():
    """Vérifie la structure du frontend"""
    log("Vérification de la structure du frontend...")
    
    frontend_path = Path("/home/walid/peproscolaire/frontend/peproscolaire-ui")
    required_files = [
        "package.json",
        "vite.config.ts",
        "src/main.ts",
        "src/App.vue",
    ]
    
    required_dirs = [
        "src/api",
        "src/stores",
        "src/views",
        "src/components",
        "src/types"
    ]
    
    all_good = True
    
    for file_path in required_files:
        full_path = frontend_path / file_path
        if full_path.exists():
            log(f"✅ Fichier trouvé: {file_path}")
        else:
            log(f"❌ Fichier manquant: {file_path}")
            all_good = False
    
    for dir_path in required_dirs:
        full_path = frontend_path / dir_path
        if full_path.exists():
            log(f"✅ Dossier trouvé: {dir_path}")
        else:
            log(f"❌ Dossier manquant: {dir_path}")
            all_good = False
    
    return all_good

def check_docker_compose_file():
    """Vérifie le fichier docker-compose.yml"""
    log("Vérification du fichier docker-compose.yml...")
    
    compose_file = Path("/home/walid/peproscolaire/docker-compose.yml")
    if not compose_file.exists():
        log("❌ Fichier docker-compose.yml manquant")
        return False
    
    log("✅ Fichier docker-compose.yml trouvé")
    return True

def test_docker_services():
    """Test de démarrage rapide des services Docker"""
    log("Test de démarrage des services Docker...")
    
    os.chdir("/home/walid/peproscolaire")
    
    # Arrêter les services existants
    log("Arrêt des services existants...")
    run_command("docker-compose down", timeout=60)
    
    # Démarrer PostgreSQL et Redis
    log("Démarrage de PostgreSQL et Redis...")
    success, stdout, stderr = run_command("docker-compose up -d db redis", timeout=120)
    
    if not success:
        log(f"❌ Échec du démarrage des services: {stderr}")
        return False
    
    # Attendre que les services soient prêts
    log("Attente que les services soient prêts...")
    time.sleep(20)
    
    # Vérifier PostgreSQL
    success, stdout, stderr = run_command("docker-compose exec -T db pg_isready -U peproscolaire_user", timeout=30)
    if success:
        log("✅ PostgreSQL est prêt")
    else:
        log(f"❌ PostgreSQL ne répond pas: {stderr}")
    
    # Vérifier Redis
    success, stdout, stderr = run_command("docker-compose exec -T redis redis-cli ping", timeout=30)
    if success and "PONG" in stdout:
        log("✅ Redis est prêt")
    else:
        log(f"❌ Redis ne répond pas: {stderr}")
    
    # Arrêter les services
    log("Arrêt des services de test...")
    run_command("docker-compose down", timeout=60)
    
    return True

def check_backend_dependencies():
    """Vérifie les dépendances Python du backend"""
    log("Vérification des dépendances Python...")
    
    backend_path = Path("/home/walid/peproscolaire/backend")
    requirements_file = backend_path / "requirements.txt"
    
    if not requirements_file.exists():
        log("❌ Fichier requirements.txt manquant")
        return False
    
    # Lire le fichier requirements
    with open(requirements_file, 'r') as f:
        requirements = f.read()
    
    critical_packages = [
        "Django",
        "djangorestframework",
        "psycopg2-binary",
        "redis",
        "djangorestframework-simplejwt"
    ]
    
    all_good = True
    for package in critical_packages:
        if package in requirements:
            log(f"✅ Dépendance trouvée: {package}")
        else:
            log(f"❌ Dépendance manquante: {package}")
            all_good = False
    
    return all_good

def check_frontend_dependencies():
    """Vérifie les dépendances Node.js du frontend"""
    log("Vérification des dépendances Node.js...")
    
    frontend_path = Path("/home/walid/peproscolaire/frontend/peproscolaire-ui")
    package_json = frontend_path / "package.json"
    
    if not package_json.exists():
        log("❌ Fichier package.json manquant")
        return False
    
    # Lire le fichier package.json
    with open(package_json, 'r') as f:
        package_data = json.load(f)
    
    dependencies = {**package_data.get('dependencies', {}), **package_data.get('devDependencies', {})}
    
    critical_packages = [
        "vue",
        "vue-router",
        "pinia",
        "axios",
        "tailwindcss",
        "typescript"
    ]
    
    all_good = True
    for package in critical_packages:
        if package in dependencies:
            log(f"✅ Dépendance trouvée: {package}")
        else:
            log(f"❌ Dépendance manquante: {package}")
            all_good = False
    
    return all_good

def run_all_tests():
    """Exécute tous les tests de validation"""
    log("🚀 Démarrage des tests de validation de l'environnement PeproScolaire", "INFO")
    print("=" * 70)
    
    tests = [
        ("Vérification de Python", check_python),
        ("Vérification de Docker", check_docker),
        ("Vérification de Docker Compose", check_docker_compose),
        ("Vérification de Node.js", check_node),
        ("Structure du backend", check_backend_structure),
        ("Structure du frontend", check_frontend_structure),
        ("Fichier docker-compose.yml", check_docker_compose_file),
        ("Dépendances backend", check_backend_dependencies),
        ("Dépendances frontend", check_frontend_dependencies),
        ("Services Docker", test_docker_services),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 50)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                log(f"✅ {test_name}: RÉUSSI", "TEST")
            else:
                log(f"❌ {test_name}: ÉCHOUÉ", "ERROR")
                
        except Exception as e:
            log(f"❌ {test_name}: ERREUR - {e}", "ERROR")
            results.append((test_name, False))
    
    # Rapport final
    print("\n" + "=" * 70)
    print("📊 RAPPORT DE VALIDATION")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"📈 Tests réussis: {passed}/{total}")
    print(f"📊 Taux de réussite: {success_rate:.1f}%")
    
    if success_rate == 100:
        log("🎉 Tous les tests ont réussi ! L'environnement est prêt.", "INFO")
        return True
    else:
        log(f"⚠️  {total - passed} test(s) ont échoué. Vérifiez les détails ci-dessus.", "WARN")
        
        print("\n❌ TESTS ÉCHOUÉS:")
        for test_name, result in results:
            if not result:
                print(f"  - {test_name}")
        
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)