"""
Configuration Celery pour les tâches asynchrones
"""
import os

try:
    from celery import Celery
except ImportError:
    # Celery n'est pas installé, créer une classe mock
    class Celery:
        def __init__(self, *args, **kwargs):
            pass
        def config_from_object(self, *args, **kwargs):
            pass
        def autodiscover_tasks(self, *args, **kwargs):
            pass
        def task(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
        conf = type('conf', (), {'beat_schedule': {}})()
    
    def crontab(*args, **kwargs):
        return None

# Définir les settings Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('peproscolaire')

# Charger la configuration depuis Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Découvrir automatiquement les tâches
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

try:
    from celery.schedules import crontab
except ImportError:
    pass  # crontab déjà défini plus haut

# Configuration des tâches périodiques
app.conf.beat_schedule = {
    # Vérification des alertes de présence
    'check-attendance-alerts': {
        'task': 'apps.attendance.tasks.check_attendance_alerts',
        'schedule': crontab(hour=16, minute=0),
    },
    
    # Rapport mensuel de présence
    'generate-monthly-attendance-report': {
        'task': 'apps.attendance.tasks.generate_monthly_attendance_report',
        'schedule': crontab(day_of_month=1, hour=8, minute=0),
    },
    
    # Rappels de devoirs
    'send-homework-reminders': {
        'task': 'apps.homework.tasks.send_homework_reminders',
        'schedule': crontab(hour=18, minute=0),
    },
    
    # Résumé hebdomadaire
    'generate-weekly-summary': {
        'task': 'apps.homework.tasks.generate_weekly_summary',
        'schedule': crontab(day_of_week=5, hour=17, minute=0),  # Vendredi 17h
    },
    
    # Vérification du cahier de textes
    'check-missing-lesson-content': {
        'task': 'apps.homework.tasks.check_missing_lesson_content',
        'schedule': crontab(day_of_week=1, hour=9, minute=0),  # Lundi 9h
    },
    
    # Nettoyage des brouillons
    'cleanup-draft-submissions': {
        'task': 'apps.homework.tasks.cleanup_draft_submissions',
        'schedule': crontab(day_of_month=1, hour=3, minute=0),
    },
}