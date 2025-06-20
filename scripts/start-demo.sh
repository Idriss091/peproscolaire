#!/bin/bash
set -e

echo "🚀 Démarrage de PeproScolaire - Mode Démo"
echo "=========================================="

# Couleurs pour les logs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Fonction de nettoyage
cleanup() {
    echo ""
    log "Arrêt des services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    exit 0
}

# Capturer Ctrl+C
trap cleanup SIGINT SIGTERM

# Vérifier les prérequis
log "Vérification des prérequis..."

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    error "Python 3 n'est pas installé"
    exit 1
fi

# Vérifier Node.js
if ! command -v node &> /dev/null; then
    error "Node.js n'est pas installé"
    exit 1
fi

# Vérifier npm
if ! command -v npm &> /dev/null; then
    error "npm n'est pas installé"
    exit 1
fi

log "✅ Prérequis validés"

# Créer l'environnement de test
log "Configuration de l'environnement de test..."

cd /home/walid/peproscolaire/backend

# Créer le fichier .env pour le mode démo
cat > .env.demo << EOF
# Configuration démo PeproScolaire
DEBUG=True
SECRET_KEY=demo-secret-key-for-testing-only
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# CORS pour le frontend
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
CORS_ALLOW_CREDENTIALS=True

# Base de données SQLite pour la démo
DATABASE_URL=sqlite:///demo_peproscolaire.db

# Cache en mémoire
CACHE_URL=locmem://

# Email de test
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Désactiver Celery pour la démo
USE_CELERY=False

# Media files
MEDIA_ROOT=/home/walid/peproscolaire/backend/media
MEDIA_URL=/media/
EOF

export ENV_FILE=.env.demo

# Utiliser l'environnement virtuel existant
VENV_PATH="/home/walid/peproscolaire/backend_env"

if [ ! -d "$VENV_PATH" ]; then
    log "Création de l'environnement virtuel Python..."
    cd /home/walid/peproscolaire
    python3 -m venv backend_env
    cd backend
fi

# Activer l'environnement virtuel
source $VENV_PATH/bin/activate

# Installer les dépendances minimales
log "Installation des dépendances Python..."
pip install -q Django==5.0.1 djangorestframework==3.14.0 django-cors-headers==4.3.1 django-environ==0.11.2 djangorestframework-simplejwt==5.3.1

# Migrations
log "Application des migrations..."
python manage.py makemigrations --verbosity=0 2>/dev/null || true
python manage.py migrate --verbosity=0

# Créer un superutilisateur de démo
log "Création de l'utilisateur de démo..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='demo@peproscolaire.fr').exists():
    user = User.objects.create_superuser(
        email='demo@peproscolaire.fr',
        password='demo123',
        first_name='Utilisateur',
        last_name='Démo',
        user_type='teacher'
    )
    print('Utilisateur démo créé: demo@peproscolaire.fr / demo123')
else:
    print('Utilisateur démo existe déjà')
" 2>/dev/null

# Démarrer le backend
log "Démarrage du serveur Django..."
python manage.py runserver 127.0.0.1:8000 > /dev/null 2>&1 &
BACKEND_PID=$!

# Attendre que le backend soit prêt
log "Attente du démarrage du backend..."
for i in {1..30}; do
    if curl -s http://127.0.0.1:8000/api/v1/auth/health/ > /dev/null 2>&1; then
        log "✅ Backend prêt sur http://127.0.0.1:8000"
        break
    fi
    sleep 1
done

# Test de connexion au backend
if ! curl -s http://127.0.0.1:8000/api/v1/auth/health/ > /dev/null 2>&1; then
    error "Le backend ne répond pas"
    cleanup
    exit 1
fi

# Préparer le frontend
log "Préparation du frontend..."
cd /home/walid/peproscolaire/frontend/peproscolaire-ui

# Vérifier/installer les dépendances Node.js
if [ ! -d "node_modules" ]; then
    log "Installation des dépendances Node.js..."
    npm install > /dev/null 2>&1
fi

# Créer le fichier de configuration pour pointer vers notre backend
cat > .env.local << EOF
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
VITE_APP_TITLE=PeproScolaire - Démo
EOF

# Démarrer le frontend
log "Démarrage du serveur de développement Vite..."
npm run dev > /dev/null 2>&1 &
FRONTEND_PID=$!

# Attendre que le frontend soit prêt
log "Attente du démarrage du frontend..."
for i in {1..30}; do
    if curl -s http://127.0.0.1:5173 > /dev/null 2>&1; then
        log "✅ Frontend prêt sur http://127.0.0.1:5173"
        break
    fi
    sleep 1
done

# Vérifications finales
log "Vérifications finales..."
if curl -s http://127.0.0.1:5173 > /dev/null 2>&1; then
    echo ""
    echo "🎉 PeproScolaire est maintenant accessible !"
    echo "=========================================="
    echo ""
    echo -e "${BLUE}🌐 Interface Web:${NC} http://127.0.0.1:5173"
    echo -e "${BLUE}🔧 API Backend:${NC}  http://127.0.0.1:8000"
    echo ""
    echo -e "${GREEN}👤 Connexion de démo:${NC}"
    echo "   Email:    demo@peproscolaire.fr"
    echo "   Mot de passe: demo123"
    echo ""
    echo -e "${YELLOW}📱 Modules disponibles:${NC}"
    echo "   • Tableau de bord"
    echo "   • Notes et évaluations"
    echo "   • Emploi du temps"
    echo "   • Vie scolaire"
    echo "   • Devoirs"
    echo "   • Messagerie"
    echo "   • Dossiers élèves"
    echo "   • Détection des risques"
    echo ""
    echo -e "${RED}⏹️  Pour arrêter:${NC} Appuyez sur Ctrl+C"
    echo ""
    
    # Ouvrir le navigateur (optionnel)
    if command -v xdg-open &> /dev/null; then
        log "Ouverture du navigateur..."
        xdg-open http://127.0.0.1:5173 2>/dev/null || true
    elif command -v open &> /dev/null; then
        log "Ouverture du navigateur..."
        open http://127.0.0.1:5173 2>/dev/null || true
    fi
    
    # Garder le script en vie
    while true; do
        sleep 1
        
        # Vérifier que les services sont toujours en vie
        if ! kill -0 $BACKEND_PID 2>/dev/null; then
            error "Le backend s'est arrêté"
            cleanup
            exit 1
        fi
        
        if ! kill -0 $FRONTEND_PID 2>/dev/null; then
            error "Le frontend s'est arrêté"
            cleanup
            exit 1
        fi
    done
else
    error "Le frontend ne répond pas"
    cleanup
    exit 1
fi