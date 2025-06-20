# Guide de Déploiement PeproScolaire

## 🚀 Vue d'ensemble

Ce guide décrit comment déployer PeproScolaire en production avec Docker et Docker Compose.

## 📋 Prérequis

### Système requis
- Linux Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum (8GB recommandé)
- 50GB espace disque minimum
- Certificats SSL/TLS (pour HTTPS)

### Installation des dépendances

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y docker.io docker-compose-plugin curl wget git

# Démarrer Docker
sudo systemctl start docker
sudo systemctl enable docker

# Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER
```

## ⚙️ Configuration

### 1. Configuration de l'environnement

```bash
# Cloner le projet
git clone <votre-repo>
cd peproscolaire

# Copier le fichier d'environnement
cp .env.production.example .env.production

# Éditer la configuration
nano .env.production
```

### 2. Variables d'environnement critiques

Modifiez obligatoirement ces valeurs dans `.env.production` :

```bash
# SÉCURITÉ CRITIQUE
SECRET_KEY=votre-clé-secrète-très-longue-et-aléatoire
DATABASE_PASSWORD=mot-de-passe-base-de-données-fort
DJANGO_SUPERUSER_EMAIL=admin@votre-ecole.fr
DJANGO_SUPERUSER_PASSWORD=mot-de-passe-admin-sécurisé

# RÉSEAU
ALLOWED_HOSTS=votre-domaine.fr,*.votre-domaine.fr
CSRF_TRUSTED_ORIGINS=https://votre-domaine.fr
CORS_ALLOWED_ORIGINS=https://votre-domaine.fr

# EMAIL
EMAIL_HOST=smtp.votre-provider.fr
EMAIL_HOST_USER=noreply@votre-ecole.fr
EMAIL_HOST_PASSWORD=mot-de-passe-email

# IA (optionnel)
OPENAI_API_KEY=sk-votre-clé-openai
HUGGINGFACE_API_KEY=hf_votre-token-huggingface
```

### 3. Certificats SSL

Pour HTTPS, placez vos certificats :

```bash
mkdir -p ssl
# Copiez vos certificats
cp votre-certificat.pem ssl/cert.pem
cp votre-clé-privée.key ssl/private.key
```

## 🚢 Déploiement

### Déploiement automatique (recommandé)

```bash
# Première installation
./scripts/deploy.sh production fresh

# Mise à jour
./scripts/deploy.sh production update

# Rollback en cas de problème
./scripts/deploy.sh production rollback
```

### Déploiement manuel

```bash
# Construction des images
docker compose -f docker-compose.production.yml build

# Démarrage des services
docker compose -f docker-compose.production.yml up -d

# Vérification des services
docker compose -f docker-compose.production.yml ps
```

## 🔍 Vérification

### Services actifs

```bash
# Statut des conteneurs
docker compose -f docker-compose.production.yml ps

# Logs en temps réel
docker compose -f docker-compose.production.yml logs -f

# Health checks
curl http://localhost:8000/api/v1/health/
curl http://localhost/health
```

### URLs d'accès

- **Frontend** : http://localhost (ou votre domaine)
- **API Backend** : http://localhost:8000/api/v1/
- **Admin Django** : http://localhost:8000/admin/
- **Monitoring** : http://localhost:3000 (Grafana, si activé)

## 📊 Monitoring (optionnel)

### Activation du monitoring

```bash
# Démarrer avec monitoring
docker compose -f docker-compose.production.yml --profile monitoring up -d

# Accès Grafana
# URL: http://localhost:3000
# Login: admin / password défini dans .env.production
```

### Métriques disponibles

- Performance de l'application
- Utilisation des ressources
- Santé de la base de données
- Métriques des tâches Celery
- Logs centralisés

## 🛡️ SSL/HTTPS (optionnel)

### Activation du reverse proxy SSL

```bash
# Démarrer avec SSL
docker compose -f docker-compose.production.yml --profile ssl up -d

# Vérification SSL
curl -I https://votre-domaine.fr
```

## 💾 Sauvegarde et Restauration

### Sauvegarde automatique

```bash
# Sauvegarde complète
./scripts/backup.sh production full

# Sauvegarde incrémentale
./scripts/backup.sh production incremental

# Configuration d'une tâche cron
crontab -e
# Ajouter : 0 2 * * * /chemin/vers/peproscolaire/scripts/backup.sh production incremental
```

### Restauration

```bash
# Restauration complète depuis la dernière sauvegarde
./scripts/restore.sh production latest full

# Restauration de la base de données seulement
./scripts/restore.sh production 20241220 database-only

# Restauration des volumes seulement
./scripts/restore.sh production latest volumes-only
```

## 🔧 Maintenance

### Mise à jour de l'application

```bash
# 1. Sauvegarder
./scripts/backup.sh production full

# 2. Mettre à jour le code
git pull origin main

# 3. Déployer les changements
./scripts/deploy.sh production update

# 4. Vérifier le déploiement
curl http://localhost:8000/api/v1/health/
```

### Gestion des logs

```bash
# Voir les logs d'un service
docker compose -f docker-compose.production.yml logs backend

# Nettoyer les logs (rotation automatique configurée)
docker system prune -f

# Archiver les anciens logs
find logs/ -name "*.log" -mtime +30 -exec gzip {} \;
```

### Mise à l'échelle

```bash
# Augmenter le nombre de workers Celery
docker compose -f docker-compose.production.yml up -d --scale celery_worker=3

# Monitoring des ressources
docker stats
```

## 🚨 Dépannage

### Problèmes courants

#### Services qui ne démarrent pas

```bash
# Vérifier les logs
docker compose -f docker-compose.production.yml logs

# Vérifier l'espace disque
df -h

# Vérifier les variables d'environnement
docker compose -f docker-compose.production.yml config
```

#### Base de données inaccessible

```bash
# Vérifier le conteneur PostgreSQL
docker compose -f docker-compose.production.yml exec database pg_isready -U pepro

# Redémarrer la base de données
docker compose -f docker-compose.production.yml restart database

# Vérifier les connexions
docker compose -f docker-compose.production.yml exec database psql -U pepro -d peproscolaire -c "SELECT version();"
```

#### Performance dégradée

```bash
# Vérifier l'utilisation des ressources
docker stats

# Vérifier les métriques Redis
docker compose -f docker-compose.production.yml exec redis redis-cli info memory

# Analyser les requêtes lentes
docker compose -f docker-compose.production.yml logs backend | grep "slow"
```

### Rollback d'urgence

```bash
# Rollback automatique
./scripts/deploy.sh production rollback

# Rollback manuel
./scripts/restore.sh production latest database-only
docker compose -f docker-compose.production.yml restart
```

## 📞 Support

### Logs utiles pour le débogage

```bash
# Logs complets
docker compose -f docker-compose.production.yml logs --timestamps

# Logs d'un service spécifique
docker compose -f docker-compose.production.yml logs -f backend

# Logs système
journalctl -u docker
```

### Commandes de diagnostic

```bash
# État des services
./scripts/deploy.sh production --help

# Test de connectivité
curl -v http://localhost:8000/api/v1/health/

# Vérification de la configuration
docker compose -f docker-compose.production.yml config --quiet
```

## 🔐 Sécurité

### Recommandations de sécurité

1. **Changez tous les mots de passe par défaut**
2. **Utilisez HTTPS en production**
3. **Configurez un firewall (ufw/iptables)**
4. **Mettez à jour régulièrement le système**
5. **Surveillez les logs de sécurité**
6. **Sauvegardez régulièrement**

### Configuration firewall basique

```bash
# Ubuntu UFW
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Vérification
sudo ufw status
```

---

## 📚 Ressources supplémentaires

- [Documentation Docker](https://docs.docker.com/)
- [Documentation Django](https://docs.djangoproject.com/)
- [Documentation Vue.js](https://vuejs.org/guide/)
- [Documentation PostgreSQL](https://www.postgresql.org/docs/)

Pour toute question, consultez les logs ou contactez l'équipe de développement.