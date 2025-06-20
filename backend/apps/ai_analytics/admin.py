"""
Administration Django pour le module d'analyse IA et détection des risques
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    RiskProfile, RiskIndicator, InterventionPlan,
    InterventionAction, AlertConfiguration, Alert
)


@admin.register(RiskProfile)
class RiskProfileAdmin(admin.ModelAdmin):
    """Administration des profils de risque"""
    list_display = [
        'student_name', 'risk_level_badge', 'risk_score', 
        'academic_year', 'is_monitored', 'last_analysis'
    ]
    list_filter = [
        'risk_level', 'is_monitored', 'academic_year',
        'last_analysis', 'created_at'
    ]
    search_fields = ['student__first_name', 'student__last_name']
    readonly_fields = [
        'risk_score', 'risk_level', 'academic_risk', 'attendance_risk',
        'behavioral_risk', 'social_risk', 'risk_factors', 'indicators',
        'dropout_probability', 'predicted_final_average', 'recommendations',
        'priority_actions', 'last_analysis', 'analysis_version'
    ]
    fieldsets = (
        ('Élève', {
            'fields': ('student', 'academic_year')
        }),
        ('Scores de risque', {
            'fields': (
                'risk_score', 'risk_level', 'academic_risk',
                'attendance_risk', 'behavioral_risk', 'social_risk'
            ),
            'classes': ('collapse',)
        }),
        ('Analyse détaillée', {
            'fields': (
                'risk_factors', 'indicators', 'dropout_probability',
                'predicted_final_average'
            ),
            'classes': ('collapse',)
        }),
        ('Recommandations', {
            'fields': ('recommendations', 'priority_actions'),
            'classes': ('collapse',)
        }),
        ('Surveillance', {
            'fields': (
                'is_monitored', 'monitoring_started', 'assigned_to'
            )
        }),
        ('Métadonnées', {
            'fields': ('last_analysis', 'analysis_version'),
            'classes': ('collapse',)
        })
    )
    
    def student_name(self, obj):
        return obj.student.get_full_name()
    student_name.short_description = 'Élève'
    
    def risk_level_badge(self, obj):
        colors = {
            'very_low': 'green',
            'low': 'lightgreen',
            'moderate': 'orange',
            'high': 'red',
            'critical': 'darkred'
        }
        color = colors.get(obj.risk_level, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 6px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_risk_level_display()
        )
    risk_level_badge.short_description = 'Niveau de risque'
    
    actions = ['start_monitoring', 'stop_monitoring']
    
    def start_monitoring(self, request, queryset):
        count = 0
        for profile in queryset:
            if not profile.is_monitored:
                profile.start_monitoring()
                count += 1
        self.message_user(request, f'{count} profils mis sous surveillance.')
    start_monitoring.short_description = 'Démarrer la surveillance'
    
    def stop_monitoring(self, request, queryset):
        count = queryset.filter(is_monitored=True).update(
            is_monitored=False,
            monitoring_started=None,
            assigned_to=None
        )
        self.message_user(request, f'{count} profils retirés de la surveillance.')
    stop_monitoring.short_description = 'Arrêter la surveillance'


@admin.register(RiskIndicator)
class RiskIndicatorAdmin(admin.ModelAdmin):
    """Administration des indicateurs de risque"""
    list_display = [
        'name', 'indicator_type', 'threshold_value', 
        'threshold_operator', 'weight', 'is_active'
    ]
    list_filter = ['indicator_type', 'is_active', 'threshold_operator']
    search_fields = ['name', 'description']
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'indicator_type', 'description', 'is_active')
        }),
        ('Configuration du seuil', {
            'fields': ('threshold_value', 'threshold_operator', 'weight')
        }),
        ('Ciblage', {
            'fields': ('applies_to_levels',)
        }),
        ('Requête personnalisée', {
            'fields': ('custom_query',),
            'classes': ('collapse',),
            'description': 'Attention: Code Python exécuté directement. Réservé aux développeurs.'
        })
    )


class InterventionActionInline(admin.TabularInline):
    """Inline pour les actions d'intervention"""
    model = InterventionAction
    extra = 0
    fields = [
        'action_type', 'title', 'responsible', 'scheduled_date',
        'completed', 'impact_assessment'
    ]
    readonly_fields = ['completed_date']


@admin.register(InterventionPlan)
class InterventionPlanAdmin(admin.ModelAdmin):
    """Administration des plans d'intervention"""
    list_display = [
        'title', 'student_name', 'status_badge', 'coordinator',
        'start_date', 'effectiveness_score'
    ]
    list_filter = ['status', 'start_date', 'coordinator']
    search_fields = ['title', 'risk_profile__student__first_name', 'risk_profile__student__last_name']
    inlines = [InterventionActionInline]
    
    fieldsets = (
        ('Plan d\'intervention', {
            'fields': ('risk_profile', 'title', 'description', 'status')
        }),
        ('Équipe', {
            'fields': ('coordinator', 'participants')
        }),
        ('Planification', {
            'fields': (
                'start_date', 'end_date', 'actual_end_date',
                'evaluation_frequency'
            )
        }),
        ('Objectifs et actions', {
            'fields': ('objectives', 'planned_actions', 'resources_needed'),
            'classes': ('collapse',)
        }),
        ('Évaluation', {
            'fields': (
                'success_criteria', 'outcomes', 'effectiveness_score'
            ),
            'classes': ('collapse',)
        })
    )
    
    def student_name(self, obj):
        return obj.risk_profile.student.get_full_name()
    student_name.short_description = 'Élève'
    
    def status_badge(self, obj):
        colors = {
            'draft': 'gray',
            'active': 'green',
            'completed': 'blue',
            'cancelled': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 6px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Statut'


@admin.register(InterventionAction)
class InterventionActionAdmin(admin.ModelAdmin):
    """Administration des actions d'intervention"""
    list_display = [
        'title', 'intervention_plan', 'action_type',
        'responsible', 'scheduled_date', 'completed_badge'
    ]
    list_filter = ['action_type', 'completed', 'scheduled_date', 'responsible']
    search_fields = ['title', 'intervention_plan__title']
    
    def completed_badge(self, obj):
        if obj.completed:
            return format_html(
                '<span style="background-color: green; color: white; padding: 3px 6px; '
                'border-radius: 3px; font-size: 11px;">✓ Terminé</span>'
            )
        else:
            return format_html(
                '<span style="background-color: orange; color: white; padding: 3px 6px; '
                'border-radius: 3px; font-size: 11px;">En attente</span>'
            )
    completed_badge.short_description = 'État'


@admin.register(AlertConfiguration)
class AlertConfigurationAdmin(admin.ModelAdmin):
    """Administration des configurations d'alerte"""
    list_display = [
        'name', 'alert_type', 'priority', 'is_active',
        'risk_level_threshold', 'cooldown_days'
    ]
    list_filter = ['alert_type', 'priority', 'is_active', 'risk_level_threshold']
    search_fields = ['name', 'description']
    
    fieldsets = (
        ('Configuration de base', {
            'fields': ('name', 'alert_type', 'description', 'is_active', 'priority')
        }),
        ('Conditions de déclenchement', {
            'fields': (
                'risk_level_threshold', 'risk_score_threshold',
                'indicator_conditions', 'cooldown_days'
            )
        }),
        ('Destinataires', {
            'fields': (
                'notify_student', 'notify_parents', 'notify_main_teacher',
                'notify_administration', 'additional_recipients'
            )
        }),
        ('Message', {
            'fields': ('message_template',),
            'description': 'Variables disponibles: {student_name}, {risk_level}, {risk_score}'
        })
    )


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    """Administration des alertes"""
    list_display = [
        'title', 'student_name', 'priority_badge', 'created_at',
        'acknowledged_badge', 'acknowledged_by'
    ]
    list_filter = [
        'priority', 'is_acknowledged', 'created_at',
        'alert_configuration__alert_type'
    ]
    search_fields = ['title', 'risk_profile__student__first_name', 'risk_profile__student__last_name']
    readonly_fields = ['risk_profile', 'alert_configuration', 'context_data', 'notifications_sent']
    
    fieldsets = (
        ('Alerte', {
            'fields': ('risk_profile', 'alert_configuration', 'title', 'message', 'priority')
        }),
        ('État', {
            'fields': (
                'is_read', 'read_by', 'is_acknowledged',
                'acknowledged_by', 'acknowledged_at', 'actions_taken'
            )
        }),
        ('Données contextuelles', {
            'fields': ('context_data', 'notifications_sent'),
            'classes': ('collapse',)
        })
    )
    
    def student_name(self, obj):
        return obj.risk_profile.student.get_full_name()
    student_name.short_description = 'Élève'
    
    def priority_badge(self, obj):
        colors = {
            'low': 'lightgray',
            'normal': 'blue',
            'high': 'orange',
            'urgent': 'red'
        }
        color = colors.get(obj.priority, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 6px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priorité'
    
    def acknowledged_badge(self, obj):
        if obj.is_acknowledged:
            return format_html(
                '<span style="background-color: green; color: white; padding: 3px 6px; '
                'border-radius: 3px; font-size: 11px;">✓ Traitée</span>'
            )
        else:
            return format_html(
                '<span style="background-color: red; color: white; padding: 3px 6px; '
                'border-radius: 3px; font-size: 11px;">⚠ En attente</span>'
            )
    acknowledged_badge.short_description = 'Statut'
    
    actions = ['mark_acknowledged']
    
    def mark_acknowledged(self, request, queryset):
        count = 0
        for alert in queryset:
            if not alert.is_acknowledged:
                alert.acknowledge(request.user, 'Marquée comme traitée via admin')
                count += 1
        self.message_user(request, f'{count} alertes marquées comme traitées.')
    mark_acknowledged.short_description = 'Marquer comme traitées'


# Configuration du site admin
admin.site.site_header = "Administration - Détection des risques"
admin.site.site_title = "Analyse IA"
admin.site.index_title = "Gestion de la détection des risques"