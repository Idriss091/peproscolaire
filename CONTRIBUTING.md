# Guide de contribution - PeproScolaire 🤝

Merci de votre intérêt pour contribuer à PeproScolaire ! Ce guide vous aidera à comprendre comment participer efficacement au développement du projet.

## 🎯 Comment contribuer

### Types de contributions recherchées

1. **🐛 Correction de bugs** - Résolution de problèmes identifiés
2. **✨ Nouvelles fonctionnalités** - Ajout de modules ou d'améliorations
3. **📚 Documentation** - Amélioration de la documentation technique et utilisateur
4. **🧪 Tests** - Ajout de tests unitaires et d'intégration
5. **🎨 Améliorations UI/UX** - Optimisation de l'interface utilisateur
6. **⚡ Performance** - Optimisations backend et frontend
7. **🤖 Modules IA** - Développement des algorithmes d'intelligence artificielle

### Domaines prioritaires

- **Tests automatisés** : Couverture de tests pour backend et frontend
- **Modules IA** : Finalisation des algorithmes ML et NLP
- **Performance** : Optimisations base de données et interface
- **Accessibilité** : Amélioration WCAG pour tous les utilisateurs
- **Documentation** : Guides utilisateur et technique

## 🚀 Processus de contribution

### 1. Préparation

```bash
# Fork du repository
git clone https://github.com/votre-username/peproscolaire.git
cd peproscolaire

# Créer une branche pour votre contribution
git checkout -b feature/nom-de-votre-fonctionnalite
# ou
git checkout -b fix/description-du-bug
```

### 2. Configuration de l'environnement

#### Backend Django
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements/dev.txt
python manage.py migrate
python manage.py runserver
```

#### Frontend Vue.js
```bash
cd frontend/peproscolaire-ui
npm install
npm run dev
```

### 3. Développement

#### Standards de code

**Backend Python/Django :**
- **PEP 8** : Style de code Python standard
- **Black** : Formatage automatique du code
- **isort** : Organisation des imports
- **flake8** : Linting et vérification de la qualité

```bash
# Formater le code
black apps/
isort apps/
flake8 apps/
```

**Frontend TypeScript/Vue :**
- **ESLint** : Linting JavaScript/TypeScript
- **Prettier** : Formatage du code
- **Vue Style Guide** : Conventions Vue.js officiales
- **Composition API** : Préférer la Composition API à l'Options API

```bash
# Formater et vérifier le code
npm run lint
npm run format
npm run type-check
```

#### Convention de nommage

**Fichiers et dossiers :**
- `kebab-case` pour les fichiers et dossiers
- `PascalCase` pour les composants Vue
- `camelCase` pour les fonctions et variables
- `SCREAMING_SNAKE_CASE` pour les constantes

**Git commits :**
```
type(scope): description

Types acceptés :
- feat: nouvelle fonctionnalité
- fix: correction de bug
- docs: documentation
- style: formatage (pas de changement de code)
- refactor: refactorisation de code
- test: ajout/modification de tests
- chore: tâches de maintenance

Exemples :
feat(grades): add bulk grade entry component
fix(auth): resolve JWT token expiration issue
docs(api): update authentication endpoints documentation
test(frontend): add unit tests for grade components
```

### 4. Tests

#### Tests Backend
```bash
# Tests unitaires Django
python manage.py test

# Tests avec coverage
coverage run manage.py test
coverage report
coverage html

# Tests spécifiques à une app
python manage.py test apps.grades.tests
```

#### Tests Frontend
```bash
# Tests unitaires Vue
npm run test

# Tests avec coverage
npm run test:coverage

# Tests e2e (quand disponibles)
npm run test:e2e
```

### 5. Documentation

#### Documentation de code
- **Docstrings** : Toutes les fonctions et classes doivent être documentées
- **Commentaires** : Expliquer la logique complexe
- **Type hints** : Utiliser les annotations de type Python et TypeScript

```python
# Exemple de docstring Python
def calculate_student_average(grades: List[Grade], weights: Dict[str, float]) -> float:
    """
    Calcule la moyenne pondérée d'un élève.
    
    Args:
        grades: Liste des notes de l'élève
        weights: Coefficients par matière
        
    Returns:
        float: Moyenne pondérée sur 20
        
    Raises:
        ValueError: Si les notes sont invalides
    """
    pass
```

```typescript
// Exemple de documentation TypeScript
/**
 * Génère une appréciation IA pour un élève
 * @param studentId - Identifiant de l'élève
 * @param options - Options de génération
 * @returns Promise contenant l'appréciation générée
 */
async function generateAppreciation(
  studentId: string,
  options: AppreciationOptions
): Promise<AppreciationResult> {
  // ...
}
```

### 6. Pull Request

#### Checklist avant soumission
- [ ] Code formaté selon les standards
- [ ] Tests passent (backend et frontend)
- [ ] Documentation mise à jour si nécessaire
- [ ] Commit messages suivent la convention
- [ ] Pas de console.log ou debug prints
- [ ] Types TypeScript corrects
- [ ] Migrations Django créées si nécessaire

#### Template de Pull Request
```markdown
## Description
Description claire de ce qui a été modifié et pourquoi.

## Type de changement
- [ ] Bug fix (changement non-breaking qui corrige un problème)
- [ ] Nouvelle fonctionnalité (changement non-breaking qui ajoute une fonctionnalité)
- [ ] Breaking change (fix ou fonctionnalité qui causera un dysfonctionnement de fonctionnalités existantes)
- [ ] Changement de documentation

## Tests effectués
Décrivez les tests que vous avez effectués pour vérifier vos changements.

## Screenshots (si applicable)
Ajoutez des captures d'écran pour illustrer les changements visuels.

## Checklist
- [ ] Mon code suit les conventions du projet
- [ ] J'ai effectué une auto-review de mon code
- [ ] J'ai commenté mon code, particulièrement dans les zones difficiles à comprendre
- [ ] J'ai fait les changements correspondants dans la documentation
- [ ] Mes changements ne génèrent pas de nouveaux warnings
- [ ] J'ai ajouté des tests qui prouvent que mon fix fonctionne ou que ma fonctionnalité marche
- [ ] Les tests unitaires nouveaux et existants passent localement avec mes changements
```

## 🏗️ Architecture et patterns

### Backend Django

#### Structure recommandée pour une nouvelle app
```python
apps/nouvelle_app/
├── __init__.py
├── admin.py              # Configuration admin Django
├── apps.py               # Configuration de l'application
├── models.py             # Modèles de données
├── serializers.py        # Serializers DRF
├── views.py              # Vues API
├── urls.py               # URLs de l'app
├── permissions.py        # Permissions personnalisées
├── filters.py            # Filtres pour les listes
├── utils.py              # Utilitaires spécifiques
├── migrations/           # Migrations de base de données
└── tests/               # Tests de l'application
    ├── test_models.py
    ├── test_views.py
    └── test_serializers.py
```

#### Patterns recommandés
- **ViewSets DRF** : Utiliser ModelViewSet pour les CRUD standards
- **Serializers imbriqués** : Pour les relations complexes
- **Permissions granulaires** : Une permission par action si nécessaire
- **Filtres et recherche** : django-filter pour les listes complexes
- **Pagination** : Systématique pour toutes les listes

### Frontend Vue.js

#### Structure recommandée pour un nouveau module
```
src/components/nouveau_module/
├── ModuleView.vue           # Vue principale du module
├── ModuleList.vue           # Liste des éléments
├── ModuleForm.vue           # Formulaire de création/édition
├── ModuleDetail.vue         # Vue détaillée d'un élément
├── ModuleFilters.vue        # Composant de filtres
└── components/              # Sous-composants spécifiques
    ├── ModuleCard.vue
    └── ModuleModal.vue

src/stores/nouveau_module.ts  # Store Pinia du module
```

#### Patterns recommandés
- **Composition API** : Obligatoire pour tous les nouveaux composants
- **TypeScript strict** : Typage complet sans `any`
- **Props typées** : Interface pour toutes les props
- **Émissions typées** : `defineEmits` avec types
- **Composables** : Extraction de la logique réutilisable

## 🤖 Modules IA - Guidelines spécifiques

### Développement d'algorithmes IA

#### Structure recommandée
```python
apps/ai_modules/algorithms/
├── __init__.py
├── base.py                  # Classes de base pour les algorithmes
├── dropout_detection/       # Détection de décrochage
│   ├── __init__.py
│   ├── features.py          # Extraction de caractéristiques
│   ├── model.py             # Modèle ML
│   ├── predictor.py         # Prédicteur principal
│   └── evaluator.py         # Évaluation du modèle
├── appreciation_generator/  # Générateur d'appréciations
│   ├── __init__.py
│   ├── templates.py         # Templates d'appréciations
│   ├── nlp_processor.py     # Traitement NLP
│   └── generator.py         # Générateur principal
└── common/                  # Utilitaires communs IA
    ├── data_preprocessing.py
    ├── model_utils.py
    └── evaluation_metrics.py
```

#### Standards pour l'IA
- **Reproductibilité** : Fixer les seeds aléatoires
- **Logging** : Tracer toutes les prédictions et leur confiance
- **Validation** : Split train/validation/test systématique
- **Monitoring** : Métriques de performance en continu
- **Explicabilité** : Documenter les facteurs de décision

### Frontend IA

#### Composants spécialisés
- **Graphiques** : Utiliser Chart.js ou D3.js pour les visualisations
- **Métriques** : Affichage clair des performances IA
- **Confiance** : Toujours afficher le niveau de confiance
- **Feedback** : Permettre la validation/correction par l'utilisateur

## 🔍 Review et validation

### Process de review

1. **Review automatique** : GitHub Actions vérifie le code
2. **Review technique** : Un mainteneur examine le code
3. **Test en staging** : Déploiement automatique pour tests
4. **Validation fonctionnelle** : Test des nouvelles fonctionnalités
5. **Merge** : Intégration dans la branche principale

### Critères de validation

- ✅ **Tests passent** : Tous les tests automatisés valides
- ✅ **Code quality** : Respect des standards et conventions
- ✅ **Performance** : Pas de régression de performance
- ✅ **Sécurité** : Pas de faille de sécurité introduite
- ✅ **Documentation** : Documentation à jour
- ✅ **Compatibilité** : Fonctionne avec l'environnement cible

## 📞 Support et communication

### Canaux de communication

- **Issues GitHub** : Bugs, demandes de fonctionnalités, questions techniques
- **Pull Requests** : Discussions sur le code et les implémentations
- **Wiki** : Documentation collaborative (à venir)

### Obtenir de l'aide

1. **Consulter la documentation** : README, API docs, guides
2. **Chercher dans les issues** : Problème peut-être déjà résolu
3. **Créer une issue** : Description détaillée du problème
4. **Proposer une solution** : PR avec fix si possible

## 🏆 Reconnaissance

### Wall of fame

Les contributeurs significatifs seront reconnus dans :
- **README principal** : Section contributeurs
- **CHANGELOG** : Mention des contributions importantes
- **Documentation** : Crédits dans la documentation
- **Releases** : Reconnaissance dans les notes de version

### Types de contributions reconnues

- **Code** : Nouvelles fonctionnalités, corrections de bugs
- **Documentation** : Amélioration des guides et de la doc technique
- **Tests** : Ajout de couverture de tests
- **Design** : Améliorations UI/UX
- **Community** : Aide aux autres contributeurs, support utilisateurs

---

**Merci de contribuer à l'amélioration de PeproScolaire !** 🎓✨

*Ensemble, révolutionnons la gestion scolaire avec l'intelligence artificielle.*