from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    ChatbotConversation, ChatbotMessage, ChatbotKnowledgeBase,
    ChatbotIntent, ChatbotAnalytics
)

@admin.register(ChatbotConversation)
class ChatbotConversationAdmin(admin.ModelAdmin):
    list_display = [
        'title_display', 'user', 'conversation_type', 'status', 
        'message_count', 'satisfaction_rating', 'last_activity'
    ]
    list_filter = [
        'conversation_type', 'status', 'created_at', 'satisfaction_rating'
    ]
    search_fields = ['title', 'user__username', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'message_count']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('id', 'user', 'title', 'conversation_type', 'status')
        }),
        ('Statistiques', {
            'fields': ('message_count', 'satisfaction_rating', 'last_activity')
        }),
        ('Contexte', {
            'fields': ('context_data',),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def title_display(self, obj):
        if obj.title:
            return obj.title[:50] + ('...' if len(obj.title) > 50 else '')
        return f"Conversation #{str(obj.id)[:8]}"
    title_display.short_description = 'Titre'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


class ChatbotMessageInline(admin.TabularInline):
    model = ChatbotMessage
    extra = 0
    readonly_fields = ['id', 'timestamp', 'response_time_ms', 'tokens_used']
    fields = ['sender', 'message_type', 'content', 'intent', 'confidence_score', 'is_read']
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('timestamp')


@admin.register(ChatbotMessage)
class ChatbotMessageAdmin(admin.ModelAdmin):
    list_display = [
        'conversation_link', 'sender', 'message_type', 'content_preview',
        'intent', 'confidence_score', 'timestamp'
    ]
    list_filter = [
        'sender', 'message_type', 'intent', 'timestamp'
    ]
    search_fields = ['content', 'intent', 'conversation__user__username']
    readonly_fields = ['id', 'timestamp', 'response_time_ms', 'tokens_used']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Message', {
            'fields': ('conversation', 'sender', 'message_type', 'content', 'is_read')
        }),
        ('Analyse IA', {
            'fields': ('intent', 'confidence_score', 'entities'),
            'classes': ('collapse',)
        }),
        ('Performance', {
            'fields': ('response_time_ms', 'tokens_used'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('id', 'timestamp'),
            'classes': ('collapse',)
        }),
    )
    
    def conversation_link(self, obj):
        url = reverse('admin:chatbot_chatbotconversation_change', args=[obj.conversation.id])
        return format_html('<a href="{}">{}</a>', url, str(obj.conversation)[:50])
    conversation_link.short_description = 'Conversation'
    
    def content_preview(self, obj):
        return obj.content[:100] + ('...' if len(obj.content) > 100 else '')
    content_preview.short_description = 'Contenu'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('conversation__user')


@admin.register(ChatbotKnowledgeBase)
class ChatbotKnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'knowledge_type', 'category', 'status',
        'usage_count', 'last_used', 'created_at'
    ]
    list_filter = [
        'knowledge_type', 'status', 'category', 'created_at'
    ]
    search_fields = ['title', 'content', 'category', 'tags']
    readonly_fields = ['id', 'created_at', 'updated_at', 'usage_count', 'last_used']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Contenu', {
            'fields': ('title', 'content', 'knowledge_type', 'status')
        }),
        ('Catégorisation', {
            'fields': ('category', 'tags')
        }),
        ('Recherche et matching', {
            'fields': ('keywords', 'similarity_threshold'),
            'classes': ('collapse',)
        }),
        ('Statistiques', {
            'fields': ('usage_count', 'last_used'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('id', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_knowledge', 'deactivate_knowledge']
    
    def activate_knowledge(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} éléments activés.')
    activate_knowledge.short_description = 'Activer les éléments sélectionnés'
    
    def deactivate_knowledge(self, request, queryset):
        updated = queryset.update(status='archived')
        self.message_user(request, f'{updated} éléments archivés.')
    deactivate_knowledge.short_description = 'Archiver les éléments sélectionnés'


@admin.register(ChatbotIntent)
class ChatbotIntentAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'description_preview', 'priority', 'requires_authentication',
        'requires_admin', 'is_active', 'created_at'
    ]
    list_filter = [
        'requires_authentication', 'requires_admin', 'is_active',
        'action_type', 'created_at'
    ]
    search_fields = ['name', 'description', 'action_type']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Intention', {
            'fields': ('name', 'description', 'priority', 'is_active')
        }),
        ('Reconnaissance', {
            'fields': ('patterns', 'responses')
        }),
        ('Permissions', {
            'fields': ('requires_authentication', 'requires_admin')
        }),
        ('Actions', {
            'fields': ('action_type', 'action_parameters'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def description_preview(self, obj):
        return obj.description[:100] + ('...' if len(obj.description) > 100 else '')
    description_preview.short_description = 'Description'


@admin.register(ChatbotAnalytics)
class ChatbotAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'date', 'total_conversations', 'total_messages',
        'avg_response_time_display', 'avg_satisfaction_rating',
        'successful_resolutions', 'escalations_to_human'
    ]
    list_filter = ['date']
    readonly_fields = [
        'date', 'total_conversations', 'new_conversations', 'closed_conversations',
        'total_messages', 'user_messages', 'bot_messages', 'avg_response_time_ms',
        'successful_resolutions', 'escalations_to_human', 'avg_satisfaction_rating',
        'total_ratings', 'top_intents', 'created_at', 'updated_at'
    ]
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Conversations', {
            'fields': ('total_conversations', 'new_conversations', 'closed_conversations')
        }),
        ('Messages', {
            'fields': ('total_messages', 'user_messages', 'bot_messages')
        }),
        ('Performance', {
            'fields': ('avg_response_time_ms', 'successful_resolutions', 'escalations_to_human')
        }),
        ('Satisfaction', {
            'fields': ('avg_satisfaction_rating', 'total_ratings')
        }),
        ('Intentions populaires', {
            'fields': ('top_intents',),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def avg_response_time_display(self, obj):
        if obj.avg_response_time_ms:
            return f"{obj.avg_response_time_ms:.0f}ms"
        return "-"
    avg_response_time_display.short_description = 'Temps de réponse moyen'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False