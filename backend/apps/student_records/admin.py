"""
Configuration admin pour les dossiers élèves
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    StudentRecord, Guardian, EmergencyContact,
    MedicalRecord, StudentDocument, ScholarshipRecord,
    DisciplinaryRecord, OrientationRecord
)


class GuardianInline(admin.TabularInline):
    model = Guardian
    extra = 0
    fields = [
        'first_name', 'last_name', 'relationship',
        'email', 'phone', 'has_custody', 'is_primary_contact'
    ]


class EmergencyContactInline(admin.TabularInline):
    model = EmergencyContact
    extra = 0
    fields = ['name', 'relationship', 'phone', 'priority']


@admin.register(StudentRecord)
class StudentRecordAdmin(admin.ModelAdmin):
    list_display = [
        'student_name', 'national_id', 'age', 'current_class',
        'entry_date', 'is_active', 'has_special_needs'
    ]
    list_filter = [
        'is_active', 'family_situation', 'has_special_needs',
        'has_disability', 'lunch_type'
    ]
    search_fields = [
        'student__first_name', 'student__last_name',
        'student__email', 'national_id'
    ]
    readonly_fields = ['created_at', 'updated_at']
    inlines = [GuardianInline, EmergencyContactInline]
    
    fieldsets = (
        ('Informations générales', {
            'fields': (
                'student', 'national_id', 'birth_certificate_number',
                'birth_place', 'birth_country', 'nationality'
            )
        }),
        ('Situation familiale', {
            'fields': (
                'family_situation', 'siblings_count'
            )
        }),
        ('Scolarité', {
            'fields': (
                'entry_date', 'previous_school', 'options',
                'specialties', 'is_active', 'graduation_date',
                'graduation_reason'
            )
        }),
        ('Besoins particuliers', {
            'fields': (
                'has_special_needs', 'special_needs_details',
                'has_disability', 'disability_details',
                'has_pai', 'has_pap', 'has_pps'
            ),
            'classes': ('collapse',)
        }),
        ('Vie scolaire', {
            'fields': (
                'uses_school_transport', 'transport_line',
                'lunch_type', 'dietary_restrictions'
            )
        }),
        ('Autorisations', {
            'fields': (
                'photo_authorization', 'leave_alone_authorization'
            )
        }),
        ('Notes', {
            'fields': ('administrative_notes',),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def student_name(self, obj):
        return obj.student.get_full_name()
    student_name.short_description = 'Élève'
    student_name.admin_order_field = 'student__last_name'
    
    def age(self, obj):
        age = obj.get_age()
        return f"{age} ans" if age else "-"
    age.short_description = 'Âge'
    
    def current_class(self, obj):
        enrollment = obj.student.enrollments.filter(is_active=True).first()
        if enrollment:
            return enrollment.class_group
        return "-"
    current_class.short_description = 'Classe actuelle'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'student', 'student__profile'
        ).prefetch_related(
            'student__enrollments__class_group'
        )


@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'relationship', 'student_name',
        'email', 'phone', 'has_custody', 'is_primary_contact'
    ]
    list_filter = ['relationship', 'has_custody', 'is_primary_contact']
    search_fields = [
        'first_name', 'last_name', 'email',
        'student_record__student__first_name',
        'student_record__student__last_name'
    ]
    raw_id_fields = ['student_record', 'user']
    
    def full_name(self, obj):
        return obj.get_full_name()
    full_name.short_description = 'Nom complet'
    
    def student_name(self, obj):
        return obj.student_record.student.get_full_name()
    student_name.short_description = 'Élève'


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = [
        'student_name', 'blood_type', 'has_allergies',
        'has_chronic_conditions', 'last_medical_check'
    ]
    list_filter = ['blood_type', 'vaccinations_up_to_date']
    search_fields = [
        'student_record__student__first_name',
        'student_record__student__last_name'
    ]
    raw_id_fields = ['student_record']
    
    def student_name(self, obj):
        return obj.student_record.student.get_full_name()
    student_name.short_description = 'Élève'
    
    def has_allergies(self, obj):
        return bool(obj.allergies)
    has_allergies.boolean = True
    has_allergies.short_description = 'Allergies'
    
    def has_chronic_conditions(self, obj):
        return bool(obj.chronic_conditions)
    has_chronic_conditions.boolean = True
    has_chronic_conditions.short_description = 'Maladies chroniques'


@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'document_type', 'student_name',
        'is_verified', 'is_expired', 'created_at'
    ]
    list_filter = [
        'document_type', 'is_verified', 'is_confidential'
    ]
    search_fields = [
        'title', 'student_record__student__first_name',
        'student_record__student__last_name'
    ]
    raw_id_fields = ['student_record', 'uploaded_by', 'verified_by']
    date_hierarchy = 'created_at'
    
    def student_name(self, obj):
        return obj.student_record.student.get_full_name()
    student_name.short_description = 'Élève'
    
    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = 'Expiré'
    
    actions = ['verify_documents']
    
    def verify_documents(self, request, queryset):
        updated = queryset.filter(is_verified=False).update(
            is_verified=True,
            verified_by=request.user,
            verified_at=timezone.now()
        )
        self.message_user(request, f"{updated} document(s) vérifié(s)")
    verify_documents.short_description = "Vérifier les documents sélectionnés"


@admin.register(ScholarshipRecord)
class ScholarshipRecordAdmin(admin.ModelAdmin):
    list_display = [
        'student_name', 'academic_year', 'scholarship_type',
        'amount', 'status', 'application_date'
    ]
    list_filter = ['scholarship_type', 'status', 'academic_year']
    search_fields = [
        'student_record__student__first_name',
        'student_record__student__last_name',
        'reference_number'
    ]
    raw_id_fields = ['student_record', 'academic_year']
    date_hierarchy = 'application_date'
    
    def student_name(self, obj):
        return obj.student_record.student.get_full_name()
    student_name.short_description = 'Élève'