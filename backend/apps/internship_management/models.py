from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator, EmailValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid
from datetime import date, timedelta

User = get_user_model()


class Company(models.Model):
    """
    Modèle pour les entreprises partenaires
    """
    COMPANY_SIZES = [
        ('micro', 'Micro-entreprise (< 10 salariés)'),
        ('small', 'Petite entreprise (10-50 salariés)'),
        ('medium', 'Moyenne entreprise (50-250 salariés)'),
        ('large', 'Grande entreprise (> 250 salariés)'),
    ]
    
    SECTORS = [
        ('tech', 'Technologies'),
        ('finance', 'Finance/Banque'),
        ('healthcare', 'Santé'),
        ('education', 'Éducation'),
        ('retail', 'Commerce/Vente'),
        ('manufacturing', 'Industrie'),
        ('consulting', 'Conseil'),
        ('media', 'Médias/Communication'),
        ('ngo', 'ONG/Associations'),
        ('public', 'Secteur public'),
        ('other', 'Autre'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Informations de base
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    sector = models.CharField(max_length=20, choices=SECTORS, default='other')
    size = models.CharField(max_length=10, choices=COMPANY_SIZES, default='small')
    
    # Contact principal
    contact_person = models.CharField(max_length=100, blank=True)
    contact_email = models.EmailField(validators=[EmailValidator()])
    contact_phone = models.CharField(max_length=20, blank=True)
    
    # Adresse
    address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=50, default='France')
    
    # Informations supplémentaires
    website = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    siret = models.CharField(max_length=14, blank=True, unique=True, null=True)
    
    # Statut et partenariat
    is_partner = models.BooleanField(default=False, help_text="Entreprise partenaire officielle")
    is_active = models.BooleanField(default=True)
    partnership_since = models.DateField(null=True, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Statistiques
    total_internships = models.PositiveIntegerField(default=0)
    average_rating = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['sector', 'is_active']),
            models.Index(fields=['city', 'is_partner']),
            models.Index(fields=['-average_rating']),
        ]
        
    def __str__(self):
        return self.name
    
    def clean(self):
        if self.is_partner and not self.partnership_since:
            self.partnership_since = timezone.now().date()
    
    def update_statistics(self):
        """Met à jour les statistiques de l'entreprise"""
        internships = self.internships.all()
        self.total_internships = internships.count()
        
        # Calculer la note moyenne
        completed_internships = internships.filter(status='completed', student_rating__isnull=False)
        if completed_internships.exists():
            self.average_rating = completed_internships.aggregate(
                avg=models.Avg('student_rating')
            )['avg'] or 0.0
        
        self.save(update_fields=['total_internships', 'average_rating'])


class InternshipOffer(models.Model):
    """
    Modèle pour les offres de stage
    """
    OFFER_TYPES = [
        ('observation', 'Stage d\'observation'),
        ('discovery', 'Stage de découverte'),
        ('practical', 'Stage pratique'),
        ('project', 'Stage projet'),
        ('research', 'Stage recherche'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
        ('filled', 'Pourvu'),
        ('expired', 'Expiré'),
        ('cancelled', 'Annulé'),
    ]
    
    DURATION_TYPES = [
        ('days', 'Jours'),
        ('weeks', 'Semaines'),
        ('months', 'Mois'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='offers')
    
    # Informations de base
    title = models.CharField(max_length=200)
    description = models.TextField()
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPES, default='practical')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Durée et dates
    duration_value = models.PositiveIntegerField(help_text="Durée du stage")
    duration_type = models.CharField(max_length=10, choices=DURATION_TYPES, default='weeks')
    start_date = models.DateField()
    end_date = models.DateField()
    application_deadline = models.DateField()
    
    # Détails du poste
    department = models.CharField(max_length=100, blank=True)
    supervisor_name = models.CharField(max_length=100, blank=True)
    supervisor_email = models.EmailField(blank=True)
    supervisor_phone = models.CharField(max_length=20, blank=True)
    
    # Exigences
    required_level = models.CharField(max_length=50, help_text="Niveau d'études requis")
    required_skills = models.JSONField(default=list, blank=True, help_text="Compétences requises")
    preferred_skills = models.JSONField(default=list, blank=True, help_text="Compétences souhaitées")
    
    # Conditions
    is_paid = models.BooleanField(default=False)
    monthly_allowance = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    benefits = models.JSONField(default=list, blank=True, help_text="Avantages offerts")
    
    # Logistique
    remote_possible = models.BooleanField(default=False)
    transport_provided = models.BooleanField(default=False)
    meal_vouchers = models.BooleanField(default=False)
    accommodation_help = models.BooleanField(default=False)
    
    # Candidatures
    max_applications = models.PositiveIntegerField(default=1, help_text="Nombre maximum de stagiaires")
    current_applications = models.PositiveIntegerField(default=0)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'start_date']),
            models.Index(fields=['company', 'status']),
            models.Index(fields=['application_deadline']),
            models.Index(fields=['-published_at']),
        ]
        
    def __str__(self):
        return f"{self.title} - {self.company.name}"
    
    def clean(self):
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError("La date de fin doit être postérieure à la date de début")
        
        if self.application_deadline and self.start_date:
            if self.application_deadline >= self.start_date:
                raise ValidationError("La date limite de candidature doit être antérieure au début du stage")
    
    def is_expired(self):
        """Vérifie si l'offre a expiré"""
        return self.application_deadline < timezone.now().date()
    
    def is_full(self):
        """Vérifie si l'offre est complète"""
        return self.current_applications >= self.max_applications
    
    def can_apply(self):
        """Vérifie si on peut encore candidater"""
        return (
            self.status == 'published' and 
            not self.is_expired() and 
            not self.is_full()
        )
    
    def publish(self):
        """Publie l'offre"""
        self.status = 'published'
        self.published_at = timezone.now()
        self.save()


class InternshipApplication(models.Model):
    """
    Modèle pour les candidatures de stage
    """
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('submitted', 'Soumise'),
        ('under_review', 'En cours d\'examen'),
        ('interview_scheduled', 'Entretien programmé'),
        ('accepted', 'Acceptée'),
        ('rejected', 'Refusée'),
        ('withdrawn', 'Retirée'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='internship_applications')
    offer = models.ForeignKey(InternshipOffer, on_delete=models.CASCADE, related_name='applications')
    
    # Statut et dates
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    response_at = models.DateTimeField(null=True, blank=True)
    
    # Documents
    cover_letter = models.TextField(help_text="Lettre de motivation")
    cv_file = models.FileField(upload_to='internships/cvs/', null=True, blank=True)
    portfolio_url = models.URLField(blank=True)
    additional_documents = models.JSONField(default=list, blank=True)
    
    # Informations complémentaires
    motivation = models.TextField(blank=True, help_text="Motivation spécifique pour ce stage")
    availability_notes = models.TextField(blank=True)
    special_requirements = models.TextField(blank=True)
    
    # Suivi par l'entreprise
    company_notes = models.TextField(blank=True, help_text="Notes internes de l'entreprise")
    interview_date = models.DateTimeField(null=True, blank=True)
    interview_notes = models.TextField(blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-submitted_at', '-created_at']
        unique_together = ['student', 'offer']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['offer', 'status']),
            models.Index(fields=['-submitted_at']),
        ]
        
    def __str__(self):
        return f"{self.student.get_full_name()} -> {self.offer.title}"
    
    def submit(self):
        """Soumet la candidature"""
        if self.status == 'draft':
            self.status = 'submitted'
            self.submitted_at = timezone.now()
            self.save()
            
            # Incrémenter le compteur de candidatures de l'offre
            self.offer.current_applications += 1
            self.offer.save()
    
    def accept(self):
        """Accepte la candidature"""
        self.status = 'accepted'
        self.response_at = timezone.now()
        self.save()
    
    def reject(self, notes=None):
        """Rejette la candidature"""
        self.status = 'rejected'
        self.response_at = timezone.now()
        if notes:
            self.company_notes = notes
        self.save()


class Internship(models.Model):
    """
    Modèle pour les stages effectifs (une fois acceptés)
    """
    STATUS_CHOICES = [
        ('upcoming', 'À venir'),
        ('ongoing', 'En cours'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
        ('interrupted', 'Interrompu'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    application = models.OneToOneField(InternshipApplication, on_delete=models.CASCADE, related_name='internship')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='internships')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='internships')
    
    # Superviseurs
    academic_supervisor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='supervised_internships', help_text="Tuteur académique"
    )
    company_supervisor = models.CharField(max_length=100, help_text="Tuteur en entreprise")
    company_supervisor_email = models.EmailField()
    
    # Dates et durée
    start_date = models.DateField()
    end_date = models.DateField()
    actual_start_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)
    
    # Statut et progression
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    progress_percentage = models.PositiveIntegerField(
        default=0, validators=[MaxValueValidator(100)]
    )
    
    # Évaluations
    student_rating = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Note donnée par l'étudiant (1-5)"
    )
    company_rating = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Note donnée par l'entreprise (1-5)"
    )
    
    # Documents et rapports
    internship_agreement = models.FileField(upload_to='internships/agreements/', null=True, blank=True)
    final_report = models.FileField(upload_to='internships/reports/', null=True, blank=True)
    company_evaluation = models.FileField(upload_to='internships/evaluations/', null=True, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['company', 'status']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['academic_supervisor']),
        ]
        
    def __str__(self):
        return f"Stage {self.student.get_full_name()} chez {self.company.name}"
    
    def clean(self):
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError("La date de fin doit être postérieure à la date de début")
    
    def update_status(self):
        """Met à jour automatiquement le statut basé sur les dates"""
        today = timezone.now().date()
        
        if self.actual_start_date:
            start_date = self.actual_start_date
        else:
            start_date = self.start_date
            
        if self.actual_end_date:
            end_date = self.actual_end_date
        else:
            end_date = self.end_date
        
        if today < start_date:
            self.status = 'upcoming'
        elif start_date <= today <= end_date:
            self.status = 'ongoing'
        elif today > end_date:
            self.status = 'completed'
        
        self.save(update_fields=['status'])
    
    def calculate_progress(self):
        """Calcule le pourcentage de progression"""
        if self.status not in ['ongoing', 'completed']:
            return 0
        
        today = timezone.now().date()
        start_date = self.actual_start_date or self.start_date
        end_date = self.actual_end_date or self.end_date
        
        total_days = (end_date - start_date).days
        elapsed_days = (today - start_date).days
        
        if total_days <= 0:
            return 100
        
        progress = min(100, max(0, int((elapsed_days / total_days) * 100)))
        
        if self.progress_percentage != progress:
            self.progress_percentage = progress
            self.save(update_fields=['progress_percentage'])
        
        return progress


class InternshipVisit(models.Model):
    """
    Modèle pour les visites de stage
    """
    VISIT_TYPES = [
        ('initial', 'Visite initiale'),
        ('midterm', 'Visite intermédiaire'),
        ('final', 'Visite finale'),
        ('problem_solving', 'Résolution de problème'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Programmée'),
        ('completed', 'Effectuée'),
        ('cancelled', 'Annulée'),
        ('rescheduled', 'Reportée'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE, related_name='visits')
    visitor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='internship_visits')
    
    # Détails de la visite
    visit_type = models.CharField(max_length=20, choices=VISIT_TYPES, default='midterm')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Planification
    scheduled_date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    location = models.CharField(max_length=200, help_text="Lieu de la visite")
    
    # Participants
    participants = models.JSONField(default=list, help_text="Liste des participants")
    
    # Rapport de visite
    visit_report = models.TextField(blank=True)
    student_feedback = models.TextField(blank=True)
    company_feedback = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    
    # Évaluation
    overall_satisfaction = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    issues_identified = models.JSONField(default=list, blank=True)
    follow_up_required = models.BooleanField(default=False)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-scheduled_date']
        indexes = [
            models.Index(fields=['internship', 'status']),
            models.Index(fields=['visitor', 'scheduled_date']),
            models.Index(fields=['visit_type']),
        ]
        
    def __str__(self):
        return f"Visite {self.get_visit_type_display()} - {self.internship}"
    
    def complete_visit(self):
        """Marque la visite comme effectuée"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()


class InternshipEvaluation(models.Model):
    """
    Modèle pour les évaluations de stage
    """
    EVALUATOR_TYPES = [
        ('student', 'Étudiant'),
        ('company', 'Entreprise'),
        ('academic', 'Superviseur académique'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE, related_name='evaluations')
    evaluator = models.ForeignKey(User, on_delete=models.CASCADE)
    evaluator_type = models.CharField(max_length=20, choices=EVALUATOR_TYPES)
    
    # Critères d'évaluation (notes de 1 à 5)
    technical_skills = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    soft_skills = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    initiative = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    reliability = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    communication = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Note globale
    overall_rating = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Commentaires
    strengths = models.TextField(help_text="Points forts")
    areas_for_improvement = models.TextField(help_text="Axes d'amélioration")
    general_comments = models.TextField(blank=True)
    
    # Recommandations
    would_recommend_student = models.BooleanField(null=True, blank=True)
    would_recommend_company = models.BooleanField(null=True, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['internship', 'evaluator_type']
        indexes = [
            models.Index(fields=['internship', 'evaluator_type']),
            models.Index(fields=['overall_rating']),
        ]
        
    def __str__(self):
        return f"Évaluation {self.get_evaluator_type_display()} - {self.internship}"
    
    def save(self, *args, **kwargs):
        # Calculer la note globale comme moyenne des critères
        self.overall_rating = (
            self.technical_skills + self.soft_skills + self.initiative +
            self.reliability + self.communication
        ) / 5
        super().save(*args, **kwargs)