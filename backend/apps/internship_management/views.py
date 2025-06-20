from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Count, Avg, F
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
import logging

from .models import (
    Company, InternshipOffer, InternshipApplication,
    Internship, InternshipVisit, InternshipEvaluation
)
from .serializers import (
    CompanySerializer, CompanyListSerializer,
    InternshipOfferSerializer, InternshipOfferListSerializer,
    InternshipApplicationSerializer, InternshipApplicationCreateSerializer,
    InternshipSerializer, InternshipListSerializer,
    InternshipVisitSerializer, InternshipEvaluationSerializer,
    InternshipStatsSerializer, InternshipSearchSerializer,
    InternshipReportSerializer
)
from .filters import InternshipOfferFilter, InternshipFilter
from ..core.permissions import IsStudentOrParentOrTeacher

logger = logging.getLogger(__name__)


class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour les entreprises (lecture seule pour les étudiants)
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sector', 'size', 'city', 'is_partner', 'is_active']
    search_fields = ['name', 'description', 'city']
    ordering_fields = ['name', 'average_rating', 'total_internships']
    ordering = ['name']
    
    def get_queryset(self):
        return Company.objects.filter(is_active=True)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CompanyListSerializer
        return CompanySerializer
    
    @action(detail=True, methods=['get'])
    def offers(self, request, pk=None):
        """
        Retourne les offres actives d'une entreprise
        """
        company = self.get_object()
        offers = company.offers.filter(
            status='published',
            application_deadline__gte=timezone.now().date()
        )
        
        serializer = InternshipOfferListSerializer(offers, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """
        Statistiques d'une entreprise
        """
        company = self.get_object()
        
        internships = company.internships.all()
        stats = {
            'total_internships': internships.count(),
            'ongoing_internships': internships.filter(status='ongoing').count(),
            'completed_internships': internships.filter(status='completed').count(),
            'average_student_rating': internships.filter(
                student_rating__isnull=False
            ).aggregate(avg=Avg('student_rating'))['avg'] or 0,
            'average_company_rating': internships.filter(
                company_rating__isnull=False
            ).aggregate(avg=Avg('company_rating'))['avg'] or 0,
            'active_offers': company.offers.filter(status='published').count(),
            'partnership_duration': (
                (timezone.now().date() - company.partnership_since).days
                if company.partnership_since else 0
            )
        }
        
        return Response(stats)


class InternshipOfferViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour les offres de stage
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = InternshipOfferFilter
    search_fields = ['title', 'description', 'company__name', 'department']
    ordering_fields = ['start_date', 'application_deadline', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return InternshipOffer.objects.filter(
            status='published',
            application_deadline__gte=timezone.now().date()
        ).select_related('company')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return InternshipOfferListSerializer
        return InternshipOfferSerializer
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """
        Recherche avancée d'offres de stage
        """
        serializer = InternshipSearchSerializer(data=request.data)
        
        if serializer.is_valid():
            queryset = self.get_queryset()
            
            # Filtrage par requête textuelle
            if serializer.validated_data.get('query'):
                query = serializer.validated_data['query']
                queryset = queryset.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query) |
                    Q(company__name__icontains=query) |
                    Q(department__icontains=query)
                )
            
            # Filtrage par secteur
            if serializer.validated_data.get('sector'):
                queryset = queryset.filter(
                    company__sector=serializer.validated_data['sector']
                )
            
            # Filtrage par ville
            if serializer.validated_data.get('city'):
                queryset = queryset.filter(
                    company__city__icontains=serializer.validated_data['city']
                )
            
            # Filtrage par type d'offre
            if serializer.validated_data.get('offer_type'):
                queryset = queryset.filter(
                    offer_type=serializer.validated_data['offer_type']
                )
            
            # Filtrage par rémunération
            if serializer.validated_data.get('is_paid') is not None:
                queryset = queryset.filter(
                    is_paid=serializer.validated_data['is_paid']
                )
            
            # Filtrage par télétravail
            if serializer.validated_data.get('remote_possible') is not None:
                queryset = queryset.filter(
                    remote_possible=serializer.validated_data['remote_possible']
                )
            
            # Filtrage par dates de début
            if serializer.validated_data.get('start_date_from'):
                queryset = queryset.filter(
                    start_date__gte=serializer.validated_data['start_date_from']
                )
            
            if serializer.validated_data.get('start_date_to'):
                queryset = queryset.filter(
                    start_date__lte=serializer.validated_data['start_date_to']
                )
            
            # Pagination
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer_data = InternshipOfferListSerializer(page, many=True)
                return self.get_paginated_response(serializer_data.data)
            
            serializer_data = InternshipOfferListSerializer(queryset, many=True)
            return Response({
                'results': serializer_data.data,
                'total': queryset.count()
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        """
        Retourne des offres similaires
        """
        offer = self.get_object()
        
        similar_offers = InternshipOffer.objects.filter(
            status='published',
            application_deadline__gte=timezone.now().date()
        ).exclude(id=offer.id).filter(
            Q(company__sector=offer.company.sector) |
            Q(offer_type=offer.offer_type) |
            Q(company__city=offer.company.city)
        ).distinct()[:5]
        
        serializer = InternshipOfferListSerializer(similar_offers, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """
        Candidater à une offre de stage
        """
        offer = self.get_object()
        
        # Vérifier si l'utilisateur peut candidater
        if not offer.can_apply():
            return Response({
                'error': 'Cette offre n\'est plus disponible pour candidature'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier si l'utilisateur a déjà candidaté
        if InternshipApplication.objects.filter(
            student=request.user, offer=offer
        ).exists():
            return Response({
                'error': 'Vous avez déjà candidaté à cette offre'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Créer la candidature
        serializer = InternshipApplicationCreateSerializer(
            data=request.data, context={'request': request}
        )
        
        if serializer.is_valid():
            application = serializer.save(offer=offer)
            
            return Response({
                'message': 'Candidature créée avec succès',
                'application_id': str(application.id)
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InternshipApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les candidatures de stage
    """
    serializer_class = InternshipApplicationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'offer__company', 'offer__offer_type']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return InternshipApplication.objects.filter(
            student=self.request.user
        ).select_related('offer__company')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return InternshipApplicationCreateSerializer
        return InternshipApplicationSerializer
    
    def perform_create(self, serializer):
        serializer.save(student=self.request.user)
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        Soumet une candidature
        """
        application = self.get_object()
        
        if application.status != 'draft':
            return Response({
                'error': 'Cette candidature a déjà été soumise'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            application.submit()
            
            # Envoyer une notification à l'entreprise
            self._send_application_notification(application)
            
            return Response({
                'message': 'Candidature soumise avec succès',
                'status': application.status
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la soumission: {e}")
            return Response({
                'error': 'Erreur lors de la soumission'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        """
        Retire une candidature
        """
        application = self.get_object()
        
        if application.status not in ['submitted', 'under_review']:
            return Response({
                'error': 'Cette candidature ne peut pas être retirée'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        application.status = 'withdrawn'
        application.save()
        
        return Response({
            'message': 'Candidature retirée',
            'status': application.status
        })
    
    def _send_application_notification(self, application):
        """Envoie une notification de candidature"""
        try:
            subject = f"Nouvelle candidature - {application.offer.title}"
            message = f"""
            Une nouvelle candidature a été reçue pour l'offre "{application.offer.title}".
            
            Étudiant: {application.student.get_full_name()}
            Email: {application.student.email}
            
            Vous pouvez consulter la candidature dans votre espace de gestion.
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[application.offer.company.contact_email],
                fail_silently=True
            )
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de notification: {e}")


class InternshipViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour les stages (lecture seule pour les étudiants)
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = InternshipFilter
    ordering = ['-start_date']
    
    def get_queryset(self):
        return Internship.objects.filter(
            student=self.request.user
        ).select_related('company', 'academic_supervisor')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return InternshipListSerializer
        return InternshipSerializer
    
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """
        Retourne les documents du stage
        """
        internship = self.get_object()
        
        documents = {
            'internship_agreement': internship.internship_agreement.url if internship.internship_agreement else None,
            'final_report': internship.final_report.url if internship.final_report else None,
            'company_evaluation': internship.company_evaluation.url if internship.company_evaluation else None
        }
        
        return Response(documents)
    
    @action(detail=True, methods=['post'])
    def upload_report(self, request, pk=None):
        """
        Upload du rapport de stage
        """
        internship = self.get_object()
        
        if 'report_file' not in request.FILES:
            return Response({
                'error': 'Fichier de rapport requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        internship.final_report = request.FILES['report_file']
        internship.save()
        
        return Response({
            'message': 'Rapport uploadé avec succès',
            'file_url': internship.final_report.url
        })
    
    @action(detail=True, methods=['post'])
    def rate_company(self, request, pk=None):
        """
        Noter l'entreprise
        """
        internship = self.get_object()
        
        if internship.status != 'completed':
            return Response({
                'error': 'Le stage doit être terminé pour être évalué'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        rating = request.data.get('rating')
        if not rating or not (1 <= int(rating) <= 5):
            return Response({
                'error': 'Note invalide (1-5)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        internship.student_rating = int(rating)
        internship.save()
        
        # Mettre à jour les statistiques de l'entreprise
        internship.company.update_statistics()
        
        return Response({
            'message': 'Note enregistrée',
            'rating': internship.student_rating
        })


class InternshipVisitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour les visites de stage
    """
    serializer_class = InternshipVisitSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['visit_type', 'status', 'follow_up_required']
    ordering = ['-scheduled_date']
    
    def get_queryset(self):
        # Étudiant : ses propres visites
        # Enseignant : visites qu'il effectue
        if hasattr(self.request.user, 'profile') and self.request.user.profile.role == 'teacher':
            return InternshipVisit.objects.filter(visitor=self.request.user)
        else:
            return InternshipVisit.objects.filter(
                internship__student=self.request.user
            )


class InternshipEvaluationViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les évaluations de stage
    """
    serializer_class = InternshipEvaluationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['evaluator_type', 'overall_rating']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return InternshipEvaluation.objects.filter(
            Q(internship__student=self.request.user) |
            Q(evaluator=self.request.user)
        )
    
    def perform_create(self, serializer):
        serializer.save(evaluator=self.request.user)


class InternshipStatsViewSet(viewsets.ViewSet):
    """
    ViewSet pour les statistiques de stage
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        Tableau de bord des stages pour l'étudiant
        """
        user_internships = Internship.objects.filter(student=request.user)
        user_applications = InternshipApplication.objects.filter(student=request.user)
        
        stats = {
            'total_applications': user_applications.count(),
            'pending_applications': user_applications.filter(
                status__in=['submitted', 'under_review']
            ).count(),
            'accepted_applications': user_applications.filter(
                status='accepted'
            ).count(),
            'total_internships': user_internships.count(),
            'ongoing_internships': user_internships.filter(status='ongoing').count(),
            'completed_internships': user_internships.filter(status='completed').count(),
            'upcoming_internships': user_internships.filter(status='upcoming').count(),
            'current_internship': None
        }
        
        # Stage en cours
        current_internship = user_internships.filter(status='ongoing').first()
        if current_internship:
            stats['current_internship'] = {
                'id': str(current_internship.id),
                'company': current_internship.company.name,
                'start_date': current_internship.start_date,
                'end_date': current_internship.end_date,
                'progress': current_internship.progress_percentage
            }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def global_stats(self, request):
        """
        Statistiques globales (pour les administrateurs)
        """
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Statistiques générales
        total_companies = Company.objects.filter(is_active=True).count()
        total_offers = InternshipOffer.objects.filter(status='published').count()
        total_applications = InternshipApplication.objects.count()
        total_internships = Internship.objects.count()
        
        # Taux de succès
        success_rate = 0
        if total_applications > 0:
            accepted_applications = InternshipApplication.objects.filter(
                status='accepted'
            ).count()
            success_rate = (accepted_applications / total_applications) * 100
        
        # Top entreprises
        top_companies = Company.objects.filter(
            is_active=True
        ).annotate(
            internship_count=Count('internships')
        ).order_by('-internship_count')[:5]
        
        # Répartition par secteur
        sector_stats = Company.objects.filter(
            is_active=True
        ).values('sector').annotate(
            count=Count('id')
        ).order_by('-count')
        
        stats = {
            'total_companies': total_companies,
            'total_offers': total_offers,
            'total_applications': total_applications,
            'total_internships': total_internships,
            'success_rate': round(success_rate, 2),
            'top_companies': [
                {
                    'name': company.name,
                    'internship_count': company.internship_count,
                    'average_rating': company.average_rating
                }
                for company in top_companies
            ],
            'sector_distribution': {
                item['sector']: item['count']
                for item in sector_stats
            }
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['post'])
    def report(self, request):
        """
        Génère un rapport personnalisé
        """
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        if not start_date or not end_date:
            return Response({
                'error': 'Dates de début et fin requises'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'error': 'Format de date invalide (YYYY-MM-DD)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Filtrer les données par période
        offers = InternshipOffer.objects.filter(
            created_at__date__range=[start_date, end_date]
        )
        applications = InternshipApplication.objects.filter(
            created_at__date__range=[start_date, end_date]
        )
        internships = Internship.objects.filter(
            start_date__range=[start_date, end_date]
        )
        
        report_data = {
            'period_start': start_date,
            'period_end': end_date,
            'total_offers': offers.count(),
            'total_applications': applications.count(),
            'total_internships': internships.count(),
            'success_rate': (
                applications.filter(status='accepted').count() / 
                applications.count() * 100
                if applications.count() > 0 else 0
            ),
            'average_duration': internships.aggregate(
                avg_duration=Avg(F('end_date') - F('start_date'))
            )['avg_duration'] or 0,
            'top_companies': list(internships.values(
                'company__name'
            ).annotate(
                count=Count('id')
            ).order_by('-count')[:5]),
            'sector_distribution': dict(internships.values(
                'company__sector'
            ).annotate(
                count=Count('id')
            ).values_list('company__sector', 'count')),
            'monthly_trends': {}  # À implémenter selon les besoins
        }
        
        serializer = InternshipReportSerializer(report_data)
        return Response(serializer.data)