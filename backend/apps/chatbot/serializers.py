from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    ChatbotConversation, ChatbotMessage, ChatbotKnowledgeBase,
    ChatbotIntent, ChatbotAnalytics
)

User = get_user_model()


class ChatbotMessageSerializer(serializers.ModelSerializer):
    """Serializer pour les messages du chatbot"""
    
    class Meta:
        model = ChatbotMessage
        fields = [
            'id', 'sender', 'message_type', 'content', 'timestamp',
            'is_read', 'intent', 'confidence_score', 'entities',
            'response_time_ms'
        ]
        read_only_fields = [
            'id', 'timestamp', 'intent', 'confidence_score', 'entities',
            'response_time_ms'
        ]


class ChatbotConversationSerializer(serializers.ModelSerializer):
    """Serializer pour les conversations du chatbot"""
    messages = ChatbotMessageSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = ChatbotConversation
        fields = [
            'id', 'user', 'user_name', 'title', 'conversation_type',
            'status', 'created_at', 'updated_at', 'last_activity',
            'message_count', 'satisfaction_rating', 'messages'
        ]
        read_only_fields = [
            'id', 'user', 'created_at', 'updated_at', 'last_activity',
            'message_count'
        ]


class ChatbotConversationListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des conversations"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatbotConversation
        fields = [
            'id', 'user_name', 'title', 'conversation_type', 'status',
            'last_activity', 'message_count', 'satisfaction_rating',
            'last_message'
        ]
    
    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return {
                'content': last_message.content[:100] + ('...' if len(last_message.content) > 100 else ''),
                'sender': last_message.sender,
                'timestamp': last_message.timestamp
            }
        return None


class ChatbotMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un nouveau message"""
    
    class Meta:
        model = ChatbotMessage
        fields = ['conversation', 'content', 'message_type']
    
    def create(self, validated_data):
        # Ajouter automatiquement l'utilisateur comme expéditeur
        validated_data['sender'] = 'user'
        return super().create(validated_data)


class ChatbotKnowledgeBaseSerializer(serializers.ModelSerializer):
    """Serializer pour la base de connaissances"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ChatbotKnowledgeBase
        fields = [
            'id', 'title', 'content', 'knowledge_type', 'category',
            'tags', 'keywords', 'status', 'usage_count', 'last_used',
            'created_at', 'updated_at', 'created_by_name'
        ]
        read_only_fields = [
            'id', 'usage_count', 'last_used', 'created_at', 'updated_at'
        ]


class ChatbotIntentSerializer(serializers.ModelSerializer):
    """Serializer pour les intentions du chatbot"""
    
    class Meta:
        model = ChatbotIntent
        fields = [
            'id', 'name', 'description', 'patterns', 'responses',
            'requires_authentication', 'requires_admin', 'priority',
            'action_type', 'action_parameters', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChatbotAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer pour les analytiques du chatbot"""
    
    class Meta:
        model = ChatbotAnalytics
        fields = [
            'date', 'total_conversations', 'new_conversations',
            'closed_conversations', 'total_messages', 'user_messages',
            'bot_messages', 'avg_response_time_ms', 'successful_resolutions',
            'escalations_to_human', 'avg_satisfaction_rating',
            'total_ratings', 'top_intents'
        ]
        read_only_fields = ['date']


class ChatbotQuickReplySerializer(serializers.Serializer):
    """Serializer pour les réponses rapides du chatbot"""
    text = serializers.CharField(max_length=100)
    action = serializers.CharField(max_length=50, required=False)
    payload = serializers.JSONField(required=False)


class ChatbotResponseSerializer(serializers.Serializer):
    """Serializer pour les réponses du chatbot"""
    message = serializers.CharField()
    message_type = serializers.ChoiceField(choices=ChatbotMessage.MESSAGE_TYPES, default='text')
    intent = serializers.CharField(required=False)
    confidence_score = serializers.FloatField(required=False)
    entities = serializers.JSONField(required=False)
    quick_replies = ChatbotQuickReplySerializer(many=True, required=False)
    suggestions = serializers.ListField(child=serializers.CharField(), required=False)
    needs_human = serializers.BooleanField(default=False)
    response_time_ms = serializers.IntegerField(required=False)
    tokens_used = serializers.IntegerField(required=False)


class ChatbotFeedbackSerializer(serializers.Serializer):
    """Serializer pour les retours sur les conversations"""
    satisfaction_rating = serializers.IntegerField(min_value=1, max_value=5)
    feedback_text = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    
    def update(self, instance, validated_data):
        instance.satisfaction_rating = validated_data.get('satisfaction_rating', instance.satisfaction_rating)
        instance.save()
        return instance


class ChatbotSearchSerializer(serializers.Serializer):
    """Serializer pour la recherche dans la base de connaissances"""
    query = serializers.CharField(max_length=500)
    knowledge_type = serializers.ChoiceField(
        choices=ChatbotKnowledgeBase.KNOWLEDGE_TYPES,
        required=False
    )
    category = serializers.CharField(max_length=100, required=False)
    limit = serializers.IntegerField(min_value=1, max_value=20, default=5)


class ChatbotSuggestionSerializer(serializers.Serializer):
    """Serializer pour les suggestions automatiques"""
    text = serializers.CharField()
    confidence_score = serializers.FloatField()
    source = serializers.CharField()  # 'knowledge_base', 'intent', 'ml_model'
    metadata = serializers.JSONField(required=False)