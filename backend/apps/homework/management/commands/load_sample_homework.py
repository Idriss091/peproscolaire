"""
Commande pour charger des devoirs d'exemple
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import random
from apps.homework.models import Homework, HomeworkType, LessonContent
from apps.schools.models import Class
from apps.timetable.models import Subject, Schedule
from apps.authentication.models import User


class Command(BaseCommand):
    help = 'Charge des devoirs d\'exemple dans la base de données'
    
    def handle(self, *args, **options):
        self.stdout.write('Chargement des devoirs d\'exemple...')
        
        # Récupérer les données nécessaires
        classes = Class.objects.filter(academic_year__is_current=True)
        subjects = Subject.objects.all()
        teachers = User.objects.filter(user_type='teacher')
        homework_types = HomeworkType.objects.all()
        
        if not all([classes, subjects, teachers, homework_types]):
            self.stdout.write(
                self.style.ERROR('Données insuffisantes. Assurez-vous d\'avoir des classes, matières, professeurs et types de devoirs.')
            )
            return
        
        homework_count = 0
        
        # Pour chaque classe
        for class_obj in classes[:5]:  # Limiter à 5 classes
            # Pour chaque matière
            for subject in subjects[:5]:  # Limiter à 5 matières
                # Vérifier s'il y a un schedule pour cette classe/matière
                schedule = Schedule.objects.filter(
                    class_group=class_obj,
                    subject=subject
                ).first()
                
                if not schedule:
                    continue
                
                # Créer 3 devoirs par matière
                for i in range(3):
                    due_date = date.today() + timedelta(days=random.randint(1, 14))
                    
                    homework = Homework.objects.create(
                        subject=subject,
                        class_group=class_obj,
                        teacher=schedule.teacher,
                        homework_type=random.choice(homework_types),
                        title=f"{subject.name} - Devoir {i+1}",
                        description=f"Description du devoir de {subject.name} pour la classe {class_obj}",
                        instructions="Faire avec soin et rendre à temps.",
                        assigned_date=date.today(),
                        due_date=due_date,
                        estimated_duration_minutes=random.choice([20, 30, 45, 60]),
                        difficulty=random.choice(['easy', 'medium', 'hard']),
                        is_graded=random.choice([True, False])
                    )
                    
                    homework_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'{homework_count} devoirs créés avec succès!')
        )