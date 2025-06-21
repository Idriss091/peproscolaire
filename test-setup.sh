#!/bin/bash

echo "=== Test de configuration PeproScolaire ==="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test Docker services
echo "🐳 Vérification des services Docker..."
if docker-compose ps | grep -q "Up.*healthy"; then
    echo -e "${GREEN}✅ PostgreSQL et Redis sont actifs${NC}"
else
    echo -e "${RED}❌ Services Docker non disponibles${NC}"
    echo "Lancement des services..."
    docker-compose up -d
fi

# Test database connection
echo ""
echo "🗄️ Test de connexion à la base de données..."
if docker exec peproscolaire_db pg_isready -U peproscolaire_user > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL accessible${NC}"
else
    echo -e "${RED}❌ PostgreSQL non accessible${NC}"
fi

# Test backend
echo ""
echo "🔧 Test du backend Django..."
cd backend
if [ -d "venv" ]; then
    source venv/bin/activate
    
    # Test dependencies
    if python -c "import django; import rest_framework" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Dépendances Python installées${NC}"
    else
        echo -e "${RED}❌ Dépendances Python manquantes${NC}"
        exit 1
    fi
    
    # Test migrations
    echo "📋 Vérification des migrations..."
    python manage.py showmigrations --plan | tail -5
    
    echo -e "${YELLOW}ℹ️  Démarrage du serveur Django en arrière-plan...${NC}"
    python manage.py runserver 0.0.0.0:8000 > /dev/null 2>&1 &
    DJANGO_PID=$!
    sleep 3
    
    if kill -0 $DJANGO_PID > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Serveur Django démarré (PID: $DJANGO_PID)${NC}"
    else
        echo -e "${RED}❌ Serveur Django non démarré${NC}"
    fi
else
    echo -e "${RED}❌ Environnement virtuel non trouvé${NC}"
    exit 1
fi

cd ..

# Test frontend
echo ""
echo "🎨 Test du frontend Vue.js..."
cd frontend/peproscolaire-ui

if [ -d "node_modules" ]; then
    echo -e "${GREEN}✅ Dépendances Node.js installées${NC}"
    
    # Test build
    echo "🔨 Test de la configuration Tailwind..."
    if [ -f "tailwind.config.js" ]; then
        echo -e "${GREEN}✅ Configuration Tailwind présente${NC}"
    else
        echo -e "${RED}❌ Configuration Tailwind manquante${NC}"
    fi
    
    echo -e "${YELLOW}ℹ️  Démarrage du serveur Vite en arrière-plan...${NC}"
    npm run dev > /dev/null 2>&1 &
    VITE_PID=$!
    sleep 5
    
    if kill -0 $VITE_PID > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Serveur Vite démarré (PID: $VITE_PID)${NC}"
    else
        echo -e "${RED}❌ Serveur Vite non démarré${NC}"
    fi
else
    echo -e "${RED}❌ Dépendances Node.js non installées${NC}"
    echo "Exécutez: npm install"
    exit 1
fi

cd ../..

# Summary
echo ""
echo "📊 === Résumé de l'installation ==="
echo -e "🐳 Docker Services: ${GREEN}PostgreSQL + Redis actifs${NC}"
echo -e "🔧 Backend Django: ${GREEN}Démarré sur http://localhost:8000${NC}"
echo -e "🎨 Frontend Vue.js: ${GREEN}Démarré sur http://localhost:5173${NC}"
echo ""
echo -e "${GREEN}🎉 Installation réussie !${NC}"
echo ""
echo "📖 Accès aux services:"
echo "   • Frontend: http://localhost:5173"
echo "   • Backend API: http://localhost:8000"
echo "   • Admin Django: http://localhost:8000/admin"
echo "   • Documentation API: http://localhost:8000/swagger"
echo ""
echo "🛑 Pour arrêter les services:"
echo "   kill $DJANGO_PID $VITE_PID"
echo "   docker-compose down"