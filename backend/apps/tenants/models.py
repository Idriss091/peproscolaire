"""
Modèles pour la gestion multi-tenant
"""
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel


class Tenant(BaseModel):
    """
    Modèle représentant un tenant (établissement) avec ses configurations
    """
    # Identification
    schema_name = models.CharField(
        max_length=63, 
        unique=True,
        validators=[
            RegexValidator(
                regex='^[a-z][a-z0-9_]*$',
                message='Le nom du schéma doit commencer par une lettre minuscule et ne contenir que des lettres minuscules, chiffres et underscores'
            )
        ],
        help_text="Nom du schéma PostgreSQL (ex: lycee_morvan)"
    )
    
    domain_url = models.CharField(
        max_length=128, 
        unique=True,
        help_text="URL complète du sous-domaine (ex: lycee-morvan.peproscolaire.fr)"
    )
    
    # Référence à l'établissement
    school = models.OneToOneField(
        'schools.School', 
        on_delete=models.CASCADE,
        related_name='tenant'
    )
    
    # Personnalisation
    primary_color = models.CharField(
        max_length=7, 
        default='#1976D2',
        validators=[
            RegexValidator(
                regex='^#[0-9A-Fa-f]{6}$',
                message='La couleur doit être au format hexadécimal (ex: #1976D2)'
            )
        ],
        help_text="Couleur principale de l'interface"
    )
    
    secondary_color = models.CharField(
        max_length=7, 
        default='#424242',
        validators=[
            RegexValidator(
                regex='^#[0-9A-Fa-f]{6}$',
                message='La couleur doit être au format hexadécimal (ex: #424242)'
            )
        ],
        help_text="Couleur secondaire de l'interface"
    )
    
    logo_url = models.URLField(
        blank=True,
        help_text="URL du logo de l'établissement"
    )
    
    favicon_url = models.URLField(
        blank=True,
        help_text="URL du favicon de l'établissement"
    )
    
    # Configuration
    is_active = models.BooleanField(
        default=True,
        help_text="Indique si le tenant est actif"
    )
    
    created_on = models.DateField(
        auto_now_add=True
    )
    
    # Limites et quotas
    max_students = models.IntegerField(
        default=1000,
        help_text="Nombre maximum d'élèves autorisés"
    )
    
    max_storage_gb = models.IntegerField(
        default=50,
        help_text="Espace de stockage maximum en GB"
    )
    
    # Modules activés
    modules_enabled = models.JSONField(
        default=dict,
        help_text="Modules activés pour ce tenant (ex: {'attendance': True, 'ai_analytics': False})"
    )
    
    # Métadonnées
    provisioned_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date de provisionnement du tenant"
    )
    
    last_accessed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Dernière date d'accès au tenant"
    )
    
    class Meta:
        db_table = 'tenants'
        verbose_name = _("Tenant")
        verbose_name_plural = _("Tenants")
        ordering = ['schema_name']
    
    def __str__(self):
        return f"{self.school.name} ({self.domain_url})"
    
    def get_default_modules(self):
        """Retourne les modules activés par défaut"""
        return {
            'authentication': True,
            'schools': True,
            'timetable': True,
            'attendance': True,
            'grades': True,
            'homework': True,
            'messaging': True,
            'student_records': True,
            'ai_analytics': False,  # Module IA désactivé par défaut
        }
    
    def save(self, *args, **kwargs):
        """Override save pour initialiser les modules si nécessaire"""
        if not self.modules_enabled:
            self.modules_enabled = self.get_default_modules()
        super().save(*args, **kwargs)
    
    def is_module_enabled(self, module_name):
        """Vérifie si un module est activé pour ce tenant"""
        return self.modules_enabled.get(module_name, False)
    
    def provision(self):
        """
        Provisionne le tenant en créant le schéma et les données initiales
        """
        from django.db import connection
        from django.core.management import call_command
        from django.utils import timezone
        
        with connection.cursor() as cursor:
            # Créer le schéma
            cursor.execute(f'CREATE SCHEMA IF NOT EXISTS {self.schema_name}')
            
            # Définir le search_path pour ce schéma
            cursor.execute(f'SET search_path TO {self.schema_name}, public')
        
        # Appliquer les migrations pour ce tenant
        call_command('migrate', schema_name=self.schema_name, verbosity=0)
        
        # Marquer comme provisionné
        self.provisioned_at = timezone.now()
        self.save()
    
    def delete_schema(self):
        """
        Supprime le schéma du tenant (ATTENTION: supprime toutes les données!)
        """
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute(f'DROP SCHEMA IF EXISTS {self.schema_name} CASCADE')


class TenantAwareModel(models.Model):
    """
    Mixin pour rendre un modèle conscient du tenant
    Tous les modèles qui doivent être isolés par tenant doivent hériter de cette classe
    """
    class Meta:
        abstract = True
        
    @classmethod
    def _get_tenant_aware_manager(cls):
        """
        Retourne un manager qui filtre automatiquement par tenant
        """
        from .managers import TenantAwareManager
        return TenantAwareManager()


class TenantDomain(BaseModel):
    """
    Domaines alternatifs pour un tenant
    Permet d'avoir plusieurs domaines pointant vers le même tenant
    """
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='domains'
    )
    
    domain = models.CharField(
        max_length=253,
        unique=True,
        help_text="Domaine alternatif (ex: lycee-morvan.ac-paris.fr)"
    )
    
    is_primary = models.BooleanField(
        default=False,
        help_text="Indique si c'est le domaine principal"
    )
    
    class Meta:
        db_table = 'tenant_domains'
        verbose_name = _("Domaine de tenant")
        verbose_name_plural = _("Domaines de tenant")
    
    def __str__(self):
        return self.domain


class TenantSettings(BaseModel):
    """
    Paramètres spécifiques au tenant
    """
    tenant = models.OneToOneField(
        Tenant,
        on_delete=models.CASCADE,
        related_name='settings'
    )
    
    # Paramètres de notification
    enable_email_notifications = models.BooleanField(
        default=True,
        help_text="Activer les notifications par email"
    )
    
    enable_sms_notifications = models.BooleanField(
        default=False,
        help_text="Activer les notifications par SMS"
    )
    
    # Paramètres de sécurité
    password_min_length = models.IntegerField(
        default=8,
        help_text="Longueur minimale des mots de passe"
    )
    
    session_timeout_minutes = models.IntegerField(
        default=60,
        help_text="Durée de session en minutes"
    )
    
    # Paramètres régionaux
    timezone = models.CharField(
        max_length=50,
        default='Europe/Paris',
        help_text="Fuseau horaire du tenant"
    )
    
    language = models.CharField(
        max_length=10,
        default='fr',
        help_text="Langue par défaut"
    )
    
    # Paramètres d'affichage
    date_format = models.CharField(
        max_length=20,
        default='%d/%m/%Y',
        help_text="Format de date"
    )
    
    time_format = models.CharField(
        max_length=20,
        default='%H:%M',
        help_text="Format d'heure"
    )
    
    class Meta:
        db_table = 'tenant_settings'
        verbose_name = _("Paramètres de tenant")
        verbose_name_plural = _("Paramètres de tenant")
    
    def __str__(self):
        return f"Paramètres de {self.tenant.school.name}"