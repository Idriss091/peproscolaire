# 🧪 Guide de Tests - PeproScolaire

Ce guide décrit la stratégie de tests et les procédures de validation pour **PeproScolaire**, couvrant à la fois le backend Django et le frontend Vue.js.

## 📊 Vue d'ensemble de l'Architecture de Tests

### Stratégie Multi-niveaux
- **Tests unitaires** : Composants et fonctions individuels
- **Tests d'intégration** : Interactions entre modules
- **Tests End-to-End** : Workflows utilisateur complets
- **Tests d'API** : Validation des endpoints Django
- **Tests de performance** : Temps de réponse et charge

### Stack Technique de Tests
- **Backend** : Django TestCase + Pytest + Coverage
- **Frontend** : Vitest + Vue Test Utils + Testing Library
- **E2E** : Playwright (recommandé pour le futur)
- **API** : Postman/Insomnia + Scripts automatisés

## 🏗️ Structure des Tests

```
peproscolaire/
├── backend/
│   ├── apps/*/tests/              # Tests Django par application
│   │   ├── test_models.py         # Tests des modèles
│   │   ├── test_views.py          # Tests des vues/API
│   │   ├── test_serializers.py    # Tests des sérialiseurs
│   │   └── conftest.py            # Configuration pytest
│   ├── pytest.ini                # Configuration globale pytest
│   └── coverage.ini               # Configuration couverture
├── frontend/peproscolaire-ui/
│   ├── src/test/                  # Configuration et utilitaires
│   │   ├── setup.ts               # Setup global Vitest
│   │   ├── utils.ts               # Utilitaires de test
│   │   └── README.md              # Guide des tests frontend
│   ├── src/**/__tests__/          # Tests unitaires par module
│   │   ├── components/            # Tests des composants Vue
│   │   ├── stores/                # Tests des stores Pinia
│   │   ├── views/                 # Tests des pages
│   │   └── api/                   # Tests des clients API
│   ├── vitest.config.ts           # Configuration Vitest
│   └── tsconfig.*.json            # Configuration TypeScript
├── scripts/
│   ├── run-tests.sh               # Script de lancement global
│   └── test-setup.sh              # Setup environnement de test
└── test-results/                  # Rapports et artifacts
```

## 🔧 Installation et Configuration

### Backend Django

```bash
cd backend
source venv/bin/activate

# Installer les dépendances de test
pip install pytest pytest-django pytest-cov factory-boy faker

# Configuration pytest dans pytest.ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = config.settings_minimal
python_files = tests.py test_*.py *_tests.py
addopts = --tb=short --strict-markers --cov=apps --cov-report=html
```

### Frontend Vue.js

```bash
cd frontend/peproscolaire-ui

# Dépendances déjà installées
npm install

# Configuration dans vitest.config.ts
export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['src/test/setup.ts']
  }
})
```

## 🚀 Commandes de Test

### Script Global (Recommandé)

```bash
# Tous les tests (backend + frontend)
./scripts/run-tests.sh all

# Backend uniquement
./scripts/run-tests.sh backend

# Frontend uniquement  
./scripts/run-tests.sh frontend

# Tests avec couverture
./scripts/run-tests.sh coverage

# Tests E2E (futur)
./scripts/run-tests.sh e2e
```

### Tests Backend Spécifiques

```bash
cd backend
source venv/bin/activate

# Tous les tests Django
DJANGO_SETTINGS_MODULE=config.settings_minimal python manage.py test

# Tests d'une application
python manage.py test apps.authentication.tests

# Tests avec pytest (plus de fonctionnalités)
pytest apps/authentication/tests/

# Tests avec couverture
pytest --cov=apps --cov-report=html

# Tests spécifiques
pytest apps/authentication/tests/test_models.py::UserModelTest::test_create_user
```

### Tests Frontend Spécifiques

```bash
cd frontend/peproscolaire-ui

# Tests unitaires
npm run test

# Tests en mode watch (développement)
npm run test:watch

# Tests avec interface UI
npm run test:ui

# Couverture de code
npm run test:coverage

# Linting et vérification des types
npm run lint
npm run type-check

# Tests spécifiques
npm run test -- auth.test.ts
npm run test -- --grep "login"
```

## 📋 Tests Implémentés

### ✅ Tests Backend Django

#### Authentication (`apps/authentication/tests/`)

```python
# test_models.py
class UserModelTest(TestCase):
    def test_create_user_with_uuid(self):
        """Test que les utilisateurs ont des UUID comme clé primaire"""
        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com', 
            password='testpass123',
            user_type='teacher'
        )
        
        self.assertIsInstance(user.id, uuid.UUID)
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.user_type, 'teacher')
        self.assertTrue(user.check_password('testpass123'))

    def test_user_types_validation(self):
        """Test validation des types d'utilisateur"""
        valid_types = ['student', 'teacher', 'parent', 'admin']
        for user_type in valid_types:
            user = User.objects.create_user(
                username=f'test_{user_type}@example.com',
                email=f'test_{user_type}@example.com',
                password='testpass123',
                user_type=user_type
            )
            self.assertEqual(user.user_type, user_type)
```

#### API Views (`apps/authentication/tests/test_views.py`)

```python
class AuthAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123',
            user_type='teacher'
        )

    def test_login_with_valid_credentials(self):
        """Test connexion avec identifiants valides"""
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'test@example.com',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.data)
        self.assertIn('user', response.data)

    def test_user_detail_api(self):
        """Test récupération des détails utilisateur"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/auth/me/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], self.user.email)
```

#### Applications Métier

```python
# apps/grades/tests/test_models.py
class GradeModelTest(TestCase):
    def test_grade_calculation(self):
        """Test calcul automatique des moyennes"""
        # Tests des modèles Evaluation, Grade, etc.
        
# apps/homework/tests/test_models.py  
class HomeworkModelTest(TestCase):
    def test_homework_submission(self):
        """Test soumission de devoirs"""
        # Tests du système de devoirs

# apps/timetable/tests/test_models.py
class ScheduleModelTest(TestCase):
    def test_schedule_conflicts(self):
        """Test détection conflits d'emploi du temps"""
        # Tests de validation des créneaux
```

### ✅ Tests Frontend Vue.js

#### Tests des Stores (`src/stores/__tests__/`)

```typescript
// auth.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../auth'

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('should login with teacher credentials', async () => {
    const authStore = useAuthStore()
    
    // Mock API response
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        access_token: 'fake-token',
        user: { id: '123', user_type: 'teacher', email: 'test@example.com' }
      })
    } as Response)

    await authStore.login({
      username: 'prof.math',
      password: 'password123'
    })

    expect(authStore.isAuthenticated).toBe(true)
    expect(authStore.user?.user_type).toBe('teacher')
    expect(authStore.token).toBe('fake-token')
  })

  it('should handle login failure', async () => {
    const authStore = useAuthStore()
    
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({ error: 'Invalid credentials' })
    } as Response)

    await expect(authStore.login({
      username: 'wrong@example.com',
      password: 'wrongpass'
    })).rejects.toThrow()

    expect(authStore.isAuthenticated).toBe(false)
  })

  it('should persist auth state in localStorage', async () => {
    const authStore = useAuthStore()
    
    authStore.token = 'test-token'
    authStore.user = { id: '123', user_type: 'student' }
    
    // Vérifier la persistance
    expect(localStorage.getItem('auth_token')).toBe('test-token')
    expect(JSON.parse(localStorage.getItem('auth_user') || '{}')).toEqual(
      authStore.user
    )
  })
})
```

```typescript
// homework.test.ts  
describe('Homework Store', () => {
  it('should fetch homework by user type', async () => {
    const homeworkStore = useHomeworkStore()
    const authStore = useAuthStore()
    
    authStore.user = { user_type: 'student' }
    
    await homeworkStore.fetchHomework()
    
    // Vérifier que seuls les devoirs de l'élève sont récupérés
    expect(homeworkStore.homeworks).toHaveLength(5)
    expect(homeworkStore.upcomingHomework).toHaveLength(2)
  })
})
```

#### Tests des Composants (`src/components/__tests__/`)

```typescript
// ui/BaseButton.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseButton from '../BaseButton.vue'

describe('BaseButton', () => {
  it('renders with default props', () => {
    const wrapper = mount(BaseButton, {
      slots: { default: 'Click me' }
    })
    
    expect(wrapper.text()).toBe('Click me')
    expect(wrapper.classes()).toContain('btn-primary')
  })

  it('emits click event', async () => {
    const wrapper = mount(BaseButton)
    
    await wrapper.trigger('click')
    
    expect(wrapper.emitted('click')).toHaveLength(1)
  })

  it('shows loading state', () => {
    const wrapper = mount(BaseButton, {
      props: { loading: true }
    })
    
    expect(wrapper.find('.loading-spinner').exists()).toBe(true)
    expect(wrapper.attributes('disabled')).toBeDefined()
  })
})
```

```typescript
// ui/BaseModal.test.ts
describe('BaseModal', () => {
  it('shows/hides based on modelValue', async () => {
    const wrapper = mount(BaseModal, {
      props: { modelValue: false }
    })
    
    expect(wrapper.find('.modal-overlay').isVisible()).toBe(false)
    
    await wrapper.setProps({ modelValue: true })
    
    expect(wrapper.find('.modal-overlay').isVisible()).toBe(true)
  })
})
```

#### Tests des Views (`src/views/__tests__/`)

```typescript
// DashboardView.test.ts
describe('DashboardView', () => {
  it('shows teacher dashboard for teacher user', async () => {
    const authStore = useAuthStore()
    authStore.user = { user_type: 'teacher' }
    
    const wrapper = mount(DashboardView, {
      global: {
        plugins: [createPinia()]
      }
    })
    
    expect(wrapper.find('[data-testid="teacher-dashboard"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="student-dashboard"]').exists()).toBe(false)
  })

  it('loads dashboard data on mount', async () => {
    const homeworkStore = useHomeworkStore()
    const fetchSpy = vi.spyOn(homeworkStore, 'fetchHomework')
    
    mount(DashboardView)
    
    expect(fetchSpy).toHaveBeenCalled()
  })
})
```

## 📊 Couverture de Code et Métriques

### Objectifs de Couverture

- **Backend Django** : ≥ 85% de couverture globale
  - Models : ≥ 90%
  - Views/API : ≥ 85%
  - Utils/Helpers : ≥ 95%

- **Frontend Vue.js** : ≥ 80% de couverture globale  
  - Stores Pinia : ≥ 90%
  - Composants UI : ≥ 85%
  - Utils/Helpers : ≥ 95%

### Génération des Rapports

```bash
# Backend - Rapport de couverture HTML
cd backend
pytest --cov=apps --cov-report=html
open htmlcov/index.html

# Frontend - Rapport de couverture
cd frontend/peproscolaire-ui
npm run test:coverage
open coverage/index.html

# Métriques JSON pour CI/CD
pytest --cov=apps --cov-report=json
npm run test:coverage -- --reporter=json
```

### Métriques de Performance

```bash
# Tests de performance backend
cd backend
python manage.py test --timing

# Analyse bundle frontend
cd frontend/peproscolaire-ui
npm run build
npm run analyze

# Métriques temps de réponse API
curl -w "@curl-format.txt" -s -o /dev/null http://127.0.0.1:8000/api/v1/auth/me/
```

## 🔄 Intégration Continue (CI/CD)

### GitHub Actions

```yaml
# .github/workflows/tests.yml
name: Tests Suite
on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Cache pip dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('backend/requirements.txt') }}
          
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          
      - name: Run tests with coverage
        run: |
          cd backend
          pytest --cov=apps --cov-report=xml
          
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js 18
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/peproscolaire-ui/package-lock.json
          
      - name: Install dependencies
        run: |
          cd frontend/peproscolaire-ui
          npm ci
          
      - name: Run tests
        run: |
          cd frontend/peproscolaire-ui
          npm run test:coverage
          npm run lint
          npm run type-check
          
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./frontend/peproscolaire-ui/coverage/coverage-final.json

  e2e-tests:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup services
        run: |
          # Démarrer backend et frontend
          docker-compose up -d
          
      - name: Run E2E tests
        run: |
          npx playwright test
```

### Pre-commit Hooks

```bash
# Installation
pip install pre-commit
cd frontend/peproscolaire-ui && npm install husky lint-staged

# Configuration .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
        
  - repo: local
    hooks:
      - id: django-tests
        name: Django Tests
        entry: bash -c 'cd backend && python manage.py test --failfast'
        language: system
        pass_filenames: false
        
      - id: vue-tests
        name: Vue Tests
        entry: bash -c 'cd frontend/peproscolaire-ui && npm run test:ci'
        language: system
        pass_filenames: false
```

## 🐛 Debugging et Troubleshooting

### Debugging Tests Backend

```python
# Test avec pdb
import pdb; pdb.set_trace()

# Test avec logging détaillé
import logging
logging.basicConfig(level=logging.DEBUG)

# Test spécifique avec verbosité
pytest -vv -s apps/authentication/tests/test_models.py::UserModelTest::test_create_user

# Test avec profiling
pytest --profile
```

### Debugging Tests Frontend

```typescript
// Test avec debug Vue Test Utils
import { debug } from '@vue/test-utils'

test('component debug', () => {
  const wrapper = mount(Component)
  debug() // Affiche le HTML du composant
})

// Test avec console
test('store debug', () => {
  const store = useAuthStore()
  console.log('Store state:', store.$state)
})

// Test spécifique avec verbosité
npm run test -- --reporter=verbose auth.test.ts
```

### Problèmes Courants

#### Backend

```bash
# Erreur base de données
rm backend/demo.db
python manage.py migrate

# Erreur CORS dans les tests
# Vérifier CORS_ALLOWED_ORIGINS dans settings

# Erreur d'importation
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
```

#### Frontend

```bash
# Erreur modules manquants
rm -rf node_modules package-lock.json
npm install

# Erreur TypeScript dans tests
npm run type-check

# Erreur cache Vitest
rm -rf node_modules/.vitest
```

## 📋 Checklist de Tests par Fonctionnalité

### ✅ Authentification
- [x] Login avec username/email
- [x] Login avec différents rôles (student, teacher, parent, admin)  
- [x] Logout et nettoyage session
- [x] Persistance token JWT dans localStorage
- [x] Redirection automatique selon le rôle
- [x] Gestion erreurs de connexion
- [x] Refresh token automatique

### ✅ Navigation et Routes
- [x] Routes protégées avec guards
- [x] Navigation conditionnelle par rôle
- [x] Routes spécialisées (/student/*, /teacher/*, etc.)
- [x] Redirection par défaut
- [x] Gestion 404

### 🔄 Gestion des Devoirs
- [x] Récupération devoirs par rôle
- [x] Affichage différencié teacher/student
- [x] Filtres par statut (draft, published, archived)
- [ ] Création/modification devoirs (teacher)
- [ ] Soumission devoirs (student)
- [ ] Système de notifications

### 🔄 Emploi du Temps
- [x] Récupération emploi du temps
- [x] Transformation données API ↔ Frontend
- [x] Affichage calendaire hebdomadaire
- [ ] Gestion conflits de créneaux
- [ ] Vue par jour/semaine/mois

### 🔄 Système de Notes
- [x] Récupération notes par rôle
- [x] Calculs moyennes automatiques
- [x] API CRUD évaluations
- [ ] Saisie notes par enseignant
- [ ] Bulletins de notes
- [ ] Système compétences

### 🔄 Messagerie
- [x] Structure conversations/messages
- [x] Navigation routes spécialisées
- [x] Interface moderne (style chat)
- [ ] Envoi messages temps réel
- [ ] Notifications non lus
- [ ] Pièces jointes

### ✅ Interface Utilisateur
- [x] Composants UI de base (BaseButton, BaseModal, etc.)
- [x] Navigation responsive
- [x] Gestion d'état réactive avec Pinia
- [x] Design System cohérent
- [ ] Thème sombre/clair
- [ ] Tests accessibilité
- [ ] Tests performance

## 📚 Ressources et Documentation

### Documentation Officielle
- [Django Testing](https://docs.djangoproject.com/en/5.0/topics/testing/)
- [Vitest Guide](https://vitest.dev/guide/)
- [Vue Test Utils](https://test-utils.vuejs.org/)
- [Testing Library Vue](https://testing-library.com/docs/vue-testing-library/intro/)
- [Playwright E2E](https://playwright.dev/)

### Bonnes Pratiques
- [Testing Best Practices](https://testing-library.com/docs/guiding-principles)
- [Vue Testing Handbook](https://lmiller1990.github.io/vue-testing-handbook/)
- [Django Testing Best Practices](https://docs.djangoproject.com/en/5.0/topics/testing/overview/)

### Outils Recommandés
- **Coverage** : Couverture de code
- **Factory Boy** : Génération données de test Django
- **MSW** : Mock Service Worker pour API mocking
- **Playwright** : Tests E2E cross-browser

---

## 🎯 Prochaines Étapes

### Priorité Haute
1. **Compléter tests E2E** : Scénarios utilisateur complets
2. **Tests performance** : Benchmarks et optimisations
3. **Tests sécurité** : Validation permissions et injection
4. **Tests accessibilité** : Conformité WCAG

### Priorité Moyenne  
1. **Tests de charge** : Comportement sous stress
2. **Tests cross-browser** : Compatibilité navigateurs
3. **Tests mobile** : Interface responsive
4. **Monitoring tests** : Métriques qualité continue

> **Note** : Ce guide évolue avec le projet. Consultez régulièrement pour les mises à jour et nouveaux patterns de tests.