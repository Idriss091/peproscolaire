# PeproScolaire Backend 🔧

API Django REST Framework pour PeproScolaire - Système de gestion scolaire avec modules IA.

[![Django](https://img.shields.io/badge/Django-5.0-green)](https://djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.14-orange)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-blue)](https://postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)

## 🚀 Démarrage rapide

```bash
# Cloner le projet
git clone <repository-url>
cd peproscolaire/backend

# Créer un environnement virtuel
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configuration base de données
createdb peproscolaire
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

**API accessible sur :** http://localhost:8000/api/
**Admin Django :** http://localhost:8000/admin/

## 🏗️ Architecture

### Stack technique
- **Framework** : Django 5.0 avec Django REST Framework
- **Base de données** : PostgreSQL avec support multi-tenant
- **Cache** : Redis (optionnel)
- **Task Queue** : Celery + RabbitMQ (pour les modules IA)
- **API** : REST avec sérializers DRF
- **Auth** : JWT avec gestion des rôles

### Structure modulaire

```
backend/
├── apps/                           # Applications Django
│   ├── authentication/            # Auth JWT + rôles
│   ├── schools/                    # Multi-tenant établissements
│   ├── users/                      # Profils utilisateurs étendus
│   ├── timetable/                  # Emplois du temps
│   ├── grades/                     # Notes et évaluations
│   ├── attendance/                 # Vie scolaire
│   ├── messaging/                  # Messagerie interne
│   ├── ai_modules/                 # Modules IA
│   └── stages/                     # Gestion stages (préparé)
├── config/                         # Configuration Django
│   ├── settings/                   # Settings modulaires
│   ├── urls.py                     # URLs principales
│   └── wsgi.py                     # WSGI configuration
├── api/                            # Configuration API globale
├── utils/                          # Utilitaires partagés
└── requirements/                   # Dépendances par environnement
```

## 📊 Modèles de données

### 🔐 Authentication & Users

```python
# Modèles principaux
class User(AbstractUser):
    """Utilisateur étendu avec rôles"""
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    school = models.ForeignKey(School)
    is_active = models.BooleanField(default=True)

class UserProfile(models.Model):
    """Profil utilisateur avec informations spécifiques"""
    user = models.OneToOneField(User)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    preferences = models.JSONField(default=dict)

# Rôles supportés
ROLE_CHOICES = [
    ('student', 'Élève'),
    ('parent', 'Parent'),
    ('teacher', 'Professeur'),
    ('admin', 'Administrateur'),
]
```

### 🏫 Schools (Multi-tenant)

```python
class School(models.Model):
    """Établissement scolaire - Tenant principal"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)  # Code RNE
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    subdomain = models.CharField(max_length=50, unique=True)
    schema_name = models.CharField(max_length=63, unique=True)
    
class AcademicYear(models.Model):
    """Année scolaire"""
    school = models.ForeignKey(School)
    name = models.CharField(max_length=20)  # "2023-2024"
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

class Class(models.Model):
    """Classe d'élèves"""
    school = models.ForeignKey(School)
    name = models.CharField(max_length=50)  # "6ème A"
    level = models.CharField(max_length=20)  # "6", "5", "4", "3"
    academic_year = models.ForeignKey(AcademicYear)
    main_teacher = models.ForeignKey(User, null=True)  # Professeur principal
```

### 📅 Timetable

```python
class Subject(models.Model):
    """Matière enseignée"""
    school = models.ForeignKey(School)
    name = models.CharField(max_length=100)  # "Mathématiques"
    code = models.CharField(max_length=10)   # "MATH"
    color = models.CharField(max_length=7, default="#3B82F6")

class Room(models.Model):
    """Salle de cours"""
    school = models.ForeignKey(School)
    name = models.CharField(max_length=50)   # "A101"
    capacity = models.IntegerField(default=30)
    equipment = models.JSONField(default=list)  # ["TBI", "Ordinateurs"]

class TimeSlot(models.Model):
    """Créneau horaire"""
    school = models.ForeignKey(School)
    day_of_week = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    period_name = models.CharField(max_length=20)  # "M1", "M2", "S1"

class Schedule(models.Model):
    """Cours planifié"""
    school = models.ForeignKey(School)
    class_group = models.ForeignKey(Class)
    subject = models.ForeignKey(Subject)
    teacher = models.ForeignKey(User)
    room = models.ForeignKey(Room)
    time_slot = models.ForeignKey(TimeSlot)
    academic_year = models.ForeignKey(AcademicYear)
```

### 📝 Grades & Evaluations

```python
class Evaluation(models.Model):
    """Évaluation/Devoir"""
    school = models.ForeignKey(School)
    name = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject)
    class_group = models.ForeignKey(Class)
    teacher = models.ForeignKey(User)
    date = models.DateField()
    max_value = models.FloatField(default=20.0)
    coefficient = models.FloatField(default=1.0)
    evaluation_type = models.CharField(max_length=20, choices=EVAL_TYPE_CHOICES)
    description = models.TextField(blank=True)

class Grade(models.Model):
    """Note d'un élève"""
    school = models.ForeignKey(School)
    student = models.ForeignKey(User)
    evaluation = models.ForeignKey(Evaluation)
    value = models.FloatField()  # Note sur max_value
    comment = models.TextField(blank=True)
    created_by = models.ForeignKey(User, related_name='grades_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class BulletinAppreciation(models.Model):
    """Appréciation de bulletin"""
    school = models.ForeignKey(School)
    student = models.ForeignKey(User)
    subject = models.ForeignKey(Subject)
    period = models.CharField(max_length=10)  # "T1", "T2", "T3"
    academic_year = models.ForeignKey(AcademicYear)
    content = models.TextField()
    teacher = models.ForeignKey(User, related_name='appreciations_written')
    is_ai_generated = models.BooleanField(default=False)
    ai_confidence = models.FloatField(null=True)
```

### 👥 Attendance & Life

```python
class AttendanceSession(models.Model):
    """Session d'appel"""
    school = models.ForeignKey(School)
    class_group = models.ForeignKey(Class)
    subject = models.ForeignKey(Subject)
    teacher = models.ForeignKey(User)
    date = models.DateField()
    time_slot = models.ForeignKey(TimeSlot)
    created_at = models.DateTimeField(auto_now_add=True)

class Attendance(models.Model):
    """Présence/Absence élève"""
    session = models.ForeignKey(AttendanceSession)
    student = models.ForeignKey(User)
    status = models.CharField(max_length=20, choices=ATTENDANCE_CHOICES)
    arrival_time = models.TimeField(null=True)
    comment = models.TextField(blank=True)
    justified = models.BooleanField(default=False)
    justification = models.TextField(blank=True)

class StudentBehavior(models.Model):
    """Observation comportementale"""
    school = models.ForeignKey(School)
    student = models.ForeignKey(User)
    teacher = models.ForeignKey(User, related_name='behavior_observations')
    date = models.DateField()
    behavior_type = models.CharField(max_length=20, choices=BEHAVIOR_CHOICES)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)

class Sanction(models.Model):
    """Sanction disciplinaire"""
    school = models.ForeignKey(School)
    student = models.ForeignKey(User)
    issued_by = models.ForeignKey(User, related_name='sanctions_issued')
    sanction_type = models.CharField(max_length=20, choices=SANCTION_CHOICES)
    description = models.TextField()
    date_issued = models.DateField()
    date_executed = models.DateField(null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
```

### 🤖 AI Modules

```python
class RiskProfile(models.Model):
    """Profil de risque d'un élève"""
    school = models.ForeignKey(School)
    student = models.ForeignKey(User)
    risk_score = models.FloatField()  # Score de 0 à 100
    confidence_level = models.FloatField()  # Confiance du modèle
    risk_factors = models.JSONField()  # Facteurs détectés
    last_analysis = models.DateTimeField()
    model_version = models.CharField(max_length=20)

class Prediction(models.Model):
    """Prédiction IA"""
    school = models.ForeignKey(School)
    student = models.ForeignKey(User)
    prediction_type = models.CharField(max_length=50)  # "dropout", "failure"
    probability = models.FloatField()  # Probabilité 0-100
    confidence = models.FloatField()   # Confiance 0-100
    key_factors = models.JSONField()   # Facteurs clés
    model_version = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

class InterventionPlan(models.Model):
    """Plan d'intervention"""
    school = models.ForeignKey(School)
    student = models.ForeignKey(User)
    created_by = models.ForeignKey(User, related_name='interventions_created')
    title = models.CharField(max_length=200)
    objectives = models.TextField()
    intervention_type = models.CharField(max_length=20, choices=INTERVENTION_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(null=True)
    progress = models.IntegerField(default=0)  # Pourcentage 0-100

class AppreciationGeneration(models.Model):
    """Génération d'appréciation IA"""
    school = models.ForeignKey(School)
    student = models.ForeignKey(User)
    subject = models.ForeignKey(Subject, null=True)
    period = models.CharField(max_length=10)
    content = models.TextField()
    generation_type = models.CharField(max_length=20, choices=APPRECIATION_TYPES)
    ai_confidence = models.FloatField()
    status = models.CharField(max_length=20, choices=GENERATION_STATUS)
    validated_by = models.ForeignKey(User, null=True, related_name='appreciations_validated')
    created_at = models.DateTimeField(auto_now_add=True)
```

## 🔗 API Endpoints

### Authentication
```
POST   /api/auth/login/           # Connexion utilisateur
POST   /api/auth/refresh/         # Refresh token
POST   /api/auth/logout/          # Déconnexion
GET    /api/auth/me/              # Profil utilisateur actuel
```

### Grades
```
GET    /api/grades/               # Liste des notes
POST   /api/grades/               # Créer une note
GET    /api/grades/{id}/          # Détail d'une note
PUT    /api/grades/{id}/          # Modifier une note
DELETE /api/grades/{id}/          # Supprimer une note

GET    /api/evaluations/          # Liste des évaluations
POST   /api/evaluations/          # Créer une évaluation
GET    /api/bulletins/            # Bulletins générés
POST   /api/bulletins/generate/   # Générer bulletins
```

### Timetable
```
GET    /api/timetable/            # Emploi du temps
GET    /api/timetable/class/{id}/ # EDT d'une classe
GET    /api/timetable/teacher/{id}/ # EDT d'un professeur
GET    /api/subjects/             # Liste des matières
GET    /api/rooms/                # Liste des salles
```

### Attendance
```
GET    /api/attendance/           # Sessions d'appel
POST   /api/attendance/           # Créer session d'appel
PUT    /api/attendance/{id}/      # Modifier présences
GET    /api/absences/             # Liste des absences
GET    /api/behavior/             # Observations comportementales
GET    /api/sanctions/            # Sanctions disciplinaires
```

### AI Modules
```
GET    /api/ai/risk-profiles/     # Profils de risque
POST   /api/ai/analyze-dropout/   # Analyser décrochage
GET    /api/ai/predictions/       # Prédictions IA
POST   /api/ai/generate-appreciation/ # Générer appréciation
GET    /api/ai/interventions/     # Plans d'intervention
POST   /api/ai/reports/generate/  # Générer rapport IA
```

## 🔒 Sécurité et permissions

### Système de rôles
```python
# Permissions par rôle
ROLE_PERMISSIONS = {
    'student': ['read_own_data', 'read_timetable', 'read_grades'],
    'parent': ['read_children_data', 'read_timetable', 'read_grades'],
    'teacher': ['teacher_access', 'manage_grades', 'manage_attendance'],
    'admin': ['admin_access', 'manage_school', 'manage_users'],
}

# Décorateurs de permission
@permission_required('teacher_access')
def teacher_only_view(request):
    pass

@method_decorator(permission_required('admin_access'), name='dispatch')
class AdminOnlyView(APIView):
    pass
```

### Multi-tenant sécurisé
```python
class SchoolFilterMixin:
    """Mixin pour filtrer par établissement"""
    def get_queryset(self):
        return super().get_queryset().filter(
            school=self.request.user.school
        )

class GradeViewSet(SchoolFilterMixin, ModelViewSet):
    """Les notes sont automatiquement filtrées par école"""
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated, TeacherPermission]
```

## 🧪 Tests

```bash
# Tests unitaires
python manage.py test

# Tests avec coverage
coverage run manage.py test
coverage report
coverage html

# Tests d'intégration API
python manage.py test tests.integration

# Tests des modules IA
python manage.py test apps.ai_modules.tests
```

## 📊 Performance

### Optimisations implémentées
- **ORM optimisé** : `select_related()`, `prefetch_related()`
- **Cache Redis** : Mise en cache des données fréquentes
- **Pagination** : Limitation automatique des réponses
- **Indexes** : Indexes sur les champs fréquemment utilisés

### Monitoring
```python
# Middleware de performance
MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',
    'apps.monitoring.middleware.PerformanceMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
]

# Logging configuré
LOGGING = {
    'handlers': {
        'file': {
            'filename': 'logs/peproscolaire.log',
            'level': 'INFO',
        }
    }
}
```

## 🔧 Configuration

### Variables d'environnement
```bash
# .env
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/peproscolaire
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=amqp://guest@localhost//

# IA Services
OPENAI_API_KEY=your-openai-key
HUGGINGFACE_API_TOKEN=your-hf-token

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

### Settings modulaires
```python
# config/settings/base.py     - Settings communs
# config/settings/dev.py      - Développement
# config/settings/staging.py  - Pre-production  
# config/settings/prod.py     - Production
```

## 🚀 Déploiement

### Docker
```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "config.wsgi:application"]
```

### Production
```bash
# Collecte des fichiers statiques
python manage.py collectstatic --noinput

# Migrations
python manage.py migrate

# Création d'un superutilisateur
python manage.py create_superuser_if_not_exists

# Lancement avec Gunicorn
gunicorn config.wsgi:application --workers 4 --bind 0.0.0.0:8000
```

---

**Backend PeproScolaire** - API robuste pour la gestion scolaire moderne 🎓⚡