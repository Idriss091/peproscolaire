"""
Vues API pour la gestion du cahier de textes et des devoirs
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Q, Avg, Prefetch
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters import rest_framework as filters
from datetime import date, datetime, timedelta
import mimetypes

from .models import (
    LessonContent, HomeworkType, Homework, HomeworkResource,
    StudentWork, HomeworkTemplate, WorkloadAnalysis
)
from .serializers import (
    LessonContentSerializer, HomeworkTypeSerializer,
    HomeworkListSerializer, HomeworkDetailSerializer,
    HomeworkCreateSerializer, HomeworkResourceSerializer,
    StudentWorkSerializer, HomeworkTemplateSerializer,
    WorkloadAnalysisSerializer, HomeworkSuggestionSerializer,
    StudentHomeworkViewSerializer, TeacherDashboardSerializer
)
from .tasks import (
    generate_homework_suggestions, analyze_workload,
    send_homework_reminders, auto_create_student_works
)
from apps.schools.models import Class
from apps.timetable.models import Schedule, Subject


class LessonContentFilter(filters.FilterSet):
    """Filtres pour le contenu des cours"""
    start_date = filters.DateFilter(field_name='date', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='date', lookup_expr='lte')
    
    class Meta:
        model = LessonContent
        fields = ['schedule', 'date', 'chapter', 'validated']


class LessonContentViewSet(viewsets.ModelViewSet):
    """ViewSet pour le contenu des cours"""
    serializer_class = LessonContentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = LessonContentFilter
    
    def get_queryset(self):
        """Filtrer selon le type d'utilisateur"""
        user = self.request.user
        queryset = LessonContent.objects.select_related(
            'schedule__subject', 'schedule__class_group',
            'schedule__teacher', 'created_by'
        ).prefetch_related('homework_assignments')
        
        if user.user_type == 'teacher':
            # Un prof voit ses propres cours
            return queryset.filter(
                Q(created_by=user) |
                Q(schedule__teacher=user)
            ).distinct()
        
        elif user.user_type == 'student':
            # Un élève voit les cours de sa classe
            enrollments = user.enrollments.filter(is_active=True)
            class_ids = enrollments.values_list('class_group_id', flat=True)
            return queryset.filter(
                schedule__class_group_id__in=class_ids,
                validated=True  # Seulement les cours validés pour les élèves
            )
        
        # Admin voit tout
        return queryset
    
    @action(detail=False, methods=['get'])
    def by_schedule(self, request):
        """Récupérer le contenu d'un schedule spécifique"""
        schedule_id = request.query_params.get('schedule_id')
        if not schedule_id:
            return Response(
                {'error': 'schedule_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        contents = self.get_queryset().filter(
            schedule_id=schedule_id
        ).order_by('-date')
        
        page = self.paginate_queryset(contents)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(contents, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """Valider un contenu de cours (admin)"""
        lesson = self.get_object()
        
        # Vérifier les permissions
        if request.user.user_type not in ['admin', 'superadmin']:
            return Response(
                {'error': 'Seuls les administrateurs peuvent valider'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        lesson.validated = True
        lesson.validated_by = request.user
        lesson.validated_at = timezone.now()
        lesson.save()
        
        return Response(LessonContentSerializer(lesson).data)
    
    @action(detail=False, methods=['get'])
    def progression(self, request):
        """Vue de la progression pédagogique"""
        subject_id = request.query_params.get('subject_id')
        class_id = request.query_params.get('class_id')
        
        if not all([subject_id, class_id]):
            return Response(
                {'error': 'subject_id and class_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Récupérer tous les contenus pour cette matière/classe
        contents = self.get_queryset().filter(
            schedule__subject_id=subject_id,
            schedule__class_group_id=class_id
        ).order_by('date')
        
        # Grouper par chapitre
        chapters = {}
        for content in contents:
            chapter = content.chapter or 'Sans chapitre'
            if chapter not in chapters:
                chapters[chapter] = {
                    'name': chapter,
                    'lessons': [],
                    'total_duration': 0,
                    'homework_count': 0
                }
            
            chapters[chapter]['lessons'].append({
                'id': str(content.id),
                'date': content.date,
                'title': content.title,
                'duration': content.duration_minutes,
                'has_homework': content.has_homework
            })
            chapters[chapter]['total_duration'] += content.duration_minutes
            if content.has_homework:
                chapters[chapter]['homework_count'] += 1
        
        return Response({
            'subject_id': subject_id,
            'class_id': class_id,
            'chapters': list(chapters.values()),
            'total_lessons': contents.count(),
            'total_duration_hours': sum(c.duration_minutes for c in contents) / 60
        })


class HomeworkTypeViewSet(viewsets.ModelViewSet):
    """ViewSet pour les types de devoirs"""
    queryset = HomeworkType.objects.all()
    serializer_class = HomeworkTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


class HomeworkFilter(filters.FilterSet):
    """Filtres pour les devoirs"""
    start_date = filters.DateFilter(field_name='due_date', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='due_date', lookup_expr='lte')
    overdue = filters.BooleanFilter(method='filter_overdue')
    
    class Meta:
        model = Homework
        fields = [
            'subject', 'class_group', 'teacher', 'homework_type',
            'difficulty', 'is_graded', 'submission_type'
        ]
    
    def filter_overdue(self, queryset, name, value):
        if value:
            return queryset.filter(due_date__lt=timezone.now().date())
        return queryset.filter(due_date__gte=timezone.now().date())


class HomeworkViewSet(viewsets.ModelViewSet):
    """ViewSet pour les devoirs"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = HomeworkFilter
    
    def get_serializer_class(self):
        if self.action == 'create':
            return HomeworkCreateSerializer
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return HomeworkDetailSerializer
        return HomeworkListSerializer
    
    def get_queryset(self):
        """Filtrer selon le type d'utilisateur"""
        user = self.request.user
        queryset = Homework.objects.select_related(
            'subject', 'class_group', 'teacher', 'homework_type'
        ).annotate(
            submission_count=Count('submissions'),
            submitted_count=Count('submissions', filter=Q(submissions__status='submitted'))
        )
        
        if user.user_type == 'teacher':
            # Un prof voit ses devoirs
            return queryset.filter(teacher=user)
        
        elif user.user_type == 'student':
            # Un élève voit les devoirs de sa classe
            enrollments = user.enrollments.filter(is_active=True)
            class_ids = enrollments.values_list('class_group_id', flat=True)
            return queryset.filter(class_group_id__in=class_ids)
        
        elif user.user_type == 'parent':
            # Un parent voit les devoirs de ses enfants
            # TODO: Implémenter la relation parent-enfant
            return queryset.none()
        
        # Admin voit tout
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        """Incrémenter le compteur de vues"""
        instance = self.get_object()
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def calendar(self, request):
        """Vue calendrier des devoirs"""
        start_date = request.query_params.get('start_date', str(date.today()))
        end_date = request.query_params.get('end_date')
        
        if not end_date:
            # Par défaut, 30 jours
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = start + timedelta(days=30)
            end_date = str(end)
        
        homework_list = self.get_queryset().filter(
            due_date__range=[start_date, end_date]
        ).order_by('due_date')
        
        # Organiser par date
        calendar_data = {}
        for hw in homework_list:
            date_str = str(hw.due_date)
            if date_str not in calendar_data:
                calendar_data[date_str] = []
            
            calendar_data[date_str].append({
                'id': str(hw.id),
                'title': hw.title,
                'subject': hw.subject.name,
                'class': str(hw.class_group),
                'difficulty': hw.difficulty,
                'is_graded': hw.is_graded,
                'estimated_duration': hw.estimated_duration_minutes
            })
        
        return Response({
            'start_date': start_date,
            'end_date': end_date,
            'calendar': calendar_data
        })
    
    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None):
        """Récupérer toutes les soumissions d'un devoir"""
        homework = self.get_object()
        
        # Vérifier les permissions
        if request.user != homework.teacher and request.user.user_type != 'admin':
            return Response(
                {'error': 'Vous ne pouvez voir que les soumissions de vos devoirs'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        submissions = homework.submissions.select_related('student').order_by(
            'student__last_name', 'student__first_name'
        )
        
        serializer = StudentWorkSerializer(submissions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def generate_ai_suggestions(self, request, pk=None):
        """Générer des suggestions de devoirs avec l'IA"""
        homework = self.get_object()
        
        # Lancer la génération asynchrone
        generate_homework_suggestions.delay(
            subject_id=str(homework.subject.id),
            class_level=str(homework.class_group.level),
            chapter=homework.lesson_content.chapter if homework.lesson_content else '',
            teacher_id=str(request.user.id)
        )
        
        return Response({
            'message': 'Génération de suggestions lancée',
            'homework_id': str(homework.id)
        })
    
    @action(detail=False, methods=['post'])
    def create_from_template(self, request):
        """Créer un devoir depuis un modèle"""
        template_id = request.data.get('template_id')
        class_id = request.data.get('class_id')
        due_date = request.data.get('due_date')
        
        if not all([template_id, class_id, due_date]):
            return Response(
                {'error': 'template_id, class_id et due_date sont requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        template = get_object_or_404(HomeworkTemplate, id=template_id)
        class_group = get_object_or_404(Class, id=class_id)
        
        # Vérifier que le prof peut utiliser ce modèle
        if template.teacher != request.user and not template.is_shared:
            return Response(
                {'error': 'Vous ne pouvez pas utiliser ce modèle'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Créer le devoir
        homework = template.create_homework(
            class_group=class_group,
            due_date=due_date,
            teacher=request.user
        )
        
        # Créer automatiquement les StudentWork
        auto_create_student_works.delay(homework.id)
        
        return Response(
            HomeworkDetailSerializer(homework).data,
            status=status.HTTP_201_CREATED
        )


class HomeworkResourceViewSet(viewsets.ModelViewSet):
    """ViewSet pour les ressources"""
    serializer_class = HomeworkResourceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrer selon le contexte"""
        queryset = HomeworkResource.objects.select_related(
            'homework', 'lesson_content', 'uploaded_by'
        )
        
        homework_id = self.request.query_params.get('homework_id')
        lesson_id = self.request.query_params.get('lesson_id')
        
        if homework_id:
            queryset = queryset.filter(homework_id=homework_id)
        if lesson_id:
            queryset = queryset.filter(lesson_content_id=lesson_id)
        
        return queryset.order_by('order', 'title')
    
    @action(detail=True, methods=['post'])
    def download(self, request, pk=None):
        """Enregistrer un téléchargement"""
        resource = self.get_object()
        resource.download_count += 1
        resource.save(update_fields=['download_count'])
        
        # Retourner l'URL de téléchargement
        if resource.file:
            return Response({
                'url': request.build_absolute_uri(resource.file.url),
                'filename': resource.file.name,
                'size_mb': resource.size_mb
            })
        elif resource.url:
            return Response({
                'url': resource.url,
                'type': 'external'
            })
        
        return Response(
            {'error': 'Aucun fichier ou URL disponible'},
            status=status.HTTP_404_NOT_FOUND
        )


class StudentWorkViewSet(viewsets.ModelViewSet):
    """ViewSet pour les travaux d'élèves"""
    serializer_class = StudentWorkSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['homework', 'student', 'status']
    
    def get_queryset(self):
        """Filtrer selon le type d'utilisateur"""
        user = self.request.user
        queryset = StudentWork.objects.select_related(
            'homework__subject', 'student', 'corrected_by'
        )
        
        if user.user_type == 'student':
            # Un élève ne voit que ses propres travaux
            return queryset.filter(student=user)
        
        elif user.user_type == 'teacher':
            # Un prof voit les travaux de ses devoirs
            return queryset.filter(homework__teacher=user)
        
        elif user.user_type == 'parent':
            # TODO: Implémenter la relation parent-enfant
            return queryset.none()
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Soumettre un travail"""
        work = self.get_object()
        
        # Vérifier que c'est bien l'élève
        if work.student != request.user:
            return Response(
                {'error': 'Vous ne pouvez soumettre que vos propres travaux'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Vérifier que le devoir n'est pas déjà soumis
        if work.status in ['submitted', 'late', 'returned']:
            return Response(
                {'error': 'Ce travail a déjà été soumis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        work.submit()
        
        return Response(StudentWorkSerializer(work).data)
    
    @action(detail=True, methods=['post'])
    def grade(self, request, pk=None):
        """Noter un travail"""
        work = self.get_object()
        
        # Vérifier que c'est le prof du devoir
        if work.homework.teacher != request.user and request.user.user_type != 'admin':
            return Response(
                {'error': 'Vous ne pouvez noter que vos propres devoirs'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Mettre à jour la note et le commentaire
        serializer = self.get_serializer(work, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_homework(self, request):
        """Vue des devoirs pour un élève"""
        if request.user.user_type != 'student':
            return Response(
                {'error': 'Réservé aux élèves'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Récupérer tous les devoirs de l'élève
        enrollments = request.user.enrollments.filter(is_active=True)
        class_ids = enrollments.values_list('class_group_id', flat=True)
        
        homework_qs = Homework.objects.filter(
            class_group_id__in=class_ids
        ).prefetch_related(
            Prefetch(
                'submissions',
                queryset=StudentWork.objects.filter(student=request.user),
                to_attr='my_submissions'
            )
        )
        
        # Filtrer par statut si demandé
        status_filter = request.query_params.get('status', 'all')
        if status_filter == 'pending':
            homework_qs = homework_qs.filter(due_date__gte=timezone.now().date())
        elif status_filter == 'overdue':
            homework_qs = homework_qs.filter(due_date__lt=timezone.now().date())
        
        serializer = StudentHomeworkViewSerializer(
            homework_qs,
            context={'request': request}
        )
        
        return Response(serializer.data)


class HomeworkTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet pour les modèles de devoirs"""
    serializer_class = HomeworkTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['subject', 'teacher', 'chapter', 'level', 'is_shared']
    search_fields = ['name', 'title', 'description', 'tags']
    
    def get_queryset(self):
        """Filtrer les modèles accessibles"""
        user = self.request.user
        
        if user.user_type in ['student', 'parent']:
            return HomeworkTemplate.objects.none()
        
        # Un prof voit ses modèles + ceux partagés
        return HomeworkTemplate.objects.filter(
            Q(teacher=user) | Q(is_shared=True)
        ).select_related('subject', 'teacher', 'homework_type')
    
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Partager un modèle"""
        template = self.get_object()
        
        # Vérifier que c'est le propriétaire
        if template.teacher != request.user:
            return Response(
                {'error': 'Vous ne pouvez partager que vos propres modèles'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        template.is_shared = True
        template.save()
        
        return Response({
            'message': 'Modèle partagé avec succès',
            'template': HomeworkTemplateSerializer(template).data
        })
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Modèles les plus utilisés"""
        popular_templates = self.get_queryset().filter(
            is_shared=True,
            use_count__gt=0
        ).order_by('-use_count')[:10]
        
        serializer = self.get_serializer(popular_templates, many=True)
        return Response(serializer.data)


class WorkloadAnalysisViewSet(viewsets.ModelViewSet):
    """ViewSet pour l'analyse de charge de travail"""
    serializer_class = WorkloadAnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['class_group', 'date', 'is_overloaded']
    
    def get_queryset(self):
        """Filtrer selon les permissions"""
        queryset = WorkloadAnalysis.objects.select_related('class_group')
        
        user = self.request.user
        if user.user_type == 'teacher':
            # Prof principal voit sa classe
            return queryset.filter(class_group__main_teacher=user)
        elif user.user_type in ['student', 'parent']:
            return queryset.none()
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def analyze(self, request):
        """Lancer une analyse de charge de travail"""
        class_id = request.data.get('class_id')
        analysis_date = request.data.get('date', str(date.today()))
        
        if not class_id:
            return Response(
                {'error': 'class_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Lancer l'analyse asynchrone
        analyze_workload.delay(class_id, analysis_date)
        
        return Response({
            'message': 'Analyse lancée',
            'class_id': class_id,
            'date': analysis_date
        })
    
    @action(detail=False, methods=['get'])
    def current_alerts(self, request):
        """Alertes de surcharge en cours"""
        alerts = self.get_queryset().filter(
            is_overloaded=True,
            date__gte=date.today() - timedelta(days=7)
        ).order_by('-overload_level', '-date')
        
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def teacher_dashboard(request):
    """Tableau de bord pour les professeurs"""
    if request.user.user_type != 'teacher':
        return Response(
            {'error': 'Réservé aux professeurs'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = TeacherDashboardSerializer(
        data={},
        context={'request': request}
    )
    
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def suggest_homework(request):
    """Suggérer des devoirs avec l'IA"""
    if request.user.user_type != 'teacher':
        return Response(
            {'error': 'Réservé aux professeurs'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = HomeworkSuggestionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    # Générer les suggestions
    from apps.ai_modules.homework_suggester import HomeworkSuggester
    suggester = HomeworkSuggester()
    
    suggestions = suggester.generate_suggestions(
        chapter=serializer.validated_data['chapter'],
        subject_id=serializer.validated_data['subject_id'],
        class_level=serializer.validated_data['class_level'],
        lesson_objectives=serializer.validated_data.get('lesson_objectives'),
        key_concepts=serializer.validated_data.get('key_concepts'),
        difficulty=serializer.validated_data['difficulty']
    )
    
    return Response({
        'suggestions': suggestions,
        'chapter': serializer.validated_data['chapter'],
        'generated_at': timezone.now()
    })