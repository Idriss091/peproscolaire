import django_filters
from django.db.models import Q
from .models import InternshipOffer, Internship, Company


class InternshipOfferFilter(django_filters.FilterSet):
    """
    Filtres pour les offres de stage
    """
    # Filtrage par texte
    search = django_filters.CharFilter(method='filter_search', label='Recherche')
    
    # Filtrage par entreprise
    company_name = django_filters.CharFilter(
        field_name='company__name', 
        lookup_expr='icontains',
        label='Nom entreprise'
    )
    company_sector = django_filters.ChoiceFilter(
        field_name='company__sector',
        choices=Company.SECTORS,
        label='Secteur'
    )
    company_size = django_filters.ChoiceFilter(
        field_name='company__size',
        choices=Company.COMPANY_SIZES,
        label='Taille entreprise'
    )
    city = django_filters.CharFilter(
        field_name='company__city',
        lookup_expr='icontains',
        label='Ville'
    )
    
    # Filtrage par dates
    start_date_from = django_filters.DateFilter(
        field_name='start_date',
        lookup_expr='gte',
        label='Début à partir de'
    )
    start_date_to = django_filters.DateFilter(
        field_name='start_date',
        lookup_expr='lte',
        label='Début jusqu\'à'
    )
    application_deadline_from = django_filters.DateFilter(
        field_name='application_deadline',
        lookup_expr='gte',
        label='Date limite à partir de'
    )
    
    # Filtrage par durée
    duration_min = django_filters.NumberFilter(method='filter_duration_min')
    duration_max = django_filters.NumberFilter(method='filter_duration_max')
    
    # Filtrage par conditions
    is_paid = django_filters.BooleanFilter(label='Rémunéré')
    remote_possible = django_filters.BooleanFilter(label='Télétravail possible')
    transport_provided = django_filters.BooleanFilter(label='Transport fourni')
    meal_vouchers = django_filters.BooleanFilter(label='Tickets restaurant')
    accommodation_help = django_filters.BooleanFilter(label='Aide logement')
    
    # Filtrage par partenariat
    partner_companies_only = django_filters.BooleanFilter(
        method='filter_partner_companies',
        label='Entreprises partenaires uniquement'
    )
    
    # Filtrage par disponibilité
    available_only = django_filters.BooleanFilter(
        method='filter_available_only',
        label='Offres disponibles uniquement'
    )
    
    class Meta:
        model = InternshipOffer
        fields = [
            'offer_type', 'status', 'duration_type', 'required_level',
            'department'
        ]
    
    def filter_search(self, queryset, name, value):
        """Recherche dans plusieurs champs"""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(company__name__icontains=value) |
            Q(department__icontains=value) |
            Q(supervisor_name__icontains=value)
        )
    
    def filter_duration_min(self, queryset, name, value):
        """Filtre par durée minimum en semaines"""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(duration_type='weeks', duration_value__gte=value) |
            Q(duration_type='months', duration_value__gte=value/4) |
            Q(duration_type='days', duration_value__gte=value*7)
        )
    
    def filter_duration_max(self, queryset, name, value):
        """Filtre par durée maximum en semaines"""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(duration_type='weeks', duration_value__lte=value) |
            Q(duration_type='months', duration_value__lte=value/4) |
            Q(duration_type='days', duration_value__lte=value*7)
        )
    
    def filter_partner_companies(self, queryset, name, value):
        """Filtre les entreprises partenaires uniquement"""
        if value:
            return queryset.filter(company__is_partner=True)
        return queryset
    
    def filter_available_only(self, queryset, name, value):
        """Filtre les offres encore disponibles"""
        if value:
            return queryset.filter(
                status='published',
                current_applications__lt=F('max_applications')
            )
        return queryset


class InternshipFilter(django_filters.FilterSet):
    """
    Filtres pour les stages
    """
    # Filtrage par dates
    start_date_from = django_filters.DateFilter(
        field_name='start_date',
        lookup_expr='gte',
        label='Début à partir de'
    )
    start_date_to = django_filters.DateFilter(
        field_name='start_date',
        lookup_expr='lte',
        label='Début jusqu\'à'
    )
    end_date_from = django_filters.DateFilter(
        field_name='end_date',
        lookup_expr='gte',
        label='Fin à partir de'
    )
    end_date_to = django_filters.DateFilter(
        field_name='end_date',
        lookup_expr='lte',
        label='Fin jusqu\'à'
    )
    
    # Filtrage par entreprise
    company_name = django_filters.CharFilter(
        field_name='company__name',
        lookup_expr='icontains',
        label='Nom entreprise'
    )
    company_sector = django_filters.ChoiceFilter(
        field_name='company__sector',
        choices=Company.SECTORS,
        label='Secteur'
    )
    city = django_filters.CharFilter(
        field_name='company__city',
        lookup_expr='icontains',
        label='Ville'
    )
    
    # Filtrage par supervision
    academic_supervisor = django_filters.ModelChoiceFilter(
        queryset=None,  # Sera défini dans __init__
        label='Tuteur académique'
    )
    company_supervisor = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Tuteur entreprise'
    )
    
    # Filtrage par évaluation
    min_student_rating = django_filters.NumberFilter(
        field_name='student_rating',
        lookup_expr='gte',
        label='Note étudiant minimum'
    )
    min_company_rating = django_filters.NumberFilter(
        field_name='company_rating',
        lookup_expr='gte',
        label='Note entreprise minimum'
    )
    
    # Filtrage par progression
    min_progress = django_filters.NumberFilter(
        field_name='progress_percentage',
        lookup_expr='gte',
        label='Progression minimum (%)'
    )
    
    # Filtrage par année scolaire
    academic_year = django_filters.CharFilter(
        method='filter_academic_year',
        label='Année scolaire (ex: 2023-2024)'
    )
    
    class Meta:
        model = Internship
        fields = ['status']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Définir le queryset pour academic_supervisor basé sur l'utilisateur connecté
        if hasattr(self, 'request') and self.request.user.is_authenticated:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Filtrer les superviseurs académiques (enseignants)
            self.filters['academic_supervisor'].queryset = User.objects.filter(
                profile__role='teacher'
            )
    
    def filter_academic_year(self, queryset, name, value):
        """Filtre par année scolaire (ex: 2023-2024)"""
        if not value:
            return queryset
        
        try:
            # Extraire les années de début et fin
            start_year, end_year = value.split('-')
            start_year = int(start_year)
            end_year = int(end_year)
            
            # Définir les dates de l'année scolaire (septembre à juin)
            from datetime import date
            academic_start = date(start_year, 9, 1)
            academic_end = date(end_year, 6, 30)
            
            return queryset.filter(
                start_date__gte=academic_start,
                start_date__lte=academic_end
            )
        except (ValueError, TypeError):
            return queryset


class CompanyFilter(django_filters.FilterSet):
    """
    Filtres pour les entreprises
    """
    # Filtrage par texte
    search = django_filters.CharFilter(method='filter_search', label='Recherche')
    
    # Filtrage géographique
    city = django_filters.CharFilter(lookup_expr='icontains', label='Ville')
    postal_code = django_filters.CharFilter(
        lookup_expr='istartswith',
        label='Code postal'
    )
    country = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Pays'
    )
    
    # Filtrage par partenariat
    partnership_since_from = django_filters.DateFilter(
        field_name='partnership_since',
        lookup_expr='gte',
        label='Partenaire depuis'
    )
    
    # Filtrage par performance
    min_rating = django_filters.NumberFilter(
        field_name='average_rating',
        lookup_expr='gte',
        label='Note minimum'
    )
    min_internships = django_filters.NumberFilter(
        field_name='total_internships',
        lookup_expr='gte',
        label='Nombre minimum de stages'
    )
    
    # Filtrage par statut
    has_active_offers = django_filters.BooleanFilter(
        method='filter_has_active_offers',
        label='A des offres actives'
    )
    
    class Meta:
        model = Company
        fields = ['sector', 'size', 'is_partner', 'is_active']
    
    def filter_search(self, queryset, name, value):
        """Recherche dans plusieurs champs"""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(contact_person__icontains=value) |
            Q(contact_email__icontains=value)
        )
    
    def filter_has_active_offers(self, queryset, name, value):
        """Filtre les entreprises avec des offres actives"""
        if value:
            return queryset.filter(
                offers__status='published',
                offers__application_deadline__gte=timezone.now().date()
            ).distinct()
        return queryset