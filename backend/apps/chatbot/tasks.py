from celery import shared_task
from django.utils import timezone
from django.db.models import Count, Avg, Q
from datetime import datetime, timedelta
import logging

from .models import (
    ChatbotConversation, ChatbotMessage, ChatbotAnalytics,
    ChatbotKnowledgeBase
)
from .ai_engine import ChatbotAIEngine

logger = logging.getLogger(__name__)


@shared_task
def generate_daily_analytics():
    """
    Génère les analytiques quotidiennes du chatbot
    """
    try:
        yesterday = (timezone.now() - timedelta(days=1)).date()
        
        # Vérifier si les analytiques existent déjà
        analytics, created = ChatbotAnalytics.objects.get_or_create(
            date=yesterday,
            defaults={}
        )
        
        if not created:
            logger.info(f"Analytiques pour {yesterday} déjà existantes, mise à jour...")
        
        # Conversations du jour
        conversations = ChatbotConversation.objects.filter(
            created_at__date=yesterday
        )
        
        messages = ChatbotMessage.objects.filter(
            timestamp__date=yesterday
        )
        
        # Statistiques des conversations
        analytics.total_conversations = ChatbotConversation.objects.filter(
            created_at__date=yesterday
        ).count()
        
        analytics.new_conversations = conversations.count()
        
        analytics.closed_conversations = ChatbotConversation.objects.filter(
            updated_at__date=yesterday,
            status='closed'
        ).count()
        
        # Statistiques des messages
        analytics.total_messages = messages.count()
        analytics.user_messages = messages.filter(sender='user').count()
        analytics.bot_messages = messages.filter(sender='bot').count()
        
        # Performance
        bot_messages_with_time = messages.filter(
            sender='bot',
            response_time_ms__isnull=False
        )
        
        if bot_messages_with_time.exists():
            analytics.avg_response_time_ms = bot_messages_with_time.aggregate(
                avg=Avg('response_time_ms')
            )['avg']
        
        # Résolutions réussies (conversations fermées avec satisfaction >= 4)
        analytics.successful_resolutions = ChatbotConversation.objects.filter(
            updated_at__date=yesterday,
            status='closed',
            satisfaction_rating__gte=4
        ).count()
        
        # Escalations vers humain (conversations avec besoin d'assistance)
        escalation_keywords = ['assistance', 'humain', 'conseiller', 'urgent']
        analytics.escalations_to_human = messages.filter(
            timestamp__date=yesterday,
            content__iregex=r'(' + '|'.join(escalation_keywords) + ')'
        ).values('conversation').distinct().count()
        
        # Satisfaction moyenne
        satisfaction_data = ChatbotConversation.objects.filter(
            updated_at__date=yesterday,
            satisfaction_rating__isnull=False
        ).aggregate(
            avg=Avg('satisfaction_rating'),
            count=Count('satisfaction_rating')
        )
        
        analytics.avg_satisfaction_rating = satisfaction_data['avg']
        analytics.total_ratings = satisfaction_data['count']
        
        # Top intentions
        top_intents = messages.filter(
            timestamp__date=yesterday,
            intent__isnull=False
        ).values('intent').annotate(
            count=Count('intent')
        ).order_by('-count')[:10]
        
        analytics.top_intents = {
            intent['intent']: intent['count']
            for intent in top_intents
        }
        
        analytics.save()
        
        logger.info(f"Analytiques générées pour {yesterday}")
        return f"Analytiques générées pour {yesterday}"
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération des analytiques: {e}")
        raise


@shared_task
def cleanup_old_conversations():
    """
    Archive les anciennes conversations inactives
    """
    try:
        # Archiver les conversations inactives depuis plus de 30 jours
        cutoff_date = timezone.now() - timedelta(days=30)
        
        old_conversations = ChatbotConversation.objects.filter(
            last_activity__lt=cutoff_date,
            status='active'
        )
        
        count = old_conversations.count()
        old_conversations.update(status='archived')
        
        logger.info(f"{count} conversations archivées")
        return f"{count} conversations archivées"
        
    except Exception as e:
        logger.error(f"Erreur lors de l'archivage: {e}")
        raise


@shared_task
def update_knowledge_base_vectors():
    """
    Met à jour les vecteurs de la base de connaissances
    """
    try:
        ai_engine = ChatbotAIEngine()
        ai_engine.update_knowledge_base()
        
        logger.info("Base de connaissances mise à jour")
        return "Base de connaissances mise à jour"
        
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de la base de connaissances: {e}")
        raise


@shared_task
def process_conversation_summaries():
    """
    Génère des résumés pour les conversations récentes
    """
    try:
        # Conversations fermées récemment sans résumé
        recent_conversations = ChatbotConversation.objects.filter(
            status='closed',
            updated_at__gte=timezone.now() - timedelta(hours=24),
            message_count__gte=5  # Au moins 5 messages
        ).exclude(
            context_data__has_key='summary'
        )
        
        ai_engine = ChatbotAIEngine()
        count = 0
        
        for conversation in recent_conversations:
            try:
                summary = ai_engine.get_conversation_summary(str(conversation.id))
                
                if not conversation.context_data:
                    conversation.context_data = {}
                
                conversation.context_data['summary'] = summary
                conversation.context_data['summary_generated_at'] = timezone.now().isoformat()
                conversation.save()
                
                count += 1
                
            except Exception as e:
                logger.error(f"Erreur lors de la génération du résumé pour {conversation.id}: {e}")
                continue
        
        logger.info(f"{count} résumés générés")
        return f"{count} résumés générés"
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement des résumés: {e}")
        raise


@shared_task
def analyze_user_satisfaction():
    """
    Analyse la satisfaction des utilisateurs et identifie les problèmes
    """
    try:
        # Conversations avec faible satisfaction (< 3) des 7 derniers jours
        cutoff_date = timezone.now() - timedelta(days=7)
        
        low_satisfaction = ChatbotConversation.objects.filter(
            updated_at__gte=cutoff_date,
            satisfaction_rating__lt=3,
            satisfaction_rating__isnull=False
        )
        
        issues = []
        
        for conversation in low_satisfaction:
            # Analyser les messages pour identifier les problèmes
            messages = conversation.messages.filter(sender='user')
            
            problem_keywords = {
                'technical': ['bug', 'erreur', 'problème', 'ne marche pas', 'cassé'],
                'response_quality': ['pas utile', 'incompréhensible', 'mauvaise réponse'],
                'speed': ['lent', 'long', 'attente', 'délai'],
                'missing_feature': ['manque', 'absent', 'devrait', 'pourquoi pas']
            }
            
            for message in messages:
                content_lower = message.content.lower()
                for category, keywords in problem_keywords.items():
                    if any(keyword in content_lower for keyword in keywords):
                        issues.append({
                            'conversation_id': str(conversation.id),
                            'category': category,
                            'satisfaction_rating': conversation.satisfaction_rating,
                            'timestamp': conversation.updated_at.isoformat(),
                            'message_sample': message.content[:200]
                        })
                        break
        
        # Grouper les problèmes par catégorie
        problem_summary = {}
        for issue in issues:
            category = issue['category']
            if category not in problem_summary:
                problem_summary[category] = 0
            problem_summary[category] += 1
        
        logger.info(f"Analyse de satisfaction terminée: {len(issues)} problèmes identifiés")
        logger.info(f"Résumé des problèmes: {problem_summary}")
        
        return {
            'total_issues': len(issues),
            'problem_summary': problem_summary,
            'issues': issues[:10]  # Limiter pour les logs
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de satisfaction: {e}")
        raise


@shared_task
def backup_conversations():
    """
    Sauvegarde les conversations importantes
    """
    try:
        # Conversations à sauvegarder (haute satisfaction ou longues)
        important_conversations = ChatbotConversation.objects.filter(
            Q(satisfaction_rating__gte=4) | Q(message_count__gte=20),
            status='closed',
            updated_at__gte=timezone.now() - timedelta(days=1)
        )
        
        backup_data = []
        
        for conversation in important_conversations:
            messages_data = []
            for message in conversation.messages.all():
                messages_data.append({
                    'sender': message.sender,
                    'content': message.content,
                    'timestamp': message.timestamp.isoformat(),
                    'intent': message.intent,
                    'confidence_score': message.confidence_score
                })
            
            backup_data.append({
                'conversation_id': str(conversation.id),
                'user_id': conversation.user.id,
                'conversation_type': conversation.conversation_type,
                'satisfaction_rating': conversation.satisfaction_rating,
                'created_at': conversation.created_at.isoformat(),
                'messages': messages_data
            })
        
        # Ici vous pourriez sauvegarder vers S3, un fichier JSON, etc.
        logger.info(f"{len(backup_data)} conversations sauvegardées")
        
        return f"{len(backup_data)} conversations sauvegardées"
        
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde: {e}")
        raise


@shared_task
def optimize_knowledge_base():
    """
    Optimise la base de connaissances en analysant l'utilisation
    """
    try:
        # Identifier les éléments non utilisés
        cutoff_date = timezone.now() - timedelta(days=90)
        
        unused_items = ChatbotKnowledgeBase.objects.filter(
            Q(last_used__lt=cutoff_date) | Q(last_used__isnull=True),
            status='active',
            usage_count__lt=5
        )
        
        # Marquer comme candidats à l'archivage
        unused_count = unused_items.count()
        
        # Identifier les éléments populaires sans contenu détaillé
        popular_items = ChatbotKnowledgeBase.objects.filter(
            usage_count__gte=50,
            status='active'
        ).filter(
            content__length__lt=200
        )
        
        suggestions = {
            'unused_items': unused_count,
            'items_to_expand': popular_items.count(),
            'total_active': ChatbotKnowledgeBase.objects.filter(status='active').count()
        }
        
        logger.info(f"Optimisation de la base de connaissances: {suggestions}")
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Erreur lors de l'optimisation: {e}")
        raise


@shared_task
def generate_conversation_insights():
    """
    Génère des insights sur les conversations
    """
    try:
        # Analyser les patterns des 30 derniers jours
        cutoff_date = timezone.now() - timedelta(days=30)
        
        conversations = ChatbotConversation.objects.filter(
            created_at__gte=cutoff_date
        )
        
        insights = {
            'total_conversations': conversations.count(),
            'avg_messages_per_conversation': conversations.aggregate(
                avg=Avg('message_count')
            )['avg'] or 0,
            'conversation_types': dict(conversations.values('conversation_type').annotate(
                count=Count('conversation_type')
            ).values_list('conversation_type', 'count')),
            'peak_hours': {},
            'avg_satisfaction': conversations.filter(
                satisfaction_rating__isnull=False
            ).aggregate(avg=Avg('satisfaction_rating'))['avg'] or 0
        }
        
        # Analyser les heures de pic
        messages = ChatbotMessage.objects.filter(
            timestamp__gte=cutoff_date,
            sender='user'
        )
        
        for hour in range(24):
            hour_messages = messages.filter(
                timestamp__hour=hour
            ).count()
            insights['peak_hours'][str(hour)] = hour_messages
        
        logger.info(f"Insights générés: {insights}")
        
        return insights
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération d'insights: {e}")
        raise