#!/bin/bash

# Script de démarrage de la stack de développement PeproScolaire
# Usage: ./scripts/start-dev-stack.sh

set -e

echo "🚀 Démarrage de la stack PeproScolaire - Développement"
echo "=================================================="

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction de log
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ERROR:${NC} $1"
}

# Vérification des prérequis
check_requirements() {
    log "Vérification des prérequis..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker n'est pas installé"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose n'est pas installé"
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        error "Node.js n'est pas installé"
        exit 1
    fi
    
    log "✅ Tous les prérequis sont installés"
}

# Démarrage des services Docker
start_docker_services() {
    log "Démarrage des services Docker (PostgreSQL, Redis)..."
    
    cd /home/walid/peproscolaire
    
    if [ ! -f docker-compose.yml ]; then
        error "Fichier docker-compose.yml non trouvé"
        exit 1
    fi
    
    # Arrêter les services existants
    docker-compose down --remove-orphans
    
    # Démarrer les services de base (utiliser les noms du docker-compose existant)
    docker-compose up -d db redis
    
    # Attendre que PostgreSQL soit prêt
    log "Attente du démarrage de PostgreSQL..."
    sleep 15
    
    # Vérifier la connexion à PostgreSQL (utiliser les credentials du docker-compose)
    if docker-compose exec -T db pg_isready -U peproscolaire_user; then
        log "✅ PostgreSQL est prêt"
    else
        error "PostgreSQL ne répond pas"
        exit 1
    fi
    
    log "✅ Services Docker démarrés"
}

# Configuration du backend Django
setup_backend() {
    log "Configuration du backend Django..."
    
    cd /home/walid/peproscolaire/backend
    
    # Vérifier l'environnement virtuel
    if [ ! -d "backend_env" ]; then
        log "Création de l'environnement virtuel Python..."
        python3 -m venv backend_env
    fi
    
    # Activer l'environnement virtuel
    source backend_env/bin/activate
    
    # Installer les dépendances
    log "Installation des dépendances Python..."
    pip install -r requirements.txt
    
    # Vérifier le fichier .env
    if [ ! -f .env ]; then
        log "Création du fichier .env..."
        cat > .env << EOF
# Configuration Django
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,backend

# CORS pour le frontend
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
CORS_ALLOW_CREDENTIALS=True

# Base de données (utiliser les credentials du docker-compose)
DATABASE_URL=postgresql://peproscolaire_user:peproscolaire_secure_password@localhost:5432/peproscolaire

# Redis (avec mot de passe du docker-compose)
REDIS_URL=redis://:peproscolaire_redis_password@localhost:6379/0

# JWT
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# Email (développement)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Celery
CELERY_BROKER_URL=redis://:peproscolaire_redis_password@localhost:6379/1
CELERY_RESULT_BACKEND=redis://:peproscolaire_redis_password@localhost:6379/2

# WebSocket
CHANNEL_LAYERS_BACKEND=channels_redis.core.RedisChannelLayer
CHANNEL_LAYERS_CONFIG_HOSTS=[("localhost", 6379)]
EOF
    fi
    
    # Migrations de base de données
    log "Application des migrations..."
    python manage.py migrate
    
    # Création du superutilisateur (si nécessaire)
    log "Création des données de test..."
    python manage.py shell << EOF
from django.contrib.auth import get_user_model
from apps.schools.models import School, AcademicYear, Level, Class
from apps.authentication.models import User
import json

User = get_user_model()

# Créer un superutilisateur de test
if not User.objects.filter(email='admin@peproscolaire.fr').exists():
    admin = User.objects.create_superuser(
        email='admin@peproscolaire.fr',
        password='admin123',
        first_name='Admin',
        last_name='PeproScolaire',
        user_type='super_admin'
    )
    print("✅ Superutilisateur créé: admin@peproscolaire.fr / admin123")

# Créer des utilisateurs de test
test_users = [
    {
        'email': 'teacher@test.fr',
        'password': 'teacher123',
        'first_name': 'Jean',
        'last_name': 'Dupont',
        'user_type': 'teacher'
    },
    {
        'email': 'student@test.fr', 
        'password': 'student123',
        'first_name': 'Marie',
        'last_name': 'Martin',
        'user_type': 'student'
    },
    {
        'email': 'parent@test.fr',
        'password': 'parent123', 
        'first_name': 'Pierre',
        'last_name': 'Durand',
        'user_type': 'parent'
    }
]

for user_data in test_users:
    if not User.objects.filter(email=user_data['email']).exists():
        User.objects.create_user(**user_data)
        print(f"✅ Utilisateur créé: {user_data['email']} / {user_data['password']}")

# Créer une école de test
if not School.objects.exists():
    school = School.objects.create(
        name='Collège de Test',
        school_type='college',
        address='123 Rue de Test',
        city='Ville Test',
        postal_code='12345',
        phone='01.23.45.67.89',
        email='contact@college-test.fr'
    )
    print("✅ École de test créée")
    
    # Année académique
    academic_year = AcademicYear.objects.create(
        school=school,
        name='2024-2025',
        start_date='2024-09-01',
        end_date='2025-07-15',
        is_current=True
    )
    
    # Niveaux et classes
    for level_name in ['6ème', '5ème', '4ème', '3ème']:
        level = Level.objects.create(
            school=school,
            name=level_name,
            order=1 if level_name == '6ème' else 2 if level_name == '5ème' else 3 if level_name == '4ème' else 4
        )
        
        for class_suffix in ['A', 'B']:
            Class.objects.create(
                school=school,
                academic_year=academic_year,
                level=level,
                name=f'{level_name} {class_suffix}',
                max_students=30
            )
    
    print("✅ Niveaux et classes créés")

print("✅ Données de test initialisées")
EOF
    
    log "✅ Backend Django configuré"
}

# Démarrage du serveur Django
start_backend_server() {
    log "Démarrage du serveur Django..."
    
    cd /home/walid/peproscolaire/backend
    source backend_env/bin/activate
    
    # Démarrer le serveur en arrière-plan
    python manage.py runserver 0.0.0.0:8000 > ../logs/django.log 2>&1 &
    DJANGO_PID=$!
    echo $DJANGO_PID > ../logs/django.pid
    
    # Attendre que le serveur soit prêt
    log "Attente du démarrage du serveur Django..."
    sleep 5
    
    # Vérifier que le serveur répond
    if curl -s http://localhost:8000/api/v1/auth/health/ > /dev/null; then
        log "✅ Serveur Django démarré sur http://localhost:8000"
    else
        warn "Le serveur Django ne répond pas encore, continuons..."
    fi
}

# Configuration du frontend Vue.js
setup_frontend() {
    log "Configuration du frontend Vue.js..."
    
    cd /home/walid/peproscolaire/frontend/peproscolaire-ui
    
    # Installer les dépendances
    if [ ! -d "node_modules" ]; then
        log "Installation des dépendances Node.js..."
        npm install
    else
        log "Mise à jour des dépendances Node.js..."
        npm ci
    fi
    
    # Vérifier la configuration Vite
    if [ ! -f ".env.local" ]; then
        log "Création du fichier .env.local..."
        cat > .env.local << EOF
# Configuration de développement
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_BASE_URL=ws://localhost:8000/ws
VITE_APP_ENV=development
VITE_DEBUG=true
EOF
    fi
    
    log "✅ Frontend Vue.js configuré"
}

# Démarrage du serveur de développement Vite
start_frontend_server() {
    log "Démarrage du serveur Vite..."
    
    cd /home/walid/peproscolaire/frontend/peproscolaire-ui
    
    # Démarrer Vite en arrière-plan
    npm run dev > ../../logs/vite.log 2>&1 &
    VITE_PID=$!
    echo $VITE_PID > ../../logs/vite.pid
    
    # Attendre que le serveur soit prêt
    log "Attente du démarrage du serveur Vite..."
    sleep 10
    
    # Vérifier que le serveur répond
    if curl -s http://localhost:5173 > /dev/null; then
        log "✅ Serveur Vite démarré sur http://localhost:5173"
    else
        warn "Le serveur Vite ne répond pas encore, continuons..."
    fi
}

# Tests de santé
health_check() {
    log "Tests de santé de la stack..."
    
    # Test PostgreSQL
    if docker-compose exec -T postgres pg_isready -U peproscolaire > /dev/null; then
        log "✅ PostgreSQL : OK"
    else
        error "❌ PostgreSQL : ERREUR"
    fi
    
    # Test Redis
    if docker-compose exec -T redis redis-cli ping | grep -q PONG; then
        log "✅ Redis : OK"
    else
        error "❌ Redis : ERREUR"
    fi
    
    # Test Django
    if curl -s http://localhost:8000/api/v1/auth/health/ > /dev/null; then
        log "✅ Django API : OK"
    else
        warn "⚠️  Django API : Non disponible"
    fi
    
    # Test Vite
    if curl -s http://localhost:5173 > /dev/null; then
        log "✅ Frontend Vite : OK"
    else
        warn "⚠️  Frontend Vite : Non disponible"
    fi
}

# Affichage des informations
show_info() {
    echo ""
    echo "🎉 Stack PeproScolaire démarrée avec succès !"
    echo "=============================================="
    echo ""
    echo "📱 Frontend (Vue.js + Vite):"
    echo "   http://localhost:5173"
    echo ""
    echo "🔧 Backend (Django + DRF):"
    echo "   http://localhost:8000"
    echo "   Admin: http://localhost:8000/admin"
    echo ""
    echo "🗃️  Base de données PostgreSQL:"
    echo "   Host: localhost:5432"
    echo "   Database: peproscolaire"
    echo "   User: peproscolaire_user"
    echo "   Password: peproscolaire_secure_password"
    echo ""
    echo "🔴 Redis:"
    echo "   Host: localhost:6379"
    echo ""
    echo "👤 Comptes de test:"
    echo "   Admin: admin@peproscolaire.fr / admin123"
    echo "   Teacher: teacher@test.fr / teacher123"
    echo "   Student: student@test.fr / student123"
    echo "   Parent: parent@test.fr / parent123"
    echo ""
    echo "📋 Commandes utiles:"
    echo "   Arrêter: ./scripts/stop-dev-stack.sh"
    echo "   Logs Django: tail -f logs/django.log"
    echo "   Logs Vite: tail -f logs/vite.log"
    echo ""
}

# Fonction principale
main() {
    # Créer le dossier des logs
    mkdir -p /home/walid/peproscolaire/logs
    
    check_requirements
    start_docker_services
    setup_backend
    start_backend_server
    setup_frontend
    start_frontend_server
    
    sleep 5
    health_check
    show_info
    
    log "🚀 Stack prête pour le développement !"
}

# Gestion des signaux pour un arrêt propre
cleanup() {
    log "Arrêt de la stack..."
    
    # Arrêter les serveurs
    if [ -f /home/walid/peproscolaire/logs/django.pid ]; then
        kill $(cat /home/walid/peproscolaire/logs/django.pid) 2>/dev/null || true
        rm -f /home/walid/peproscolaire/logs/django.pid
    fi
    
    if [ -f /home/walid/peproscolaire/logs/vite.pid ]; then
        kill $(cat /home/walid/peproscolaire/logs/vite.pid) 2>/dev/null || true
        rm -f /home/walid/peproscolaire/logs/vite.pid
    fi
    
    # Arrêter Docker
    cd /home/walid/peproscolaire
    docker-compose down
    
    log "✅ Stack arrêtée"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Exécution
main "$@"