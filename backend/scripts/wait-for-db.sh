#!/bin/bash
set -e

# Script pour attendre que la base de données soit disponible

host="$DATABASE_HOST"
port="${DATABASE_PORT:-5432}"
timeout="${DB_WAIT_TIMEOUT:-30}"

if [ -z "$host" ]; then
    echo "⚠️  DATABASE_HOST not set, skipping database check"
    exit 0
fi

echo "⏳ Waiting for database at $host:$port..."

start_time=$(date +%s)
while ! nc -z "$host" "$port" >/dev/null 2>&1; do
    current_time=$(date +%s)
    elapsed=$((current_time - start_time))
    
    if [ $elapsed -ge $timeout ]; then
        echo "❌ Database connection timeout after ${timeout}s"
        exit 1
    fi
    
    echo "⏳ Database not ready yet, waiting... (${elapsed}s/${timeout}s)"
    sleep 2
done

echo "✅ Database is ready!"

# Test de connexion Django
echo "🔌 Testing Django database connection..."
python manage.py check --database default

if [ $? -eq 0 ]; then
    echo "✅ Django database connection successful!"
else
    echo "❌ Django database connection failed!"
    exit 1
fi