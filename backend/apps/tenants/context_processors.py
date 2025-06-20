"""
Context processors pour injecter les informations du tenant dans les templates
"""
from django.conf import settings


def tenant_context(request):
    """
    Injecte les variables de personnalisation du tenant dans le contexte des templates
    """
    context = {
        'TENANT_ENABLED': True,
        'DEFAULT_THEME': {
            'primary_color': '#1976D2',
            'secondary_color': '#424242',
            'logo_url': '/static/img/default-logo.png',
            'favicon_url': '/static/img/favicon.ico',
            'school_name': 'PeproScolaire',
        }
    }
    
    if hasattr(request, 'tenant') and request.tenant:
        tenant = request.tenant
        
        # Informations du tenant
        context['tenant'] = tenant
        context['tenant_active'] = True
        
        # Thème personnalisé
        context['theme'] = {
            'primary_color': tenant.primary_color,
            'secondary_color': tenant.secondary_color,
            'logo_url': tenant.logo_url or context['DEFAULT_THEME']['logo_url'],
            'favicon_url': tenant.favicon_url or context['DEFAULT_THEME']['favicon_url'],
            'school_name': tenant.school.name,
            'school_type': tenant.school.get_school_type_display(),
        }
        
        # Modules activés
        context['modules_enabled'] = tenant.modules_enabled
        
        # Paramètres du tenant si disponibles
        if hasattr(tenant, 'settings'):
            settings_obj = tenant.settings
            context['tenant_settings'] = {
                'timezone': settings_obj.timezone,
                'language': settings_obj.language,
                'date_format': settings_obj.date_format,
                'time_format': settings_obj.time_format,
            }
    else:
        # Pas de tenant, utiliser les valeurs par défaut
        context['tenant_active'] = False
        context['theme'] = context['DEFAULT_THEME']
        context['modules_enabled'] = {
            'authentication': True,
            'schools': True,
            'timetable': True,
            'attendance': True,
            'grades': True,
            'homework': True,
            'messaging': True,
            'student_records': True,
            'ai_analytics': True,
        }
    
    return context


def tenant_urls(request):
    """
    Injecte les URLs spécifiques au tenant
    """
    urls = {}
    
    if hasattr(request, 'tenant') and request.tenant:
        tenant = request.tenant
        
        # URLs de base
        urls['tenant_home_url'] = f"https://{tenant.domain_url}/"
        urls['tenant_login_url'] = f"https://{tenant.domain_url}/login/"
        urls['tenant_logout_url'] = f"https://{tenant.domain_url}/logout/"
        
        # URLs des modules si activés
        if tenant.is_module_enabled('timetable'):
            urls['tenant_timetable_url'] = f"https://{tenant.domain_url}/timetable/"
        
        if tenant.is_module_enabled('grades'):
            urls['tenant_grades_url'] = f"https://{tenant.domain_url}/grades/"
        
        if tenant.is_module_enabled('attendance'):
            urls['tenant_attendance_url'] = f"https://{tenant.domain_url}/attendance/"
        
        if tenant.is_module_enabled('messaging'):
            urls['tenant_messaging_url'] = f"https://{tenant.domain_url}/messaging/"
    
    return {'tenant_urls': urls}


def tenant_features(request):
    """
    Injecte les fonctionnalités disponibles pour le tenant
    """
    features = {
        'has_ai_features': False,
        'has_sms_notifications': False,
        'has_email_notifications': True,
        'has_parent_portal': True,
        'has_student_portal': True,
        'has_teacher_portal': True,
        'max_file_upload_mb': 10,
    }
    
    if hasattr(request, 'tenant') and request.tenant:
        tenant = request.tenant
        
        # Fonctionnalités IA
        features['has_ai_features'] = tenant.is_module_enabled('ai_analytics')
        
        # Paramètres de notification
        if hasattr(tenant, 'settings'):
            settings_obj = tenant.settings
            features['has_sms_notifications'] = settings_obj.enable_sms_notifications
            features['has_email_notifications'] = settings_obj.enable_email_notifications
        
        # Limite de stockage
        features['max_storage_gb'] = tenant.max_storage_gb
        features['max_students'] = tenant.max_students
    
    return {'tenant_features': features}