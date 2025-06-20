"""
Modèles pour le système de messagerie interne
"""
from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from apps.core.models import BaseModel
from apps.authentication.models import User
from apps.schools.models import Class, School


class MessageFolder(models.TextChoices):
    """Dossiers de messages"""
    INBOX = 'inbox', _('Boîte de réception')
    SENT = 'sent', _('Messages envoyés')
    DRAFT = 'draft', _('Brouillons')
    TRASH = 'trash', _('Corbeille')
    ARCHIVE = 'archive', _('Archives')


class MessagePriority(models.TextChoices):
    """Priorité des messages"""
    LOW = 'low', _('Faible')
    NORMAL = 'normal', _('Normale')
    HIGH = 'high', _('Haute')
    URGENT = 'urgent', _('Urgente')


class Message(BaseModel):
    """
    Message principal
    """
    # Expéditeur
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name=_("Expéditeur")
    )
    
    # Contenu
    subject = models.CharField(
        max_length=255,
        verbose_name=_("Objet")
    )
    body = models.TextField(verbose_name=_("Corps du message"))
    
    # Métadonnées
    priority = models.CharField(
        max_length=10,
        choices=MessagePriority.choices,
        default=MessagePriority.NORMAL,
        verbose_name=_("Priorité")
    )
    is_announcement = models.BooleanField(
        default=False,
        verbose_name=_("Annonce"),
        help_text=_("Message diffusé à plusieurs destinataires")
    )
    
    # Réponse
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name=_("Message parent")
    )
    
    # État
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Date d'envoi")
    )
    
    # Paramètres
    allow_reply = models.BooleanField(
        default=True,
        verbose_name=_("Autoriser les réponses")
    )
    request_read_receipt = models.BooleanField(
        default=False,
        verbose_name=_("Demander accusé de lecture")
    )
    
    # Redirection email
    forward_to_email = models.BooleanField(
        default=False,
        verbose_name=_("Transférer par email")
    )
    
    class Meta:
        db_table = 'messages'
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sender', 'sent_at']),
            models.Index(fields=['subject']),
        ]
    
    def __str__(self):
        return f"{self.subject} - {self.sender.get_full_name()}"
    
    @property
    def is_draft(self):
        """Vérifie si le message est un brouillon"""
        return self.sent_at is None
    
    @property
    def thread_count(self):
        """Nombre de messages dans le fil de discussion"""
        count = 1  # Le message lui-même
        if self.parent_message:
            # Remonter jusqu'au message racine
            root = self.get_root_message()
            count = root.get_thread_messages().count()
        else:
            # C'est le message racine
            count = self.get_thread_messages().count()
        return count
    
    def get_root_message(self):
        """Récupère le message racine du fil"""
        message = self
        while message.parent_message:
            message = message.parent_message
        return message
    
    def get_thread_messages(self):
        """Récupère tous les messages du fil"""
        if self.parent_message:
            return self.get_root_message().get_thread_messages()
        
        # Récupérer tous les descendants
        messages = [self]
        replies = list(self.replies.all())
        
        while replies:
            messages.extend(replies)
            new_replies = []
            for reply in replies:
                new_replies.extend(list(reply.replies.all()))
            replies = new_replies
        
        return Message.objects.filter(id__in=[m.id for m in messages])
    
    def send(self):
        """Envoyer le message"""
        if not self.is_draft:
            raise ValidationError(_("Ce message a déjà été envoyé"))
        
        self.sent_at = timezone.now()
        self.save()
        
        # Si redirection email activée, envoyer par email
        if self.forward_to_email:
            from .tasks import send_message_by_email
            send_message_by_email.delay(self.id)


class MessageRecipient(BaseModel):
    """
    Destinataire d'un message
    """
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='recipients'
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    
    # État pour ce destinataire
    folder = models.CharField(
        max_length=20,
        choices=MessageFolder.choices,
        default=MessageFolder.INBOX,
        verbose_name=_("Dossier")
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name=_("Lu")
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Lu le")
    )
    is_starred = models.BooleanField(
        default=False,
        verbose_name=_("Favori")
    )
    is_archived = models.BooleanField(
        default=False,
        verbose_name=_("Archivé")
    )
    
    # Labels personnalisés
    labels = ArrayField(
        models.CharField(max_length=50),
        default=list,
        blank=True,
        verbose_name=_("Étiquettes")
    )
    
    # Notification
    notification_sent = models.BooleanField(
        default=False,
        verbose_name=_("Notification envoyée")
    )
    email_sent = models.BooleanField(
        default=False,
        verbose_name=_("Email envoyé")
    )
    
    class Meta:
        db_table = 'message_recipients'
        verbose_name = _("Destinataire")
        verbose_name_plural = _("Destinataires")
        unique_together = ['message', 'recipient']
        indexes = [
            models.Index(fields=['recipient', 'folder', 'is_read']),
            models.Index(fields=['recipient', 'is_starred']),
        ]
    
    def __str__(self):
        return f"{self.message.subject} -> {self.recipient.get_full_name()}"
    
    def mark_as_read(self):
        """Marquer comme lu"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
            
            # Envoyer accusé de lecture si demandé
            if self.message.request_read_receipt:
                from .tasks import send_read_receipt
                send_read_receipt.delay(self.id)
    
    def move_to_folder(self, folder):
        """Déplacer vers un dossier"""
        if folder not in MessageFolder.values:
            raise ValidationError(f"Dossier invalide: {folder}")
        
        self.folder = folder
        if folder == MessageFolder.ARCHIVE:
            self.is_archived = True
        self.save()
    
    def toggle_star(self):
        """Ajouter/retirer des favoris"""
        self.is_starred = not self.is_starred
        self.save()


class MessageAttachment(BaseModel):
    """
    Pièce jointe d'un message
    """
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    
    file = models.FileField(
        upload_to='messages/attachments/%Y/%m/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx',
                                  'ppt', 'pptx', 'jpg', 'jpeg', 'png',
                                  'gif', 'zip', 'txt']
            )
        ],
        verbose_name=_("Fichier")
    )
    
    filename = models.CharField(
        max_length=255,
        verbose_name=_("Nom du fichier")
    )
    
    file_size = models.PositiveIntegerField(
        verbose_name=_("Taille (octets)")
    )
    
    content_type = models.CharField(
        max_length=100,
        verbose_name=_("Type MIME")
    )
    
    # Sécurité
    is_safe = models.BooleanField(
        default=True,
        verbose_name=_("Fichier sûr"),
        help_text=_("Résultat du scan antivirus")
    )
    scan_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Date du scan")
    )
    
    class Meta:
        db_table = 'message_attachments'
        verbose_name = _("Pièce jointe")
        verbose_name_plural = _("Pièces jointes")
        ordering = ['filename']
    
    def __str__(self):
        return self.filename
    
    def save(self, *args, **kwargs):
        # Enregistrer les métadonnées du fichier
        if self.file:
            self.filename = self.file.name.split('/')[-1]
            self.file_size = self.file.size
            # Le content_type sera défini dans la vue
        super().save(*args, **kwargs)
    
    @property
    def size_display(self):
        """Affichage formaté de la taille"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class MessageTemplate(BaseModel):
    """
    Modèle de message réutilisable
    """
    CATEGORY_CHOICES = [
        ('general', 'Général'),
        ('absence', 'Absence'),
        ('behavior', 'Comportement'),
        ('grades', 'Notes'),
        ('meeting', 'Rendez-vous'),
        ('info', 'Information'),
    ]
    
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='message_templates'
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name=_("Nom du modèle")
    )
    
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='general',
        verbose_name=_("Catégorie")
    )
    
    subject = models.CharField(
        max_length=255,
        verbose_name=_("Objet")
    )
    
    body = models.TextField(
        verbose_name=_("Corps du message"),
        help_text=_("Utilisez {nom}, {prenom}, {classe} comme variables")
    )
    
    is_shared = models.BooleanField(
        default=False,
        verbose_name=_("Partagé"),
        help_text=_("Disponible pour tous les enseignants")
    )
    
    use_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Nombre d'utilisations")
    )
    
    class Meta:
        db_table = 'message_templates'
        verbose_name = _("Modèle de message")
        verbose_name_plural = _("Modèles de messages")
        ordering = ['-use_count', 'name']
    
    def __str__(self):
        return self.name
    
    def create_message(self, sender, context=None):
        """Créer un message à partir du modèle"""
        # Remplacer les variables
        subject = self.subject
        body = self.body
        
        if context:
            for key, value in context.items():
                subject = subject.replace(f"{{{key}}}", str(value))
                body = body.replace(f"{{{key}}}", str(value))
        
        message = Message.objects.create(
            sender=sender,
            subject=subject,
            body=body
        )
        
        # Incrémenter le compteur
        self.use_count += 1
        self.save()
        
        return message


class MessageGroup(BaseModel):
    """
    Groupe de destinataires
    """
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='message_groups'
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name=_("Nom du groupe")
    )
    
    description = models.TextField(
        blank=True,
        verbose_name=_("Description")
    )
    
    # Membres du groupe
    members = models.ManyToManyField(
        User,
        related_name='messaging_groups',
        verbose_name=_("Membres")
    )
    
    # Groupe dynamique basé sur des critères
    is_dynamic = models.BooleanField(
        default=False,
        verbose_name=_("Groupe dynamique")
    )
    
    # Critères pour les groupes dynamiques
    dynamic_class = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text=_("Tous les élèves de cette classe")
    )
    
    dynamic_user_type = models.CharField(
        max_length=20,
        blank=True,
        help_text=_("Type d'utilisateur (student, parent, teacher)")
    )
    
    # Statistiques
    last_used = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Dernière utilisation")
    )
    
    use_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Nombre d'utilisations")
    )
    
    class Meta:
        db_table = 'message_groups'
        verbose_name = _("Groupe de destinataires")
        verbose_name_plural = _("Groupes de destinataires")
        unique_together = ['owner', 'name']
        ordering = ['-last_used', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_member_count()} membres)"
    
    def get_member_count(self):
        """Nombre de membres du groupe"""
        if self.is_dynamic:
            return self.get_dynamic_members().count()
        return self.members.count()
    
    def get_dynamic_members(self):
        """Récupérer les membres pour un groupe dynamique"""
        if not self.is_dynamic:
            return self.members.all()
        
        queryset = User.objects.filter(is_active=True)
        
        if self.dynamic_class:
            # Tous les élèves de la classe
            queryset = queryset.filter(
                enrollments__class_group=self.dynamic_class,
                enrollments__is_active=True
            )
        
        if self.dynamic_user_type:
            queryset = queryset.filter(user_type=self.dynamic_user_type)
        
        return queryset.distinct()
    
    def get_all_members(self):
        """Récupérer tous les membres (statiques + dynamiques)"""
        if self.is_dynamic:
            return self.get_dynamic_members()
        return self.members.all()


class EmailForwarding(BaseModel):
    """
    Configuration de redirection email
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='email_forwarding'
    )
    
    forward_email = models.EmailField(
        verbose_name=_("Email de redirection")
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Actif")
    )
    
    # Filtres
    forward_all = models.BooleanField(
        default=True,
        verbose_name=_("Transférer tous les messages")
    )
    
    forward_priority = ArrayField(
        models.CharField(max_length=10),
        default=list,
        blank=True,
        verbose_name=_("Priorités à transférer"),
        help_text=_("Liste des priorités de messages à transférer")
    )
    
    forward_from_types = ArrayField(
        models.CharField(max_length=20),
        default=list,
        blank=True,
        verbose_name=_("Types d'expéditeurs"),
        help_text=_("Types d'utilisateurs dont transférer les messages")
    )
    
    # Statistiques
    last_forwarded = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Dernier transfert")
    )
    
    forward_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Nombre de transferts")
    )
    
    class Meta:
        db_table = 'email_forwardings'
        verbose_name = _("Redirection email")
        verbose_name_plural = _("Redirections email")
    
    def __str__(self):
        return f"{self.user.get_full_name()} -> {self.forward_email}"
    
    def should_forward(self, message):
        """Détermine si un message doit être transféré"""
        if not self.is_active:
            return False
        
        if self.forward_all:
            return True
        
        # Vérifier la priorité
        if self.forward_priority and message.priority in self.forward_priority:
            return True
        
        # Vérifier le type d'expéditeur
        if self.forward_from_types and message.sender.user_type in self.forward_from_types:
            return True
        
        return False


class NotificationPreference(BaseModel):
    """
    Préférences de notification pour la messagerie
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    # Notifications push
    push_enabled = models.BooleanField(
        default=True,
        verbose_name=_("Notifications push")
    )
    
    push_sound = models.BooleanField(
        default=True,
        verbose_name=_("Son des notifications")
    )
    
    # Notifications email
    email_enabled = models.BooleanField(
        default=True,
        verbose_name=_("Notifications email")
    )
    
    email_frequency = models.CharField(
        max_length=20,
        choices=[
            ('instant', 'Immédiat'),
            ('hourly', 'Toutes les heures'),
            ('daily', 'Quotidien'),
            ('weekly', 'Hebdomadaire'),
        ],
        default='instant',
        verbose_name=_("Fréquence des emails")
    )
    
    # Heures de silence
    quiet_hours_enabled = models.BooleanField(
        default=False,
        verbose_name=_("Heures de silence")
    )
    
    quiet_hours_start = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("Début")
    )
    
    quiet_hours_end = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("Fin")
    )
    
    # Filtres par priorité
    notify_urgent_only = models.BooleanField(
        default=False,
        verbose_name=_("Urgents uniquement")
    )
    
    # Résumé
    daily_summary = models.BooleanField(
        default=False,
        verbose_name=_("Résumé quotidien")
    )
    
    summary_time = models.TimeField(
        default='18:00',
        verbose_name=_("Heure du résumé")
    )
    
    class Meta:
        db_table = 'notification_preferences'
        verbose_name = _("Préférences de notification")
        verbose_name_plural = _("Préférences de notification")
    
    def __str__(self):
        return f"Préférences de {self.user.get_full_name()}"
    
    def should_send_notification(self, message, notification_type='push'):
        """Détermine si une notification doit être envoyée"""
        if notification_type == 'push' and not self.push_enabled:
            return False
        
        if notification_type == 'email' and not self.email_enabled:
            return False
        
        # Vérifier les heures de silence
        if self.quiet_hours_enabled:
            now = timezone.now().time()
            if self.quiet_hours_start <= now <= self.quiet_hours_end:
                return False
        
        # Vérifier la priorité
        if self.notify_urgent_only and message.priority != MessagePriority.URGENT:
            return False
        
        return True