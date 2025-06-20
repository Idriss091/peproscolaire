"""
Tâches asynchrones pour le cahier de textes et les devoirs
"""
from celery import shared_task
from django.utils import timezone
from django.db.models import Count, Sum, Q
from datetime import date, timedelta
from .models import (
    Homework, StudentWork, WorkloadAnalysis,
    HomeworkTemplate, LessonContent
)
from apps.schools.models import Class
from apps.authentication.models import User


@shared_task
def generate_homework_suggestions(subject_id, class_level, chapter, teacher_id):
    """
    Générer des suggestions de devoirs avec l'IA
    """
    from apps.ai_modules.homework_suggester import HomeworkSuggester
    
    teacher = User.objects.get(id=teacher_id)
    suggester = HomeworkSuggester()
    
    # Analyser les devoirs précédents du professeur
    previous_homework = Homework.objects.filter(
        teacher=teacher,
        subject_id=subject_id
    ).order_by('-created_at')[:10]
    
    # Générer des suggestions personnalisées
    suggestions = suggester.generate_personalized_suggestions(
        subject_id=subject_id,
        class_level=class_level,
        chapter=chapter,
        teacher_style=analyze_teacher_style(previous_homework),
        avoid_repetition=True
    )
    
    # Sauvegarder les suggestions comme modèles
    templates_created = 0
    for suggestion in suggestions:
        HomeworkTemplate.objects.create(
            subject_id=subject_id,
            teacher=teacher,
            name=f"Suggestion IA - {suggestion['title'][:50]}",
            chapter=chapter,
            level=class_level,
            title=suggestion['title'],
            description=suggestion['description'],
            instructions=suggestion.get('instructions', ''),
            estimated_duration_minutes=suggestion.get('duration', 30),
            difficulty=suggestion.get('difficulty', 'medium'),
            tags=f"ia,suggestion,{chapter}",
            is_shared=False
        )
        templates_created += 1
    
    return f"{templates_created} suggestions créées"


def analyze_teacher_style(homework_list):
    """
    Analyser le style pédagogique d'un professeur
    """
    if not homework_list:
        return {
            'avg_duration': 30,
            'difficulty_preference': 'medium',
            'common_types': [],
            'instruction_style': 'standard'
        }
    
    # Analyser les caractéristiques
    durations = [hw.estimated_duration_minutes for hw in homework_list]
    difficulties = [hw.difficulty for hw in homework_list]
    
    # Calculer les préférences
    from collections import Counter
    
    return {
        'avg_duration': sum(durations) / len(durations) if durations else 30,
        'difficulty_preference': Counter(difficulties).most_common(1)[0][0] if difficulties else 'medium',
        'common_types': list(set(hw.homework_type.name for hw in homework_list if hw.homework_type)),
        'instruction_style': 'detailed' if any(len(hw.instructions) > 200 for hw in homework_list) else 'concise'
    }


@shared_task
def analyze_workload(class_id, analysis_date=None):
    """
    Analyser la charge de travail d'une classe
    """
    if analysis_date is None:
        analysis_date = date.today()
    else:
        analysis_date = datetime.strptime(analysis_date, '%Y-%m-%d').date()
    
    class_obj = Class.objects.get(id=class_id)
    
    # Créer ou récupérer l'analyse
    analysis, created = WorkloadAnalysis.objects.get_or_create(
        class_group=class_obj,
        date=analysis_date
    )
    
    # Lancer l'analyse
    analysis.analyze()
    
    # Si surcharge détectée, notifier
    if analysis.is_overloaded:
        notify_workload_alert(analysis)
    
    return f"Analyse terminée pour {class_obj}"


def notify_workload_alert(analysis):
    """
    Notifier en cas de surcharge détectée
    """
    # Notifier le professeur principal
    if analysis.class_group.main_teacher:
        # TODO: Envoyer notification
        pass
    
    # Si critique, notifier aussi l'administration
    if analysis.overload_level in ['critical', 'high']:
        # TODO: Notifier les admins
        pass


@shared_task
def send_homework_reminders():
    """
    Envoyer des rappels pour les devoirs à venir
    """
    tomorrow = date.today() + timedelta(days=1)
    
    # Devoirs dus demain
    homework_due_tomorrow = Homework.objects.filter(
        due_date=tomorrow
    ).select_related('class_group', 'subject')
    
    reminders_sent = 0
    
    for homework in homework_due_tomorrow:
        # Élèves qui n'ont pas encore rendu
        students_without_submission = homework.class_group.students.filter(
            is_active=True
        ).exclude(
            student__homework_submissions__homework=homework,
            student__homework_submissions__status__in=['submitted', 'late', 'returned']
        )
        
        for enrollment in students_without_submission:
            student = enrollment.student
            
            # TODO: Envoyer notification
            # - Email
            # - Notification push
            # - Message interne
            
            reminders_sent += 1
    
    return f"{reminders_sent} rappels envoyés"


@shared_task
def auto_create_student_works(homework_id):
    """
    Créer automatiquement les StudentWork pour tous les élèves
    """
    homework = Homework.objects.get(id=homework_id)
    
    # Récupérer tous les élèves actifs de la classe
    students = homework.class_group.students.filter(
        is_active=True
    ).values_list('student', flat=True)
    
    created_count = 0
    
    for student_id in students:
        work, created = StudentWork.objects.get_or_create(
            homework=homework,
            student_id=student_id,
            defaults={
                'status': 'draft'
            }
        )
        if created:
            created_count += 1
    
    return f"{created_count} travaux créés"


@shared_task
def cleanup_draft_submissions():
    """
    Nettoyer les brouillons non modifiés depuis longtemps
    """
    threshold_date = timezone.now() - timedelta(days=90)
    
    # Supprimer les brouillons vides de plus de 90 jours
    deleted = StudentWork.objects.filter(
        status='draft',
        created_at__lt=threshold_date,
        content='',
        file__isnull=True
    ).delete()
    
    return f"{deleted[0]} brouillons supprimés"


@shared_task
def generate_weekly_summary():
    """
    Générer un résumé hebdomadaire pour chaque classe
    """
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    summaries_generated = 0
    
    # Pour chaque classe active
    classes = Class.objects.filter(
        academic_year__is_current=True
    )
    
    for class_obj in classes:
        # Cours de la semaine
        lessons = LessonContent.objects.filter(
            schedule__class_group=class_obj,
            date__range=[week_start, week_end]
        ).count()
        
        # Devoirs donnés
        homework_assigned = Homework.objects.filter(
            class_group=class_obj,
            assigned_date__range=[week_start, week_end]
        ).count()
        
        # Devoirs à rendre
        homework_due = Homework.objects.filter(
            class_group=class_obj,
            due_date__range=[week_start, week_end]
        )
        
        # Taux de rendu moyen
        submission_rates = []
        for hw in homework_due:
            total_students = class_obj.students.filter(is_active=True).count()
            if total_students > 0:
                submitted = hw.submissions.filter(
                    status__in=['submitted', 'late', 'returned']
                ).count()
                rate = (submitted / total_students) * 100
                submission_rates.append(rate)
        
        avg_submission_rate = sum(submission_rates) / len(submission_rates) if submission_rates else 0
        
        # TODO: Envoyer le résumé au professeur principal
        summary = {
            'class': str(class_obj),
            'week': f"{week_start} - {week_end}",
            'lessons_count': lessons,
            'homework_assigned': homework_assigned,
            'homework_due': homework_due.count(),
            'avg_submission_rate': round(avg_submission_rate, 2)
        }
        
        summaries_generated += 1
    
    return f"{summaries_generated} résumés générés"


@shared_task
def check_missing_lesson_content():
    """
    Détecter les cours sans contenu dans le cahier de textes
    """
    from apps.timetable.models import Schedule
    
    # Vérifier les cours des 7 derniers jours
    check_date = date.today() - timedelta(days=7)
    
    missing_content = []
    
    # Pour chaque jour de la semaine passée
    for i in range(7):
        current_date = check_date + timedelta(days=i)
        day_of_week = current_date.weekday()
        
        # Récupérer les schedules de ce jour
        schedules = Schedule.objects.filter(
            time_slot__day=day_of_week,
            is_cancelled=False
        ).select_related('subject', 'class_group', 'teacher')
        
        for schedule in schedules:
            # Vérifier s'il y a un contenu pour cette date
            has_content = LessonContent.objects.filter(
                schedule=schedule,
                date=current_date
            ).exists()
            
            if not has_content:
                missing_content.append({
                    'date': current_date,
                    'schedule': schedule,
                    'teacher': schedule.teacher
                })
    
    # Notifier les professeurs
    teachers_notified = set()
    for missing in missing_content:
        teacher = missing['teacher']
        if teacher.id not in teachers_notified:
            # TODO: Envoyer notification au professeur
            teachers_notified.add(teacher.id)
    
    return f"{len(missing_content)} cours sans contenu détectés, {len(teachers_notified)} professeurs notifiés"


@shared_task
def auto_validate_old_content():
    """
    Valider automatiquement les anciens contenus non validés
    """
    # Contenus de plus de 30 jours non validés
    threshold_date = date.today() - timedelta(days=30)
    
    old_content = LessonContent.objects.filter(
        validated=False,
        date__lt=threshold_date
    )
    
    validated_count = old_content.update(
        validated=True,
        validated_at=timezone.now()
    )
    
    return f"{validated_count} contenus validés automatiquement"


@shared_task
def generate_homework_statistics():
    """
    Générer des statistiques sur les devoirs
    """
    # Période : dernier mois
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    # Statistiques globales
    homework_stats = Homework.objects.filter(
        assigned_date__range=[start_date, end_date]
    ).aggregate(
        total_count=Count('id'),
        avg_duration=models.Avg('estimated_duration_minutes'),
        graded_count=Count('id', filter=Q(is_graded=True)),
        ai_suggested_count=Count('id', filter=Q(is_ai_suggested=True))
    )
    
    # Par matière
    by_subject = Homework.objects.filter(
        assigned_date__range=[start_date, end_date]
    ).values('subject__name').annotate(
        count=Count('id'),
        avg_duration=models.Avg('estimated_duration_minutes')
    ).order_by('-count')
    
    # Taux de rendu global
    submission_stats = StudentWork.objects.filter(
        homework__assigned_date__range=[start_date, end_date]
    ).aggregate(
        total=Count('id'),
        submitted=Count('id', filter=Q(status__in=['submitted', 'returned'])),
        late=Count('id', filter=Q(status='late'))
    )
    
    submission_rate = 0
    if submission_stats['total'] > 0:
        submission_rate = (submission_stats['submitted'] / submission_stats['total']) * 100
    
    report = {
        'period': f"{start_date} - {end_date}",
        'global_stats': homework_stats,
        'by_subject': list(by_subject[:10]),
        'submission_rate': round(submission_rate, 2),
        'late_rate': round((submission_stats['late'] / submission_stats['total'] * 100), 2) if submission_stats['total'] > 0 else 0
    }
    
    # TODO: Envoyer le rapport aux administrateurs
    
    return "Statistiques générées"