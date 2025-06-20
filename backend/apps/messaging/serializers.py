"""
Serializers pour le système de messagerie
"""
from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from .models import (
    Message, MessageRecipient, MessageAttachment,
    MessageTemplate, MessageGroup, EmailForwarding,
    NotificationPreference, MessageFolder
)
from apps.authentication.serializers import UserSerializer


class MessageAttachmentSerializer(serializers.ModelSerializer):
    """Serializer pour les pièces jointes"""
    size_display = serializers.CharField(read_only=True)
    
    class Meta:
        model = MessageAttachment
        fields = [
            'id', 'file', 'filename', 'file_size', 'size_display',
            'content_type', 'is_safe', 'scan_date'
        ]
        read_only_fields = ['id', 'filename', 'file_size', 'is_safe', 'scan_date']


class MessageRecipientSerializer(serializers.ModelSerializer):
    """Serializer pour les destinataires"""
    recipient_name = serializers.CharField(
        source='recipient.get_full_name',
        read_only=True
    )
    recipient_email = serializers.EmailField(
        source='recipient.email',
        read_only=True
    )
    
    class Meta:
        model = MessageRecipient
        fields = [
            'id', 'recipient', 'recipient_name', 'recipient_email',
            'folder', 'is_read', 'read_at', 'is_starred',
            'is_archived', 'labels'
        ]
        read_only_fields = ['id', 'read_at']


class MessageListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des messages"""
    sender_name = serializers.CharField(
        source='sender.get_full_name',
        read_only=True
    )
    sender_avatar = serializers.ImageField(
        source='sender.profile.avatar',
        read_only=True
    )
    recipients_count = serializers.IntegerField(
        source='recipients.count',
        read_only=True
    )
    has_attachments = serializers.BooleanField(
        source='attachments.exists',
        read_only=True
    )
    thread_count = serializers.IntegerField(read_only=True)
    is_draft = serializers.BooleanField(read_only=True)
    
    # Champs spécifiques au destinataire
    is_read = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    folder = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'sender_name', 'sender_avatar',
            'subject', 'priority', 'is_announcement',
            'sent_at', 'recipients_count', 'has_attachments',
            'thread_count', 'is_draft', 'is_read', 'is_starred',
            'folder', 'created_at'
        ]
    
    def get_is_read(self, obj):
        """Statut de lecture pour l'utilisateur actuel"""
        user = self.context['request'].user
        recipient = obj.recipients.filter(recipient=user).first()
        return recipient.is_read if recipient else True
    
    def get_is_starred(self, obj):
        """Statut favori pour l'utilisateur actuel"""
        user = self.context['request'].user
        recipient = obj.recipients.filter(recipient=user).first()
        return recipient.is_starred if recipient else False
    
    def get_folder(self, obj):
        """Dossier pour l'utilisateur actuel"""
        user = self.context['request'].user
        if obj.sender == user:
            return MessageFolder.SENT
        recipient = obj.recipients.filter(recipient=user).first()
        return recipient.folder if recipient else None


class MessageDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour un message"""
    sender = UserSerializer(read_only=True)
    recipients = MessageRecipientSerializer(many=True, read_only=True)
    attachments = MessageAttachmentSerializer(many=True, read_only=True)
    parent_message = MessageListSerializer(read_only=True)
    replies = MessageListSerializer(many=True, read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'subject', 'body', 'priority',
            'is_announcement', 'parent_message', 'sent_at',
            'allow_reply', 'request_read_receipt', 'forward_to_email',
            'recipients', 'attachments', 'replies', 'created_at'
        ]


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un message"""
    recipients = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    groups = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    attachments = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )
    send_now = serializers.BooleanField(
        write_only=True,
        default=True
    )
    
    class Meta:
        model = Message
        fields = [
            'subject', 'body', 'priority', 'is_announcement',
            'parent_message', 'allow_reply', 'request_read_receipt',
            'forward_to_email', 'recipients', 'groups',
            'attachments', 'send_now'
        ]
    
    def validate(self, attrs):
        """Validation des destinataires"""
        recipients = attrs.get('recipients', [])
        groups = attrs.get('groups', [])
        
        if not recipients and not groups:
            raise serializers.ValidationError(
                "Au moins un destinataire ou groupe est requis"
            )
        
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        # Extraire les données supplémentaires
        recipient_ids = validated_data.pop('recipients', [])
        group_ids = validated_data.pop('groups', [])
        attachment_files = validated_data.pop('attachments', [])
        send_now = validated_data.pop('send_now', True)
        
        # Créer le message
        validated_data['sender'] = self.context['request'].user
        message = Message.objects.create(**validated_data)
        
        # Collecter tous les destinataires
        all_recipients = set()
        
        # Ajouter les destinataires directs
        all_recipients.update(recipient_ids)
        
        # Ajouter les membres des groupes
        for group_id in group_ids:
            try:
                group = MessageGroup.objects.get(id=group_id)
                members = group.get_all_members()
                all_recipients.update(members.values_list('id', flat=True))
                
                # Mettre à jour les stats du groupe
                group.last_used = timezone.now()
                group.use_count += 1
                group.save()
            except MessageGroup.DoesNotExist:
                pass
        
        # Créer les entrées destinataires
        for recipient_id in all_recipients:
            if str(recipient_id) != str(message.sender.id):  # Pas d'auto-envoi
                MessageRecipient.objects.create(
                    message=message,
                    recipient_id=recipient_id
                )
        
        # Gérer les pièces jointes
        for file in attachment_files:
            MessageAttachment.objects.create(
                message=message,
                file=file,
                content_type=file.content_type
            )
        
        # Envoyer si demandé
        if send_now:
            message.send()
        
        return message


class MessageReplySerializer(serializers.ModelSerializer):
    """Serializer pour répondre à un message"""
    reply_all = serializers.BooleanField(write_only=True, default=False)
    
    class Meta:
        model = Message
        fields = ['body', 'attachments', 'reply_all']
    
    @transaction.atomic
    def create(self, validated_data):
        # Récupérer le message parent
        parent_message = self.context['parent_message']
        reply_all = validated_data.pop('reply_all', False)
        
        # Créer la réponse
        reply = Message.objects.create(
            sender=self.context['request'].user,
            subject=f"Re: {parent_message.subject}",
            body=validated_data['body'],
            parent_message=parent_message,
            priority=parent_message.priority
        )
        
        # Déterminer les destinataires
        if reply_all:
            # Répondre à tous (expéditeur + tous les destinataires sauf soi)
            recipients = set([parent_message.sender.id])
            recipients.update(
                parent_message.recipients.exclude(
                    recipient=self.context['request'].user
                ).values_list('recipient_id', flat=True)
            )
        else:
            # Répondre seulement à l'expéditeur
            recipients = [parent_message.sender.id]
        
        # Créer les destinataires
        for recipient_id in recipients:
            if recipient_id != reply.sender.id:
                MessageRecipient.objects.create(
                    message=reply,
                    recipient_id=recipient_id
                )
        
        # Envoyer
        reply.send()
        
        return reply


class MessageTemplateSerializer(serializers.ModelSerializer):
    """Serializer pour les modèles de messages"""
    owner_name = serializers.CharField(
        source='owner.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = MessageTemplate
        fields = [
            'id', 'owner', 'owner_name', 'name', 'category',
            'subject', 'body', 'is_shared', 'use_count',
            'created_at'
        ]
        read_only_fields = ['id', 'owner', 'use_count', 'created_at']
    
    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class MessageGroupSerializer(serializers.ModelSerializer):
    """Serializer pour les groupes de destinataires"""
    member_count = serializers.IntegerField(
        source='get_member_count',
        read_only=True
    )
    members = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = MessageGroup
        fields = [
            'id', 'owner', 'name', 'description', 'members',
            'member_count', 'is_dynamic', 'dynamic_class',
            'dynamic_user_type', 'last_used', 'use_count',
            'created_at'
        ]
        read_only_fields = ['id', 'owner', 'last_used', 'use_count', 'created_at']
    
    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class EmailForwardingSerializer(serializers.ModelSerializer):
    """Serializer pour la redirection email"""
    
    class Meta:
        model = EmailForwarding
        fields = [
            'id', 'forward_email', 'is_active', 'forward_all',
            'forward_priority', 'forward_from_types',
            'last_forwarded', 'forward_count'
        ]
        read_only_fields = ['id', 'last_forwarded', 'forward_count']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer pour les préférences de notification"""
    
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'push_enabled', 'push_sound', 'email_enabled',
            'email_frequency', 'quiet_hours_enabled',
            'quiet_hours_start', 'quiet_hours_end',
            'notify_urgent_only', 'daily_summary', 'summary_time'
        ]
        read_only_fields = ['id']


class MessageSearchSerializer(serializers.Serializer):
    """Serializer pour la recherche de messages"""
    query = serializers.CharField(required=False)
    sender = serializers.UUIDField(required=False)
    folder = serializers.ChoiceField(
        choices=MessageFolder.choices,
        required=False
    )
    priority = serializers.ChoiceField(
        choices=['high', 'urgent'],
        required=False
    )
    is_starred = serializers.BooleanField(required=False)
    is_unread = serializers.BooleanField(required=False)
    has_attachments = serializers.BooleanField(required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    
    def search(self, user):
        """Effectuer la recherche"""
        from django.db.models import Q, Exists, OuterRef
        
        # Requête de base - messages où l'utilisateur est destinataire ou expéditeur
        queryset = Message.objects.filter(
            Q(recipients__recipient=user) | Q(sender=user)
        ).distinct()
        
        # Appliquer les filtres
        if self.validated_data.get('query'):
            query = self.validated_data['query']
            queryset = queryset.filter(
                Q(subject__icontains=query) |
                Q(body__icontains=query) |
                Q(sender__first_name__icontains=query) |
                Q(sender__last_name__icontains=query)
            )
        
        if self.validated_data.get('sender'):
            queryset = queryset.filter(sender_id=self.validated_data['sender'])
        
        if self.validated_data.get('folder'):
            queryset = queryset.filter(
                recipients__recipient=user,
                recipients__folder=self.validated_data['folder']
            )
        
        if self.validated_data.get('priority'):
            queryset = queryset.filter(priority=self.validated_data['priority'])
        
        if self.validated_data.get('is_starred'):
            queryset = queryset.filter(
                recipients__recipient=user,
                recipients__is_starred=True
            )
        
        if self.validated_data.get('is_unread'):
            queryset = queryset.filter(
                recipients__recipient=user,
                recipients__is_read=False
            )
        
        if self.validated_data.get('has_attachments'):
            queryset = queryset.filter(
                Exists(MessageAttachment.objects.filter(message=OuterRef('pk')))
            )
        
        if self.validated_data.get('date_from'):
            queryset = queryset.filter(sent_at__date__gte=self.validated_data['date_from'])
        
        if self.validated_data.get('date_to'):
            queryset = queryset.filter(sent_at__date__lte=self.validated_data['date_to'])
        
        return queryset.order_by('-sent_at')


class ConversationSerializer(serializers.Serializer):
    """Serializer pour afficher une conversation complète"""
    
    def to_representation(self, instance):
        """Instance est le message racine"""
        # Récupérer tous les messages du fil
        messages = instance.get_thread_messages().order_by('created_at')
        
        # Marquer comme lus
        user = self.context['request'].user
        MessageRecipient.objects.filter(
            message__in=messages,
            recipient=user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        
        return {
            'root_message': MessageDetailSerializer(instance).data,
            'messages': MessageDetailSerializer(messages, many=True).data,
            'total_messages': messages.count()
        }