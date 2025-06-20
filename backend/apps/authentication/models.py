"""
Modèles pour l'authentification et la gestion des utilisateurs
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
import uuid

class User(AbstractUser):
    """
    Modèle utilisateur personnalisé étendant AbstractUser
    Gère tous les types d'utilisateurs : élèves, parents, professeurs, administration
    """
    
    # Types d'utilisateurs
    USER_TYPE_CHOICES = [
        ('student', 'Élève'),
        ('parent', 'Parent'),
        ('teacher', 'Professeur'),
        ('admin', 'Administration'),
        ('superadmin', 'Super Admin'),
    ]
    
    # UUID pour plus de sécurité
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Type d'utilisateur
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='student',
        verbose_name=_("Type d'utilisateur")
    )
    
    # Email unique et obligatoire
    email = models.EmailField(
        unique=True,
        verbose_name=_("Adresse email")
    )
    
    # Numéro de téléphone avec validation
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Le numéro de téléphone doit être au format: '+33612345678'"
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        verbose_name=_("Numéro de téléphone")
    )
    
    # Champs supplémentaires
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_("Email vérifié")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Configuration
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        verbose_name = _("Utilisateur")
        verbose_name_plural = _("Utilisateurs")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.user_type})"
    
    def get_full_name(self):
        """Retourne le nom complet de l'utilisateur"""
        return f"{self.first_name} {self.last_name}".strip() or self.email


class UserProfile(models.Model):
    """
    Profil utilisateur étendu pour stocker des informations supplémentaires
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    # Photo de profil
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name=_("Photo de profil")
    )
    
    # Date de naissance (importante pour les élèves)
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Date de naissance")
    )
    
    # Adresse
    address = models.TextField(
        blank=True,
        verbose_name=_("Adresse")
    )
    postal_code = models.CharField(
        max_length=10,
        blank=True,
        verbose_name=_("Code postal")
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Ville")
    )
    
    # Informations de contact d'urgence
    emergency_contact_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Contact d'urgence - Nom")
    )
    emergency_contact_phone = models.CharField(
        max_length=17,
        blank=True,
        verbose_name=_("Contact d'urgence - Téléphone")
    )
    
    # Préférences
    email_notifications = models.BooleanField(
        default=True,
        verbose_name=_("Notifications par email")
    )
    sms_notifications = models.BooleanField(
        default=False,
        verbose_name=_("Notifications par SMS")
    )
    
    # Métadonnées
    bio = models.TextField(
        blank=True,
        verbose_name=_("Biographie")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = _("Profil utilisateur")
        verbose_name_plural = _("Profils utilisateurs")
    
    def __str__(self):
        return f"Profil de {self.user.get_full_name()}"


class PasswordResetToken(models.Model):
    """
    Token de réinitialisation de mot de passe
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens'
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'password_reset_tokens'
        verbose_name = _("Token de réinitialisation")
        verbose_name_plural = _("Tokens de réinitialisation")
        ordering = ['-created_at']
    
    def is_expired(self):
        """Vérifie si le token a expiré (24h)"""
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() > self.created_at + timedelta(hours=24)