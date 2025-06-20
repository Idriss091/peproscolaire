"""
Vues API pour la gestion des notes et évaluations
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Avg, Count, Q, Prefetch
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters import rest_framework as filters
from datetime import date
import csv
from io import StringIO

from .models import (
    EvaluationType, GradingPeriod, Evaluation, Grade,
    SubjectAverage, GeneralAverage, Competence, CompetenceEvaluation
)
from .serializers import (
    EvaluationTypeSerializer, GradingPeriodSerializer,
    EvaluationListSerializer, EvaluationDetailSerializer,
    EvaluationCreateSerializer, GradeSerializer, BulkGradeSerializer,
    SubjectAverageSerializer, GeneralAverageSerializer,
    CompetenceSerializer, CompetenceEvaluationSerializer,
    StudentReportCardSerializer
)
from .tasks import (
    calculate_class_averages, generate_report_cards,
    send_grade_notifications
)
from apps.schools.models import Class
from apps.authentication.models import User


class EvaluationTypeViewSet(viewsets.ModelViewSet):
    """ViewSet pour les types d'évaluation"""
    queryset = EvaluationType.objects.all()
    serializer_class = EvaluationTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


class GradingPeriodViewSet(viewsets.ModelViewSet):
    """ViewSet pour les périodes de notation"""
    serializer_class = GradingPeriodSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['academic_year', 'is_active']
    
    def get_queryset(self):
        """Filtrer par établissement de l'utilisateur"""
        queryset = GradingPeriod.objects.select_related('academic_year')
        
        # TODO: Filtrer par école de l'utilisateur
        return queryset
    
    @action(detail=True, methods=['post'])
    def lock_grades(self, request, pk=None):
        """Verrouiller les notes d'une période"""
        period = self.get_object()
        
        # Vérifier les permissions (admin ou chef d'établissement)
        if request.user.user_type not in ['admin', 'superadmin']:
            return Response(
                {'error': 'Seuls les administrateurs peuvent verrouiller les notes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        period.grades_locked = True
        period.save()
        
        return Response({
            'message': 'Notes verrouillées avec succès',
            'period': GradingPeriodSerializer(period).data
        })
    
    @action(detail=True, methods=['post'])
    def publish_bulletins(self, request, pk=None):
        """Publier les bulletins d'une période"""
        period = self.get_object()
        
        if not period.grades_locked:
            return Response(
                {'error': 'Les notes doivent être verrouillées avant publication'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Lancer la génération des bulletins
        generate_report_cards.delay(period.id)
        
        period.bulletins_published = True
        period.save()
        
        return Response({
            'message': 'Publication des bulletins lancée',
            'period': GradingPeriodSerializer(period).data
        })


class EvaluationFilter(filters.FilterSet):
    """Filtres pour les évaluations"""
    start_date = filters.DateFilter(field_name='date', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='date', lookup_expr='lte')
    
    class Meta:
        model = Evaluation
        fields = [
            'evaluation_type', 'subject', 'class_group',
            'teacher', 'grading_period', 'is_graded',
            'grades_published'
        ]


class EvaluationViewSet(viewsets.ModelViewSet):
    """ViewSet pour les évaluations"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = EvaluationFilter
    
    def get_serializer_class(self):
        if self.action == 'create':
            return EvaluationCreateSerializer
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return EvaluationDetailSerializer
        return EvaluationListSerializer
    
    def get_queryset(self):
        """Filtrer selon le type d'utilisateur"""
        user = self.request.user
        queryset = Evaluation.objects.select_related(
            'evaluation_type', 'subject', 'class_group', 'teacher'
        ).annotate(
            average_score=Avg('grades__score', filter=Q(grades__is_absent=False)),
            graded_count=Count('grades', filter=Q(grades__score__isnull=False))
        )
        
        if user.user_type == 'teacher':
            # Un prof voit ses évaluations
            return queryset.filter(teacher=user)
        
        elif user.user_type == 'student':
            # Un élève voit les évaluations publiées de sa classe
            enrollments = user.enrollments.filter(is_active=True)
            class_ids = enrollments.values_list('class_group_id', flat=True)
            return queryset.filter(
                class_group_id__in=class_ids,
                grades_published=True
            )
        
        # Admin voit tout
        return queryset
    
    @action(detail=True, methods=['get', 'post'])
    def grades(self, request, pk=None):
        """Gérer les notes d'une évaluation"""
        evaluation = self.get_object()
        
        if request.method == 'GET':
            # Récupérer toutes les notes
            grades = evaluation.grades.select_related('student').order_by(
                'student__last_name', 'student__first_name'
            )
            serializer = GradeSerializer(grades, many=True)
            return Response(serializer.data)
        
        else:  # POST
            # Saisie des notes en masse
            serializer = BulkGradeSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            grades_data = serializer.validated_data['grades']
            created_grades = []
            
            for grade_data in grades_data:
                student_id = grade_data.pop('student_id')
                
                # Créer ou mettre à jour la note
                grade, created = Grade.objects.update_or_create(
                    evaluation=evaluation,
                    student_id=student_id,
                    defaults={
                        **grade_data,
                        'graded_by': request.user,
                        'graded_at': timezone.now() if 'score' in grade_data else None,
                        'modified_by': request.user if not created else None
                    }
                )
                created_grades.append(grade)
            
            # Marquer l'évaluation comme corrigée
            if not evaluation.is_graded:
                evaluation.is_graded = True
                evaluation.save()
            
            return Response(
                GradeSerializer(created_grades, many=True).data,
                status=status.HTTP_201_CREATED
            )
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publier les notes d'une évaluation"""
        evaluation = self.get_object()
        
        # Vérifier que c'est le prof de l'évaluation
        if evaluation.teacher != request.user and request.user.user_type != 'admin':
            return Response(
                {'error': 'Seul le professeur peut publier les notes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not evaluation.is_graded:
            return Response(
                {'error': 'L\'évaluation doit être corrigée avant publication'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        evaluation.grades_published = True
        evaluation.save()
        
        # Envoyer des notifications aux élèves
        send_grade_notifications.delay(evaluation.id)
        
        return Response({
            'message': 'Notes publiées avec succès',
            'evaluation': EvaluationListSerializer(evaluation).data
        })
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Statistiques détaillées d'une évaluation"""
        evaluation = self.get_object()
        
        grades = evaluation.grades.filter(
            score__isnull=False,
            is_absent=False
        )
        
        if not grades.exists():
            return Response({'message': 'Aucune note saisie'})
        
        # Statistiques générales
        stats = grades.aggregate(
            average=Avg('score'),
            count=Count('id'),
            min_score=models.Min('score'),
            max_score=models.Max('score')
        )
        
        # Distribution détaillée
        total = grades.count()
        distribution = []
        
        # Par tranches de 2 points
        for i in range(0, int(evaluation.max_score) + 1, 2):
            count = grades.filter(
                score__gte=i,
                score__lt=i + 2
            ).count()
            distribution.append({
                'range': f"{i}-{i+2}",
                'count': count,
                'percentage': round(count / total * 100, 2)
            })
        
        # Analyse par genre (si disponible)
        # TODO: Ajouter le champ genre dans UserProfile
        
        return Response({
            'evaluation': EvaluationListSerializer(evaluation).data,
            'statistics': stats,
            'distribution': distribution,
            'absent_count': evaluation.grades.filter(is_absent=True).count(),
            'not_graded_count': evaluation.grades.filter(score__isnull=True).count()
        })
    
    @action(detail=True, methods=['get'])
    def export_grades(self, request, pk=None):
        """Exporter les notes au format CSV"""
        evaluation = self.get_object()
        
        # Créer le CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # En-têtes
        writer.writerow([
            'Nom', 'Prénom', 'Note', 'Sur', 'Note/20',
            'Absent', 'Commentaire'
        ])
        
        # Données
        grades = evaluation.grades.select_related('student').order_by(
            'student__last_name', 'student__first_name'
        )
        
        for grade in grades:
            writer.writerow([
                grade.student.last_name,
                grade.student.first_name,
                grade.score or '',
                evaluation.max_score,
                grade.normalized_score or '',
                'Oui' if grade.is_absent else 'Non',
                grade.comment
            ])
        
        # Retourner le fichier
        response = Response(
            output.getvalue(),
            content_type='text/csv'
        )
        response['Content-Disposition'] = f'attachment; filename="notes_{evaluation.title}.csv"'
        
        return response


class SubjectAverageViewSet(viewsets.ModelViewSet):
    """ViewSet pour les moyennes par matière"""
    serializer_class = SubjectAverageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['student', 'subject', 'grading_period', 'class_group']
    
    def get_queryset(self):
        """Filtrer selon le type d'utilisateur"""
        user = self.request.user
        queryset = SubjectAverage.objects.select_related(
            'student', 'subject', 'grading_period'
        )
        
        if user.user_type == 'student':
            return queryset.filter(student=user)
        elif user.user_type == 'parent':
            # TODO: Filtrer par enfants
            return queryset.none()
        elif user.user_type == 'teacher':
            # Prof voit les moyennes de ses matières
            return queryset.filter(
                Q(subject__schedules__teacher=user) |
                Q(class_group__main_teacher=user)
            ).distinct()
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """Calculer les moyennes pour une classe/période"""
        class_id = request.data.get('class_id')
        period_id = request.data.get('grading_period_id')
        
        if not all([class_id, period_id]):
            return Response(
                {'error': 'class_id et grading_period_id sont requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Lancer le calcul asynchrone
        calculate_class_averages.delay(class_id, period_id)
        
        return Response({
            'message': 'Calcul des moyennes lancé',
            'class_id': class_id,
            'grading_period_id': period_id
        })


class GeneralAverageViewSet(viewsets.ModelViewSet):
    """ViewSet pour les moyennes générales"""
    serializer_class = GeneralAverageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['student', 'grading_period', 'class_group']
    
    def get_queryset(self):
        """Filtrer selon le type d'utilisateur"""
        user = self.request.user
        queryset = GeneralAverage.objects.select_related(
            'student', 'grading_period'
        ).prefetch_related(
            Prefetch(
                'student__subject_averages',
                queryset=SubjectAverage.objects.select_related('subject')
            )
        )
        
        if user.user_type == 'student':
            return queryset.filter(student=user)
        elif user.user_type == 'parent':
            # TODO: Filtrer par enfants
            return queryset.none()
        elif user.user_type == 'teacher':
            # Prof principal voit sa classe
            return queryset.filter(class_group__main_teacher=user)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """Valider une moyenne générale (conseil de classe)"""
        average = self.get_object()
        
        # Vérifier les permissions
        if request.user.user_type not in ['admin', 'superadmin']:
            return Response(
                {'error': 'Seuls les administrateurs peuvent valider'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Mettre à jour les champs
        average.council_decision = request.data.get('council_decision', average.council_decision)
        average.general_appreciation = request.data.get('general_appreciation', average.general_appreciation)
        average.validated_by = request.user
        average.validated_at = timezone.now()
        average.save()
        
        return Response(GeneralAverageSerializer(average).data)
    
    @action(detail=False, methods=['get'])
    def class_ranking(self, request):
        """Classement d'une classe"""
        class_id = request.query_params.get('class_id')
        period_id = request.query_params.get('grading_period_id')
        
        if not all([class_id, period_id]):
            return Response(
                {'error': 'class_id et grading_period_id sont requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        averages = self.get_queryset().filter(
            class_group_id=class_id,
            grading_period_id=period_id,
            weighted_average__isnull=False
        ).order_by('-weighted_average')
        
        serializer = self.get_serializer(averages, many=True)
        
        return Response({
            'class_id': class_id,
            'grading_period_id': period_id,
            'ranking': serializer.data
        })


class CompetenceViewSet(viewsets.ModelViewSet):
    """ViewSet pour les compétences"""
    queryset = Competence.objects.all()
    serializer_class = CompetenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['domain', 'subject']


class CompetenceEvaluationViewSet(viewsets.ModelViewSet):
    """ViewSet pour l'évaluation des compétences"""
    serializer_class = CompetenceEvaluationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['student', 'competence', 'evaluation', 'grading_period', 'mastery_level']
    
    def get_queryset(self):
        """Filtrer selon le type d'utilisateur"""
        user = self.request.user
        queryset = CompetenceEvaluation.objects.select_related(
            'student', 'competence', 'evaluation'
        )
        
        if user.user_type == 'student':
            return queryset.filter(student=user)
        elif user.user_type == 'teacher':
            # Prof voit les évaluations qu'il a faites
            return queryset.filter(
                Q(evaluated_by=user) |
                Q(evaluation__teacher=user)
            ).distinct()
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def student_summary(self, request):
        """Résumé des compétences d'un élève"""
        student_id = request.query_params.get('student_id')
        period_id = request.query_params.get('grading_period_id')
        
        if not student_id:
            return Response(
                {'error': 'student_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Filtrer les évaluations
        evaluations = self.get_queryset().filter(student_id=student_id)
        
        if period_id:
            evaluations = evaluations.filter(grading_period_id=period_id)
        
        # Grouper par domaine
        summary = {}
        for domain, label in Competence._meta.get_field('domain').choices:
            domain_evals = evaluations.filter(competence__domain=domain)
            
            if domain_evals.exists():
                summary[domain] = {
                    'label': label,
                    'competences': [],
                    'statistics': domain_evals.aggregate(
                        total=Count('id'),
                        expert=Count('id', filter=Q(mastery_level='e')),
                        acquired=Count('id', filter=Q(mastery_level='a')),
                        in_progress=Count('id', filter=Q(mastery_level='ec')),
                        not_acquired=Count('id', filter=Q(mastery_level='na'))
                    )
                }
                
                # Détail par compétence
                for comp_eval in domain_evals.select_related('competence'):
                    summary[domain]['competences'].append({
                        'competence': comp_eval.competence.name,
                        'code': comp_eval.competence.code,
                        'mastery_level': comp_eval.mastery_level,
                        'mastery_level_display': comp_eval.get_mastery_level_display()
                    })
        
        return Response(summary)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def student_report_card(request):
    """Générer le bulletin d'un élève"""
    student_id = request.query_params.get('student_id')
    period_id = request.query_params.get('grading_period_id')
    
    if not all([student_id, period_id]):
        return Response(
            {'error': 'student_id et grading_period_id sont requis'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Vérifier les permissions
    user = request.user
    if user.user_type == 'student' and str(user.id) != student_id:
        return Response(
            {'error': 'Vous ne pouvez voir que votre propre bulletin'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Vérifier que les bulletins sont publiés
    period = get_object_or_404(GradingPeriod, id=period_id)
    if not period.bulletins_published and user.user_type not in ['teacher', 'admin']:
        return Response(
            {'error': 'Les bulletins ne sont pas encore publiés'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = StudentReportCardSerializer(
        data={'student_id': student_id, 'grading_period_id': period_id}
    )
    serializer.is_valid(raise_exception=True)
    
    return Response(serializer.data)