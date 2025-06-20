from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    Company, InternshipOffer, InternshipApplication,
    Internship, InternshipVisit, InternshipEvaluation
)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'sector', 'size', 'city', 'is_partner',
        'total_internships', 'average_rating_display', 'is_active'
    ]
    list_filter = [
        'sector', 'size', 'is_partner', 'is_active', 'city'
    ]
    search_fields = ['name', 'contact_person', 'contact_email', 'city']
    readonly_fields = ['id', 'created_at', 'updated_at', 'total_internships', 'average_rating']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'description', 'sector', 'size')
        }),
        ('Contact', {
            'fields': ('contact_person', 'contact_email', 'contact_phone')
        }),
        ('Adresse', {
            'fields': ('address', 'city', 'postal_code', 'country')
        }),
        ('Liens', {
            'fields': ('website', 'linkedin_url', 'siret'),
            'classes': ('collapse',)
        }),
        ('Partenariat', {
            'fields': ('is_partner', 'partnership_since', 'is_active')
        }),
        ('Statistiques', {
            'fields': ('total_internships', 'average_rating'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('id', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['make_partner', 'remove_partner', 'activate_companies', 'deactivate_companies']
    
    def average_rating_display(self, obj):
        if obj.average_rating > 0:
            stars = '⭐' * int(obj.average_rating)
            return f"{obj.average_rating:.1f}/5 {stars}"
        return "-"
    average_rating_display.short_description = 'Note moyenne'
    
    def make_partner(self, request, queryset):
        updated = queryset.update(is_partner=True, partnership_since=timezone.now().date())
        self.message_user(request, f'{updated} entreprises marquées comme partenaires.')
    make_partner.short_description = 'Marquer comme partenaire'
    
    def remove_partner(self, request, queryset):
        updated = queryset.update(is_partner=False, partnership_since=None)
        self.message_user(request, f'{updated} entreprises retirées du partenariat.')
    remove_partner.short_description = 'Retirer du partenariat'
    
    def activate_companies(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} entreprises activées.')
    activate_companies.short_description = 'Activer'
    
    def deactivate_companies(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} entreprises désactivées.')
    deactivate_companies.short_description = 'Désactiver'


@admin.register(InternshipOffer)
class InternshipOfferAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'company', 'offer_type', 'status', 'start_date',
        'application_deadline', 'applications_count', 'is_paid'
    ]
    list_filter = [
        'offer_type', 'status', 'is_paid', 'remote_possible',
        'start_date', 'created_at'
    ]
    search_fields = ['title', 'company__name', 'description', 'department']
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'published_at', 'current_applications'
    ]
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('company', 'title', 'description', 'offer_type', 'status')
        }),
        ('Durée et dates', {
            'fields': ('duration_value', 'duration_type', 'start_date', 'end_date', 'application_deadline')
        }),
        ('Détails du poste', {
            'fields': ('department', 'supervisor_name', 'supervisor_email', 'supervisor_phone')
        }),
        ('Exigences', {
            'fields': ('required_level', 'required_skills', 'preferred_skills'),
            'classes': ('collapse',)
        }),
        ('Conditions', {
            'fields': ('is_paid', 'monthly_allowance', 'benefits')
        }),
        ('Logistique', {
            'fields': ('remote_possible', 'transport_provided', 'meal_vouchers', 'accommodation_help'),
            'classes': ('collapse',)
        }),
        ('Candidatures', {
            'fields': ('max_applications', 'current_applications')
        }),
        ('Métadonnées', {
            'fields': ('id', 'created_by', 'created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['publish_offers', 'unpublish_offers', 'mark_as_filled']
    
    def applications_count(self, obj):
        return f"{obj.current_applications}/{obj.max_applications}"
    applications_count.short_description = 'Candidatures'
    
    def publish_offers(self, request, queryset):
        updated = 0
        for offer in queryset.filter(status='draft'):
            offer.publish()
            updated += 1
        self.message_user(request, f'{updated} offres publiées.')
    publish_offers.short_description = 'Publier les offres'
    
    def unpublish_offers(self, request, queryset):
        updated = queryset.update(status='draft', published_at=None)
        self.message_user(request, f'{updated} offres dépubliées.')
    unpublish_offers.short_description = 'Dépublier les offres'
    
    def mark_as_filled(self, request, queryset):
        updated = queryset.update(status='filled')
        self.message_user(request, f'{updated} offres marquées comme pourvues.')
    mark_as_filled.short_description = 'Marquer comme pourvu'


@admin.register(InternshipApplication)
class InternshipApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'student_name', 'offer_title', 'company_name', 'status',
        'submitted_at', 'response_at'
    ]
    list_filter = [
        'status', 'submitted_at', 'offer__company', 'offer__offer_type'
    ]
    search_fields = [
        'student__first_name', 'student__last_name', 'student__email',
        'offer__title', 'offer__company__name'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'submitted_at', 'reviewed_at', 'response_at'
    ]
    date_hierarchy = 'submitted_at'
    
    fieldsets = (
        ('Candidature', {
            'fields': ('student', 'offer', 'status')
        }),
        ('Documents', {
            'fields': ('cover_letter', 'cv_file', 'portfolio_url', 'additional_documents')
        }),
        ('Informations complémentaires', {
            'fields': ('motivation', 'availability_notes', 'special_requirements'),
            'classes': ('collapse',)
        }),
        ('Suivi entreprise', {
            'fields': ('company_notes', 'interview_date', 'interview_notes'),
            'classes': ('collapse',)
        }),
        ('Dates importantes', {
            'fields': ('submitted_at', 'reviewed_at', 'response_at'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['accept_applications', 'reject_applications', 'schedule_interviews']
    
    def student_name(self, obj):
        return obj.student.get_full_name()
    student_name.short_description = 'Étudiant'
    
    def offer_title(self, obj):
        return obj.offer.title
    offer_title.short_description = 'Offre'
    
    def company_name(self, obj):
        return obj.offer.company.name
    company_name.short_description = 'Entreprise'
    
    def accept_applications(self, request, queryset):
        updated = 0
        for application in queryset.filter(status__in=['submitted', 'under_review']):
            application.accept()
            updated += 1
        self.message_user(request, f'{updated} candidatures acceptées.')
    accept_applications.short_description = 'Accepter les candidatures'
    
    def reject_applications(self, request, queryset):
        updated = 0
        for application in queryset.filter(status__in=['submitted', 'under_review']):
            application.reject()
            updated += 1
        self.message_user(request, f'{updated} candidatures rejetées.')
    reject_applications.short_description = 'Rejeter les candidatures'
    
    def schedule_interviews(self, request, queryset):
        updated = queryset.update(status='interview_scheduled')
        self.message_user(request, f'{updated} entretiens programmés.')
    schedule_interviews.short_description = 'Programmer des entretiens'


@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    list_display = [
        'student_name', 'company_name', 'status', 'start_date',
        'end_date', 'progress_display', 'ratings_display'
    ]
    list_filter = [
        'status', 'start_date', 'company', 'academic_supervisor'
    ]
    search_fields = [
        'student__first_name', 'student__last_name',
        'company__name', 'company_supervisor'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'progress_percentage'
    ]
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Stage', {
            'fields': ('application', 'student', 'company', 'status')
        }),
        ('Supervision', {
            'fields': ('academic_supervisor', 'company_supervisor', 'company_supervisor_email')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'actual_start_date', 'actual_end_date')
        }),
        ('Progression', {
            'fields': ('progress_percentage',)
        }),
        ('Évaluations', {
            'fields': ('student_rating', 'company_rating'),
            'classes': ('collapse',)
        }),
        ('Documents', {
            'fields': ('internship_agreement', 'final_report', 'company_evaluation'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['start_internships', 'complete_internships', 'update_progress']
    
    def student_name(self, obj):
        return obj.student.get_full_name()
    student_name.short_description = 'Étudiant'
    
    def company_name(self, obj):
        return obj.company.name
    company_name.short_description = 'Entreprise'
    
    def progress_display(self, obj):
        if obj.status == 'ongoing':
            return format_html(
                '<div style="width: 100px; background: #f0f0f0; border-radius: 3px;">'
                '<div style="width: {}%; background: #007cba; height: 20px; border-radius: 3px; text-align: center; color: white; line-height: 20px;">'
                '{}%</div></div>',
                obj.progress_percentage, obj.progress_percentage
            )
        return f"{obj.progress_percentage}%"
    progress_display.short_description = 'Progression'
    
    def ratings_display(self, obj):
        ratings = []
        if obj.student_rating:
            ratings.append(f"Étudiant: {obj.student_rating}/5")
        if obj.company_rating:
            ratings.append(f"Entreprise: {obj.company_rating}/5")
        return " | ".join(ratings) if ratings else "-"
    ratings_display.short_description = 'Notes'
    
    def start_internships(self, request, queryset):
        updated = queryset.filter(status='upcoming').update(status='ongoing')
        self.message_user(request, f'{updated} stages démarrés.')
    start_internships.short_description = 'Démarrer les stages'
    
    def complete_internships(self, request, queryset):
        updated = queryset.filter(status='ongoing').update(status='completed')
        self.message_user(request, f'{updated} stages terminés.')
    complete_internships.short_description = 'Terminer les stages'
    
    def update_progress(self, request, queryset):
        updated = 0
        for internship in queryset.filter(status='ongoing'):
            internship.calculate_progress()
            updated += 1
        self.message_user(request, f'{updated} progressions mises à jour.')
    update_progress.short_description = 'Mettre à jour la progression'


@admin.register(InternshipVisit)
class InternshipVisitAdmin(admin.ModelAdmin):
    list_display = [
        'internship_display', 'visitor', 'visit_type', 'status',
        'scheduled_date', 'overall_satisfaction', 'follow_up_required'
    ]
    list_filter = [
        'visit_type', 'status', 'follow_up_required', 'scheduled_date'
    ]
    search_fields = [
        'internship__student__first_name', 'internship__student__last_name',
        'internship__company__name', 'visitor__first_name', 'visitor__last_name'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at', 'completed_at']
    date_hierarchy = 'scheduled_date'
    
    fieldsets = (
        ('Visite', {
            'fields': ('internship', 'visitor', 'visit_type', 'status')
        }),
        ('Planification', {
            'fields': ('scheduled_date', 'duration_minutes', 'location', 'participants')
        }),
        ('Rapport', {
            'fields': ('visit_report', 'student_feedback', 'company_feedback', 'recommendations'),
            'classes': ('collapse',)
        }),
        ('Évaluation', {
            'fields': ('overall_satisfaction', 'issues_identified', 'follow_up_required'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('id', 'created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['complete_visits', 'mark_follow_up_required']
    
    def internship_display(self, obj):
        return f"{obj.internship.student.get_full_name()} @ {obj.internship.company.name}"
    internship_display.short_description = 'Stage'
    
    def complete_visits(self, request, queryset):
        updated = 0
        for visit in queryset.filter(status='scheduled'):
            visit.complete_visit()
            updated += 1
        self.message_user(request, f'{updated} visites marquées comme effectuées.')
    complete_visits.short_description = 'Marquer comme effectuées'
    
    def mark_follow_up_required(self, request, queryset):
        updated = queryset.update(follow_up_required=True)
        self.message_user(request, f'{updated} visites marquées pour suivi.')
    mark_follow_up_required.short_description = 'Marquer pour suivi'


@admin.register(InternshipEvaluation)
class InternshipEvaluationAdmin(admin.ModelAdmin):
    list_display = [
        'internship_display', 'evaluator_type', 'overall_rating',
        'technical_skills', 'soft_skills', 'would_recommend'
    ]
    list_filter = [
        'evaluator_type', 'overall_rating', 'would_recommend_student',
        'would_recommend_company', 'created_at'
    ]
    search_fields = [
        'internship__student__first_name', 'internship__student__last_name',
        'internship__company__name', 'evaluator__first_name', 'evaluator__last_name'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at', 'overall_rating']
    
    fieldsets = (
        ('Évaluation', {
            'fields': ('internship', 'evaluator', 'evaluator_type')
        }),
        ('Critères (1-5)', {
            'fields': ('technical_skills', 'soft_skills', 'initiative', 'reliability', 'communication')
        }),
        ('Note globale', {
            'fields': ('overall_rating',)
        }),
        ('Commentaires', {
            'fields': ('strengths', 'areas_for_improvement', 'general_comments')
        }),
        ('Recommandations', {
            'fields': ('would_recommend_student', 'would_recommend_company'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def internship_display(self, obj):
        return f"{obj.internship.student.get_full_name()} @ {obj.internship.company.name}"
    internship_display.short_description = 'Stage'
    
    def would_recommend(self, obj):
        if obj.evaluator_type == 'student':
            return "Oui" if obj.would_recommend_company else "Non" if obj.would_recommend_company is False else "-"
        elif obj.evaluator_type == 'company':
            return "Oui" if obj.would_recommend_student else "Non" if obj.would_recommend_student is False else "-"
        return "-"
    would_recommend.short_description = 'Recommande'