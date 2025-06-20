"""
Serializers pour le module d'analyse IA et détection des risques
"""
from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from .models import (
    RiskProfile, RiskIndicator, InterventionPlan,
    InterventionAction, AlertConfiguration, Alert
)
from apps.authentication.serializers import UserSerializer
from apps.schools.serializers import AcademicYearSerializer


class RiskIndicatorSerializer(serializers.ModelSerializer):
    """Serializer pour les indicateurs de risque"""
    
    class Meta:
        model = RiskIndicator
        fields = "__all__"


class RiskProfileSerializer(serializers.ModelSerializer):
    """Serializer pour les profils de risque"""
    
    class Meta:
        model = RiskProfile
        fields = "__all__"


class RiskProfileCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer/mettre à jour un profil de risque"""
    
    class Meta:
        model = RiskProfile
        fields = ['student', 'academic_year']
    
    def create(self, validated_data):
        # Vérifier l'unicité
        student = validated_data['student']
        academic_year = validated_data['academic_year']
        
        profile, created = RiskProfile.objects.get_or_create(
            student=student,
            academic_year=academic_year
        )
        
        if not created:
            # Si existe déjà, déclencher une nouvelle analyse
            from .tasks import analyze_student_risk
            analyze_student_risk.delay(str(profile.id))
        
        return profile


class InterventionActionSerializer(serializers.ModelSerializer):
    """Serializer pour les actions d'intervention"""
    responsible_name = serializers.CharField(
        source='responsible.get_full_name',
        read_only=True
    )
    action_type_display = serializers.CharField(
        source='get_action_type_display',
        read_only=True
    )
    
    class Meta:
        model = InterventionAction
        fields = [
            'id', 'action_type', 'action_type_display', 'title',
            'description', 'responsible', 'responsible_name',
            'scheduled_date', 'scheduled_time', 'duration_minutes',
            'completed', 'completed_date', 'notes',
            'impact_assessment', 'created_at'
        ]
        read_only_fields = ['id', 'completed_date', 'created_at']


class InterventionPlanSerializer(serializers.ModelSerializer):
    """Serializer pour les plans d'intervention"""
    
    class Meta:
        model = InterventionPlan
        fields = "__all__"


class InterventionPlanCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un plan d'intervention"""
    actions = InterventionActionSerializer(many=True, required=False)
    
    class Meta:
        model = InterventionPlan
        fields = [
            'risk_profile', 'title', 'description', 'coordinator',
            'participants', 'start_date', 'end_date', 'objectives',
            'planned_actions', 'resources_needed', 'success_criteria',
            'evaluation_frequency', 'actions'
        ]
    
    @transaction.atomic
    def create(self, validated_data):
        actions_data = validated_data.pop('actions', [])
        participants = validated_data.pop('participants', [])
        
        # Créer le plan
        plan = InterventionPlan.objects.create(**validated_data)
        
        # Ajouter les participants
        plan.participants.set(participants)
        
        # Créer les actions
        for action_data in actions_data:
            InterventionAction.objects.create(
                intervention_plan=plan,
                **action_data
            )
        
        # Démarrer le monitoring automatiquement
        plan.risk_profile.start_monitoring(assigned_to=plan.coordinator)
        
        return plan


class AlertConfigurationSerializer(serializers.ModelSerializer):
    """Serializer pour la configuration des alertes"""
    alert_type_display = serializers.CharField(
        source='get_alert_type_display',
        read_only=True
    )
    additional_recipients = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = AlertConfiguration
        fields = [
            'id', 'name', 'alert_type', 'alert_type_display',
            'description', 'risk_level_threshold',
            'risk_score_threshold', 'indicator_conditions',
            'notify_student', 'notify_parents',
            'notify_main_teacher', 'notify_administration',
            'additional_recipients', 'is_active',
            'cooldown_days', 'message_template', 'priority',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AlertSerializer(serializers.ModelSerializer):
    """Serializer pour les alertes"""
    
    class Meta:
        model = Alert
        fields = "__all__"


class RiskAnalysisRequestSerializer(serializers.Serializer):
    """Serializer pour demander une analyse de risque"""
    student_id = serializers.UUIDField(required=False)
    class_id = serializers.UUIDField(required=False)
    force_update = serializers.BooleanField(default=False)
    
    def validate(self, attrs):
        if not attrs.get('student_id') and not attrs.get('class_id'):
            raise serializers.ValidationError(
                "Au moins un student_id ou class_id est requis"
            )
        return attrs


class RiskDashboardSerializer(serializers.Serializer):
    """Serializer pour le tableau de bord des risques"""
    
    def to_representation(self, instance):
        """Instance est un dictionnaire de données du dashboard"""
        return {
            'summary': instance.get('summary', {}),
            'risk_distribution': instance.get('risk_distribution', {}),
            'trending_students': instance.get('trending_students', []),
            'recent_alerts': instance.get('recent_alerts', []),
            'intervention_stats': instance.get('intervention_stats', {}),
            'class_comparison': instance.get('class_comparison', [])
        }


class StudentRiskHistorySerializer(serializers.Serializer):
    """Serializer pour l'historique de risque d'un élève"""
    
    def to_representation(self, instance):
        """Instance est un élève"""
        from .models import RiskProfile
        
        profiles = RiskProfile.objects.filter(
            student=instance
        ).select_related('academic_year').order_by('-academic_year__start_date')
        
        history = []
        for profile in profiles:
            history.append({
                'academic_year': profile.academic_year.name,
                'risk_score': profile.risk_score,
                'risk_level': profile.risk_level,
                'risk_level_display': profile.get_risk_level_display(),
                'main_risks': {
                    'academic': profile.academic_risk,
                    'attendance': profile.attendance_risk,
                    'behavioral': profile.behavioral_risk,
                    'social': profile.social_risk
                },
                'dropout_probability': profile.dropout_probability,
                'interventions': profile.intervention_plans.count(),
                'last_analysis': profile.last_analysis
            })
        
        # Calculer les tendances
        if len(history) >= 2:
            current = history[0]
            previous = history[1]
            trend = {
                'risk_score_change': current['risk_score'] - previous['risk_score'],
                'improving': current['risk_score'] < previous['risk_score']
            }
        else:
            trend = None
        
        return {
            'student': UserSerializer(instance).data,
            'current_profile': history[0] if history else None,
            'history': history,
            'trend': trend
        }


class ClassRiskReportSerializer(serializers.Serializer):
    """Serializer pour le rapport de risque d'une classe"""
    
    def to_representation(self, instance):
        """Instance est une classe"""
        from .analyzers import ClassRiskAnalyzer
        
        analyzer = ClassRiskAnalyzer(instance)
        analysis = analyzer.analyze_class_risks()
        
        # Ajouter des informations supplémentaires
        analysis['class_info'] = {
            'id': str(instance.id),
            'name': str(instance),
            'level': instance.level.name,
            'main_teacher': instance.main_teacher.get_full_name() if instance.main_teacher else None,
            'academic_year': instance.academic_year.name
        }
        
        # Statistiques des interventions
        from .models import InterventionPlan
        active_interventions = InterventionPlan.objects.filter(
            risk_profile__student__enrollments__class_group=instance,
            risk_profile__student__enrollments__is_active=True,
            status='active'
        ).count()
        
        analysis['intervention_stats'] = {
            'active_plans': active_interventions,
            'monitored_students': len([s for s in analysis['at_risk_students'] 
                                     if s.get('risk_level') in ['high', 'critical']])
        }
        
        return analysis


class InterventionEffectivenessSerializer(serializers.Serializer):
    """Serializer pour l'évaluation de l'efficacité des interventions"""
    intervention_plan_id = serializers.UUIDField()
    effectiveness_score = serializers.FloatField(min_value=0, max_value=10)
    outcomes = serializers.CharField()
    recommendations = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    
    def update(self, instance, validated_data):
        """Instance est un InterventionPlan"""
        instance.effectiveness_score = validated_data['effectiveness_score']
        instance.outcomes = validated_data['outcomes']
        
        # Si l'intervention est terminée
        if validated_data.get('effectiveness_score', 0) >= 7:
            instance.status = 'completed'
            instance.actual_end_date = timezone.now().date()
        
        instance.save()
        return instance