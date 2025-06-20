"""
Vues API pour la gestion des emplois du temps
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Prefetch
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from datetime import datetime, timedelta

from .models import (
    Subject, Room, TimeSlot, Schedule,
    ScheduleModification
)
from .serializers import (
    SubjectSerializer, RoomSerializer, TimeSlotSerializer,
    ScheduleListSerializer, ScheduleCreateSerializer,
    ScheduleModificationSerializer, TimetableSerializer
)
from apps.schools.models import Class, School
from apps.authentication.models import User


class SubjectViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des matières"""
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['is_optional']
    search_fields = ['name', 'short_name']
    ordering_fields = ['name', 'coefficient']


class RoomViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des salles"""
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['room_type', 'is_available', 'building']
    search_fields = ['name', 'building']
    ordering_fields = ['name', 'capacity']
    
    def get_queryset(self):
        """Filtrer les salles par école de l'utilisateur"""
        user = self.request.user
        
        # Pour un admin, récupérer son école
        if user.user_type == 'admin':
            # TODO: Implémenter la relation admin-école
            return Room.objects.all()
        
        # Pour un professeur, récupérer via ses cours
        if user.user_type == 'teacher':
            schools = School.objects.filter(
                classes__schedules__teacher=user
            ).distinct()
            return Room.objects.filter(school__in=schools)
        
        # Pour un élève, récupérer via sa classe
        if user.user_type == 'student':
            schools = School.objects.filter(
                classes__students__student=user
            ).distinct()
            return Room.objects.filter(school__in=schools)
        
        return Room.objects.none()
    
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """Vérifier la disponibilité d'une salle"""
        room = self.get_object()
        date = request.query_params.get('date', datetime.now().date())
        
        # Récupérer les créneaux occupés
        occupied_slots = Schedule.objects.filter(
            room=room,
            is_cancelled=False
        ).values_list('time_slot_id', flat=True)
        
        # Récupérer tous les créneaux
        all_slots = TimeSlot.objects.filter(
            school=room.school,
            is_break=False
        )
        
        available_slots = all_slots.exclude(id__in=occupied_slots)
        
        return Response({
            'room': RoomSerializer(room).data,
            'available_slots': TimeSlotSerializer(available_slots, many=True).data,
            'date': date
        })


class TimeSlotViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des créneaux horaires"""
    serializer_class = TimeSlotSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrer par école"""
        user = self.request.user
        school_id = self.request.query_params.get('school_id')
        
        if school_id:
            return TimeSlot.objects.filter(school_id=school_id)
        
        # Logique similaire à RoomViewSet pour déterminer l'école
        return TimeSlot.objects.all()


class ScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des cours"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['academic_year', 'class_group', 'teacher', 'subject', 'week_type']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ScheduleCreateSerializer
        return ScheduleListSerializer
    
    def get_queryset(self):
        """Filtrer selon le type d'utilisateur"""
        user = self.request.user
        queryset = Schedule.objects.select_related(
            'subject', 'teacher', 'room', 'time_slot', 'class_group'
        )
        
        if user.user_type == 'teacher':
            # Un prof voit ses cours + ceux de ses classes
            return queryset.filter(
                Q(teacher=user) |
                Q(class_group__main_teacher=user)
            ).distinct()
        
        elif user.user_type == 'student':
            # Un élève voit les cours de sa classe
            return queryset.filter(
                class_group__students__student=user,
                class_group__students__is_active=True
            )
        
        # Admin voit tout
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_schedule(self, request):
        """Récupérer son propre emploi du temps"""
        user = request.user
        serializer = TimetableSerializer(
            user,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def class_schedule(self, request):
        """Récupérer l'emploi du temps d'une classe"""
        class_id = request.query_params.get('class_id')
        if not class_id:
            return Response(
                {'error': 'class_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        class_obj = get_object_or_404(Class, id=class_id)
        
        # Vérifier les permissions
        user = request.user
        if user.user_type == 'student':
            # Un élève ne peut voir que sa classe
            if not class_obj.students.filter(student=user, is_active=True).exists():
                return Response(
                    {'error': 'Vous n\'avez pas accès à cette classe'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = TimetableSerializer(
            class_obj,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def teacher_schedule(self, request):
        """Récupérer l'emploi du temps d'un professeur"""
        teacher_id = request.query_params.get('teacher_id')
        if not teacher_id:
            return Response(
                {'error': 'teacher_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        teacher = get_object_or_404(User, id=teacher_id, user_type='teacher')
        
        serializer = TimetableSerializer(
            teacher,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def room_schedule(self, request):
        """Récupérer l'emploi du temps d'une salle"""
        room_id = request.query_params.get('room_id')
        if not room_id:
            return Response(
                {'error': 'room_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        room = get_object_or_404(Room, id=room_id)
        
        serializer = TimetableSerializer(
            room,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Annuler un cours"""
        schedule = self.get_object()
        date = request.data.get('date')
        reason = request.data.get('reason', '')
        
        if not date:
            return Response(
                {'error': 'La date est requise'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Créer une modification d'annulation
        modification = ScheduleModification.objects.create(
            schedule=schedule,
            date=date,
            modification_type='cancelled',
            reason=reason,
            created_by=request.user
        )
        
        serializer = ScheduleModificationSerializer(modification)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ScheduleModificationViewSet(viewsets.ModelViewSet):
    """ViewSet pour les modifications de cours"""
    queryset = ScheduleModification.objects.all()
    serializer_class = ScheduleModificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['schedule', 'date', 'modification_type']
    
    def get_queryset(self):
        """Filtrer selon les permissions"""
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.user_type == 'teacher':
            # Un prof voit les modifications de ses cours
            return queryset.filter(
                Q(schedule__teacher=user) |
                Q(substitute_teacher=user)
            ).distinct()
        
        elif user.user_type == 'student':
            # Un élève voit les modifications de sa classe
            return queryset.filter(
                schedule__class_group__students__student=user,
                schedule__class_group__students__is_active=True
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Récupérer les modifications à venir"""
        today = datetime.now().date()
        next_week = today + timedelta(days=7)
        
        modifications = self.get_queryset().filter(
            date__gte=today,
            date__lte=next_week
        ).order_by('date')
        
        serializer = self.get_serializer(modifications, many=True)
        return Response(serializer.data)