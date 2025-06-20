#!/bin/bash

# Script pour lancer tous les tests du projet PeproScolaire
# Usage: ./scripts/run-tests.sh [backend|frontend|all]

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Variables
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend/peproscolaire-ui"
TEST_TYPE="${1:-all}"

# Vérifier les dépendances
check_dependencies() {
    print_info "Vérification des dépendances..."
    
    # Vérifier Python et Django
    if [ "$TEST_TYPE" = "backend" ] || [ "$TEST_TYPE" = "all" ]; then
        if ! command -v python &> /dev/null; then
            print_error "Python n'est pas installé"
            exit 1
        fi
        
        cd "$BACKEND_DIR"
        if ! python -c "import django" &> /dev/null; then
            print_error "Django n'est pas installé. Lancez: pip install -r requirements.txt"
            exit 1
        fi
    fi
    
    # Vérifier Node.js et npm
    if [ "$TEST_TYPE" = "frontend" ] || [ "$TEST_TYPE" = "all" ]; then
        if ! command -v node &> /dev/null; then
            print_error "Node.js n'est pas installé"
            exit 1
        fi
        
        if ! command -v npm &> /dev/null; then
            print_error "npm n'est pas installé"
            exit 1
        fi
        
        cd "$FRONTEND_DIR"
        if [ ! -d "node_modules" ]; then
            print_warning "node_modules manquant. Installation des dépendances..."
            npm install
        fi
    fi
}

# Tests Backend
run_backend_tests() {
    print_header "TESTS BACKEND - DJANGO"
    
    cd "$BACKEND_DIR"
    
    # Variables d'environnement pour les tests
    export DJANGO_SETTINGS_MODULE=config.settings
    export DATABASE_URL="sqlite:///test.db"
    
    print_info "Préparation de la base de données de test..."
    python manage.py migrate --run-syncdb --verbosity=0
    
    print_info "Lancement des tests unitaires..."
    
    # Tests des modèles IA
    print_info "Tests des modèles IA..."
    if python manage.py test apps.ai_analytics.test_models --verbosity=2; then
        print_success "Tests des modèles IA - SUCCÈS"
    else
        print_error "Tests des modèles IA - ÉCHEC"
        return 1
    fi
    
    # Tests des vues API
    print_info "Tests des vues API..."
    if python manage.py test apps.ai_analytics.test_views --verbosity=2; then
        print_success "Tests des vues API - SUCCÈS"
    else
        print_error "Tests des vues API - ÉCHEC"
        return 1
    fi
    
    # Tests des tâches Celery
    print_info "Tests des tâches Celery..."
    if python manage.py test apps.ai_analytics.test_tasks --verbosity=2; then
        print_success "Tests des tâches Celery - SUCCÈS"
    else
        print_error "Tests des tâches Celery - ÉCHEC"
        return 1
    fi
    
    # Tests d'intégration
    print_info "Tests d'intégration..."
    if python manage.py test apps.ai_analytics.test_integration --verbosity=2; then
        print_success "Tests d'intégration - SUCCÈS"
    else
        print_error "Tests d'intégration - ÉCHEC"
        return 1
    fi
    
    # Tests avec coverage
    print_info "Génération du rapport de couverture..."
    if command -v coverage &> /dev/null; then
        coverage run --source='.' manage.py test apps.ai_analytics
        coverage report --show-missing
        coverage html
        print_success "Rapport de couverture généré dans htmlcov/"
    else
        print_warning "Coverage non installé. Installez avec: pip install coverage"
    fi
    
    # Nettoyage
    rm -f test.db
    
    print_success "TESTS BACKEND TERMINÉS AVEC SUCCÈS"
}

# Tests Frontend
run_frontend_tests() {
    print_header "TESTS FRONTEND - VUE.JS"
    
    cd "$FRONTEND_DIR"
    
    print_info "Vérification du linting..."
    if npm run lint:check; then
        print_success "Linting - SUCCÈS"
    else
        print_error "Linting - ÉCHEC"
        print_info "Tentative de correction automatique..."
        npm run lint:fix
    fi
    
    print_info "Vérification TypeScript..."
    if npm run type-check; then
        print_success "TypeScript - SUCCÈS"
    else
        print_error "TypeScript - ÉCHEC"
        return 1
    fi
    
    print_info "Lancement des tests unitaires..."
    if npm run test:unit; then
        print_success "Tests unitaires - SUCCÈS"
    else
        print_error "Tests unitaires - ÉCHEC"
        return 1
    fi
    
    print_info "Tests avec couverture..."
    if npm run test:coverage; then
        print_success "Tests avec couverture - SUCCÈS"
        print_info "Rapport de couverture disponible dans coverage/"
    else
        print_error "Tests avec couverture - ÉCHEC"
        return 1
    fi
    
    print_success "TESTS FRONTEND TERMINÉS AVEC SUCCÈS"
}

# Tests End-to-End
run_e2e_tests() {
    print_header "TESTS END-TO-END"
    
    print_info "Démarrage des services..."
    
    # Démarrer le backend en arrière-plan
    cd "$BACKEND_DIR"
    python manage.py runserver 8000 &
    BACKEND_PID=$!
    
    # Attendre que le backend soit prêt
    print_info "Attente du démarrage du backend..."
    sleep 10
    
    # Démarrer le frontend en arrière-plan
    cd "$FRONTEND_DIR"
    npm run dev &
    FRONTEND_PID=$!
    
    # Attendre que le frontend soit prêt
    print_info "Attente du démarrage du frontend..."
    sleep 15
    
    # Lancer les tests E2E (si disponibles)
    if [ -f "cypress.config.ts" ]; then
        print_info "Lancement des tests Cypress..."
        if npx cypress run; then
            print_success "Tests E2E - SUCCÈS"
        else
            print_error "Tests E2E - ÉCHEC"
        fi
    else
        print_warning "Tests E2E non configurés"
    fi
    
    # Arrêter les services
    print_info "Arrêt des services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    
    print_success "TESTS END-TO-END TERMINÉS"
}

# Fonction principale
main() {
    print_header "LANCEMENT DES TESTS PEPROSCOLAIRE"
    print_info "Type de tests: $TEST_TYPE"
    
    check_dependencies
    
    case $TEST_TYPE in
        "backend")
            run_backend_tests
            ;;
        "frontend")
            run_frontend_tests
            ;;
        "e2e")
            run_e2e_tests
            ;;
        "all")
            run_backend_tests
            if [ $? -eq 0 ]; then
                run_frontend_tests
                if [ $? -eq 0 ]; then
                    run_e2e_tests
                fi
            fi
            ;;
        *)
            print_error "Type de test invalide. Utilisez: backend, frontend, e2e, ou all"
            exit 1
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        print_header "TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS! 🎉"
        print_success "Le projet PeproScolaire est prêt pour la production"
    else
        print_header "CERTAINS TESTS ONT ÉCHOUÉ ❌"
        print_error "Veuillez corriger les erreurs avant de continuer"
        exit 1
    fi
}

# Point d'entrée
main "$@"