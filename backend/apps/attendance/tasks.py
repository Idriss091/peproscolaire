"""
Tâches asynchrones pour la vie scolaire
"""
from celery import shared_task
from django.db.models import Count, Q
from django.utils import timezone
from datetime import date, timedelta
from .models import (
    Attendance, AttendanceAlert, AttendanceStatus,
    StudentBehavior
)
from apps.schools.models import Class
from apps.authentication.models import User


@shared_task
def check_attendance_alerts(class_id=None):
    """
    Vérifier et créer des alertes d'assiduité
    Peut être exécuté pour une classe spécifique ou toutes les classes
    """
    if class_id:
        classes = Class.objects.filter(id=class_id)
    else:
        # Toutes les classes actives
        classes = Class.objects.filter(
            academic_year__is_current=True
        )
    
    alerts_created = 0
    
    for class_obj in classes:
        students = class_obj.students.filter(is_active=True)
        
        for enrollment in students:
            student = enrollment.student
            
            # Vérifier différents types d'alertes
            # 1. Nombre d'absences sur 30 jours
            check_absence_count(student)
            
            # 2. Nombre de retards sur 30 jours
            check_late_count(student)
            
            # 3. Absences consécutives
            check_consecutive_absences(student)
            
            # 4. Pattern d'absence (même jour de la semaine)
            check_absence_pattern(student)
    
    return f"{alerts_created} alertes créées"


def check_absence_count(student):
    """Vérifier le nombre d'absences sur 30 jours"""
    threshold = 5  # Seuil d'alerte
    period_days = 30
    
    end_date = date.today()
    start_date = end_date - timedelta(days=period_days)
    
    absence_count = Attendance.objects.filter(
        student=student,
        date__range=[start_date, end_date],
        status=AttendanceStatus.ABSENT,
        is_justified=False
    ).count()
    
    if absence_count >= threshold:
        # Vérifier si une alerte existe déjà
        existing_alert = AttendanceAlert.objects.filter(
            student=student,
            alert_type='absence_count',
            period_start=start_date,
            period_end=end_date,
            is_resolved=False
        ).exists()
        
        if not existing_alert:
            # Créer l'alerte
            alert = AttendanceAlert.objects.create(
                student=student,
                alert_type='absence_count',
                threshold_value=absence_count,
                period_start=start_date,
                period_end=end_date,
                message=f"{student.get_full_name()} a {absence_count} absences non justifiées sur les {period_days} derniers jours.",
                details={
                    'absence_count': absence_count,
                    'threshold': threshold,
                    'period_days': period_days
                }
            )
            
            # Notifier les personnes concernées
            notify_alert(alert)


def check_late_count(student):
    """Vérifier le nombre de retards sur 30 jours"""
    threshold = 10  # Seuil d'alerte
    period_days = 30
    
    end_date = date.today()
    start_date = end_date - timedelta(days=period_days)
    
    late_count = Attendance.objects.filter(
        student=student,
        date__range=[start_date, end_date],
        status=AttendanceStatus.LATE
    ).count()
    
    if late_count >= threshold:
        existing_alert = AttendanceAlert.objects.filter(
            student=student,
            alert_type='late_count',
            period_start=start_date,
            period_end=end_date,
            is_resolved=False
        ).exists()
        
        if not existing_alert:
            alert = AttendanceAlert.objects.create(
                student=student,
                alert_type='late_count',
                threshold_value=late_count,
                period_start=start_date,
                period_end=end_date,
                message=f"{student.get_full_name()} a {late_count} retards sur les {period_days} derniers jours.",
                details={
                    'late_count': late_count,
                    'threshold': threshold,
                    'period_days': period_days
                }
            )
            
            notify_alert(alert)


def check_consecutive_absences(student):
    """Vérifier les absences consécutives"""
    threshold = 3  # Nombre de jours consécutifs
    
    # Récupérer les 10 derniers jours d'école
    end_date = date.today()
    start_date = end_date - timedelta(days=14)
    
    attendances = Attendance.objects.filter(
        student=student,
        date__range=[start_date, end_date]
    ).order_by('date').values('date', 'status')
    
    # Compter les absences consécutives
    consecutive_count = 0
    max_consecutive = 0
    last_absence_date = None
    first_absence_date = None
    
    for attendance in attendances:
        if attendance['status'] == AttendanceStatus.ABSENT:
            if last_absence_date and (attendance['date'] - last_absence_date).days == 1:
                consecutive_count += 1
            else:
                consecutive_count = 1
                first_absence_date = attendance['date']
            
            last_absence_date = attendance['date']
            max_consecutive = max(max_consecutive, consecutive_count)
        else:
            consecutive_count = 0
    
    if max_consecutive >= threshold:
        existing_alert = AttendanceAlert.objects.filter(
            student=student,
            alert_type='consecutive_absence',
            period_end=end_date,
            is_resolved=False
        ).exists()
        
        if not existing_alert:
            alert = AttendanceAlert.objects.create(
                student=student,
                alert_type='consecutive_absence',
                threshold_value=max_consecutive,
                period_start=first_absence_date,
                period_end=last_absence_date,
                message=f"{student.get_full_name()} a été absent {max_consecutive} jours consécutifs.",
                details={
                    'consecutive_days': max_consecutive,
                    'threshold': threshold
                }
            )
            
            notify_alert(alert)


def check_absence_pattern(student):
    """Détecter les patterns d'absence (ex: toujours absent le lundi)"""
    period_weeks = 4  # Analyser sur 4 semaines
    threshold = 3  # Absent au moins 3 fois le même jour
    
    end_date = date.today()
    start_date = end_date - timedelta(weeks=period_weeks)
    
    # Analyser les absences par jour de la semaine
    absences_by_day = Attendance.objects.filter(
        student=student,
        date__range=[start_date, end_date],
        status=AttendanceStatus.ABSENT
    ).values('date')
    
    day_counts = {i: 0 for i in range(7)}  # 0=Lundi, 6=Dimanche
    
    for absence in absences_by_day:
        day_of_week = absence['date'].weekday()
        day_counts[day_of_week] += 1
    
    # Vérifier si un jour dépasse le seuil
    for day, count in day_counts.items():
        if count >= threshold:
            day_names = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
            
            existing_alert = AttendanceAlert.objects.filter(
                student=student,
                alert_type='pattern',
                period_start=start_date,
                period_end=end_date,
                is_resolved=False,
                details__day_of_week=day
            ).exists()
            
            if not existing_alert:
                alert = AttendanceAlert.objects.create(
                    student=student,
                    alert_type='pattern',
                    threshold_value=count,
                    period_start=start_date,
                    period_end=end_date,
                    message=f"{student.get_full_name()} est souvent absent le {day_names[day]} ({count} fois sur {period_weeks} semaines).",
                    details={
                        'day_of_week': day,
                        'day_name': day_names[day],
                        'absence_count': count,
                        'period_weeks': period_weeks
                    }
                )
                
                notify_alert(alert)


def notify_alert(alert):
    """Notifier les personnes concernées d'une alerte"""
    # Récupérer les personnes à notifier
    notified_users = []
    
    # 1. Le professeur principal
    enrollment = alert.student.enrollments.filter(is_active=True).first()
    if enrollment and enrollment.class_group.main_teacher:
        notified_users.append(enrollment.class_group.main_teacher)
    
    # 2. Les CPE (à implémenter)
    # TODO: Ajouter la relation avec les CPE
    
    # 3. Les parents (à implémenter)
    # TODO: Ajouter la relation parent-enfant
    
    # Ajouter les utilisateurs notifiés
    alert.notified_users.add(*notified_users)
    
    # TODO: Envoyer des notifications (email, push, etc.)
    # Pour l'instant, on enregistre juste dans la base


@shared_task
def generate_monthly_attendance_report():
    """
    Générer un rapport mensuel de présence pour chaque classe
    """
    # Récupérer le mois précédent
    today = date.today()
    first_day_current_month = today.replace(day=1)
    last_day_previous_month = first_day_current_month - timedelta(days=1)
    first_day_previous_month = last_day_previous_month.replace(day=1)
    
    # Pour chaque classe active
    classes = Class.objects.filter(
        academic_year__is_current=True
    )
    
    reports = []
    
    for class_obj in classes:
        # Statistiques globales de la classe
        class_attendances = Attendance.objects.filter(
            schedule__class_group=class_obj,
            date__range=[first_day_previous_month, last_day_previous_month]
        )
        
        total_entries = class_attendances.count()
        
        if total_entries > 0:
            stats = class_attendances.aggregate(
                present_count=Count('id', filter=Q(status=AttendanceStatus.PRESENT)),
                absent_count=Count('id', filter=Q(status=AttendanceStatus.ABSENT)),
                late_count=Count('id', filter=Q(status=AttendanceStatus.LATE)),
                excused_count=Count('id', filter=Q(status=AttendanceStatus.EXCUSED))
            )
            
            # Statistiques par élève
            student_stats = []
            for enrollment in class_obj.students.filter(is_active=True):
                student = enrollment.student
                student_attendances = class_attendances.filter(student=student)
                
                if student_attendances.exists():
                    student_stat = student_attendances.aggregate(
                        total=Count('id'),
                        present=Count('id', filter=Q(status=AttendanceStatus.PRESENT)),
                        absent=Count('id', filter=Q(status=AttendanceStatus.ABSENT)),
                        late=Count('id', filter=Q(status=AttendanceStatus.LATE))
                    )
                    
                    attendance_rate = (
                        (student_stat['present'] + student_stat['late']) / 
                        student_stat['total'] * 100
                    )
                    
                    student_stats.append({
                        'student': student.get_full_name(),
                        'attendance_rate': round(attendance_rate, 2),
                        'absences': student_stat['absent'],
                        'lates': student_stat['late']
                    })
            
            # Trier par taux de présence
            student_stats.sort(key=lambda x: x['attendance_rate'])
            
            report = {
                'class': str(class_obj),
                'month': last_day_previous_month.strftime('%B %Y'),
                'global_stats': stats,
                'attendance_rate': round(
                    (stats['present_count'] + stats['late_count']) / total_entries * 100,
                    2
                ),
                'students_at_risk': student_stats[:5],  # 5 élèves avec le plus faible taux
                'best_students': student_stats[-5:][::-1]  # 5 meilleurs élèves
            }
            
            reports.append(report)
    
    # TODO: Envoyer les rapports par email aux chefs d'établissement
    return f"{len(reports)} rapports générés"


@shared_task
def auto_justify_medical_absences():
    """
    Justifier automatiquement les absences avec certificat médical
    """
    # Récupérer les périodes d'absence justifiées
    justified_periods = AbsencePeriod.objects.filter(
        is_justified=True,
        justification_document__isnull=False
    )
    
    updated_count = 0
    
    for period in justified_periods:
        # Justifier toutes les absences de cette période
        updated = Attendance.objects.filter(
            student=period.student,
            date__range=[period.start_date, period.end_date],
            status__in=[AttendanceStatus.ABSENT, AttendanceStatus.EXCUSED],
            is_justified=False
        ).update(
            is_justified=True,
            justification_reason=f"Période d'absence justifiée: {period.reason}"
        )
        
        updated_count += updated
    
    return f"{updated_count} absences justifiées automatiquement"