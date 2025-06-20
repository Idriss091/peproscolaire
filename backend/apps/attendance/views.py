"""
Vues API pour la gestion de la vie scolaire
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q, Avg, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters import rest_framework as filters
from datetime import date, datetime, timedelta
import calendar

from .models import (
    Attendance, AbsencePeriod, Sanction,
    StudentBehavior, AttendanceAlert, AttendanceStatus
)
from .serializers import (
    AttendanceSerializer, AttendanceBulkSerializer,
    AbsencePeriodSerializer, SanctionSerializer,
    StudentBehaviorSerializer, AttendanceAlertSerializer,
    AttendanceStatsSerializer, DailyAttendanceReportSerializer
)
from .tasks import check_attendance_alerts
from apps.schools.models import Class
from apps.timetable.models import Schedule
from apps.authentication.models import User


class AttendanceFilter(filters.FilterSet):
    """Filtres pour les présences"""
    start_date = filters.DateFilter(field_name='date', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='date', lookup_expr='lte')
    
    class Meta:
        model = Attendance
        fields = ['student', 'schedule', 'status', 'is_justified', 'date']


class AttendanceViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des présences"""
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = AttendanceFilter
    
    def get_queryset(self):
        """Filtrer selon le type d'utilisateur"""
        user = self.request.user
        queryset = Attendance.objects.select_related(
            'student', 'schedule__subject', 'schedule__teacher',
            'recorded_by'
        )
        
        if user.user_type == 'student':
            # Un élève ne voit que ses propres présences
            return queryset.filter(student=user)
        
        elif user.user_type == 'parent':
            # Un parent voit les présences de ses enfants
            # TODO: Implémenter la relation parent-enfant
            return queryset.none()
        
        elif user.user_type == 'teacher':
            # Un prof voit les présences de ses cours
            return queryset.filter(
                Q(schedule__teacher=user) |
                Q(schedule__class_group__main_teacher=user)
            ).distinct()
        
        # Admin voit tout
        return queryset
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Faire l'appel pour toute une classe"""
        serializer = AttendanceBulkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        schedule_id = serializer.validated_data['schedule_id']
        date = serializer.validated_data['date']
        attendances_data = serializer.validated_data['attendances']
        
        # Vérifier que le schedule existe et que l'utilisateur peut faire l'appel
        schedule = get_object_or_404(Schedule, id=schedule_id)
        
        if request.user.user_type == 'teacher' and schedule.teacher != request.user:
            return Response(
                {'error': 'Vous ne pouvez faire l\'appel que pour vos cours'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Créer ou mettre à jour les présences
        created_attendances = []
        for attendance_data in attendances_data:
            student_id = attendance_data['student_id']
            status_value = attendance_data['status']
            arrival_time = attendance_data.get('arrival_time')
            
            attendance, created = Attendance.objects.update_or_create(
                student_id=student_id,
                schedule=schedule,
                date=date,
                defaults={
                    'status': status_value,
                    'arrival_time': arrival_time,
                    'recorded_by': request.user,
                    'modified_by': request.user if not created else None
                }
            )
            created_attendances.append(attendance)
        
        # Vérifier les alertes d'assiduité
        check_attendance_alerts.delay(schedule.class_group.id)
        
        return Response(
            AttendanceSerializer(created_attendances, many=True).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'])
    def daily_report(self, request):
        """Rapport journalier de présence pour une classe"""
        date_str = request.query_params.get('date', str(date.today()))
        class_id = request.query_params.get('class_id')
        
        if not class_id:
            return Response(
                {'error': 'class_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            report_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = DailyAttendanceReportSerializer(
            {'date': report_date, 'class_id': class_id}
        )
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Statistiques de présence"""
        # Paramètres de filtrage
        student_id = request.query_params.get('student_id')
        class_id = request.query_params.get('class_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Construction du queryset
        queryset = self.get_queryset()
        
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        
        if class_id:
            queryset = queryset.filter(schedule__class_group_id=class_id)
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Calcul des statistiques
        serializer = AttendanceStatsSerializer(queryset)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def justify(self, request, pk=None):
        """Justifier une absence"""
        attendance = self.get_object()
        
        # Vérifier les permissions
        if request.user.user_type == 'student' and attendance.student != request.user:
            return Response(
                {'error': 'Vous ne pouvez justifier que vos propres absences'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        attendance.is_justified = True
        attendance.justification_reason = request.data.get('reason', '')
        attendance.modified_by = request.user
        attendance.save()
        
        return Response(AttendanceSerializer(attendance).data)


class AbsencePeriodViewSet(viewsets.ModelViewSet):
    """ViewSet pour les périodes d'absence"""
    serializer_class = AbsencePeriodSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['student', 'is_justified']
    
    def get_queryset(self):
        """Filtrer selon le type d'utilisateur"""
        user = self.request.user
        queryset = AbsencePeriod.objects.select_related(
            'student', 'notified_by'
        )
        
        if user.user_type == 'student':
            return queryset.filter(student=user)
        elif user.user_type == 'parent':
            # TODO: Implémenter la relation parent-enfant
            return queryset.none()
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Périodes d'absence en cours"""
        today = date.today()
        current_periods = self.get_queryset().filter(
            start_date__lte=today,
            end_date__gte=today
        )
        
        serializer = self.get_serializer(current_periods, many=True)
        return Response(serializer.data)


class SanctionViewSet(viewsets.ModelViewSet):
    """ViewSet pour les sanctions"""
    serializer_class = SanctionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['student', 'sanction_type', 'is_completed', 'given_by']
    
    def get_queryset(self):
        """Filtrer selon le type d'utilisateur"""
        user = self.request.user
        queryset = Sanction.objects.select_related('student', 'given_by')
        
        if user.user_type == 'student':
            return queryset.filter(student=user)
        elif user.user_type == 'parent':
            # TODO: Implémenter la relation parent-enfant
            return queryset.none()
        elif user.user_type == 'teacher':
            # Un prof voit les sanctions qu'il a données + celles de ses classes
            return queryset.filter(
                Q(given_by=user) |
                Q(student__enrollments__class_group__main_teacher=user)
            ).distinct()
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Marquer une sanction comme effectuée"""
        sanction = self.get_object()
        
        sanction.is_completed = True
        sanction.completion_notes = request.data.get('notes', '')
        sanction.save()
        
        return Response(SanctionSerializer(sanction).data)
    
    @action(detail=True, methods=['post'])
    def notify_parents(self, request, pk=None):
        """Notifier les parents d'une sanction"""
        sanction = self.get_object()
        
        # TODO: Implémenter l'envoi de notification
        # Pour l'instant, on marque juste comme notifié
        sanction.parents_notified = True
        sanction.notification_date = timezone.now()
        sanction.save()
        
        return Response({
            'message': 'Parents notifiés avec succès',
            'sanction': SanctionSerializer(sanction).data
        })
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Sanctions en attente"""
        pending_sanctions = self.get_queryset().filter(
            is_completed=False
        ).order_by('date')
        
        # Filtrer les retenues à venir
        today = date.today()
        pending_sanctions = pending_sanctions.filter(
            Q(sanction_type='detention', detention_date__gte=today) |
            ~Q(sanction_type='detention')
        )
        
        serializer = self.get_serializer(pending_sanctions, many=True)
        return Response(serializer.data)


class StudentBehaviorViewSet(viewsets.ModelViewSet):
    """ViewSet pour le suivi du comportement"""
    serializer_class = StudentBehaviorSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['student', 'behavior_type', 'category', 'recorded_by']
    
    def get_queryset(self):
        """Filtrer selon le type d'utilisateur"""
        user = self.request.user
        queryset = StudentBehavior.objects.select_related(
            'student', 'recorded_by'
        )
        
        if user.user_type == 'student':
            return queryset.filter(student=user)
        elif user.user_type == 'parent':
            # TODO: Implémenter la relation parent-enfant
            return queryset.none()
        elif user.user_type == 'teacher':
            # Un prof voit les comportements qu'il a enregistrés
            return queryset.filter(
                Q(recorded_by=user) |
                Q(student__enrollments__class_group__main_teacher=user)
            ).distinct()
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Résumé du comportement d'un élève"""
        student_id = request.query_params.get('student_id')
        if not student_id:
            return Response(
                {'error': 'student_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Période par défaut : 30 derniers jours
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        if request.query_params.get('start_date'):
            start_date = datetime.strptime(
                request.query_params.get('start_date'),
                '%Y-%m-%d'
            ).date()
        
        if request.query_params.get('end_date'):
            end_date = datetime.strptime(
                request.query_params.get('end_date'),
                '%Y-%m-%d'
            ).date()
        
        behaviors = self.get_queryset().filter(
            student_id=student_id,
            date__range=[start_date, end_date]
        )
        
        # Calculer le résumé
        summary = behaviors.aggregate(
            total_count=Count('id'),
            positive_count=Count('id', filter=Q(behavior_type='positive')),
            negative_count=Count('id', filter=Q(behavior_type='negative')),
            neutral_count=Count('id', filter=Q(behavior_type='neutral')),
            total_points=Sum('points'),
            avg_points=Avg('points')
        )
        
        # Ajouter les catégories les plus fréquentes
        categories = behaviors.values('category', 'behavior_type').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        summary['top_categories'] = list(categories)
        summary['period'] = {
            'start_date': start_date,
            'end_date': end_date
        }
        
        return Response(summary)


class AttendanceAlertViewSet(viewsets.ModelViewSet):
    """ViewSet pour les alertes d'assiduité"""
    serializer_class = AttendanceAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['student', 'alert_type', 'is_resolved']
    
    def get_queryset(self):
        """Filtrer selon le type d'utilisateur"""
        user = self.request.user
        queryset = AttendanceAlert.objects.select_related(
            'student', 'resolved_by'
        ).prefetch_related('notified_users')
        
        if user.user_type == 'student':
            return queryset.filter(student=user)
        elif user.user_type == 'parent':
            # TODO: Implémenter la relation parent-enfant
            return queryset.none()
        elif user.user_type == 'teacher':
            # Un prof voit les alertes de ses élèves
            return queryset.filter(
                Q(notified_users=user) |
                Q(student__enrollments__class_group__main_teacher=user)
            ).distinct()
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Résoudre une alerte"""
        alert = self.get_object()
        
        alert.is_resolved = True
        alert.resolved_by = request.user
        alert.resolved_at = timezone.now()
        alert.resolution_notes = request.data.get('notes', '')
        alert.save()
        
        return Response(AttendanceAlertSerializer(alert).data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Alertes actives (non résolues)"""
        active_alerts = self.get_queryset().filter(
            is_resolved=False
        ).order_by('-created_at')
        
        serializer = self.get_serializer(active_alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def check_alerts(self, request):
        """Déclencher la vérification des alertes pour une classe"""
        class_id = request.data.get('class_id')
        if not class_id:
            return Response(
                {'error': 'class_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Lancer la tâche asynchrone
        check_attendance_alerts.delay(class_id)
        
        return Response({
            'message': 'Vérification des alertes lancée',
            'class_id': class_id
        })