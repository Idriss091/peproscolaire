"""
Configuration admin pour la messagerie
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import (
    Message, MessageRecipient, MessageAttachment,
    MessageTemplate, MessageGroup, EmailForwarding,
    NotificationPreference
)


class MessageRecipientInline(admin.TabularInline):
    model = MessageRecipient
    extra = 0
    fields = ['recipient', 'folder', 'is_read', 'is_starred']
    readonly_fields = ['read_at']
    raw_id_fields = ['recipient']


class MessageAttachmentInline(admin.TabularInline):
    model = MessageAttachment
    extra = 0
    fields = ['file', 'filename', 'file_size', 'content_type', 'is_safe']
    readonly_fields = ['filename', 'file_size', 'content_type']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        'subject', 'sender', 'priority_colored', 'sent_at',
        'recipient_count', 'has_attachments', 'is_announcement'
    ]
    list_filter = ['priority', 'is_announcement', 'sent_at']
    search_fields = ['subject', 'body', 'sender__first_name', 'sender__last_name']
    date_hierarchy = 'sent_at'
    raw_id_fields = ['sender', 'parent_message']
    inlines = [MessageRecipientInline, MessageAttachmentInline]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            recipient_count=Count('recipients'),
            attachment_count=Count('attachments')
        )
    
    def recipient_count(self, obj):
        return obj.recipient_count
    recipient_count.short_description = 'Destinataires'
    recipient_count.admin_order_field = 'recipient_count'
    
    def has_attachments(self, obj):
        return obj.attachment_count > 0
    has_attachments.short_description = 'PJ'
    has_attachments.boolean = True
    has_attachments.admin_order_field = 'attachment_count'
    
    def priority_colored(self, obj):
        colors = {
            'low': 'gray',
            'normal': 'blue',
            'high': 'orange',
            'urgent': 'red'
        }
        color = colors.get(obj.priority, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_colored.short_description = 'Priorité'
    priority_colored.admin_order_field = 'priority'


@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'owner', 'is_shared', 'use_count'
    ]
    list_filter = ['category', 'is_shared']
    search_fields = ['name', 'subject', 'body']
    raw_id_fields = ['owner']
    
    actions = ['make_shared', 'make_private']
    
    def make_shared(self, request, queryset):
        updated = queryset.update(is_shared=True)
        self.message_user(request, f"{updated} modèle(s) partagé(s)")
    make_shared.short_description = "Partager les modèles"
    
    def make_private(self, request, queryset):
        updated = queryset.update(is_shared=False)
        self.message_user(request, f"{updated} modèle(s) rendu(s) privé(s)")
    make_private.short_description = "Rendre privés les modèles"


@admin.register(MessageGroup)
class MessageGroupAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'owner', 'member_count', 'is_dynamic',
        'last_used', 'use_count'
    ]
    list_filter = ['is_dynamic']
    search_fields = ['name', 'description']
    raw_id_fields = ['owner', 'dynamic_class']
    filter_horizontal = ['members']
    
    def member_count(self, obj):
        return obj.get_member_count()
    member_count.short_description = 'Membres'


@admin.register(EmailForwarding)
class EmailForwardingAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'forward_email', 'is_active',
        'last_forwarded', 'forward_count'
    ]
    list_filter = ['is_active']
    search_fields = ['user__email', 'forward_email']
    raw_id_fields = ['user']


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'push_enabled', 'email_enabled',
        'email_frequency', 'daily_summary'
    ]
    list_filter = [
        'push_enabled', 'email_enabled',
        'email_frequency', 'daily_summary'
    ]
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    raw_id_fields = ['user']