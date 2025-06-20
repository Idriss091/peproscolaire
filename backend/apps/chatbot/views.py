from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Count, Avg
from datetime import datetime, timedelta
import logging

from .models import (
    ChatbotConversation, ChatbotMessage, ChatbotKnowledgeBase,
    ChatbotIntent, ChatbotAnalytics
)
from .serializers import (
    ChatbotConversationSerializer, ChatbotConversationListSerializer,
    ChatbotMessageSerializer, ChatbotMessageCreateSerializer,
    ChatbotKnowledgeBaseSerializer, ChatbotIntentSerializer,
    ChatbotAnalyticsSerializer, ChatbotResponseSerializer,
    ChatbotFeedbackSerializer, ChatbotSearchSerializer
)
from .ai_engine import ChatbotAIEngine
from ..core.permissions import IsStudentOrParentOrTeacher

logger = logging.getLogger(__name__)


class ChatbotConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les conversations du chatbot
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['conversation_type', 'status']
    
    def get_queryset(self):
        return ChatbotConversation.objects.filter(
            user=self.request.user
        ).prefetch_related('messages')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ChatbotConversationListSerializer
        return ChatbotConversationSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """
        Envoie un message dans une conversation
        """
        conversation = self.get_object()
        serializer = ChatbotMessageCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            # Créer le message utilisateur
            user_message = serializer.save(
                conversation=conversation,
                sender='user'
            )
            
            try:
                # Générer la réponse du chatbot
                ai_engine = ChatbotAIEngine()
                response_data = ai_engine.process_message(
                    message=user_message.content,
                    user=request.user,
                    conversation_id=str(conversation.id)
                )
                
                # Créer le message de réponse
                bot_message = ChatbotMessage.objects.create(
                    conversation=conversation,
                    sender='bot',
                    content=response_data['message'],
                    message_type=response_data.get('message_type', 'text'),
                    intent=response_data.get('intent'),
                    confidence_score=response_data.get('confidence_score'),
                    entities=response_data.get('entities', []),
                    response_time_ms=response_data.get('response_time_ms'),
                    tokens_used=response_data.get('tokens_used')
                )
                
                # Mettre à jour le titre de la conversation si nécessaire
                if not conversation.title:
                    conversation.generate_title()
                
                # Sérialiser les réponses
                user_msg_data = ChatbotMessageSerializer(user_message).data
                bot_msg_data = ChatbotMessageSerializer(bot_message).data
                
                return Response({
                    'user_message': user_msg_data,
                    'bot_response': bot_msg_data,
                    'quick_replies': response_data.get('quick_replies', []),
                    'suggestions': response_data.get('suggestions', []),
                    'needs_human': response_data.get('needs_human', False)
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                logger.error(f"Erreur lors de la génération de réponse: {e}")
                return Response({
                    'error': 'Erreur lors de la génération de la réponse',
                    'user_message': ChatbotMessageSerializer(user_message).data
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def close_conversation(self, request, pk=None):
        """
        Ferme une conversation
        """
        conversation = self.get_object()
        conversation.status = 'closed'
        conversation.save()
        
        # Message système de fermeture
        ChatbotMessage.objects.create(
            conversation=conversation,
            sender='system',
            content="Conversation fermée.",
            message_type='action'
        )
        
        return Response({'status': 'conversation closed'})
    
    @action(detail=True, methods=['post'])
    def rate_conversation(self, request, pk=None):
        """
        Évalue une conversation
        """
        conversation = self.get_object()
        serializer = ChatbotFeedbackSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.update(conversation, serializer.validated_data)
            
            # Message de remerciement
            if 'feedback_text' in serializer.validated_data:
                ChatbotMessage.objects.create(
                    conversation=conversation,
                    sender='system',
                    content=f"Merci pour votre évaluation: {serializer.validated_data['satisfaction_rating']}/5",
                    message_type='action'
                )
            
            return Response({'status': 'rating saved'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """
        Génère un résumé de la conversation
        """
        conversation = self.get_object()
        
        try:
            ai_engine = ChatbotAIEngine()
            summary = ai_engine.get_conversation_summary(str(conversation.id))
            
            return Response({
                'conversation_id': str(conversation.id),
                'summary': summary,
                'message_count': conversation.message_count,
                'duration': (conversation.updated_at - conversation.created_at).total_seconds() / 60
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du résumé: {e}")
            return Response({
                'error': 'Erreur lors de la génération du résumé'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatbotMessageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour les messages du chatbot (lecture seule)
    """
    serializer_class = ChatbotMessageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sender', 'message_type', 'intent']
    
    def get_queryset(self):
        return ChatbotMessage.objects.filter(
            conversation__user=self.request.user
        ).select_related('conversation')
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """
        Marque un message comme lu
        """
        message = self.get_object()
        message.is_read = True
        message.save()
        
        return Response({'status': 'message marked as read'})


class ChatbotKnowledgeBaseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour la base de connaissances (lecture seule pour les utilisateurs)
    """
    serializer_class = ChatbotKnowledgeBaseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['knowledge_type', 'category', 'status']
    
    def get_queryset(self):
        return ChatbotKnowledgeBase.objects.filter(status='active')
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """
        Recherche dans la base de connaissances
        """
        serializer = ChatbotSearchSerializer(data=request.data)
        
        if serializer.is_valid():
            query = serializer.validated_data['query']
            knowledge_type = serializer.validated_data.get('knowledge_type')
            category = serializer.validated_data.get('category')
            limit = serializer.validated_data.get('limit', 5)
            
            try:
                ai_engine = ChatbotAIEngine()
                results = ai_engine._search_knowledge_base(query, limit)
                
                # Filtrer par type et catégorie si spécifié
                if knowledge_type:
                    results = [r for r in results if r.get('knowledge_type') == knowledge_type]
                
                if category:
                    results = [r for r in results if r.get('category') == category]
                
                return Response({
                    'query': query,
                    'results': results,
                    'total_found': len(results)
                })
                
            except Exception as e:
                logger.error(f"Erreur lors de la recherche: {e}")
                return Response({
                    'error': 'Erreur lors de la recherche'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatbotAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour les analytiques du chatbot (admin seulement)
    """
    serializer_class = ChatbotAnalyticsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_staff:
            return ChatbotAnalytics.objects.none()
        
        return ChatbotAnalytics.objects.all().order_by('-date')
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        Données pour le tableau de bord analytique
        """
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Statistiques des 30 derniers jours
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
            
            analytics = ChatbotAnalytics.objects.filter(
                date__range=[start_date, end_date]
            )
            
            # Calculs agrégés
            total_conversations = analytics.aggregate(
                total=Count('total_conversations')
            )['total'] or 0
            
            avg_satisfaction = analytics.aggregate(
                avg=Avg('avg_satisfaction_rating')
            )['avg'] or 0
            
            avg_response_time = analytics.aggregate(
                avg=Avg('avg_response_time_ms')
            )['avg'] or 0
            
            # Conversations par jour
            daily_stats = list(analytics.values(
                'date', 'total_conversations', 'new_conversations',
                'total_messages', 'avg_satisfaction_rating'
            ))
            
            # Top intentions
            all_intents = {}
            for day in analytics:
                for intent, count in day.top_intents.items():
                    all_intents[intent] = all_intents.get(intent, 0) + count
            
            top_intents = sorted(
                all_intents.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            return Response({
                'period': {
                    'start_date': start_date,
                    'end_date': end_date
                },
                'summary': {
                    'total_conversations': total_conversations,
                    'avg_satisfaction_rating': round(avg_satisfaction, 2),
                    'avg_response_time_ms': round(avg_response_time, 2)
                },
                'daily_stats': daily_stats,
                'top_intents': top_intents
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du dashboard: {e}")
            return Response({
                'error': 'Erreur lors de la génération des statistiques'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatbotQuickActionsViewSet(viewsets.ViewSet):
    """
    ViewSet pour les actions rapides du chatbot
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def quick_start(self, request):
        """
        Démarre rapidement une conversation selon le contexte
        """
        conversation_type = request.data.get('type', 'general')
        initial_message = request.data.get('message', '')
        
        # Créer une nouvelle conversation
        conversation = ChatbotConversation.objects.create(
            user=request.user,
            conversation_type=conversation_type
        )
        
        if initial_message:
            # Ajouter le message initial
            user_message = ChatbotMessage.objects.create(
                conversation=conversation,
                sender='user',
                content=initial_message
            )
            
            # Générer une réponse
            try:
                ai_engine = ChatbotAIEngine()
                response_data = ai_engine.process_message(
                    message=initial_message,
                    user=request.user,
                    conversation_id=str(conversation.id)
                )
                
                bot_message = ChatbotMessage.objects.create(
                    conversation=conversation,
                    sender='bot',
                    content=response_data['message'],
                    intent=response_data.get('intent'),
                    confidence_score=response_data.get('confidence_score')
                )
                
                conversation.generate_title()
                
                return Response({
                    'conversation_id': str(conversation.id),
                    'messages': [
                        ChatbotMessageSerializer(user_message).data,
                        ChatbotMessageSerializer(bot_message).data
                    ],
                    'quick_replies': response_data.get('quick_replies', [])
                })
                
            except Exception as e:
                logger.error(f"Erreur lors du quick start: {e}")
                return Response({
                    'conversation_id': str(conversation.id),
                    'error': 'Erreur lors de l\'initialisation'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'conversation_id': str(conversation.id),
            'status': 'conversation created'
        })
    
    @action(detail=False, methods=['get'])
    def suggestions(self, request):
        """
        Retourne des suggestions de démarrage
        """
        suggestions = [
            {
                'title': 'Voir mes notes',
                'description': 'Consulter vos dernières évaluations',
                'action': 'view_grades',
                'type': 'academic'
            },
            {
                'title': 'Planning de la semaine',
                'description': 'Votre emploi du temps de la semaine',
                'action': 'view_schedule',
                'type': 'academic'
            },
            {
                'title': 'Devoirs à rendre',
                'description': 'Liste des devoirs et projets à rendre',
                'action': 'view_homework',
                'type': 'academic'
            },
            {
                'title': 'Justifier une absence',
                'description': 'Signaler et justifier une absence',
                'action': 'justify_absence',
                'type': 'administrative'
            },
            {
                'title': 'Problème technique',
                'description': 'Signaler un problème avec la plateforme',
                'action': 'report_issue',
                'type': 'support'
            },
            {
                'title': 'Orientation scolaire',
                'description': 'Conseils d\'orientation et de carrière',
                'action': 'orientation_help',
                'type': 'orientation'
            }
        ]
        
        return Response({
            'suggestions': suggestions
        })
    
    @action(detail=False, methods=['post'])
    def handle_action(self, request):
        """
        Gère les actions rapides prédéfinies
        """
        action = request.data.get('action')
        payload = request.data.get('payload', {})
        
        action_handlers = {
            'view_grades': self._handle_view_grades,
            'view_schedule': self._handle_view_schedule,
            'view_homework': self._handle_view_homework,
            'justify_absence': self._handle_justify_absence,
            'report_issue': self._handle_report_issue,
            'orientation_help': self._handle_orientation_help,
            'contact_support': self._handle_contact_support
        }
        
        handler = action_handlers.get(action)
        if handler:
            return handler(request, payload)
        
        return Response({
            'error': f'Action inconnue: {action}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def _handle_view_grades(self, request, payload):
        """Gère l'action 'voir mes notes'"""
        # Rediriger vers l'endpoint des notes avec un message explicatif
        return Response({
            'message': 'Voici vos dernières notes. Vous pouvez également consulter votre bulletin complet.',
            'action_type': 'redirect',
            'redirect_url': '/api/v1/grades/',
            'quick_replies': [
                {'text': 'Voir le bulletin', 'action': 'view_report_card'},
                {'text': 'Graphique des notes', 'action': 'view_grade_chart'}
            ]
        })
    
    def _handle_view_schedule(self, request, payload):
        """Gère l'action 'voir mon planning'"""
        return Response({
            'message': 'Voici votre emploi du temps de la semaine.',
            'action_type': 'redirect',
            'redirect_url': '/api/v1/timetable/',
            'quick_replies': [
                {'text': 'Semaine suivante', 'action': 'next_week_schedule'},
                {'text': 'Exporter en PDF', 'action': 'export_schedule'}
            ]
        })
    
    def _handle_view_homework(self, request, payload):
        """Gère l'action 'voir mes devoirs'"""
        return Response({
            'message': 'Voici vos devoirs à rendre et projets en cours.',
            'action_type': 'redirect',
            'redirect_url': '/api/v1/homework/',
            'quick_replies': [
                {'text': 'Marquer comme fait', 'action': 'mark_homework_done'},
                {'text': 'Aide aux devoirs', 'action': 'homework_help'}
            ]
        })
    
    def _handle_justify_absence(self, request, payload):
        """Gère l'action 'justifier une absence'"""
        return Response({
            'message': 'Pour justifier une absence, vous pouvez utiliser le formulaire de justification.',
            'action_type': 'form',
            'form_fields': [
                {'name': 'date', 'type': 'date', 'label': 'Date d\'absence'},
                {'name': 'reason', 'type': 'select', 'label': 'Motif', 'options': ['Maladie', 'Rendez-vous médical', 'Autre']},
                {'name': 'justification', 'type': 'file', 'label': 'Justificatif'}
            ]
        })
    
    def _handle_report_issue(self, request, payload):
        """Gère l'action 'signaler un problème'"""
        return Response({
            'message': 'Décrivez votre problème technique et nous vous aiderons à le résoudre.',
            'action_type': 'form',
            'form_fields': [
                {'name': 'issue_type', 'type': 'select', 'label': 'Type de problème', 'options': ['Connexion', 'Performance', 'Bug', 'Autre']},
                {'name': 'description', 'type': 'textarea', 'label': 'Description du problème'},
                {'name': 'screenshot', 'type': 'file', 'label': 'Capture d\'écran (optionnel)'}
            ],
            'quick_replies': [
                {'text': 'Problème urgent', 'action': 'urgent_support'},
                {'text': 'FAQ technique', 'action': 'view_tech_faq'}
            ]
        })
    
    def _handle_orientation_help(self, request, payload):
        """Gère l'action 'aide à l'orientation'"""
        return Response({
            'message': 'Je peux vous aider avec vos questions d\'orientation. Dans quel domaine souhaitez-vous des conseils ?',
            'quick_replies': [
                {'text': 'Choix de filière', 'action': 'career_path_help'},
                {'text': 'Études supérieures', 'action': 'higher_education_help'},
                {'text': 'Métiers', 'action': 'job_exploration'},
                {'text': 'Parler à un conseiller', 'action': 'contact_counselor'}
            ]
        })
    
    def _handle_contact_support(self, request, payload):
        """Gère l'action 'contacter le support'"""
        return Response({
            'message': 'Votre demande a été transmise au support. Un conseiller vous contactera dans les plus brefs délais.',
            'action_type': 'ticket_created',
            'ticket_id': f"SUPPORT-{timezone.now().strftime('%Y%m%d%H%M%S')}",
            'estimated_response_time': '2-4 heures'
        })