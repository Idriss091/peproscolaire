"""
Serializers pour l'API de gestion des tenants
"""
from rest_framework import serializers
from .models import Tenant, TenantDomain, TenantSettings
from apps.schools.models import School
from apps.schools.serializers import SchoolSerializer


class TenantDomainSerializer(serializers.ModelSerializer):
    """
    Serializer pour les domaines alternatifs d'un tenant
    """
    class Meta:
        model = TenantDomain
        fields = ['id', 'domain', 'is_primary', 'created_at']
        read_only_fields = ['created_at']


class TenantSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer pour les paramètres d'un tenant
    """
    class Meta:
        model = TenantSettings
        fields = [
            'enable_email_notifications',
            'enable_sms_notifications',
            'password_min_length',
            'session_timeout_minutes',
            'timezone',
            'language',
            'date_format',
            'time_format'
        ]


class TenantSerializer(serializers.ModelSerializer):
    """
    Serializer principal pour les tenants
    """
    school = SchoolSerializer(read_only=True)
    school_id = serializers.PrimaryKeyRelatedField(
        queryset=School.objects.all(),
        source='school',
        write_only=True
    )
    domains = TenantDomainSerializer(many=True, read_only=True)
    settings = TenantSettingsSerializer(read_only=True)
    storage_usage_gb = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tenant
        fields = [
            'id',
            'schema_name',
            'domain_url',
            'school',
            'school_id',
            'primary_color',
            'secondary_color',
            'logo_url',
            'favicon_url',
            'is_active',
            'created_on',
            'max_students',
            'max_storage_gb',
            'modules_enabled',
            'provisioned_at',
            'last_accessed_at',
            'domains',
            'settings',
            'storage_usage_gb',
            'student_count'
        ]
        read_only_fields = [
            'id',
            'schema_name',
            'created_on',
            'provisioned_at',
            'last_accessed_at',
            'storage_usage_gb',
            'student_count'
        ]
    
    def get_storage_usage_gb(self, obj):
        """
        Calcule l'espace de stockage utilisé
        """
        try:
            from .storage import tenant_storage
            from .utils import execute_on_tenant
            return execute_on_tenant(obj, tenant_storage.get_tenant_usage_gb)
        except:
            return 0
    
    def get_student_count(self, obj):
        """
        Compte le nombre d'élèves dans le tenant
        """
        try:
            from apps.authentication.models import User
            from .utils import execute_on_tenant
            return execute_on_tenant(
                obj,
                lambda: User.objects.filter(user_type='student').count()
            )
        except:
            return 0
    
    def validate_domain_url(self, value):
        """
        Valide le format du domaine
        """
        import re
        if not re.match(r'^[a-z0-9.-]+\.[a-z]{2,}$', value.lower()):
            raise serializers.ValidationError(
                "Le domaine doit être au format: sous-domaine.domaine.extension"
            )
        return value.lower()
    
    def validate_modules_enabled(self, value):
        """
        Valide la structure des modules activés
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Les modules doivent être un dictionnaire"
            )
        
        # Modules valides
        valid_modules = [
            'authentication', 'schools', 'timetable', 'attendance',
            'grades', 'homework', 'messaging', 'student_records',
            'ai_analytics'
        ]
        
        for module, enabled in value.items():
            if module not in valid_modules:
                raise serializers.ValidationError(
                    f"Module invalide: {module}"
                )
            if not isinstance(enabled, bool):
                raise serializers.ValidationError(
                    f"La valeur du module {module} doit être un booléen"
                )
        
        return value


class TenantCreateSerializer(serializers.Serializer):
    """
    Serializer pour la création d'un nouveau tenant avec école
    """
    # Informations de l'école
    school_name = serializers.CharField(max_length=200)
    school_type = serializers.ChoiceField(choices=School.SCHOOL_TYPE_CHOICES)
    address = serializers.CharField()
    postal_code = serializers.RegexField(
        regex=r'^\d{5}$',
        error_messages={'invalid': 'Code postal invalide'}
    )
    city = serializers.CharField(max_length=100)
    phone = serializers.RegexField(
        regex=r'^0[1-9]\d{8}$',
        error_messages={'invalid': 'Numéro de téléphone invalide'}
    )
    email = serializers.EmailField()
    website = serializers.URLField(required=False, allow_blank=True)
    
    # Informations du tenant
    subdomain = serializers.RegexField(
        regex=r'^[a-z0-9-]+$',
        error_messages={'invalid': 'Le sous-domaine ne doit contenir que des lettres minuscules, chiffres et tirets'}
    )
    primary_color = serializers.RegexField(
        regex=r'^#[0-9A-Fa-f]{6}$',
        default='#1976D2',
        error_messages={'invalid': 'La couleur doit être au format hexadécimal'}
    )
    secondary_color = serializers.RegexField(
        regex=r'^#[0-9A-Fa-f]{6}$',
        default='#424242',
        error_messages={'invalid': 'La couleur doit être au format hexadécimal'}
    )
    max_students = serializers.IntegerField(default=1000, min_value=1)
    max_storage_gb = serializers.IntegerField(default=50, min_value=1)
    
    # Options
    provision_now = serializers.BooleanField(default=False)
    
    def validate_subdomain(self, value):
        """
        Vérifie que le sous-domaine est unique
        """
        domain_url = f"{value}.peproscolaire.fr"
        if Tenant.objects.filter(domain_url=domain_url).exists():
            raise serializers.ValidationError(
                f"Le sous-domaine {value} est déjà utilisé"
            )
        return value
    
    def create(self, validated_data):
        """
        Crée l'école et le tenant
        """
        from django.db import transaction
        from .utils import provision_tenant
        
        # Extraire les données
        school_data = {
            'name': validated_data.pop('school_name'),
            'school_type': validated_data.pop('school_type'),
            'address': validated_data.pop('address'),
            'postal_code': validated_data.pop('postal_code'),
            'city': validated_data.pop('city'),
            'phone': validated_data.pop('phone'),
            'email': validated_data.pop('email'),
            'website': validated_data.pop('website', ''),
            'subdomain': validated_data['subdomain']
        }
        
        provision_now = validated_data.pop('provision_now', False)
        subdomain = validated_data.pop('subdomain')
        
        with transaction.atomic():
            # Créer l'école
            school = School.objects.create(**school_data)
            
            # Créer le tenant
            tenant = Tenant.objects.create(
                schema_name=subdomain.replace('-', '_'),
                domain_url=f"{subdomain}.peproscolaire.fr",
                school=school,
                **validated_data
            )
            
            # Provisionner si demandé
            if provision_now:
                provision_tenant(tenant)
        
        return tenant


class TenantStatsSerializer(serializers.Serializer):
    """
    Serializer pour les statistiques d'un tenant
    """
    tenant_id = serializers.UUIDField()
    tenant_name = serializers.CharField()
    domain_url = serializers.CharField()
    is_active = serializers.BooleanField()
    
    # Statistiques utilisateurs
    total_users = serializers.IntegerField()
    student_count = serializers.IntegerField()
    teacher_count = serializers.IntegerField()
    parent_count = serializers.IntegerField()
    admin_count = serializers.IntegerField()
    
    # Statistiques de stockage
    storage_used_gb = serializers.FloatField()
    storage_limit_gb = serializers.IntegerField()
    storage_percentage = serializers.FloatField()
    
    # Statistiques d'utilisation
    last_accessed = serializers.DateTimeField(allow_null=True)
    days_since_last_access = serializers.IntegerField(allow_null=True)
    
    # Modules
    active_modules = serializers.ListField(child=serializers.CharField())
    inactive_modules = serializers.ListField(child=serializers.CharField())