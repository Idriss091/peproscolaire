# Generated by Django 5.0.1 on 2025-06-20 20:35

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('schools', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, verbose_name='Nom')),
                ('short_name', models.CharField(max_length=10, verbose_name='Abréviation')),
                ('color', models.CharField(default='#3498db', max_length=7, verbose_name='Couleur (hex)')),
                ('coefficient', models.DecimalField(decimal_places=1, default=1.0, max_digits=3, verbose_name='Coefficient')),
                ('is_optional', models.BooleanField(default=False, verbose_name='Matière optionnelle')),
            ],
            options={
                'verbose_name': 'Matière',
                'verbose_name_plural': 'Matières',
                'db_table': 'subjects',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50, verbose_name='Nom')),
                ('building', models.CharField(blank=True, max_length=50, verbose_name='Bâtiment')),
                ('floor', models.CharField(blank=True, max_length=20, verbose_name='Étage')),
                ('capacity', models.PositiveIntegerField(default=30, verbose_name='Capacité')),
                ('room_type', models.CharField(choices=[('classroom', 'Salle de classe'), ('laboratory', 'Laboratoire'), ('computer_room', 'Salle informatique'), ('gym', 'Gymnase'), ('library', 'CDI/Bibliothèque'), ('auditorium', 'Amphithéâtre')], default='classroom', max_length=50, verbose_name='Type de salle')),
                ('is_available', models.BooleanField(default=True, verbose_name='Disponible')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rooms', to='schools.school')),
            ],
            options={
                'verbose_name': 'Salle',
                'verbose_name_plural': 'Salles',
                'db_table': 'rooms',
                'ordering': ['building', 'name'],
                'unique_together': {('school', 'name')},
            },
        ),
        migrations.CreateModel(
            name='TimeSlot',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('day', models.IntegerField(choices=[(0, 'Lundi'), (1, 'Mardi'), (2, 'Mercredi'), (3, 'Jeudi'), (4, 'Vendredi'), (5, 'Samedi')], verbose_name='Jour')),
                ('start_time', models.TimeField(verbose_name='Heure de début')),
                ('end_time', models.TimeField(verbose_name='Heure de fin')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Ordre dans la journée')),
                ('is_break', models.BooleanField(default=False, verbose_name='Pause/Récréation')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='time_slots', to='schools.school')),
            ],
            options={
                'verbose_name': 'Créneau horaire',
                'verbose_name_plural': 'Créneaux horaires',
                'db_table': 'time_slots',
                'ordering': ['day', 'order', 'start_time'],
                'unique_together': {('school', 'day', 'start_time')},
            },
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('week_type', models.CharField(choices=[('A', 'Semaine A'), ('B', 'Semaine B'), ('*', 'Toutes les semaines')], default='*', max_length=1, verbose_name='Type de semaine')),
                ('start_date', models.DateField(blank=True, null=True, verbose_name='Date de début')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='Date de fin')),
                ('is_cancelled', models.BooleanField(default=False, verbose_name='Cours annulé')),
                ('academic_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='schools.academicyear')),
                ('class_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='schools.class')),
                ('room', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='schedules', to='timetable.room')),
                ('teacher', models.ForeignKey(limit_choices_to={'user_type': 'teacher'}, on_delete=django.db.models.deletion.CASCADE, related_name='teaching_schedules', to=settings.AUTH_USER_MODEL)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='timetable.subject')),
                ('time_slot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='timetable.timeslot')),
            ],
            options={
                'verbose_name': 'Cours',
                'verbose_name_plural': 'Cours',
                'db_table': 'schedules',
                'ordering': ['time_slot__day', 'time_slot__start_time'],
            },
        ),
        migrations.CreateModel(
            name='ScheduleModification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('date', models.DateField(verbose_name='Date de la modification')),
                ('modification_type', models.CharField(choices=[('cancelled', 'Annulé'), ('replaced', 'Remplacé'), ('room_changed', 'Changement de salle'), ('time_changed', "Changement d'horaire")], max_length=20, verbose_name='Type de modification')),
                ('new_start_time', models.TimeField(blank=True, null=True, verbose_name='Nouvelle heure de début')),
                ('new_end_time', models.TimeField(blank=True, null=True, verbose_name='Nouvelle heure de fin')),
                ('reason', models.TextField(blank=True, verbose_name='Raison de la modification')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_modifications', to=settings.AUTH_USER_MODEL)),
                ('new_room', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='timetable.room')),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modifications', to='timetable.schedule')),
                ('substitute_teacher', models.ForeignKey(blank=True, limit_choices_to={'user_type': 'teacher'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='substitute_schedules', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': "Modification d'emploi du temps",
                'verbose_name_plural': "Modifications d'emploi du temps",
                'db_table': 'schedule_modifications',
                'ordering': ['-date'],
                'unique_together': {('schedule', 'date')},
            },
        ),
    ]
