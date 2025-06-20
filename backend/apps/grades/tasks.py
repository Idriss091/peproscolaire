"""
Tâches asynchrones pour la gestion des notes
"""
from celery import shared_task
from django.db.models import Avg, Count, Q
from decimal import Decimal
from .models import (
    Evaluation, Grade, SubjectAverage, GeneralAverage,
    GradingPeriod
)
from apps.schools.models import Class
from apps.authentication.models import User


@shared_task
def calculate_class_averages(class_id, grading_period_id):
    """
    Calculer toutes les moyennes d'une classe pour une période
    """
    class_obj = Class.objects.get(id=class_id)
    period = GradingPeriod.objects.get(id=grading_period_id)
    
    # Pour chaque élève de la classe
    enrollments = class_obj.students.filter(is_active=True)
    
    for enrollment in enrollments:
        student = enrollment.student
        
        # Calculer les moyennes par matière
        calculate_student_subject_averages(student.id, period.id, class_obj.id)
        
        # Calculer la moyenne générale
        calculate_student_general_average(student.id, period.id, class_obj.id)
    
    # Calculer les rangs
    calculate_class_rankings(class_obj.id, period.id)
    
    return f"Moyennes calculées pour {enrollments.count()} élèves"


@shared_task
def calculate_student_subject_averages(student_id, grading_period_id, class_id):
    """
    Calculer les moyennes par matière d'un élève
    """
    student = User.objects.get(id=student_id)
    period = GradingPeriod.objects.get(id=grading_period_id)
    class_obj = Class.objects.get(id=class_id)
    
    # Récupérer toutes les matières de la classe
    subjects = Subject.objects.filter(
        schedules__class_group=class_obj
    ).distinct()
    
    for subject in subjects:
        # Créer ou récupérer la moyenne
        avg, created = SubjectAverage.objects.get_or_create(
            student=student,
            subject=subject,
            grading_period=period,
            defaults={'class_group': class_obj}
        )
        
        # Calculer la moyenne
        avg.calculate_average()
        
        # Calculer le rang sera fait globalement après


@shared_task
def calculate_student_general_average(student_id, grading_period_id, class_id):
    """
    Calculer la moyenne générale d'un élève
    """
    student = User.objects.get(id=student_id)
    period = GradingPeriod.objects.get(id=grading_period_id)
    class_obj = Class.objects.get(id=class_id)
    
    # Créer ou récupérer la moyenne générale
    avg, created = GeneralAverage.objects.get_or_create(
        student=student,
        grading_period=period,
        defaults={'class_group': class_obj}
    )
    
    # Calculer la moyenne
    avg.calculate_average()


@shared_task
def calculate_class_rankings(class_id, grading_period_id):
    """
    Calculer les rangs de tous les élèves d'une classe
    """
    # Rangs par matière
    subject_averages = SubjectAverage.objects.filter(
        class_group_id=class_id,
        grading_period_id=grading_period_id
    ).select_related('subject')
    
    # Grouper par matière
    subjects = {}
    for avg in subject_averages:
        if avg.subject_id not in subjects:
            subjects[avg.subject_id] = []
        subjects[avg.subject_id].append(avg)
    
    # Calculer les rangs par matière
    for subject_id, averages in subjects.items():
        # Trier par moyenne décroissante
        sorted_avgs = sorted(
            averages,
            key=lambda x: x.average or Decimal('0'),
            reverse=True
        )
        
        rank = 1
        prev_avg = None
        same_rank_count = 0
        
        for i, avg in enumerate(sorted_avgs):
            if avg.average is None:
                avg.rank = None
            else:
                if prev_avg and avg.average == prev_avg:
                    same_rank_count += 1
                else:
                    rank = i + 1 - same_rank_count
                    same_rank_count = 0
                
                avg.rank = rank
                prev_avg = avg.average
            
            avg.class_size = len([a for a in sorted_avgs if a.average is not None])
            
            # Statistiques de classe
            valid_avgs = [a.average for a in sorted_avgs if a.average is not None]
            if valid_avgs:
                avg.class_average = sum(valid_avgs) / len(valid_avgs)
                avg.min_average = min(valid_avgs)
                avg.max_average = max(valid_avgs)
            
            avg.save()
    
    # Rangs généraux
    general_averages = GeneralAverage.objects.filter(
        class_group_id=class_id,
        grading_period_id=grading_period_id
    )
    
    for avg in general_averages:
        avg.calculate_rank()


@shared_task
def generate_report_cards(grading_period_id):
    """
    Générer tous les bulletins d'une période
    """
    period = GradingPeriod.objects.get(id=grading_period_id)
    
    # Récupérer toutes les classes de l'année scolaire
    classes = Class.objects.filter(academic_year=period.academic_year)
    
    total_bulletins = 0
    
    for class_obj in classes:
        # S'assurer que les moyennes sont calculées
        calculate_class_averages(class_obj.id, period.id)
        
        # Générer les bulletins PDF
        # TODO: Implémenter la génération PDF avec ReportLab ou WeasyPrint
        
        total_bulletins += class_obj.students.filter(is_active=True).count()
    
    return f"{total_bulletins} bulletins générés"


@shared_task
def send_grade_notifications(evaluation_id):
    """
    Envoyer des notifications quand des notes sont publiées
    """
    evaluation = Evaluation.objects.get(id=evaluation_id)
    
    # Récupérer tous les élèves notés
    grades = evaluation.grades.filter(
        score__isnull=False
    ).select_related('student')
    
    notifications_sent = 0
    
    for grade in grades:
        # TODO: Implémenter l'envoi de notification
        # - Email aux parents
        # - Notification push sur l'app
        # - Message dans la messagerie interne
        
        notifications_sent += 1
    
    return f"{notifications_sent} notifications envoyées"


@shared_task
def auto_generate_appreciations(grading_period_id, class_id=None):
    """
    Générer automatiquement des appréciations avec l'IA
    """
    from apps.ai_modules.appreciation_generator import AppreciationGenerator
    
    generator = AppreciationGenerator()
    period = GradingPeriod.objects.get(id=grading_period_id)
    
    # Filtrer par classe si spécifiée
    query = SubjectAverage.objects.filter(
        grading_period=period,
        appreciation=''  # Seulement celles sans appréciation
    )
    
    if class_id:
        query = query.filter(class_group_id=class_id)
    
    appreciations_generated = 0
    
    for subject_avg in query.select_related('student', 'subject'):
        # Générer l'appréciation avec l'IA
        appreciation = generator.generate_appreciation(
            student=subject_avg.student,
            subject=subject_avg.subject,
            average=subject_avg.average,
            period=period
        )
        
        if appreciation:
            subject_avg.appreciation = appreciation
            subject_avg.save()
            appreciations_generated += 1
    
    return f"{appreciations_generated} appréciations générées"


@shared_task
def detect_struggling_students(class_id, grading_period_id):
    """
    Détecter les élèves en difficulté
    """
    threshold = Decimal('10.0')  # Moyenne en dessous de 10
    
    # Élèves avec moyenne générale faible
    struggling_students = GeneralAverage.objects.filter(
        class_group_id=class_id,
        grading_period_id=grading_period_id,
        weighted_average__lt=threshold
    ).select_related('student')
    
    alerts = []
    
    for avg in struggling_students:
        # Analyser les matières en difficulté
        weak_subjects = SubjectAverage.objects.filter(
            student=avg.student,
            grading_period_id=grading_period_id,
            average__lt=threshold
        ).select_related('subject')
        
        alert = {
            'student': avg.student.get_full_name(),
            'general_average': float(avg.weighted_average),
            'weak_subjects': [
                {
                    'subject': subj.subject.name,
                    'average': float(subj.average)
                }
                for subj in weak_subjects
            ]
        }
        alerts.append(alert)
        
        # TODO: Créer une alerte dans le système
        # TODO: Notifier le professeur principal et les parents
    
    return alerts


@shared_task
def calculate_subject_statistics(subject_id, grading_period_id):
    """
    Calculer les statistiques globales d'une matière
    """
    from django.db.models import StdDev
    
    averages = SubjectAverage.objects.filter(
        subject_id=subject_id,
        grading_period_id=grading_period_id,
        average__isnull=False
    )
    
    stats = averages.aggregate(
        total_students=Count('id'),
        mean=Avg('average'),
        min_avg=models.Min('average'),
        max_avg=models.Max('average'),
        std_dev=StdDev('average'),
        above_15=Count('id', filter=Q(average__gte=15)),
        between_10_15=Count('id', filter=Q(average__gte=10, average__lt=15)),
        below_10=Count('id', filter=Q(average__lt=10))
    )
    
    # Distribution par classe
    class_stats = averages.values('class_group__name').annotate(
        class_average=Avg('average'),
        student_count=Count('id')
    ).order_by('-class_average')
    
    return {
        'global_statistics': stats,
        'class_distribution': list(class_stats)
    }