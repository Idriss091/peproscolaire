"""
Tâches Celery pour l'analyse IA et la détection des risques
"""
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Avg, Count, Q
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def analyze_student_risk(self, risk_profile_id):
    """
    Analyser le risque d'un élève spécifique
    """
    try:
        from .models import RiskProfile, RiskIndicator
        from .analyzers import StudentRiskAnalyzer
        
        profile = RiskProfile.objects.get(id=risk_profile_id)
        logger.info(f"Début analyse de risque pour {profile.student.get_full_name()}")
        
        # Initialiser l'analyseur
        analyzer = StudentRiskAnalyzer(profile.student, profile.academic_year)
        
        # Effectuer l'analyse complète
        analysis_result = analyzer.analyze_comprehensive_risk()
        
        # Mettre à jour le profil de risque
        profile.risk_score = analysis_result['risk_score']
        profile.academic_risk = analysis_result['academic_risk']
        profile.attendance_risk = analysis_result['attendance_risk']
        profile.behavioral_risk = analysis_result['behavioral_risk']
        profile.social_risk = analysis_result['social_risk']
        profile.risk_factors = analysis_result['risk_factors']
        profile.indicators = analysis_result['indicators']
        profile.dropout_probability = analysis_result['dropout_probability']
        profile.predicted_final_average = analysis_result.get('predicted_final_average')
        profile.recommendations = analysis_result['recommendations']
        profile.priority_actions = analysis_result['priority_actions']
        
        # Calculer le niveau de risque
        profile.calculate_risk_level()
        profile.save()
        
        logger.info(f"Analyse terminée - Score: {profile.risk_score}, Niveau: {profile.risk_level}")
        
        # Vérifier si des alertes doivent être déclenchées
        check_and_send_alerts.delay(risk_profile_id)
        
        return {
            'success': True,
            'profile_id': str(profile.id),
            'risk_score': profile.risk_score,
            'risk_level': profile.risk_level
        }
        
    except Exception as exc:
        logger.error(f"Erreur lors de l'analyse de risque {risk_profile_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=2)
def analyze_class_risks(self, class_id):
    """
    Analyser les risques pour toute une classe
    """
    try:
        from apps.schools.models import Class
        from .analyzers import ClassRiskAnalyzer
        
        class_obj = Class.objects.get(id=class_id)
        logger.info(f"Début analyse de classe {class_obj}")
        
        analyzer = ClassRiskAnalyzer(class_obj)
        results = analyzer.analyze_class_risks()
        
        # Déclencher l'analyse individuelle pour chaque élève à risque
        for student_data in results.get('at_risk_students', []):
            if student_data.get('needs_analysis'):
                analyze_student_risk.delay(student_data['profile_id'])
        
        logger.info(f"Analyse de classe terminée - {len(results.get('at_risk_students', []))} élèves à risque")
        
        return {
            'success': True,
            'class_id': str(class_id),
            'students_analyzed': len(results.get('at_risk_students', [])),
            'summary': results.get('summary', {})
        }
        
    except Exception as exc:
        logger.error(f"Erreur lors de l'analyse de classe {class_id}: {exc}")
        raise self.retry(exc=exc, countdown=120)


@shared_task
def check_and_send_alerts(risk_profile_id):
    """
    Vérifier et envoyer les alertes pour un profil de risque
    """
    try:
        from .models import RiskProfile, AlertConfiguration, Alert
        
        profile = RiskProfile.objects.get(id=risk_profile_id)
        
        # Récupérer toutes les configurations d'alerte actives
        alert_configs = AlertConfiguration.objects.filter(is_active=True)
        
        for config in alert_configs:
            if config.should_trigger(profile):
                # Créer l'alerte
                alert = Alert.objects.create(
                    risk_profile=profile,
                    alert_configuration=config,
                    title=f"{config.name} - {profile.student.get_full_name()}",
                    message=config.message_template.format(
                        student_name=profile.student.get_full_name(),
                        risk_level=profile.get_risk_level_display(),
                        risk_score=profile.risk_score
                    ),
                    priority=config.priority,
                    context_data={
                        'risk_score': profile.risk_score,
                        'risk_factors': profile.risk_factors,
                        'indicators': profile.indicators
                    }
                )
                
                # Envoyer les notifications
                send_alert_notifications.delay(str(alert.id))
                
                logger.info(f"Alerte créée: {alert.title}")
        
        return {'success': True, 'profile_id': str(profile.id)}
        
    except Exception as exc:
        logger.error(f"Erreur lors de la vérification d'alertes {risk_profile_id}: {exc}")
        return {'success': False, 'error': str(exc)}


@shared_task
def send_alert_notifications(alert_id):
    """
    Envoyer les notifications pour une alerte
    """
    try:
        from .models import Alert
        from apps.messaging.models import Message
        from apps.student_records.models import Guardian
        
        alert = Alert.objects.select_related(
            'risk_profile__student',
            'alert_configuration'
        ).get(id=alert_id)
        
        config = alert.alert_configuration
        student = alert.risk_profile.student
        notifications_sent = {}
        
        # Notification à l'élève
        if config.notify_student:
            Message.objects.create(
                sender=None,  # Message système
                recipient=student,
                subject=f"Suivi personnalisé - {alert.title}",
                content=alert.message,
                message_type='system_alert',
                priority=config.priority
            )
            notifications_sent['student'] = True
        
        # Notification aux parents
        if config.notify_parents:
            guardians = Guardian.objects.filter(
                student_record__student=student,
                has_custody=True
            ).select_related('user')
            
            for guardian in guardians:
                Message.objects.create(
                    sender=None,
                    recipient=guardian.user,
                    subject=f"Alerte - {student.get_full_name()}",
                    content=f"Concernant {student.get_full_name()}: {alert.message}",
                    message_type='parent_alert',
                    priority=config.priority
                )
            
            notifications_sent['parents'] = guardians.count()
        
        # Notification au professeur principal
        if config.notify_main_teacher:
            from apps.schools.models import Enrollment
            enrollment = Enrollment.objects.filter(
                student=student,
                is_active=True
            ).select_related('class_group__main_teacher').first()
            
            if enrollment and enrollment.class_group.main_teacher:
                Message.objects.create(
                    sender=None,
                    recipient=enrollment.class_group.main_teacher,
                    subject=f"Alerte élève - {student.get_full_name()}",
                    content=alert.message,
                    message_type='teacher_alert',
                    priority=config.priority
                )
                notifications_sent['main_teacher'] = True
        
        # Notifications supplémentaires
        for recipient in config.additional_recipients.all():
            Message.objects.create(
                sender=None,
                recipient=recipient,
                subject=f"Alerte - {student.get_full_name()}",
                content=alert.message,
                message_type='system_alert',
                priority=config.priority
            )
        
        notifications_sent['additional'] = config.additional_recipients.count()
        
        # Mettre à jour l'alerte
        alert.notifications_sent = notifications_sent
        alert.save()
        
        logger.info(f"Notifications envoyées pour alerte {alert.title}")
        
        return {'success': True, 'notifications_sent': notifications_sent}
        
    except Exception as exc:
        logger.error(f"Erreur lors de l'envoi de notifications {alert_id}: {exc}")
        return {'success': False, 'error': str(exc)}


@shared_task
def daily_risk_analysis():
    """
    Analyse quotidienne de tous les profils de risque
    """
    try:
        from .models import RiskProfile
        from apps.schools.models import AcademicYear
        
        # Année scolaire actuelle
        current_year = AcademicYear.objects.filter(
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).first()
        
        if not current_year:
            logger.warning("Aucune année scolaire active trouvée")
            return {'success': False, 'error': 'No active academic year'}
        
        # Profils nécessitant une analyse
        profiles_to_analyze = RiskProfile.objects.filter(
            academic_year=current_year
        ).filter(
            Q(last_analysis__lt=timezone.now() - timedelta(days=7)) |
            Q(last_analysis__isnull=True)
        )
        
        count = 0
        for profile in profiles_to_analyze:
            analyze_student_risk.delay(str(profile.id))
            count += 1
        
        logger.info(f"Analyse quotidienne lancée pour {count} profils")
        
        return {'success': True, 'profiles_analyzed': count}
        
    except Exception as exc:
        logger.error(f"Erreur lors de l'analyse quotidienne: {exc}")
        return {'success': False, 'error': str(exc)}


@shared_task
def weekly_pattern_detection():
    """
    Détection hebdomadaire de patterns de risque
    """
    try:
        from .models import RiskProfile
        from .analyzers import PatternDetector
        
        # Profils actifs avec surveillance
        monitored_profiles = RiskProfile.objects.filter(
            is_monitored=True,
            academic_year__start_date__lte=timezone.now(),
            academic_year__end_date__gte=timezone.now()
        ).select_related('student')
        
        detector = PatternDetector()
        patterns_found = 0
        
        for profile in monitored_profiles:
            patterns = detector.detect_patterns(profile.student)
            
            if patterns:
                # Mettre à jour les indicateurs du profil
                profile.indicators.update({
                    'detected_patterns': patterns,
                    'pattern_detection_date': timezone.now().isoformat()
                })
                profile.save()
                
                # Si patterns critiques, déclencher une alerte
                if any(p.get('severity') == 'critical' for p in patterns):
                    check_and_send_alerts.delay(str(profile.id))
                
                patterns_found += 1
        
        logger.info(f"Détection de patterns terminée - {patterns_found} profils avec nouveaux patterns")
        
        return {'success': True, 'patterns_found': patterns_found}
        
    except Exception as exc:
        logger.error(f"Erreur lors de la détection de patterns: {exc}")
        return {'success': False, 'error': str(exc)}


@shared_task
def evaluate_intervention_effectiveness(intervention_plan_id):
    """
    Évaluer l'efficacité d'un plan d'intervention
    """
    try:
        from .models import InterventionPlan
        from .analyzers import InterventionAnalyzer
        
        plan = InterventionPlan.objects.get(id=intervention_plan_id)
        analyzer = InterventionAnalyzer(plan)
        
        # Analyser l'efficacité
        effectiveness = analyzer.evaluate_effectiveness()
        
        # Mettre à jour le plan si l'évaluation automatique est concluante
        if effectiveness.get('auto_score'):
            plan.effectiveness_score = effectiveness['auto_score']
            plan.outcomes = effectiveness.get('summary', '')
            plan.save()
        
        # Si l'intervention est très efficace, proposer de la dupliquer
        if effectiveness.get('auto_score', 0) >= 8:
            suggest_intervention_replication.delay(str(plan.id))
        
        logger.info(f"Évaluation d'efficacité terminée pour {plan.title}")
        
        return {'success': True, 'effectiveness': effectiveness}
        
    except Exception as exc:
        logger.error(f"Erreur lors de l'évaluation d'intervention {intervention_plan_id}: {exc}")
        return {'success': False, 'error': str(exc)}


@shared_task
def suggest_intervention_replication(successful_plan_id):
    """
    Suggérer la réplication d'une intervention réussie
    """
    try:
        from .models import InterventionPlan, RiskProfile
        
        successful_plan = InterventionPlan.objects.get(id=successful_plan_id)
        
        # Trouver des profils similaires qui pourraient bénéficier de cette intervention
        similar_profiles = RiskProfile.objects.filter(
            risk_level=successful_plan.risk_profile.risk_level,
            is_monitored=True,
            intervention_plans__isnull=True
        ).exclude(id=successful_plan.risk_profile.id)
        
        suggestions = []
        for profile in similar_profiles[:5]:  # Limiter à 5 suggestions
            similarity_score = calculate_profile_similarity(
                successful_plan.risk_profile, 
                profile
            )
            
            if similarity_score > 0.7:  # Seuil de similarité
                suggestions.append({
                    'profile_id': str(profile.id),
                    'student_name': profile.student.get_full_name(),
                    'similarity_score': similarity_score,
                    'recommended_plan': {
                        'title': f"Plan inspiré de: {successful_plan.title}",
                        'description': successful_plan.description,
                        'objectives': successful_plan.objectives,
                        'planned_actions': successful_plan.planned_actions
                    }
                })
        
        # Enregistrer les suggestions pour les coordinateurs
        if suggestions:
            from apps.messaging.models import Message
            from django.contrib.auth import get_user_model
            
            User = get_user_model()
            coordinators = User.objects.filter(
                user_type='teacher',
                is_active=True
            )
            
            for coordinator in coordinators:
                Message.objects.create(
                    sender=None,
                    recipient=coordinator,
                    subject="Suggestions de réplication d'intervention",
                    content=f"Une intervention réussie ({successful_plan.title}) pourrait être adaptée pour {len(suggestions)} autres élèves.",
                    message_type='suggestion',
                    priority='normal',
                    metadata={'suggestions': suggestions}
                )
        
        logger.info(f"Suggestions de réplication créées: {len(suggestions)}")
        
        return {'success': True, 'suggestions_count': len(suggestions)}
        
    except Exception as exc:
        logger.error(f"Erreur lors de la suggestion de réplication {successful_plan_id}: {exc}")
        return {'success': False, 'error': str(exc)}


def calculate_profile_similarity(profile1, profile2):
    """
    Calculer la similarité entre deux profils de risque
    """
    try:
        # Facteurs de risque
        risk_factors_similarity = 0
        for factor in ['academic_risk', 'attendance_risk', 'behavioral_risk', 'social_risk']:
            val1 = getattr(profile1, factor)
            val2 = getattr(profile2, factor)
            risk_factors_similarity += 1 - abs(val1 - val2) / 100
        
        risk_factors_similarity /= 4
        
        # Indicateurs communs
        indicators1 = set(profile1.indicators.keys())
        indicators2 = set(profile2.indicators.keys())
        
        if indicators1 or indicators2:
            common_indicators = len(indicators1.intersection(indicators2))
            total_indicators = len(indicators1.union(indicators2))
            indicators_similarity = common_indicators / total_indicators
        else:
            indicators_similarity = 0
        
        # Score final pondéré
        final_score = (risk_factors_similarity * 0.7) + (indicators_similarity * 0.3)
        
        return final_score
        
    except Exception:
        return 0


@shared_task
def cleanup_old_alerts():
    """
    Nettoyer les anciennes alertes
    """
    try:
        from .models import Alert
        
        # Supprimer les alertes lues de plus de 30 jours
        cutoff_date = timezone.now() - timedelta(days=30)
        
        old_alerts = Alert.objects.filter(
            is_acknowledged=True,
            acknowledged_at__lt=cutoff_date
        )
        
        count = old_alerts.count()
        old_alerts.delete()
        
        logger.info(f"Nettoyage terminé: {count} anciennes alertes supprimées")
        
        return {'success': True, 'deleted_count': count}
        
    except Exception as exc:
        logger.error(f"Erreur lors du nettoyage: {exc}")
        return {'success': False, 'error': str(exc)}


@shared_task(bind=True, max_retries=1)
def train_ml_model(self, model_type='dropout_risk', force_retrain=False):
    """
    Entraîner ou ré-entraîner un modèle ML
    """
    try:
        from .ml_models import ModelTrainer
        
        trainer = ModelTrainer()
        
        logger.info(f"Début entraînement modèle {model_type}")
        
        if model_type == 'dropout_risk':
            if force_retrain:
                result = trainer.train_dropout_model()
            else:
                result = trainer.retrain_if_needed()
        else:
            return {'success': False, 'error': 'Type de modèle non supporté'}
        
        if result.get('success'):
            logger.info(f"Entraînement réussi: {result.get('metrics', {})}")
        else:
            logger.info(f"Entraînement non nécessaire: {result.get('reason', 'Unknown')}")
        
        return result
        
    except Exception as exc:
        logger.error(f"Erreur lors de l'entraînement du modèle {model_type}: {exc}")
        raise self.retry(exc=exc, countdown=300)  # Retry après 5 minutes


@shared_task
def weekly_model_evaluation():
    """
    Évaluation hebdomadaire des modèles ML
    """
    try:
        from .ml_models import ModelTrainer
        
        trainer = ModelTrainer()
        
        # Évaluer les performances du modèle de décrochage
        performance = trainer.evaluate_model_performance()
        
        if 'error' not in performance:
            logger.info(f"Évaluation modèle: Accuracy={performance.get('accuracy', 0):.3f}, "
                       f"F1={performance.get('f1_score', 0):.3f}")
            
            # Si performances dégradées, programmer un ré-entraînement
            if performance.get('f1_score', 0) < 0.75:
                train_ml_model.delay('dropout_risk', force_retrain=True)
                logger.info("Performances dégradées, ré-entraînement programmé")
        
        return {'success': True, 'performance': performance}
        
    except Exception as exc:
        logger.error(f"Erreur lors de l'évaluation hebdomadaire: {exc}")
        return {'success': False, 'error': str(exc)}


@shared_task
def create_risk_profiles_for_new_students():
    """
    Créer des profils de risque pour les nouveaux élèves
    """
    try:
        from .models import RiskProfile
        from apps.schools.models import Enrollment, AcademicYear
        from django.utils import timezone
        
        # Année scolaire actuelle
        current_year = AcademicYear.objects.filter(
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).first()
        
        if not current_year:
            return {'success': False, 'error': 'No active academic year'}
        
        # Élèves sans profil de risque
        enrollments_without_profile = Enrollment.objects.filter(
            academic_year=current_year,
            is_active=True
        ).exclude(
            student__risk_profiles__academic_year=current_year
        ).select_related('student')
        
        created_count = 0
        
        for enrollment in enrollments_without_profile:
            student = enrollment.student
            
            # Créer un profil de risque initial
            profile, created = RiskProfile.objects.get_or_create(
                student=student,
                academic_year=current_year,
                defaults={
                    'risk_score': 0.0,
                    'risk_level': 'low',
                    'academic_risk': 0.0,
                    'attendance_risk': 0.0,
                    'behavioral_risk': 0.0,
                    'social_risk': 0.0,
                    'risk_factors': {},
                    'indicators': {},
                    'dropout_probability': 0.0,
                    'recommendations': [],
                    'priority_actions': []
                }
            )
            
            if created:
                # Programmer l'analyse du nouveau profil
                analyze_student_risk.delay(str(profile.id))
                created_count += 1
        
        logger.info(f"Profils de risque créés pour {created_count} nouveaux élèves")
        
        return {'success': True, 'profiles_created': created_count}
        
    except Exception as exc:
        logger.error(f"Erreur lors de la création de profils: {exc}")
        return {'success': False, 'error': str(exc)}


@shared_task
def update_model_performance_metrics():
    """
    Mettre à jour les métriques de performance du modèle pour le dashboard
    """
    try:
        from .ml_models import ModelTrainer
        
        trainer = ModelTrainer()
        
        # Évaluer les performances actuelles
        performance = trainer.evaluate_model_performance()
        
        if 'error' in performance:
            return {'success': False, 'error': performance['error']}
        
        # Stocker les métriques dans un cache ou base de données
        # Pour l'instant, on va les mettre dans les settings ou cache Django
        from django.core.cache import cache
        
        cache.set('ai_model_performance', performance, timeout=86400)  # 24h
        
        # Calculer des statistiques additionnelles
        from .models import RiskProfile
        from django.utils import timezone
        from django.db.models import Count, Avg
        
        current_year_profiles = RiskProfile.objects.filter(
            academic_year__start_date__lte=timezone.now(),
            academic_year__end_date__gte=timezone.now()
        )
        
        risk_distribution = current_year_profiles.values('risk_level').annotate(
            count=Count('id')
        )
        
        avg_risk_score = current_year_profiles.aggregate(
            avg_score=Avg('risk_score')
        )['avg_score'] or 0
        
        dashboard_metrics = {
            'model_performance': performance,
            'risk_distribution': {item['risk_level']: item['count'] for item in risk_distribution},
            'average_risk_score': float(avg_risk_score),
            'total_profiles': current_year_profiles.count(),
            'high_risk_count': current_year_profiles.filter(risk_level__in=['high', 'critical']).count(),
            'last_update': timezone.now().isoformat()
        }
        
        cache.set('ai_dashboard_metrics', dashboard_metrics, timeout=3600)  # 1h
        
        logger.info(f"Métriques dashboard mises à jour: {dashboard_metrics['total_profiles']} profils")
        
        return {'success': True, 'metrics': dashboard_metrics}
        
    except Exception as exc:
        logger.error(f"Erreur lors de la mise à jour des métriques: {exc}")
        return {'success': False, 'error': str(exc)}