#!/bin/bash

# Script pour démarrer le frontend en développement

echo "🚀 Démarrage du frontend PeproScolaire..."

cd "$(dirname "$0")/../frontend/peproscolaire-ui"

# Vérifier que les dépendances sont installées
if [ ! -d "node_modules" ]; then
    echo "📦 Installation des dépendances..."
    npm install
fi

# Démarrer le serveur de développement
echo "🏃 Démarrage du serveur de développement sur http://localhost:5173"
npm run dev