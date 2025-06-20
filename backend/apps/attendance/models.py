"""
Modèles pour la gestion de la vie scolaire (absences, retards, sanctions)
"""
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import datetime, time
from apps.core.models import BaseModel
from apps.authentication.models import User
from apps.schools.models import Class, AcademicYear
from apps.timetable.models import Schedule, TimeSlot


class AttendanceStatus(models.TextChoices):
    """Statuts de présence possibles"""
    PRESENT = 'present', _('Présent')
    ABSENT = 'absent', _('Absent')
    LATE = 'late', _('En retard')
    EXCUSED = 'excused', _('Absent excusé')
    EXCLUDED = 'excluded', _('Exclu')


class Attendance(BaseModel):
    """
    Enregistrement de présence pour un élève à un cours
    """
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='attendances',
        limit_choices_to={'user_type': 'student'}
    )
    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    date = models.DateField(verbose_name=_("Date"))
    status = models.CharField(
        max_length=20,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PRESENT,
        verbose_name=_("Statut")
    )
    
    # Pour les retards
    arrival_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("Heure d'arrivée")
    )
    late_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Minutes de retard")
    )
    
    # Justification
    is_justified = models.BooleanField(
        default=False,
        verbose_name=_("Justifié")
    )
    justification_document = models.FileField(
        upload_to='justifications/%Y/%m/',
        null=True,
        blank=True,
        verbose_name=_("Document justificatif")
    )
    justification_reason = models.TextField(
        blank=True,
        verbose_name=_("Motif")
    )
    
    # Métadonnées
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_attendances',
        verbose_name=_("Enregistré par")
    )
    recorded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Enregistré le")
    )
    modified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='modified_attendances',
        verbose_name=_("Modifié par")
    )
    modified_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Modifié le")
    )
    
    class Meta:
        db_table = 'attendances'
        verbose_name = _("Présence")
        verbose_name_plural = _("Présences")
        unique_together = ['student', 'schedule', 'date']
        ordering = ['-date', 'schedule__time_slot__start_time']
        indexes = [
            models.Index(fields=['date', 'status']),
            models.Index(fields=['student', 'date']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.schedule} - {self.date}"
    
    def clean(self):
        """Validation des données"""
        if self.status == AttendanceStatus.LATE and not self.arrival_time:
            raise ValidationError({
                'arrival_time': _("L'heure d'arrivée est requise pour un retard")
            })
        
        if self.arrival_time and self.schedule.time_slot.start_time:
            # Calculer automatiquement les minutes de retard
            start_datetime = datetime.combine(self.date, self.schedule.time_slot.start_time)
            arrival_datetime = datetime.combine(self.date, self.arrival_time)
            
            if arrival_datetime > start_datetime:
                delta = arrival_datetime - start_datetime
                self.late_minutes = int(delta.total_seconds() / 60)
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class AbsencePeriod(BaseModel):
    """
    Période d'absence longue (maladie, voyage, etc.)
    """
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='absence_periods',
        limit_choices_to={'user_type': 'student'}
    )
    start_date = models.DateField(verbose_name=_("Date de début"))
    end_date = models.DateField(verbose_name=_("Date de fin"))
    reason = models.CharField(
        max_length=200,
        verbose_name=_("Motif")
    )
    is_justified = models.BooleanField(
        default=False,
        verbose_name=_("Justifiée")
    )
    justification_document = models.FileField(
        upload_to='absence_periods/%Y/%m/',
        null=True,
        blank=True,
        verbose_name=_("Justificatif")
    )
    
    # Notification
    notified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='notified_absences',
        verbose_name=_("Notifié par")
    )
    notified_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Notifié le")
    )
    
    class Meta:
        db_table = 'absence_periods'
        verbose_name = _("Période d'absence")
        verbose_name_plural = _("Périodes d'absence")
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.start_date} au {self.end_date}"
    
    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError({
                'end_date': _("La date de fin doit être après la date de début")
            })
    
    def get_duration_days(self):
        """Retourne la durée en jours"""
        return (self.end_date - self.start_date).days + 1


class Sanction(BaseModel):
    """
    Sanctions disciplinaires
    """
    SANCTION_TYPE_CHOICES = [
        ('warning', 'Avertissement'),
        ('blame', 'Blâme'),
        ('detention', 'Retenue'),
        ('exclusion_temp', 'Exclusion temporaire'),
        ('exclusion_def', 'Exclusion définitive'),
        ('work', 'Travail supplémentaire'),
        ('community_service', "Travail d'intérêt général"),
    ]
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sanctions',
        limit_choices_to={'user_type': 'student'}
    )
    sanction_type = models.CharField(
        max_length=30,
        choices=SANCTION_TYPE_CHOICES,
        verbose_name=_("Type de sanction")
    )
    date = models.DateField(
        default=timezone.now,
        verbose_name=_("Date de la sanction")
    )
    
    # Détails de la sanction
    reason = models.TextField(verbose_name=_("Motif"))
    description = models.TextField(
        blank=True,
        verbose_name=_("Description détaillée")
    )
    
    # Pour les retenues
    detention_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Date de la retenue")
    )
    detention_start_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("Heure de début")
    )
    detention_end_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("Heure de fin")
    )
    detention_room = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Salle")
    )
    
    # Pour les exclusions
    exclusion_start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Début d'exclusion")
    )
    exclusion_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Fin d'exclusion")
    )
    
    # Responsable
    given_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='given_sanctions',
        verbose_name=_("Donnée par")
    )
    
    # Suivi
    is_completed = models.BooleanField(
        default=False,
        verbose_name=_("Effectuée")
    )
    completion_notes = models.TextField(
        blank=True,
        verbose_name=_("Notes de suivi")
    )
    
    # Notification parents
    parents_notified = models.BooleanField(
        default=False,
        verbose_name=_("Parents notifiés")
    )
    notification_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Date de notification")
    )
    
    class Meta:
        db_table = 'sanctions'
        verbose_name = _("Sanction")
        verbose_name_plural = _("Sanctions")
        ordering = ['-date']
        indexes = [
            models.Index(fields=['student', 'date']),
            models.Index(fields=['sanction_type', 'is_completed']),
        ]
    
    def __str__(self):
        return f"{self.get_sanction_type_display()} - {self.student.get_full_name()} - {self.date}"
    
    def clean(self):
        """Validation selon le type de sanction"""
        if self.sanction_type == 'detention':
            if not all([self.detention_date, self.detention_start_time, self.detention_end_time]):
                raise ValidationError({
                    'detention_date': _("Les informations de retenue sont requises")
                })
            
            if self.detention_end_time <= self.detention_start_time:
                raise ValidationError({
                    'detention_end_time': _("L'heure de fin doit être après l'heure de début")
                })
        
        elif self.sanction_type in ['exclusion_temp', 'exclusion_def']:
            if not self.exclusion_start_date:
                raise ValidationError({
                    'exclusion_start_date': _("La date de début d'exclusion est requise")
                })
            
            if self.sanction_type == 'exclusion_temp' and not self.exclusion_end_date:
                raise ValidationError({
                    'exclusion_end_date': _("La date de fin est requise pour une exclusion temporaire")
                })


class StudentBehavior(BaseModel):
    """
    Suivi du comportement général d'un élève
    """
    BEHAVIOR_TYPE_CHOICES = [
        ('positive', 'Positif'),
        ('negative', 'Négatif'),
        ('neutral', 'Neutre'),
    ]
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='behavior_records',
        limit_choices_to={'user_type': 'student'}
    )
    date = models.DateField(
        default=timezone.now,
        verbose_name=_("Date")
    )
    behavior_type = models.CharField(
        max_length=20,
        choices=BEHAVIOR_TYPE_CHOICES,
        verbose_name=_("Type")
    )
    category = models.CharField(
        max_length=100,
        verbose_name=_("Catégorie"),
        help_text=_("Ex: Participation, Respect, Travail, etc.")
    )
    description = models.TextField(verbose_name=_("Description"))
    
    # Points de comportement (système de points optionnel)
    points = models.IntegerField(
        default=0,
        verbose_name=_("Points"),
        help_text=_("Positif ou négatif selon le comportement")
    )
    
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_behaviors',
        verbose_name=_("Enregistré par")
    )
    
    class Meta:
        db_table = 'student_behaviors'
        verbose_name = _("Comportement")
        verbose_name_plural = _("Comportements")
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.get_behavior_type_display()} - {self.date}"


class AttendanceAlert(BaseModel):
    """
    Alertes automatiques pour absences/retards répétés
    """
    ALERT_TYPE_CHOICES = [
        ('absence_count', 'Nombre d\'absences'),
        ('late_count', 'Nombre de retards'),
        ('consecutive_absence', 'Absences consécutives'),
        ('pattern', 'Schéma récurrent'),
    ]
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='attendance_alerts',
        limit_choices_to={'user_type': 'student'}
    )
    alert_type = models.CharField(
        max_length=30,
        choices=ALERT_TYPE_CHOICES,
        verbose_name=_("Type d'alerte")
    )
    threshold_value = models.IntegerField(
        verbose_name=_("Valeur seuil atteinte")
    )
    period_start = models.DateField(verbose_name=_("Début de période"))
    period_end = models.DateField(verbose_name=_("Fin de période"))
    
    # Détails
    message = models.TextField(verbose_name=_("Message d'alerte"))
    details = models.JSONField(
        default=dict,
        verbose_name=_("Détails supplémentaires")
    )
    
    # Suivi
    is_resolved = models.BooleanField(
        default=False,
        verbose_name=_("Résolu")
    )
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_alerts',
        verbose_name=_("Résolu par")
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Résolu le")
    )
    resolution_notes = models.TextField(
        blank=True,
        verbose_name=_("Notes de résolution")
    )
    
    # Notifications
    notified_users = models.ManyToManyField(
        User,
        related_name='received_alerts',
        verbose_name=_("Utilisateurs notifiés")
    )
    
    class Meta:
        db_table = 'attendance_alerts'
        verbose_name = _("Alerte d'assiduité")
        verbose_name_plural = _("Alertes d'assiduité")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'is_resolved']),
            models.Index(fields=['alert_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"Alerte {self.get_alert_type_display()} - {self.student.get_full_name()}"