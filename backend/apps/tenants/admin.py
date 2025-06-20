"""
Configuration de l'interface d'administration Django pour les tenants
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Tenant, TenantDomain, TenantSettings


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """
    Administration des tenants
    """
    list_display = [
        'school_name',
        'domain_link',
        'schema_name',
        'is_active_badge',
        'student_quota',
        'storage_quota',
        'provisioned_status',
        'created_on'
    ]
    
    list_filter = [
        'is_active',
        'school__school_type',
        'created_on',
        'provisioned_at'
    ]
    
    search_fields = [
        'school__name',
        'domain_url',
        'schema_name'
    ]
    
    readonly_fields = [
        'id',
        'schema_name',
        'created_on',
        'provisioned_at',
        'last_accessed_at',
        'color_preview'
    ]
    
    fieldsets = (
        ('Informations principales', {
            'fields': (
                'id',
                'school',
                'domain_url',
                'schema_name',
                'is_active'
            )
        }),
        ('Personnalisation', {
            'fields': (
                'primary_color',
                'secondary_color',
                'color_preview',
                'logo_url',
                'favicon_url'
            )
        }),
        ('Limites et quotas', {
            'fields': (
                'max_students',
                'max_storage_gb'
            )
        }),
        ('Modules', {
            'fields': ('modules_enabled',),
            'classes': ('wide',)
        }),
        ('Métadonnées', {
            'fields': (
                'created_on',
                'provisioned_at',
                'last_accessed_at'
            )
        })
    )
    
    actions = [
        'activate_tenants',
        'deactivate_tenants',
        'provision_tenants'
    ]
    
    def school_name(self, obj):
        """Affiche le nom de l'école"""
        return obj.school.name
    school_name.short_description = 'École'
    school_name.admin_order_field = 'school__name'
    
    def domain_link(self, obj):
        """Affiche le domaine avec un lien"""
        return format_html(
            '<a href="https://{}" target="_blank">{}</a>',
            obj.domain_url,
            obj.domain_url
        )
    domain_link.short_description = 'Domaine'
    
    def is_active_badge(self, obj):
        """Badge pour le statut actif"""
        if obj.is_active:
            return format_html(
                '<span style="color: green;">✓ Actif</span>'
            )
        return format_html(
            '<span style="color: red;">✗ Inactif</span>'
        )
    is_active_badge.short_description = 'Statut'
    
    def student_quota(self, obj):
        """Affiche le quota d'élèves"""
        # TODO: Compter les élèves réels
        return f"0/{obj.max_students}"
    student_quota.short_description = 'Élèves'
    
    def storage_quota(self, obj):
        """Affiche le quota de stockage"""
        # TODO: Calculer l'utilisation réelle
        return f"0/{obj.max_storage_gb} GB"
    storage_quota.short_description = 'Stockage'
    
    def provisioned_status(self, obj):
        """Statut de provisionnement"""
        if obj.provisioned_at:
            return format_html(
                '<span style="color: green;">✓ Provisionné</span>'
            )
        return format_html(
            '<span style="color: orange;">⚠ Non provisionné</span>'
        )
    provisioned_status.short_description = 'Provisionnement'
    
    def color_preview(self, obj):
        """Aperçu des couleurs"""
        return format_html(
            '<div style="display: flex; gap: 10px;">'
            '<div style="width: 50px; height: 30px; background-color: {}; border: 1px solid #ccc;"></div>'
            '<div style="width: 50px; height: 30px; background-color: {}; border: 1px solid #ccc;"></div>'
            '</div>',
            obj.primary_color,
            obj.secondary_color
        )
    color_preview.short_description = 'Aperçu des couleurs'
    
    def activate_tenants(self, request, queryset):
        """Action pour activer les tenants sélectionnés"""
        count = queryset.update(is_active=True)
        self.message_user(
            request,
            f"{count} tenant(s) activé(s) avec succès."
        )
    activate_tenants.short_description = "Activer les tenants sélectionnés"
    
    def deactivate_tenants(self, request, queryset):
        """Action pour désactiver les tenants sélectionnés"""
        count = queryset.update(is_active=False)
        self.message_user(
            request,
            f"{count} tenant(s) désactivé(s) avec succès."
        )
    deactivate_tenants.short_description = "Désactiver les tenants sélectionnés"
    
    def provision_tenants(self, request, queryset):
        """Action pour provisionner les tenants sélectionnés"""
        from .utils import provision_tenant
        
        success_count = 0
        error_count = 0
        
        for tenant in queryset.filter(provisioned_at__isnull=True):
            try:
                provision_tenant(tenant)
                success_count += 1
            except Exception as e:
                error_count += 1
                self.message_user(
                    request,
                    f"Erreur lors du provisionnement de {tenant.domain_url}: {str(e)}",
                    level='ERROR'
                )
        
        if success_count > 0:
            self.message_user(
                request,
                f"{success_count} tenant(s) provisionné(s) avec succès."
            )
        
        if error_count > 0:
            self.message_user(
                request,
                f"{error_count} erreur(s) lors du provisionnement.",
                level='WARNING'
            )
    provision_tenants.short_description = "Provisionner les tenants sélectionnés"


@admin.register(TenantDomain)
class TenantDomainAdmin(admin.ModelAdmin):
    """
    Administration des domaines alternatifs
    """
    list_display = [
        'domain',
        'tenant_name',
        'is_primary',
        'created_at'
    ]
    
    list_filter = [
        'is_primary',
        'created_at'
    ]
    
    search_fields = [
        'domain',
        'tenant__school__name'
    ]
    
    def tenant_name(self, obj):
        """Nom du tenant"""
        return obj.tenant.school.name
    tenant_name.short_description = 'Tenant'
    tenant_name.admin_order_field = 'tenant__school__name'


@admin.register(TenantSettings)
class TenantSettingsAdmin(admin.ModelAdmin):
    """
    Administration des paramètres des tenants
    """
    list_display = [
        'tenant_name',
        'email_notifications',
        'sms_notifications',
        'timezone',
        'language'
    ]
    
    list_filter = [
        'enable_email_notifications',
        'enable_sms_notifications',
        'timezone',
        'language'
    ]
    
    search_fields = [
        'tenant__school__name'
    ]
    
    fieldsets = (
        ('Tenant', {
            'fields': ('tenant',)
        }),
        ('Notifications', {
            'fields': (
                'enable_email_notifications',
                'enable_sms_notifications'
            )
        }),
        ('Sécurité', {
            'fields': (
                'password_min_length',
                'session_timeout_minutes'
            )
        }),
        ('Régionalisation', {
            'fields': (
                'timezone',
                'language',
                'date_format',
                'time_format'
            )
        })
    )
    
    def tenant_name(self, obj):
        """Nom du tenant"""
        return obj.tenant.school.name
    tenant_name.short_description = 'Tenant'
    
    def email_notifications(self, obj):
        """Statut des notifications email"""
        return '✓' if obj.enable_email_notifications else '✗'
    email_notifications.short_description = 'Email'
    
    def sms_notifications(self, obj):
        """Statut des notifications SMS"""
        return '✓' if obj.enable_sms_notifications else '✗'
    sms_notifications.short_description = 'SMS'