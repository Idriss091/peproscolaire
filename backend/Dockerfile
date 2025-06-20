# Multi-stage build pour optimiser la taille de l'image
FROM python:3.11-slim as builder

# Variables d'environnement pour Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Installation des dépendances de build
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python dans un environnement virtuel
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage de production
FROM python:3.11-slim as production

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

# Installation des dépendances runtime uniquement
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gettext \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copie de l'environnement virtuel depuis le builder
COPY --from=builder /opt/venv /opt/venv

# Création d'un utilisateur non-root pour la sécurité
RUN groupadd -r pepro && useradd -r -g pepro pepro

# Répertoire de travail
WORKDIR /app

# Copie du code source
COPY --chown=pepro:pepro . /app/

# Création des répertoires pour les fichiers statiques et media
RUN mkdir -p /app/staticfiles /app/mediafiles && \
    chown -R pepro:pepro /app/staticfiles /app/mediafiles

# Copie des scripts de démarrage
COPY --chown=pepro:pepro scripts/docker-entrypoint.sh /app/
COPY --chown=pepro:pepro scripts/wait-for-db.sh /app/
RUN chmod +x /app/docker-entrypoint.sh /app/wait-for-db.sh

# Changement vers l'utilisateur non-root
USER pepro

# Collecte des fichiers statiques
RUN python manage.py collectstatic --noinput --clear

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health/ || exit 1

# Exposition du port
EXPOSE 8000

# Script de démarrage
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "60", "config.wsgi:application"]