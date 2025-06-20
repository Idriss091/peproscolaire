"""
Modèles de données pour les modules d'Intelligence Artificielle
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import json


class StudentProfile(models.Model):
    """Profil étudiant pour l'analyse IA"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    
    # Informations scolaires
    class_level = models.CharField(max_length=20, choices=[
        ('6eme', '6ème'),
        ('5eme', '5ème'),
        ('4eme', '4ème'),
        ('3eme', '3ème'),
        ('seconde', 'Seconde'),
        ('premiere', 'Première'),
        ('terminale', 'Terminale'),
    ])
    
    # Métriques pour l'IA
    current_average = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(20)])
    attendance_rate = models.FloatField(default=100.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    behavior_score = models.FloatField(default=5.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    participation_score = models.FloatField(default=3.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    homework_completion_rate = models.FloatField(default=100.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profil de {self.user.get_full_name()} ({self.class_level})"
    
    class Meta:
        verbose_name = "Profil Étudiant"
        verbose_name_plural = "Profils Étudiants"


class RiskAssessment(models.Model):
    """Évaluation du risque de décrochage"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='risk_assessments')
    
    # Score de risque calculé par l'IA
    risk_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    risk_level = models.CharField(max_length=20, choices=[
        ('low', 'Faible'),
        ('moderate', 'Modéré'),
        ('high', 'Élevé'),
        ('critical', 'Critique'),
    ])
    
    # Facteurs de risque détaillés
    risk_factors = models.JSONField(default=dict, help_text="Facteurs contribuant au risque")
    confidence_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    
    # Prédictions
    prediction_horizon_days = models.IntegerField(default=30)
    predicted_outcome = models.CharField(max_length=50, choices=[
        ('stable', 'Stable'),
        ('at_risk', 'À risque'),
        ('likely_dropout', 'Décrochage probable'),
    ])
    
    # Métadonnées
    model_version = models.CharField(max_length=20, default='1.0')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Risque {self.risk_level} - {self.student.user.get_full_name()}"
    
    class Meta:
        verbose_name = "Évaluation de Risque"
        verbose_name_plural = "Évaluations de Risque"
        ordering = ['-created_at']


class AppreciationGeneration(models.Model):
    """Génération d'appréciations par IA"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='ai_appreciations')
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='generated_appreciations')
    
    # Configuration de génération
    subject = models.CharField(max_length=100, blank=True, help_text="Matière concernée")
    appreciation_type = models.CharField(max_length=30, choices=[
        ('bulletin', 'Bulletin scolaire'),
        ('subject', 'Matière spécifique'),
        ('behavior', 'Comportement'),
        ('progress', 'Progrès'),
        ('orientation', 'Orientation'),
    ])
    
    # Paramètres IA
    tone = models.CharField(max_length=20, choices=[
        ('positive', 'Positif'),
        ('neutral', 'Neutre'),
        ('constructive', 'Constructif'),
        ('encouraging', 'Encourageant'),
    ], default='constructive')
    
    # Contenu généré
    generated_text = models.TextField()
    confidence_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    
    # Workflow de validation
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Brouillon'),
        ('reviewed', 'Relu'),
        ('approved', 'Approuvé'),
        ('published', 'Publié'),
        ('rejected', 'Rejeté'),
    ], default='draft')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Appréciation {self.appreciation_type} - {self.student.user.get_full_name()}"
    
    class Meta:
        verbose_name = "Génération d'Appréciation"
        verbose_name_plural = "Générations d'Appréciations"
        ordering = ['-created_at']
