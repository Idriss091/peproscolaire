"""
Tâches asynchrones pour la messagerie
"""
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.conf import settings
from datetime import datetime, timedelta
import logging

from .models import (
    Message, MessageRecipient, EmailForwarding,
    NotificationPreference, MessagePriority
)

logger = logging.getLogger(__name__)


@shared_task
def send_message_notifications(message_id):
    """
    Envoyer les notifications pour un nouveau message
    """
    try:
        message = Message.objects.get(id=message_id)
    except Message.DoesNotExist:
        logger.error(f"Message {message_id} introuvable")
        return
    
    notifications_sent = 0
    
    for recipient in message.recipients.all():
        # Vérifier les préférences
        prefs, created = NotificationPreference.objects.get_or_create(
            user=recipient.recipient
        )
        
        # Notification push
        if prefs.should_send_notification(message, 'push'):
            send_push_notification(recipient.recipient, message)
            notifications_sent += 1
        
        # Notification email
        if prefs.should_send_notification(message, 'email'):
            if prefs.email_frequency == 'instant':
                send_email_notification(recipient.recipient, message)
                notifications_sent += 1
            else:
                # Ajouter à la file d'attente pour envoi groupé
                queue_email_notification(recipient.recipient, message)
        
        # Marquer comme notifié
        recipient.notification_sent = True
        recipient.save()
    
    return f"{notifications_sent} notifications envoyées pour le message {message_id}"


def send_push_notification(user, message):
    """Envoyer une notification push"""
    # TODO: Implémenter avec Firebase ou autre service
    logger.info(f"Notification push pour {user.email}: {message.subject}")


def send_email_notification(user, message):
    """Envoyer une notification par email"""
    context = {
        'user': user,
        'message': message,
        'sender': message.sender,
        'site_url': settings.FRONTEND_URL
    }
    
    html_message = render_to_string(
        'emails/new_message.html',
        context
    )
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=f"Nouveau message: {message.subject}",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        
        # Marquer comme envoyé
        MessageRecipient.objects.filter(
            message=message,
            recipient=user
        ).update(email_sent=True)
        
    except Exception as e:
        logger.error(f"Erreur envoi email à {user.email}: {str(e)}")


def queue_email_notification(user, message):
    """Ajouter à la file pour envoi groupé"""
    # TODO: Implémenter avec Redis ou base de données
    pass


@shared_task
def send_message_by_email(message_id):
    """
    Transférer un message par email
    """
    try:
        message = Message.objects.get(id=message_id)
    except Message.DoesNotExist:
        return
    
    if not message.forward_to_email:
        return
    
    forwarded_count = 0
    
    for recipient in message.recipients.all():
        # Vérifier la configuration de redirection
        try:
            forwarding = recipient.recipient.email_forwarding
            if forwarding.should_forward(message):
                # Envoyer l'email
                context = {
                    'message': message,
                    'recipient': recipient.recipient
                }
                
                html_message = render_to_string(
                    'emails/forwarded_message.html',
                    context
                )
                plain_message = strip_tags(html_message)
                
                send_mail(
                    subject=f"[PeproScolaire] {message.subject}",
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[forwarding.forward_email],
                    html_message=html_message,
                    fail_silently=False
                )
                
                # Mettre à jour les stats
                forwarding.last_forwarded = timezone.now()
                forwarding.forward_count += 1
                forwarding.save()
                
                forwarded_count += 1
                
        except EmailForwarding.DoesNotExist:
            pass
        except Exception as e:
            logger.error(f"Erreur forwarding pour {recipient.recipient.email}: {str(e)}")
    
    return f"{forwarded_count} emails transférés"


@shared_task
def send_read_receipt(recipient_id):
    """
    Envoyer un accusé de lecture
    """
    try:
        recipient = MessageRecipient.objects.get(id=recipient_id)
    except MessageRecipient.DoesNotExist:
        return
    
    message = recipient.message
    
    # Créer le message d'accusé
    receipt = Message.objects.create(
        sender=recipient.recipient,
        subject=f"Lu: {message.subject}",
        body=f"Votre message '{message.subject}' a été lu le {recipient.read_at:%d/%m/%Y à %H:%M}.",
        priority=MessagePriority.LOW,
        allow_reply=False
    )
    
    # Ajouter l'expéditeur original comme destinataire
    MessageRecipient.objects.create(
        message=receipt,
        recipient=message.sender
    )
    
    # Envoyer
    receipt.send()
    
    return f"Accusé de lecture envoyé pour {message.subject}"


@shared_task
def process_email_batch():
    """
    Traiter les envois d'emails groupés
    """
    # Récupérer les préférences avec envoi groupé
    for freq in ['hourly', 'daily', 'weekly']:
        process_frequency_batch(freq)


def process_frequency_batch(frequency):
    """Traiter une fréquence spécifique"""
    now = timezone.now()
    
    # Déterminer la période
    if frequency == 'hourly':
        since = now - timedelta(hours=1)
    elif frequency == 'daily':
        since = now - timedelta(days=1)
    else:  # weekly
        since = now - timedelta(days=7)
    
    # Récupérer les utilisateurs avec cette fréquence
    users = NotificationPreference.objects.filter(
        email_enabled=True,
        email_frequency=frequency
    ).values_list('user', flat=True)
    
    for user_id in users:
        # Récupérer les messages non notifiés
        messages = MessageRecipient.objects.filter(
            recipient_id=user_id,
            email_sent=False,
            message__sent_at__gte=since
        ).select_related('message', 'message__sender')
        
        if messages.exists():
            send_batch_email(user_id, messages)


def send_batch_email(user_id, message_recipients):
    """Envoyer un email groupé"""
    from apps.authentication.models import User
    
    user = User.objects.get(id=user_id)
    
    context = {
        'user': user,
        'messages': [mr.message for mr in message_recipients],
        'count': message_recipients.count(),
        'site_url': settings.FRONTEND_URL
    }
    
    html_message = render_to_string(
        'emails/message_digest.html',
        context
    )
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=f"[PeproScolaire] {message_recipients.count()} nouveaux messages",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        
        # Marquer comme envoyés
        message_recipients.update(email_sent=True)
        
    except Exception as e:
        logger.error(f"Erreur envoi batch à {user.email}: {str(e)}")


@shared_task
def send_daily_summary():
    """
    Envoyer le résumé quotidien
    """
    # Récupérer les utilisateurs avec résumé activé
    prefs = NotificationPreference.objects.filter(
        daily_summary=True
    )
    
    summaries_sent = 0
    
    for pref in prefs:
        # Vérifier l'heure
        now = timezone.now().time()
        if now.hour == pref.summary_time.hour:
            # Générer et envoyer le résumé
            summary = generate_daily_summary(pref.user)
            if summary:
                send_summary_email(pref.user, summary)
                summaries_sent += 1
    
    return f"{summaries_sent} résumés envoyés"


def generate_daily_summary(user):
    """Générer le résumé quotidien pour un utilisateur"""
    today = timezone.now().date()
    
    # Messages reçus aujourd'hui
    received_today = MessageRecipient.objects.filter(
        recipient=user,
        message__sent_at__date=today
    ).count()
    
    # Messages non lus
    unread = MessageRecipient.objects.filter(
        recipient=user,
        is_read=False
    ).count()
    
    # Messages urgents non lus
    urgent_unread = MessageRecipient.objects.filter(
        recipient=user,
        is_read=False,
        message__priority=MessagePriority.URGENT
    ).select_related('message', 'message__sender')[:5]
    
    if received_today == 0 and unread == 0:
        return None
    
    return {
        'received_today': received_today,
        'unread_total': unread,
        'urgent_messages': urgent_unread
    }


def send_summary_email(user, summary):
    """Envoyer l'email de résumé"""
    context = {
        'user': user,
        'summary': summary,
        'site_url': settings.FRONTEND_URL
    }
    
    html_message = render_to_string(
        'emails/daily_summary.html',
        context
    )
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=f"[PeproScolaire] Votre résumé du {timezone.now():%d/%m/%Y}",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
    except Exception as e:
        logger.error(f"Erreur envoi résumé à {user.email}: {str(e)}")


@shared_task
def cleanup_old_messages():
    """
    Nettoyer les anciens messages
    """
    # Messages dans la corbeille depuis plus de 30 jours
    threshold = timezone.now() - timedelta(days=30)
    
    old_trash = MessageRecipient.objects.filter(
        folder='trash',
        modified_at__lt=threshold
    )
    
    deleted_count = old_trash.delete()[0]
    
    # Supprimer les messages orphelins (sans destinataires)
    orphan_messages = Message.objects.filter(
        recipients__isnull=True,
        sent_at__isnull=False,
        sent_at__lt=threshold
    )
    
    orphan_count = orphan_messages.delete()[0]
    
    return f"{deleted_count} messages de corbeille et {orphan_count} messages orphelins supprimés"


@shared_task
def detect_spam_patterns():
    """
    Détecter les patterns de spam
    """
    # Analyser les messages des dernières 24h
    since = timezone.now() - timedelta(days=1)
    
    # Détecter les expéditeurs qui envoient trop
    from django.db.models import Count
    
    suspicious_senders = Message.objects.filter(
        sent_at__gte=since
    ).values('sender').annotate(
        count=Count('id')
    ).filter(count__gt=50)  # Plus de 50 messages en 24h
    
    for sender_data in suspicious_senders:
        logger.warning(
            f"Activité suspecte: User {sender_data['sender']} a envoyé "
            f"{sender_data['count']} messages en 24h"
        )
        
        # TODO: Implémenter des actions (limitation, notification admin)
    
    return f"{len(suspicious_senders)} expéditeurs suspects détectés"