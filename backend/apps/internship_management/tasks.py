from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import logging

from .models import (
    InternshipOffer, InternshipApplication, Internship,
    InternshipVisit, Company
)

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task
def send_application_deadline_reminders():
    """
    Envoie des rappels pour les dates limites de candidature
    """
    try:
        # Offres avec date limite dans 3 jours
        deadline_soon = timezone.now().date() + timedelta(days=3)
        
        offers_ending_soon = InternshipOffer.objects.filter(
            status='published',
            application_deadline=deadline_soon
        )
        
        # Envoyer des notifications aux étudiants intéressés
        # (ceux qui ont consulté l'offre récemment)
        
        for offer in offers_ending_soon:
            subject = f"Date limite approche - {offer.title}"
            message = f"""
            La date limite de candidature pour l'offre "{offer.title}" 
            chez {offer.company.name} expire le {offer.application_deadline}.
            
            N'oubliez pas de soumettre votre candidature !
            
            Détails de l'offre:
            - Durée: {offer.duration_value} {offer.get_duration_type_display()}
            - Début: {offer.start_date}
            - Lieu: {offer.company.city}
            """
            
            # Ici vous pourriez ajouter une logique pour identifier
            # les étudiants intéressés et leur envoyer le rappel
            
        logger.info(f"Rappels envoyés pour {offers_ending_soon.count()} offres")
        return f"Rappels envoyés pour {offers_ending_soon.count()} offres"
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi des rappels: {e}")
        raise


@shared_task
def update_internship_statuses():
    """
    Met à jour automatiquement les statuts des stages
    """
    try:
        updated_count = 0
        
        # Stages à venir qui devraient commencer
        upcoming_internships = Internship.objects.filter(
            status='upcoming',
            start_date__lte=timezone.now().date()
        )
        
        for internship in upcoming_internships:
            internship.status = 'ongoing'
            internship.save()
            updated_count += 1
        
        # Stages en cours qui devraient se terminer
        ongoing_internships = Internship.objects.filter(
            status='ongoing',
            end_date__lt=timezone.now().date()
        )
        
        for internship in ongoing_internships:
            internship.status = 'completed'
            internship.save()
            updated_count += 1
        
        # Mettre à jour la progression des stages en cours
        for internship in Internship.objects.filter(status='ongoing'):
            internship.calculate_progress()
        
        logger.info(f"{updated_count} statuts de stages mis à jour")
        return f"{updated_count} statuts de stages mis à jour"
        
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour des statuts: {e}")
        raise


@shared_task
def send_visit_reminders():
    """
    Envoie des rappels pour les visites de stage programmées
    """
    try:
        # Visites dans les 24 prochaines heures
        tomorrow = timezone.now() + timedelta(hours=24)
        
        upcoming_visits = InternshipVisit.objects.filter(
            status='scheduled',
            scheduled_date__lte=tomorrow,
            scheduled_date__gte=timezone.now()
        )
        
        for visit in upcoming_visits:
            # Rappel au visiteur
            subject_visitor = f"Rappel - Visite de stage demain"
            message_visitor = f"""
            Rappel: Vous avez une visite de stage programmée demain.
            
            Détails:
            - Étudiant: {visit.internship.student.get_full_name()}
            - Entreprise: {visit.internship.company.name}
            - Date: {visit.scheduled_date.strftime('%d/%m/%Y à %H:%M')}
            - Lieu: {visit.location}
            - Durée: {visit.duration_minutes} minutes
            
            Type de visite: {visit.get_visit_type_display()}
            """
            
            send_mail(
                subject=subject_visitor,
                message=message_visitor,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[visit.visitor.email],
                fail_silently=True
            )
            
            # Rappel à l'étudiant
            subject_student = f"Rappel - Visite de votre tuteur demain"
            message_student = f"""
            Rappel: Votre tuteur académique {visit.visitor.get_full_name()} 
            vous rendra visite demain dans votre entreprise.
            
            Détails:
            - Date: {visit.scheduled_date.strftime('%d/%m/%Y à %H:%M')}
            - Lieu: {visit.location}
            - Durée: {visit.duration_minutes} minutes
            
            Assurez-vous d'être disponible et de préparer un point sur votre stage.
            """
            
            send_mail(
                subject=subject_student,
                message=message_student,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[visit.internship.student.email],
                fail_silently=True
            )
            
            # Rappel à l'entreprise
            subject_company = f"Rappel - Visite de stage demain"
            message_company = f"""
            Rappel: Une visite de stage est programmée demain pour votre stagiaire.
            
            Détails:
            - Stagiaire: {visit.internship.student.get_full_name()}
            - Visiteur: {visit.visitor.get_full_name()}
            - Date: {visit.scheduled_date.strftime('%d/%m/%Y à %H:%M')}
            - Durée: {visit.duration_minutes} minutes
            
            Merci de vous assurer que le tuteur entreprise soit disponible.
            """
            
            send_mail(
                subject=subject_company,
                message=message_company,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[visit.internship.company.contact_email],
                fail_silently=True
            )
        
        logger.info(f"Rappels envoyés pour {upcoming_visits.count()} visites")
        return f"Rappels envoyés pour {upcoming_visits.count()} visites"
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi des rappels de visite: {e}")
        raise


@shared_task
def expire_old_offers():
    """
    Marque les offres expirées comme telles
    """
    try:
        expired_offers = InternshipOffer.objects.filter(
            status='published',
            application_deadline__lt=timezone.now().date()
        )
        
        count = expired_offers.update(status='expired')
        
        logger.info(f"{count} offres marquées comme expirées")
        return f"{count} offres marquées comme expirées"
        
    except Exception as e:
        logger.error(f"Erreur lors de l'expiration des offres: {e}")
        raise


@shared_task
def send_evaluation_reminders():
    """
    Envoie des rappels pour les évaluations de stage en attente
    """
    try:
        # Stages terminés sans évaluation étudiant
        completed_internships = Internship.objects.filter(
            status='completed',
            student_rating__isnull=True,
            end_date__lt=timezone.now().date(),
            end_date__gte=timezone.now().date() - timedelta(days=30)  # Limiter aux 30 derniers jours
        )
        
        for internship in completed_internships:
            subject = "Évaluez votre stage"
            message = f"""
            Votre stage chez {internship.company.name} est terminé.
            
            Nous vous invitons à évaluer votre expérience pour aider
            les futurs stagiaires et améliorer nos partenariats.
            
            Détails du stage:
            - Entreprise: {internship.company.name}
            - Période: du {internship.start_date} au {internship.end_date}
            - Tuteur: {internship.company_supervisor}
            
            Votre évaluation est importante pour nous !
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[internship.student.email],
                fail_silently=True
            )
        
        logger.info(f"Rappels d'évaluation envoyés pour {completed_internships.count()} stages")
        return f"Rappels d'évaluation envoyés pour {completed_internships.count()} stages"
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi des rappels d'évaluation: {e}")
        raise


@shared_task
def update_company_statistics():
    """
    Met à jour les statistiques des entreprises
    """
    try:
        companies = Company.objects.filter(is_active=True)
        updated_count = 0
        
        for company in companies:
            company.update_statistics()
            updated_count += 1
        
        logger.info(f"Statistiques mises à jour pour {updated_count} entreprises")
        return f"Statistiques mises à jour pour {updated_count} entreprises"
        
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour des statistiques: {e}")
        raise


@shared_task
def generate_internship_reports():
    """
    Génère des rapports automatiques sur les stages
    """
    try:
        today = timezone.now().date()
        
        # Rapport mensuel (le 1er de chaque mois)
        if today.day == 1:
            last_month = today.replace(day=1) - timedelta(days=1)
            month_start = last_month.replace(day=1)
            
            # Statistiques du mois écoulé
            monthly_stats = {
                'period': f"{last_month.strftime('%B %Y')}",
                'new_offers': InternshipOffer.objects.filter(
                    created_at__date__range=[month_start, last_month]
                ).count(),
                'new_applications': InternshipApplication.objects.filter(
                    created_at__date__range=[month_start, last_month]
                ).count(),
                'started_internships': Internship.objects.filter(
                    start_date__range=[month_start, last_month]
                ).count(),
                'completed_internships': Internship.objects.filter(
                    end_date__range=[month_start, last_month]
                ).count()
            }
            
            # Envoyer le rapport aux administrateurs
            admin_users = User.objects.filter(is_staff=True)
            
            for admin in admin_users:
                subject = f"Rapport mensuel des stages - {monthly_stats['period']}"
                message = f"""
                Rapport des activités de stage pour {monthly_stats['period']}:
                
                - Nouvelles offres: {monthly_stats['new_offers']}
                - Nouvelles candidatures: {monthly_stats['new_applications']}
                - Stages commencés: {monthly_stats['started_internships']}
                - Stages terminés: {monthly_stats['completed_internships']}
                
                Consultez le tableau de bord pour plus de détails.
                """
                
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[admin.email],
                    fail_silently=True
                )
            
            logger.info("Rapport mensuel généré et envoyé")
            return f"Rapport mensuel généré: {monthly_stats}"
        
        return "Pas de rapport à générer aujourd'hui"
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération des rapports: {e}")
        raise


@shared_task
def cleanup_old_applications():
    """
    Archive les anciennes candidatures
    """
    try:
        # Archive les candidatures rejetées ou retirées anciennes (> 1 an)
        cutoff_date = timezone.now() - timedelta(days=365)
        
        old_applications = InternshipApplication.objects.filter(
            status__in=['rejected', 'withdrawn'],
            updated_at__lt=cutoff_date
        )
        
        # Ici vous pourriez implémenter une logique d'archivage
        # ou de suppression selon vos besoins de compliance
        
        count = old_applications.count()
        logger.info(f"{count} anciennes candidatures identifiées pour archivage")
        
        return f"{count} anciennes candidatures identifiées pour archivage"
        
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage: {e}")
        raise


@shared_task
def send_partnership_renewal_reminders():
    """
    Envoie des rappels pour le renouvellement des partenariats
    """
    try:
        # Partenariats arrivant à échéance (exemple: tous les 2 ans)
        two_years_ago = timezone.now().date() - timedelta(days=730)
        
        partnerships_to_renew = Company.objects.filter(
            is_partner=True,
            partnership_since__lte=two_years_ago
        )
        
        for company in partnerships_to_renew:
            subject = f"Renouvellement partenariat - {company.name}"
            message = f"""
            Le partenariat avec {company.name} arrive à échéance.
            
            Partenariat depuis: {company.partnership_since}
            Contact: {company.contact_person} ({company.contact_email})
            
            Statistiques:
            - Stages réalisés: {company.total_internships}
            - Note moyenne: {company.average_rating}/5
            
            Veuillez contacter l'entreprise pour discuter du renouvellement.
            """
            
            # Envoyer aux administrateurs
            admin_users = User.objects.filter(is_staff=True)
            for admin in admin_users:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[admin.email],
                    fail_silently=True
                )
        
        logger.info(f"Rappels de renouvellement envoyés pour {partnerships_to_renew.count()} partenariats")
        return f"Rappels de renouvellement envoyés pour {partnerships_to_renew.count()} partenariats"
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi des rappels de renouvellement: {e}")
        raise


@shared_task
def analyze_internship_trends():
    """
    Analyse les tendances des stages pour insights
    """
    try:
        # Analyser les 6 derniers mois
        six_months_ago = timezone.now().date() - timedelta(days=180)
        
        recent_internships = Internship.objects.filter(
            start_date__gte=six_months_ago
        )
        
        # Secteurs populaires
        popular_sectors = {}
        for internship in recent_internships:
            sector = internship.company.sector
            popular_sectors[sector] = popular_sectors.get(sector, 0) + 1
        
        # Entreprises les plus actives
        active_companies = {}
        for internship in recent_internships:
            company = internship.company.name
            active_companies[company] = active_companies.get(company, 0) + 1
        
        # Durées moyennes par secteur
        sector_durations = {}
        for internship in recent_internships:
            sector = internship.company.sector
            duration = (internship.end_date - internship.start_date).days
            
            if sector not in sector_durations:
                sector_durations[sector] = []
            sector_durations[sector].append(duration)
        
        # Calculer les moyennes
        avg_durations = {}
        for sector, durations in sector_durations.items():
            avg_durations[sector] = sum(durations) / len(durations) if durations else 0
        
        insights = {
            'analysis_period': '6 derniers mois',
            'total_internships': recent_internships.count(),
            'popular_sectors': sorted(popular_sectors.items(), key=lambda x: x[1], reverse=True)[:5],
            'active_companies': sorted(active_companies.items(), key=lambda x: x[1], reverse=True)[:5],
            'avg_duration_by_sector': avg_durations
        }
        
        logger.info(f"Analyse des tendances terminée: {insights}")
        return insights
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse des tendances: {e}")
        raise