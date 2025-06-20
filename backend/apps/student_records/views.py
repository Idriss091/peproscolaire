"""
Vues API pour la gestion des dossiers élèves
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters import rest_framework as filters
from django.db.models import Q, Prefetch

from .models import (
    StudentRecord, Guardian, EmergencyContact,
    MedicalRecord, StudentDocument, ScholarshipRecord,
    DisciplinaryRecord, OrientationRecord
)
from .serializers import (
    StudentRecordSerializer, StudentRecordCreateSerializer,
    GuardianSerializer, EmergencyContactSerializer,
    MedicalRecordSerializer, StudentDocumentSerializer,
    ScholarshipRecordSerializer, DisciplinaryRecordSerializer,
    OrientationRecordSerializer, StudentSummarySerializer,
    ParentAccessSerializer
)
from .permissions import (
    IsOwnerOrStaff, CanAccessStudentRecord,
    CanModifyMedicalRecord
)
from apps.authentication.models import User


class StudentRecordFilter(filters.FilterSet):
    """Filtres pour les dossiers élèves"""
    is_active = filters.BooleanFilter()
    has_special_needs = filters.BooleanFilter()
    has_disability = filters.BooleanFilter()
    family_situation = filters.ChoiceFilter(
        choices=StudentRecord._meta.get_field('family_situation').choices
    )
    entry_year = filters.NumberFilter(
        field_name='entry_date',
        lookup_expr='year'
    )
    
    class Meta:
        model = StudentRecord
        fields = [
            'student', 'is_active', 'has_special_needs',
            'has_disability', 'family_situation'
        ]


class StudentRecordViewSet(viewsets.ModelViewSet):
    """ViewSet pour les dossiers élèves"""
    permission_classes = [permissions.IsAuthenticated, CanAccessStudentRecord]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = StudentRecordFilter
    search_fields = [
        'student__first_name', 'student__last_name',
        'student__email', 'national_id'
    ]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return StudentRecordCreateSerializer
        return StudentRecordSerializer
    
    def get_queryset(self):
        """Filtrer selon le type d'utilisateur"""
        user = self.request.user
        queryset = StudentRecord.objects.select_related(
            'student', 'student__profile', 'medical_record'
        ).prefetch_related(
            'guardians', 'emergency_contacts', 'documents'
        )
        
        if user.user_type == 'student':
            # Un élève ne voit que son propre dossier
            return queryset.filter(student=user)
        
        elif user.user_type == 'parent':
            # Un parent voit les dossiers de ses enfants
            return queryset.filter(
                guardians__user=user,
                guardians__has_custody=True
            ).distinct()
        
        elif user.user_type == 'teacher':
            # Un prof voit les dossiers de ses élèves
            return queryset.filter(
                Q(student__enrollments__class_group__main_teacher=user) |
                Q(student__enrollments__class_group__schedules__teacher=user)
            ).distinct()
        
        # Admin voit tout
        return queryset
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Résumé complet du dossier élève"""
        student_record = self.get_object()
        serializer = StudentSummarySerializer(student_record)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def academic_history(self, request, pk=None):
        """Historique académique complet"""
        student_record = self.get_object()
        student = student_record.student
        
        # Récupérer toutes les moyennes générales
        from apps.grades.models import GeneralAverage
        
        averages = GeneralAverage.objects.filter(
            student=student
        ).select_related(
            'grading_period__academic_year'
        ).order_by('-grading_period__academic_year__start_date')
        
        history = []
        for avg in averages:
            history.append({
                'academic_year': avg.grading_period.academic_year.name,
                'period': avg.grading_period.name,
                'general_average': float(avg.average) if avg.average else None,
                'rank': avg.rank,
                'class_size': avg.class_size,
                'honor_roll': avg.honor_roll,
                'council_decision': avg.council_decision
            })
        
        return Response({
            'student': student.get_full_name(),
            'history': history
        })
    
    @action(detail=True, methods=['get'])
    def attendance_history(self, request, pk=None):
        """Historique de présence"""
        student_record = self.get_object()
        student = student_record.student
        
        # Paramètres de période
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        from apps.attendance.models import Attendance
        
        attendances = Attendance.objects.filter(student=student)
        
        if start_date:
            attendances = attendances.filter(date__gte=start_date)
        if end_date:
            attendances = attendances.filter(date__lte=end_date)
        
        # Grouper par mois
        from django.db.models import Count
        from django.db.models.functions import TruncMonth
        
        monthly_stats = attendances.values(
            month=TruncMonth('date')
        ).annotate(
            total=Count('id'),
            present=Count('id', filter=Q(status='present')),
            absent=Count('id', filter=Q(status='absent')),
            late=Count('id', filter=Q(status='late')),
            excused=Count('id', filter=Q(status='excused'))
        ).order_by('month')
        
        return Response({
            'student': student.get_full_name(),
            'monthly_statistics': list(monthly_stats)
        })
    
    @action(detail=True, methods=['post'])
    def add_guardian(self, request, pk=None):
        """Ajouter un responsable légal"""
        student_record = self.get_object()
        
        serializer = GuardianSerializer(
            data=request.data,
            context={'student_record': student_record}
        )
        serializer.is_valid(raise_exception=True)
        
        guardian = serializer.save(student_record=student_record)
        
        return Response(
            GuardianSerializer(guardian).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def add_document(self, request, pk=None):
        """Ajouter un document"""
        student_record = self.get_object()
        
        serializer = StudentDocumentSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        document = serializer.save(student_record=student_record)
        
        return Response(
            StudentDocumentSerializer(document).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['get'])
    def export_pdf(self, request, pk=None):
        """Exporter le dossier complet en PDF"""
        student_record = self.get_object()
        
        # TODO: Implémenter la génération PDF avec ReportLab
        # Pour l'instant, retourner les données
        
        return Response({
            'message': 'Export PDF en cours de développement',
            'student': student_record.student.get_full_name()
        })


class GuardianViewSet(viewsets.ModelViewSet):
    """ViewSet pour les responsables légaux"""
    serializer_class = GuardianSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrer les responsables accessibles"""
        user = self.request.user
        
        if user.user_type == 'student':
            # Un élève voit ses responsables
            return Guardian.objects.filter(
                student_record__student=user
            )
        
        elif user.user_type == 'parent':
            # Un parent se voit lui-même et les autres responsables de ses enfants
            return Guardian.objects.filter(
                Q(user=user) |
                Q(student_record__guardians__user=user)
            ).distinct()
        
        elif user.user_type in ['teacher', 'admin', 'superadmin']:
            return Guardian.objects.all()
        
        return Guardian.objects.none()
    
    @action(detail=True, methods=['post'])
    def link_user_account(self, request, pk=None):
        """Lier un compte utilisateur à un responsable"""
        guardian = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id, user_type='parent')
            guardian.user = user
            guardian.save()
            
            return Response({
                'message': 'Compte lié avec succès',
                'guardian': GuardianSerializer(guardian).data
            })
        
        except User.DoesNotExist:
            return Response(
                {'error': 'Utilisateur parent non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )


class MedicalRecordViewSet(viewsets.ModelViewSet):
    """ViewSet pour les dossiers médicaux"""
    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated, CanModifyMedicalRecord]
    
    def get_queryset(self):
        """Filtrer selon les permissions"""
        user = self.request.user
        queryset = MedicalRecord.objects.select_related('student_record__student')
        
        if user.user_type == 'student':
            return queryset.filter(student_record__student=user)
        
        elif user.user_type == 'parent':
            return queryset.filter(
                student_record__guardians__user=user,
                student_record__guardians__has_custody=True
            ).distinct()
        
        elif user.user_type in ['teacher', 'admin', 'superadmin']:
            return queryset
        
        return queryset.none()
    
    @action(detail=True, methods=['post'])
    def update_emergency_protocol(self, request, pk=None):
        """Mettre à jour le protocole d'urgence"""
        medical_record = self.get_object()
        
        protocol = request.data.get('emergency_protocol')
        if protocol:
            medical_record.emergency_protocol = protocol
            medical_record.save()
            
            return Response({
                'message': 'Protocole mis à jour',
                'medical_record': MedicalRecordSerializer(medical_record).data
            })
        
        return Response(
            {'error': 'emergency_protocol is required'},
            status=status.HTTP_400_BAD_REQUEST
        )


class StudentDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet pour les documents élèves"""
    serializer_class = StudentDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['student_record', 'document_type', 'is_verified']
    
    def get_queryset(self):
        """Filtrer selon les permissions"""
        user = self.request.user
        queryset = StudentDocument.objects.select_related(
            'student_record__student',
            'uploaded_by',
            'verified_by'
        )
        
        if user.user_type == 'student':
            return queryset.filter(
                student_record__student=user
            )
        
        elif user.user_type == 'parent':
            return queryset.filter(
                student_record__guardians__user=user,
                is_confidential=False
            ).distinct()
        
        elif user.user_type == 'teacher':
            return queryset.filter(
                is_confidential=False
            )
        
        # Admin voit tout
        return queryset
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Vérifier un document"""
        document = self.get_object()
        
        # Seuls les admins peuvent vérifier
        if request.user.user_type not in ['admin', 'superadmin']:
            return Response(
                {'error': 'Seuls les administrateurs peuvent vérifier les documents'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        document.is_verified = True
        document.verified_by = request.user
        document.verified_at = timezone.now()
        document.save()
        
        return Response({
            'message': 'Document vérifié',
            'document': StudentDocumentSerializer(document).data
        })
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Documents expirant bientôt"""
        days_ahead = int(request.query_params.get('days', 30))
        
        expiry_date = timezone.now().date() + timezone.timedelta(days=days_ahead)
        
        documents = self.get_queryset().filter(
            expiry_date__lte=expiry_date,
            expiry_date__gte=timezone.now().date()
        ).order_by('expiry_date')
        
        serializer = self.get_serializer(documents, many=True)
        
        return Response({
            'count': documents.count(),
            'documents': serializer.data
        })


class DisciplinaryRecordViewSet(viewsets.ModelViewSet):
    """ViewSet pour les dossiers disciplinaires"""
    serializer_class = DisciplinaryRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrer selon les permissions"""
        user = self.request.user
        queryset = DisciplinaryRecord.objects.select_related(
            'student_record__student',
            'academic_year',
            'tutor_assigned'
        )
        
        if user.user_type == 'student':
            return queryset.filter(student_record__student=user)
        
        elif user.user_type == 'parent':
            return queryset.filter(
                student_record__guardians__user=user
            ).distinct()
        
        elif user.user_type in ['teacher', 'admin', 'superadmin']:
            return queryset
        
        return queryset.none()
    
    @action(detail=True, methods=['post'])
    def update_counts(self, request, pk=None):
        """Mettre à jour les compteurs depuis le module sanctions"""
        record = self.get_object()
        record.update_counts()
        
        return Response({
            'message': 'Compteurs mis à jour',
            'record': DisciplinaryRecordSerializer(record).data
        })


class OrientationRecordViewSet(viewsets.ModelViewSet):
    """ViewSet pour les dossiers d'orientation"""
    serializer_class = OrientationRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrer selon les permissions"""
        user = self.request.user
        queryset = OrientationRecord.objects.select_related(
            'student_record__student',
            'academic_year'
        )
        
        if user.user_type == 'student':
            return queryset.filter(student_record__student=user)
        
        elif user.user_type == 'parent':
            return queryset.filter(
                student_record__guardians__user=user
            ).distinct()
        
        elif user.user_type in ['teacher', 'admin', 'superadmin']:
            return queryset
        
        return queryset.none()
    
    @action(detail=True, methods=['post'])
    def submit_wishes(self, request, pk=None):
        """Soumettre les vœux d'orientation"""
        record = self.get_object()
        wishes = request.data.get('wishes', [])
        
        if not wishes:
            return Response(
                {'error': 'wishes is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        record.student_wishes = wishes
        record.save()
        
        return Response({
            'message': 'Vœux enregistrés',
            'record': OrientationRecordSerializer(record).data
        })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def parent_dashboard(request):
    """Tableau de bord parent avec accès aux dossiers des enfants"""
    if request.user.user_type != 'parent':
        return Response(
            {'error': 'Réservé aux parents'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = ParentAccessSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_students(request):
    """Recherche globale d'élèves"""
    query = request.query_params.get('q', '')
    
    if len(query) < 3:
        return Response({
            'error': 'La recherche doit contenir au moins 3 caractères'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Rechercher dans les dossiers
    records = StudentRecord.objects.filter(
        Q(student__first_name__icontains=query) |
        Q(student__last_name__icontains=query) |
        Q(student__email__icontains=query) |
        Q(national_id__icontains=query)
    ).select_related('student')[:20]
    
    # Vérifier les permissions
    user = request.user
    if user.user_type == 'teacher':
        # Filtrer par élèves du prof
        records = records.filter(
            Q(student__enrollments__class_group__main_teacher=user) |
            Q(student__enrollments__class_group__schedules__teacher=user)
        ).distinct()
    
    results = []
    for record in records:
        # Classe actuelle
        current_class = None
        enrollment = record.student.enrollments.filter(is_active=True).first()
        if enrollment:
            current_class = str(enrollment.class_group)
        
        results.append({
            'id': str(record.id),
            'student_id': str(record.student.id),
            'name': record.student.get_full_name(),
            'email': record.student.email,
            'national_id': record.national_id,
            'current_class': current_class
        })
    
    return Response({
        'count': len(results),
        'results': results
    })