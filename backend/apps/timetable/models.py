"""
Modèles pour la gestion des emplois du temps
"""
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel
from apps.authentication.models import User
from apps.schools.models import School, Class, AcademicYear


class Subject(BaseModel):
    """
    Matière enseignée
    """
    name = models.CharField(max_length=100, verbose_name=_("Nom"))
    short_name = models.CharField(
        max_length=10,
        verbose_name=_("Abréviation")
    )
    color = models.CharField(
        max_length=7,
        default='#3498db',
        verbose_name=_("Couleur (hex)")
    )
    coefficient = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=1.0,
        verbose_name=_("Coefficient")
    )
    is_optional = models.BooleanField(
        default=False,
        verbose_name=_("Matière optionnelle")
    )
    
    class Meta:
        db_table = 'subjects'
        verbose_name = _("Matière")
        verbose_name_plural = _("Matières")
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Room(BaseModel):
    """
    Salle de classe
    """
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='rooms'
    )
    name = models.CharField(max_length=50, verbose_name=_("Nom"))
    building = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Bâtiment")
    )
    floor = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Étage")
    )
    capacity = models.PositiveIntegerField(
        default=30,
        verbose_name=_("Capacité")
    )
    room_type = models.CharField(
        max_length=50,
        choices=[
            ('classroom', 'Salle de classe'),
            ('laboratory', 'Laboratoire'),
            ('computer_room', 'Salle informatique'),
            ('gym', 'Gymnase'),
            ('library', 'CDI/Bibliothèque'),
            ('auditorium', 'Amphithéâtre'),
        ],
        default='classroom',
        verbose_name=_("Type de salle")
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name=_("Disponible")
    )
    
    class Meta:
        db_table = 'rooms'
        verbose_name = _("Salle")
        verbose_name_plural = _("Salles")
        unique_together = ['school', 'name']
        ordering = ['building', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.building})" if self.building else self.name


class TimeSlot(BaseModel):
    """
    Créneau horaire type
    """
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='time_slots'
    )
    day = models.IntegerField(
        choices=[
            (0, 'Lundi'),
            (1, 'Mardi'),
            (2, 'Mercredi'),
            (3, 'Jeudi'),
            (4, 'Vendredi'),
            (5, 'Samedi'),
        ],
        verbose_name=_("Jour")
    )
    start_time = models.TimeField(verbose_name=_("Heure de début"))
    end_time = models.TimeField(verbose_name=_("Heure de fin"))
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Ordre dans la journée")
    )
    is_break = models.BooleanField(
        default=False,
        verbose_name=_("Pause/Récréation")
    )
    
    class Meta:
        db_table = 'time_slots'
        verbose_name = _("Créneau horaire")
        verbose_name_plural = _("Créneaux horaires")
        ordering = ['day', 'order', 'start_time']
        unique_together = ['school', 'day', 'start_time']
    
    def __str__(self):
        days = dict(self._meta.get_field('day').choices)
        return f"{days[self.day]} {self.start_time:%H:%M}-{self.end_time:%H:%M}"
    
    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError(_("L'heure de fin doit être après l'heure de début"))


class Schedule(BaseModel):
    """
    Cours planifié dans l'emploi du temps
    """
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    class_group = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='teaching_schedules',
        limit_choices_to={'user_type': 'teacher'}
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='schedules'
    )
    time_slot = models.ForeignKey(
        TimeSlot,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    
    # Pour les cours sur plusieurs semaines
    week_type = models.CharField(
        max_length=1,
        choices=[
            ('A', 'Semaine A'),
            ('B', 'Semaine B'),
            ('*', 'Toutes les semaines'),
        ],
        default='*',
        verbose_name=_("Type de semaine")
    )
    
    # Pour les cours temporaires ou annulés
    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Date de début")
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Date de fin")
    )
    is_cancelled = models.BooleanField(
        default=False,
        verbose_name=_("Cours annulé")
    )
    
    class Meta:
        db_table = 'schedules'
        verbose_name = _("Cours")
        verbose_name_plural = _("Cours")
        ordering = ['time_slot__day', 'time_slot__start_time']
    
    def __str__(self):
        return f"{self.class_group} - {self.subject} - {self.time_slot}"
    
    def clean(self):
        # Vérification des conflits d'emploi du temps
        # Pour le professeur
        teacher_conflict = Schedule.objects.filter(
            academic_year=self.academic_year,
            teacher=self.teacher,
            time_slot=self.time_slot,
            week_type__in=[self.week_type, '*'],
            is_cancelled=False
        ).exclude(pk=self.pk)
        
        if teacher_conflict.exists():
            raise ValidationError(
                _("Le professeur a déjà un cours à ce créneau")
            )
        
        # Pour la salle
        if self.room:
            room_conflict = Schedule.objects.filter(
                academic_year=self.academic_year,
                room=self.room,
                time_slot=self.time_slot,
                week_type__in=[self.week_type, '*'],
                is_cancelled=False
            ).exclude(pk=self.pk)
            
            if room_conflict.exists():
                raise ValidationError(
                    _("La salle est déjà occupée à ce créneau")
                )
        
        # Pour la classe
        class_conflict = Schedule.objects.filter(
            academic_year=self.academic_year,
            class_group=self.class_group,
            time_slot=self.time_slot,
            week_type__in=[self.week_type, '*'],
            is_cancelled=False
        ).exclude(pk=self.pk)
        
        if class_conflict.exists():
            raise ValidationError(
                _("La classe a déjà un cours à ce créneau")
            )


class ScheduleModification(BaseModel):
    """
    Modification ponctuelle d'un cours (remplacement, annulation, etc.)
    """
    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        related_name='modifications'
    )
    date = models.DateField(verbose_name=_("Date de la modification"))
    
    MODIFICATION_TYPE_CHOICES = [
        ('cancelled', 'Annulé'),
        ('replaced', 'Remplacé'),
        ('room_changed', 'Changement de salle'),
        ('time_changed', 'Changement d\'horaire'),
    ]
    
    modification_type = models.CharField(
        max_length=20,
        choices=MODIFICATION_TYPE_CHOICES,
        verbose_name=_("Type de modification")
    )
    
    # Pour les remplacements
    substitute_teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='substitute_schedules',
        limit_choices_to={'user_type': 'teacher'}
    )
    
    # Pour les changements de salle
    new_room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Pour les changements d'horaire
    new_start_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("Nouvelle heure de début")
    )
    new_end_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("Nouvelle heure de fin")
    )
    
    reason = models.TextField(
        blank=True,
        verbose_name=_("Raison de la modification")
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_modifications'
    )
    
    class Meta:
        db_table = 'schedule_modifications'
        verbose_name = _("Modification d'emploi du temps")
        verbose_name_plural = _("Modifications d'emploi du temps")
        unique_together = ['schedule', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.schedule} - {self.date} - {self.get_modification_type_display()}"