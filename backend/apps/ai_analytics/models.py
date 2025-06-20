"""
Modèles pour l'analyse IA et la détection des risques
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from apps.core.models import BaseModel
from apps.authentication.models import User
from apps.schools.models import Class, AcademicYear


class RiskProfile(BaseModel):
    """
    Profil de risque d'un élève
    """
    RISK_LEVEL_CHOICES = [
        ('very_low', 'Très faible'),
        ('low', 'Faible'),
        ('moderate', 'Modéré'),
        ('high', 'Élevé'),
        ('critical', 'Critique'),
    ]
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='risk_profiles',
        limit_choices_to={'user_type': 'student'}
    )
    
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='risk_profiles'
    )
    
    # Score de risque global (0-100)
    risk_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        verbose_name=_("Score de risque")
    )
    
    risk_level = models.CharField(
        max_length=20,
        choices=RISK_LEVEL_CHOICES,
        default='low',
        verbose_name=_("Niveau de risque")
    )
    
    # Facteurs de risque détaillés
    academic_risk = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        verbose_name=_("Risque académique")
    )
    
    attendance_risk = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        verbose_name=_("Risque d'assiduité")
    )
    
    behavioral_risk = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        verbose_name=_("Risque comportemental")
    )
    
    social_risk = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        verbose_name=_("Risque social")
    )
    
    # Données détaillées
    risk_factors = models.JSONField(
        default=dict,
        verbose_name=_("Facteurs de risque détaillés")
    )
    
    # Indicateurs spécifiques
    indicators = models.JSONField(
        default=dict,
        verbose_name=_("Indicateurs")
    )
    
    # Prédictions
    dropout_probability = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name=_("Probabilité de décrochage")
    )
    
    predicted_final_average = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_("Moyenne finale prédite")
    )
    
    # Recommandations
    recommendations = ArrayField(
        models.TextField(),
        default=list,
        blank=True,
        verbose_name=_("Recommandations")
    )
    
    priority_actions = ArrayField(
        models.CharField(max_length=200),
        default=list,
        blank=True,
        verbose_name=_("Actions prioritaires")
    )
    
    # Suivi
    last_analysis = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Dernière analyse")
    )
    
    analysis_version = models.CharField(
        max_length=20,
        default='1.0',
        verbose_name=_("Version du modèle")
    )
    
    # État
    is_monitored = models.BooleanField(
        default=False,
        verbose_name=_("Sous surveillance")
    )
    
    monitoring_started = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Début de surveillance")
    )
    
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='monitored_students',
        limit_choices_to={'user_type': 'teacher'},
        verbose_name=_("Référent assigné")
    )
    
    class Meta:
        db_table = 'risk_profiles'
        verbose_name = _("Profil de risque")
        verbose_name_plural = _("Profils de risque")
        unique_together = ['student', 'academic_year']
        ordering = ['-risk_score']
        indexes = [
            models.Index(fields=['risk_level', 'academic_year']),
            models.Index(fields=['is_monitored', 'risk_score']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - Risque: {self.get_risk_level_display()}"
    
    def calculate_risk_level(self):
        """Déterminer le niveau de risque selon le score"""
        if self.risk_score >= 80:
            self.risk_level = 'critical'
        elif self.risk_score >= 60:
            self.risk_level = 'high'
        elif self.risk_score >= 40:
            self.risk_level = 'moderate'
        elif self.risk_score >= 20:
            self.risk_level = 'low'
        else:
            self.risk_level = 'very_low'
    
    def start_monitoring(self, assigned_to=None):
        """Démarrer le suivi de l'élève"""
        self.is_monitored = True
        self.monitoring_started = timezone.now()
        if assigned_to:
            self.assigned_to = assigned_to
        self.save()


class RiskIndicator(BaseModel):
    """
    Indicateur de risque configuré
    """
    INDICATOR_TYPE_CHOICES = [
        ('absence_rate', 'Taux d\'absence'),
        ('grade_drop', 'Chute des notes'),
        ('late_submissions', 'Retards de rendu'),
        ('behavior_incidents', 'Incidents comportementaux'),
        ('social_isolation', 'Isolement social'),
        ('attendance_pattern', 'Schéma d\'absence'),
        ('engagement_drop', 'Baisse d\'engagement'),
        ('custom', 'Personnalisé'),
    ]
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Nom")
    )
    
    indicator_type = models.CharField(
        max_length=30,
        choices=INDICATOR_TYPE_CHOICES,
        verbose_name=_("Type d'indicateur")
    )
    
    description = models.TextField(
        verbose_name=_("Description")
    )
    
    # Configuration du seuil
    threshold_value = models.FloatField(
        verbose_name=_("Valeur seuil")
    )
    
    threshold_operator = models.CharField(
        max_length=10,
        choices=[
            ('gt', 'Supérieur à'),
            ('gte', 'Supérieur ou égal à'),
            ('lt', 'Inférieur à'),
            ('lte', 'Inférieur ou égal à'),
            ('eq', 'Égal à'),
        ],
        default='gt',
        verbose_name=_("Opérateur")
    )
    
    # Poids dans le calcul
    weight = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        verbose_name=_("Poids")
    )
    
    # Configuration
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Actif")
    )
    
    applies_to_levels = ArrayField(
        models.CharField(max_length=50),
        default=list,
        blank=True,
        verbose_name=_("Niveaux concernés"),
        help_text=_("Laisser vide pour tous les niveaux")
    )
    
    # Requête personnalisée
    custom_query = models.TextField(
        blank=True,
        verbose_name=_("Requête personnalisée"),
        help_text=_("Code Python pour calculer l'indicateur")
    )
    
    class Meta:
        db_table = 'risk_indicators'
        verbose_name = _("Indicateur de risque")
        verbose_name_plural = _("Indicateurs de risque")
        ordering = ['-weight', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_indicator_type_display()})"
    
    def evaluate(self, student, period_start, period_end):
        """Évaluer l'indicateur pour un élève"""
        if self.indicator_type == 'custom' and self.custom_query:
            # Exécuter la requête personnalisée
            # Sécurité : exécuter dans un environnement sandboxé
            return self._evaluate_custom(student, period_start, period_end)
        
        # Évaluations prédéfinies
        evaluators = {
            'absence_rate': self._evaluate_absence_rate,
            'grade_drop': self._evaluate_grade_drop,
            'late_submissions': self._evaluate_late_submissions,
            'behavior_incidents': self._evaluate_behavior_incidents,
            'social_isolation': self._evaluate_social_isolation,
            'attendance_pattern': self._evaluate_attendance_pattern,
            'engagement_drop': self._evaluate_engagement_drop,
        }
        
        evaluator = evaluators.get(self.indicator_type)
        if evaluator:
            return evaluator(student, period_start, period_end)
        
        return None
    
    def _evaluate_absence_rate(self, student, period_start, period_end):
        """Évaluer le taux d'absence"""
        from apps.attendance.models import Attendance, AttendanceStatus
        
        attendances = Attendance.objects.filter(
            student=student,
            date__range=[period_start, period_end]
        )
        
        total = attendances.count()
        if total == 0:
            return 0
        
        absences = attendances.filter(
            status=AttendanceStatus.ABSENT,
            is_justified=False
        ).count()
        
        return (absences / total) * 100
    
    def _evaluate_grade_drop(self, student, period_start, period_end):
        """Évaluer la chute des notes"""
        from apps.grades.models import Grade
        from django.db.models import Avg
        
        # Moyenne période actuelle
        current_avg = Grade.objects.filter(
            student=student,
            evaluation__date__range=[period_start, period_end],
            score__isnull=False
        ).aggregate(avg=Avg('normalized_score'))['avg']
        
        # Moyenne période précédente
        previous_period_end = period_start - timezone.timedelta(days=1)
        previous_period_start = previous_period_end - (period_end - period_start)
        
        previous_avg = Grade.objects.filter(
            student=student,
            evaluation__date__range=[previous_period_start, previous_period_end],
            score__isnull=False
        ).aggregate(avg=Avg('normalized_score'))['avg']
        
        if not current_avg or not previous_avg:
            return 0
        
        # Pourcentage de chute
        drop = ((previous_avg - current_avg) / previous_avg) * 100
        return max(0, drop)
    
    def _evaluate_late_submissions(self, student, period_start, period_end):
        """Évaluer les retards de rendu"""
        from apps.homework.models import StudentWork
        
        submissions = StudentWork.objects.filter(
            student=student,
            homework__due_date__range=[period_start, period_end]
        )
        
        total = submissions.count()
        if total == 0:
            return 0
        
        late = submissions.filter(status='late').count()
        return (late / total) * 100
    
    def _evaluate_behavior_incidents(self, student, period_start, period_end):
        """Évaluer les incidents comportementaux"""
        from apps.attendance.models import Sanction
        
        return Sanction.objects.filter(
            student=student,
            date__range=[period_start, period_end]
        ).count()
    
    def _evaluate_social_isolation(self, student, period_start, period_end):
        """Évaluer l'isolement social"""
        # Analyse des interactions (messages, travaux de groupe, etc.)
        # Simplifié pour l'exemple
        return 0
    
    def _evaluate_attendance_pattern(self, student, period_start, period_end):
        """Évaluer les schémas d'absence"""
        # Détection de patterns (ex: toujours absent le lundi)
        # Implémenté dans les tâches Celery
        return 0
    
    def _evaluate_engagement_drop(self, student, period_start, period_end):
        """Évaluer la baisse d'engagement"""
        # Analyse de la participation, connexions, etc.
        return 0
    
    def _evaluate_custom(self, student, period_start, period_end):
        """Évaluer avec une requête personnalisée"""
        # Sécurité : exécuter dans un environnement restreint
        # TODO: Implémenter l'exécution sécurisée
        return 0


class InterventionPlan(BaseModel):
    """
    Plan d'intervention pour un élève à risque
    """
    PLAN_STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('active', 'Actif'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
    ]
    
    risk_profile = models.ForeignKey(
        RiskProfile,
        on_delete=models.CASCADE,
        related_name='intervention_plans'
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name=_("Titre du plan")
    )
    
    description = models.TextField(
        verbose_name=_("Description")
    )
    
    status = models.CharField(
        max_length=20,
        choices=PLAN_STATUS_CHOICES,
        default='draft',
        verbose_name=_("Statut")
    )
    
    # Participants
    coordinator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='coordinated_plans',
        verbose_name=_("Coordinateur")
    )
    
    participants = models.ManyToManyField(
        User,
        related_name='intervention_participations',
        verbose_name=_("Participants")
    )
    
    # Période
    start_date = models.DateField(
        verbose_name=_("Date de début")
    )
    
    end_date = models.DateField(
        verbose_name=_("Date de fin prévue")
    )
    
    actual_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Date de fin réelle")
    )
    
    # Objectifs
    objectives = models.JSONField(
        default=list,
        verbose_name=_("Objectifs")
    )
    
    # Actions prévues
    planned_actions = models.JSONField(
        default=list,
        verbose_name=_("Actions planifiées")
    )
    
    # Ressources
    resources_needed = models.TextField(
        blank=True,
        verbose_name=_("Ressources nécessaires")
    )
    
    # Évaluation
    success_criteria = models.TextField(
        blank=True,
        verbose_name=_("Critères de réussite")
    )
    
    evaluation_frequency = models.CharField(
        max_length=20,
        choices=[
            ('weekly', 'Hebdomadaire'),
            ('biweekly', 'Bimensuel'),
            ('monthly', 'Mensuel'),
        ],
        default='weekly',
        verbose_name=_("Fréquence d'évaluation")
    )
    
    # Résultats
    outcomes = models.TextField(
        blank=True,
        verbose_name=_("Résultats obtenus")
    )
    
    effectiveness_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        verbose_name=_("Score d'efficacité")
    )
    
    class Meta:
        db_table = 'intervention_plans'
        verbose_name = _("Plan d'intervention")
        verbose_name_plural = _("Plans d'intervention")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.risk_profile.student.get_full_name()}"


class InterventionAction(BaseModel):
    """
    Action spécifique dans un plan d'intervention
    """
    ACTION_TYPE_CHOICES = [
        ('tutoring', 'Tutorat'),
        ('counseling', 'Suivi psychologique'),
        ('parental_meeting', 'Rencontre parents'),
        ('academic_support', 'Soutien scolaire'),
        ('social_activity', 'Activité sociale'),
        ('monitoring', 'Surveillance renforcée'),
        ('other', 'Autre'),
    ]
    
    intervention_plan = models.ForeignKey(
        InterventionPlan,
        on_delete=models.CASCADE,
        related_name='actions'
    )
    
    action_type = models.CharField(
        max_length=30,
        choices=ACTION_TYPE_CHOICES,
        verbose_name=_("Type d'action")
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name=_("Titre")
    )
    
    description = models.TextField(
        verbose_name=_("Description")
    )
    
    responsible = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='responsible_actions',
        verbose_name=_("Responsable")
    )
    
    # Planification
    scheduled_date = models.DateField(
        verbose_name=_("Date prévue")
    )
    
    scheduled_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("Heure prévue")
    )
    
    duration_minutes = models.PositiveIntegerField(
        default=60,
        verbose_name=_("Durée (minutes)")
    )
    
    # Réalisation
    completed = models.BooleanField(
        default=False,
        verbose_name=_("Réalisée")
    )
    
    completed_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Date de réalisation")
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_("Notes de suivi")
    )
    
    # Impact
    impact_assessment = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ('very_positive', 'Très positif'),
            ('positive', 'Positif'),
            ('neutral', 'Neutre'),
            ('negative', 'Négatif'),
            ('very_negative', 'Très négatif'),
        ],
        verbose_name=_("Évaluation de l'impact")
    )
    
    class Meta:
        db_table = 'intervention_actions'
        verbose_name = _("Action d'intervention")
        verbose_name_plural = _("Actions d'intervention")
        ordering = ['scheduled_date', 'scheduled_time']
    
    def __str__(self):
        return f"{self.title} - {self.scheduled_date}"
    
    def mark_completed(self, notes=''):
        """Marquer l'action comme complétée"""
        self.completed = True
        self.completed_date = timezone.now()
        if notes:
            self.notes = notes
        self.save()


class AlertConfiguration(BaseModel):
    """
    Configuration des alertes automatiques
    """
    ALERT_TYPE_CHOICES = [
        ('risk_increase', 'Augmentation du risque'),
        ('threshold_reached', 'Seuil atteint'),
        ('pattern_detected', 'Schéma détecté'),
        ('intervention_needed', 'Intervention requise'),
        ('progress_report', 'Rapport de progrès'),
    ]
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Nom")
    )
    
    alert_type = models.CharField(
        max_length=30,
        choices=ALERT_TYPE_CHOICES,
        verbose_name=_("Type d'alerte")
    )
    
    description = models.TextField(
        verbose_name=_("Description")
    )
    
    # Conditions de déclenchement
    risk_level_threshold = models.CharField(
        max_length=20,
        choices=RiskProfile.RISK_LEVEL_CHOICES,
        blank=True,
        verbose_name=_("Seuil de niveau de risque")
    )
    
    risk_score_threshold = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        verbose_name=_("Seuil de score de risque")
    )
    
    indicator_conditions = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Conditions sur les indicateurs")
    )
    
    # Destinataires
    notify_student = models.BooleanField(
        default=False,
        verbose_name=_("Notifier l'élève")
    )
    
    notify_parents = models.BooleanField(
        default=True,
        verbose_name=_("Notifier les parents")
    )
    
    notify_main_teacher = models.BooleanField(
        default=True,
        verbose_name=_("Notifier le professeur principal")
    )
    
    notify_administration = models.BooleanField(
        default=False,
        verbose_name=_("Notifier l'administration")
    )
    
    additional_recipients = models.ManyToManyField(
        User,
        blank=True,
        related_name='alert_subscriptions',
        verbose_name=_("Destinataires supplémentaires")
    )
    
    # Configuration
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active")
    )
    
    cooldown_days = models.PositiveIntegerField(
        default=7,
        verbose_name=_("Délai entre alertes (jours)")
    )
    
    # Template du message
    message_template = models.TextField(
        verbose_name=_("Modèle de message"),
        help_text=_("Variables disponibles: {student_name}, {risk_level}, {risk_score}")
    )
    
    priority = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Faible'),
            ('normal', 'Normale'),
            ('high', 'Haute'),
            ('urgent', 'Urgente'),
        ],
        default='normal',
        verbose_name=_("Priorité")
    )
    
    class Meta:
        db_table = 'alert_configurations'
        verbose_name = _("Configuration d'alerte")
        verbose_name_plural = _("Configurations d'alertes")
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_alert_type_display()})"
    
    def should_trigger(self, risk_profile):
        """Vérifier si l'alerte doit être déclenchée"""
        # Vérifier le niveau de risque
        if self.risk_level_threshold:
            levels = ['very_low', 'low', 'moderate', 'high', 'critical']
            current_idx = levels.index(risk_profile.risk_level)
            threshold_idx = levels.index(self.risk_level_threshold)
            
            if current_idx < threshold_idx:
                return False
        
        # Vérifier le score de risque
        if self.risk_score_threshold is not None:
            if risk_profile.risk_score < self.risk_score_threshold:
                return False
        
        # Vérifier les conditions sur les indicateurs
        if self.indicator_conditions:
            for indicator, condition in self.indicator_conditions.items():
                value = risk_profile.indicators.get(indicator)
                if not self._check_condition(value, condition):
                    return False
        
        # Vérifier le cooldown
        from apps.ai_analytics.models import Alert
        last_alert = Alert.objects.filter(
            risk_profile=risk_profile,
            alert_configuration=self
        ).order_by('-created_at').first()
        
        if last_alert:
            days_since = (timezone.now() - last_alert.created_at).days
            if days_since < self.cooldown_days:
                return False
        
        return True
    
    def _check_condition(self, value, condition):
        """Vérifier une condition"""
        if value is None:
            return False
        
        operator = condition.get('operator', 'gt')
        threshold = condition.get('value', 0)
        
        operators = {
            'gt': lambda x, y: x > y,
            'gte': lambda x, y: x >= y,
            'lt': lambda x, y: x < y,
            'lte': lambda x, y: x <= y,
            'eq': lambda x, y: x == y,
        }
        
        return operators.get(operator, lambda x, y: False)(value, threshold)


class Alert(BaseModel):
    """
    Alerte générée
    """
    risk_profile = models.ForeignKey(
        RiskProfile,
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    
    alert_configuration = models.ForeignKey(
        AlertConfiguration,
        on_delete=models.CASCADE,
        related_name='generated_alerts'
    )
    
    # Contenu
    title = models.CharField(
        max_length=200,
        verbose_name=_("Titre")
    )
    
    message = models.TextField(
        verbose_name=_("Message")
    )
    
    priority = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Faible'),
            ('normal', 'Normale'),
            ('high', 'Haute'),
            ('urgent', 'Urgente'),
        ],
        verbose_name=_("Priorité")
    )
    
    # Données contextuelles
    context_data = models.JSONField(
        default=dict,
        verbose_name=_("Données contextuelles")
    )
    
    # État
    is_read = models.BooleanField(
        default=False,
        verbose_name=_("Lue")
    )
    
    read_by = models.ManyToManyField(
        User,
        related_name='read_risk_alerts',
        blank=True,
        verbose_name=_("Lue par")
    )
    
    is_acknowledged = models.BooleanField(
        default=False,
        verbose_name=_("Prise en compte")
    )
    
    acknowledged_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts',
        verbose_name=_("Prise en compte par")
    )
    
    acknowledged_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Prise en compte le")
    )
    
    # Actions prises
    actions_taken = models.TextField(
        blank=True,
        verbose_name=_("Actions prises")
    )
    
    # Notifications
    notifications_sent = models.JSONField(
        default=dict,
        verbose_name=_("Notifications envoyées")
    )
    
    class Meta:
        db_table = 'risk_alerts'
        verbose_name = _("Alerte de risque")
        verbose_name_plural = _("Alertes de risque")
        ordering = ['-created_at', '-priority']
        indexes = [
            models.Index(fields=['is_acknowledged', 'priority']),
            models.Index(fields=['risk_profile', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.risk_profile.student.get_full_name()}"
    
    def acknowledge(self, user, actions=''):
        """Prendre en compte l'alerte"""
        self.is_acknowledged = True
        self.acknowledged_by = user
        self.acknowledged_at = timezone.now()
        if actions:
            self.actions_taken = actions
        self.save()