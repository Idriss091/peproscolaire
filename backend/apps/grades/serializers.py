"""
Serializers pour la gestion des notes et évaluations
"""
from rest_framework import serializers
from django.db import transaction
from django.db.models import Avg, Count, Q
from decimal import Decimal
from .models import (
    EvaluationType, GradingPeriod, Evaluation, Grade,
    SubjectAverage, GeneralAverage, Competence, CompetenceEvaluation
)
from apps.authentication.serializers import UserSerializer
from apps.timetable.serializers import SubjectSerializer
from apps.schools.serializers import ClassSerializer


class EvaluationTypeSerializer(serializers.ModelSerializer):
    """Serializer pour les types d'évaluation"""
    
    class Meta:
        model = EvaluationType
        fields = [
            'id', 'name', 'short_name', 'default_coefficient',
            'color', 'is_graded'
        ]


class GradingPeriodSerializer(serializers.ModelSerializer):
    """Serializer pour les périodes de notation"""
    academic_year_name = serializers.CharField(
        source='academic_year.name',
        read_only=True
    )
    
    class Meta:
        model = GradingPeriod
        fields = [
            'id', 'academic_year', 'academic_year_name', 'name',
            'number', 'start_date', 'end_date', 'is_active',
            'council_date', 'grades_locked', 'bulletins_published'
        ]
        read_only_fields = ['id']


class GradeSerializer(serializers.ModelSerializer):
    """Serializer pour les notes"""
    student_name = serializers.CharField(
        source='student.get_full_name',
        read_only=True
    )
    normalized_score = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = Grade
        fields = [
            'id', 'evaluation', 'student', 'student_name',
            'score', 'normalized_score', 'is_absent', 'is_excused',
            'is_cheating', 'comment', 'graded_by', 'graded_at'
        ]
        read_only_fields = ['id', 'graded_by', 'graded_at']
    
    def validate_score(self, value):
        """Valider que la note ne dépasse pas le maximum"""
        if value and 'evaluation' in self.initial_data:
            evaluation = Evaluation.objects.get(id=self.initial_data['evaluation'])
            if value > evaluation.max_score:
                raise serializers.ValidationError(
                    f"La note ne peut pas dépasser {evaluation.max_score}"
                )
        return value


class EvaluationListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des évaluations"""
    evaluation_type_name = serializers.CharField(
        source='evaluation_type.name',
        read_only=True
    )
    subject_name = serializers.CharField(
        source='subject.name',
        read_only=True
    )
    class_name = serializers.CharField(
        source='class_group.__str__',
        read_only=True
    )
    teacher_name = serializers.CharField(
        source='teacher.get_full_name',
        read_only=True
    )
    average_score = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    graded_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Evaluation
        fields = [
            'id', 'title', 'evaluation_type', 'evaluation_type_name',
            'subject', 'subject_name', 'class_group', 'class_name',
            'teacher', 'teacher_name', 'date', 'max_score',
            'coefficient', 'is_graded', 'grades_published',
            'average_score', 'graded_count'
        ]


class EvaluationDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour une évaluation"""
    evaluation_type = EvaluationTypeSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)
    class_group = ClassSerializer(read_only=True)
    teacher = UserSerializer(read_only=True)
    grades = GradeSerializer(many=True, read_only=True)
    statistics = serializers.SerializerMethodField()
    
    class Meta:
        model = Evaluation
        fields = [
            'id', 'title', 'description', 'evaluation_type',
            'subject', 'class_group', 'teacher', 'grading_period',
            'date', 'max_score', 'coefficient', 'is_optional',
            'counts_in_average', 'allow_absent_makeup', 'is_graded',
            'grades_published', 'subject_file', 'correction_file',
            'grades', 'statistics', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_statistics(self, obj):
        """Calculer les statistiques de l'évaluation"""
        grades = obj.grades.filter(score__isnull=False, is_absent=False)
        
        if not grades.exists():
            return None
        
        stats = grades.aggregate(
            average=Avg('score'),
            count=Count('id'),
            min_score=models.Min('score'),
            max_score=models.Max('score')
        )
        
        # Distribution des notes
        distribution = {
            'excellent': grades.filter(score__gte=obj.max_score * 0.8).count(),
            'good': grades.filter(
                score__gte=obj.max_score * 0.6,
                score__lt=obj.max_score * 0.8
            ).count(),
            'average': grades.filter(
                score__gte=obj.max_score * 0.4,
                score__lt=obj.max_score * 0.6
            ).count(),
            'below_average': grades.filter(
                score__gte=obj.max_score * 0.2,
                score__lt=obj.max_score * 0.4
            ).count(),
            'poor': grades.filter(score__lt=obj.max_score * 0.2).count()
        }
        
        stats['distribution'] = distribution
        stats['absent_count'] = obj.grades.filter(is_absent=True).count()
        
        return stats


class EvaluationCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer une évaluation"""
    
    class Meta:
        model = Evaluation
        fields = [
            'title', 'description', 'evaluation_type', 'subject',
            'class_group', 'grading_period', 'date', 'max_score',
            'coefficient', 'is_optional', 'counts_in_average',
            'allow_absent_makeup', 'subject_file'
        ]
    
    def create(self, validated_data):
        validated_data['teacher'] = self.context['request'].user
        return super().create(validated_data)


class BulkGradeSerializer(serializers.Serializer):
    """Serializer pour saisir les notes en masse"""
    evaluation_id = serializers.UUIDField()
    grades = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False
    )
    
    def validate_grades(self, value):
        """Valider la liste des notes"""
        required_fields = {'student_id'}
        
        for grade in value:
            if not required_fields.issubset(grade.keys()):
                raise serializers.ValidationError(
                    "Chaque note doit avoir 'student_id'"
                )
            
            # Au moins un des champs doit être présent
            if not any(k in grade for k in ['score', 'is_absent', 'comment']):
                raise serializers.ValidationError(
                    "Au moins un champ (score, is_absent, comment) doit être fourni"
                )
        
        return value


class SubjectAverageSerializer(serializers.ModelSerializer):
    """Serializer pour les moyennes par matière"""
    student_name = serializers.CharField(
        source='student.get_full_name',
        read_only=True
    )
    subject_name = serializers.CharField(
        source='subject.name',
        read_only=True
    )
    
    class Meta:
        model = SubjectAverage
        fields = [
            'id', 'student', 'student_name', 'subject', 'subject_name',
            'grading_period', 'average', 'weighted_average', 'rank',
            'class_size', 'class_average', 'min_average', 'max_average',
            'appreciation'
        ]
        read_only_fields = [
            'id', 'average', 'weighted_average', 'rank',
            'class_size', 'class_average', 'min_average', 'max_average'
        ]


class GeneralAverageSerializer(serializers.ModelSerializer):
    """Serializer pour les moyennes générales"""
    student_name = serializers.CharField(
        source='student.get_full_name',
        read_only=True
    )
    subject_averages = SubjectAverageSerializer(
        source='student.subject_averages',
        many=True,
        read_only=True
    )
    
    class Meta:
        model = GeneralAverage
        fields = [
            'id', 'student', 'student_name', 'grading_period',
            'average', 'weighted_average', 'rank', 'class_size',
            'class_average', 'council_decision', 'honor_roll',
            'general_appreciation', 'subject_averages',
            'validated_by', 'validated_at'
        ]
        read_only_fields = [
            'id', 'average', 'weighted_average', 'rank',
            'class_size', 'class_average', 'validated_by', 'validated_at'
        ]


class CompetenceSerializer(serializers.ModelSerializer):
    """Serializer pour les compétences"""
    subject_name = serializers.CharField(
        source='subject.name',
        read_only=True
    )
    
    class Meta:
        model = Competence
        fields = [
            'id', 'name', 'code', 'description', 'domain',
            'subject', 'subject_name'
        ]


class CompetenceEvaluationSerializer(serializers.ModelSerializer):
    """Serializer pour l'évaluation des compétences"""
    student_name = serializers.CharField(
        source='student.get_full_name',
        read_only=True
    )
    competence_name = serializers.CharField(
        source='competence.name',
        read_only=True
    )
    mastery_level_display = serializers.CharField(
        source='get_mastery_level_display',
        read_only=True
    )
    
    class Meta:
        model = CompetenceEvaluation
        fields = [
            'id', 'student', 'student_name', 'competence',
            'competence_name', 'evaluation', 'grading_period',
            'mastery_level', 'mastery_level_display', 'comment',
            'evaluated_by', 'evaluated_at'
        ]
        read_only_fields = ['id', 'evaluated_by', 'evaluated_at']
    
    def create(self, validated_data):
        validated_data['evaluated_by'] = self.context['request'].user
        return super().create(validated_data)


class StudentReportCardSerializer(serializers.Serializer):
    """
    Serializer pour générer le bulletin d'un élève
    """
    student_id = serializers.UUIDField()
    grading_period_id = serializers.UUIDField()
    
    def to_representation(self, instance):
        """Générer le bulletin complet"""
        student = User.objects.get(id=instance['student_id'])
        period = GradingPeriod.objects.get(id=instance['grading_period_id'])
        
        # Récupérer la moyenne générale
        general_avg = GeneralAverage.objects.filter(
            student=student,
            grading_period=period
        ).first()
        
        # Récupérer toutes les moyennes par matière
        subject_avgs = SubjectAverage.objects.filter(
            student=student,
            grading_period=period
        ).select_related('subject').order_by('subject__name')
        
        # Récupérer les évaluations de compétences
        competence_evals = CompetenceEvaluation.objects.filter(
            student=student,
            grading_period=period
        ).select_related('competence').order_by('competence__domain', 'competence__name')
        
        # Construire le bulletin
        report_card = {
            'student': UserSerializer(student).data,
            'grading_period': GradingPeriodSerializer(period).data,
            'general_average': GeneralAverageSerializer(general_avg).data if general_avg else None,
            'subject_averages': SubjectAverageSerializer(subject_avgs, many=True).data,
            'competence_evaluations': CompetenceEvaluationSerializer(competence_evals, many=True).data,
            'attendance_summary': self._get_attendance_summary(student, period),
            'behavior_summary': self._get_behavior_summary(student, period)
        }
        
        return report_card
    
    def _get_attendance_summary(self, student, period):
        """Résumé des absences pour la période"""
        from apps.attendance.models import Attendance, AttendanceStatus
        
        attendances = Attendance.objects.filter(
            student=student,
            date__range=[period.start_date, period.end_date]
        )
        
        return {
            'total_hours': attendances.count(),
            'absences': attendances.filter(status=AttendanceStatus.ABSENT).count(),
            'justified_absences': attendances.filter(
                status=AttendanceStatus.ABSENT,
                is_justified=True
            ).count(),
            'delays': attendances.filter(status=AttendanceStatus.LATE).count()
        }
    
    def _get_behavior_summary(self, student, period):
        """Résumé du comportement pour la période"""
        from apps.attendance.models import StudentBehavior, Sanction
        
        behaviors = StudentBehavior.objects.filter(
            student=student,
            date__range=[period.start_date, period.end_date]
        )
        
        sanctions = Sanction.objects.filter(
            student=student,
            date__range=[period.start_date, period.end_date]
        )
        
        return {
            'positive_points': behaviors.filter(
                behavior_type='positive'
            ).aggregate(total=models.Sum('points'))['total'] or 0,
            'negative_points': behaviors.filter(
                behavior_type='negative'
            ).aggregate(total=models.Sum('points'))['total'] or 0,
            'sanctions_count': sanctions.count(),
            'sanctions': [
                {
                    'type': s.get_sanction_type_display(),
                    'date': s.date,
                    'reason': s.reason
                }
                for s in sanctions[:3]  # Les 3 dernières sanctions
            ]
        }