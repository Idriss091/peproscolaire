# Guide de Tests - PeproScolaire

Ce guide décrit la stratégie de tests mise en place pour le projet PeproScolaire, en particulier pour les modules d'Intelligence Artificielle.

## 📊 Vue d'ensemble

Le projet utilise une approche de tests multi-niveaux :
- **Tests unitaires** : Fonctions et composants individuels
- **Tests d'intégration** : Interactions entre modules
- **Tests End-to-End** : Workflows complets utilisateur
- **Tests de performance** : Benchmarks et optimisations

## 🏗️ Structure des Tests

```
/tests
├── backend/
│   ├── apps/ai_analytics/
│   │   ├── test_models.py          # Tests des modèles ML
│   │   ├── test_views.py           # Tests des APIs
│   │   ├── test_tasks.py           # Tests des tâches Celery
│   │   └── test_integration.py     # Tests d'intégration
│   └── requirements-test.txt
├── frontend/
│   ├── src/stores/__tests__/       # Tests des stores Pinia
│   ├── src/components/__tests__/   # Tests des composants Vue
│   ├── src/api/__tests__/          # Tests des services API
│   └── vitest.config.ts
└── scripts/
    └── run-tests.sh               # Script de lancement global
```

## 🔧 Configuration et Installation

### Backend (Django + Pytest)

```bash
cd backend
pip install -r requirements.txt
pip install pytest pytest-django coverage
```

### Frontend (Vue.js + Vitest)

```bash
cd frontend/peproscolaire-ui
npm install
npm install --save-dev @vue/test-utils vitest jsdom
```

## 🚀 Lancement des Tests

### Script Global (Recommandé)

```bash
# Tous les tests
./scripts/run-tests.sh all

# Backend uniquement
./scripts/run-tests.sh backend

# Frontend uniquement
./scripts/run-tests.sh frontend

# Tests E2E
./scripts/run-tests.sh e2e
```

### Tests Backend Spécifiques

```bash
cd backend

# Tests des modèles IA
python manage.py test apps.ai_analytics.test_models

# Tests des APIs
python manage.py test apps.ai_analytics.test_views

# Tests des tâches Celery
python manage.py test apps.ai_analytics.test_tasks

# Tests d'intégration
python manage.py test apps.ai_analytics.test_integration

# Avec couverture
coverage run --source='apps/ai_analytics' manage.py test apps.ai_analytics
coverage report --show-missing
coverage html
```

### Tests Frontend Spécifiques

```bash
cd frontend/peproscolaire-ui

# Tests des modules IA
npm run test:ai

# Tests des composants
npm run test:components

# Tests des APIs
npm run test:api

# Avec couverture
npm run test:coverage

# Mode watch
npm run test:watch
```

## 📋 Détail des Tests Implémentés

### 🤖 Tests des Modules IA

#### Tests des Modèles ML (`test_models.py`)

- **DropoutRiskModelTest** : Tests du modèle de détection de décrochage
  - Extraction des features (18 indicateurs)
  - Prédictions de risque (faible, modéré, élevé)
  - Gestion des données manquantes
  - Importance des facteurs de risque

- **ModelTrainerTest** : Tests de l'entraînement
  - Entraînement du modèle avec données synthétiques
  - Évaluation des performances (accuracy, precision, recall, F1)
  - Génération de données d'entraînement
  - Gestion des erreurs d'entraînement

- **RiskProfileModelTest** : Tests du modèle de profil de risque
  - Création et mise à jour des profils
  - Calcul automatique du niveau de risque
  - Relations avec les étudiants et années scolaires

#### Tests des APIs (`test_views.py`)

- **GenerateAppreciationAPITest** : Tests de génération d'appréciations
  - Génération simple avec options personnalisées
  - Gestion des erreurs (étudiant inexistant, données invalides)
  - Validation des permissions

- **GenerateMultipleAppreciationsAPITest** : Tests de génération en lot
  - Génération pour une classe entière
  - Gestion des échecs partiels
  - Statistiques de génération

- **PredictStudentRiskAPITest** : Tests de prédiction de risque
  - Prédiction pour différents niveaux de risque
  - Facteurs de risque et recommandations
  - Cache des prédictions

- **AIModelStatusAPITest** : Tests du statut des modèles
  - Récupération des performances des modèles
  - Métriques globales du système
  - État des modèles (actif, erreur, entraînement)

#### Tests des Tâches Asynchrones (`test_tasks.py`)

- **MLModelTrainingTaskTest** : Tests d'entraînement des modèles
  - Entraînement réussi et échecs
  - Retry automatique en cas d'erreur temporaire
  - Types de modèles supportés

- **StudentRiskAnalysisTaskTest** : Tests d'analyse de risque
  - Analyse complète d'un étudiant
  - Déclenchement d'alertes automatiques
  - Gestion des données insuffisantes

- **BulkAnalysisTaskTest** : Tests d'analyse en masse
  - Analyse quotidienne automatique
  - Détection de patterns hebdomadaires
  - Performance sur de gros volumes

#### Tests d'Intégration (`test_integration.py`)

- **AIModulesIntegrationTest** : Workflows complets
  - Analyse → Profil → Alerte → Intervention
  - Génération d'appréciations bout en bout
  - Entraînement et validation des modèles
  - Sécurité et permissions

- **PerformanceIntegrationTest** : Tests de performance
  - Métriques du dashboard avec 50+ étudiants
  - Optimisation des requêtes SQL
  - Temps de réponse des APIs critiques

### 🖥️ Tests Frontend

#### Tests des Stores (`ai-modules.test.ts`)

- **State Management** : Tests de gestion d'état
  - Initialisation avec valeurs par défaut
  - Gestion des états de chargement et d'erreur
  - Mise à jour réactive des données

- **Model Status** : Tests du statut des modèles
  - Récupération et mise à jour du statut
  - Propriétés calculées (isDropoutModelActive)
  - Performance des modèles

- **Appreciation Generation** : Tests de génération
  - Génération simple et multiple
  - Cache des appréciations
  - Historique et gestion des limites

#### Tests des Composants (`AiDashboardView.test.ts`)

- **Component Rendering** : Tests de rendu
  - Affichage sans erreurs
  - Métriques de performance des modèles
  - Distribution des risques
  - États de chargement

- **User Interactions** : Tests d'interactions
  - Boutons d'actions rapides
  - Déclenchement d'analyses
  - Gestion des erreurs utilisateur

- **Reactive Updates** : Tests de réactivité
  - Mise à jour lors des changements de store
  - Recalcul des propriétés calculées

#### Tests des APIs (`ai-modules.test.ts`)

- **API Calls** : Tests des appels API
  - Tous les endpoints des modules IA
  - Gestion des erreurs HTTP
  - Authentification et permissions

- **Data Transformation** : Tests de transformation
  - Conversion des données API vers interface
  - Validation des types TypeScript
  - Gestion des réponses malformées

## 📈 Métriques et Couverture

### Objectifs de Couverture

- **Backend** : ≥ 90% de couverture de code
- **Frontend** : ≥ 85% de couverture de code
- **APIs critiques** : 100% de couverture

### Métriques de Performance

- **Temps de réponse API** : < 200ms pour les endpoints standards
- **Analyse de risque** : < 2s par étudiant
- **Génération d'appréciation** : < 5s par étudiant
- **Dashboard metrics** : < 1s avec 1000+ profils

## 🔄 CI/CD et Automatisation

### GitHub Actions

Le projet utilise GitHub Actions pour l'automatisation :

```yaml
# .github/workflows/tests.yml
- Backend tests (PostgreSQL + Redis)
- Frontend tests (Node.js)
- Integration tests
- Security tests (Bandit, npm audit)
- Performance tests (Locust)
```

### Hooks Pré-commit

```bash
# Installation des hooks
pre-commit install

# Vérifications automatiques :
- Linting (flake8, ESLint)
- Formatting (black, prettier)
- Tests unitaires critiques
- Sécurité (bandit)
```

## 🐛 Debugging et Troubleshooting

### Problèmes Courants

#### Tests Backend

```bash
# Erreur de base de données
export DATABASE_URL="sqlite:///test.db"
python manage.py migrate

# Erreur de permissions
python manage.py collectstatic --noinput

# Erreur de dépendances
pip install -r requirements.txt
```

#### Tests Frontend

```bash
# Erreur de modules
npm install

# Erreur TypeScript
npm run type-check

# Cache Vitest
npx vitest run --reporter=verbose
```

### Debugging Avancé

#### Tests ML en Mode Debug

```python
# Dans test_models.py
import pdb; pdb.set_trace()

# Ou avec logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Tests Frontend en Mode Debug

```javascript
// Dans les tests Vitest
import { debug } from '@vue/test-utils'
debug() // Affiche le HTML du composant
```

## 📊 Rapports et Monitoring

### Rapports de Couverture

```bash
# Backend
open backend/htmlcov/index.html

# Frontend
open frontend/peproscolaire-ui/coverage/index.html
```

### Rapports de Performance

```bash
# Profiling Python
python -m cProfile manage.py test apps.ai_analytics

# Bundle analyzer Frontend
npm run build:analyze
```

## 🚀 Bonnes Pratiques

### Tests Backend

1. **Isolation** : Chaque test est indépendant
2. **Mocking** : Mock des services externes (OpenAI, etc.)
3. **Fixtures** : Données de test cohérentes
4. **Performance** : Tests de charge pour les analyses en masse

### Tests Frontend

1. **Component Testing** : Tests isolés des composants
2. **Store Testing** : Tests de la logique métier
3. **API Mocking** : Mock des appels réseau
4. **Accessibility** : Tests d'accessibilité

### Tests d'Intégration

1. **Scénarios Réels** : Tests basés sur les cas d'usage
2. **Données Cohérentes** : Jeux de données représentatifs
3. **Performance** : Benchmarks sur des volumes réels
4. **Sécurité** : Tests de permissions et validation

## 📚 Ressources

- [Pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [Vue Test Utils](https://test-utils.vuejs.org/)
- [Django Testing](https://docs.djangoproject.com/en/4.2/topics/testing/)

---

> **Note** : Ce guide évolue avec le projet. Consultez la documentation pour les mises à jour.