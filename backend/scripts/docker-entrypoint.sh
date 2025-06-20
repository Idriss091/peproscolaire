#!/bin/bash
set -e

# Script de point d'entrée pour le conteneur Django

echo "🚀 Starting PeproScolaire Backend..."

# Attendre que la base de données soit disponible
echo "⏳ Waiting for database..."
/app/wait-for-db.sh

# Appliquer les migrations
echo "🔄 Applying database migrations..."
python manage.py migrate --noinput

# Créer un superutilisateur par défaut si défini
if [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "👤 Creating superuser..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='$DJANGO_SUPERUSER_EMAIL').exists():
    User.objects.create_superuser(
        email='$DJANGO_SUPERUSER_EMAIL',
        password='$DJANGO_SUPERUSER_PASSWORD',
        first_name='Admin',
        last_name='System',
        user_type='superadmin'
    )
    print('✅ Superuser created successfully')
else:
    print('ℹ️  Superuser already exists')
"
fi

# Charger les données initiales si nécessaire
if [ "$LOAD_INITIAL_DATA" = "true" ]; then
    echo "📊 Loading initial data..."
    python manage.py loaddata apps/schools/fixtures/initial_data.json || echo "⚠️  Initial data already loaded or not found"
fi

# Collecter les fichiers statiques en production
if [ "$DJANGO_ENV" = "production" ]; then
    echo "📁 Collecting static files..."
    python manage.py collectstatic --noinput --clear
fi

# Démarrer Celery worker en arrière-plan si demandé
if [ "$START_CELERY" = "true" ]; then
    echo "🔧 Starting Celery worker..."
    celery -A config worker --loglevel=info --detach
fi

# Démarrer Celery beat en arrière-plan si demandé
if [ "$START_CELERY_BEAT" = "true" ]; then
    echo "⏰ Starting Celery beat..."
    celery -A config beat --loglevel=info --detach
fi

echo "✅ Backend initialization complete!"

# Exécuter la commande passée en argument
exec "$@"