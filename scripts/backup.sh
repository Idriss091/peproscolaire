#!/bin/bash

# Script de sauvegarde automatique pour PeproScolaire
# Usage: ./scripts/backup.sh [environment] [--full|--incremental]

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables par défaut
ENVIRONMENT=${1:-production}
BACKUP_TYPE=${2:-incremental}
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_BASE_DIR="${BACKUP_BASE_DIR:-$PROJECT_ROOT/backups}"
BACKUP_DIR="$BACKUP_BASE_DIR/$(date +%Y%m%d)"
LOG_FILE="$PROJECT_ROOT/logs/backup-$(date +%Y%m%d-%H%M%S).log"
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}

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

# Création des répertoires de sauvegarde
setup_backup_directories() {
    print_info "Création des répertoires de sauvegarde..."
    
    mkdir -p "$BACKUP_DIR"/{database,volumes,configs,logs}
    mkdir -p "$(dirname "$LOG_FILE")"
    
    print_success "Répertoires créés dans $BACKUP_DIR"
}

# Sauvegarde de la base de données
backup_database() {
    print_info "Sauvegarde de la base de données..."
    
    local backup_file="$BACKUP_DIR/database/peproscolaire-$(date +%Y%m%d-%H%M%S).sql"
    local backup_custom_file="$BACKUP_DIR/database/peproscolaire-$(date +%Y%m%d-%H%M%S).custom"
    
    # Vérifier si le conteneur de base de données est actif
    if ! docker compose -f docker-compose.$ENVIRONMENT.yml ps database | grep -q "Up"; then
        print_error "Le conteneur de base de données n'est pas actif"
        return 1
    fi
    
    # Sauvegarde au format SQL (lisible)
    log "Création de la sauvegarde SQL..."
    docker compose -f docker-compose.$ENVIRONMENT.yml exec -T database \
        pg_dump -U "${DATABASE_USER:-pepro}" \
        -d "${DATABASE_NAME:-peproscolaire}" \
        --verbose --clean --if-exists --create > "$backup_file"
    
    # Sauvegarde au format custom (optimisé)
    log "Création de la sauvegarde au format custom..."
    docker compose -f docker-compose.$ENVIRONMENT.yml exec -T database \
        pg_dump -U "${DATABASE_USER:-pepro}" \
        -d "${DATABASE_NAME:-peproscolaire}" \
        --format=custom --verbose --clean --if-exists --create > "$backup_custom_file"
    
    if [ $? -eq 0 ]; then
        # Compression des sauvegardes
        gzip "$backup_file"
        
        local backup_size=$(du -h "$backup_custom_file" | cut -f1)
        print_success "Base de données sauvegardée (${backup_size})"
        
        # Créer un lien vers la dernière sauvegarde
        ln -sf "$backup_custom_file" "$BACKUP_BASE_DIR/latest-database-backup.custom"
        ln -sf "$backup_file.gz" "$BACKUP_BASE_DIR/latest-database-backup.sql.gz"
        
        return 0
    else
        print_error "Échec de la sauvegarde de la base de données"
        return 1
    fi
}

# Sauvegarde des volumes Docker
backup_volumes() {
    print_info "Sauvegarde des volumes Docker..."
    
    local volumes=("static_files" "media_files" "backend_logs" "frontend_logs")
    
    for volume in "${volumes[@]}"; do
        local volume_name="${ENVIRONMENT}_${volume}"
        local backup_file="$BACKUP_DIR/volumes/${volume}-$(date +%Y%m%d-%H%M%S).tar.gz"
        
        log "Sauvegarde du volume $volume_name..."
        
        # Créer une sauvegarde du volume via un conteneur temporaire
        docker run --rm \
            -v "${volume_name}:/data:ro" \
            -v "$BACKUP_DIR/volumes:/backup" \
            alpine:latest \
            tar czf "/backup/$(basename "$backup_file")" -C /data .
        
        if [ $? -eq 0 ]; then
            local volume_size=$(du -h "$backup_file" | cut -f1)
            print_success "Volume $volume sauvegardé (${volume_size})"
        else
            print_warning "Échec de la sauvegarde du volume $volume"
        fi
    done
}

# Sauvegarde des configurations
backup_configurations() {
    print_info "Sauvegarde des fichiers de configuration..."
    
    local config_files=(
        ".env.$ENVIRONMENT"
        "docker-compose.$ENVIRONMENT.yml"
        "nginx/nginx.conf"
        "nginx/conf.d/"
        "monitoring/"
    )
    
    for config in "${config_files[@]}"; do
        if [ -e "$PROJECT_ROOT/$config" ]; then
            cp -r "$PROJECT_ROOT/$config" "$BACKUP_DIR/configs/"
            print_success "Configuration $config sauvegardée"
        else
            print_warning "Configuration $config non trouvée"
        fi
    done
}

# Sauvegarde des logs
backup_logs() {
    print_info "Sauvegarde des logs..."
    
    # Copier les logs du projet
    if [ -d "$PROJECT_ROOT/logs" ]; then
        cp -r "$PROJECT_ROOT/logs" "$BACKUP_DIR/"
        print_success "Logs du projet sauvegardés"
    fi
    
    # Exporter les logs des conteneurs Docker
    local containers=$(docker compose -f docker-compose.$ENVIRONMENT.yml ps --services)
    
    for container in $containers; do
        local log_file="$BACKUP_DIR/logs/docker-${container}-$(date +%Y%m%d-%H%M%S).log"
        docker compose -f docker-compose.$ENVIRONMENT.yml logs --no-color "$container" > "$log_file" 2>/dev/null
        
        if [ -s "$log_file" ]; then
            gzip "$log_file"
            print_success "Logs du conteneur $container sauvegardés"
        else
            rm -f "$log_file"
        fi
    done
}

# Upload vers S3 (optionnel)
upload_to_s3() {
    if [ -z "$S3_BUCKET" ]; then
        print_info "Pas de bucket S3 configuré, saut de l'upload"
        return 0
    fi
    
    if ! command -v aws &> /dev/null; then
        print_warning "AWS CLI non installé, saut de l'upload S3"
        return 0
    fi
    
    print_info "Upload vers S3 bucket: $S3_BUCKET"
    
    local s3_path="s3://$S3_BUCKET/peproscolaire/$ENVIRONMENT/$(basename "$BACKUP_DIR")"
    
    aws s3 sync "$BACKUP_DIR" "$s3_path" \
        --region "$AWS_REGION" \
        --storage-class STANDARD_IA \
        --delete
    
    if [ $? -eq 0 ]; then
        print_success "Sauvegarde uploadée vers S3: $s3_path"
    else
        print_error "Échec de l'upload vers S3"
        return 1
    fi
}

# Nettoyage des anciennes sauvegardes
cleanup_old_backups() {
    print_info "Nettoyage des anciennes sauvegardes (> $RETENTION_DAYS jours)..."
    
    # Nettoyage local
    find "$BACKUP_BASE_DIR" -maxdepth 1 -type d -name "20*" -mtime +$RETENTION_DAYS -exec rm -rf {} \;
    
    local cleaned=$(find "$BACKUP_BASE_DIR" -maxdepth 1 -type d -name "20*" -mtime +$RETENTION_DAYS | wc -l)
    print_success "$cleaned anciennes sauvegardes supprimées"
    
    # Nettoyage S3 (si configuré)
    if [ -n "$S3_BUCKET" ] && command -v aws &> /dev/null; then
        aws s3api list-objects-v2 \
            --bucket "$S3_BUCKET" \
            --prefix "peproscolaire/$ENVIRONMENT/" \
            --query "Contents[?LastModified<='$(date -d "$RETENTION_DAYS days ago" --iso-8601)'].Key" \
            --output text | xargs -r aws s3 rm --bucket "$S3_BUCKET"
    fi
}

# Vérification de l'intégrité des sauvegardes
verify_backup_integrity() {
    print_info "Vérification de l'intégrité des sauvegardes..."
    
    local database_backup="$BACKUP_DIR/database/peproscolaire-"*".custom"
    
    if [ -f $database_backup ]; then
        # Test de la sauvegarde avec pg_restore --list
        docker run --rm \
            -v "$BACKUP_DIR/database:/backup:ro" \
            postgres:15-alpine \
            pg_restore --list "/backup/$(basename $database_backup)" > /dev/null
        
        if [ $? -eq 0 ]; then
            print_success "Intégrité de la sauvegarde database vérifiée"
        else
            print_error "Sauvegarde database corrompue!"
            return 1
        fi
    fi
    
    # Vérifier les volumes compressés
    for volume_backup in "$BACKUP_DIR/volumes"/*.tar.gz; do
        if [ -f "$volume_backup" ]; then
            if gzip -t "$volume_backup" 2>/dev/null; then
                print_success "Intégrité vérifiée: $(basename "$volume_backup")"
            else
                print_error "Archive corrompue: $(basename "$volume_backup")"
            fi
        fi
    done
}

# Génération du rapport de sauvegarde
generate_backup_report() {
    local report_file="$BACKUP_DIR/backup-report.txt"
    local total_size=$(du -sh "$BACKUP_DIR" | cut -f1)
    
    cat > "$report_file" << EOF
===========================================
RAPPORT DE SAUVEGARDE PEPROSCOLAIRE
===========================================

Date: $(date)
Environnement: $ENVIRONMENT
Type: $BACKUP_TYPE
Taille totale: $total_size

Contenu de la sauvegarde:
$(find "$BACKUP_DIR" -type f -exec ls -lh {} \; | awk '{print $9 " (" $5 ")"}')

Vérifications:
- Base de données: $([ -f "$BACKUP_DIR"/database/*.custom ] && echo "✓" || echo "✗")
- Volumes: $([ -n "$(ls -A "$BACKUP_DIR"/volumes/ 2>/dev/null)" ] && echo "✓" || echo "✗")
- Configurations: $([ -n "$(ls -A "$BACKUP_DIR"/configs/ 2>/dev/null)" ] && echo "✓" || echo "✗")
- Logs: $([ -n "$(ls -A "$BACKUP_DIR"/logs/ 2>/dev/null)" ] && echo "✓" || echo "✗")

Upload S3: $([ -n "$S3_BUCKET" ] && echo "Configuré" || echo "Non configuré")

===========================================
EOF

    print_success "Rapport généré: $report_file"
}

# Fonction principale
main() {
    print_header "SAUVEGARDE PEPROSCOLAIRE - $ENVIRONMENT"
    
    # Vérification des arguments
    if [[ ! "$ENVIRONMENT" =~ ^(staging|production)$ ]]; then
        print_error "Environnement invalide. Utilisez 'staging' ou 'production'"
        exit 1
    fi
    
    if [[ ! "$BACKUP_TYPE" =~ ^(full|incremental)$ ]]; then
        print_error "Type de sauvegarde invalide. Utilisez 'full' ou 'incremental'"
        exit 1
    fi
    
    log "Début de la sauvegarde - Environnement: $ENVIRONMENT, Type: $BACKUP_TYPE"
    
    # Changer vers le répertoire du projet
    cd "$PROJECT_ROOT"
    
    # Charger les variables d'environnement
    if [ -f ".env.$ENVIRONMENT" ]; then
        set -a
        source ".env.$ENVIRONMENT"
        set +a
        print_success "Variables d'environnement chargées"
    fi
    
    # Exécution des sauvegardes
    setup_backup_directories
    
    if backup_database; then
        backup_volumes
        backup_configurations
        backup_logs
        verify_backup_integrity
        upload_to_s3
        cleanup_old_backups
        generate_backup_report
        
        log "Sauvegarde terminée avec succès"
        print_success "🎉 Sauvegarde terminée avec succès dans $BACKUP_DIR"
    else
        print_error "Échec de la sauvegarde"
        exit 1
    fi
}

# Affichage de l'aide
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: $0 [staging|production] [full|incremental]"
    echo ""
    echo "Environnements :"
    echo "  staging     - Environnement de test"
    echo "  production  - Environnement de production"
    echo ""
    echo "Types de sauvegarde :"
    echo "  full        - Sauvegarde complète (défaut)"
    echo "  incremental - Sauvegarde incrémentale"
    echo ""
    echo "Variables d'environnement :"
    echo "  BACKUP_BASE_DIR          - Répertoire de base des sauvegardes"
    echo "  BACKUP_RETENTION_DAYS    - Nombre de jours de rétention (défaut: 30)"
    echo "  S3_BACKUP_BUCKET         - Bucket S3 pour l'upload (optionnel)"
    echo "  AWS_REGION               - Région AWS (défaut: eu-west-3)"
    echo ""
    echo "Exemples :"
    echo "  $0 production full"
    echo "  $0 staging incremental"
    echo "  BACKUP_RETENTION_DAYS=7 $0 staging full"
    exit 0
fi

# Gestion des signaux pour un arrêt propre
trap 'print_error "Sauvegarde interrompue"; exit 1' INT TERM

# Exécution
main "$@"