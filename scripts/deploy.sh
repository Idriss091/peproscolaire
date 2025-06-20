#!/bin/bash

# Script de déploiement automatique pour PeproScolaire
# Usage: ./scripts/deploy.sh [staging|production] [--update|--fresh|--rollback]

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables par défaut
ENVIRONMENT=${1:-staging}
ACTION=${2:-update}
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="$PROJECT_ROOT/backups"
LOG_FILE="$PROJECT_ROOT/logs/deploy-$(date +%Y%m%d-%H%M%S).log"

# Fonctions utilitaires
print_header() {
    echo -e "${BLUE}===========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Vérification des prérequis
check_prerequisites() {
    print_info "Vérification des prérequis..."
    
    # Vérifier Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker n'est pas installé"
        exit 1
    fi
    
    # Vérifier Docker Compose
    if ! docker compose version &> /dev/null; then
        print_error "Docker Compose n'est pas installé"
        exit 1
    fi
    
    # Vérifier le fichier d'environnement
    if [ ! -f "$PROJECT_ROOT/.env.$ENVIRONMENT" ]; then
        print_error "Fichier .env.$ENVIRONMENT manquant"
        print_info "Copiez .env.$ENVIRONMENT.example et configurez vos valeurs"
        exit 1
    fi
    
    # Créer les répertoires nécessaires
    mkdir -p "$BACKUP_DIR" "$(dirname "$LOG_FILE")"
    
    print_success "Prérequis vérifiés"
}

# Sauvegarde de la base de données
backup_database() {
    if [ "$ACTION" = "fresh" ]; then
        print_info "Mode fresh : pas de sauvegarde nécessaire"
        return
    fi
    
    print_info "Sauvegarde de la base de données..."
    
    local backup_file="$BACKUP_DIR/db-backup-$(date +%Y%m%d-%H%M%S).sql"
    
    # Vérifier si le conteneur de base de données existe
    if docker compose -f docker-compose.$ENVIRONMENT.yml ps database | grep -q "Up"; then
        docker compose -f docker-compose.$ENVIRONMENT.yml exec -T database \
            pg_dump -U "${DATABASE_USER:-pepro}" "${DATABASE_NAME:-peproscolaire}" > "$backup_file"
        
        if [ $? -eq 0 ]; then
            print_success "Base de données sauvegardée : $backup_file"
            echo "$backup_file" > "$BACKUP_DIR/latest-backup.txt"
        else
            print_warning "Échec de la sauvegarde de la base de données"
        fi
    else
        print_info "Base de données non démarrée, pas de sauvegarde possible"
    fi
}

# Restauration de la base de données
restore_database() {
    local backup_file=${1:-$(cat "$BACKUP_DIR/latest-backup.txt" 2>/dev/null)}
    
    if [ -z "$backup_file" ] || [ ! -f "$backup_file" ]; then
        print_error "Fichier de sauvegarde non trouvé : $backup_file"
        return 1
    fi
    
    print_info "Restauration de la base de données depuis $backup_file..."
    
    # Arrêter l'application
    docker compose -f docker-compose.$ENVIRONMENT.yml stop backend celery_worker celery_beat
    
    # Restaurer la base de données
    docker compose -f docker-compose.$ENVIRONMENT.yml exec -T database \
        psql -U "${DATABASE_USER:-pepro}" -d "${DATABASE_NAME:-peproscolaire}" < "$backup_file"
    
    if [ $? -eq 0 ]; then
        print_success "Base de données restaurée"
    else
        print_error "Échec de la restauration"
        return 1
    fi
}

# Construction des images
build_images() {
    print_info "Construction des images Docker..."
    
    # Construction avec cache si possible
    docker compose -f docker-compose.$ENVIRONMENT.yml build \
        --parallel \
        --progress=auto
    
    if [ $? -eq 0 ]; then
        print_success "Images construites avec succès"
    else
        print_error "Échec de la construction des images"
        exit 1
    fi
}

# Déploiement des services
deploy_services() {
    print_info "Déploiement des services..."
    
    # Variables d'environnement
    export COMPOSE_FILE="docker-compose.$ENVIRONMENT.yml"
    export COMPOSE_PROJECT_NAME="peproscolaire_$ENVIRONMENT"
    
    case "$ACTION" in
        "fresh")
            print_info "Déploiement fresh - suppression des données existantes"
            docker compose down -v --remove-orphans
            docker compose up -d --force-recreate
            ;;
        "update")
            print_info "Mise à jour des services"
            # Mise à jour progressive pour éviter les interruptions
            docker compose up -d --no-deps database redis
            sleep 10
            docker compose up -d --no-deps backend
            sleep 5
            docker compose up -d --no-deps celery_worker celery_beat
            sleep 5
            docker compose up -d --no-deps frontend
            ;;
        "rollback")
            print_info "Rollback en cours..."
            restore_database
            # Redémarrer avec les anciennes images
            docker compose restart
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        print_success "Services déployés"
    else
        print_error "Échec du déploiement"
        exit 1
    fi
}

# Vérification de la santé des services
health_check() {
    print_info "Vérification de la santé des services..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        print_info "Tentative $attempt/$max_attempts..."
        
        # Vérifier la base de données
        if docker compose -f docker-compose.$ENVIRONMENT.yml exec -T database pg_isready -U "${DATABASE_USER:-pepro}" > /dev/null 2>&1; then
            print_success "Base de données : OK"
        else
            print_warning "Base de données : En attente..."
            sleep 2
            ((attempt++))
            continue
        fi
        
        # Vérifier Redis
        if docker compose -f docker-compose.$ENVIRONMENT.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
            print_success "Redis : OK"
        else
            print_warning "Redis : En attente..."
            sleep 2
            ((attempt++))
            continue
        fi
        
        # Vérifier le backend
        if curl -f http://localhost:8000/api/v1/health/ > /dev/null 2>&1; then
            print_success "Backend : OK"
        else
            print_warning "Backend : En attente..."
            sleep 2
            ((attempt++))
            continue
        fi
        
        # Vérifier le frontend
        if curl -f http://localhost:${FRONTEND_PORT:-80}/health > /dev/null 2>&1; then
            print_success "Frontend : OK"
        else
            print_warning "Frontend : En attente..."
            sleep 2
            ((attempt++))
            continue
        fi
        
        print_success "Tous les services sont opérationnels !"
        return 0
    done
    
    print_error "Échec de la vérification de santé après $max_attempts tentatives"
    print_info "Vérifiez les logs : docker compose -f docker-compose.$ENVIRONMENT.yml logs"
    return 1
}

# Nettoyage post-déploiement
cleanup() {
    print_info "Nettoyage post-déploiement..."
    
    # Supprimer les images inutilisées
    docker image prune -f
    
    # Supprimer les anciennes sauvegardes (garde les 10 plus récentes)
    find "$BACKUP_DIR" -name "db-backup-*.sql" -type f | sort -r | tail -n +11 | xargs rm -f
    
    print_success "Nettoyage terminé"
}

# Affichage du statut final
show_status() {
    print_header "STATUT DU DÉPLOIEMENT"
    
    echo "Environnement : $ENVIRONMENT"
    echo "Action : $ACTION"
    echo "Date : $(date)"
    echo "Log : $LOG_FILE"
    echo ""
    
    print_info "Services actifs :"
    docker compose -f docker-compose.$ENVIRONMENT.yml ps
    
    echo ""
    print_info "URLs d'accès :"
    echo "Frontend : http://localhost:${FRONTEND_PORT:-80}"
    echo "Backend API : http://localhost:8000/api/v1/"
    echo "Admin Django : http://localhost:8000/admin/"
    
    if docker compose -f docker-compose.$ENVIRONMENT.yml ps | grep -q grafana; then
        echo "Monitoring : http://localhost:3000 (admin/admin)"
    fi
}

# Gestion des signaux pour un arrêt propre
trap 'print_error "Déploiement interrompu"; exit 1' INT TERM

# Fonction principale
main() {
    print_header "DÉPLOIEMENT PEPROSCOLAIRE - $ENVIRONMENT"
    
    # Vérification des arguments
    if [[ ! "$ENVIRONMENT" =~ ^(staging|production)$ ]]; then
        print_error "Environnement invalide. Utilisez 'staging' ou 'production'"
        exit 1
    fi
    
    if [[ ! "$ACTION" =~ ^(update|fresh|rollback)$ ]]; then
        print_error "Action invalide. Utilisez 'update', 'fresh' ou 'rollback'"
        exit 1
    fi
    
    log "Début du déploiement - Environnement: $ENVIRONMENT, Action: $ACTION"
    
    # Changer vers le répertoire du projet
    cd "$PROJECT_ROOT"
    
    # Charger les variables d'environnement
    if [ -f ".env.$ENVIRONMENT" ]; then
        set -a
        source ".env.$ENVIRONMENT"
        set +a
        print_success "Variables d'environnement chargées"
    fi
    
    # Étapes du déploiement
    check_prerequisites
    
    if [ "$ACTION" != "fresh" ]; then
        backup_database
    fi
    
    build_images
    deploy_services
    
    if ! health_check; then
        print_error "Échec de la vérification de santé"
        if [ "$ACTION" = "update" ]; then
            print_info "Tentative de rollback automatique..."
            ACTION="rollback"
            deploy_services
            health_check
        fi
        exit 1
    fi
    
    cleanup
    show_status
    
    log "Déploiement terminé avec succès"
    print_success "🎉 Déploiement terminé avec succès !"
}

# Affichage de l'aide
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: $0 [staging|production] [update|fresh|rollback]"
    echo ""
    echo "Environnements :"
    echo "  staging     - Environnement de test"
    echo "  production  - Environnement de production"
    echo ""
    echo "Actions :"
    echo "  update      - Mise à jour des services (défaut)"
    echo "  fresh       - Déploiement complet (supprime les données)"
    echo "  rollback    - Retour à la version précédente"
    echo ""
    echo "Exemples :"
    echo "  $0 staging update"
    echo "  $0 production fresh"
    echo "  $0 production rollback"
    exit 0
fi

# Exécution
main "$@"