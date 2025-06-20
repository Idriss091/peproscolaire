from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxLengthValidator
from django.utils import timezone
import uuid
import json

User = get_user_model()

class ChatbotConversation(models.Model):
    """
    Modèle pour les conversations avec le chatbot IA
    """
    CONVERSATION_TYPES = [
        ('support', 'Support technique'),
        ('academic', 'Aide académique'),
        ('administrative', 'Questions administratives'),
        ('orientation', 'Orientation scolaire'),
        ('general', 'Questions générales'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Fermée'),
        ('archived', 'Archivée'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chatbot_conversations')
    title = models.CharField(max_length=200, blank=True)
    conversation_type = models.CharField(max_length=20, choices=CONVERSATION_TYPES, default='general')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(default=timezone.now)
    
    # Statistiques
    message_count = models.PositiveIntegerField(default=0)
    satisfaction_rating = models.IntegerField(null=True, blank=True, help_text="Note de 1 à 5")
    
    # Contexte de la conversation
    context_data = models.JSONField(default=dict, blank=True, help_text="Données contextuelles pour l'IA")
    
    class Meta:
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-last_activity']),
            models.Index(fields=['conversation_type']),
        ]
        
    def __str__(self):
        return f"Conversation {self.user.username} - {self.get_conversation_type_display()}"
    
    def update_activity(self):
        """Met à jour la dernière activité et incrémente le compteur de messages"""
        self.last_activity = timezone.now()
        self.message_count += 1
        self.save(update_fields=['last_activity', 'message_count'])
    
    def generate_title(self):
        """Génère automatiquement un titre basé sur les premiers messages"""
        first_messages = self.messages.filter(sender='user')[:2]
        if first_messages:
            content = ' '.join([msg.content[:100] for msg in first_messages])
            self.title = content[:100] + ('...' if len(content) > 100 else '')
            self.save(update_fields=['title'])


class ChatbotMessage(models.Model):
    """
    Modèle pour les messages individuels dans une conversation
    """
    MESSAGE_TYPES = [
        ('text', 'Texte'),
        ('quick_reply', 'Réponse rapide'),
        ('attachment', 'Pièce jointe'),
        ('action', 'Action système'),
    ]
    
    SENDER_TYPES = [
        ('user', 'Utilisateur'),
        ('bot', 'Chatbot'),
        ('system', 'Système'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(ChatbotConversation, on_delete=models.CASCADE, related_name='messages')
    
    # Contenu du message
    sender = models.CharField(max_length=10, choices=SENDER_TYPES)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    content = models.TextField(validators=[MaxLengthValidator(4000)])
    
    # Métadonnées
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    # Données IA
    intent = models.CharField(max_length=100, blank=True, help_text="Intention détectée par l'IA")
    confidence_score = models.FloatField(null=True, blank=True, help_text="Score de confiance de l'IA")
    entities = models.JSONField(default=list, blank=True, help_text="Entités extraites du message")
    
    # Réponse du chatbot
    response_time_ms = models.PositiveIntegerField(null=True, blank=True)
    tokens_used = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['conversation', 'timestamp']),
            models.Index(fields=['sender', 'timestamp']),
            models.Index(fields=['intent']),
        ]
        
    def __str__(self):
        return f"{self.get_sender_display()} - {self.content[:50]}..."
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Mettre à jour l'activité de la conversation
        if self.sender == 'user':
            self.conversation.update_activity()


class ChatbotKnowledgeBase(models.Model):
    """
    Base de connaissances pour le chatbot
    """
    KNOWLEDGE_TYPES = [
        ('faq', 'FAQ'),
        ('procedure', 'Procédure'),
        ('policy', 'Politique'),
        ('contact', 'Contact'),
        ('emergency', 'Urgence'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('draft', 'Brouillon'),
        ('archived', 'Archivé'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Contenu
    title = models.CharField(max_length=200)
    content = models.TextField()
    knowledge_type = models.CharField(max_length=20, choices=KNOWLEDGE_TYPES, default='faq')
    
    # Catégorisation
    category = models.CharField(max_length=100, blank=True)
    tags = models.JSONField(default=list, blank=True)
    
    # Recherche et matching
    keywords = models.JSONField(default=list, blank=True, help_text="Mots-clés pour la recherche")
    similarity_threshold = models.FloatField(default=0.7, help_text="Seuil de similarité pour la correspondance")
    
    # Métadonnées
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Statistiques d'utilisation
    usage_count = models.PositiveIntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'knowledge_type']),
            models.Index(fields=['category']),
            models.Index(fields=['-usage_count']),
        ]
        
    def __str__(self):
        return f"{self.title} ({self.get_knowledge_type_display()})"
    
    def increment_usage(self):
        """Incrémente le compteur d'utilisation"""
        self.usage_count += 1
        self.last_used = timezone.now()
        self.save(update_fields=['usage_count', 'last_used'])


class ChatbotIntent(models.Model):
    """
    Intentions prédéfinies pour le chatbot
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    # Patterns de reconnaissance
    patterns = models.JSONField(default=list, help_text="Patterns pour reconnaître cette intention")
    responses = models.JSONField(default=list, help_text="Réponses possibles pour cette intention")
    
    # Configuration
    requires_authentication = models.BooleanField(default=False)
    requires_admin = models.BooleanField(default=False)
    priority = models.IntegerField(default=0, help_text="Priorité pour la résolution des conflits")
    
    # Actions associées
    action_type = models.CharField(max_length=50, blank=True, help_text="Type d'action à exécuter")
    action_parameters = models.JSONField(default=dict, blank=True)
    
    # Métadonnées
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', 'name']
        
    def __str__(self):
        return self.name


class ChatbotAnalytics(models.Model):
    """
    Analytiques des conversations du chatbot
    """
    date = models.DateField()
    
    # Statistiques des conversations
    total_conversations = models.PositiveIntegerField(default=0)
    new_conversations = models.PositiveIntegerField(default=0)
    closed_conversations = models.PositiveIntegerField(default=0)
    
    # Statistiques des messages
    total_messages = models.PositiveIntegerField(default=0)
    user_messages = models.PositiveIntegerField(default=0)
    bot_messages = models.PositiveIntegerField(default=0)
    
    # Performance
    avg_response_time_ms = models.FloatField(null=True, blank=True)
    successful_resolutions = models.PositiveIntegerField(default=0)
    escalations_to_human = models.PositiveIntegerField(default=0)
    
    # Satisfaction
    avg_satisfaction_rating = models.FloatField(null=True, blank=True)
    total_ratings = models.PositiveIntegerField(default=0)
    
    # Intentions les plus fréquentes
    top_intents = models.JSONField(default=dict, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['date']
        
    def __str__(self):
        return f"Analytics {self.date}"