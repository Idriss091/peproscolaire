"""
Modèles pour la gestion des établissements scolaires
"""
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel
from apps.authentication.models import User


class School(BaseModel):
    """
    Modèle représentant un établissement scolaire
    """
    SCHOOL_TYPE_CHOICES = [
        ('college', 'Collège'),
        ('lycee', 'Lycée'),
        ('lycee_pro', 'Lycée Professionnel'),
    ]
    
    name = models.CharField(
        max_length=200,
        verbose_name=_("Nom de l'établissement")
    )
    school_type = models.CharField(
        max_length=20,
        choices=SCHOOL_TYPE_CHOICES,
        verbose_name=_("Type d'établissement")
    )
    address = models.TextField(verbose_name=_("Adresse"))
    postal_code = models.CharField(
        max_length=5,
        validators=[RegexValidator(r'^\d{5}$', 'Code postal invalide')],
        verbose_name=_("Code postal")
    )
    city = models.CharField(max_length=100, verbose_name=_("Ville"))
    phone = models.CharField(
        max_length=14,
        validators=[RegexValidator(r'^0[1-9]\d{8}$', 'Numéro de téléphone invalide')],
        verbose_name=_("Téléphone")
    )
    email = models.EmailField(verbose_name=_("Email"))
    website = models.URLField(blank=True, verbose_name=_("Site web"))
    logo = models.ImageField(
        upload_to='schools/logos/',
        blank=True,
        null=True,
        verbose_name=_("Logo")
    )
    subdomain = models.SlugField(
        unique=True,
        max_length=50,
        verbose_name=_("Sous-domaine")
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'schools'
        verbose_name = _("Établissement")
        verbose_name_plural = _("Établissements")
        ordering = ['name']
    
    def __str__(self):
        return self.name


class AcademicYear(BaseModel):
    """
    Année scolaire
    """
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='academic_years'
    )
    name = models.CharField(
        max_length=50,
        verbose_name=_("Nom (ex: 2024-2025)")
    )
    start_date = models.DateField(verbose_name=_("Date de début"))
    end_date = models.DateField(verbose_name=_("Date de fin"))
    is_current = models.BooleanField(
        default=False,
        verbose_name=_("Année en cours")
    )
    
    class Meta:
        db_table = 'academic_years'
        verbose_name = _("Année scolaire")
        verbose_name_plural = _("Années scolaires")
        unique_together = ['school', 'name']
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} - {self.school.name}"


class Level(BaseModel):
    """
    Niveau scolaire (6ème, 5ème, etc.)
    """
    name = models.CharField(max_length=50, verbose_name=_("Nom"))
    short_name = models.CharField(
        max_length=10,
        verbose_name=_("Nom court")
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Ordre d'affichage")
    )
    school_type = models.CharField(
        max_length=20,
        choices=School.SCHOOL_TYPE_CHOICES
    )
    
    class Meta:
        db_table = 'levels'
        verbose_name = _("Niveau")
        verbose_name_plural = _("Niveaux")
        ordering = ['order']
    
    def __str__(self):
        return self.name


class Class(BaseModel):
    """
    Classe (ex: 6ème A, 2nde 3)
    """
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='classes'
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='classes'
    )
    level = models.ForeignKey(
        Level,
        on_delete=models.PROTECT,
        related_name='classes'
    )
    name = models.CharField(max_length=50, verbose_name=_("Nom"))
    main_teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='main_classes',
        limit_choices_to={'user_type': 'teacher'},
        verbose_name=_("Professeur principal")
    )
    max_students = models.PositiveIntegerField(
        default=30,
        verbose_name=_("Nombre maximum d'élèves")
    )
    
    class Meta:
        db_table = 'classes'
        verbose_name = _("Classe")
        verbose_name_plural = _("Classes")
        unique_together = ['school', 'academic_year', 'name']
        ordering = ['level__order', 'name']
    
    def __str__(self):
        return f"{self.level.short_name} {self.name}"
    
    @property
    def student_count(self):
        return self.students.count()


class StudentClassEnrollment(BaseModel):
    """
    Inscription d'un élève dans une classe
    """
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'user_type': 'student'}
    )
    class_group = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='students'
    )
    enrollment_date = models.DateField(
        auto_now_add=True,
        verbose_name=_("Date d'inscription")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Inscription active")
    )
    
    class Meta:
        db_table = 'student_class_enrollments'
        verbose_name = _("Inscription élève")
        verbose_name_plural = _("Inscriptions élèves")
        unique_together = ['student', 'class_group']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.class_group}"