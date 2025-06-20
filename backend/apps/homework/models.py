"""
Modèles pour la gestion du cahier de textes et des devoirs
"""
from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import datetime, timedelta
from apps.core.models import BaseModel
from apps.authentication.models import User
from apps.schools.models import Class, AcademicYear
from apps.timetable.models import Subject, Schedule


class LessonContent(BaseModel):
    """
    Contenu d'un cours (cahier de textes)
    """
    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        related_name='lesson_contents'
    )
    date = models.DateField(verbose_name=_("Date du cours"))
    
    # Contenu du cours
    title = models.CharField(
        max_length=200,
        verbose_name=_("Titre de la séance")
    )
    objectives = models.TextField(
        blank=True,
        verbose_name=_("Objectifs pédagogiques")
    )
    content = models.TextField(
        verbose_name=_("Contenu du cours"),
        help_text=_("Ce qui a été fait pendant la séance")
    )
    
    # Notions et compétences
    key_concepts = models.TextField(
        blank=True,
        verbose_name=_("Notions clés"),
        help_text=_("Mots-clés, formules, définitions importantes")
    )
    skills_worked = models.TextField(
        blank=True,
        verbose_name=_("Compétences travaillées")
    )
    
    # Métadonnées
    duration_minutes = models.PositiveIntegerField(
        default=55,
        verbose_name=_("Durée (minutes)")
    )
    is_catch_up = models.BooleanField(
        default=False,
        verbose_name=_("Cours de rattrapage")
    )
    
    # Progression
    chapter = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Chapitre")
    )
    sequence_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Numéro de séquence")
    )
    
    # Validation
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_lessons'
    )
    validated = models.BooleanField(
        default=False,
        verbose_name=_("Validé par l'administration")
    )
    validated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_lessons'
    )
    validated_at = models.DateTimeField(
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'lesson_contents'
        verbose_name = _("Contenu de cours")
        verbose_name_plural = _("Contenus de cours")
        unique_together = ['schedule', 'date']
        ordering = ['-date', 'schedule__time_slot__start_time']
        indexes = [
            models.Index(fields=['date', 'schedule']),
            models.Index(fields=['chapter', 'sequence_number']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.date}"
    
    def clean(self):
        # Vérifier que la date correspond au jour de la semaine du schedule
        if self.date and self.schedule:
            expected_day = self.schedule.time_slot.day
            actual_day = self.date.weekday()
            
            if expected_day != actual_day:
                days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
                raise ValidationError({
                    'date': _(f"La date doit être un {days[expected_day]}")
                })
    
    @property
    def has_homework(self):
        """Vérifie s'il y a des devoirs associés"""
        return self.homework_assignments.exists()


class HomeworkType(BaseModel):
    """
    Type de devoir
    """
    name = models.CharField(max_length=100, verbose_name=_("Nom"))
    short_name = models.CharField(max_length=20, verbose_name=_("Abréviation"))
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Icône"),
        help_text=_("Nom de l'icône Material Design")
    )
    default_duration_days = models.PositiveIntegerField(
        default=7,
        verbose_name=_("Délai par défaut (jours)")
    )
    color = models.CharField(
        max_length=7,
        default='#3498db',
        verbose_name=_("Couleur")
    )
    
    class Meta:
        db_table = 'homework_types'
        verbose_name = _("Type de devoir")
        verbose_name_plural = _("Types de devoirs")
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Homework(BaseModel):
    """
    Devoir à faire
    """
    DIFFICULTY_CHOICES = [
        ('easy', 'Facile'),
        ('medium', 'Moyen'),
        ('hard', 'Difficile'),
    ]
    
    lesson_content = models.ForeignKey(
        LessonContent,
        on_delete=models.CASCADE,
        related_name='homework_assignments',
        null=True,
        blank=True
    )
    
    # Peut aussi être créé indépendamment
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='homework_assignments'
    )
    class_group = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='homework_assignments'
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_homework',
        limit_choices_to={'user_type': 'teacher'}
    )
    
    # Description du devoir
    homework_type = models.ForeignKey(
        HomeworkType,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assignments'
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_("Titre")
    )
    description = models.TextField(
        verbose_name=_("Description détaillée")
    )
    instructions = models.TextField(
        blank=True,
        verbose_name=_("Instructions"),
        help_text=_("Consignes spécifiques pour réaliser le devoir")
    )
    
    # Dates
    assigned_date = models.DateField(
        default=timezone.now,
        verbose_name=_("Date de distribution")
    )
    due_date = models.DateField(verbose_name=_("Date de rendu"))
    
    # Paramètres
    estimated_duration_minutes = models.PositiveIntegerField(
        default=30,
        verbose_name=_("Durée estimée (minutes)")
    )
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='medium',
        verbose_name=_("Difficulté")
    )
    is_graded = models.BooleanField(
        default=False,
        verbose_name=_("Noté")
    )
    allow_late_submission = models.BooleanField(
        default=True,
        verbose_name=_("Rendu en retard autorisé")
    )
    
    # Options de rendu
    submission_type = models.CharField(
        max_length=20,
        choices=[
            ('paper', 'Papier'),
            ('digital', 'Numérique'),
            ('both', 'Les deux'),
            ('none', 'Pas de rendu'),
        ],
        default='paper',
        verbose_name=_("Type de rendu")
    )
    max_file_size_mb = models.PositiveIntegerField(
        default=10,
        verbose_name=_("Taille max fichier (MB)")
    )
    allowed_file_types = models.CharField(
        max_length=200,
        default='pdf,doc,docx,jpg,png',
        verbose_name=_("Types de fichiers autorisés"),
        help_text=_("Extensions séparées par des virgules")
    )
    
    # Suggestions IA
    is_ai_suggested = models.BooleanField(
        default=False,
        verbose_name=_("Suggéré par l'IA")
    )
    ai_suggestion_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Données de suggestion IA")
    )
    
    # Statistiques
    view_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Nombre de vues")
    )
    
    class Meta:
        db_table = 'homework'
        verbose_name = _("Devoir")
        verbose_name_plural = _("Devoirs")
        ordering = ['due_date', 'subject']
        indexes = [
            models.Index(fields=['due_date', 'class_group']),
            models.Index(fields=['teacher', 'assigned_date']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.due_date}"
    
    def clean(self):
        if self.due_date <= self.assigned_date:
            raise ValidationError({
                'due_date': _("La date de rendu doit être après la date de distribution")
            })
    
    @property
    def is_overdue(self):
        """Vérifie si le devoir est en retard"""
        return timezone.now().date() > self.due_date
    
    @property
    def days_remaining(self):
        """Nombre de jours restants"""
        delta = self.due_date - timezone.now().date()
        return max(0, delta.days)
    
    @property
    def submission_rate(self):
        """Taux de rendu"""
        total_students = self.class_group.students.filter(is_active=True).count()
        if total_students == 0:
            return 0
        submissions = self.submissions.count()
        return (submissions / total_students) * 100


class HomeworkResource(BaseModel):
    """
    Ressource associée à un devoir ou une leçon
    """
    RESOURCE_TYPE_CHOICES = [
        ('document', 'Document'),
        ('link', 'Lien'),
        ('video', 'Vidéo'),
        ('exercise', 'Exercice'),
        ('correction', 'Correction'),
    ]
    
    # Peut être lié à un devoir ou une leçon
    homework = models.ForeignKey(
        Homework,
        on_delete=models.CASCADE,
        related_name='resources',
        null=True,
        blank=True
    )
    lesson_content = models.ForeignKey(
        LessonContent,
        on_delete=models.CASCADE,
        related_name='resources',
        null=True,
        blank=True
    )
    
    # Informations sur la ressource
    resource_type = models.CharField(
        max_length=20,
        choices=RESOURCE_TYPE_CHOICES,
        verbose_name=_("Type")
    )
    title = models.CharField(max_length=200, verbose_name=_("Titre"))
    description = models.TextField(
        blank=True,
        verbose_name=_("Description")
    )
    
    # Contenu
    file = models.FileField(
        upload_to='homework/resources/%Y/%m/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'doc', 'docx', 'ppt', 'pptx',
                                  'xls', 'xlsx', 'jpg', 'png', 'mp4', 'avi']
            )
        ],
        verbose_name=_("Fichier")
    )
    url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name=_("Lien")
    )
    
    # Métadonnées
    is_mandatory = models.BooleanField(
        default=False,
        verbose_name=_("Obligatoire")
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Ordre d'affichage")
    )
    download_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Nombre de téléchargements")
    )
    
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_resources'
    )
    
    class Meta:
        db_table = 'homework_resources'
        verbose_name = _("Ressource")
        verbose_name_plural = _("Ressources")
        ordering = ['order', 'title']
    
    def __str__(self):
        return self.title
    
    def clean(self):
        # Vérifier qu'au moins un parent est défini
        if not self.homework and not self.lesson_content:
            raise ValidationError(
                _("La ressource doit être liée à un devoir ou une leçon")
            )
        
        # Vérifier qu'il y a soit un fichier soit une URL
        if not self.file and not self.url:
            raise ValidationError(
                _("Un fichier ou une URL doit être fourni")
            )
    
    @property
    def size_mb(self):
        """Taille du fichier en MB"""
        if self.file:
            return round(self.file.size / (1024 * 1024), 2)
        return None


class StudentWork(BaseModel):
    """
    Travail rendu par un élève
    """
    SUBMISSION_STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('submitted', 'Rendu'),
        ('late', 'En retard'),
        ('returned', 'Corrigé'),
    ]
    
    homework = models.ForeignKey(
        Homework,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='homework_submissions',
        limit_choices_to={'user_type': 'student'}
    )
    
    # Statut
    status = models.CharField(
        max_length=20,
        choices=SUBMISSION_STATUS_CHOICES,
        default='draft',
        verbose_name=_("Statut")
    )
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Date de rendu")
    )
    
    # Contenu du travail
    content = models.TextField(
        blank=True,
        verbose_name=_("Contenu texte")
    )
    file = models.FileField(
        upload_to='homework/submissions/%Y/%m/',
        null=True,
        blank=True,
        verbose_name=_("Fichier")
    )
    
    # Commentaires
    student_comment = models.TextField(
        blank=True,
        verbose_name=_("Commentaire de l'élève")
    )
    
    # Correction
    grade = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Note")
    )
    teacher_comment = models.TextField(
        blank=True,
        verbose_name=_("Commentaire du professeur")
    )
    corrected_file = models.FileField(
        upload_to='homework/corrections/%Y/%m/',
        null=True,
        blank=True,
        verbose_name=_("Fichier corrigé")
    )
    corrected_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Date de correction")
    )
    corrected_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='corrected_homework'
    )
    
    # Métadonnées
    time_spent_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Temps passé (minutes)")
    )
    
    class Meta:
        db_table = 'student_works'
        verbose_name = _("Travail d'élève")
        verbose_name_plural = _("Travaux d'élèves")
        unique_together = ['homework', 'student']
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.homework.title}"
    
    def clean(self):
        # Validation de la taille du fichier
        if self.file and self.homework.max_file_size_mb:
            if self.file.size > self.homework.max_file_size_mb * 1024 * 1024:
                raise ValidationError({
                    'file': _(f"Le fichier ne doit pas dépasser {self.homework.max_file_size_mb} MB")
                })
        
        # Validation du type de fichier
        if self.file and self.homework.allowed_file_types:
            allowed = self.homework.allowed_file_types.split(',')
            ext = self.file.name.split('.')[-1].lower()
            if ext not in allowed:
                raise ValidationError({
                    'file': _(f"Type de fichier non autorisé. Types acceptés: {self.homework.allowed_file_types}")
                })
    
    def submit(self):
        """Soumettre le travail"""
        self.submitted_at = timezone.now()
        if timezone.now().date() > self.homework.due_date:
            self.status = 'late'
        else:
            self.status = 'submitted'
        self.save()


class HomeworkTemplate(BaseModel):
    """
    Modèle de devoir réutilisable
    """
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='homework_templates'
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='homework_templates',
        limit_choices_to={'user_type': 'teacher'}
    )
    
    # Informations du modèle
    name = models.CharField(
        max_length=200,
        verbose_name=_("Nom du modèle")
    )
    chapter = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Chapitre")
    )
    level = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Niveau"),
        help_text=_("Ex: 6ème, 2nde...")
    )
    
    # Contenu du modèle
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructions = models.TextField(blank=True)
    homework_type = models.ForeignKey(
        HomeworkType,
        on_delete=models.SET_NULL,
        null=True
    )
    estimated_duration_minutes = models.PositiveIntegerField(default=30)
    difficulty = models.CharField(
        max_length=10,
        choices=Homework.DIFFICULTY_CHOICES,
        default='medium'
    )
    
    # Métadonnées
    tags = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("Tags"),
        help_text=_("Mots-clés séparés par des virgules")
    )
    use_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Nombre d'utilisations")
    )
    is_shared = models.BooleanField(
        default=False,
        verbose_name=_("Partagé avec d'autres professeurs")
    )
    
    class Meta:
        db_table = 'homework_templates'
        verbose_name = _("Modèle de devoir")
        verbose_name_plural = _("Modèles de devoirs")
        ordering = ['-use_count', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.subject.name})"
    
    def create_homework(self, class_group, due_date, **kwargs):
        """Créer un devoir à partir du modèle"""
        homework_data = {
            'subject': self.subject,
            'class_group': class_group,
            'teacher': self.teacher,
            'title': self.title,
            'description': self.description,
            'instructions': self.instructions,
            'homework_type': self.homework_type,
            'estimated_duration_minutes': self.estimated_duration_minutes,
            'difficulty': self.difficulty,
            'due_date': due_date,
        }
        homework_data.update(kwargs)
        
        homework = Homework.objects.create(**homework_data)
        
        # Incrémenter le compteur d'utilisation
        self.use_count += 1
        self.save()
        
        return homework


class WorkloadAnalysis(BaseModel):
    """
    Analyse de la charge de travail des élèves
    """
    class_group = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='workload_analyses'
    )
    date = models.DateField(verbose_name=_("Date d'analyse"))
    
    # Métriques
    total_homework_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Nombre total de devoirs")
    )
    total_estimated_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Temps total estimé (minutes)")
    )
    
    # Par matière
    homework_by_subject = models.JSONField(
        default=dict,
        verbose_name=_("Devoirs par matière")
    )
    
    # Alertes
    is_overloaded = models.BooleanField(
        default=False,
        verbose_name=_("Surcharge détectée")
    )
    overload_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Faible'),
            ('medium', 'Moyen'),
            ('high', 'Élevé'),
            ('critical', 'Critique'),
        ],
        blank=True,
        verbose_name=_("Niveau de surcharge")
    )
    
    # Recommandations
    recommendations = models.TextField(
        blank=True,
        verbose_name=_("Recommandations")
    )
    
    class Meta:
        db_table = 'workload_analyses'
        verbose_name = _("Analyse de charge de travail")
        verbose_name_plural = _("Analyses de charge de travail")
        unique_together = ['class_group', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.class_group} - {self.date}"
    
    def analyze(self):
        """Analyser la charge de travail"""
        # Récupérer tous les devoirs dus dans les 7 prochains jours
        start_date = self.date
        end_date = self.date + timedelta(days=7)
        
        homework_list = Homework.objects.filter(
            class_group=self.class_group,
            due_date__range=[start_date, end_date]
        ).select_related('subject')
        
        # Calculer les métriques
        self.total_homework_count = homework_list.count()
        self.total_estimated_minutes = sum(
            hw.estimated_duration_minutes for hw in homework_list
        )
        
        # Par matière
        by_subject = {}
        for hw in homework_list:
            subject_name = hw.subject.name
            if subject_name not in by_subject:
                by_subject[subject_name] = {
                    'count': 0,
                    'minutes': 0
                }
            by_subject[subject_name]['count'] += 1
            by_subject[subject_name]['minutes'] += hw.estimated_duration_minutes
        
        self.homework_by_subject = by_subject
        
        # Détection de surcharge
        # Seuils: plus de 2h par jour en moyenne
        daily_average = self.total_estimated_minutes / 7
        if daily_average > 180:  # 3h
            self.is_overloaded = True
            self.overload_level = 'critical'
        elif daily_average > 150:  # 2h30
            self.is_overloaded = True
            self.overload_level = 'high'
        elif daily_average > 120:  # 2h
            self.is_overloaded = True
            self.overload_level = 'medium'
        elif daily_average > 90:  # 1h30
            self.is_overloaded = True
            self.overload_level = 'low'
        
        # Recommandations
        if self.is_overloaded:
            self.recommendations = self._generate_recommendations()
        
        self.save()
    
    def _generate_recommendations(self):
        """Générer des recommandations"""
        recs = []
        
        if self.overload_level in ['critical', 'high']:
            recs.append("⚠️ Charge de travail excessive détectée")
            recs.append("Recommandation: Reporter certains devoirs")
        
        # Identifier les matières surchargées
        for subject, data in self.homework_by_subject.items():
            if data['minutes'] > 60:
                recs.append(f"- {subject}: {data['count']} devoirs ({data['minutes']} min)")
        
        return "\n".join(recs)