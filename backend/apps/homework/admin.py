"""
Configuration admin pour le cahier de textes et les devoirs
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Avg
from .models import (
    LessonContent, HomeworkType, Homework,
    HomeworkResource, StudentWork, HomeworkTemplate,
    WorkloadAnalysis
)


@admin.register(LessonContent)
class LessonContentAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'schedule', 'date', 'chapter',
        'duration_minutes', 'validated', 'created_by'
    ]
    list_filter = [
        'validated', 'date', 'chapter',
        'schedule__subject', 'schedule__class_group'
    ]
    search_fields = ['title', 'content', 'objectives']
    date_hierarchy = 'date'
    raw_id_fields = ['schedule', 'created_by', 'validated_by']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('schedule', 'date', 'title', 'chapter', 'sequence_number')
        }),
        ('Contenu pédagogique', {
            'fields': ('objectives', 'content', 'key_concepts', 'skills_worked')
        }),
        ('Métadonnées', {
            'fields': ('duration_minutes', 'is_catch_up', 'created_by')
        }),
        ('Validation', {
            'fields': ('validated', 'validated_by', 'validated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'schedule__subject', 'schedule__class_group',
            'schedule__teacher', 'created_by'
        )


@admin.register(HomeworkType)
class HomeworkTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name', 'default_duration_days', 'color_display']
    search_fields = ['name', 'short_name']
    
    def color_display(self, obj):
        return format_html(
            '<div style="width: 30px; height: 30px; background-color: {}; border-radius: 3px;"></div>',
            obj.color
        )
    color_display.short_description = 'Couleur'


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'subject', 'class_group', 'teacher',
        'due_date', 'difficulty', 'is_graded', 'submission_count',
        'view_count'
    ]
    list_filter = [
        'subject', 'class_group', 'homework_type',
        'difficulty', 'is_graded', 'submission_type',
        'is_ai_suggested'
    ]
    search_fields = ['title', 'description']
    date_hierarchy = 'due_date'
    raw_id_fields = ['lesson_content', 'teacher']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            submission_count=Count('submissions')
        )
    
    def submission_count(self, obj):
        return obj.submission_count
    submission_count.short_description = 'Rendus'
    submission_count.admin_order_field = 'submission_count'


class HomeworkResourceInline(admin.TabularInline):
    model = HomeworkResource
    extra = 1
    fields = ['resource_type', 'title', 'file', 'url', 'is_mandatory', 'order']


@admin.register(StudentWork)
class StudentWorkAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'homework', 'status', 'submitted_at',
        'grade', 'corrected_by'
    ]
    list_filter = ['status', 'submitted_at', 'corrected_at']
    search_fields = [
        'student__first_name', 'student__last_name',
        'homework__title'
    ]
    raw_id_fields = ['homework', 'student', 'corrected_by']
    date_hierarchy = 'submitted_at'
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('homework', 'student', 'status')
        }),
        ('Travail rendu', {
            'fields': ('submitted_at', 'content', 'file', 'student_comment',
                      'time_spent_minutes')
        }),
        ('Correction', {
            'fields': ('grade', 'teacher_comment', 'corrected_file',
                      'corrected_by', 'corrected_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(HomeworkTemplate)
class HomeworkTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'subject', 'teacher', 'chapter', 'level',
        'use_count', 'is_shared'
    ]
    list_filter = ['subject', 'level', 'is_shared', 'difficulty']
    search_fields = ['name', 'title', 'description', 'tags']
    raw_id_fields = ['teacher']
    
    actions = ['make_shared', 'make_private']
    
    def make_shared(self, request, queryset):
        updated = queryset.update(is_shared=True)
        self.message_user(request, f"{updated} modèle(s) partagé(s)")
    make_shared.short_description = "Partager les modèles sélectionnés"
    
    def make_private(self, request, queryset):
        updated = queryset.update(is_shared=False)
        self.message_user(request, f"{updated} modèle(s) rendu(s) privé(s)")
    make_private.short_description = "Rendre privés les modèles sélectionnés"


@admin.register(WorkloadAnalysis)
class WorkloadAnalysisAdmin(admin.ModelAdmin):
    list_display = [
        'class_group', 'date', 'total_homework_count',
        'total_estimated_minutes', 'is_overloaded', 'overload_level'
    ]
    list_filter = ['is_overloaded', 'overload_level', 'date']
    date_hierarchy = 'date'
    readonly_fields = [
        'total_homework_count', 'total_estimated_minutes',
        'homework_by_subject', 'recommendations'
    ]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('class_group')