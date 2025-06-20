"""
Fixtures pour les tests du module homework
"""
import pytest
from datetime import date, time, timedelta
from apps.authentication.models import User
from apps.schools.models import School, AcademicYear, Level, Class
from apps.timetable.models import Subject, TimeSlot, Schedule
from apps.homework.models import Homework, HomeworkType


@pytest.fixture
def teacher():
    """Créer un professeur de test"""
    return User.objects.create_user(
        email='prof@test.com',
        username='proftest',
        password='testpass123',
        first_name='Prof',
        last_name='Test',
        user_type='teacher'
    )


@pytest.fixture
def student():
    """Créer un élève de test"""
    return User.objects.create_user(
        email='eleve@test.com',
        username='elevetest',
        password='testpass123',
        first_name='Élève',
        last_name='Test',
        user_type='student'
    )


@pytest.fixture
def school():
    """Créer un établissement de test"""
    return School.objects.create(
        name='Lycée Test',
        school_type='lycee',
        address='1 rue du Test',
        postal_code='75000',
        city='Paris',
        phone='0123456789',
        email='contact@lyceetest.fr',
        subdomain='lycee-test'
    )


@pytest.fixture
def academic_year(school):
    """Créer une année scolaire de test"""
    return AcademicYear.objects.create(
        school=school,
        name='2024-2025',
        start_date=date(2024, 9, 1),
        end_date=date(2025, 6, 30),
        is_current=True
    )


@pytest.fixture
def class_group(school, academic_year, teacher):
    """Créer une classe de test"""
    level = Level.objects.create(
        name='Seconde',
        short_name='2nde',
        order=10,
        school_type='lycee'
    )
    
    return Class.objects.create(
        school=school,
        academic_year=academic_year,
        level=level,
        name='A',
        main_teacher=teacher,
        max_students=30
    )


@pytest.fixture
def subject():
    """Créer une matière de test"""
    return Subject.objects.create(
        name='Mathématiques',
        short_name='MATH',
        coefficient=4.0
    )


@pytest.fixture
def schedule(school, class_group, subject, teacher):
    """Créer un emploi du temps de test"""
    time_slot = TimeSlot.objects.create(
        school=school,
        day=0,  # Lundi
        start_time=time(8, 0),
        end_time=time(9, 0),
        order=1
    )
    
    return Schedule.objects.create(
        academic_year=class_group.academic_year,
        class_group=class_group,
        subject=subject,
        teacher=teacher,
        time_slot=time_slot
    )


@pytest.fixture
def homework(subject, class_group, teacher):
    """Créer un devoir de test"""
    homework_type = HomeworkType.objects.create(
        name='Exercices',
        short_name='EX'
    )
    
    return Homework.objects.create(
        subject=subject,
        class_group=class_group,
        teacher=teacher,
        homework_type=homework_type,
        title='Exercices de mathématiques',
        description='Faire les exercices du manuel',
        assigned_date=date.today(),
        due_date=date.today() + timedelta(days=7),
        estimated_duration_minutes=30
    )


@pytest.fixture
def homework_with_students(homework, class_group):
    """Créer un devoir avec des élèves inscrits"""
    students = []
    for i in range(5):
        student = User.objects.create_user(
            email=f'student{i}@test.com',
            username=f'student{i}',
            password='testpass123',
            first_name=f'Student',
            last_name=f'{i}',
            user_type='student'
        )
        students.append(student)
        
        # Inscrire l'élève dans la classe
        class_group.students.create(
            student=student,
            is_active=True
        )
    
    return homework, students


@pytest.fixture
def class_with_homework(class_group, subject, teacher):
    """Créer une classe avec plusieurs devoirs"""
    homework_type = HomeworkType.objects.create(
        name='Devoir maison',
        short_name='DM'
    )
    
    homework_list = []
    for i in range(5):
        hw = Homework.objects.create(
            subject=subject,
            class_group=class_group,
            teacher=teacher,
            homework_type=homework_type,
            title=f'Devoir {i}',
            description=f'Description du devoir {i}',
            assigned_date=date.today(),
            due_date=date.today() + timedelta(days=i+1),
            estimated_duration_minutes=30 + i*10
        )
        homework_list.append(hw)
    
    return class_group, homework_list