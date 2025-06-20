"""
Serializers pour la gestion du cahier de textes et des devoirs
"""
from rest_framework import serializers
from django.utils import timezone
from django.db.models import Count, Avg, Q
from .models import (
    LessonContent, HomeworkType, Homework, HomeworkResource,
    StudentWork, HomeworkTemplate, WorkloadAnalysis
)
from apps.authentication.serializers import UserSerializer
from apps.timetable.serializers import ScheduleListSerializer, SubjectSerializer
from apps.schools.serializers import ClassSerializer


class LessonContentSerializer(serializers.ModelSerializer):
    """Serializer pour le contenu des cours"""
    schedule_info = ScheduleListSerializer(source='schedule', read_only=True)
    created_by_name = serializers.CharField(
        source='created_by.get_full_name',
        read_only=True
    )
    has_homework = serializers.BooleanField(read_only=True)
    homework_count = serializers.IntegerField(
        source='homework_assignments.count',
        read_only=True
    )
    
    class Meta:
        model = LessonContent
        fields = [
            'id', 'schedule', 'schedule_info', 'date', 'title',
            'objectives', 'content', 'key_concepts', 'skills_worked',
            'duration_minutes', 'is_catch_up', 'chapter',
            'sequence_number', 'created_by', 'created_by_name',
            'validated', 'validated_by', 'validated_at',
            'has_homework', 'homework_count', 'created_at'
        ]
        read_only_fields = [
            'id', 'created_by', 'validated_by', 'validated_at', 'created_at'
        ]
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class HomeworkTypeSerializer(serializers.ModelSerializer):
    """Serializer pour les types de devoirs"""
    
    class Meta:
        model = HomeworkType
        fields = [
            'id', 'name', 'short_name', 'icon',
            'default_duration_days', 'color'
        ]


class HomeworkResourceSerializer(serializers.ModelSerializer):
    """Serializer pour les ressources"""
    uploaded_by_name = serializers.CharField(
        source='uploaded_by.get_full_name',
        read_only=True
    )
    size_mb = serializers.FloatField(read_only=True)
    
    class Meta:
        model = HomeworkResource
        fields = [
            'id', 'homework', 'lesson_content', 'resource_type',
            'title', 'description', 'file', 'url', 'is_mandatory',
            'order', 'download_count', 'uploaded_by',
            'uploaded_by_name', 'size_mb', 'created_at'
        ]
        read_only_fields = ['id', 'uploaded_by', 'download_count', 'created_at']
    
    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)


class StudentWorkSerializer(serializers.ModelSerializer):
    """Serializer pour les travaux d'élèves"""
    student_name = serializers.CharField(
        source='student.get_full_name',
        read_only=True
    )
    homework_title = serializers.CharField(
        source='homework.title',
        read_only=True
    )
    is_late = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentWork
        fields = [
            'id', 'homework', 'homework_title', 'student',
            'student_name', 'status', 'submitted_at', 'content',
            'file', 'student_comment', 'grade', 'teacher_comment',
            'corrected_file', 'corrected_at', 'corrected_by',
            'time_spent_minutes', 'is_late', 'created_at'
        ]
        read_only_fields = [
            'id', 'corrected_at', 'corrected_by', 'created_at'
        ]
    
    def get_is_late(self, obj):
        """Vérifier si le rendu est en retard"""
        if obj.submitted_at and obj.homework.due_date:
            return obj.submitted_at.date() > obj.homework.due_date
        return False
    
    def update(self, instance, validated_data):
        """Gérer la soumission et la correction"""
        # Si on passe le statut à 'submitted'
        if validated_data.get('status') == 'submitted' and instance.status != 'submitted':
            instance.submitted_at = timezone.now()
            if timezone.now().date() > instance.homework.due_date:
                validated_data['status'] = 'late'
        
        # Si on ajoute une note
        if validated_data.get('grade') is not None and instance.grade is None:
            instance.corrected_at = timezone.now()
            instance.corrected_by = self.context['request'].user
            validated_data['status'] = 'returned'
        
        return super().update(instance, validated_data)


class HomeworkListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des devoirs"""
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
    homework_type_name = serializers.CharField(
        source='homework_type.name',
        read_only=True
    )
    is_overdue = serializers.BooleanField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    submission_rate = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Homework
        fields = [
            'id', 'subject', 'subject_name', 'class_group', 'class_name',
            'teacher', 'teacher_name', 'homework_type', 'homework_type_name',
            'title', 'assigned_date', 'due_date', 'difficulty',
            'estimated_duration_minutes', 'is_graded', 'submission_type',
            'is_overdue', 'days_remaining', 'submission_rate',
            'is_ai_suggested', 'view_count'
        ]


class HomeworkDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour un devoir"""
    lesson_content = LessonContentSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)
    class_group = ClassSerializer(read_only=True)
    teacher = UserSerializer(read_only=True)
    homework_type = HomeworkTypeSerializer(read_only=True)
    resources = HomeworkResourceSerializer(many=True, read_only=True)
    statistics = serializers.SerializerMethodField()
    
    class Meta:
        model = Homework
        fields = [
            'id', 'lesson_content', 'subject', 'class_group', 'teacher',
            'homework_type', 'title', 'description', 'instructions',
            'assigned_date', 'due_date', 'estimated_duration_minutes',
            'difficulty', 'is_graded', 'allow_late_submission',
            'submission_type', 'max_file_size_mb', 'allowed_file_types',
            'is_ai_suggested', 'ai_suggestion_data', 'view_count',
            'resources', 'statistics', 'created_at'
        ]
        read_only_fields = ['id', 'view_count', 'created_at']
    
    def get_statistics(self, obj):
        """Calculer les statistiques du devoir"""
        submissions = obj.submissions.all()
        total_students = obj.class_group.students.filter(is_active=True).count()
        
        stats = {
            'total_students': total_students,
            'submissions_count': submissions.count(),
            'submission_rate': (submissions.count() / total_students * 100) if total_students > 0 else 0,
            'submitted_on_time': submissions.filter(status='submitted').count(),
            'submitted_late': submissions.filter(status='late').count(),
            'graded_count': submissions.filter(grade__isnull=False).count(),
        }
        
        # Si noté, ajouter les stats de notes
        if obj.is_graded:
            graded = submissions.filter(grade__isnull=False)
            if graded.exists():
                grade_stats = graded.aggregate(
                    average_grade=Avg('grade'),
                    min_grade=models.Min('grade'),
                    max_grade=models.Max('grade')
                )
                stats.update(grade_stats)
        
        return stats


class HomeworkCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un devoir"""
    resources = HomeworkResourceSerializer(many=True, required=False)
    
    class Meta:
        model = Homework
        fields = [
            'lesson_content', 'subject', 'class_group', 'homework_type',
            'title', 'description', 'instructions', 'due_date',
            'estimated_duration_minutes', 'difficulty', 'is_graded',
            'allow_late_submission', 'submission_type', 'max_file_size_mb',
            'allowed_file_types', 'resources'
        ]
    
    def create(self, validated_data):
        resources_data = validated_data.pop('resources', [])
        validated_data['teacher'] = self.context['request'].user
        
        homework = Homework.objects.create(**validated_data)
        
        # Créer les ressources associées
        for resource_data in resources_data:
            HomeworkResource.objects.create(
                homework=homework,
                uploaded_by=self.context['request'].user,
                **resource_data
            )
        
        return homework


class HomeworkTemplateSerializer(serializers.ModelSerializer):
    """Serializer pour les modèles de devoirs"""
    subject_name = serializers.CharField(
        source='subject.name',
        read_only=True
    )
    teacher_name = serializers.CharField(
        source='teacher.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = HomeworkTemplate
        fields = [
            'id', 'subject', 'subject_name', 'teacher', 'teacher_name',
            'name', 'chapter', 'level', 'title', 'description',
            'instructions', 'homework_type', 'estimated_duration_minutes',
            'difficulty', 'tags', 'use_count', 'is_shared', 'created_at'
        ]
        read_only_fields = ['id', 'teacher', 'use_count', 'created_at']
    
    def create(self, validated_data):
        validated_data['teacher'] = self.context['request'].user
        return super().create(validated_data)


class WorkloadAnalysisSerializer(serializers.ModelSerializer):
    """Serializer pour l'analyse de charge de travail"""
    class_name = serializers.CharField(
        source='class_group.__str__',
        read_only=True
    )
    
    class Meta:
        model = WorkloadAnalysis
        fields = [
            'id', 'class_group', 'class_name', 'date',
            'total_homework_count', 'total_estimated_minutes',
            'homework_by_subject', 'is_overloaded', 'overload_level',
            'recommendations', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class HomeworkSuggestionSerializer(serializers.Serializer):
    """Serializer pour les suggestions de devoirs par l'IA"""
    chapter = serializers.CharField(required=True)
    subject_id = serializers.UUIDField(required=True)
    class_level = serializers.CharField(required=True)
    lesson_objectives = serializers.CharField(required=False)
    key_concepts = serializers.CharField(required=False)
    difficulty = serializers.ChoiceField(
        choices=Homework.DIFFICULTY_CHOICES,
        default='medium'
    )
    homework_type = serializers.CharField(required=False)
    
    def to_representation(self, instance):
        """Retourner les suggestions générées"""
        # Instance contient les suggestions générées par l'IA
        return {
            'suggestions': instance.get('suggestions', []),
            'chapter': instance.get('chapter'),
            'generated_at': timezone.now()
        }


class StudentHomeworkViewSerializer(serializers.Serializer):
    """
serializer pour la vue des devoirs d'un élève"""
    date = serializers.DateField(required=False)
    subject_id = serializers.UUIDField(required=False)
    status = serializers.ChoiceField(
        choices=['all', 'pending', 'submitted', 'late', 'graded'],
        default='all'
    )
    
    def to_representation(self, instance):
        """Retourner les devoirs organisés pour l'élève"""
        # Instance est un queryset de devoirs
        homework_list = []
        
        for homework in instance:
            # Récupérer le travail de l'élève s'il existe
            student_work = homework.submissions.filter(
                student=self.context['request'].user
            ).first()
            
            homework_data = HomeworkListSerializer(homework).data
            homework_data['my_work'] = {
                'status': student_work.status if student_work else 'not_started',
                'submitted_at': student_work.submitted_at if student_work else None,
                'grade': student_work.grade if student_work else None,
                'teacher_comment': student_work.teacher_comment if student_work else None
            }
            
            homework_list.append(homework_data)
        
        # Organiser par date de rendu
        upcoming = [h for h in homework_list if not h['is_overdue']]
        overdue = [h for h in homework_list if h['is_overdue']]
        
        return {
            'upcoming': sorted(upcoming, key=lambda x: x['due_date']),
            'overdue': sorted(overdue, key=lambda x: x['due_date'], reverse=True),
            'total_count': len(homework_list)
        }


class TeacherDashboardSerializer(serializers.Serializer):
    """Serializer pour le tableau de bord professeur"""
    
    def to_representation(self, instance):
        """Générer le tableau de bord"""
        user = self.context['request'].user
        today = timezone.now().date()
        
        # Devoirs à corriger
        pending_corrections = StudentWork.objects.filter(
            homework__teacher=user,
            status='submitted',
            grade__isnull=True
        ).count()
        
        # Devoirs récemment assignés
        recent_homework = Homework.objects.filter(
            teacher=user,
            assigned_date__gte=today - timezone.timedelta(days=7)
        ).count()
        
        # Taux de rendu moyen
        homework_with_submissions = Homework.objects.filter(
            teacher=user,
            due_date__lt=today
        ).annotate(
            submission_count=Count('submissions')
        )
        
        avg_submission_rate = 0
        if homework_with_submissions.exists():
            rates = []
            for hw in homework_with_submissions:
                total = hw.class_group.students.filter(is_active=True).count()
                if total > 0:
                    rates.append(hw.submission_count / total * 100)
            if rates:
                avg_submission_rate = sum(rates) / len(rates)
        
        # Cours à remplir
        from apps.timetable.models import Schedule
        schedules_without_content = Schedule.objects.filter(
            teacher=user,
            lesson_contents__isnull=True
        ).count()
        
        return {
            'pending_corrections': pending_corrections,
            'recent_homework_count': recent_homework,
            'average_submission_rate': round(avg_submission_rate, 2),
            'schedules_to_fill': schedules_without_content,
            'quick_stats': {
                'total_homework_assigned': Homework.objects.filter(teacher=user).count(),
                'total_lessons': LessonContent.objects.filter(created_by=user).count(),
                'templates_created': HomeworkTemplate.objects.filter(teacher=user).count()
            }
        }