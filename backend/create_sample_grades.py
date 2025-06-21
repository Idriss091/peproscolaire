#!/usr/bin/env python
"""
Script pour créer des données d'exemple pour les notes
"""
import os
import sys
import django

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_minimal')
django.setup()

from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from apps.authentication.models import User
from apps.schools.models import School, AcademicYear, Class, Level
from apps.timetable.models import Subject
from apps.grades.models import EvaluationType, GradingPeriod, Evaluation, Grade

def create_sample_grades():
    print("Création des données d'exemple pour les notes...")
    
    # 1. Créer ou récupérer une école
    school, created = School.objects.get_or_create(
        name="Collège de Test",
        defaults={
            'school_type': 'college',
            'address': '123 Rue de Test',
            'city': 'Testville',
            'postal_code': '12345',
            'phone': '0123456789',
            'email': 'test@test.com',
            'subdomain': 'test-college'
        }
    )
    
    # 2. Créer ou récupérer une année académique
    academic_year, created = AcademicYear.objects.get_or_create(
        name="2023-2024",
        school=school,
        defaults={
            'start_date': date(2023, 9, 1),
            'end_date': date(2024, 6, 30),
            'is_current': True
        }
    )
    
    # 3. Créer ou récupérer un niveau
    level, created = Level.objects.get_or_create(
        name="Troisième",
        defaults={
            'short_name': '3ème',
            'order': 3,
            'school_type': 'college'
        }
    )
    
    # 4. Créer ou récupérer une classe
    class_group, created = Class.objects.get_or_create(
        name="A",
        school=school,
        academic_year=academic_year,
        level=level,
        defaults={
            'max_students': 30
        }
    )
    
    # 5. Créer ou récupérer des matières
    subjects_data = [
        {'name': 'Mathématiques', 'short_name': 'MATH', 'coefficient': 4},
        {'name': 'Français', 'short_name': 'FR', 'coefficient': 4},
        {'name': 'Histoire-Géographie', 'short_name': 'HG', 'coefficient': 3},
        {'name': 'Sciences Physiques', 'short_name': 'PC', 'coefficient': 2},
    ]
    
    subjects = []
    for subject_data in subjects_data:
        subject, created = Subject.objects.get_or_create(
            name=subject_data['name'],
            defaults={
                'short_name': subject_data['short_name'],
                'coefficient': subject_data['coefficient'],
                'color': '#3B82F6'
            }
        )
        subjects.append(subject)
    
    # 6. Récupérer ou créer un type d'évaluation
    eval_type = EvaluationType.objects.filter(name="Contrôle").first()
    if not eval_type:
        eval_type = EvaluationType.objects.create(
            name="Contrôle",
            short_name='DS',
            default_coefficient=2.0,
            color='#EF4444'
        )
    
    # 7. Créer une période de notation
    grading_period, created = GradingPeriod.objects.get_or_create(
        academic_year=academic_year,
        number=1,
        defaults={
            'name': 'Trimestre 1',
            'start_date': date(2023, 9, 1),
            'end_date': date(2023, 12, 22),
            'is_active': True
        }
    )
    
    # 8. Créer ou récupérer des enseignants
    teachers = []
    teachers_data = [
        {'username': 'prof.math', 'first_name': 'Jean', 'last_name': 'Martin', 'email': 'jean.martin@test.com'},
        {'username': 'prof.francais', 'first_name': 'Marie', 'last_name': 'Dupont', 'email': 'marie.dupont@test.com'},
    ]
    
    for teacher_data in teachers_data:
        teacher, created = User.objects.get_or_create(
            username=teacher_data['username'],
            defaults={
                'first_name': teacher_data['first_name'],
                'last_name': teacher_data['last_name'],
                'email': teacher_data['email'],
                'user_type': 'teacher',
                'is_active': True
            }
        )
        if created:
            teacher.set_password('password123')
            teacher.save()
        teachers.append(teacher)
    
    # 9. Créer ou récupérer des élèves
    students = []
    students_data = [
        {'username': 'eleve1', 'first_name': 'Pierre', 'last_name': 'Durand', 'email': 'pierre.durand@test.com'},
        {'username': 'eleve2', 'first_name': 'Sophie', 'last_name': 'Bernard', 'email': 'sophie.bernard@test.com'},
        {'username': 'eleve3', 'first_name': 'Paul', 'last_name': 'Leroy', 'email': 'paul.leroy@test.com'},
    ]
    
    for student_data in students_data:
        student, created = User.objects.get_or_create(
            username=student_data['username'],
            defaults={
                'first_name': student_data['first_name'],
                'last_name': student_data['last_name'],
                'email': student_data['email'],
                'user_type': 'student',
                'is_active': True
            }
        )
        if created:
            student.set_password('password123')
            student.save()
        students.append(student)
    
    # 10. Créer des évaluations et des notes
    evaluations_data = [
        {
            'title': 'Contrôle équations',
            'subject': subjects[0],  # Math
            'teacher': teachers[0],
            'date': date.today() - timedelta(days=7),
            'max_score': 20.0,
            'coefficient': 2.0
        },
        {
            'title': 'Rédaction',
            'subject': subjects[1],  # Français
            'teacher': teachers[1],
            'date': date.today() - timedelta(days=3),
            'max_score': 20.0,
            'coefficient': 1.5
        }
    ]
    
    for eval_data in evaluations_data:
        evaluation, created = Evaluation.objects.get_or_create(
            title=eval_data['title'],
            subject=eval_data['subject'],
            class_group=class_group,
            defaults={
                'description': f"Évaluation de {eval_data['subject'].name}",
                'evaluation_type': eval_type,
                'teacher': eval_data['teacher'],
                'grading_period': grading_period,
                'date': eval_data['date'],
                'max_score': eval_data['max_score'],
                'coefficient': eval_data['coefficient'],
                'is_graded': True,
                'grades_published': True
            }
        )
        
        if created:
            # Créer des notes pour chaque élève
            grades_data = [
                {'student': students[0], 'score': Decimal('15.5')},
                {'student': students[1], 'score': Decimal('17.0')},
                {'student': students[2], 'score': Decimal('12.5')},
            ]
            
            for grade_data in grades_data:
                Grade.objects.get_or_create(
                    evaluation=evaluation,
                    student=grade_data['student'],
                    defaults={
                        'score': grade_data['score'],
                        'graded_by': eval_data['teacher'],
                        'graded_at': timezone.now()
                    }
                )
    
    print("✅ Données d'exemple créées avec succès!")
    print(f"- École: {school.name}")
    print(f"- Année académique: {academic_year.name}")
    print(f"- Classe: {class_group.name}")
    print(f"- Matières: {len(subjects)}")
    print(f"- Enseignants: {len(teachers)}")
    print(f"- Élèves: {len(students)}")
    print(f"- Évaluations: {Evaluation.objects.count()}")
    print(f"- Notes: {Grade.objects.count()}")

if __name__ == '__main__':
    create_sample_grades()