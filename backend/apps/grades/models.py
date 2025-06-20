"""
Modèles pour la gestion des notes et évaluations
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from decimal import Decimal
from apps.core.models import BaseModel
from apps.authentication.models import User
from apps.schools.models import Class, AcademicYear
from apps.timetable.models import Subject


class EvaluationType(BaseModel):
    """
    Type d'évaluation (DS, DM, Interrogation, etc.)
    """
    name = models.CharField(max_length=100, verbose_name=_("Nom"))
    short_name = models.CharField(max_length=20, verbose_name=_("Abréviation"))
    default_coefficient = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=1.0,
        validators=[MinValueValidator(0.1)],
        verbose_name=_("Coefficient par défaut")
    )
    color = models.CharField(
        max_length=7,
        default='#3498db',
        verbose_name=_("Couleur")
    )
    is_graded = models.BooleanField(
        default=True,
        verbose_name=_("Noté"),
        help_text=_("Si non coché, évaluation par compétences uniquement")
    )
    
    class Meta:
        db_table = 'evaluation_types'
        verbose_name = _("Type d'évaluation")
        verbose_name_plural = _("Types d'évaluation")
        ordering = ['name']
    
    def __str__(self):
        return self.name


class GradingPeriod(BaseModel):
    """
    Période de notation (Trimestre, Semestre)
    """
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='grading_periods'
    )
    name = models.CharField(max_length=50, verbose_name=_("Nom"))
    number = models.PositiveIntegerField(
        verbose_name=_("Numéro"),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    start_date = models.DateField(verbose_name=_("Date de début"))
    end_date = models.DateField(verbose_name=_("Date de fin"))
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Période active")
    )
    
    # Configuration des conseils de classe
    council_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Date du conseil de classe")
    )
    grades_locked = models.BooleanField(
        default=False,
        verbose_name=_("Notes verrouillées")
    )
    bulletins_published = models.BooleanField(
        default=False,
        verbose_name=_("Bulletins publiés")
    )
    
    class Meta:
        db_table = 'grading_periods'
        verbose_name = _("Période de notation")
        verbose_name_plural = _("Périodes de notation")
        unique_together = ['academic_year', 'number']
        ordering = ['academic_year', 'number']
    
    def __str__(self):
        return f"{self.name} - {self.academic_year}"
    
    def clean(self):
        if self.end_date <= self.start_date:
            raise ValidationError({
                'end_date': _("La date de fin doit être après la date de début")
            })


class Evaluation(BaseModel):
    """
    Évaluation (contrôle, devoir, etc.)
    """
    title = models.CharField(max_length=200, verbose_name=_("Titre"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    evaluation_type = models.ForeignKey(
        EvaluationType,
        on_delete=models.PROTECT,
        related_name='evaluations'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='evaluations'
    )
    class_group = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='evaluations'
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_evaluations',
        limit_choices_to={'user_type': 'teacher'}
    )
    grading_period = models.ForeignKey(
        GradingPeriod,
        on_delete=models.CASCADE,
        related_name='evaluations'
    )
    
    # Configuration de la notation
    date = models.DateField(verbose_name=_("Date de l'évaluation"))
    max_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=20.0,
        validators=[MinValueValidator(1)],
        verbose_name=_("Note maximale")
    )
    coefficient = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=1.0,
        validators=[MinValueValidator(0.1)],
        verbose_name=_("Coefficient")
    )
    
    # Options
    is_optional = models.BooleanField(
        default=False,
        verbose_name=_("Évaluation optionnelle")
    )
    counts_in_average = models.BooleanField(
        default=True,
        verbose_name=_("Compte dans la moyenne")
    )
    allow_absent_makeup = models.BooleanField(
        default=True,
        verbose_name=_("Rattrapage autorisé")
    )
    
    # Statut
    is_graded = models.BooleanField(
        default=False,
        verbose_name=_("Corrigé")
    )
    grades_published = models.BooleanField(
        default=False,
        verbose_name=_("Notes publiées")
    )
    
    # Documents
    subject_file = models.FileField(
        upload_to='evaluations/subjects/%Y/%m/',
        null=True,
        blank=True,
        verbose_name=_("Sujet")
    )
    correction_file = models.FileField(
        upload_to='evaluations/corrections/%Y/%m/',
        null=True,
        blank=True,
        verbose_name=_("Correction")
    )
    
    class Meta:
        db_table = 'evaluations'
        verbose_name = _("Évaluation")
        verbose_name_plural = _("Évaluations")
        ordering = ['-date', 'subject']
        indexes = [
            models.Index(fields=['class_group', 'grading_period']),
            models.Index(fields=['teacher', 'date']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.class_group} - {self.date}"
    
    def clean(self):
        # Vérifier que la date est dans la période de notation
        if hasattr(self, 'grading_period') and self.date:
            if not (self.grading_period.start_date <= self.date <= self.grading_period.end_date):
                raise ValidationError({
                    'date': _("La date doit être dans la période de notation")
                })
    
    @property
    def average_score(self):
        """Calculer la moyenne de la classe"""
        grades = self.grades.filter(is_absent=False).values_list('score', flat=True)
        if grades:
            return sum(grades) / len(grades)
        return None
    
    @property
    def graded_count(self):
        """Nombre d'élèves notés"""
        return self.grades.filter(score__isnull=False).count()


class Grade(BaseModel):
    """
    Note d'un élève pour une évaluation
    """
    evaluation = models.ForeignKey(
        Evaluation,
        on_delete=models.CASCADE,
        related_name='grades'
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='grades',
        limit_choices_to={'user_type': 'student'}
    )
    
    # Note
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("Note")
    )
    
    # Statut
    is_absent = models.BooleanField(
        default=False,
        verbose_name=_("Absent")
    )
    is_excused = models.BooleanField(
        default=False,
        verbose_name=_("Absence justifiée")
    )
    is_cheating = models.BooleanField(
        default=False,
        verbose_name=_("Tricherie")
    )
    
    # Commentaires
    comment = models.TextField(
        blank=True,
        verbose_name=_("Commentaire")
    )
    
    # Métadonnées
    graded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='graded_evaluations',
        verbose_name=_("Noté par")
    )
    graded_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Noté le")
    )
    modified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='modified_grades'
    )
    modified_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'grades'
        verbose_name = _("Note")
        verbose_name_plural = _("Notes")
        unique_together = ['evaluation', 'student']
        ordering = ['student__last_name', 'student__first_name']
    
    def __str__(self):
        if self.score is not None:
            return f"{self.student.get_full_name()} - {self.score}/{self.evaluation.max_score}"
        return f"{self.student.get_full_name()} - Non noté"
    
    def clean(self):
        # Validation de la note
        if self.score is not None:
            if self.score > self.evaluation.max_score:
                raise ValidationError({
                    'score': _(f"La note ne peut pas dépasser {self.evaluation.max_score}")
                })
            
            if self.is_absent:
                raise ValidationError({
                    'score': _("Un élève absent ne peut pas avoir de note")
                })
        
        # Si absent, pas de note
        if self.is_absent and self.score is not None:
            self.score = None
        
        # Si tricherie, note = 0
        if self.is_cheating:
            self.score = Decimal('0.00')
    
    @property
    def normalized_score(self):
        """Note ramenée sur 20"""
        if self.score is not None and self.evaluation.max_score != 20:
            return (self.score * 20) / self.evaluation.max_score
        return self.score


class SubjectAverage(BaseModel):
    """
    Moyenne d'un élève dans une matière pour une période
    """
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subject_averages',
        limit_choices_to={'user_type': 'student'}
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='student_averages'
    )
    grading_period = models.ForeignKey(
        GradingPeriod,
        on_delete=models.CASCADE,
        related_name='subject_averages'
    )
    class_group = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='subject_averages'
    )
    
    # Moyennes
    average = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Moyenne")
    )
    weighted_average = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Moyenne pondérée")
    )
    
    # Rang
    rank = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Rang")
    )
    class_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Effectif")
    )
    
    # Statistiques de la classe
    class_average = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Moyenne de classe")
    )
    min_average = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Note minimale")
    )
    max_average = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Note maximale")
    )
    
    # Appréciation
    appreciation = models.TextField(
        blank=True,
        verbose_name=_("Appréciation")
    )
    
    class Meta:
        db_table = 'subject_averages'
        verbose_name = _("Moyenne par matière")
        verbose_name_plural = _("Moyennes par matière")
        unique_together = ['student', 'subject', 'grading_period']
        ordering = ['subject', '-average']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.subject} - {self.average or 'N/A'}"
    
    def calculate_average(self):
        """Calculer la moyenne de l'élève dans cette matière"""
        grades = Grade.objects.filter(
            student=self.student,
            evaluation__subject=self.subject,
            evaluation__grading_period=self.grading_period,
            evaluation__counts_in_average=True,
            score__isnull=False,
            is_absent=False
        ).select_related('evaluation')
        
        if not grades:
            self.average = None
            self.weighted_average = None
            return
        
        # Calcul de la moyenne simple
        total_score = Decimal('0')
        total_max_score = Decimal('0')
        
        # Calcul de la moyenne pondérée
        weighted_sum = Decimal('0')
        total_coefficient = Decimal('0')
        
        for grade in grades:
            normalized = grade.normalized_score
            if normalized is not None:
                # Moyenne simple
                total_score += grade.score
                total_max_score += grade.evaluation.max_score
                
                # Moyenne pondérée
                weighted_sum += normalized * grade.evaluation.coefficient
                total_coefficient += grade.evaluation.coefficient
        
        # Calcul final
        if total_max_score > 0:
            self.average = (total_score * 20) / total_max_score
        
        if total_coefficient > 0:
            self.weighted_average = weighted_sum / total_coefficient
        
        self.save()
    
    def calculate_rank(self):
        """Calculer le rang de l'élève"""
        # Récupérer toutes les moyennes de la classe pour cette matière
        class_averages = SubjectAverage.objects.filter(
            subject=self.subject,
            grading_period=self.grading_period,
            class_group=self.class_group,
            average__isnull=False
        ).order_by('-average')
        
        # Calculer le rang
        rank = 1
        for avg in class_averages:
            if avg.id == self.id:
                self.rank = rank
                self.class_size = class_averages.count()
                break
            if avg.average != self.average:
                rank += 1
        
        # Calculer les statistiques de classe
        averages_list = list(class_averages.values_list('average', flat=True))
        if averages_list:
            self.class_average = sum(averages_list) / len(averages_list)
            self.min_average = min(averages_list)
            self.max_average = max(averages_list)
        
        self.save()


class GeneralAverage(BaseModel):
    """
    Moyenne générale d'un élève pour une période
    """
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='general_averages',
        limit_choices_to={'user_type': 'student'}
    )
    grading_period = models.ForeignKey(
        GradingPeriod,
        on_delete=models.CASCADE,
        related_name='general_averages'
    )
    class_group = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='general_averages'
    )
    
    # Moyennes
    average = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Moyenne générale")
    )
    weighted_average = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Moyenne générale pondérée")
    )
    
    # Rang
    rank = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Rang général")
    )
    class_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Effectif")
    )
    
    # Statistiques
    class_average = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Moyenne de classe")
    )
    
    # Décision du conseil
    council_decision = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('passed', 'Passage'),
            ('passed_conditional', 'Passage avec réserves'),
            ('repeat', 'Redoublement'),
            ('pending', 'En attente'),
        ],
        verbose_name=_("Décision du conseil")
    )
    
    # Mentions
    honor_roll = models.CharField(
        max_length=30,
        blank=True,
        choices=[
            ('felicitations', 'Félicitations'),
            ('compliments', 'Compliments'),
            ('encouragements', 'Encouragements'),
            ('', 'Aucune'),
        ],
        verbose_name=_("Mention")
    )
    
    # Appréciation générale
    general_appreciation = models.TextField(
        blank=True,
        verbose_name=_("Appréciation générale")
    )
    
    # Validation
    validated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_averages',
        verbose_name=_("Validé par")
    )
    validated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Validé le")
    )
    
    class Meta:
        db_table = 'general_averages'
        verbose_name = _("Moyenne générale")
        verbose_name_plural = _("Moyennes générales")
        unique_together = ['student', 'grading_period']
        ordering = ['-average']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.grading_period} - {self.average or 'N/A'}"
    
    def calculate_average(self):
        """Calculer la moyenne générale"""
        subject_averages = SubjectAverage.objects.filter(
            student=self.student,
            grading_period=self.grading_period,
            average__isnull=False
        ).select_related('subject')
        
        if not subject_averages:
            self.average = None
            self.weighted_average = None
            return
        
        # Moyenne simple
        total_average = Decimal('0')
        count = 0
        
        # Moyenne pondérée
        weighted_sum = Decimal('0')
        total_coefficient = Decimal('0')
        
        for subj_avg in subject_averages:
            if subj_avg.average:
                # Moyenne simple
                total_average += subj_avg.average
                count += 1
                
                # Moyenne pondérée
                coefficient = subj_avg.subject.coefficient
                weighted_sum += subj_avg.average * coefficient
                total_coefficient += coefficient
        
        # Calcul final
        if count > 0:
            self.average = total_average / count
        
        if total_coefficient > 0:
            self.weighted_average = weighted_sum / total_coefficient
        
        # Déterminer la mention automatiquement
        if self.weighted_average:
            if self.weighted_average >= 16:
                self.honor_roll = 'felicitations'
            elif self.weighted_average >= 14:
                self.honor_roll = 'compliments'
            elif self.weighted_average >= 12:
                self.honor_roll = 'encouragements'
            else:
                self.honor_roll = ''
        
        self.save()
    
    def calculate_rank(self):
        """Calculer le rang général"""
        # Récupérer toutes les moyennes de la classe
        class_averages = GeneralAverage.objects.filter(
            grading_period=self.grading_period,
            class_group=self.class_group,
            weighted_average__isnull=False
        ).order_by('-weighted_average')
        
        # Calculer le rang
        rank = 1
        for avg in class_averages:
            if avg.id == self.id:
                self.rank = rank
                self.class_size = class_averages.count()
                break
            if avg.weighted_average != self.weighted_average:
                rank += 1
        
        # Moyenne de classe
        averages_list = list(class_averages.values_list('weighted_average', flat=True))
        if averages_list:
            self.class_average = sum(averages_list) / len(averages_list)
        
        self.save()


class Competence(BaseModel):
    """
    Compétence évaluable
    """
    name = models.CharField(max_length=200, verbose_name=_("Nom"))
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("Code")
    )
    description = models.TextField(blank=True, verbose_name=_("Description"))
    domain = models.CharField(
        max_length=100,
        verbose_name=_("Domaine"),
        choices=[
            ('languages', 'Langages'),
            ('methods', 'Méthodes et outils'),
            ('citizenship', 'Formation de la personne et du citoyen'),
            ('systems', 'Systèmes naturels et techniques'),
            ('representations', 'Représentations du monde'),
        ]
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='competences',
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'competences'
        verbose_name = _("Compétence")
        verbose_name_plural = _("Compétences")
        ordering = ['domain', 'name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class CompetenceEvaluation(BaseModel):
    """
    Évaluation d'une compétence pour un élève
    """
    MASTERY_LEVELS = [
        ('na', 'Non acquis'),
        ('ec', 'En cours d\'acquisition'),
        ('a', 'Acquis'),
        ('e', 'Expert'),
    ]
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='competence_evaluations',
        limit_choices_to={'user_type': 'student'}
    )
    competence = models.ForeignKey(
        Competence,
        on_delete=models.CASCADE,
        related_name='evaluations'
    )
    evaluation = models.ForeignKey(
        Evaluation,
        on_delete=models.CASCADE,
        related_name='competence_evaluations',
        null=True,
        blank=True
    )
    grading_period = models.ForeignKey(
        GradingPeriod,
        on_delete=models.CASCADE,
        related_name='competence_evaluations'
    )
    
    # Niveau de maîtrise
    mastery_level = models.CharField(
        max_length=2,
        choices=MASTERY_LEVELS,
        verbose_name=_("Niveau de maîtrise")
    )
    
    # Commentaire
    comment = models.TextField(
        blank=True,
        verbose_name=_("Commentaire")
    )
    
    # Métadonnées
    evaluated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='evaluated_competences'
    )
    evaluated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'competence_evaluations'
        verbose_name = _("Évaluation de compétence")
        verbose_name_plural = _("Évaluations de compétences")
        unique_together = ['student', 'competence', 'evaluation']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.competence.code} - {self.get_mastery_level_display()}"