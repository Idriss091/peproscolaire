"""
Configuration admin pour les notes et évaluations
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Avg, Count
from .models import (
    EvaluationType, GradingPeriod, Evaluation, Grade,
    SubjectAverage, GeneralAverage, Competence, CompetenceEvaluation
)


@admin.register(EvaluationType)
class EvaluationTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name', 'default_coefficient', 'color_display', 'is_graded']
    list_filter = ['is_graded']
    search_fields = ['name', 'short_name']
    
    def color_display(self, obj):
        return format_html(
            '<div style="width: 30px; height: 30px; background-color: {}; border-radius: 3px;"></div>',
            obj.color
        )
    color_display.short_description = 'Couleur'


@admin.register(GradingPeriod)
class GradingPeriodAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'academic_year', 'number', 'start_date',
        'end_date', 'is_active', 'grades_locked', 'bulletins_published'
    ]
    list_filter = ['academic_year', 'is_active', 'grades_locked', 'bulletins_published']
    date_hierarchy = 'start_date'
    actions = ['lock_grades', 'unlock_grades']
    
    def lock_grades(self, request, queryset):
        updated = queryset.update(grades_locked=True)
        self.message_user(request, f"{updated} période(s) verrouillée(s)")
    lock_grades.short_description = "Verrouiller les notes"
    
    def unlock_grades(self, request, queryset):
        updated = queryset.update(grades_locked=False)
        self.message_user(request, f"{updated} période(s) déverrouillée(s)")
    unlock_grades.short_description = "Déverrouiller les notes"


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'evaluation_type', 'subject', 'class_group',
        'date', 'max_score', 'coefficient', 'is_graded',
        'grades_published', 'average_score'
    ]
    list_filter = [
        'evaluation_type', 'subject', 'grading_period',
        'is_graded', 'grades_published'
    ]
    search_fields = ['title', 'description']
    date_hierarchy = 'date'
    raw_id_fields = ['teacher']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            avg_score=Avg('grades__score')
        )
    
    def average_score(self, obj):
        if obj.avg_score:
            return format_html(
                '<strong>{:.2f}</strong>/{:.0f}',
                obj.avg_score,
                obj.max_score
            )
        return '-'
    average_score.short_description = 'Moyenne'
    average_score.admin_order_field = 'avg_score'


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'evaluation', 'score', 'normalized_score',
        'is_absent', 'is_excused', 'graded_by', 'graded_at'
    ]
    list_filter = ['is_absent', 'is_excused', 'is_cheating']
    search_fields = [
        'student__first_name', 'student__last_name',
        'evaluation__title'
    ]
    raw_id_fields = ['student', 'evaluation', 'graded_by', 'modified_by']
    readonly_fields = ['normalized_score', 'graded_at', 'modified_at']


@admin.register(SubjectAverage)
class SubjectAverageAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'subject', 'grading_period', 'average',
        'weighted_average', 'rank', 'class_average'
    ]
    list_filter = ['grading_period', 'subject', 'class_group']
    search_fields = ['student__first_name', 'student__last_name']
    raw_id_fields = ['student']
    readonly_fields = [
        'average', 'weighted_average', 'rank', 'class_size',
        'class_average', 'min_average', 'max_average'
    ]


@admin.register(GeneralAverage)
class GeneralAverageAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'grading_period', 'average', 'weighted_average',
        'rank', 'honor_roll', 'council_decision'
    ]
    list_filter = [
        'grading_period', 'honor_roll', 'council_decision',
        'class_group'
    ]
    search_fields = ['student__first_name', 'student__last_name']
    raw_id_fields = ['student', 'validated_by']
    readonly_fields = [
        'average', 'weighted_average', 'rank', 'class_size',
        'class_average', 'validated_at'
    ]
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('student', 'grading_period', 'class_group')
        }),
        ('Moyennes et rang', {
            'fields': ('average', 'weighted_average', 'rank',
                      'class_size', 'class_average')
        }),
        ('Décision du conseil', {
            'fields': ('council_decision', 'honor_roll',
                      'general_appreciation')
        }),
        ('Validation', {
            'fields': ('validated_by', 'validated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Competence)
class CompetenceAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'domain', 'subject']
    list_filter = ['domain', 'subject']
    search_fields = ['name', 'code', 'description']


@admin.register(CompetenceEvaluation)
class CompetenceEvaluationAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'competence', 'mastery_level',
        'evaluation', 'evaluated_by', 'evaluated_at'
    ]
    list_filter = ['mastery_level', 'grading_period']
    search_fields = [
        'student__first_name', 'student__last_name',
        'competence__name', 'competence__code'
    ]
    raw_id_fields = ['student', 'evaluation', 'evaluated_by']