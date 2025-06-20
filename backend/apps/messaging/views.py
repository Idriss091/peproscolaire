"""
Vues API pour le système de messagerie
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Count, Case, When, BooleanField, F
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters import rest_framework as filters

from .models import (
    Message, MessageRecipient, MessageAttachment,
    MessageTemplate, MessageGroup, EmailForwarding,
    NotificationPreference, MessageFolder, MessagePriority
)
from .serializers import (
    MessageListSerializer, MessageDetailSerializer,
    MessageCreateSerializer, MessageReplySerializer,
    MessageTemplateSerializer, MessageGroupSerializer,
    EmailForwardingSerializer, NotificationPreferenceSerializer,
    MessageSearchSerializer, ConversationSerializer,
    MessageRecipientSerializer
)
from .tasks import send_message_notifications, process_email_batch


class MessageFilter(filters.FilterSet):
    """Filtres pour les messages"""
    folder = filters.ChoiceFilter(
        field_name='recipients__folder',
        choices=MessageFolder.choices,
        method='filter_folder'
    )
    is_unread = filters.BooleanFilter(method='filter_unread')
    is_starred = filters.BooleanFilter(
        field_name='recipients__is_starred',
        method='filter_starred'
    )
    priority = filters.MultipleChoiceFilter(
        choices=MessagePriority.choices
    )
    has_attachments = filters.BooleanFilter(method='filter_attachments')
    
    class Meta:
        model = Message
        fields = ['sender', 'is_announcement']
    
    def filter_folder(self, queryset, name, value):
        user = self.request.user
        if value == MessageFolder.SENT:
            return queryset.filter(sender=user)
        return queryset.filter(
            recipients__recipient=user,
            recipients__folder=value
        )
    
    def filter_unread(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(
                recipients__recipient=user,
                recipients__is_read=False
            )
        return queryset.filter(
            recipients__recipient=user,
            recipients__is_read=True
        )
    
    def filter_starred(self, queryset, name, value):
        user = self.request.user
        return queryset.filter(
            recipients__recipient=user,
            recipients__is_starred=value
        )
    
    def filter_attachments(self, queryset, name, value):
        if value:
            return queryset.filter(attachments__isnull=False).distinct()
        return queryset.filter(attachments__isnull=True)


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet pour les messages"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = MessageFilter
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        elif self.action in ['retrieve', 'conversation']:
            return MessageDetailSerializer
        elif self.action == 'reply':
            return MessageReplySerializer
        return MessageListSerializer
    
    def get_queryset(self):
        """Messages de l'utilisateur connecté"""
        user = self.request.user
        
        # Messages reçus ou envoyés
        queryset = Message.objects.filter(
            Q(recipients__recipient=user) | Q(sender=user)
        ).select_related(
            'sender', 'sender__profile'
        ).prefetch_related(
            'recipients', 'attachments'
        ).annotate(
            # Annotations pour l'utilisateur actuel
            user_is_recipient=Case(
                When(recipients__recipient=user, then=True),
                default=False,
                output_field=BooleanField()
            )
        ).distinct()
        
        # Exclure les brouillons des autres
        queryset = queryset.exclude(
            ~Q(sender=user) & Q(sent_at__isnull=True)
        )
        
        return queryset.order_by('-created_at')
    
    def retrieve(self, request, *args, **kwargs):
        """Récupérer un message et le marquer comme lu"""
        instance = self.get_object()
        
        # Marquer comme lu si destinataire
        recipient = instance.recipients.filter(recipient=request.user).first()
        if recipient:
            recipient.mark_as_read()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Nombre de messages non lus"""
        count = MessageRecipient.objects.filter(
            recipient=request.user,
            is_read=False,
            folder=MessageFolder.INBOX
        ).count()
        
        return Response({'unread_count': count})
    
    @action(detail=False, methods=['get'])
    def folders(self, request):
        """Statistiques par dossier"""
        user = request.user
        
        stats = {}
        for folder, label in MessageFolder.choices:
            if folder == MessageFolder.SENT:
                count = Message.objects.filter(
                    sender=user,
                    sent_at__isnull=False
                ).count()
            else:
                count = MessageRecipient.objects.filter(
                    recipient=user,
                    folder=folder
                ).count()
            
            unread = 0
            if folder == MessageFolder.INBOX:
                unread = MessageRecipient.objects.filter(
                    recipient=user,
                    folder=folder,
                    is_read=False
                ).count()
            
            stats[folder] = {
                'label': label,
                'count': count,
                'unread': unread
            }
        
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Marquer comme lu"""
        message = self.get_object()
        recipient = message.recipients.filter(recipient=request.user).first()
        
        if recipient:
            recipient.mark_as_read()
            return Response({'status': 'marked as read'})
        
        return Response(
            {'error': 'Vous n\'êtes pas destinataire de ce message'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def toggle_star(self, request, pk=None):
        """Ajouter/retirer des favoris"""
        message = self.get_object()
        recipient = message.recipients.filter(recipient=request.user).first()
        
        if recipient:
            recipient.toggle_star()
            return Response({'is_starred': recipient.is_starred})
        
        return Response(
            {'error': 'Vous n\'êtes pas destinataire de ce message'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def move_to_folder(self, request, pk=None):
        """Déplacer vers un dossier"""
        message = self.get_object()
        folder = request.data.get('folder')
        
        if not folder:
            return Response(
                {'error': 'Le dossier est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        recipient = message.recipients.filter(recipient=request.user).first()
        
        if recipient:
            try:
                recipient.move_to_folder(folder)
                return Response({'folder': folder})
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(
            {'error': 'Vous n\'êtes pas destinataire de ce message'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        """Actions en masse sur les messages"""
        message_ids = request.data.get('message_ids', [])
        action = request.data.get('action')
        
        if not message_ids or not action:
            return Response(
                {'error': 'message_ids et action sont requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Récupérer les messages concernés
        messages = self.get_queryset().filter(id__in=message_ids)
        
        if action == 'mark_read':
            MessageRecipient.objects.filter(
                message__in=messages,
                recipient=request.user
            ).update(is_read=True, read_at=timezone.now())
            
        elif action == 'mark_unread':
            MessageRecipient.objects.filter(
                message__in=messages,
                recipient=request.user
            ).update(is_read=False, read_at=None)
            
        elif action == 'star':
            MessageRecipient.objects.filter(
                message__in=messages,
                recipient=request.user
            ).update(is_starred=True)
            
        elif action == 'unstar':
            MessageRecipient.objects.filter(
                message__in=messages,
                recipient=request.user
            ).update(is_starred=False)
            
        elif action in MessageFolder.values:
            MessageRecipient.objects.filter(
                message__in=messages,
                recipient=request.user
            ).update(folder=action)
            
        else:
            return Response(
                {'error': f'Action inconnue: {action}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({'status': f'{len(messages)} messages traités'})
    
    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """Répondre à un message"""
        parent_message = self.get_object()
        
        # Vérifier que l'utilisateur peut répondre
        if not parent_message.allow_reply:
            return Response(
                {'error': 'Les réponses ne sont pas autorisées pour ce message'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        is_recipient = parent_message.recipients.filter(
            recipient=request.user
        ).exists()
        is_sender = parent_message.sender == request.user
        
        if not (is_recipient or is_sender):
            return Response(
                {'error': 'Vous ne pouvez pas répondre à ce message'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = MessageReplySerializer(
            data=request.data,
            context={
                'request': request,
                'parent_message': parent_message
            }
        )
        serializer.is_valid(raise_exception=True)
        reply = serializer.save()
        
        return Response(
            MessageDetailSerializer(reply).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['get'])
    def conversation(self, request, pk=None):
        """Afficher la conversation complète"""
        message = self.get_object()
        root_message = message.get_root_message()
        
        serializer = ConversationSerializer(
            root_message,
            context={'request': request}
        )
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Recherche avancée de messages"""
        serializer = MessageSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        messages = serializer.search(request.user)
        
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageListSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        
        serializer = MessageListSerializer(
            messages,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def create_from_template(self, request):
        """Créer un message depuis un modèle"""
        template_id = request.data.get('template_id')
        context = request.data.get('context', {})
        recipients = request.data.get('recipients', [])
        
        if not template_id:
            return Response(
                {'error': 'template_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        template = get_object_or_404(MessageTemplate, id=template_id)
        
        # Vérifier l'accès au modèle
        if template.owner != request.user and not template.is_shared:
            return Response(
                {'error': 'Vous n\'avez pas accès à ce modèle'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Créer le message
        message = template.create_message(request.user, context)
        
        # Ajouter les destinataires
        for recipient_id in recipients:
            MessageRecipient.objects.create(
                message=message,
                recipient_id=recipient_id
            )
        
        # Envoyer
        message.send()
        
        return Response(
            MessageDetailSerializer(message).data,
            status=status.HTTP_201_CREATED
        )


class MessageTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet pour les modèles de messages"""
    serializer_class = MessageTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['category', 'is_shared']
    search_fields = ['name', 'subject', 'body']
    
    def get_queryset(self):
        """Modèles accessibles à l'utilisateur"""
        user = self.request.user
        return MessageTemplate.objects.filter(
            Q(owner=user) | Q(is_shared=True)
        )
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Modèles groupés par catégorie"""
        templates = self.get_queryset()
        
        categories = {}
        for category, label in MessageTemplate.CATEGORY_CHOICES:
            category_templates = templates.filter(category=category)
            if category_templates.exists():
                categories[category] = {
                    'label': label,
                    'templates': MessageTemplateSerializer(
                        category_templates,
                        many=True
                    ).data
                }
        
        return Response(categories)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Dupliquer un modèle"""
        template = self.get_object()
        
        # Créer une copie
        new_template = MessageTemplate.objects.create(
            owner=request.user,
            name=f"Copie de {template.name}",
            category=template.category,
            subject=template.subject,
            body=template.body,
            is_shared=False
        )
        
        return Response(
            MessageTemplateSerializer(new_template).data,
            status=status.HTTP_201_CREATED
        )


class MessageGroupViewSet(viewsets.ModelViewSet):
    """ViewSet pour les groupes de destinataires"""
    serializer_class = MessageGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Groupes de l'utilisateur"""
        return MessageGroup.objects.filter(
            owner=self.request.user
        ).prefetch_related('members')
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Liste des membres d'un groupe"""
        group = self.get_object()
        members = group.get_all_members()
        
        # Paginer si nécessaire
        page = self.paginate_queryset(members)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = UserSerializer(members, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_members(self, request, pk=None):
        """Ajouter des membres à un groupe"""
        group = self.get_object()
        
        if group.is_dynamic:
            return Response(
                {'error': 'Impossible d\'ajouter des membres à un groupe dynamique'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        member_ids = request.data.get('member_ids', [])
        group.members.add(*member_ids)
        
        return Response({
            'message': f'{len(member_ids)} membres ajoutés',
            'total_members': group.get_member_count()
        })
    
    @action(detail=True, methods=['post'])
    def remove_members(self, request, pk=None):
        """Retirer des membres d'un groupe"""
        group = self.get_object()
        
        if group.is_dynamic:
            return Response(
                {'error': 'Impossible de retirer des membres d\'un groupe dynamique'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        member_ids = request.data.get('member_ids', [])
        group.members.remove(*member_ids)
        
        return Response({
            'message': f'{len(member_ids)} membres retirés',
            'total_members': group.get_member_count()
        })
    
    @action(detail=False, methods=['get'])
    def quick_groups(self, request):
        """Groupes rapides prédéfinis"""
        user = request.user
        quick_groups = []
        
        if user.user_type == 'teacher':
            # Groupe "Mes élèves"
            from apps.schools.models import Class
            my_classes = Class.objects.filter(
                Q(main_teacher=user) |
                Q(schedules__teacher=user)
            ).distinct()
            
            for class_obj in my_classes:
                quick_groups.append({
                    'id': f'class_{class_obj.id}',
                    'name': f'Élèves de {class_obj}',
                    'member_count': class_obj.students.filter(is_active=True).count(),
                    'type': 'class'
                })
            
            # Groupe "Collègues"
            quick_groups.append({
                'id': 'teachers',
                'name': 'Tous les professeurs',
                'member_count': User.objects.filter(
                    user_type='teacher',
                    is_active=True
                ).count(),
                'type': 'teachers'
            })
        
        return Response(quick_groups)


@api_view(['GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def email_forwarding_settings(request):
    """Gérer les paramètres de redirection email"""
    forwarding, created = EmailForwarding.objects.get_or_create(
        user=request.user
    )
    
    if request.method == 'GET':
        serializer = EmailForwardingSerializer(forwarding)
        return Response(serializer.data)
    
    else:  # PUT
        serializer = EmailForwardingSerializer(
            forwarding,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data)


@api_view(['GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def notification_preferences(request):
    """Gérer les préférences de notification"""
    preferences, created = NotificationPreference.objects.get_or_create(
        user=request.user
    )
    
    if request.method == 'GET':
        serializer = NotificationPreferenceSerializer(preferences)
        return Response(serializer.data)
    
    else:  # PUT
        serializer = NotificationPreferenceSerializer(
            preferences,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def message_statistics(request):
    """Statistiques de messagerie de l'utilisateur"""
    user = request.user
    
    # Messages envoyés
    sent_count = Message.objects.filter(
        sender=user,
        sent_at__isnull=False
    ).count()
    
    # Messages reçus
    received_count = MessageRecipient.objects.filter(
        recipient=user
    ).count()
    
    # Taux de lecture
    read_count = MessageRecipient.objects.filter(
        recipient=user,
        is_read=True
    ).count()
    
    read_rate = (read_count / received_count * 100) if received_count > 0 else 0
    
    # Messages par priorité
    priority_stats = MessageRecipient.objects.filter(
        recipient=user
    ).values('message__priority').annotate(
        count=Count('id')
    )
    
    # Expéditeurs fréquents
    top_senders = MessageRecipient.objects.filter(
        recipient=user
    ).values(
        'message__sender__id',
        'message__sender__first_name',
        'message__sender__last_name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    return Response({
        'sent_count': sent_count,
        'received_count': received_count,
        'read_rate': round(read_rate, 2),
        'priority_distribution': {
            item['message__priority']: item['count']
            for item in priority_stats
        },
        'top_senders': [
            {
                'id': sender['message__sender__id'],
                'name': f"{sender['message__sender__first_name']} {sender['message__sender__last_name']}",
                'count': sender['count']
            }
            for sender in top_senders
        ]
    })