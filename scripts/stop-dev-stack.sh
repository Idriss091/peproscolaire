#!/bin/bash

# Script d'arrêt de la stack de développement PeproScolaire
# Usage: ./scripts/stop-dev-stack.sh

set -e

echo "🛑 Arrêt de la stack PeproScolaire"
echo "=================================="

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] WARNING:${NC} $1"
}

cd /home/walid/peproscolaire

# Arrêter le serveur Django
if [ -f logs/django.pid ]; then
    DJANGO_PID=$(cat logs/django.pid)
    if kill -0 $DJANGO_PID 2>/dev/null; then
        log "Arrêt du serveur Django (PID: $DJANGO_PID)..."
        kill $DJANGO_PID
        rm -f logs/django.pid
        log "✅ Serveur Django arrêté"
    else
        warn "Le serveur Django n'était pas en cours d'exécution"
        rm -f logs/django.pid
    fi
else
    warn "Fichier PID Django non trouvé"
fi

# Arrêter le serveur Vite
if [ -f logs/vite.pid ]; then
    VITE_PID=$(cat logs/vite.pid)
    if kill -0 $VITE_PID 2>/dev/null; then
        log "Arrêt du serveur Vite (PID: $VITE_PID)..."
        kill $VITE_PID
        rm -f logs/vite.pid
        log "✅ Serveur Vite arrêté"
    else
        warn "Le serveur Vite n'était pas en cours d'exécution"
        rm -f logs/vite.pid
    fi
else
    warn "Fichier PID Vite non trouvé"
fi

# Arrêter les services Docker
log "Arrêt des services Docker..."
if [ -f docker-compose.yml ]; then
    docker-compose down --remove-orphans
    log "✅ Services Docker arrêtés"
else
    warn "Fichier docker-compose.yml non trouvé"
fi

# Nettoyer les fichiers temporaires
log "Nettoyage des fichiers temporaires..."
rm -f logs/*.pid
rm -f logs/*.log

log "🛑 Stack PeproScolaire complètement arrêtée"