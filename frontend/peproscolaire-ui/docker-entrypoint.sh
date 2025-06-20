#!/bin/sh
set -e

echo "🌐 Starting PeproScolaire Frontend..."

# Configuration dynamique de l'API URL si fournie
if [ ! -z "$VITE_API_URL" ]; then
    echo "🔧 Configuring API URL: $VITE_API_URL"
    
    # Remplacement de l'URL de l'API dans les fichiers JS buildés
    find /usr/share/nginx/html -name "*.js" -exec sed -i "s|http://localhost:8000/api/v1|$VITE_API_URL|g" {} \;
    
    echo "✅ API URL configured"
fi

# Configuration des variables d'environnement pour le runtime
if [ ! -z "$VITE_APP_NAME" ]; then
    echo "🏷️  Configuring app name: $VITE_APP_NAME"
    find /usr/share/nginx/html -name "*.js" -exec sed -i "s|PEP RO Scolaire|$VITE_APP_NAME|g" {} \;
fi

# Création d'un fichier de configuration JavaScript pour les variables d'environnement runtime
cat > /usr/share/nginx/html/config.js << EOF
window.ENV = {
  API_URL: '${VITE_API_URL:-/api/v1}',
  APP_NAME: '${VITE_APP_NAME:-PEP RO Scolaire}',
  APP_VERSION: '${VITE_APP_VERSION:-1.0.0}',
  DEBUG: '${VITE_DEBUG:-false}' === 'true'
};
EOF

echo "📝 Runtime configuration created"

# Test de la configuration Nginx
echo "🧪 Testing Nginx configuration..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration is valid"
else
    echo "❌ Nginx configuration is invalid"
    exit 1
fi

echo "✅ Frontend initialization complete!"

# Exécuter la commande passée en argument
exec "$@"