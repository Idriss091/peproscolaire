#!/bin/bash

# Script de restauration pour PeproScolaire
# Usage: ./scripts/restore.sh [environment] [backup_date] [--database-only|--volumes-only|--full]

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables par défaut
ENVIRONMENT=${1:-production}
BACKUP_DATE=${2:-latest}
RESTORE_TYPE=${3:-full}
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_BASE_DIR="${BACKUP_BASE_DIR:-$PROJECT_ROOT/backups}"
LOG_FILE="$PROJECT_ROOT/logs/restore-$(date +%Y%m%d-%H%M%S).log"

# Configuration S3 (optionnel)
S3_BUCKET=${S3_BACKUP_BUCKET:-""}
AWS_REGION=${AWS_REGION:-"eu-west-3"}

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

# Confirmation de l'utilisateur
confirm_restore() {
    echo -e "${RED}⚠️  ATTENTION: Cette opération va remplacer les données existantes!${NC}"
    echo -e "${YELLOW}Environnement: $ENVIRONMENT${NC}"
    echo -e "${YELLOW}Sauvegarde: $BACKUP_DATE${NC}"
    echo -e "${YELLOW}Type: $RESTORE_TYPE${NC}"
    echo ""
    
    read -p "Êtes-vous sûr de vouloir continuer? (oui/non): " confirm
    
    if [[ ! "$confirm" =~ ^(oui|yes|y|o)$ ]]; then
        print_info "Restauration annulée par l'utilisateur"
        exit 0
    fi
    
    print_success "Restauration confirmée"
}

# Déterminer le répertoire de sauvegarde
find_backup_directory() {
    if [ "$BACKUP_DATE" = "latest" ]; then
        # Trouver la sauvegarde la plus récente
        BACKUP_DIR=$(find "$BACKUP_BASE_DIR" -maxdepth 1 -type d -name "20*" | sort -r | head -n1)
        
        if [ -z "$BACKUP_DIR" ]; then
            print_error "Aucune sauvegarde trouvée dans $BACKUP_BASE_DIR"
            exit 1
        fi
        
        BACKUP_DATE=$(basename "$BACKUP_DIR")
        print_info "Sauvegarde la plus récente: $BACKUP_DATE"
    else
        BACKUP_DIR="$BACKUP_BASE_DIR/$BACKUP_DATE"
        
        if [ ! -d "$BACKUP_DIR" ]; then
            print_error "Sauvegarde $BACKUP_DATE non trouvée dans $BACKUP_BASE_DIR"
            
            # Essayer de télécharger depuis S3
            if [ -n "$S3_BUCKET" ] && command -v aws &> /dev/null; then
                print_info "Tentative de téléchargement depuis S3..."
                download_from_s3
            else
                exit 1
            fi
        fi
    fi
    
    print_success "Répertoire de sauvegarde: $BACKUP_DIR"
}

# Téléchargement depuis S3
download_from_s3() {
    if [ -z "$S3_BUCKET" ]; then
        print_error "Pas de bucket S3 configuré"
        return 1
    fi
    
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI non installé"
        return 1
    fi
    
    print_info "Téléchargement depuis S3..."
    
    local s3_path="s3://$S3_BUCKET/peproscolaire/$ENVIRONMENT/$BACKUP_DATE"
    
    # Créer le répertoire local
    mkdir -p "$BACKUP_DIR"
    
    # Télécharger la sauvegarde
    aws s3 sync "$s3_path" "$BACKUP_DIR" \
        --region "$AWS_REGION"
    
    if [ $? -eq 0 ]; then
        print_success "Sauvegarde téléchargée depuis S3"
    else
        print_error "Échec du téléchargement depuis S3"
        return 1
    fi
}

# Arrêt des services
stop_services() {
    print_info "Arrêt des services..."
    
    # Arrêter les services de l'application (sauf la DB pour la restauration)
    case "$RESTORE_TYPE" in
        "database-only")
            docker compose -f docker-compose.$ENVIRONMENT.yml stop backend celery_worker celery_beat
            ;;
        "volumes-only")
            docker compose -f docker-compose.$ENVIRONMENT.yml stop backend celery_worker celery_beat frontend
            ;;
        "full")
            docker compose -f docker-compose.$ENVIRONMENT.yml stop
            ;;
    esac
    
    print_success "Services arrêtés"
}

# Restauration de la base de données
restore_database() {
    if [[ "$RESTORE_TYPE" == "volumes-only" ]]; then
        print_info "Saut de la restauration de la base de données (volumes-only)"
        return 0
    fi
    
    print_info "Restauration de la base de données..."
    
    # Trouver le fichier de sauvegarde
    local backup_file=$(find "$BACKUP_DIR/database" -name "*.custom" | head -n1)
    
    if [ -z "$backup_file" ]; then
        print_error "Fichier de sauvegarde de base de données non trouvé"
        return 1
    fi
    
    print_info "Fichier de sauvegarde: $(basename "$backup_file")"
    
    # S'assurer que la base de données est démarrée
    docker compose -f docker-compose.$ENVIRONMENT.yml up -d database
    
    # Attendre que la base de données soit prête
    print_info "Attente de la disponibilité de la base de données..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker compose -f docker-compose.$ENVIRONMENT.yml exec -T database pg_isready -U "${DATABASE_USER:-pepro}" > /dev/null 2>&1; then
            break
        fi
        
        print_info "Tentative $attempt/$max_attempts..."
        sleep 2
        ((attempt++))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        print_error "Impossible de se connecter à la base de données"
        return 1
    fi
    
    print_success "Base de données disponible"
    
    # Copier le fichier de sauvegarde dans le conteneur
    docker cp "$backup_file" "$(docker compose -f docker-compose.$ENVIRONMENT.yml ps -q database):/tmp/restore.custom"
    
    # Supprimer et recréer la base de données
    print_info "Suppression et recréation de la base de données..."
    docker compose -f docker-compose.$ENVIRONMENT.yml exec -T database psql -U "${DATABASE_USER:-pepro}" -d postgres -c "DROP DATABASE IF EXISTS \"${DATABASE_NAME:-peproscolaire}\";"
    docker compose -f docker-compose.$ENVIRONMENT.yml exec -T database psql -U "${DATABASE_USER:-pepro}" -d postgres -c "CREATE DATABASE \"${DATABASE_NAME:-peproscolaire}\";"
    
    # Restaurer la base de données
    print_info "Restauration des données..."
    docker compose -f docker-compose.$ENVIRONMENT.yml exec -T database \
        pg_restore -U "${DATABASE_USER:-pepro}" \
        -d "${DATABASE_NAME:-peproscolaire}" \
        --verbose --clean --if-exists --no-owner --no-privileges \
        /tmp/restore.custom
    
    if [ $? -eq 0 ]; then
        print_success "Base de données restaurée avec succès"
        
        # Nettoyer le fichier temporaire
        docker compose -f docker-compose.$ENVIRONMENT.yml exec -T database rm -f /tmp/restore.custom
        
        return 0
    else
        print_error "Échec de la restauration de la base de données"
        return 1
    fi
}

# Restauration des volumes Docker
restore_volumes() {
    if [[ "$RESTORE_TYPE" == "database-only" ]]; then
        print_info "Saut de la restauration des volumes (database-only)"
        return 0
    fi
    
    print_info "Restauration des volumes Docker..."
    
    local volumes=("static_files" "media_files" "backend_logs" "frontend_logs")
    
    for volume in "${volumes[@]}"; do
        local volume_name="${ENVIRONMENT}_${volume}"
        local backup_file=$(find "$BACKUP_DIR/volumes" -name "${volume}-*.tar.gz" | head -n1)
        
        if [ -z "$backup_file" ]; then
            print_warning "Sauvegarde du volume $volume non trouvée"
            continue
        fi
        
        print_info "Restauration du volume $volume_name..."
        
        # Supprimer le volume existant
        docker volume rm "$volume_name" 2>/dev/null || true
        
        # Recréer le volume et restaurer les données
        docker run --rm \
            -v "${volume_name}:/data" \
            -v "$BACKUP_DIR/volumes:/backup:ro" \
            alpine:latest \
            sh -c "cd /data && tar xzf /backup/$(basename "$backup_file")"
        
        if [ $? -eq 0 ]; then
            print_success "Volume $volume restauré"
        else
            print_error "Échec de la restauration du volume $volume"
        fi
    done
}

# Restauration des configurations
restore_configurations() {
    if [[ "$RESTORE_TYPE" == "database-only" ]] || [[ "$RESTORE_TYPE" == "volumes-only" ]]; then
        print_info "Saut de la restauration des configurations"
        return 0
    fi
    
    print_info "Restauration des fichiers de configuration..."
    
    if [ ! -d "$BACKUP_DIR/configs" ]; then
        print_warning "Pas de configurations sauvegardées"
        return 0
    fi
    
    # Sauvegarder les configurations actuelles
    local config_backup_dir="$PROJECT_ROOT/configs-backup-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$config_backup_dir"
    
    local config_files=(
        ".env.$ENVIRONMENT"
        "docker-compose.$ENVIRONMENT.yml"
        "nginx"
        "monitoring"
    )
    
    for config in "${config_files[@]}"; do
        if [ -e "$PROJECT_ROOT/$config" ]; then
            cp -r "$PROJECT_ROOT/$config" "$config_backup_dir/"
        fi
    done
    
    print_info "Configurations actuelles sauvegardées dans $config_backup_dir"
    
    # Restaurer les configurations
    for config in "${config_files[@]}"; do
        if [ -e "$BACKUP_DIR/configs/$config" ]; then
            cp -r "$BACKUP_DIR/configs/$config" "$PROJECT_ROOT/"
            print_success "Configuration $config restaurée"
        fi
    done
}

# Redémarrage des services
restart_services() {
    print_info "Redémarrage des services..."
    
    # Démarrer tous les services
    docker compose -f docker-compose.$ENVIRONMENT.yml up -d
    
    print_success "Services redémarrés"
}

# Vérification de la restauration
verify_restore() {
    print_info "Vérification de la restauration..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        print_info "Vérification $attempt/$max_attempts..."
        
        # Vérifier la base de données
        if [[ "$RESTORE_TYPE" != "volumes-only" ]]; then
            if ! docker compose -f docker-compose.$ENVIRONMENT.yml exec -T database pg_isready -U "${DATABASE_USER:-pepro}" > /dev/null 2>&1; then
                print_warning "Base de données : En attente..."
                sleep 3
                ((attempt++))
                continue
            fi
            print_success "Base de données : OK"
        fi
        
        # Vérifier le backend
        if curl -f http://localhost:8000/api/v1/health/ > /dev/null 2>&1; then
            print_success "Backend : OK"
        else
            print_warning "Backend : En attente..."
            sleep 3
            ((attempt++))
            continue
        fi
        
        # Vérifier le frontend
        if curl -f http://localhost:${FRONTEND_PORT:-80}/health > /dev/null 2>&1; then
            print_success "Frontend : OK"
        else
            print_warning "Frontend : En attente..."
            sleep 3
            ((attempt++))
            continue
        fi
        
        print_success "🎉 Restauration vérifiée avec succès!"
        return 0
    done
    
    print_error "Échec de la vérification après $max_attempts tentatives"
    print_info "Vérifiez les logs : docker compose -f docker-compose.$ENVIRONMENT.yml logs"
    return 1
}

# Génération du rapport de restauration
generate_restore_report() {
    local report_file="$PROJECT_ROOT/logs/restore-report-$(date +%Y%m%d-%H%M%S).txt"
    
    cat > "$report_file" << EOF
===========================================
RAPPORT DE RESTAURATION PEPROSCOLAIRE
===========================================

Date de restauration: $(date)
Environnement: $ENVIRONMENT
Sauvegarde utilisée: $BACKUP_DATE
Type de restauration: $RESTORE_TYPE

Source de la sauvegarde: $BACKUP_DIR

Composants restaurés:
- Base de données: $([ "$RESTORE_TYPE" != "volumes-only" ] && echo "✓" || echo "✗")
- Volumes Docker: $([ "$RESTORE_TYPE" != "database-only" ] && echo "✓" || echo "✗")
- Configurations: $([ "$RESTORE_TYPE" = "full" ] && echo "✓" || echo "✗")

État des services:
$(docker compose -f docker-compose.$ENVIRONMENT.yml ps)

Vérifications post-restauration:
- Backend disponible: $(curl -f http://localhost:8000/api/v1/health/ &>/dev/null && echo "✓" || echo "✗")
- Frontend disponible: $(curl -f http://localhost:${FRONTEND_PORT:-80}/health &>/dev/null && echo "✓" || echo "✗")

===========================================
EOF

    print_success "Rapport généré: $report_file"
}

# Fonction principale
main() {
    print_header "RESTAURATION PEPROSCOLAIRE - $ENVIRONMENT"
    
    # Vérification des arguments
    if [[ ! "$ENVIRONMENT" =~ ^(staging|production)$ ]]; then
        print_error "Environnement invalide. Utilisez 'staging' ou 'production'"
        exit 1
    fi
    
    if [[ ! "$RESTORE_TYPE" =~ ^(full|database-only|volumes-only)$ ]]; then
        print_error "Type de restauration invalide. Utilisez 'full', 'database-only' ou 'volumes-only'"
        exit 1
    fi
    
    log "Début de la restauration - Environnement: $ENVIRONMENT, Type: $RESTORE_TYPE"
    
    # Changer vers le répertoire du projet
    cd "$PROJECT_ROOT"
    
    # Charger les variables d'environnement
    if [ -f ".env.$ENVIRONMENT" ]; then
        set -a
        source ".env.$ENVIRONMENT"
        set +a
        print_success "Variables d'environnement chargées"
    fi
    
    # Créer le répertoire de logs
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Exécution de la restauration
    find_backup_directory
    confirm_restore
    stop_services
    
    if [[ "$RESTORE_TYPE" != "volumes-only" ]]; then
        restore_database
    fi
    
    if [[ "$RESTORE_TYPE" != "database-only" ]]; then
        restore_volumes
    fi
    
    if [[ "$RESTORE_TYPE" == "full" ]]; then
        restore_configurations
    fi
    
    restart_services
    
    if verify_restore; then
        generate_restore_report
        log "Restauration terminée avec succès"
        print_success "🎉 Restauration terminée avec succès!"
        
        print_info "URLs d'accès :"
        echo "Frontend : http://localhost:${FRONTEND_PORT:-80}"
        echo "Backend API : http://localhost:8000/api/v1/"
        echo "Admin Django : http://localhost:8000/admin/"
    else
        print_error "Échec de la vérification de la restauration"
        exit 1
    fi
}

# Affichage de l'aide
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: $0 [staging|production] [backup_date|latest] [full|database-only|volumes-only]"
    echo ""
    echo "Environnements :"
    echo "  staging     - Environnement de test"
    echo "  production  - Environnement de production"
    echo ""
    echo "Date de sauvegarde :"
    echo "  latest      - Dernière sauvegarde disponible (défaut)"
    echo "  YYYYMMDD    - Date spécifique (ex: 20241220)"
    echo ""
    echo "Types de restauration :"
    echo "  full            - Restauration complète (défaut)"
    echo "  database-only   - Base de données seulement"
    echo "  volumes-only    - Volumes Docker seulement"
    echo ""
    echo "Variables d'environnement :"
    echo "  BACKUP_BASE_DIR     - Répertoire de base des sauvegardes"
    echo "  S3_BACKUP_BUCKET    - Bucket S3 pour le téléchargement (optionnel)"
    echo "  AWS_REGION          - Région AWS (défaut: eu-west-3)"
    echo ""
    echo "Exemples :"
    echo "  $0 production latest full"
    echo "  $0 staging 20241220 database-only"
    echo "  $0 production latest volumes-only"
    exit 0
fi

# Gestion des signaux pour un arrêt propre
trap 'print_error "Restauration interrompue"; exit 1' INT TERM

# Exécution
main "$@"