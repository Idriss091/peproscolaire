# Multi-stage build pour optimiser l'image frontend
FROM node:18-alpine as builder

# Variables d'environnement
ENV NODE_ENV=production
ENV NPM_CONFIG_CACHE=/tmp/.npm

# Répertoire de travail
WORKDIR /app

# Installation des dépendances
COPY package*.json ./
RUN npm ci --only=production --cache /tmp/.npm && \
    npm cache clean --force

# Copie du code source
COPY . .

# Build de l'application
RUN npm run build

# Stage de production avec Nginx
FROM nginx:alpine as production

# Installation des dépendances pour le health check
RUN apk add --no-cache curl

# Copie de la configuration Nginx
COPY nginx.conf /etc/nginx/nginx.conf
COPY nginx-default.conf /etc/nginx/conf.d/default.conf

# Copie des fichiers buildés depuis le builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copie du script d'entrée pour la configuration dynamique
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1

# Exposition du port
EXPOSE 80

# Script de démarrage
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]