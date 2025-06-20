"""
Vues pour la gestion des établissements scolaires
"""
from django.db.models import Count, Q
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import School, AcademicYear, Level, Class, StudentClassEnrollment
from .serializers import (
    SchoolSerializer, AcademicYearSerializer, LevelSerializer,
    ClassSerializer, StudentClassEnrollmentSerializer
)


class SchoolViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des établissements
    """
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['school_type', 'is_active']
    search_fields = ['name', 'city', 'subdomain']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        """
        Filtre les établissements selon les permissions utilisateur
        """
        user = self.request.user
        queryset = School.objects.all()
        
        # Si l'utilisateur n'est pas superadmin, il ne voit que son établissement
        if user.user_type != 'superadmin':
            if hasattr(user, 'profile') and user.profile.school:
                queryset = queryset.filter(id=user.profile.school.id)
            else:
                queryset = queryset.none()
        
        return queryset

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """
        Statistiques d'un établissement
        """
        school = self.get_object()
        current_year = school.academic_years.filter(is_current=True).first()
        
        if not current_year:
            return Response({
                'error': 'Aucune année scolaire active trouvée'
            }, status=status.HTTP_404_NOT_FOUND)
        
        stats = {
            'total_classes': school.classes.filter(academic_year=current_year).count(),
            'total_students': StudentClassEnrollment.objects.filter(
                class_group__school=school,
                class_group__academic_year=current_year,
                is_active=True
            ).count(),
            'total_teachers': school.classes.filter(
                academic_year=current_year,
                main_teacher__isnull=False
            ).values('main_teacher').distinct().count(),
            'classes_by_level': list(
                school.classes.filter(academic_year=current_year)
                .values('level__name')
                .annotate(count=Count('id'))
                .order_by('level__order')
            )
        }
        
        return Response(stats)


class AcademicYearViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des années scolaires
    """
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['school', 'is_current']
    search_fields = ['name']
    ordering_fields = ['start_date', 'name']
    ordering = ['-start_date']

    def get_queryset(self):
        """
        Filtre selon l'établissement de l'utilisateur
        """
        user = self.request.user
        queryset = AcademicYear.objects.all()
        
        if user.user_type != 'superadmin':
            if hasattr(user, 'profile') and user.profile.school:
                queryset = queryset.filter(school=user.profile.school)
            else:
                queryset = queryset.none()
        
        return queryset

    def perform_create(self, serializer):
        """
        Assigne automatiquement l'établissement de l'utilisateur
        """
        user = self.request.user
        
        if user.user_type == 'superadmin':
            # Le superadmin peut créer pour n'importe quel établissement
            serializer.save()
        else:
            # Les autres utilisateurs créent pour leur établissement
            if hasattr(user, 'profile') and user.profile.school:
                serializer.save(school=user.profile.school)
            else:
                raise permissions.PermissionDenied(
                    "Vous devez être associé à un établissement"
                )

    @action(detail=False, methods=['get'])
    def current(self, request):
        """
        Retourne l'année scolaire en cours
        """
        user = request.user
        
        if user.user_type == 'superadmin':
            # Le superadmin doit spécifier l'établissement
            school_id = request.query_params.get('school_id')
            if not school_id:
                return Response({
                    'error': 'Paramètre school_id requis pour le superadmin'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                current_year = AcademicYear.objects.get(
                    school_id=school_id,
                    is_current=True
                )
            except AcademicYear.DoesNotExist:
                return Response({
                    'error': 'Aucune année scolaire active trouvée'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            # Pour les autres utilisateurs, utilise leur établissement
            if not (hasattr(user, 'profile') and user.profile.school):
                return Response({
                    'error': 'Utilisateur non associé à un établissement'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                current_year = AcademicYear.objects.get(
                    school=user.profile.school,
                    is_current=True
                )
            except AcademicYear.DoesNotExist:
                return Response({
                    'error': 'Aucune année scolaire active trouvée'
                }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(current_year)
        return Response(serializer.data)


class LevelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour la consultation des niveaux (lecture seule)
    """
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['school_type']
    ordering_fields = ['order', 'name']
    ordering = ['order']


class ClassViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des classes
    """
    queryset = Class.objects.select_related(
        'school', 'academic_year', 'level', 'main_teacher'
    ).prefetch_related('students')
    serializer_class = ClassSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['school', 'academic_year', 'level', 'main_teacher']
    search_fields = ['name', 'level__name']
    ordering_fields = ['name', 'level__order', 'created_at']
    ordering = ['level__order', 'name']

    def get_queryset(self):
        """
        Filtre selon l'établissement et les permissions
        """
        user = self.request.user
        queryset = Class.objects.select_related(
            'school', 'academic_year', 'level', 'main_teacher'
        ).prefetch_related('students')
        
        if user.user_type == 'superadmin':
            # Le superadmin voit toutes les classes
            pass
        elif user.user_type in ['admin', 'teacher']:
            # Admin et enseignants voient les classes de leur établissement
            if hasattr(user, 'profile') and user.profile.school:
                queryset = queryset.filter(school=user.profile.school)
            else:
                queryset = queryset.none()
        elif user.user_type == 'student':
            # Les élèves ne voient que leurs classes
            queryset = queryset.filter(
                students__student=user,
                students__is_active=True
            )
        elif user.user_type == 'parent':
            # Les parents voient les classes de leurs enfants
            # Récupérer les enfants du parent via les relations
            children = user.children.all()
            queryset = queryset.filter(
                students__student__in=children,
                students__is_active=True
            )
        else:
            queryset = queryset.none()
        
        return queryset

    def perform_create(self, serializer):
        """
        Assigne automatiquement l'établissement de l'utilisateur
        """
        user = self.request.user
        
        if user.user_type == 'superadmin':
            serializer.save()
        else:
            if hasattr(user, 'profile') and user.profile.school:
                # Récupère l'année scolaire en cours
                current_year = AcademicYear.objects.filter(
                    school=user.profile.school,
                    is_current=True
                ).first()
                
                if not current_year:
                    raise ValidationError(
                        "Aucune année scolaire active trouvée pour cet établissement"
                    )
                
                serializer.save(
                    school=user.profile.school,
                    academic_year=current_year
                )
            else:
                raise permissions.PermissionDenied(
                    "Vous devez être associé à un établissement"
                )

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """
        Liste des élèves d'une classe
        """
        class_obj = self.get_object()
        enrollments = StudentClassEnrollment.objects.filter(
            class_group=class_obj,
            is_active=True
        ).select_related('student').order_by('student__last_name', 'student__first_name')
        
        serializer = StudentClassEnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_student(self, request, pk=None):
        """
        Ajouter un élève à une classe
        """
        class_obj = self.get_object()
        student_id = request.data.get('student_id')
        
        if not student_id:
            return Response({
                'error': 'student_id requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier que l'élève existe et est bien un élève
        try:
            from apps.authentication.models import User
            student = User.objects.get(id=student_id, user_type='student')
        except User.DoesNotExist:
            return Response({
                'error': 'Élève introuvable'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Vérifier que l'élève n'est pas déjà dans une classe active
        existing_enrollment = StudentClassEnrollment.objects.filter(
            student=student,
            class_group__academic_year=class_obj.academic_year,
            is_active=True
        ).first()
        
        if existing_enrollment:
            return Response({
                'error': f'L\'élève est déjà inscrit dans la classe {existing_enrollment.class_group}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier la capacité de la classe
        if class_obj.student_count >= class_obj.max_students:
            return Response({
                'error': 'La classe a atteint sa capacité maximale'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Créer l'inscription
        enrollment = StudentClassEnrollment.objects.create(
            student=student,
            class_group=class_obj
        )
        
        serializer = StudentClassEnrollmentSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'])
    def remove_student(self, request, pk=None):
        """
        Retirer un élève d'une classe
        """
        class_obj = self.get_object()
        student_id = request.data.get('student_id')
        
        if not student_id:
            return Response({
                'error': 'student_id requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            enrollment = StudentClassEnrollment.objects.get(
                class_group=class_obj,
                student_id=student_id,
                is_active=True
            )
            enrollment.is_active = False
            enrollment.save()
            
            return Response({
                'message': 'Élève retiré de la classe'
            }, status=status.HTTP_200_OK)
            
        except StudentClassEnrollment.DoesNotExist:
            return Response({
                'error': 'Inscription introuvable'
            }, status=status.HTTP_404_NOT_FOUND)


class StudentClassEnrollmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des inscriptions élèves
    """
    queryset = StudentClassEnrollment.objects.select_related(
        'student', 'class_group'
    )
    serializer_class = StudentClassEnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['class_group', 'is_active']
    search_fields = ['student__first_name', 'student__last_name']
    ordering_fields = ['enrollment_date']
    ordering = ['-enrollment_date']

    def get_queryset(self):
        """
        Filtre selon les permissions utilisateur
        """
        user = self.request.user
        queryset = StudentClassEnrollment.objects.select_related(
            'student', 'class_group'
        )
        
        if user.user_type == 'superadmin':
            pass
        elif user.user_type in ['admin', 'teacher']:
            if hasattr(user, 'profile') and user.profile.school:
                queryset = queryset.filter(class_group__school=user.profile.school)
            else:
                queryset = queryset.none()
        elif user.user_type == 'student':
            queryset = queryset.filter(student=user)
        elif user.user_type == 'parent':
            children = user.children.all()
            queryset = queryset.filter(student__in=children)
        else:
            queryset = queryset.none()
        
        return queryset