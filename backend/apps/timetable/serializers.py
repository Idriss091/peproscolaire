"""
Serializers pour l'application emploi du temps
"""
from rest_framework import serializers
from django.db import transaction
from .models import (
    Subject, Room, TimeSlot, Schedule,
    ScheduleModification
)
from apps.schools.models import Class, AcademicYear
from apps.authentication.serializers import UserSerializer


class SubjectSerializer(serializers.ModelSerializer):
    """Serializer pour les matières"""
    
    class Meta:
        model = Subject
        fields = [
            'id', 'name', 'short_name', 'color',
            'coefficient', 'is_optional'
        ]


class RoomSerializer(serializers.ModelSerializer):
    """Serializer pour les salles"""
    
    class Meta:
        model = Room
        fields = [
            'id', 'name', 'building', 'floor',
            'capacity', 'room_type', 'is_available'
        ]
        read_only_fields = ['id']


class TimeSlotSerializer(serializers.ModelSerializer):
    """Serializer pour les créneaux horaires"""
    day_display = serializers.CharField(
        source='get_day_display',
        read_only=True
    )
    
    class Meta:
        model = TimeSlot
        fields = [
            'id', 'day', 'day_display', 'start_time',
            'end_time', 'order', 'is_break'
        ]
        read_only_fields = ['id']


class ScheduleListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des cours"""
    subject = SubjectSerializer(read_only=True)
    teacher = UserSerializer(read_only=True)
    room = RoomSerializer(read_only=True)
    time_slot = TimeSlotSerializer(read_only=True)
    class_name = serializers.CharField(
        source='class_group.__str__',
        read_only=True
    )
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'class_name', 'subject', 'teacher',
            'room', 'time_slot', 'week_type',
            'start_date', 'end_date', 'is_cancelled'
        ]


class ScheduleCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer/modifier un cours"""
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'academic_year', 'class_group', 'subject',
            'teacher', 'room', 'time_slot', 'week_type',
            'start_date', 'end_date'
        ]
        read_only_fields = ['id']
    
    def validate(self, attrs):
        """Validation des conflits d'emploi du temps"""
        instance = self.instance
        
        # Récupération des valeurs
        academic_year = attrs.get('academic_year', instance.academic_year if instance else None)
        teacher = attrs.get('teacher', instance.teacher if instance else None)
        room = attrs.get('room', instance.room if instance else None)
        time_slot = attrs.get('time_slot', instance.time_slot if instance else None)
        week_type = attrs.get('week_type', instance.week_type if instance else '*')
        class_group = attrs.get('class_group', instance.class_group if instance else None)
        
        # Vérifications des conflits
        base_query = Schedule.objects.filter(
            academic_year=academic_year,
            time_slot=time_slot,
            is_cancelled=False
        )
        
        if week_type == '*':
            base_query = base_query.filter(week_type__in=['*', 'A', 'B'])
        else:
            base_query = base_query.filter(week_type__in=[week_type, '*'])
        
        if instance:
            base_query = base_query.exclude(pk=instance.pk)
        
        # Conflit professeur
        if base_query.filter(teacher=teacher).exists():
            raise serializers.ValidationError({
                'teacher': 'Ce professeur a déjà un cours à ce créneau.'
            })
        
        # Conflit salle
        if room and base_query.filter(room=room).exists():
            raise serializers.ValidationError({
                'room': 'Cette salle est déjà occupée à ce créneau.'
            })
        
        # Conflit classe
        if base_query.filter(class_group=class_group).exists():
            raise serializers.ValidationError({
                'class_group': 'Cette classe a déjà un cours à ce créneau.'
            })
        
        return attrs


class ScheduleModificationSerializer(serializers.ModelSerializer):
    """Serializer pour les modifications de cours"""
    schedule_info = ScheduleListSerializer(source='schedule', read_only=True)
    created_by_name = serializers.CharField(
        source='created_by.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = ScheduleModification
        fields = [
            'id', 'schedule', 'schedule_info', 'date',
            'modification_type', 'substitute_teacher',
            'new_room', 'new_start_time', 'new_end_time',
            'reason', 'created_by', 'created_by_name',
            'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class TimetableSerializer(serializers.Serializer):
    """
    Serializer pour afficher l'emploi du temps complet
    Format optimisé pour l'affichage frontend
    """
    week_type = serializers.CharField(required=False, default='*')
    date = serializers.DateField(required=False)
    
    def to_representation(self, instance):
        """
        Retourne l'emploi du temps sous forme de grille
        instance peut être une Class, un User (prof/élève) ou une Room
        """
        request = self.context.get('request')
        week_type = request.query_params.get('week_type', '*')
        
        # Récupération des créneaux horaires
        school = None
        schedules_query = Schedule.objects.filter(is_cancelled=False)
        
        if hasattr(instance, 'school'):  # Class ou Room
            school = instance.school
            if isinstance(instance, Class):
                schedules_query = schedules_query.filter(class_group=instance)
            else:  # Room
                schedules_query = schedules_query.filter(room=instance)
        else:  # User
            if instance.user_type == 'teacher':
                schedules_query = schedules_query.filter(teacher=instance)
            elif instance.user_type == 'student':
                # Récupérer la classe de l'élève
                enrollment = instance.enrollments.filter(is_active=True).first()
                if enrollment:
                    schedules_query = schedules_query.filter(
                        class_group=enrollment.class_group
                    )
                    school = enrollment.class_group.school
        
        if not school:
            return {'error': 'Impossible de déterminer l\'établissement'}
        
        # Filtrer par type de semaine
        if week_type != '*':
            schedules_query = schedules_query.filter(
                week_type__in=[week_type, '*']
            )
        
        # Récupération des créneaux horaires de l'école
        time_slots = TimeSlot.objects.filter(
            school=school,
            is_break=False
        ).order_by('day', 'order')
        
        # Construction de la grille
        timetable = {}
        days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
        
        for day_num, day_name in enumerate(days[:6]):
            timetable[day_name] = {}
            day_slots = time_slots.filter(day=day_num)
            
            for slot in day_slots:
                slot_key = f"{slot.start_time:%H:%M}-{slot.end_time:%H:%M}"
                schedule = schedules_query.filter(time_slot=slot).first()
                
                if schedule:
                    timetable[day_name][slot_key] = {
                        'id': str(schedule.id),
                        'subject': schedule.subject.name,
                        'subject_color': schedule.subject.color,
                        'teacher': schedule.teacher.get_full_name(),
                        'room': schedule.room.name if schedule.room else None,
                        'is_modified': False
                    }
                    
                    # Vérifier s'il y a une modification aujourd'hui
                    if 'date' in request.query_params:
                        date = request.query_params.get('date')
                        modification = schedule.modifications.filter(
                            date=date
                        ).first()
                        
                        if modification:
                            timetable[day_name][slot_key]['is_modified'] = True
                            timetable[day_name][slot_key]['modification'] = {
                                'type': modification.modification_type,
                                'reason': modification.reason
                            }
                else:
                    timetable[day_name][slot_key] = None
        
        return {
            'timetable': timetable,
            'time_slots': TimeSlotSerializer(
                time_slots.distinct('start_time', 'end_time'),
                many=True
            ).data,
            'week_type': week_type
        }