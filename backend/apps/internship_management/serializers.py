from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Company, InternshipOffer, InternshipApplication,
    Internship, InternshipVisit, InternshipEvaluation
)

User = get_user_model()


class CompanySerializer(serializers.ModelSerializer):
    """Serializer pour les entreprises"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    total_offers = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'description', 'sector', 'size',
            'contact_person', 'contact_email', 'contact_phone',
            'address', 'city', 'postal_code', 'country',
            'website', 'linkedin_url', 'siret',
            'is_partner', 'is_active', 'partnership_since',
            'total_internships', 'average_rating', 'total_offers',
            'created_at', 'updated_at', 'created_by_name'
        ]
        read_only_fields = [
            'id', 'total_internships', 'average_rating',
            'created_at', 'updated_at'
        ]
    
    def get_total_offers(self, obj):
        return obj.offers.filter(status='published').count()


class CompanyListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des entreprises"""
    total_offers = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'sector', 'size', 'city',
            'is_partner', 'average_rating', 'total_offers'
        ]
    
    def get_total_offers(self, obj):
        return obj.offers.filter(status='published').count()


class InternshipOfferSerializer(serializers.ModelSerializer):
    """Serializer pour les offres de stage"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_details = CompanyListSerializer(source='company', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    can_apply = serializers.SerializerMethodField()
    applications_count = serializers.SerializerMethodField()
    
    class Meta:
        model = InternshipOffer
        fields = [
            'id', 'company', 'company_name', 'company_details',
            'title', 'description', 'offer_type', 'status',
            'duration_value', 'duration_type', 'start_date', 'end_date',
            'application_deadline', 'department', 'supervisor_name',
            'supervisor_email', 'supervisor_phone',
            'required_level', 'required_skills', 'preferred_skills',
            'is_paid', 'monthly_allowance', 'benefits',
            'remote_possible', 'transport_provided', 'meal_vouchers',
            'accommodation_help', 'max_applications', 'current_applications',
            'applications_count', 'can_apply',
            'created_at', 'updated_at', 'published_at', 'created_by_name'
        ]
        read_only_fields = [
            'id', 'current_applications', 'created_at', 'updated_at', 'published_at'
        ]
    
    def get_can_apply(self, obj):
        return obj.can_apply()
    
    def get_applications_count(self, obj):
        return f"{obj.current_applications}/{obj.max_applications}"


class InternshipOfferListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des offres"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_city = serializers.CharField(source='company.city', read_only=True)
    can_apply = serializers.SerializerMethodField()
    
    class Meta:
        model = InternshipOffer
        fields = [
            'id', 'title', 'company_name', 'company_city',
            'offer_type', 'start_date', 'application_deadline',
            'duration_value', 'duration_type', 'is_paid',
            'remote_possible', 'can_apply'
        ]
    
    def get_can_apply(self, obj):
        return obj.can_apply()


class InternshipApplicationSerializer(serializers.ModelSerializer):
    """Serializer pour les candidatures de stage"""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    offer_title = serializers.CharField(source='offer.title', read_only=True)
    company_name = serializers.CharField(source='offer.company.name', read_only=True)
    
    class Meta:
        model = InternshipApplication
        fields = [
            'id', 'student', 'student_name', 'offer', 'offer_title', 'company_name',
            'status', 'submitted_at', 'reviewed_at', 'response_at',
            'cover_letter', 'cv_file', 'portfolio_url', 'additional_documents',
            'motivation', 'availability_notes', 'special_requirements',
            'company_notes', 'interview_date', 'interview_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'submitted_at', 'reviewed_at', 'response_at',
            'created_at', 'updated_at'
        ]


class InternshipApplicationCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer une candidature"""
    
    class Meta:
        model = InternshipApplication
        fields = [
            'offer', 'cover_letter', 'cv_file', 'portfolio_url',
            'motivation', 'availability_notes', 'special_requirements'
        ]
    
    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)


class InternshipSerializer(serializers.ModelSerializer):
    """Serializer pour les stages"""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    academic_supervisor_name = serializers.CharField(source='academic_supervisor.get_full_name', read_only=True)
    offer_title = serializers.CharField(source='application.offer.title', read_only=True)
    
    class Meta:
        model = Internship
        fields = [
            'id', 'application', 'student', 'student_name',
            'company', 'company_name', 'offer_title',
            'academic_supervisor', 'academic_supervisor_name',
            'company_supervisor', 'company_supervisor_email',
            'start_date', 'end_date', 'actual_start_date', 'actual_end_date',
            'status', 'progress_percentage',
            'student_rating', 'company_rating',
            'internship_agreement', 'final_report', 'company_evaluation',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'progress_percentage', 'created_at', 'updated_at'
        ]


class InternshipListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des stages"""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = Internship
        fields = [
            'id', 'student_name', 'company_name', 'status',
            'start_date', 'end_date', 'progress_percentage'
        ]


class InternshipVisitSerializer(serializers.ModelSerializer):
    """Serializer pour les visites de stage"""
    visitor_name = serializers.CharField(source='visitor.get_full_name', read_only=True)
    student_name = serializers.CharField(source='internship.student.get_full_name', read_only=True)
    company_name = serializers.CharField(source='internship.company.name', read_only=True)
    
    class Meta:
        model = InternshipVisit
        fields = [
            'id', 'internship', 'student_name', 'company_name',
            'visitor', 'visitor_name', 'visit_type', 'status',
            'scheduled_date', 'duration_minutes', 'location', 'participants',
            'visit_report', 'student_feedback', 'company_feedback',
            'recommendations', 'overall_satisfaction', 'issues_identified',
            'follow_up_required', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'completed_at'
        ]


class InternshipEvaluationSerializer(serializers.ModelSerializer):
    """Serializer pour les évaluations de stage"""
    evaluator_name = serializers.CharField(source='evaluator.get_full_name', read_only=True)
    student_name = serializers.CharField(source='internship.student.get_full_name', read_only=True)
    company_name = serializers.CharField(source='internship.company.name', read_only=True)
    
    class Meta:
        model = InternshipEvaluation
        fields = [
            'id', 'internship', 'student_name', 'company_name',
            'evaluator', 'evaluator_name', 'evaluator_type',
            'technical_skills', 'soft_skills', 'initiative',
            'reliability', 'communication', 'overall_rating',
            'strengths', 'areas_for_improvement', 'general_comments',
            'would_recommend_student', 'would_recommend_company',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'overall_rating', 'created_at', 'updated_at'
        ]


class InternshipStatsSerializer(serializers.Serializer):
    """Serializer pour les statistiques de stage"""
    total_internships = serializers.IntegerField()
    ongoing_internships = serializers.IntegerField()
    completed_internships = serializers.IntegerField()
    upcoming_internships = serializers.IntegerField()
    average_rating = serializers.FloatField()
    top_companies = serializers.ListField()
    popular_sectors = serializers.DictField()
    monthly_stats = serializers.DictField()


class InternshipSearchSerializer(serializers.Serializer):
    """Serializer pour la recherche d'offres de stage"""
    query = serializers.CharField(max_length=200, required=False)
    sector = serializers.ChoiceField(choices=Company.SECTORS, required=False)
    city = serializers.CharField(max_length=100, required=False)
    offer_type = serializers.ChoiceField(choices=InternshipOffer.OFFER_TYPES, required=False)
    is_paid = serializers.BooleanField(required=False)
    remote_possible = serializers.BooleanField(required=False)
    start_date_from = serializers.DateField(required=False)
    start_date_to = serializers.DateField(required=False)
    duration_min = serializers.IntegerField(required=False)
    duration_max = serializers.IntegerField(required=False)


class InternshipReportSerializer(serializers.Serializer):
    """Serializer pour les rapports de stage"""
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    total_offers = serializers.IntegerField()
    total_applications = serializers.IntegerField()
    total_internships = serializers.IntegerField()
    success_rate = serializers.FloatField()
    average_duration = serializers.FloatField()
    top_companies = serializers.ListField()
    sector_distribution = serializers.DictField()
    monthly_trends = serializers.DictField()


class InternshipNotificationSerializer(serializers.Serializer):
    """Serializer pour les notifications de stage"""
    message = serializers.CharField()
    notification_type = serializers.ChoiceField(choices=[
        ('new_offer', 'Nouvelle offre'),
        ('application_status', 'Statut candidature'),
        ('visit_reminder', 'Rappel visite'),
        ('evaluation_due', 'Évaluation à faire'),
        ('deadline_approaching', 'Échéance proche')
    ])
    priority = serializers.ChoiceField(choices=[
        ('low', 'Faible'),
        ('medium', 'Moyenne'),
        ('high', 'Élevée'),
        ('urgent', 'Urgente')
    ], default='medium')
    action_url = serializers.URLField(required=False)
    action_text = serializers.CharField(required=False)