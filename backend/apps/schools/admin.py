"""
Configuration admin pour les écoles
"""
from django.contrib import admin
from .models import (
    School, AcademicYear, Level, Class,
    StudentClassEnrollment
)


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'school_type', 'city', 'postal_code', 'is_active']
    list_filter = ['school_type', 'is_active']
    search_fields = ['name', 'city', 'postal_code']
    prepopulated_fields = {'subdomain': ('name',)}


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'school', 'start_date', 'end_date', 'is_current']
    list_filter = ['school', 'is_current']
    date_hierarchy = 'start_date'
    
    def save_model(self, request, obj, form, change):
        # S'assurer qu'il n'y a qu'une seule année en cours par école
        if obj.is_current:
            AcademicYear.objects.filter(
                school=obj.school,
                is_current=True
            ).exclude(pk=obj.pk).update(is_current=False)
        super().save_model(request, obj, form, change)


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name', 'school_type', 'order']
    list_filter = ['school_type']
    ordering = ['order']


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'level', 'school', 'academic_year',
        'main_teacher', 'student_count', 'max_students'
    ]
    list_filter = ['school', 'academic_year', 'level']
    search_fields = ['name']
    raw_id_fields = ['main_teacher']
    
    def student_count(self, obj):
        return obj.student_count
    student_count.short_description = 'Nombre d\'élèves'


@admin.register(StudentClassEnrollment)
class StudentClassEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'class_group', 'enrollment_date', 'is_active']
    list_filter = ['class_group__school', 'class_group__academic_year', 'is_active']
    search_fields = ['student__first_name', 'student__last_name', 'student__email']
    raw_id_fields = ['student']
    date_hierarchy = 'enrollment_date'