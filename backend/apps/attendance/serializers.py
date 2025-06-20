"""
Serializers pour la gestion de la vie scolaire
"""
from rest_framework import serializers
from django.db.models import Count, Q
from django.utils import timezone
from datetime import date, timedelta
from .models import (
    Attendance, AbsencePeriod, Sanction,
    StudentBehavior, AttendanceAlert, AttendanceStatus
)
from apps.authentication.serializers import UserSerializer
from apps.timetable.serializers import ScheduleListSerializer


class AttendanceSerializer(serializers.ModelSerializer):
    """Serializer pour les présences"""
    student_name = serializers.CharField(
        source='student.get_full_name',
        read_only=True
    )
    schedule_info = ScheduleListSerializer(
        source='schedule',
        read_only=True
    )
    recorded_by_name = serializers.CharField(
        source='recorded_by.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'student', 'student_name', 'schedule',
            'schedule_info', 'date', 'status', 'arrival_time',
            'late_minutes', 'is_justified', 'justification_reason',
            'justification_document', 'recorded_by', 'recorded_by_name',
            'recorded_at', 'modified_at'
        ]
        read_only_fields = ['id', 'recorded_by', 'recorded_at', 'late_minutes']
    
    def validate(self, attrs):
        """Validation personnalisée"""
        status = attrs.get('status')
        arrival_time = attrs.get('arrival_time')
        
        if status == AttendanceStatus.LATE and not arrival_time:
            raise serializers.ValidationError({
                'arrival_time': "L'heure d'arrivée est requise pour un retard"
            })
        
        return attrs
    
    def create(self, validated_data):
        validated_data['recorded_by'] = self.context['request'].user
        return super().create(validated_data)


class AttendanceBulkSerializer(serializers.Serializer):
    """Serializer pour l'appel en masse"""
    schedule_id = serializers.UUIDField()
    date = serializers.DateField()
    attendances = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False
    )
    
    def validate_attendances(self, value):
        """Valider la liste des présences"""
        required_fields = {'student_id', 'status'}
        
        for attendance in value:
            if not required_fields.issubset(attendance.keys()):
                raise serializers.ValidationError(
                    "Chaque présence doit avoir 'student_id' et 'status'"
                )
            
            # Valider le statut
            if attendance['status'] not in AttendanceStatus.values:
                raise serializers.ValidationError(
                    f"Statut invalide: {attendance['status']}"
                )
        
        return value


class AbsencePeriodSerializer(serializers.ModelSerializer):
    """Serializer pour les périodes d'absence"""
    student_name = serializers.CharField(
        source='student.get_full_name',
        read_only=True
    )
    duration_days = serializers.IntegerField(
        source='get_duration_days',
        read_only=True
    )
    notified_by_name = serializers.CharField(
        source='notified_by.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = AbsencePeriod
        fields = [
            'id', 'student', 'student_name', 'start_date',
            'end_date', 'duration_days', 'reason', 'is_justified',
            'justification_document', 'notified_by', 'notified_by_name',
            'notified_at'
        ]
        read_only_fields = ['id', 'notified_by', 'notified_at']
    
    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if end_date < start_date:
            raise serializers.ValidationError({
                'end_date': "La date de fin doit être après la date de début"
            })
        
        return attrs
    
    def create(self, validated_data):
        validated_data['notified_by'] = self.context['request'].user
        return super().create(validated_data)


class SanctionSerializer(serializers.ModelSerializer):
    """Serializer pour les sanctions"""
    student_name = serializers.CharField(
        source='student.get_full_name',
        read_only=True
    )
    given_by_name = serializers.CharField(
        source='given_by.get_full_name',
        read_only=True
    )
    sanction_type_display = serializers.CharField(
        source='get_sanction_type_display',
        read_only=True
    )
    
    class Meta:
        model = Sanction
        fields = [
            'id', 'student', 'student_name', 'sanction_type',
            'sanction_type_display', 'date', 'reason', 'description',
            'detention_date', 'detention_start_time', 'detention_end_time',
            'detention_room', 'exclusion_start_date', 'exclusion_end_date',
            'given_by', 'given_by_name', 'is_completed', 'completion_notes',
            'parents_notified', 'notification_date', 'created_at'
        ]
        read_only_fields = ['id', 'given_by', 'created_at']
    
    def create(self, validated_data):
        validated_data['given_by'] = self.context['request'].user
        return super().create(validated_data)


class StudentBehaviorSerializer(serializers.ModelSerializer):
    """Serializer pour le comportement"""
    student_name = serializers.CharField(
        source='student.get_full_name',
        read_only=True
    )
    recorded_by_name = serializers.CharField(
        source='recorded_by.get_full_name',
        read_only=True
    )
    behavior_type_display = serializers.CharField(
        source='get_behavior_type_display',
        read_only=True
    )
    
    class Meta:
        model = StudentBehavior
        fields = [
            'id', 'student', 'student_name', 'date',
            'behavior_type', 'behavior_type_display',
            'category', 'description', 'points',
            'recorded_by', 'recorded_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'recorded_by', 'created_at']
    
    def create(self, validated_data):
        validated_data['recorded_by'] = self.context['request'].user
        return super().create(validated_data)


class AttendanceAlertSerializer(serializers.ModelSerializer):
    """Serializer pour les alertes"""
    student_name = serializers.CharField(
        source='student.get_full_name',
        read_only=True
    )
    alert_type_display = serializers.CharField(
        source='get_alert_type_display',
        read_only=True
    )
    resolved_by_name = serializers.CharField(
        source='resolved_by.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = AttendanceAlert
        fields = [
            'id', 'student', 'student_name', 'alert_type',
            'alert_type_display', 'threshold_value', 'period_start',
            'period_end', 'message', 'details', 'is_resolved',
            'resolved_by', 'resolved_by_name', 'resolved_at',
            'resolution_notes', 'created_at'
        ]
        read_only_fields = [
            'id', 'resolved_by', 'resolved_at', 'created_at'
        ]


class AttendanceStatsSerializer(serializers.Serializer):
    """Serializer pour les statistiques de présence"""
    student_id = serializers.UUIDField(required=False)
    class_id = serializers.UUIDField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    
    def to_representation(self, instance):
        """Calculer les statistiques"""
        # Instance peut être un queryset d'attendances
        total = instance.count()
        
        if total == 0:
            return {
                'total_courses': 0,
                'present': 0,
                'absent': 0,
                'late': 0,
                'excused': 0,
                'attendance_rate': 100.0,
                'punctuality_rate': 100.0
            }
        
        stats = instance.aggregate(
            present=Count('id', filter=Q(status=AttendanceStatus.PRESENT)),
            absent=Count('id', filter=Q(status=AttendanceStatus.ABSENT)),
            late=Count('id', filter=Q(status=AttendanceStatus.LATE)),
            excused=Count('id', filter=Q(status=AttendanceStatus.EXCUSED))
        )
        
        present_and_late = stats['present'] + stats['late']
        attendance_rate = (present_and_late / total * 100) if total > 0 else 0
        punctuality_rate = (stats['present'] / total * 100) if total > 0 else 0
        
        return {
            'total_courses': total,
            'present': stats['present'],
            'absent': stats['absent'],
            'late': stats['late'],
            'excused': stats['excused'],
            'attendance_rate': round(attendance_rate, 2),
            'punctuality_rate': round(punctuality_rate, 2),
            'absence_rate': round(100 - attendance_rate, 2),
            'late_rate': round(stats['late'] / total * 100, 2) if total > 0 else 0
        }


class DailyAttendanceReportSerializer(serializers.Serializer):
    """Serializer pour le rapport journalier de présence"""
    date = serializers.DateField()
    class_id = serializers.UUIDField()
    
    def to_representation(self, instance):
        """Générer le rapport journalier"""
        # Instance est un dictionnaire avec date et class_id
        date = instance['date']
        class_id = instance['class_id']
        
        # Récupérer tous les cours de la journée pour cette classe
        from apps.timetable.models import Schedule
        from apps.schools.models import Class
        
        class_obj = Class.objects.get(id=class_id)
        day_of_week = date.weekday()
        
        schedules = Schedule.objects.filter(
            class_group=class_obj,
            time_slot__day=day_of_week,
            is_cancelled=False
        ).select_related('subject', 'teacher', 'time_slot')
        
        report = {
            'date': date,
            'class': {
                'id': str(class_obj.id),
                'name': str(class_obj)
            },
            'courses': []
        }
        
        for schedule in schedules:
            attendances = Attendance.objects.filter(
                schedule=schedule,
                date=date
            ).select_related('student')
            
            course_data = {
                'schedule': ScheduleListSerializer(schedule).data,
                'attendance_summary': {
                    'total_students': class_obj.students.filter(is_active=True).count(),
                    'present': attendances.filter(status=AttendanceStatus.PRESENT).count(),
                    'absent': attendances.filter(status=AttendanceStatus.ABSENT).count(),
                    'late': attendances.filter(status=AttendanceStatus.LATE).count(),
                    'excused': attendances.filter(status=AttendanceStatus.EXCUSED).count(),
                },
                'missing_attendance': []
            }
            
            # Identifier les élèves sans enregistrement de présence
            recorded_students = set(attendances.values_list('student_id', flat=True))
            all_students = set(class_obj.students.filter(
                is_active=True
            ).values_list('student_id', flat=True))
            
            missing_students = all_students - recorded_students
            if missing_students:
                from apps.authentication.models import User
                missing_users = User.objects.filter(id__in=missing_students)
                course_data['missing_attendance'] = [
                    {
                        'id': str(user.id),
                        'name': user.get_full_name()
                    }
                    for user in missing_users
                ]
            
            report['courses'].append(course_data)
        
        return report