# 🚀 Guide d'Installation Complet - PeproScolaire

Ce guide vous accompagne pas à pas pour installer et tester **PeproScolaire**, le système de gestion scolaire intelligent avec modules IA.

## 📋 Prérequis

### Méthode 1 : Installation avec Docker (Recommandée ⭐)
- **Docker** : Version 20.0+ ([Installation Docker](https://docs.docker.com/get-docker/))
- **Docker Compose** : Version 2.0+ (inclus avec Docker Desktop)
- **Git** : Pour cloner le repository
- **4 GB RAM minimum** pour faire tourner tous les services

### Méthode 2 : Installation manuelle (Développement)
- **Python** : Version 3.11+
- **Node.js** : Version 18+ avec npm
- **PostgreSQL** : Version 14+
- **Redis** : Version 6+ (optionnel mais recommandé)

## 🐳 Installation avec Docker (Méthode rapide)

### Étape 1 : Cloner le projet

```bash
# Cloner le repository
git clone https://github.com/your-username/peproscolaire.git
cd peproscolaire
```

### Étape 2 : Configuration de l'environnement

```bash
# Copier le fichier d'environnement
cp .env.example .env

# Modifier si nécessaire (optionnel pour la démo)
nano .env
```

Contenu du fichier `.env` par défaut :
```env
# Base de données
DATABASE_URL=postgresql://pepro_user:pepro_password@db:5432/peproscolaire

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Redis
REDIS_URL=redis://redis:6379/0

# IA et APIs externes
OPENAI_API_KEY=your-openai-key-here
HUGGINGFACE_API_KEY=your-hf-key-here
```

### Étape 3 : Lancement des services

```bash
# Construire et lancer tous les services
docker-compose up --build -d

# Vérifier que tous les services sont démarrés
docker-compose ps
```

Vous devriez voir :
```
NAME                COMMAND             STATUS
pepro_frontend      npm run dev         Up
pepro_backend       python manage.py    Up  
pepro_db            postgres           Up
pepro_redis         redis-server       Up
pepro_nginx         nginx              Up
```

### Étape 4 : Initialisation de la base de données

```bash
# Créer les tables de la base de données
docker-compose exec backend python manage.py migrate

# Créer un superutilisateur admin
docker-compose exec backend python manage.py createsuperuser

# Charger les données de démonstration
docker-compose exec backend python manage.py loaddata demo_data.json

# Entraîner les modèles IA avec les données de demo
docker-compose exec backend python manage.py train_ai_models
```

### Étape 5 : Accéder à l'application

L'application est maintenant disponible sur :

- **🏠 Application principale** : http://localhost:3000
- **🔧 Interface d'administration** : http://localhost:3000/admin
- **📚 API Documentation** : http://localhost:3000/api/docs
- **📊 Métriques (optionnel)** : http://localhost:3000/metrics

## 💻 Installation manuelle (Développement)

### Étape 1 : Préparer l'environnement

```bash
# Cloner le repository
git clone https://github.com/your-username/peproscolaire.git
cd peproscolaire

# Créer la base de données PostgreSQL
sudo -u postgres createuser pepro_user
sudo -u postgres createdb peproscolaire -O pepro_user
sudo -u postgres psql -c "ALTER USER pepro_user WITH PASSWORD 'pepro_password';"
```

### Étape 2 : Configuration du Backend Django

```bash
cd backend

# Créer un environnement virtuel Python
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# Installer les dépendances Python
pip install -r requirements.txt

# Configuration de l'environnement
cp .env.example .env
# Modifier .env avec vos paramètres locaux

# Initialiser la base de données
python manage.py migrate
python manage.py collectstatic --noinput

# Créer un superutilisateur
python manage.py createsuperuser

# Charger les données de démonstration
python manage.py loaddata demo_data.json

# Entraîner les modèles IA
python manage.py train_ai_models

# Lancer le serveur Django
python manage.py runserver 0.0.0.0:8000
```

### Étape 3 : Configuration du Frontend Vue.js

```bash
# Ouvrir un nouveau terminal
cd frontend/peproscolaire-ui

# Installer les dépendances Node.js
npm install

# Copier la configuration
cp .env.example .env.local

# Modifier si nécessaire
nano .env.local
```

Contenu de `.env.local` :
```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_BASE_URL=ws://localhost:8000/ws
VITE_APP_NAME=PeproScolaire
```

```bash
# Lancer le serveur de développement
npm run dev
```

### Étape 4 : Services optionnels

#### Redis (pour les performances)
```bash
# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis-server

# macOS avec Homebrew
brew install redis
brew services start redis

# Windows avec Chocolatey
choco install redis-64
```

#### Celery (pour les tâches asynchrones)
```bash
# Dans le dossier backend, nouveau terminal
source venv/bin/activate
celery -A config worker --loglevel=info

# Worker pour les tâches IA (nouveau terminal)
celery -A config worker --loglevel=info --queue=ai_tasks
```

## 🎮 Premiers pas après l'installation

### 1. Connexion à l'interface d'administration

1. Aller sur http://localhost:3000/admin
2. Se connecter avec le superutilisateur créé
3. Explorer les modèles de données
4. Vérifier que les données de démo sont bien chargées

### 2. Test des comptes de démonstration

| Rôle | Email | Mot de passe | Utilisation |
|------|-------|--------------|-------------|
| **Administrateur** | `admin@college-demo.fr` | `demo123` | Gestion complète de l'établissement |
| **Professeur Principal** | `prof.martin@college-demo.fr` | `demo123` | Notes, emplois du temps, appréciations IA |
| **Professeur** | `prof.durand@college-demo.fr` | `demo123` | Matière spécifique, évaluations |
| **Élève** | `eleve.dupont@college-demo.fr` | `demo123` | Consultation notes, devoirs, chatbot |
| **Parent** | `parent.dupont@college-demo.fr` | `demo123` | Suivi scolarité enfant |

### 3. Explorer les modules IA

#### Module de détection de décrochage
1. Se connecter en tant que **Professeur** ou **Admin**
2. Aller dans **Menu IA** → **Détection de risque**
3. Explorer le dashboard avec les métriques ML
4. Consulter la liste des élèves à risque
5. Ouvrir un plan d'intervention

#### Générateur d'appréciations IA
1. Aller dans **Menu IA** → **Appréciations IA**
2. Sélectionner une classe (ex: 3ème A)
3. Choisir le type d'appréciation (Bulletin, Progrès, etc.)
4. Configurer les paramètres de génération
5. Prévisualiser et valider

#### Chatbot pédagogique
1. Se connecter en tant qu'**Élève**
2. Cliquer sur l'icône de chat en bas à droite
3. Tester les suggestions rapides
4. Poser des questions sur les notes ou devoirs

### 4. Tester l'interface moderne

- **Navigation responsive** : Tester sur mobile/tablette
- **Recherche globale** : Utiliser `Ctrl/Cmd + K`
- **Notifications** : Cliquer sur l'icône cloche
- **Actions rapides** : Bouton `+` en haut à droite
- **Thème sombre** : Menu utilisateur → Basculer le thème

## 🔧 Personnalisation et configuration

### Configuration des modules IA

```bash
# Modifier les paramètres IA dans le backend
cd backend
nano apps/ai_modules/settings.py
```

### Ajout de données personnalisées

```bash
# Utiliser l'interface admin Django
# Ou créer des fixtures personnalisées
python manage.py dumpdata auth.User > my_users.json
python manage.py loaddata my_users.json
```

### Configuration de l'établissement

1. Interface admin → **Schools** → **Establishments**
2. Modifier les informations de l'établissement
3. Ajouter logo, couleurs, configuration

## 🐛 Résolution des problèmes courants

### Problème : Les services Docker ne démarrent pas
```bash
# Vérifier les logs
docker-compose logs

# Relancer les services
docker-compose down
docker-compose up --build
```

### Problème : Erreur de base de données
```bash
# Réinitialiser la base de données
docker-compose exec backend python manage.py flush
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py loaddata demo_data.json
```

### Problème : Les modules IA ne fonctionnent pas
```bash
# Vérifier les clés API dans .env
# Réentraîner les modèles
docker-compose exec backend python manage.py train_ai_models

# Vérifier les logs Celery
docker-compose logs worker
```

### Problème : Interface frontend inaccessible
```bash
# Vérifier que le serveur Node.js fonctionne
docker-compose logs frontend

# Reconstruire les assets
docker-compose exec frontend npm run build
```

## 🚀 Mise en production

Pour déployer PeproScolaire en production :

1. **Modifier les variables d'environnement** (DEBUG=False, clés sécurisées)
2. **Configurer un nom de domaine** et certificats SSL
3. **Utiliser une base de données externe** (RDS, etc.)
4. **Configurer le stockage de fichiers** (S3, etc.)
5. **Mettre en place la surveillance** (logs, métriques)

Consultez le [Guide de déploiement production](DEPLOYMENT.md) pour plus de détails.

## 📞 Support et communauté

- **Issues GitHub** : Signaler des bugs ou demander des fonctionnalités
- **Documentation** : Wiki complet avec exemples
- **Communauté** : Discord/Slack pour les discussions

---

**Félicitations ! 🎉** 

Vous avez maintenant PeproScolaire fonctionnel avec tous les modules IA. 

Explorez les fonctionnalités, testez les différents rôles utilisateur et découvrez comment l'IA peut transformer la gestion scolaire !