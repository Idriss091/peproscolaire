# 🚀 Guide d'Installation Complet - PeproScolaire

Ce guide vous accompagne pas à pas pour installer et configurer **PeproScolaire**, la solution moderne de gestion scolaire avec interface Vue.js et backend Django.

## 📋 Prérequis Système

### Installation Recommandée (Développement)
- **Python** : Version 3.11+
- **Node.js** : Version 18+ avec npm
- **Git** : Pour cloner le repository
- **4 GB RAM minimum** pour un fonctionnement optimal
- **10 GB d'espace disque** pour les dépendances

### Système d'Exploitation Supportés
- **Linux** : Ubuntu 20.04+, Debian 11+, CentOS 8+
- **macOS** : macOS 11+ (Big Sur)
- **Windows** : Windows 10+ avec WSL2 recommandé

## 🐳 Installation avec Docker (Recommandé pour le Développement)

Pour un environnement de développement cohérent et qui se rapproche de la configuration de production, l'utilisation de Docker est fortement recommandée. Le projet fournit un fichier `docker-compose.yml` à la racine pour orchestrer les services backend et frontend.

### Prérequis pour Docker
- Docker Engine (version 20.10+ recommandée)
- Docker Compose (version V2+ recommandée)
  (Consultez la [documentation officielle de Docker](https://docs.docker.com/get-docker/) pour l'installation)

### Étapes d'installation avec Docker

1.  **Cloner le repository :**
    ```bash
    git clone <repository-url> # Remplacez <repository-url> par l'URL du projet
    cd peproscolaire
    ```

2.  **Configuration des variables d'environnement (Optionnel pour un premier test) :**
    *   **Backend :** Pour des configurations spécifiques (ex: base de données PostgreSQL externe), copiez `backend/.env.example` vers `backend/.env` et modifiez-le. Pour un démarrage rapide avec SQLite (géré dans un volume Docker), ce fichier n'est pas immédiatement requis.
    *   **Frontend :** Copiez `frontend/peproscolaire-ui/.env.example` vers `frontend/peproscolaire-ui/.env.local`. Assurez-vous que `VITE_API_URL` est configuré correctement (par exemple, `http://localhost:8000/api/v1`, car le backend sera exposé sur le port 8000 de l'hôte).

3.  **Lancer les services avec Docker Compose :**
    Depuis la racine du projet (`peproscolaire/`):
    ```bash
    docker compose up --build
    ```
    Cette commande va :
    *   Construire les images Docker pour les services `backend` et `frontend` (si elles n'existent pas ou si les Dockerfiles ont été modifiés).
    *   Démarrer les conteneurs.

    Une fois terminé :
    *   Le backend Django sera accessible sur `http://localhost:8000`.
    *   Le frontend Vue.js sera accessible sur `http://localhost:5173`.

4.  **Arrêter les services :**
    Dans le terminal où `docker compose up` s'exécute, appuyez sur `Ctrl+C`. Puis, pour s'assurer que les conteneurs sont bien arrêtés et supprimés (les volumes de données persistent) :
    ```bash
    docker compose down
    ```

5.  **Gestion des migrations et superutilisateur (Backend) :**
    Pour exécuter des commandes `manage.py` (comme les migrations initiales ou la création d'un superutilisateur), ouvrez un nouveau terminal et utilisez `docker compose exec` :
    ```bash
    # Appliquer les migrations
    docker compose exec backend python3.11 manage.py migrate

    # Créer un superutilisateur
    docker compose exec backend python3.11 manage.py createsuperuser
    ```
    *(Note: Si `python3.11` n'est pas trouvé, essayez `python`)*

### Avantages de l'approche Docker
- **Isolation :** Les dépendances sont gérées dans les conteneurs, évitant les conflits avec votre système local.
- **Cohérence :** Assure que tous les développeurs travaillent avec le même environnement.
- **Simplicité :** Moins d'étapes manuelles pour la configuration des dépendances Python et Node.js.
- **Proximité avec la Production :** L'environnement de production utilise également Docker (voir `README-DEPLOYMENT.md`).

Passez à la section [Premiers Pas avec l'Application](#-premiers-pas-avec-lapplication) après avoir démarré les services.

## 💻 Installation Pas à Pas (Manuelle)

### Étape 1 : Cloner le Projet

```bash
# Cloner le repository
git clone https://github.com/your-username/peproscolaire.git
cd peproscolaire
```

### Étape 2 : Configuration Backend Django

```bash
cd backend

# Créer un environnement virtuel Python
python3.11 -m venv venv

# Activer l'environnement virtuel
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# Mettre à jour pip
pip install --upgrade pip

# Installer les dépendances Python
pip install -r requirements.txt

# Configurer la base de données
DJANGO_SETTINGS_MODULE=config.settings_minimal python manage.py migrate

# Créer des données de test (optionnel)
python create_sample_grades.py

# Lancer le serveur Django
DJANGO_SETTINGS_MODULE=config.settings_minimal python manage.py runserver
```

✅ Le backend sera accessible sur **http://127.0.0.1:8000/**

---

### (Optionnel) Utiliser PostgreSQL pour le Développement Backend

Par défaut, l'installation de développement utilise SQLite. Si vous préférez utiliser PostgreSQL pour le développement :

1.  **Installez PostgreSQL** sur votre machine. Consultez la [documentation officielle de PostgreSQL](https://www.postgresql.org/download/) pour les instructions spécifiques à votre système d'exploitation.

2.  **Créez un utilisateur et une base de données** pour PeproScolaire. Par exemple, via `psql`:
    ```sql
    CREATE DATABASE peproscolaire_dev;
    CREATE USER pepro_user WITH PASSWORD 'votre_mot_de_passe_securise';
    ALTER ROLE pepro_user SET client_encoding TO 'utf8';
    ALTER ROLE pepro_user SET default_transaction_isolation TO 'read committed';
    ALTER ROLE pepro_user SET timezone TO 'UTC';
    GRANT ALL PRIVILEGES ON DATABASE peproscolaire_dev TO pepro_user;
    ```

3.  **Configurez les variables d'environnement** pour Django. Le moyen le plus simple est de créer un fichier `.env` à la racine du dossier `backend/` (s'il n'existe pas déjà) et d'y ajouter :
    ```env
    DATABASE_URL=postgres://pepro_user:votre_mot_de_passe_securise@localhost:5432/peproscolaire_dev
    # Assurez-vous que DJANGO_SETTINGS_MODULE est toujours bien défini pour utiliser settings_minimal
    # DJANGO_SETTINGS_MODULE=config.settings_minimal
    ```
    Le fichier `backend/config/settings_minimal.py` est déjà configuré pour utiliser `DATABASE_URL` si elle est définie, grâce à `django-environ`.

4.  **Assurez-vous que `psycopg2-binary` est installé** (il est déjà dans `requirements.txt`, donc `pip install -r requirements.txt` devrait l'avoir installé).

5.  **Supprimez le fichier `demo.db`** (la base SQLite) s'il a été créé, pour éviter toute confusion.

6.  **Appliquez les migrations** à votre nouvelle base de données PostgreSQL :
    ```bash
    DJANGO_SETTINGS_MODULE=config.settings_minimal python manage.py migrate
    ```

7.  **Créez des données de test ou un superutilisateur** comme décrit précédemment, si nécessaire.

Après ces étapes, Django utilisera votre base de données PostgreSQL locale. N'oubliez pas de démarrer votre service PostgreSQL avant de lancer le serveur Django.

---

### Étape 3 : Configuration Frontend Vue.js

```bash
# Ouvrir un nouveau terminal
cd frontend/peproscolaire-ui

# Installer les dépendances Node.js
npm install

# Configurer l'environnement en copiant le fichier d'exemple
cp .env.example .env.local
# Assurez-vous que les valeurs dans .env.local sont correctes pour votre environnement,
# notamment VITE_API_URL si votre backend tourne sur un port différent.

# Lancer le serveur de développement
npm run dev
```

✅ Le frontend sera accessible sur **http://localhost:5173/**

### Étape 4 : Vérification de l'Installation

#### Test Backend
```bash
# Test API REST
curl http://127.0.0.1:8000/api/v1/auth/
# Réponse attendue : {"detail": "Authentication credentials were not provided."}

# Test Admin Interface
curl http://127.0.0.1:8000/admin/
# Doit retourner une page HTML d'administration
```

#### Test Frontend
```bash
# Vérifier le build
cd frontend/peproscolaire-ui
npm run build

# Vérifier les tests
npm run test
```

### Étape 5 : Créer un Superutilisateur (Optionnel)

```bash
cd backend
source venv/bin/activate
DJANGO_SETTINGS_MODULE=config.settings_minimal python manage.py createsuperuser
```

## 🎮 Premiers Pas avec l'Application

### 👤 Comptes de Démonstration Pré-configurés

Le système inclut des comptes de test dans `demo.db` :

| **Rôle** | **Username** | **Email** | **Mot de passe** | **Accès** |
|-----------|--------------|-----------|-------------------|-----------|
| **Élève** | `eleve1` | `pierre.durand@test.com` | `password123` | `/student/*` |
| **Enseignant** | `prof.math` | `jean.martin@test.com` | `password123` | `/teacher/*` |
| **Parent** | `parent` | `parent@test.com` | `password123` | `/parent/*` |
| **Admin** | `admin` | `admin@test.com` | `password123` | `/admin/*` |

### 🎯 Parcours de Test Recommandé

1. **Accéder à l'application** → http://localhost:5173/
2. **Page de connexion** → Utiliser un compte de test
3. **Explorer le dashboard** personnalisé par rôle
4. **Tester les modules** :
   - 📊 **Tableau de bord** : Statistiques et actions rapides
   - 📝 **Devoirs** : Consultation/création selon le rôle
   - ⏰ **Emploi du temps** : Vue hebdomadaire
   - 📈 **Notes** : Système d'évaluation
   - 💬 **Messagerie** : Communication interne
   - 👥 **Vie scolaire** : Présences/absences

### 🌐 Structure des Routes

- **Élèves** : `/student/dashboard`, `/student/homework`, `/student/grades`
- **Enseignants** : `/teacher/dashboard`, `/teacher/homework`, `/teacher/grades`
- **Parents** : `/parent/dashboard`, `/parent/children`, `/parent/grades`
- **Administrateurs** : `/admin/dashboard`, `/admin/users`, `/admin/statistics`

## ⚙️ Configuration Avancée

### Variables d'Environnement Backend

Créer `backend/.env` :
```bash
DJANGO_SETTINGS_MODULE=config.settings_minimal
DEBUG=True
SECRET_KEY=django-insecure-demo-key-for-development-only
ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### Variables d'Environnement Frontend

Fichier `frontend/peproscolaire-ui/.env.local` :
```bash
# URL de l'API backend
VITE_API_URL=http://127.0.0.1:8000/api/v1

# Mode de fonctionnement
VITE_USE_MOCK_API=false  # false = API Django, true = données mockées

# Configuration optionnelle
VITE_APP_TITLE=PeproScolaire
VITE_APP_VERSION=1.0.0
```

### Modes de Fonctionnement

#### Mode API Real (Recommandé)
```bash
VITE_USE_MOCK_API=false
```
- Communication avec l'API Django
- Données persistantes en base
- Test complet frontend/backend

#### Mode Mock (Développement Frontend)
```bash
VITE_USE_MOCK_API=true
```
- Données simulées côté frontend
- Pas besoin du backend Django
- Idéal pour développement UI pur

## 🔧 Commandes Utiles

### Backend Django
```bash
cd backend
source venv/bin/activate

# Gestion de la base de données
python manage.py makemigrations      # Créer nouvelles migrations
python manage.py migrate             # Appliquer migrations
python manage.py showmigrations      # Voir statut migrations

# Gestion des utilisateurs
python manage.py createsuperuser     # Créer superutilisateur
python manage.py shell               # Shell Django interactif

# Gestion des données
python create_sample_grades.py       # Créer données de test
python manage.py dumpdata > backup.json  # Sauvegarde
python manage.py loaddata backup.json    # Restauration

# Tests et validation
python manage.py test                 # Lancer tests Django
python manage.py check               # Vérifier configuration
```

### Frontend Vue.js
```bash
cd frontend/peproscolaire-ui

# Développement
npm run dev                    # Serveur développement
npm run dev -- --host         # Accessible depuis réseau local

# Tests et qualité
npm run test                   # Tests unitaires Vitest
npm run test:coverage          # Coverage des tests
npm run lint                   # Linting ESLint
npm run type-check             # Vérification TypeScript

# Build et déploiement
npm run build                  # Build pour production
npm run preview                # Prévisualiser le build
npm run build-analyze          # Analyser la taille du bundle
```

## 🐛 Résolution des Problèmes Courants

### ❌ Backend Django ne démarre pas

**Erreur** : `ModuleNotFoundError` ou `ImproperlyConfigured`

```bash
# Vérifier l'environnement virtuel
cd backend
source venv/bin/activate
which python  # Doit pointer vers venv/bin/python

# Réinstaller les dépendances
pip install --upgrade pip
pip install -r requirements.txt

# Vérifier la configuration Django
python manage.py check
```

### ❌ Frontend Vue.js ne démarre pas

**Erreur** : `ENOENT` ou `Module not found`

```bash
# Nettoyer le cache Node.js
cd frontend/peproscolaire-ui
rm -rf node_modules package-lock.json
npm cache clean --force
npm install

# Vérifier la version Node.js
node --version  # Doit être 18+
npm --version   # Doit être 8+
```

### ❌ Erreur 404 sur l'API

**Erreur** : Frontend ne peut pas contacter le backend

```bash
# Vérifier que le backend fonctionne
curl http://127.0.0.1:8000/api/v1/
# Doit retourner du JSON

# Vérifier la configuration frontend
cat frontend/peproscolaire-ui/.env.local
# VITE_API_URL doit pointer vers le bon port

# Vérifier CORS
grep CORS_ALLOWED_ORIGINS backend/config/settings_minimal.py
```

### ❌ Erreur de connexion utilisateur

**Erreur** : Identifiants invalides

```bash
# Lister les utilisateurs existants
cd backend
source venv/bin/activate
python manage.py shell
>>> from apps.authentication.models import User
>>> for u in User.objects.all(): print(f"{u.username} - {u.email}")

# Créer un nouvel utilisateur de test
python create_sample_grades.py
```

### ❌ Erreur de permissions CORS

**Erreur** : `Access-Control-Allow-Origin` en console browser

```bash
# Vérifier la configuration CORS dans backend/config/settings_minimal.py
# Doit contenir :
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
```

## 🧪 Tests et Validation

### Tests Backend
```bash
cd backend
source venv/bin/activate
DJANGO_SETTINGS_MODULE=config.settings_minimal python manage.py test
```

### Tests Frontend
```bash
cd frontend/peproscolaire-ui
npm run test              # Tests unitaires
npm run test:coverage     # Rapport de couverture
npm run lint              # Vérification syntaxe
npm run type-check        # Vérification types TypeScript
```

### Validation Manuelle
1. **Authentification** : Tester connexion/déconnexion
2. **Navigation** : Vérifier toutes les routes
3. **API** : Tester CRUD sur chaque module
4. **Responsive** : Tester sur mobile/desktop
5. **Performance** : Vérifier temps de chargement

## 🚀 Mise en Production

Pour déployer PeproScolaire en production, consultez :

1. **[Guide de déploiement](DEPLOYMENT.md)** - Configuration serveur
2. **[Guide Docker](DOCKER.md)** - Conteneurisation
3. **[Guide sécurité](SECURITY.md)** - Bonnes pratiques

### Points Clés Production
- Utiliser PostgreSQL au lieu de SQLite
- Configurer HTTPS avec certificats SSL
- Utiliser Nginx + Gunicorn
- Mettre en place la surveillance (logs, métriques)
- Configurer les sauvegardes automatiques

## 📚 Ressources Supplémentaires

- **[README principal](README.md)** - Vue d'ensemble du projet
- **[Guide de démonstration](DEMO-GUIDE.md)** - Présentation fonctionnalités
- **[Tests et déploiement](TESTING.md)** - Procédures de test
- **[Résolution des problèmes](RESOLUTION-PROBLEMES.md)** - FAQ complète

## 📞 Support et Communauté

- **Issues GitHub** : Signaler des bugs ou demander des fonctionnalités
- **Documentation** : Wiki complet avec exemples
- **Discussions** : Forum de la communauté

---

**Félicitations ! 🎉** 

Vous avez maintenant PeproScolaire entièrement fonctionnel avec :
- ✅ Backend Django 5.0 opérationnel
- ✅ Frontend Vue.js 3 moderne et réactif
- ✅ Authentification JWT multi-rôles
- ✅ Interface responsive et intuitive
- ✅ Données de démonstration prêtes à l'emploi

**Prochaines étapes** : Explorez les différents rôles utilisateur, testez les modules, et découvrez l'interface moderne de gestion scolaire !