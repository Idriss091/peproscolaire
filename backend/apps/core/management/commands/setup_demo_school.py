"""
Commande de génération de données de démonstration pour PeproScolaire
Crée un établissement complet avec élèves, professeurs, emplois du temps, notes, etc.
"""
import random
from datetime import datetime, date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from faker import Faker

# Imports des modèles
from apps.authentication.models import User, UserProfile
from apps.schools.models import School, AcademicYear, Level, Class, StudentClassEnrollment
from apps.timetable.models import Subject, Room, TimeSlot, Schedule
from apps.homework.models import HomeworkType, LessonContent, Homework, StudentWork
from apps.grades.models import (
    EvaluationType, GradingPeriod, Evaluation, Grade, 
    SubjectAverage, GeneralAverage, Competence
)
from apps.messaging.models import Message, MessageRecipient

fake = Faker('fr_FR')


class Command(BaseCommand):
    help = 'Génère un jeu de données complet pour la démonstration de PeproScolaire'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force la recréation même si des données existent déjà',
        )
        parser.add_argument(
            '--students-per-class',
            type=int,
            default=20,
            help='Nombre d\'élèves par classe (défaut: 20)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🏫 Génération des données de démonstration PeproScolaire')
        )
        
        force = options['force']
        students_per_class = options['students_per_class']
        
        # Vérifier si des données existent déjà
        if not force and School.objects.exists():
            raise CommandError(
                'Des données existent déjà. Utilisez --force pour les remplacer.'
            )
        
        try:
            with transaction.atomic():
                self.stdout.write('📊 Suppression des anciennes données...')
                if force:
                    self._cleanup_existing_data()
                
                self.stdout.write('🏫 Création de l\'établissement...')
                school = self._create_school()
                
                self.stdout.write('📅 Création de l\'année scolaire...')
                academic_year = self._create_academic_year(school)
                
                self.stdout.write('📚 Création des niveaux et classes...')
                levels, classes = self._create_levels_and_classes(school, academic_year)
                
                self.stdout.write('📖 Création des matières...')
                subjects = self._create_subjects()
                
                self.stdout.write('🏛️ Création des salles...')
                rooms = self._create_rooms(school)
                
                self.stdout.write('⏰ Création des créneaux horaires...')
                time_slots = self._create_time_slots(school)
                
                self.stdout.write('👨‍🏫 Création des professeurs...')
                teachers = self._create_teachers()
                
                self.stdout.write('👨‍🎓 Création des élèves...')
                students = self._create_students(classes, students_per_class)
                
                self.stdout.write('👨‍👩‍👧 Création des parents...')
                parents = self._create_parents(students)
                
                self.stdout.write('📋 Création des emplois du temps...')
                schedules = self._create_schedules(
                    academic_year, classes, subjects, teachers, rooms, time_slots
                )
                
                self.stdout.write('📝 Création des types d\'évaluation...')
                evaluation_types = self._create_evaluation_types()
                
                self.stdout.write('📊 Création des périodes de notation...')
                grading_periods = self._create_grading_periods(academic_year)
                
                self.stdout.write('✅ Création des évaluations et notes...')
                evaluations = self._create_evaluations_and_grades(
                    classes, subjects, teachers, grading_periods, evaluation_types, students
                )
                
                self.stdout.write('📖 Création des types de devoirs...')
                homework_types = self._create_homework_types()
                
                self.stdout.write('📝 Création des devoirs...')
                homeworks = self._create_homework(
                    schedules, subjects, classes, teachers, homework_types, students
                )
                
                self.stdout.write('💬 Création de la messagerie...')
                self._create_messages(teachers, students, parents)
                
                self.stdout.write('🧮 Calcul des moyennes...')
                self._calculate_averages(students, grading_periods, classes)
                
                self._display_summary(school, academic_year, classes, teachers, students, parents)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur lors de la génération: {str(e)}')
            )
            raise

    def _cleanup_existing_data(self):
        """Supprime les données existantes"""
        from django.db import connection
        
        # Supprimer dans l'ordre pour éviter les contraintes FK
        models_to_clean = [
            # Messages et relations
            MessageRecipient, Message,
            # Évaluations et notes  
            Grade, Evaluation, SubjectAverage, GeneralAverage,
            # Devoirs
            StudentWork, Homework,
            # Emplois du temps
            Schedule,
            # Relations élèves-classes
            StudentClassEnrollment,
            # Structure scolaire
            Class, TimeSlot, Room, AcademicYear, School,
            # Matières et niveaux
            Subject, Level,
            # Utilisateurs (sauf ceux de démo)
            # User - on garde les comptes de démo
        ]
        
        for model in models_to_clean:
            model.objects.all().delete()
        
        # Supprimer tous les utilisateurs sauf les comptes de démo
        User.objects.exclude(
            username__in=['demo', 'admin', 'eleve', 'parent']
        ).delete()
        
        # Reset des IDs auto-increment pour SQLite
        if connection.vendor == 'sqlite':
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM sqlite_sequence WHERE name NOT LIKE 'auth_%' AND name NOT LIKE 'django_%'")

    def _create_school(self):
        """Crée l'établissement de démonstration"""
        school, created = School.objects.get_or_create(
            subdomain="demo",
            defaults={
                'name': "Collège Demo PeproScolaire",
                'school_type': 'college',
                'address': "123 Rue de la Démo",
                'postal_code': "75001",
                'city': "Paris",
                'phone': "0123456789",
                'email': "contact@demo-peproscolaire.fr",
                'website': "https://demo-peproscolaire.fr",
                'is_active': True
            }
        )
        return school

    def _create_academic_year(self, school):
        """Crée l'année scolaire actuelle"""
        current_year = datetime.now().year
        next_year = current_year + 1
        
        academic_year, created = AcademicYear.objects.get_or_create(
            school=school,
            name=f"{current_year}-{next_year}",
            defaults={
                'start_date': date(current_year, 9, 1),
                'end_date': date(next_year, 7, 15),
                'is_current': True
            }
        )
        return academic_year

    def _create_levels_and_classes(self, school, academic_year):
        """Crée les niveaux et classes"""
        # Niveaux collège
        levels_data = [
            ('6ème', '6e', 1),
            ('5ème', '5e', 2),
            ('4ème', '4e', 3),
            ('3ème', '3e', 4),
        ]
        
        levels = []
        for name, short_name, order in levels_data:
            level, created = Level.objects.get_or_create(
                name=name,
                short_name=short_name,
                school_type='college',
                defaults={
                    'order': order
                }
            )
            levels.append(level)
        
        # Classes - Noms uniques par école/année
        classes = []
        
        for level in levels:
            if level.short_name == '6e':
                # 6ème A et B
                for suffix in ['A', 'B']:
                    class_name = f"6{suffix}"
                    class_obj, created = Class.objects.get_or_create(
                        school=school,
                        academic_year=academic_year,
                        level=level,
                        name=class_name,
                        defaults={'max_students': 25}
                    )
                    classes.append(class_obj)
            else:
                # Une seule classe pour les autres niveaux
                class_name = f"{level.short_name[0]}A"  # 5A, 4A, 3A
                class_obj, created = Class.objects.get_or_create(
                    school=school,
                    academic_year=academic_year,
                    level=level,
                    name=class_name,
                    defaults={'max_students': 25}
                )
                classes.append(class_obj)
        
        return levels, classes

    def _create_subjects(self):
        """Crée les matières du collège"""
        subjects_data = [
            ('Français', 'FR', '#e74c3c', 4.0),
            ('Mathématiques', 'MATH', '#3498db', 4.0),
            ('Histoire-Géographie', 'HG', '#9b59b6', 3.0),
            ('Sciences de la Vie et de la Terre', 'SVT', '#27ae60', 2.0),
            ('Physique-Chimie', 'PC', '#f39c12', 2.0),
            ('Anglais', 'ANG', '#e67e22', 3.0),
            ('Espagnol', 'ESP', '#2c3e50', 2.5),
            ('Éducation Physique et Sportive', 'EPS', '#1abc9c', 1.0),
            ('Arts Plastiques', 'AP', '#34495e', 1.0),
            ('Éducation Musicale', 'MUS', '#8e44ad', 1.0),
            ('Technologie', 'TECH', '#16a085', 2.0),
        ]
        
        subjects = []
        for name, short_name, color, coefficient in subjects_data:
            subject = Subject.objects.create(
                name=name,
                short_name=short_name,
                color=color,
                coefficient=Decimal(str(coefficient))
            )
            subjects.append(subject)
        
        return subjects

    def _create_rooms(self, school):
        """Crée les salles de l'établissement"""
        rooms_data = [
            ('101', 'Bâtiment A', 'classroom', 30),
            ('102', 'Bâtiment A', 'classroom', 30),
            ('103', 'Bâtiment A', 'classroom', 30),
            ('201', 'Bâtiment A', 'classroom', 30),
            ('202', 'Bâtiment A', 'classroom', 30),
            ('Lab SVT', 'Bâtiment B', 'laboratory', 20),
            ('Lab PC', 'Bâtiment B', 'laboratory', 20),
            ('Salle Info', 'Bâtiment B', 'computer_room', 25),
            ('Gymnase', 'Bâtiment C', 'gym', 50),
            ('CDI', 'Bâtiment A', 'library', 40),
            ('Salle Arts', 'Bâtiment B', 'classroom', 25),
            ('Salle Musique', 'Bâtiment B', 'classroom', 25),
        ]
        
        rooms = []
        for name, building, room_type, capacity in rooms_data:
            room = Room.objects.create(
                school=school,
                name=name,
                building=building,
                room_type=room_type,
                capacity=capacity
            )
            rooms.append(room)
        
        return rooms

    def _create_time_slots(self, school):
        """Crée les créneaux horaires"""
        # Horaires type collège
        time_slots_data = [
            # Lundi
            (0, '08:00', '09:00', 1),
            (0, '09:00', '10:00', 2),
            (0, '10:00', '10:15', 3, True),  # Récréation
            (0, '10:15', '11:15', 4),
            (0, '11:15', '12:15', 5),
            (0, '12:15', '13:45', 6, True),  # Pause déjeuner
            (0, '13:45', '14:45', 7),
            (0, '14:45', '15:45', 8),
            (0, '15:45', '16:00', 9, True),  # Récréation
            (0, '16:00', '17:00', 10),
        ]
        
        # Répliquer pour toute la semaine (lundi à vendredi)
        all_slots = []
        for day in range(5):  # Lundi à Vendredi
            for _, start, end, order, *is_break in time_slots_data:
                if day == 2 and order >= 7:  # Mercredi après-midi libre
                    continue
                all_slots.append((
                    day, start, end, order, len(is_break) > 0 and is_break[0]
                ))
        
        time_slots = []
        for day, start_time, end_time, order, is_break in all_slots:
            time_slot = TimeSlot.objects.create(
                school=school,
                day=day,
                start_time=datetime.strptime(start_time, '%H:%M').time(),
                end_time=datetime.strptime(end_time, '%H:%M').time(),
                order=order,
                is_break=is_break if is_break else False
            )
            time_slots.append(time_slot)
        
        return time_slots

    def _create_teachers(self):
        """Crée les professeurs"""
        teachers_data = [
            ('Marie', 'Dubois', 'marie.dubois@demo.fr', ['Français']),
            ('Pierre', 'Martin', 'pierre.martin@demo.fr', ['Mathématiques']),
            ('Sophie', 'Lefebvre', 'sophie.lefebvre@demo.fr', ['Histoire-Géographie']),
            ('Jean', 'Moreau', 'jean.moreau@demo.fr', ['Sciences de la Vie et de la Terre']),
            ('Claire', 'Simon', 'claire.simon@demo.fr', ['Physique-Chimie']),
            ('David', 'Laurent', 'david.laurent@demo.fr', ['Anglais']),
            ('Carmen', 'Garcia', 'carmen.garcia@demo.fr', ['Espagnol']),
            ('Marc', 'Roux', 'marc.roux@demo.fr', ['Éducation Physique et Sportive']),
            ('Julie', 'Fournier', 'julie.fournier@demo.fr', ['Arts Plastiques', 'Éducation Musicale']),
            ('Thomas', 'Michel', 'thomas.michel@demo.fr', ['Technologie']),
        ]
        
        teachers = []
        for first_name, last_name, email, subject_names in teachers_data:
            teacher = User.objects.create_user(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                user_type='teacher',
                password='demo123',
                is_active=True
            )
            
            # Créer le profil
            UserProfile.objects.create(
                user=teacher,
                bio=f"Professeur de {', '.join(subject_names)}",
                email_notifications=True
            )
            
            teachers.append(teacher)
        
        # Ajouter le compte professeur de démo existant
        demo_teacher = User.objects.filter(username='demo').first()
        if demo_teacher:
            teachers.append(demo_teacher)
        
        return teachers

    def _create_students(self, classes, students_per_class):
        """Crée les élèves"""
        students = []
        
        for class_obj in classes:
            for i in range(students_per_class):
                # Générer des noms français réalistes
                first_name = fake.first_name()
                last_name = fake.last_name()
                
                # Email basé sur le nom et classe
                email = f"{first_name.lower()}.{last_name.lower()}.{class_obj.level.short_name}{class_obj.name.lower()}@eleves-demo.fr"
                username = f"{first_name.lower()}.{last_name.lower()}.{class_obj.level.short_name}{class_obj.name.lower()}"
                
                student = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    user_type='student',
                    password='demo123',
                    is_active=True
                )
                
                # Créer le profil avec date de naissance
                birth_year = datetime.now().year - (10 + int(class_obj.level.order))
                birth_date = fake.date_of_birth(
                    minimum_age=10 + int(class_obj.level.order),
                    maximum_age=11 + int(class_obj.level.order)
                )
                
                UserProfile.objects.create(
                    user=student,
                    date_of_birth=birth_date,
                    address=fake.address(),
                    postal_code=fake.postcode(),
                    city=fake.city(),
                    emergency_contact_name=fake.name(),
                    emergency_contact_phone=fake.phone_number()
                )
                
                # Inscrire l'élève dans la classe
                StudentClassEnrollment.objects.create(
                    student=student,
                    class_group=class_obj,
                    is_active=True
                )
                
                students.append(student)
        
        # Ajouter le compte élève de démo existant
        demo_student = User.objects.filter(username='eleve').first()
        if demo_student and classes:
            # L'inscrire dans la première classe
            StudentClassEnrollment.objects.get_or_create(
                student=demo_student,
                class_group=classes[0],
                defaults={'is_active': True}
            )
            students.append(demo_student)
        
        return students

    def _create_parents(self, students):
        """Crée les parents (certains peuvent avoir plusieurs enfants)"""
        parents = []
        used_emails = set()
        
        # Grouper les élèves par nom de famille pour créer des fratries
        families = {}
        for student in students:
            last_name = student.last_name
            if last_name not in families:
                families[last_name] = []
            families[last_name].append(student)
        
        for last_name, family_students in families.items():
            # Créer 1 ou 2 parents par famille
            num_parents = random.choice([1, 2])  # Familles monoparentales ou biparentales
            
            for parent_num in range(num_parents):
                # Noms des parents
                if parent_num == 0:
                    first_name = fake.first_name_male() if random.choice([True, False]) else fake.first_name_female()
                    parent_last_name = last_name
                else:
                    first_name = fake.first_name_female() if parent_num == 1 else fake.first_name_male()
                    parent_last_name = fake.last_name() if random.choice([True, False]) else last_name
                
                email = f"{first_name.lower()}.{parent_last_name.lower()}@parents-demo.fr"
                
                # Éviter les doublons d'email
                counter = 1
                original_email = email
                while email in used_emails:
                    email = f"{original_email.split('@')[0]}{counter}@parents-demo.fr"
                    counter += 1
                used_emails.add(email)
                
                parent = User.objects.create_user(
                    username=email,
                    email=email,
                    first_name=first_name,
                    last_name=parent_last_name,
                    user_type='parent',
                    password='demo123',
                    is_active=True
                )
                
                # Profil parent
                UserProfile.objects.create(
                    user=parent,
                    address=fake.address(),
                    postal_code=fake.postcode(),
                    city=fake.city(),
                    bio=f"Parent de {', '.join([s.first_name for s in family_students])}"
                )
                
                parents.append(parent)
        
        # Ajouter le compte parent de démo existant
        demo_parent = User.objects.filter(username='parent').first()
        if demo_parent:
            parents.append(demo_parent)
        
        return parents

    def _create_schedules(self, academic_year, classes, subjects, teachers, rooms, time_slots):
        """Crée les emplois du temps"""
        schedules = []
        
        # Matières par niveau
        subjects_by_level = {
            '6e': ['Français', 'Mathématiques', 'Histoire-Géographie', 'Anglais', 'Arts Plastiques', 'Éducation Musicale', 'Éducation Physique et Sportive'],
            '5e': ['Français', 'Mathématiques', 'Histoire-Géographie', 'Anglais', 'Espagnol', 'Sciences de la Vie et de la Terre', 'Technologie', 'Éducation Physique et Sportive'],
            '4e': ['Français', 'Mathématiques', 'Histoire-Géographie', 'Anglais', 'Espagnol', 'Sciences de la Vie et de la Terre', 'Physique-Chimie', 'Technologie', 'Éducation Physique et Sportive'],
            '3e': ['Français', 'Mathématiques', 'Histoire-Géographie', 'Anglais', 'Espagnol', 'Sciences de la Vie et de la Terre', 'Physique-Chimie', 'Technologie', 'Éducation Physique et Sportive']
        }
        
        # Créneaux disponibles (pas les pauses)
        available_slots = [ts for ts in time_slots if not ts.is_break]
        
        # Assigner les professeurs principaux
        for i, class_obj in enumerate(classes):
            if i < len(teachers):
                class_obj.main_teacher = teachers[i]
                class_obj.save()
        
        # Pour chaque classe, créer l'emploi du temps
        for class_obj in classes:
            level_code = class_obj.level.short_name
            if level_code not in subjects_by_level:
                continue
                
            subject_names = subjects_by_level[level_code]
            used_slots = set()
            
            # Distribuer les matières sur la semaine
            for subject_name in subject_names:
                subject = next((s for s in subjects if s.name == subject_name), None)
                if not subject:
                    continue
                
                # Trouver un professeur pour cette matière
                teacher = self._find_teacher_for_subject(teachers, subject_name)
                if not teacher:
                    continue
                
                # Nombre d'heures par semaine selon la matière
                hours_per_week = self._get_hours_per_week(subject_name, level_code)
                
                # Assigner les créneaux
                for _ in range(hours_per_week):
                    # Trouver un créneau disponible
                    available = [slot for slot in available_slots 
                               if (slot.day, slot.order) not in used_slots
                               and not self._has_conflict(slot, teacher, class_obj)]
                    
                    if not available:
                        continue
                    
                    time_slot = random.choice(available)
                    room = self._find_suitable_room(rooms, subject_name)
                    
                    schedule = Schedule.objects.create(
                        academic_year=academic_year,
                        class_group=class_obj,
                        subject=subject,
                        teacher=teacher,
                        room=room,
                        time_slot=time_slot,
                        week_type='*'
                    )
                    
                    schedules.append(schedule)
                    used_slots.add((time_slot.day, time_slot.order))
        
        return schedules

    def _find_teacher_for_subject(self, teachers, subject_name):
        """Trouve un professeur pour une matière donnée"""
        subject_mapping = {
            'Français': ['marie.dubois@demo.fr'],
            'Mathématiques': ['pierre.martin@demo.fr'],
            'Histoire-Géographie': ['sophie.lefebvre@demo.fr'],
            'Sciences de la Vie et de la Terre': ['jean.moreau@demo.fr'],
            'Physique-Chimie': ['claire.simon@demo.fr'],
            'Anglais': ['david.laurent@demo.fr'],
            'Espagnol': ['carmen.garcia@demo.fr'],
            'Éducation Physique et Sportive': ['marc.roux@demo.fr'],
            'Arts Plastiques': ['julie.fournier@demo.fr'],
            'Éducation Musicale': ['julie.fournier@demo.fr'],
            'Technologie': ['thomas.michel@demo.fr'],
        }
        
        if subject_name in subject_mapping:
            for email in subject_mapping[subject_name]:
                teacher = next((t for t in teachers if t.email == email), None)
                if teacher:
                    return teacher
        
        # Fallback sur un professeur aléatoire
        return random.choice(teachers) if teachers else None

    def _get_hours_per_week(self, subject_name, level_code):
        """Retourne le nombre d'heures par semaine pour une matière"""
        hours_mapping = {
            'Français': 4,
            'Mathématiques': 4,
            'Histoire-Géographie': 3,
            'Anglais': 3,
            'Sciences de la Vie et de la Terre': 2,
            'Physique-Chimie': 2,
            'Espagnol': 2,
            'Technologie': 2,
            'Éducation Physique et Sportive': 3,
            'Arts Plastiques': 1,
            'Éducation Musicale': 1,
        }
        return hours_mapping.get(subject_name, 1)

    def _has_conflict(self, time_slot, teacher, class_group):
        """Vérifie s'il y a un conflit d'emploi du temps"""
        # Simplifié pour la démo
        return False

    def _find_suitable_room(self, rooms, subject_name):
        """Trouve une salle adaptée à la matière"""
        room_preferences = {
            'Sciences de la Vie et de la Terre': 'laboratory',
            'Physique-Chimie': 'laboratory',
            'Technologie': 'computer_room',
            'Éducation Physique et Sportive': 'gym',
            'Arts Plastiques': 'classroom',
            'Éducation Musicale': 'classroom',
        }
        
        preferred_type = room_preferences.get(subject_name, 'classroom')
        suitable_rooms = [r for r in rooms if r.room_type == preferred_type]
        
        if suitable_rooms:
            return random.choice(suitable_rooms)
        
        # Fallback sur n'importe quelle salle
        return random.choice(rooms) if rooms else None

    def _create_evaluation_types(self):
        """Crée les types d'évaluation"""
        types_data = [
            ('Contrôle', 'DS', 2.0, '#e74c3c'),
            ('Devoir Maison', 'DM', 1.0, '#3498db'),
            ('Interrogation', 'IE', 1.0, '#f39c12'),
            ('Exposé', 'EXP', 1.5, '#9b59b6'),
            ('Projet', 'PROJ', 2.0, '#27ae60'),
        ]
        
        evaluation_types = []
        for name, short_name, coefficient, color in types_data:
            eval_type = EvaluationType.objects.create(
                name=name,
                short_name=short_name,
                default_coefficient=Decimal(str(coefficient)),
                color=color
            )
            evaluation_types.append(eval_type)
        
        return evaluation_types

    def _create_grading_periods(self, academic_year):
        """Crée les trimestres"""
        current_year = academic_year.start_date.year
        
        periods_data = [
            ('1er Trimestre', 1, date(current_year, 9, 1), date(current_year, 12, 20)),
            ('2ème Trimestre', 2, date(current_year + 1, 1, 5), date(current_year + 1, 4, 5)),
            ('3ème Trimestre', 3, date(current_year + 1, 4, 20), date(current_year + 1, 7, 15)),
        ]
        
        grading_periods = []
        for name, number, start_date, end_date in periods_data:
            period = GradingPeriod.objects.create(
                academic_year=academic_year,
                name=name,
                number=number,
                start_date=start_date,
                end_date=end_date,
                is_active=True
            )
            grading_periods.append(period)
        
        return grading_periods

    def _create_evaluations_and_grades(self, classes, subjects, teachers, grading_periods, evaluation_types, students):
        """Crée les évaluations et notes"""
        evaluations = []
        
        # Pour chaque classe et matière, créer des évaluations
        for class_obj in classes:
            for subject in subjects:
                # Trouver le professeur de cette matière
                teacher = self._find_teacher_for_subject(teachers, subject.name)
                if not teacher:
                    continue
                
                # Créer 2-3 évaluations par trimestre
                for period in grading_periods[:2]:  # Seulement 1er et 2ème trimestre
                    num_evaluations = random.randint(2, 4)
                    
                    for eval_num in range(num_evaluations):
                        # Date d'évaluation dans la période
                        days_in_period = (period.end_date - period.start_date).days
                        random_day = random.randint(10, days_in_period - 10)
                        eval_date = period.start_date + timedelta(days=random_day)
                        
                        eval_type = random.choice(evaluation_types)
                        
                        evaluation = Evaluation.objects.create(
                            title=f"{eval_type.name} {subject.short_name} n°{eval_num + 1}",
                            description=f"Évaluation de {subject.name} - {period.name}",
                            evaluation_type=eval_type,
                            subject=subject,
                            class_group=class_obj,
                            teacher=teacher,
                            grading_period=period,
                            date=eval_date,
                            max_score=Decimal('20.00'),
                            coefficient=eval_type.default_coefficient,
                            is_graded=True,
                            grades_published=True
                        )
                        evaluations.append(evaluation)
                        
                        # Créer les notes pour tous les élèves de la classe
                        class_students = [s for s in students 
                                        if StudentClassEnrollment.objects.filter(
                                            student=s, class_group=class_obj, is_active=True
                                        ).exists()]
                        
                        for student in class_students:
                            # Générer une note réaliste
                            base_score = self._generate_realistic_grade(subject.name, class_obj.level.short_name)
                            
                            # Quelques élèves absents (5%)
                            is_absent = random.random() < 0.05
                            
                            grade = Grade.objects.create(
                                evaluation=evaluation,
                                student=student,
                                score=None if is_absent else Decimal(str(base_score)),
                                is_absent=is_absent,
                                graded_by=teacher,
                                graded_at=timezone.now()
                            )
        
        return evaluations

    def _generate_realistic_grade(self, subject_name, level_code):
        """Génère une note réaliste selon la matière et le niveau"""
        # Moyennes par matière et niveau
        base_averages = {
            ('Français', '6e'): 13.5,
            ('Mathématiques', '6e'): 12.8,
            ('Français', '5e'): 13.2,
            ('Mathématiques', '5e'): 12.5,
            ('Français', '4e'): 12.8,
            ('Mathématiques', '4e'): 12.2,
            ('Français', '3e'): 12.5,
            ('Mathématiques', '3e'): 11.8,
        }
        
        # Moyenne par défaut
        base_avg = base_averages.get((subject_name, level_code), 13.0)
        
        # Distribution normale avec écart-type de 3
        grade = random.normalvariate(base_avg, 3.0)
        
        # Borner entre 0 et 20
        grade = max(0, min(20, grade))
        
        # Arrondir à 0.5 près
        return round(grade * 2) / 2

    def _create_homework_types(self):
        """Crée les types de devoirs"""
        types_data = [
            ('Exercices', 'EX', 'edit', 3, '#3498db'),
            ('Leçon à apprendre', 'LECON', 'book', 1, '#27ae60'),
            ('Recherche', 'RECH', 'search', 7, '#9b59b6'),
            ('Exposé à préparer', 'EXPO', 'presentation', 14, '#e74c3c'),
            ('Devoir Maison', 'DM', 'assignment', 7, '#f39c12'),
        ]
        
        homework_types = []
        for name, short_name, icon, duration, color in types_data:
            hw_type = HomeworkType.objects.create(
                name=name,
                short_name=short_name,
                icon=icon,
                default_duration_days=duration,
                color=color
            )
            homework_types.append(hw_type)
        
        return homework_types

    def _create_homework(self, schedules, subjects, classes, teachers, homework_types, students):
        """Crée les devoirs"""
        homeworks = []
        
        # Pour chaque cours dans l'emploi du temps
        for schedule in schedules[:50]:  # Limiter pour la démo
            # 30% de chance d'avoir un devoir
            if random.random() > 0.3:
                continue
            
            # Date du cours (simulation sur les 3 dernières semaines)
            today = date.today()
            lesson_date = today - timedelta(days=random.randint(1, 21))
            
            # Date de rendu (1 à 7 jours après)
            due_date = lesson_date + timedelta(days=random.randint(1, 7))
            
            # Type de devoir
            homework_type = random.choice(homework_types)
            
            # Contenu du devoir selon la matière
            homework_content = self._generate_homework_content(schedule.subject.name, schedule.class_group.level.short_name)
            
            homework = Homework.objects.create(
                subject=schedule.subject,
                class_group=schedule.class_group,
                teacher=schedule.teacher,
                homework_type=homework_type,
                title=homework_content['title'],
                description=homework_content['description'],
                instructions=homework_content['instructions'],
                assigned_date=lesson_date,
                due_date=due_date,
                estimated_duration_minutes=random.randint(20, 90),
                difficulty=random.choice(['easy', 'medium', 'hard']),
                is_graded=homework_type.name == 'Devoir Maison'
            )
            homeworks.append(homework)
            
            # Créer quelques rendus d'élèves (60% des élèves rendent)
            class_students = [s for s in students 
                            if StudentClassEnrollment.objects.filter(
                                student=s, class_group=schedule.class_group, is_active=True
                            ).exists()]
            
            for student in class_students:
                if random.random() < 0.6:  # 60% rendent
                    status = random.choice(['submitted', 'late', 'draft'])
                    submitted_at = None
                    
                    if status in ['submitted', 'late']:
                        # Date de soumission
                        if status == 'submitted':
                            submitted_at = timezone.now() - timedelta(
                                days=random.randint(0, (due_date - lesson_date).days)
                            )
                        else:  # late
                            submitted_at = timezone.now() - timedelta(
                                days=random.randint(0, 3)
                            )
                    
                    StudentWork.objects.create(
                        homework=homework,
                        student=student,
                        status=status,
                        submitted_at=submitted_at,
                        content=f"Travail rendu par {student.get_full_name()}",
                        time_spent_minutes=random.randint(15, 120)
                    )
        
        return homeworks

    def _generate_homework_content(self, subject_name, level_code):
        """Génère du contenu de devoir réaliste"""
        content_templates = {
            'Français': {
                'title': [
                    "Rédaction : portrait d'un personnage",
                    "Analyse de texte - Victor Hugo",
                    "Conjugaison : le passé composé",
                    "Lecture : chapitre 3 du livre",
                ],
                'description': [
                    "Rédiger un portrait physique et moral d'un personnage de votre choix",
                    "Analyser le texte distribué en classe et répondre aux questions",
                    "Conjuguer les verbes de la liste au passé composé",
                    "Lire le chapitre 3 et préparer un résumé oral",
                ],
            },
            'Mathématiques': {
                'title': [
                    "Exercices sur les fractions",
                    "Problème de géométrie",
                    "Calcul mental - tables de multiplication",
                    "Révisions : équations du premier degré",
                ],
                'description': [
                    "Faire les exercices 12 à 18 page 45 du manuel",
                    "Résoudre le problème de construction géométrique",
                    "Apprendre les tables de 6, 7, 8 et 9",
                    "Réviser les méthodes de résolution d'équations",
                ],
            },
            'Histoire-Géographie': {
                'title': [
                    "L'Empire romain : frise chronologique",
                    "Les climats dans le monde",
                    "Révolutions française : causes",
                    "Carte de l'Europe",
                ],
                'description': [
                    "Réaliser une frise chronologique de l'Empire romain",
                    "Compléter la carte des climats mondiaux",
                    "Rechercher les causes de la Révolution française",
                    "Apprendre les capitales européennes",
                ],
            }
        }
        
        if subject_name in content_templates:
            templates = content_templates[subject_name]
            title = random.choice(templates['title'])
            description = random.choice(templates['description'])
        else:
            title = f"Devoir de {subject_name}"
            description = f"Travail à faire en {subject_name} pour la prochaine séance"
        
        instructions = "Soyez précis dans vos réponses. N'hésitez pas à poser des questions si nécessaire."
        
        return {
            'title': title,
            'description': description,
            'instructions': instructions
        }

    def _create_messages(self, teachers, students, parents):
        """Crée des messages de démonstration"""
        # Messages types
        message_templates = [
            {
                'subject': 'Absence de votre enfant',
                'body': 'Bonjour,\n\nVotre enfant était absent aujourd\'hui. Merci de justifier cette absence.\n\nCordialement',
                'from_type': 'teacher',
                'to_type': 'parent'
            },
            {
                'subject': 'Excellents résultats',
                'body': 'Bonjour,\n\nFélicitations ! Votre enfant a obtenu d\'excellents résultats ce trimestre.\n\nCordialement',
                'from_type': 'teacher',
                'to_type': 'parent'
            },
            {
                'subject': 'Devoir non rendu',
                'body': 'Bonjour,\n\nLe devoir était à rendre aujourd\'hui. Merci de le apporter dès que possible.\n\nCordialement',
                'from_type': 'teacher',
                'to_type': 'student'
            },
            {
                'subject': 'Réunion parents-professeurs',
                'body': 'Bonjour,\n\nLa réunion parents-professeurs aura lieu le vendredi 15 mars à 18h.\n\nCordialement',
                'from_type': 'teacher',
                'to_type': 'parent'
            }
        ]
        
        # Créer 20 messages aléatoires
        for _ in range(20):
            template = random.choice(message_templates)
            
            # Sélectionner expéditeur et destinataire
            if template['from_type'] == 'teacher':
                sender = random.choice(teachers)
                if template['to_type'] == 'parent':
                    recipient = random.choice(parents)
                else:  # student
                    recipient = random.choice(students)
            else:
                continue  # Pour simplifier, seuls les profs envoient des messages
            
            # Créer le message
            message = Message.objects.create(
                sender=sender,
                subject=template['subject'],
                body=template['body'],
                sent_at=timezone.now() - timedelta(days=random.randint(1, 30)),
                priority='normal'
            )
            
            # Créer le destinataire
            MessageRecipient.objects.create(
                message=message,
                recipient=recipient,
                is_read=random.choice([True, False]),
                read_at=timezone.now() - timedelta(days=random.randint(0, 5)) if random.choice([True, False]) else None,
                folder='inbox'
            )

    def _calculate_averages(self, students, grading_periods, classes):
        """Calcule les moyennes des élèves"""
        for period in grading_periods[:2]:  # 1er et 2ème trimestre
            for class_obj in classes:
                class_students = [s for s in students 
                                if StudentClassEnrollment.objects.filter(
                                    student=s, class_group=class_obj, is_active=True
                                ).exists()]
                
                for student in class_students:
                    # Calculer les moyennes par matière
                    subjects_with_grades = Grade.objects.filter(
                        student=student,
                        evaluation__grading_period=period,
                        score__isnull=False
                    ).values_list('evaluation__subject', flat=True).distinct()
                    
                    for subject_id in subjects_with_grades:
                        subject_avg, created = SubjectAverage.objects.get_or_create(
                            student=student,
                            subject_id=subject_id,
                            grading_period=period,
                            class_group=class_obj
                        )
                        subject_avg.calculate_average()
                        subject_avg.calculate_rank()
                    
                    # Calculer la moyenne générale
                    general_avg, created = GeneralAverage.objects.get_or_create(
                        student=student,
                        grading_period=period,
                        class_group=class_obj
                    )
                    general_avg.calculate_average()
                    general_avg.calculate_rank()

    def _display_summary(self, school, academic_year, classes, teachers, students, parents):
        """Affiche un résumé des données créées"""
        self.stdout.write(
            self.style.SUCCESS('\n🎉 Génération terminée avec succès !')
        )
        
        self.stdout.write(f'\n📊 Résumé des données créées:')
        self.stdout.write(f'   🏫 Établissement: {school.name}')
        self.stdout.write(f'   📅 Année scolaire: {academic_year.name}')
        self.stdout.write(f'   🏛️ Classes: {len(classes)}')
        self.stdout.write(f'   👨‍🏫 Professeurs: {len(teachers)}')
        self.stdout.write(f'   👨‍🎓 Élèves: {len(students)}')
        self.stdout.write(f'   👨‍👩‍👧 Parents: {len(parents)}')
        
        self.stdout.write(f'\n📚 Contenu pédagogique:')
        self.stdout.write(f'   📋 Emplois du temps: {Schedule.objects.count()} créneaux')
        self.stdout.write(f'   ✅ Évaluations: {Evaluation.objects.count()}')
        self.stdout.write(f'   📊 Notes: {Grade.objects.count()}')
        self.stdout.write(f'   📝 Devoirs: {Homework.objects.count()}')
        self.stdout.write(f'   💬 Messages: {Message.objects.count()}')
        
        self.stdout.write(f'\n🔑 Comptes de démonstration:')
        self.stdout.write(f'   👨‍🏫 Professeur: demo / demo123')
        self.stdout.write(f'   👨‍🎓 Élève: eleve / demo123')
        self.stdout.write(f'   👨‍👩‍👧 Parent: parent / demo123')
        self.stdout.write(f'   🔧 Admin: admin / demo123')
        
        self.stdout.write(f'\n🌐 Accès application:')
        self.stdout.write(f'   Frontend: http://localhost:5173/')
        self.stdout.write(f'   Backend API: http://127.0.0.1:8000/')
        self.stdout.write(f'   Admin Django: http://127.0.0.1:8000/admin/')
        
        self.stdout.write(
            self.style.SUCCESS('\n✨ Votre environnement de démonstration est prêt !')
        )