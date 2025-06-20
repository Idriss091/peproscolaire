"""
Tests pour les modèles du cahier de textes
"""
import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from apps.homework.models import (
    LessonContent, HomeworkType, Homework,
    StudentWork, WorkloadAnalysis
)
from apps.schools.models import Class
from apps.timetable.models import Schedule, Subject
from apps.authentication.models import User


@pytest.mark.django_db
class TestLessonContent:
    """Tests pour le modèle LessonContent"""
    
    def test_create_lesson_content(self, schedule, teacher):
        """Test de création d'un contenu de cours"""
        lesson = LessonContent.objects.create(
            schedule=schedule,
            date=date.today(),
            title="Introduction aux fonctions",
            content="Définition et exemples de fonctions",
            created_by=teacher
        )
        
        assert lesson.title == "Introduction aux fonctions"
        assert not lesson.validated
        assert lesson.has_homework is False
    
    def test_date_validation(self, schedule):
        """Test de validation de la date (doit correspondre au jour du schedule)"""
        # Si le schedule est le lundi (0), la date doit être un lundi
        wrong_date = date.today()
        while wrong_date.weekday() != (schedule.time_slot.day + 1) % 7:
            wrong_date += timedelta(days=1)
        
        lesson = LessonContent(
            schedule=schedule,
            date=wrong_date,
            title="Test",
            content="Test"
        )
        
        with pytest.raises(ValidationError):
            lesson.clean()
    
    def test_unique_constraint(self, schedule, teacher):
        """Test de contrainte d'unicité schedule/date"""
        lesson_date = date.today()
        
        # Première création OK
        LessonContent.objects.create(
            schedule=schedule,
            date=lesson_date,
            title="Cours 1",
            content="Contenu 1",
            created_by=teacher
        )
        
        # Deuxième création doit échouer
        with pytest.raises(Exception):
            LessonContent.objects.create(
                schedule=schedule,
                date=lesson_date,
                title="Cours 2",
                content="Contenu 2",
                created_by=teacher
            )


@pytest.mark.django_db
class TestHomework:
    """Tests pour le modèle Homework"""
    
    def test_create_homework(self, subject, class_group, teacher):
        """Test de création d'un devoir"""
        homework_type = HomeworkType.objects.create(
            name="Exercices",
            short_name="EX"
        )
        
        homework = Homework.objects.create(
            subject=subject,
            class_group=class_group,
            teacher=teacher,
            homework_type=homework_type,
            title="Exercices sur les fonctions",
            description="Faire les exercices 1 à 5",
            assigned_date=date.today(),
            due_date=date.today() + timedelta(days=7)
        )
        
        assert homework.title == "Exercices sur les fonctions"
        assert homework.days_remaining >= 6
        assert not homework.is_overdue
    
    def test_due_date_validation(self, subject, class_group, teacher):
        """Test de validation de la date de rendu"""
        homework = Homework(
            subject=subject,
            class_group=class_group,
            teacher=teacher,
            title="Test",
            description="Test",
            assigned_date=date.today(),
            due_date=date.today() - timedelta(days=1)  # Date passée
        )
        
        with pytest.raises(ValidationError):
            homework.clean()
    
    def test_submission_rate(self, homework_with_students):
        """Test du calcul du taux de rendu"""
        homework, students = homework_with_students
        
        # Au début, taux = 0
        assert homework.submission_rate == 0
        
        # Créer des soumissions
        for i, student in enumerate(students[:3]):
            StudentWork.objects.create(
                homework=homework,
                student=student,
                status='submitted' if i < 2 else 'draft'
            )
        
        # Taux = 3/5 = 60%
        assert homework.submission_rate == 60.0


@pytest.mark.django_db
class TestStudentWork:
    """Tests pour le modèle StudentWork"""
    
    def test_create_student_work(self, homework, student):
        """Test de création d'un travail d'élève"""
        work = StudentWork.objects.create(
            homework=homework,
            student=student,
            content="Ma réponse aux exercices"
        )
        
        assert work.status == 'draft'
        assert work.submitted_at is None
    
    def test_submit_work(self, homework, student):
        """Test de soumission d'un travail"""
        work = StudentWork.objects.create(
            homework=homework,
            student=student
        )
        
        work.submit()
        
        assert work.status == 'submitted'
        assert work.submitted_at is not None
    
    def test_late_submission(self, student):
        """Test de soumission en retard"""
        # Créer un devoir avec date passée
        homework = Homework.objects.create(
            subject=Subject.objects.first(),
            class_group=Class.objects.first(),
            teacher=User.objects.filter(user_type='teacher').first(),
            title="Test",
            description="Test",
            due_date=date.today() - timedelta(days=1)
        )
        
        work = StudentWork.objects.create(
            homework=homework,
            student=student
        )
        
        work.submit()
        
        assert work.status == 'late'
    
    def test_file_validation(self, homework, student):
        """Test de validation du fichier"""
        # Homework avec limite de taille
        homework.max_file_size_mb = 1
        homework.allowed_file_types = 'pdf,doc'
        homework.save()
        
        work = StudentWork(
            homework=homework,
            student=student
        )
        
        # Simuler un fichier trop gros
        # TODO: Implémenter avec un vrai fichier de test
        
    def test_unique_constraint(self, homework, student):
        """Test de contrainte d'unicité homework/student"""
        # Premier travail OK
        StudentWork.objects.create(
            homework=homework,
            student=student
        )
        
        # Deuxième doit échouer
        with pytest.raises(Exception):
            StudentWork.objects.create(
                homework=homework,
                student=student
            )


@pytest.mark.django_db
class TestWorkloadAnalysis:
    """Tests pour l'analyse de charge de travail"""
    
    def test_workload_calculation(self, class_with_homework):
        """Test du calcul de charge de travail"""
        class_group, homework_list = class_with_homework
        
        analysis = WorkloadAnalysis.objects.create(
            class_group=class_group,
            date=date.today()
        )
        
        analysis.analyze()
        
        assert analysis.total_homework_count == len(homework_list)
        assert analysis.total_estimated_minutes == sum(
            hw.estimated_duration_minutes for hw in homework_list
        )
    
    def test_overload_detection(self, class_group):
        """Test de détection de surcharge"""
        # Créer beaucoup de devoirs
        subject = Subject.objects.first()
        teacher = User.objects.filter(user_type='teacher').first()
        
        for i in range(10):
            Homework.objects.create(
                subject=subject,
                class_group=class_group,
                teacher=teacher,
                title=f"Devoir {i}",
                description="Test",
                due_date=date.today() + timedelta(days=i % 7),
                estimated_duration_minutes=45
            )
        
        analysis = WorkloadAnalysis.objects.create(
            class_group=class_group,
            date=date.today()
        )
        
        analysis.analyze()
        
        assert analysis.is_overloaded
        assert analysis.overload_level in ['high', 'critical']
        assert analysis.recommendations != ''