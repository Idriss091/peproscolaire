"""
Configuration admin pour la vie scolaire
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Attendance, AbsencePeriod, Sanction,
    StudentBehavior, AttendanceAlert
)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'schedule', 'date', 'status_colored',
        'arrival_time', 'is_justified', 'recorded_by'
    ]
    list_filter = [
        'status', 'is_justified', 'date',
        'schedule__class_group', 'schedule__subject'
    ]
    search_fields = [
        'student__first_name', 'student__last_name',
        'student__email'
    ]
    date_hierarchy = 'date'
    raw_id_fields = ['student', 'schedule', 'recorded_by', 'modified_by']
    
    def status_colored(self, obj):
        colors = {
            'present': 'green',
            'absent': 'red',
            'late': 'orange',
            'excused': 'blue',
            'excluded': 'darkred'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_colored.short_description = 'Statut'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'student', 'schedule__subject',
            'schedule__class_group', 'recorded_by'
        )


@admin.register(AbsencePeriod)
class AbsencePeriodAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'start_date', 'end_date',
        'get_duration_days', 'reason', 'is_justified'
    ]
    list_filter = ['is_justified', 'start_date']
    search_fields = ['student__first_name', 'student__last_name', 'reason']
    date_hierarchy = 'start_date'
    raw_id_fields = ['student', 'notified_by']


@admin.register(Sanction)
class SanctionAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'sanction_type', 'date',
        'is_completed', 'parents_notified', 'given_by'
    ]
    list_filter = [
        'sanction_type', 'is_completed',
        'parents_notified', 'date'
    ]
    search_fields = [
        'student__first_name', 'student__last_name',
        'reason'
    ]
    date_hierarchy = 'date'
    raw_id_fields = ['student', 'given_by']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('student', 'sanction_type', 'date', 'reason', 'description')
        }),
        ('Détails retenue', {
            'fields': ('detention_date', 'detention_start_time',
                      'detention_end_time', 'detention_room'),
            'classes': ('collapse',)
        }),
        ('Détails exclusion', {
            'fields': ('exclusion_start_date', 'exclusion_end_date'),
            'classes': ('collapse',)
        }),
        ('Suivi', {
            'fields': ('given_by', 'is_completed', 'completion_notes',
                      'parents_notified', 'notification_date')
        })
    )


@admin.register(StudentBehavior)
class StudentBehaviorAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'date', 'behavior_type_colored',
        'category', 'points', 'recorded_by'
    ]
    list_filter = ['behavior_type', 'category', 'date']
    search_fields = ['student__first_name', 'student__last_name', 'description']
    date_hierarchy = 'date'
    raw_id_fields = ['student', 'recorded_by']
    
    def behavior_type_colored(self, obj):
        colors = {
            'positive': 'green',
            'negative': 'red',
            'neutral': 'gray'
        }
        color = colors.get(obj.behavior_type, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_behavior_type_display()
        )
    behavior_type_colored.short_description = 'Type'


@admin.register(AttendanceAlert)
class AttendanceAlertAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'alert_type', 'threshold_value',
        'period_start', 'period_end', 'is_resolved',
        'created_at'
    ]
    list_filter = ['alert_type', 'is_resolved', 'created_at']
    search_fields = ['student__first_name', 'student__last_name', 'message']
    date_hierarchy = 'created_at'
    raw_id_fields = ['student', 'resolved_by']
    filter_horizontal = ['notified_users']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('student', 'resolved_by')