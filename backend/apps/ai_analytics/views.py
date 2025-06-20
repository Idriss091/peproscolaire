"""
Vues API pour l'analyse IA et la détection des risques
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters import rest_framework as filters
from django.db.models import Count, Q, Avg
from datetime import datetime, timedelta

from .models import (
    RiskProfile, RiskIndicator, InterventionPlan,
    InterventionAction, AlertConfiguration, Alert
)
from .serializers import (
    RiskProfileSerializer, RiskProfileCreateSerializer,
    RiskIndicatorSerializer, InterventionPlanSerializer,
    InterventionPlanCreateSerializer, InterventionActionSerializer,
    AlertConfigurationSerializer, AlertSerializer,
    RiskAnalysisRequestSerializer, RiskDashboardSerializer,
    StudentRiskHistorySerializer, ClassRiskReportSerializer,
    InterventionEffectivenessSerializer
)
from .tasks import (
    analyze_student_risk, analyze_class_risks,
    check_and_send_alerts, evaluate_intervention_effectiveness,
    daily_risk_analysis, weekly_pattern_detection
)
from apps.authentication.models import User
from apps.schools.models import Class


class RiskIndicatorViewSet(viewsets.ModelViewSet):
    """ViewSet pour les indicateurs de risque"""
    serializer_class = RiskIndicatorSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = RiskIndicator.objects.all()
    
    def get_queryset(self):
        """Seuls les admins peuvent gérer les indicateurs"""
        if self.request.user.user_type in ['admin', 'superadmin']:
            return RiskIndicator.objects.all()
        return RiskIndicator.objects.filter(is_active=True)


class RiskProfileFilter(filters.FilterSet):
    """Filtres pour les profils de risque"""
    risk_level = filters.MultipleChoiceFilter(
        choices=RiskProfile.RISK_LEVEL_CHOICES
    )
    is_monitored = filters.BooleanFilter()
    min_risk_score = filters.NumberFilter(
        field_name='risk_score',
        lookup_expr='gte'
    )
    max_risk_score = filters.NumberFilter(
        field_name='risk_score',
        lookup_expr='lte'
    )
    
    class Meta:
        model = RiskProfile
        fields = [
            'student', 'academic_year', 'risk_level',
            'is_monitored', 'assigned_to'
        ]


class RiskProfileViewSet(viewsets.ModelViewSet):
    """ViewSet pour les profils de risque"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = RiskProfileFilter
    search_fields = ['student__first_name', 'student__last_name']
    ordering_fields = ['risk_score', 'last_analysis', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return RiskProfileCreateSerializer
        return RiskProfileSerializer
    
    def get_queryset(self):
        """Filtrer selon le type d'utilisateur"""
        user = self.request.user
        queryset = RiskProfile.objects.select_related(
            'student', 'academic_year', 'assigned_to'
        )
        
        if user.user_type == 'student':
            # Un élève voit son propre profil
            return queryset.filter(student=user)
        
        elif user.user_type == 'parent':
            # Un parent voit les profils de ses enfants
            from apps.student_records.models import Guardian
            children_ids = Guardian.objects.filter(
                user=user,
                has_custody=True
            ).values_list('student_record__student_id', flat=True)
            return queryset.filter(student_id__in=children_ids)
        
        elif user.user_type == 'teacher':
            # Un prof voit les profils de ses élèves
            return queryset.filter(
                Q(assigned_to=user) |
                Q(student__enrollments__class_group__main_teacher=user) |
                Q(student__enrollments__class_group__schedules__teacher=user)
            ).distinct()
        
        # Admin voit tout
        return queryset
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """Déclencher une analyse pour un profil"""
        profile = self.get_object()
        
        # Lancer l'analyse asynchrone
        analyze_student_risk.delay(str(profile.id))
        
        return Response({
            'message': 'Analyse lancée',
            'profile_id': str(profile.id)
        })
    
    @action(detail=True, methods=['post'])
    def start_monitoring(self, request, pk=None):
        """Démarrer le suivi d'un élève à risque"""
        profile = self.get_object()
        assigned_to_id = request.data.get('assigned_to')
        
        # Vérifier les permissions
        if request.user.user_type not in ['teacher', 'admin']:
            return Response(
                {'error': 'Seuls les professeurs et administrateurs peuvent démarrer un suivi'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        assigned_to = None
        if assigned_to_id:
            assigned_to = get_object_or_404(User, id=assigned_to_id, user_type='teacher')
        
        profile.start_monitoring(assigned_to=assigned_to)
        
        return Response({
            'message': 'Suivi démarré',
            'profile': RiskProfileSerializer(profile).data
        })
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Historique de risque d'un élève"""
        profile = self.get_object()
        serializer = StudentRiskHistorySerializer(profile.student)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def recommendations(self, request, pk=None):
        """Recommandations détaillées pour un profil"""
        profile = self.get_object()
        
        # Enrichir les recommandations avec plus de contexte
        detailed_recommendations = []
        
        for rec in profile.recommendations:
            detailed_rec = {
                'recommendation': rec,
                'related_resources': self._get_related_resources(rec),
                'success_examples': self._get_success_examples(rec)
            }
            detailed_recommendations.append(detailed_rec)
        
        return Response({
            'profile_id': str(profile.id),
            'student': profile.student.get_full_name(),
            'risk_level': profile.get_risk_level_display(),
            'recommendations': detailed_recommendations,
            'priority_actions': profile.priority_actions
        })
    
    def _get_related_resources(self, recommendation):
        """Obtenir des ressources liées à une recommandation"""
        # Simplifié pour l'exemple
        resources_map = {
            'soutien scolaire': [
                {'type': 'guide', 'title': 'Guide du soutien scolaire', 'url': '#'},
                {'type': 'contact', 'title': 'Coordinateur du soutien', 'email': 'soutien@ecole.fr'}
            ],
            'suivi d\'assiduité': [
                {'type': 'procedure', 'title': 'Protocole de suivi d\'assiduité', 'url': '#'},
                {'type': 'form', 'title': 'Fiche de suivi', 'url': '#'}
            ]
        }
        
        for key in resources_map:
            if key in recommendation.lower():
                return resources_map[key]
        
        return []
    
    def _get_success_examples(self, recommendation):
        """Obtenir des exemples de réussite similaires"""
        # Simplifié pour l'exemple
        return [
            "Élève A : amélioration de 3 points après 2 mois de soutien",
            "Élève B : retour à une assiduité normale après suivi familial"
        ]


class InterventionPlanViewSet(viewsets.ModelViewSet):
    """ViewSet pour les plans d'intervention"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['status', 'coordinator', 'risk_profile__student']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return InterventionPlanCreateSerializer
        return InterventionPlanSerializer
    
    def get_queryset(self):
        """Filtrer selon le type d'utilisateur"""
        user = self.request.user
        queryset = InterventionPlan.objects.select_related(
            'risk_profile__student',
            'coordinator'
        ).prefetch_related('participants', 'actions')
        
        if user.user_type == 'student':
            # Un élève voit ses propres plans
            return queryset.filter(risk_profile__student=user)
        
        elif user.user_type == 'parent':
            # Un parent voit les plans de ses enfants
            from apps.student_records.models import Guardian
            children_ids = Guardian.objects.filter(
                user=user,
                has_custody=True
            ).values_list('student_record__student_id', flat=True)
            return queryset.filter(risk_profile__student_id__in=children_ids)
        
        elif user.user_type == 'teacher':
            # Un prof voit les plans où il est impliqué
            return queryset.filter(
                Q(coordinator=user) |
                Q(participants=user) |
                Q(actions__responsible=user)
            ).distinct()
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def add_action(self, request, pk=None):
        """Ajouter une action à un plan"""
        plan = self.get_object()
        
        # Vérifier les permissions
        if request.user != plan.coordinator and request.user.user_type != 'admin':
            return Response(
                {'error': 'Seul le coordinateur peut ajouter des actions'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = InterventionActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        action = serializer.save(intervention_plan=plan)
        
        return Response(
            InterventionActionSerializer(action).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def evaluate_effectiveness(self, request, pk=None):
        """Évaluer l'efficacité d'un plan"""
        plan = self.get_object()
        
        serializer = InterventionEffectivenessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        plan = serializer.update(plan, serializer.validated_data)
        
        # Lancer l'analyse d'efficacité
        evaluate_intervention_effectiveness.delay(str(plan.id))
        
        return Response({
            'message': 'Évaluation enregistrée',
            'plan': InterventionPlanSerializer(plan).data
        })
    
    @action(detail=False, methods=['get'])
    def my_interventions(self, request):
        """Interventions où l'utilisateur est impliqué"""
        user = request.user
        
        if user.user_type != 'teacher':
            return Response(
                {'error': 'Réservé aux enseignants'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Plans actifs où le prof est impliqué
        active_plans = self.get_queryset().filter(
            status='active'
        ).filter(
            Q(coordinator=user) |
            Q(participants=user) |
            Q(actions__responsible=user)
        ).distinct()
        
        # Actions à venir
        upcoming_actions = InterventionAction.objects.filter(
            Q(responsible=user) |
            Q(intervention_plan__coordinator=user),
            completed=False,
            scheduled_date__gte=timezone.now().date()
        ).order_by('scheduled_date', 'scheduled_time')[:10]
        
        return Response({
            'active_plans': InterventionPlanSerializer(active_plans, many=True).data,
            'upcoming_actions': InterventionActionSerializer(upcoming_actions, many=True).data,
            'stats': {
                'total_plans': active_plans.count(),
                'actions_pending': upcoming_actions.count()
            }
        })


class InterventionActionViewSet(viewsets.ModelViewSet):
    """ViewSet pour les actions d'intervention"""
    serializer_class = InterventionActionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['intervention_plan', 'responsible', 'completed', 'action_type']
    
    def get_queryset(self):
        """Filtrer selon les permissions"""
        user = self.request.user
        queryset = InterventionAction.objects.select_related(
            'intervention_plan__risk_profile__student',
            'responsible'
        )
        
        if user.user_type == 'teacher':
            # Actions où le prof est responsable ou coordinateur
            return queryset.filter(
                Q(responsible=user) |
                Q(intervention_plan__coordinator=user)
            ).distinct()
        
        elif user.user_type in ['admin', 'superadmin']:
            return queryset
        
        return queryset.none()
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Marquer une action comme complétée"""
        action = self.get_object()
        
        # Vérifier les permissions
        if request.user != action.responsible and request.user != action.intervention_plan.coordinator:
            return Response(
                {'error': 'Seul le responsable peut compléter cette action'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        notes = request.data.get('notes', '')
        impact = request.data.get('impact_assessment')
        
        action.mark_completed(notes=notes)
        
        if impact:
            action.impact_assessment = impact
            action.save()
        
        return Response({
            'message': 'Action complétée',
            'action': InterventionActionSerializer(action).data
        })
    
    @action(detail=False, methods=['get'])
    def calendar(self, request):
        """Vue calendrier des actions"""
        start_date = request.query_params.get('start_date', str(datetime.now().date()))
        end_date = request.query_params.get('end_date')
        
        if not end_date:
            end_date = (datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=30)).date()
        
        actions = self.get_queryset().filter(
            scheduled_date__range=[start_date, end_date]
        ).order_by('scheduled_date', 'scheduled_time')
        
        # Organiser par date
        calendar_data = {}
        for action in actions:
            date_str = str(action.scheduled_date)
            if date_str not in calendar_data:
                calendar_data[date_str] = []
            
            calendar_data[date_str].append({
                'id': str(action.id),
                'time': str(action.scheduled_time) if action.scheduled_time else None,
                'title': action.title,
                'type': action.get_action_type_display(),
                'student': action.intervention_plan.risk_profile.student.get_full_name(),
                'responsible': action.responsible.get_full_name() if action.responsible else None,
                'completed': action.completed
            })
        
        return Response({
            'start_date': str(start_date),
            'end_date': str(end_date),
            'calendar': calendar_data
        })


class AlertConfigurationViewSet(viewsets.ModelViewSet):
    """ViewSet pour la configuration des alertes"""
    serializer_class = AlertConfigurationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Seuls les admins peuvent gérer les configurations"""
        if self.request.user.user_type in ['admin', 'superadmin']:
            return AlertConfiguration.objects.prefetch_related('additional_recipients')
        return AlertConfiguration.objects.none()
    
    @action(detail=True, methods=['post'])
    def test_alert(self, request, pk=None):
        """Tester une configuration d'alerte"""
        config = self.get_object()
        
        # Créer une alerte de test
        from .models import RiskProfile
        
        # Prendre un profil à risque pour le test
        test_profile = RiskProfile.objects.filter(
            risk_level__in=['high', 'critical']
        ).first()
        
        if not test_profile:
            return Response(
                {'error': 'Aucun profil de test disponible'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
                # Simuler le déclenchement
        if config.should_trigger(test_profile):
            # Créer l'alerte de test
            alert = Alert.objects.create(
                risk_profile=test_profile,
                alert_configuration=config,
                title=f"[TEST] {config.name}",
                # On limite volontairement les placeholders pour éviter les KeyError
                message=config.message_template.format(
                    student_name=test_profile.student.get_full_name(),
                    risk_level=test_profile.get_risk_level_display(),
                ),
                is_test=True,  # champ booléen à prévoir dans le modèle pour distinguer les tests
            )

            # Lancer l'envoi de l'alerte en asynchrone
            check_and_send_alerts.delay(str(alert.id))

            return Response(
                {
                    'message': 'Alerte de test envoyée',
                    'alert': AlertSerializer(alert).data
                },
                status=status.HTTP_201_CREATED
            )

        # Sinon, la condition n'est pas remplie
        return Response(
            {'message': 'La configuration ne se déclenche pas pour ce profil.'},
            status=status.HTTP_200_OK
        )


class AlertViewSet(viewsets.ModelViewSet):
    """ViewSet pour les alertes"""
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['is_acknowledged', 'priority', 'risk_profile__student']
    
    def get_queryset(self):
        """Filtrer les alertes selon les permissions"""
        user = self.request.user
        queryset = Alert.objects.select_related(
            'risk_profile__student',
            'alert_configuration',
            'acknowledged_by'
        ).prefetch_related('read_by')
        
        if user.user_type == 'student':
            # Un élève voit ses propres alertes
            return queryset.filter(risk_profile__student=user)
        
        elif user.user_type == 'parent':
            # Un parent voit les alertes de ses enfants
            from apps.student_records.models import Guardian
            children_ids = Guardian.objects.filter(
                user=user,
                has_custody=True
            ).values_list('student_record__student_id', flat=True)
            return queryset.filter(risk_profile__student_id__in=children_ids)
        
        elif user.user_type == 'teacher':
            # Un prof voit les alertes de ses élèves
            return queryset.filter(
                Q(risk_profile__assigned_to=user) |
                Q(risk_profile__student__enrollments__class_group__main_teacher=user) |
                Q(risk_profile__student__enrollments__class_group__schedules__teacher=user)
            ).distinct()
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Prendre en compte une alerte"""
        alert = self.get_object()
        actions = request.data.get('actions_taken', '')
        
        alert.acknowledge(request.user, actions)
        
        return Response({
            'message': 'Alerte prise en compte',
            'alert': AlertSerializer(alert).data
        })
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Marquer une alerte comme lue"""
        alert = self.get_object()
        alert.read_by.add(request.user)
        
        # Si tous les destinataires ont lu l'alerte
        if alert.read_by.count() >= 3:  # Seuil arbitraire
            alert.is_read = True
            alert.save()
        
        return Response({'message': 'Alerte marquée comme lue'})
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Dashboard des alertes"""
        user = request.user
        queryset = self.get_queryset()
        
        # Statistiques des alertes
        stats = {
            'total': queryset.count(),
            'unacknowledged': queryset.filter(is_acknowledged=False).count(),
            'high_priority': queryset.filter(priority__in=['high', 'urgent']).count(),
            'recent': queryset.filter(created_at__gte=timezone.now() - timedelta(days=7)).count()
        }
        
        # Alertes par priorité
        priority_distribution = {}
        for priority, _ in Alert._meta.get_field('priority').choices:
            priority_distribution[priority] = queryset.filter(priority=priority).count()
        
        # Alertes récentes non traitées
        recent_alerts = queryset.filter(
            is_acknowledged=False,
            created_at__gte=timezone.now() - timedelta(days=3)
        ).order_by('-created_at', '-priority')[:10]
        
        return Response({
            'stats': stats,
            'priority_distribution': priority_distribution,
            'recent_alerts': AlertSerializer(recent_alerts, many=True).data
        })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def trigger_risk_analysis(request):
    """Déclencher une analyse de risque"""
    serializer = RiskAnalysisRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    student_id = serializer.validated_data.get('student_id')
    class_id = serializer.validated_data.get('class_id')
    force_update = serializer.validated_data.get('force_update', False)
    
    tasks_launched = []
    
    if student_id:
        # Analyse individuelle
        from .models import RiskProfile
        try:
            profile = RiskProfile.objects.get(
                student_id=student_id,
                academic_year__start_date__lte=timezone.now(),
                academic_year__end_date__gte=timezone.now()
            )
            task = analyze_student_risk.delay(str(profile.id))
            tasks_launched.append(str(task.id))
        except RiskProfile.DoesNotExist:
            return Response(
                {'error': 'Profil de risque non trouvé pour cet élève'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    if class_id:
        # Analyse de classe
        task = analyze_class_risks.delay(str(class_id))
        tasks_launched.append(str(task.id))
    
    return Response({
        'message': 'Analyses lancées',
        'tasks': tasks_launched
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def risk_dashboard(request):
    """Dashboard principal des risques"""
    user = request.user
    
    # Vérifier les permissions
    if user.user_type not in ['teacher', 'admin', 'superadmin']:
        return Response(
            {'error': 'Accès réservé aux enseignants et administrateurs'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Année scolaire actuelle
    from apps.schools.models import AcademicYear
    current_year = AcademicYear.objects.filter(
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    ).first()
    
    if not current_year:
        return Response({'error': 'Aucune année scolaire active'})
    
    # Profils de risque de l'année
    risk_profiles = RiskProfile.objects.filter(
        academic_year=current_year
    ).select_related('student', 'assigned_to')
    
    # Filtrer selon les permissions
    if user.user_type == 'teacher':
        risk_profiles = risk_profiles.filter(
            Q(assigned_to=user) |
            Q(student__enrollments__class_group__main_teacher=user) |
            Q(student__enrollments__class_group__schedules__teacher=user)
        ).distinct()
    
    # Statistiques générales
    total_students = risk_profiles.count()
    risk_distribution = {
        'very_low': risk_profiles.filter(risk_level='very_low').count(),
        'low': risk_profiles.filter(risk_level='low').count(),
        'moderate': risk_profiles.filter(risk_level='moderate').count(),
        'high': risk_profiles.filter(risk_level='high').count(),
        'critical': risk_profiles.filter(risk_level='critical').count(),
    }
    
    # Élèves à risque par ordre de priorité
    at_risk_students = risk_profiles.filter(
        risk_level__in=['high', 'critical']
    ).order_by('-risk_score')[:20]
    
    # Tendances récentes
    recent_analyses = risk_profiles.filter(
        last_analysis__gte=timezone.now() - timedelta(days=7)
    ).order_by('-last_analysis')[:10]
    
    # Alertes récentes
    recent_alerts = Alert.objects.filter(
        risk_profile__in=risk_profiles,
        created_at__gte=timezone.now() - timedelta(days=7),
        is_acknowledged=False
    ).order_by('-created_at', '-priority')[:10]
    
    # Interventions actives
    active_interventions = InterventionPlan.objects.filter(
        risk_profile__in=risk_profiles,
        status='active'
    ).count()
    
    # Comparaison par classe (pour les admins)
    class_comparison = []
    if user.user_type in ['admin', 'superadmin']:
        from apps.schools.models import Class
        classes = Class.objects.filter(
            academic_year=current_year
        ).prefetch_related('students__student')
        
        for class_obj in classes[:10]:  # Limiter à 10 classes
            class_profiles = risk_profiles.filter(
                student__enrollments__class_group=class_obj
            )
            
            if class_profiles.exists():
                class_comparison.append({
                    'class_name': str(class_obj),
                    'total_students': class_profiles.count(),
                    'at_risk_count': class_profiles.filter(risk_level__in=['high', 'critical']).count(),
                    'average_risk_score': class_profiles.aggregate(avg=Avg('risk_score'))['avg'] or 0
                })
    
    dashboard_data = {
        'summary': {
            'total_students': total_students,
            'at_risk_students': risk_distribution['high'] + risk_distribution['critical'],
            'monitored_students': risk_profiles.filter(is_monitored=True).count(),
            'active_interventions': active_interventions,
            'unacknowledged_alerts': len(recent_alerts)
        },
        'risk_distribution': risk_distribution,
        'trending_students': RiskProfileSerializer(recent_analyses, many=True).data,
        'recent_alerts': AlertSerializer(recent_alerts, many=True).data,
        'intervention_stats': {
            'active_plans': active_interventions,
            'completion_rate': 0.75,  # À calculer dynamiquement
            'average_effectiveness': 7.2  # À calculer dynamiquement
        },
        'class_comparison': class_comparison
    }
    
    serializer = RiskDashboardSerializer(dashboard_data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def student_risk_history(request, student_id):
    """Historique de risque d'un élève"""
    student = get_object_or_404(User, id=student_id, user_type='student')
    
    # Vérifier les permissions
    user = request.user
    if user.user_type == 'student' and user != student:
        return Response(
            {'error': 'Accès refusé'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = StudentRiskHistorySerializer(student)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def class_risk_report(request, class_id):
    """Rapport de risque d'une classe"""
    from apps.schools.models import Class
    class_obj = get_object_or_404(Class, id=class_id)
    
    # Vérifier les permissions
    user = request.user
    if user.user_type == 'teacher':
        # Vérifier si le prof enseigne dans cette classe
        if not (class_obj.main_teacher == user or 
                class_obj.schedules.filter(teacher=user).exists()):
            return Response(
                {'error': 'Accès refusé'},
                status=status.HTTP_403_FORBIDDEN
            )
    
    serializer = ClassRiskReportSerializer(class_obj)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_risk_analysis(request):
    """Analyse en lot"""
    if request.user.user_type not in ['admin', 'superadmin']:
        return Response(
            {'error': 'Accès réservé aux administrateurs'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    analysis_type = request.data.get('type', 'daily')
    
    if analysis_type == 'daily':
        task = daily_risk_analysis.delay()
    elif analysis_type == 'patterns':
        task = weekly_pattern_detection.delay()
    else:
        return Response(
            {'error': 'Type d\'analyse non reconnu'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    return Response({
        'message': f'Analyse {analysis_type} lancée',
        'task_id': str(task.id)
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def risk_statistics(request):
    """Statistiques avancées des risques"""
    if request.user.user_type not in ['admin', 'superadmin']:
        return Response(
            {'error': 'Accès réservé aux administrateurs'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Période d'analyse
    period_days = int(request.query_params.get('period_days', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=period_days)
    
    # Évolution des scores de risque
    risk_evolution = []
    profiles = RiskProfile.objects.filter(
        last_analysis__date__range=[start_date, end_date]
    )
    
    # Grouper par semaine
    current_date = start_date
    while current_date <= end_date:
        week_end = min(current_date + timedelta(days=7), end_date)
        week_profiles = profiles.filter(
            last_analysis__date__range=[current_date, week_end]
        )
        
        if week_profiles.exists():
            avg_score = week_profiles.aggregate(avg=Avg('risk_score'))['avg']
            risk_evolution.append({
                'week': current_date.strftime('%Y-W%U'),
                'average_risk_score': round(avg_score, 1),
                'students_analyzed': week_profiles.count()
            })
        
        current_date = week_end + timedelta(days=1)
    
    # Efficacité des interventions
    interventions = InterventionPlan.objects.filter(
        created_at__date__range=[start_date, end_date],
        effectiveness_score__isnull=False
    )
    
    intervention_effectiveness = {
        'total_interventions': interventions.count(),
        'average_effectiveness': interventions.aggregate(
            avg=Avg('effectiveness_score')
        )['avg'] or 0,
        'successful_interventions': interventions.filter(
            effectiveness_score__gte=7
        ).count()
    }
    
    # Patterns détectés
    patterns_detected = RiskProfile.objects.filter(
        indicators__has_key='detected_patterns',
        updated_at__date__range=[start_date, end_date]
    ).count()
    
    return Response({
        'period': {
            'start_date': str(start_date),
            'end_date': str(end_date),
            'days': period_days
        },
        'risk_evolution': risk_evolution,
        'intervention_effectiveness': intervention_effectiveness,
        'patterns_detected': patterns_detected,
        'alert_statistics': {
            'total_alerts': Alert.objects.filter(
                created_at__date__range=[start_date, end_date]
            ).count(),
            'acknowledged_rate': Alert.objects.filter(
                created_at__date__range=[start_date, end_date],
                is_acknowledged=True
            ).count() / max(1, Alert.objects.filter(
                created_at__date__range=[start_date, end_date]
            ).count()) * 100
        }
    })


# ====== NOUVEAUX ENDPOINTS POUR MODULES IA ======

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_appreciation(request):
    """Générer une appréciation avec IA"""
    from apps.ai_modules.appreciation_generator import AppreciationGenerator
    from apps.grades.models import SubjectAverage, GradingPeriod
    from apps.schools.models import Subject
    
    # Vérifier les permissions
    if request.user.user_type not in ['teacher', 'admin']:
        return Response(
            {'error': 'Seuls les enseignants peuvent générer des appréciations'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        # Récupérer les paramètres
        student_id = request.data.get('student_id')
        subject_id = request.data.get('subject_id')
        period_id = request.data.get('period_id')
        options = request.data.get('options', {})
        
        # Validation des données
        if not all([student_id, subject_id, period_id]):
            return Response(
                {'error': 'student_id, subject_id et period_id sont requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Récupérer les objets
        student = get_object_or_404(User, id=student_id, user_type='student')
        subject = get_object_or_404(Subject, id=subject_id)
        period = get_object_or_404(GradingPeriod, id=period_id)
        
        # Récupérer la moyenne de l'élève
        subject_average = SubjectAverage.objects.filter(
            student=student,
            subject=subject,
            grading_period=period
        ).first()
        
        average = subject_average.average if subject_average else None
        
        # Générer l'appréciation
        generator = AppreciationGenerator()
        result = generator.generate_appreciation(student, subject, average, period, options)
        
        return Response({
            'success': True,
            'appreciation': result,
            'student': {
                'id': str(student.id),
                'name': student.get_full_name()
            },
            'subject': {
                'id': str(subject.id),
                'name': subject.name
            },
            'period': {
                'id': str(period.id),
                'name': period.name
            },
            'average': float(average) if average else None
        })
        
    except Exception as e:
        logger.error(f"Erreur génération appréciation: {e}")
        return Response(
            {'error': f'Erreur lors de la génération: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_multiple_appreciations(request):
    """Générer des appréciations pour plusieurs élèves"""
    from apps.ai_modules.appreciation_generator import AppreciationGenerator
    from apps.grades.models import SubjectAverage, GradingPeriod
    from apps.schools.models import Subject, Class
    
    # Vérifier les permissions
    if request.user.user_type not in ['teacher', 'admin']:
        return Response(
            {'error': 'Seuls les enseignants peuvent générer des appréciations'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        # Récupérer les paramètres
        class_id = request.data.get('class_id')
        subject_id = request.data.get('subject_id')
        period_id = request.data.get('period_id')
        student_ids = request.data.get('student_ids', [])
        options = request.data.get('options', {})
        
        # Validation
        if not all([subject_id, period_id]):
            return Response(
                {'error': 'subject_id et period_id sont requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        subject = get_object_or_404(Subject, id=subject_id)
        period = get_object_or_404(GradingPeriod, id=period_id)
        
        # Déterminer les élèves
        students = []
        if class_id:
            class_obj = get_object_or_404(Class, id=class_id)
            students = [enrollment.student for enrollment in class_obj.students.filter(is_active=True)]
        elif student_ids:
            students = User.objects.filter(id__in=student_ids, user_type='student')
        else:
            return Response(
                {'error': 'class_id ou student_ids requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Préparer les données pour la génération
        students_data = []
        for student in students:
            subject_average = SubjectAverage.objects.filter(
                student=student,
                subject=subject,
                grading_period=period
            ).first()
            
            students_data.append({
                'student': student,
                'subject': subject,
                'average': subject_average.average if subject_average else None,
                'period': period
            })
        
        # Générer toutes les appréciations
        generator = AppreciationGenerator()
        results = generator.generate_multiple_appreciations(students_data, options)
        
        return Response({
            'success': True,
            'total_students': len(students_data),
            'successful_generations': len([r for r in results if r['status'] == 'success']),
            'failed_generations': len([r for r in results if r['status'] == 'error']),
            'results': results,
            'options_used': options
        })
        
    except Exception as e:
        logger.error(f"Erreur génération multiple: {e}")
        return Response(
            {'error': f'Erreur lors de la génération: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def train_ai_model(request):
    """Entraîner ou ré-entraîner un modèle IA"""
    # Vérifier les permissions admin
    if request.user.user_type not in ['admin', 'superadmin']:
        return Response(
            {'error': 'Seuls les administrateurs peuvent entraîner les modèles'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        from .tasks import train_ml_model
        
        model_type = request.data.get('model_type', 'dropout_risk')
        force_retrain = request.data.get('force_retrain', False)
        
        # Valider le type de modèle
        if model_type not in ['dropout_risk', 'performance_prediction']:
            return Response(
                {'error': 'Type de modèle non supporté'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Lancer l'entraînement asynchrone
        task = train_ml_model.delay(model_type, force_retrain)
        
        return Response({
            'message': f'Entraînement du modèle {model_type} lancé',
            'task_id': str(task.id),
            'force_retrain': force_retrain
        })
        
    except Exception as e:
        logger.error(f"Erreur lancement entraînement: {e}")
        return Response(
            {'error': f'Erreur lors du lancement: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def ai_model_status(request):
    """Status et métriques des modèles IA"""
    # Vérifier les permissions
    if request.user.user_type not in ['teacher', 'admin', 'superadmin']:
        return Response(
            {'error': 'Accès réservé'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        from django.core.cache import cache
        from .ml_models import ModelTrainer
        
        # Récupérer les métriques depuis le cache
        model_performance = cache.get('ai_model_performance', {})
        dashboard_metrics = cache.get('ai_dashboard_metrics', {})
        
        # Si pas de cache, évaluer en temps réel (limité)
        if not model_performance:
            try:
                trainer = ModelTrainer()
                model_performance = trainer.evaluate_model_performance()
            except Exception as e:
                model_performance = {'error': f'Impossible d\'évaluer le modèle: {str(e)}'}
        
        # Modèles disponibles et leur status
        models_status = {
            'dropout_risk': {
                'name': 'Détection de décrochage',
                'status': 'active' if 'error' not in model_performance else 'error',
                'performance': model_performance,
                'last_training': dashboard_metrics.get('last_update', 'N/A'),
                'features_count': 18,
                'training_samples': model_performance.get('test_samples', 'N/A')
            },
            'appreciation_generator': {
                'name': 'Générateur d\'appréciations',
                'status': 'active',
                'performance': {
                    'api_status': 'configured' if hasattr(settings, 'OPENAI_API_KEY') else 'not_configured',
                    'fallback_available': True
                },
                'last_update': 'Always available',
                'features': ['Analyse contextuelle', 'Templates intelligents', 'Post-traitement']
            }
        }
        
        return Response({
            'models': models_status,
            'global_metrics': dashboard_metrics,
            'system_status': {
                'total_profiles': dashboard_metrics.get('total_profiles', 0),
                'high_risk_students': dashboard_metrics.get('high_risk_count', 0),
                'average_risk_score': dashboard_metrics.get('average_risk_score', 0),
                'last_analysis_update': dashboard_metrics.get('last_update')
            }
        })
        
    except Exception as e:
        logger.error(f"Erreur status modèles IA: {e}")
        return Response(
            {'error': f'Erreur lors de la récupération du status: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def predict_student_risk(request):
    """Prédire le risque de décrochage d'un élève"""
    # Vérifier les permissions
    if request.user.user_type not in ['teacher', 'admin']:
        return Response(
            {'error': 'Seuls les enseignants peuvent lancer des prédictions'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        from .ml_models import DropoutRiskModel
        from .analyzers import StudentDataAnalyzer
        
        student_id = request.data.get('student_id')
        if not student_id:
            return Response(
                {'error': 'student_id requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        student = get_object_or_404(User, id=student_id, user_type='student')
        
        # Analyser les données de l'élève
        analyzer = StudentDataAnalyzer(student)
        student_data = analyzer.collect_all_data()
        
        # Prédire avec le modèle ML
        model = DropoutRiskModel()
        prediction = model.predict(student_data['features'])
        
        return Response({
            'student': {
                'id': str(student.id),
                'name': student.get_full_name()
            },
            'prediction': prediction,
            'data_collected': {
                'analysis_date': student_data['analysis_date'],
                'features_count': len(student_data['features'])
            }
        })
        
    except Exception as e:
        logger.error(f"Erreur prédiction risque: {e}")
        return Response(
            {'error': f'Erreur lors de la prédiction: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def ai_dashboard_metrics(request):
    """Métriques détaillées pour le dashboard IA"""
    # Vérifier les permissions
    if request.user.user_type not in ['teacher', 'admin', 'superadmin']:
        return Response(
            {'error': 'Accès réservé'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        from django.core.cache import cache
        from .tasks import update_model_performance_metrics
        
        # Récupérer les métriques du cache
        metrics = cache.get('ai_dashboard_metrics')
        
        if not metrics:
            # Si pas de cache, lancer la mise à jour
            update_model_performance_metrics.delay()
            metrics = {
                'message': 'Métriques en cours de calcul',
                'refresh_in': '1-2 minutes'
            }
        
        # Ajouter des métriques temps réel
        from .models import RiskProfile, Alert
        from django.utils import timezone
        from datetime import timedelta
        
        real_time_metrics = {
            'recent_alerts': Alert.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=24),
                is_acknowledged=False
            ).count(),
            'profiles_analyzed_today': RiskProfile.objects.filter(
                last_analysis__date=timezone.now().date()
            ).count(),
            'interventions_active': InterventionPlan.objects.filter(
                status='active'
            ).count()
        }
        
        # Fusionner les métriques
        if isinstance(metrics, dict) and 'message' not in metrics:
            metrics.update(real_time_metrics)
        
        return Response(metrics)
        
    except Exception as e:
        logger.error(f"Erreur métriques dashboard IA: {e}")
        return Response(
            {'error': f'Erreur lors de la récupération des métriques: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
