# PeproScolaire 🎓

[![Django](https://img.shields.io/badge/Django-5.0-green)](https://djangoproject.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.4-brightgreen)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Présentation du projet

**PeproScolaire** est une solution web moderne de gestion scolaire développée par un enseignant pour les établissements du second degré. Cette plateforme combine les fonctionnalités essentielles de gestion scolaire avec une architecture moderne et évolutive.

### 🎯 Vision du projet

- **Interface moderne et intuitive** : UX/UI pensée pour la simplicité d'usage
- **Architecture scalable** : Solution modulaire et maintenable
- **Fonctionnalités complètes** : Tous les outils nécessaires à la gestion scolaire
- **Approche terrain** : Conçu par et pour les professionnels de l'éducation

## 🏗️ Architecture Technique

### Stack Technologique

#### Backend
- **Framework** : Django 5.0 + Django REST Framework
- **Base de données** : SQLite (dev) / PostgreSQL (production)
- **Authentification** : JWT avec système de rôles personnalisé (UUID)
- **API** : REST API complète avec documentation

#### Frontend  
- **Framework** : Vue.js 3 + TypeScript + Composition API
- **UI** : Tailwind CSS + Headless UI
- **State Management** : Pinia avec storeToRefs
- **Build Tool** : Vite
- **Testing** : Vitest + Vue Test Utils + Testing Library

#### Architecture
- **API REST** : Communication frontend/backend
- **Authentification JWT** : Système sécurisé multi-rôles
- **CORS configuré** : Communication cross-origin sécurisée
- **Routing avancé** : Routes spécialisées par type d'utilisateur

### 🗂️ Structure du Projet

```
peproscolaire/
├── backend/                    # API Django
│   ├── apps/                  # Applications modulaires
│   │   ├── authentication/   # Système d'auth personnalisé (UUID)
│   │   ├── schools/          # Gestion établissements et classes
│   │   ├── homework/         # Cahier de textes et devoirs
│   │   ├── timetable/        # Emplois du temps et créneaux
│   │   ├── grades/           # Notes, évaluations et bulletins
│   │   ├── attendance/       # Vie scolaire et absences
│   │   ├── messaging/        # Messagerie interne
│   │   └── ai_core/          # Base pour modules IA futurs
│   ├── config/               # Configuration Django
│   │   ├── settings_minimal.py  # Config développement
│   │   └── urls_minimal.py      # Routes API
│   ├── demo.db              # Base SQLite avec données de test
│   ├── requirements.txt     # Dépendances Python
│   └── create_sample_*.py   # Scripts de génération de données
├── frontend/peproscolaire-ui/  # Application Vue.js
│   ├── src/
│   │   ├── components/       # Composants Vue réutilisables
│   │   │   ├── ui/          # Composants UI de base (BaseModal, BaseButton...)
│   │   │   ├── common/      # Composants communs (StatCard, UserAvatar...)
│   │   │   ├── layout/      # Navigation et layout
│   │   │   └── [modules]/   # Composants métier par module
│   │   ├── views/           # Pages principales par rôle utilisateur
│   │   │   ├── auth/        # Connexion et profil
│   │   │   ├── grades/      # Gestion des notes
│   │   │   ├── homework/    # Gestion des devoirs
│   │   │   ├── timetable/   # Emploi du temps
│   │   │   ├── attendance/  # Vie scolaire
│   │   │   └── messaging/   # Messagerie
│   │   ├── stores/          # Gestion d'état Pinia
│   │   ├── api/             # Clients API avec types
│   │   ├── types/           # Types TypeScript
│   │   └── router/          # Configuration routes avec guards
│   ├── .env.local           # Variables d'environnement
│   ├── tailwind.config.js   # Configuration Tailwind
│   ├── vite.config.ts       # Configuration Vite
│   └── package.json         # Dépendances Node.js
├── GUIDE_INSTALLATION.md    # Guide d'installation détaillé
├── TESTING.md              # Guide des tests
├── DEMO-GUIDE.md           # Guide de démonstration
└── RESOLUTION-PROBLEMES.md # Guide de résolution des problèmes
```

## 🚀 Installation et Démarrage

### Prérequis
- Python 3.11+
- Node.js 18+
- npm ou yarn

### 🔧 Installation Rapide

#### 1. Backend Django
```bash
# Cloner le repository
git clone <repository-url>
cd peproscolaire/backend

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Migrer la base de données
DJANGO_SETTINGS_MODULE=config.settings_minimal python manage.py migrate

# Créer des données de test (optionnel)
python create_sample_grades.py

# Lancer le serveur backend
DJANGO_SETTINGS_MODULE=config.settings_minimal python manage.py runserver
```

Le backend sera accessible sur **http://127.0.0.1:8000/**

#### 2. Frontend Vue.js
```bash
# Aller dans le dossier frontend
cd peproscolaire/frontend/peproscolaire-ui

# Installer les dépendances
npm install

# Configurer l'environnement
cp .env.example .env.local

# Lancer le serveur de développement
npm run dev
```

Le frontend sera accessible sur **http://localhost:5173/**

### ⚙️ Configuration

Fichier `/frontend/peproscolaire-ui/.env.local` :
```bash
VITE_API_URL=http://127.0.0.1:8000/api/v1
VITE_USE_MOCK_API=false
```

## 🎮 Utilisation

### 👤 Comptes de Démonstration

Le système inclut des comptes de test pré-configurés dans `demo.db` :

| **Rôle** | **Username** | **Email** | **Mot de passe** | **Interface** |
|-----------|--------------|-----------|-------------------|---------------|
| **Élève** | `eleve1` | `pierre.durand@test.com` | `password123` | Dashboard élève, devoirs, notes |
| **Enseignant** | `prof.math` | `jean.martin@test.com` | `password123` | Cahier de textes, notes, classes |
| **Parent** | `parent` | `parent@test.com` | `password123` | Suivi enfant, messagerie |
| **Admin** | `admin` | `admin@test.com` | `password123` | Gestion complète |

### 🎯 Parcours de Test Recommandé

1. **Connexion** → http://localhost:5173/login
2. **Se connecter** avec un compte de test
3. **Explorer l'interface** adaptée au rôle
4. **Tester les modules** :
   - Tableau de bord avec statistiques temps réel
   - Devoirs avec données backend
   - Emploi du temps avec cours programmés
   - Notes et évaluations
   - Messagerie interne

### 🌐 Routes par Type d'Utilisateur

- **Élèves** : `/student/*` (dashboard, homework, grades, messages, timetable)
- **Enseignants** : `/teacher/*` (dashboard, homework, grades, attendance, messages)
- **Parents** : `/parent/*` (dashboard, children, grades, messages, timetable)
- **Administrateurs** : `/admin/*` (dashboard, users, statistics, settings)

## 📱 Fonctionnalités Implémentées

### ✅ Authentification et Sécurité
- **Système multi-rôles** : Student, Parent, Teacher, Admin avec permissions
- **JWT Authentication** : Tokens sécurisés avec refresh automatique
- **Routes protégées** : Guards selon les permissions utilisateur
- **User Model personnalisé** : UUID comme clé primaire

### ✅ Interface Utilisateur
- **Design System cohérent** : 30+ composants UI réutilisables
- **Responsive Design** : Mobile/Desktop optimisé
- **Navigation adaptative** : Menus spécialisés par rôle
- **Gestion d'état réactive** : Pinia avec storeToRefs

### ✅ Modules Métier Fonctionnels

#### 📊 Tableaux de bord
- Statistiques temps réel par rôle
- Widgets personnalisés (StatCard)
- Actions rapides contextuelles
- Activité récente

#### 📝 Gestion des devoirs
- **Backend complet** : Models Homework, HomeworkSubmission
- **CRUD complet** : Création, modification, suppression
- **Statuts multiples** : draft, published, archived
- **Soumissions** : Gestion des rendus élèves
- **Interface teacher/student** : Vues adaptées

#### ⏰ Emploi du temps
- **Models complexes** : Schedule, TimeSlot, Subject, Room
- **Vue hebdomadaire** : Calendrier interactif
- **Transformation de données** : API ↔ Frontend
- **Gestion des conflits** : Validation backend

#### 📈 Notes et évaluations
- **Système complet** : Evaluation, Grade, GradingPeriod
- **API REST** : Endpoints CRUD avec filtres
- **Calculs automatiques** : Moyennes et statistiques
- **Interface notation** : Saisie et consultation

#### 💬 Messagerie
- **Système interne** : Conversation, Message, Participant
- **Interface moderne** : Style WhatsApp/Slack
- **Gestion réactive** : storeToRefs pour la réactivité
- **Navigation correcte** : Routes spécialisées par rôle

#### 👥 Vie scolaire
- **Models Attendance** : Gestion présences/absences
- **Interface enseignant** : Saisie appel
- **Suivi parental** : Consultation absences

### ✅ Architecture Technique

#### Backend Django
- **Apps modulaires** : Séparation claire des responsabilités
- **Models relationnels** : ForeignKey et ManyToMany optimisées
- **API REST complète** : DRF avec sérializers
- **Validation métier** : Clean methods et contraintes
- **Gestion d'erreurs** : Responses HTTP appropriées

#### Frontend Vue.js
- **Composition API** : Code moderne et maintenable
- **TypeScript strict** : Typage complet
- **Stores Pinia** : State management modulaire
- **API Client** : Axios avec intercepteurs et retry
- **Composants réutilisables** : Architecture DRY

## 🧪 Tests et Qualité

### Tests Backend
```bash
cd backend
source venv/bin/activate
DJANGO_SETTINGS_MODULE=config.settings_minimal python manage.py test
```

### Tests Frontend
```bash
cd frontend/peproscolaire-ui
npm run test              # Tests unitaires Vitest
npm run test:coverage     # Coverage report
npm run lint              # ESLint + TypeScript
npm run type-check        # Vérification types
```

### Qualité Code
- **Backend** : Tests Django + Validation models
- **Frontend** : Vitest + Testing Library + TypeScript strict
- **Linting** : ESLint + Prettier configurés
- **Types** : Interface TypeScript ↔ Models Django

## 🎯 État Actuel et Prochaines Étapes

### ✅ Fonctionnalités Opérationnelles
1. **Authentification complète** : Multi-rôles avec JWT
2. **Navigation adaptative** : Routes spécialisées
3. **CRUD devoirs** : Backend + Frontend complets
4. **Emploi du temps** : Affichage et gestion
5. **Notes** : Système d'évaluation fonctionnel
6. **Messagerie** : Communication interne
7. **Tableaux de bord** : Statistiques temps réel

### 🔄 En Cours de Finalisation
1. **Tests end-to-end** : Couverture complète
2. **Gestion d'erreurs** : Fallbacks robustes
3. **Performance** : Optimisations frontend
4. **Documentation** : Guides utilisateur

### 🚀 Évolutions Futures
1. **Modules IA** : Génération d'appréciations, détection de risques
2. **Déploiement** : Docker + CI/CD
3. **Multi-tenant** : Architecture SaaS
4. **Mobile** : Application React Native

## 📚 Documentation

- **[Guide d'installation](GUIDE_INSTALLATION.md)** : Installation détaillée pas à pas
- **[Guide de démonstration](DEMO-GUIDE.md)** : Présentation des fonctionnalités
- **[Tests et déploiement](TESTING.md)** : Procédures de test et build
- **[Résolution des problèmes](RESOLUTION-PROBLEMES.md)** : FAQ et dépannage

## 🤝 Contribution

Le projet est en développement actif. Contributions bienvenues !

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)  
5. Créer une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus de détails.

## 👥 Auteur

**Walid** - Enseignant et développeur  
*Créer des outils modernes pour l'éducation* 🎓

---

*PeproScolaire - Une solution moderne pour la gestion scolaire* 🚀