"""
Modèles pour la gestion des dossiers élèves
"""
from django.db import models
from django.core.validators import RegexValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from apps.core.models import BaseModel
from apps.authentication.models import User
from apps.schools.models import School, Class, AcademicYear


class StudentRecord(BaseModel):
    """
    Dossier principal de l'élève
    """
    student = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_record',
        limit_choices_to={'user_type': 'student'}
    )
    
    # Numéro d'identification national
    national_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("INE (Identifiant National Élève)")
    )
    
    # Informations de naissance
    birth_certificate_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Numéro d'acte de naissance")
    )
    birth_place = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Lieu de naissance")
    )
    birth_country = models.CharField(
        max_length=100,
        default='France',
        verbose_name=_("Pays de naissance")
    )
    nationality = models.CharField(
        max_length=100,
        default='Française',
        verbose_name=_("Nationalité")
    )
    
    # Situation familiale
    family_situation = models.CharField(
        max_length=30,
        choices=[
            ('parents_together', 'Parents ensemble'),
            ('separated', 'Parents séparés'),
            ('divorced', 'Parents divorcés'),
            ('single_parent', 'Famille monoparentale'),
            ('guardian', 'Sous tutelle'),
            ('foster', 'Famille d\'accueil'),
            ('other', 'Autre'),
        ],
        default='parents_together',
        verbose_name=_("Situation familiale")
    )
    
    siblings_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Nombre de frères et sœurs")
    )
    
    # Informations scolaires
    entry_date = models.DateField(
        verbose_name=_("Date d'entrée dans l'établissement")
    )
    
    previous_school = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Établissement précédent")
    )
    
    # Options et spécialités
    options = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True,
        verbose_name=_("Options suivies")
    )
    
    specialties = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True,
        verbose_name=_("Spécialités")
    )
    
    # Besoins particuliers
    has_special_needs = models.BooleanField(
        default=False,
        verbose_name=_("Besoins éducatifs particuliers")
    )
    
    special_needs_details = models.TextField(
        blank=True,
        verbose_name=_("Détails des besoins particuliers")
    )
    
    has_disability = models.BooleanField(
        default=False,
        verbose_name=_("Situation de handicap")
    )
    
    disability_details = models.TextField(
        blank=True,
        verbose_name=_("Détails du handicap")
    )
    
    # PAI, PAP, PPS
    has_pai = models.BooleanField(
        default=False,
        verbose_name=_("PAI (Projet d'Accueil Individualisé)")
    )
    
    has_pap = models.BooleanField(
        default=False,
        verbose_name=_("PAP (Plan d'Accompagnement Personnalisé)")
    )
    
    has_pps = models.BooleanField(
        default=False,
        verbose_name=_("PPS (Projet Personnalisé de Scolarisation)")
    )
    
    # Transport
    uses_school_transport = models.BooleanField(
        default=False,
        verbose_name=_("Utilise le transport scolaire")
    )
    
    transport_line = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Ligne de transport")
    )
    
    # Restauration
    lunch_type = models.CharField(
        max_length=20,
        choices=[
            ('none', 'Externe'),
            ('cafeteria', 'Demi-pensionnaire'),
            ('packed', 'Panier repas'),
            ('boarding', 'Interne'),
        ],
        default='cafeteria',
        verbose_name=_("Régime")
    )
    
    dietary_restrictions = models.TextField(
        blank=True,
        verbose_name=_("Restrictions alimentaires")
    )
    
    # Autorisations
    photo_authorization = models.BooleanField(
        default=False,
        verbose_name=_("Autorisation droit à l'image")
    )
    
    leave_alone_authorization = models.BooleanField(
        default=False,
        verbose_name=_("Autorisation de sortie seul")
    )
    
    # Notes administratives
    administrative_notes = models.TextField(
        blank=True,
        verbose_name=_("Notes administratives")
    )
    
    # Statut
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Dossier actif")
    )
    
    graduation_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Date de sortie")
    )
    
    graduation_reason = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('graduated', 'Diplômé'),
            ('transferred', 'Mutation'),
            ('dropped_out', 'Abandon'),
            ('excluded', 'Exclusion'),
            ('other', 'Autre'),
        ],
        verbose_name=_("Motif de sortie")
    )
    
    class Meta:
        db_table = 'student_records'
        verbose_name = _("Dossier élève")
        verbose_name_plural = _("Dossiers élèves")
    
    def __str__(self):
        return f"Dossier de {self.student.get_full_name()}"
    
    def get_age(self):
        """Calculer l'âge de l'élève"""
        if hasattr(self.student, 'profile') and self.student.profile.date_of_birth:
            today = timezone.now().date()
            birth_date = self.student.profile.date_of_birth
            age = today.year - birth_date.year
            if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
                age -= 1
            return age
        return None


class Guardian(BaseModel):
    """
    Responsable légal de l'élève
    """
    RELATIONSHIP_CHOICES = [
        ('mother', 'Mère'),
        ('father', 'Père'),
        ('stepmother', 'Belle-mère'),
        ('stepfather', 'Beau-père'),
        ('grandmother', 'Grand-mère'),
        ('grandfather', 'Grand-père'),
        ('aunt', 'Tante'),
        ('uncle', 'Oncle'),
        ('guardian', 'Tuteur/Tutrice'),
        ('other', 'Autre'),
    ]
    
    student_record = models.ForeignKey(
        StudentRecord,
        on_delete=models.CASCADE,
        related_name='guardians'
    )
    
    # Lien avec un compte utilisateur si existant
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='guardian_profiles',
        limit_choices_to={'user_type': 'parent'}
    )
    
    # Informations personnelles
    first_name = models.CharField(
        max_length=100,
        verbose_name=_("Prénom")
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name=_("Nom")
    )
    relationship = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_CHOICES,
        verbose_name=_("Lien de parenté")
    )
    
    # Contact
    email = models.EmailField(
        verbose_name=_("Email")
    )
    phone = models.CharField(
        max_length=17,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        verbose_name=_("Téléphone")
    )
    mobile_phone = models.CharField(
        max_length=17,
        blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        verbose_name=_("Téléphone portable")
    )
    work_phone = models.CharField(
        max_length=17,
        blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        verbose_name=_("Téléphone professionnel")
    )
    
    # Adresse
    address = models.TextField(
        verbose_name=_("Adresse")
    )
    postal_code = models.CharField(
        max_length=10,
        verbose_name=_("Code postal")
    )
    city = models.CharField(
        max_length=100,
        verbose_name=_("Ville")
    )
    
    # Informations professionnelles
    profession = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Profession")
    )
    employer = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Employeur")
    )
    
    # Droits et responsabilités
    has_custody = models.BooleanField(
        default=True,
        verbose_name=_("Autorité parentale")
    )
    is_primary_contact = models.BooleanField(
        default=False,
        verbose_name=_("Contact principal")
    )
    receives_mail = models.BooleanField(
        default=True,
        verbose_name=_("Reçoit le courrier")
    )
    can_pickup = models.BooleanField(
        default=True,
        verbose_name=_("Autorisé à récupérer l'enfant")
    )
    
    # Notes
    notes = models.TextField(
        blank=True,
        verbose_name=_("Notes")
    )
    
    class Meta:
        db_table = 'guardians'
        verbose_name = _("Responsable légal")
        verbose_name_plural = _("Responsables légaux")
        ordering = ['-is_primary_contact', 'relationship']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_relationship_display()})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def clean(self):
        # S'assurer qu'il y a au moins un contact principal
        if not self.is_primary_contact:
            primary_exists = Guardian.objects.filter(
                student_record=self.student_record,
                is_primary_contact=True
            ).exclude(pk=self.pk).exists()
            
            if not primary_exists:
                self.is_primary_contact = True


class EmergencyContact(BaseModel):
    """
    Contact d'urgence
    """
    student_record = models.ForeignKey(
        StudentRecord,
        on_delete=models.CASCADE,
        related_name='emergency_contacts'
    )
    
    name = models.CharField(
        max_length=200,
        verbose_name=_("Nom complet")
    )
    
    relationship = models.CharField(
        max_length=100,
        verbose_name=_("Lien avec l'élève")
    )
    
    phone = models.CharField(
        max_length=17,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        verbose_name=_("Téléphone")
    )
    
    priority = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Ordre de priorité")
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_("Notes")
    )
    
    class Meta:
        db_table = 'emergency_contacts'
        verbose_name = _("Contact d'urgence")
        verbose_name_plural = _("Contacts d'urgence")
        ordering = ['priority']
    
    def __str__(self):
        return f"{self.name} ({self.relationship})"


class MedicalRecord(BaseModel):
    """
    Dossier médical de l'élève
    """
    student_record = models.OneToOneField(
        StudentRecord,
        on_delete=models.CASCADE,
        related_name='medical_record'
    )
    
    # Informations médicales générales
    blood_type = models.CharField(
        max_length=10,
        blank=True,
        choices=[
            ('A+', 'A+'), ('A-', 'A-'),
            ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'),
            ('O+', 'O+'), ('O-', 'O-'),
        ],
        verbose_name=_("Groupe sanguin")
    )
    
    height = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Taille (cm)")
    )
    
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Poids (kg)")
    )
    
    last_medical_check = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Dernière visite médicale")
    )
    
    # Médecin traitant
    doctor_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Médecin traitant")
    )
    
    doctor_phone = models.CharField(
        max_length=17,
        blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        verbose_name=_("Téléphone médecin")
    )
    
    # Conditions médicales
    chronic_conditions = models.TextField(
        blank=True,
        verbose_name=_("Maladies chroniques")
    )
    
    allergies = models.TextField(
        blank=True,
        verbose_name=_("Allergies")
    )
    
    medications = models.TextField(
        blank=True,
        verbose_name=_("Traitements en cours")
    )
    
    # Vaccinations
    vaccinations_up_to_date = models.BooleanField(
        default=True,
        verbose_name=_("Vaccinations à jour")
    )
    
    vaccination_details = models.TextField(
        blank=True,
        verbose_name=_("Détails vaccinations")
    )
    
    # Restrictions et recommandations
    physical_restrictions = models.TextField(
        blank=True,
        verbose_name=_("Restrictions physiques")
    )
    
    emergency_protocol = models.TextField(
        blank=True,
        verbose_name=_("Protocole d'urgence")
    )
    
    # Assurance
    insurance_company = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Compagnie d'assurance")
    )
    
    insurance_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Numéro d'assurance")
    )
    
    # Confidentialité
    confidential_notes = models.TextField(
        blank=True,
        verbose_name=_("Notes confidentielles"),
        help_text=_("Visible uniquement par l'infirmerie et l'administration")
    )
    
    class Meta:
        db_table = 'medical_records'
        verbose_name = _("Dossier médical")
        verbose_name_plural = _("Dossiers médicaux")
    
    def __str__(self):
        return f"Dossier médical de {self.student_record.student.get_full_name()}"


class StudentDocument(BaseModel):
    """
    Document du dossier élève
    """
    DOCUMENT_TYPE_CHOICES = [
        # Documents administratifs
        ('birth_certificate', 'Acte de naissance'),
        ('id_card', 'Carte d\'identité'),
        ('passport', 'Passeport'),
        ('residence_proof', 'Justificatif de domicile'),
        ('family_record', 'Livret de famille'),
        
        # Documents scolaires
        ('report_card', 'Bulletin scolaire'),
        ('transcript', 'Relevé de notes'),
        ('diploma', 'Diplôme'),
        ('certificate', 'Certificat de scolarité'),
        ('transfer_form', 'Exeat'),
        
        # Documents médicaux
        ('medical_certificate', 'Certificat médical'),
        ('vaccination_record', 'Carnet de vaccination'),
        ('pai_document', 'Document PAI'),
        ('pap_document', 'Document PAP'),
        ('pps_document', 'Document PPS'),
        
        # Autorisations
        ('photo_authorization', 'Autorisation photo'),
        ('trip_authorization', 'Autorisation de sortie'),
        ('pickup_authorization', 'Autorisation de prise en charge'),
        
        # Autres
        ('insurance', 'Attestation d\'assurance'),
        ('scholarship', 'Dossier de bourse'),
        ('other', 'Autre'),
    ]
    
    student_record = models.ForeignKey(
        StudentRecord,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    
    document_type = models.CharField(
        max_length=30,
        choices=DOCUMENT_TYPE_CHOICES,
        verbose_name=_("Type de document")
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name=_("Titre")
    )
    
    description = models.TextField(
        blank=True,
        verbose_name=_("Description")
    )
    
    file = models.FileField(
        upload_to='student_documents/%Y/%m/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'jpg', 'jpeg', 'png']
            )
        ],
        verbose_name=_("Fichier")
    )
    
    # Période de validité
    issue_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Date d'émission")
    )
    
    expiry_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Date d'expiration")
    )
    
    # Métadonnées
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_student_documents'
    )
    
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_("Document vérifié")
    )
    
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_student_documents'
    )
    
    verified_at = models.DateTimeField(
        null=True,
        blank=True
    )
    
    # Confidentialité
    is_confidential = models.BooleanField(
        default=False,
        verbose_name=_("Document confidentiel")
    )
    
    class Meta:
        db_table = 'student_documents'
        verbose_name = _("Document élève")
        verbose_name_plural = _("Documents élèves")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.student_record.student.get_full_name()}"
    
    @property
    def is_expired(self):
        """Vérifie si le document est expiré"""
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False
    
    @property
    def size_mb(self):
        """Taille du fichier en MB"""
        if self.file:
            return round(self.file.size / (1024 * 1024), 2)
        return None


class ScholarshipRecord(BaseModel):
    """
    Dossier de bourse
    """
    student_record = models.ForeignKey(
        StudentRecord,
        on_delete=models.CASCADE,
        related_name='scholarships'
    )
    
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='scholarships'
    )
    
    scholarship_type = models.CharField(
        max_length=50,
        choices=[
            ('national', 'Bourse nationale'),
            ('regional', 'Bourse régionale'),
            ('departmental', 'Bourse départementale'),
            ('merit', 'Bourse au mérite'),
            ('social', 'Aide sociale'),
            ('other', 'Autre'),
        ],
        verbose_name=_("Type de bourse")
    )
    
    amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name=_("Montant annuel")
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'En attente'),
            ('approved', 'Accordée'),
            ('rejected', 'Refusée'),
            ('cancelled', 'Annulée'),
        ],
        default='pending',
        verbose_name=_("Statut")
    )
    
    application_date = models.DateField(
        verbose_name=_("Date de demande")
    )
    
    decision_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Date de décision")
    )
    
    reference_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Numéro de dossier")
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_("Notes")
    )
    
    class Meta:
        db_table = 'scholarship_records'
        verbose_name = _("Dossier de bourse")
        verbose_name_plural = _("Dossiers de bourse")
        unique_together = ['student_record', 'academic_year', 'scholarship_type']
        ordering = ['-academic_year', '-application_date']
    
    def __str__(self):
        return f"{self.get_scholarship_type_display()} - {self.student_record.student.get_full_name()}"


class DisciplinaryRecord(BaseModel):
    """
    Dossier disciplinaire (vue consolidée)
    """
    student_record = models.ForeignKey(
        StudentRecord,
        on_delete=models.CASCADE,
        related_name='disciplinary_records'
    )
    
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='disciplinary_records'
    )
    
    # Résumé des sanctions
    total_warnings = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Avertissements")
    )
    
    total_detentions = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Retenues")
    )
    
    total_exclusions = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Exclusions")
    )
    
    # Conseil de discipline
    has_disciplinary_council = models.BooleanField(
        default=False,
        verbose_name=_("Passage en conseil de discipline")
    )
    
    council_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Date du conseil")
    )
    
    council_decision = models.TextField(
        blank=True,
        verbose_name=_("Décision du conseil")
    )
    
    # Suivi
    improvement_plan = models.TextField(
        blank=True,
        verbose_name=_("Plan d'amélioration")
    )
    
    tutor_assigned = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tutored_students',
        limit_choices_to={'user_type': 'teacher'},
        verbose_name=_("Tuteur assigné")
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_("Notes de suivi")
    )
    
    class Meta:
        db_table = 'disciplinary_records'
        verbose_name = _("Dossier disciplinaire")
        verbose_name_plural = _("Dossiers disciplinaires")
        unique_together = ['student_record', 'academic_year']
        ordering = ['-academic_year']
    
    def __str__(self):
        return f"Dossier disciplinaire {self.academic_year} - {self.student_record.student.get_full_name()}"
    
    def update_counts(self):
        """Mettre à jour les compteurs depuis le module attendance"""
        from apps.attendance.models import Sanction
        
        sanctions = Sanction.objects.filter(
            student=self.student_record.student,
            date__range=[
                self.academic_year.start_date,
                self.academic_year.end_date
            ]
        )
        
        self.total_warnings = sanctions.filter(
            sanction_type__in=['warning', 'blame']
        ).count()
        
        self.total_detentions = sanctions.filter(
            sanction_type='detention'
        ).count()
        
        self.total_exclusions = sanctions.filter(
            sanction_type__in=['exclusion_temp', 'exclusion_def']
        ).count()
        
        self.save()


class OrientationRecord(BaseModel):
    """
    Dossier d'orientation
    """
    student_record = models.ForeignKey(
        StudentRecord,
        on_delete=models.CASCADE,
        related_name='orientation_records'
    )
    
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='orientation_records'
    )
    
    current_level = models.CharField(
        max_length=50,
        verbose_name=_("Niveau actuel")
    )
    
    # Souhaits de l'élève
    student_wishes = models.JSONField(
        default=list,
        verbose_name=_("Vœux de l'élève"),
        help_text=_("Liste ordonnée des vœux")
    )
    
    # Avis du conseil de classe
    class_council_opinion = models.TextField(
        blank=True,
        verbose_name=_("Avis du conseil de classe")
    )
    
    recommended_orientation = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Orientation recommandée")
    )
    
    # Décision finale
    final_decision = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Décision finale")
    )
    
    decision_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Date de décision")
    )
    
    # Appel
    has_appeal = models.BooleanField(
        default=False,
        verbose_name=_("Appel déposé")
    )
    
    appeal_decision = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Décision d'appel")
    )
    
    # Documents joints
    meeting_report = models.FileField(
        upload_to='orientation/%Y/',
        null=True,
        blank=True,
        verbose_name=_("Compte-rendu d'entretien")
    )
    
    # Suivi post-orientation
    next_school = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Établissement d'affectation")
    )
    
    next_program = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Formation suivie")
    )
    
    class Meta:
        db_table = 'orientation_records'
        verbose_name = _("Dossier d'orientation")
        verbose_name_plural = _("Dossiers d'orientation")
        unique_together = ['student_record', 'academic_year']
        ordering = ['-academic_year']
    
    def __str__(self):
        return f"Orientation {self.academic_year} - {self.student_record.student.get_full_name()}"