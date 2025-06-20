"""
Tests pour les tâches Celery des modules IA
"""
import pytest
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from celery.exceptions import Retry
from django.utils import timezone
from datetime import datetime, timedelta

from .tasks import (
    train_ml_model,
    analyze_student_risk,
    daily_risk_analysis,
    weekly_pattern_detection,
    generate_appreciation_task,
    check_and_send_alerts
)
from .models import RiskProfile, Alert, InterventionPlan
from apps.student_records.models import Student
from apps.tenants.models import Tenant

User = get_user_model()


class MLModelTrainingTaskTest(TestCase):
    """Tests pour les tâches d'entraînement des modèles ML"""
    
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test School",
            subdomain="test"
        )
    
    @patch('apps.ai_analytics.ml_models.ModelTrainer.train_dropout_model')
    def test_train_dropout_model_success(self, mock_train):
        """Test d'entraînement réussi du modèle de décrochage"""
        mock_train.return_value = {
            'success': True,
            'metrics': {
                'accuracy': 0.87,
                'precision': 0.82,
                'recall': 0.85,
                'f1_score': 0.83
            },
            'model_path': '/tmp/dropout_model.pkl',
            'training_time': 120.5
        }
        
        result = train_ml_model('dropout_risk', force_retrain=False)
        
        self.assertTrue(result['success'])
        self.assertIn('metrics', result)
        self.assertEqual(result['metrics']['accuracy'], 0.87)
        mock_train.assert_called_once_with(training_data=None, save_model=True)
    
    @patch('apps.ai_analytics.ml_models.ModelTrainer.train_dropout_model')
    def test_train_dropout_model_failure(self, mock_train):
        """Test d'échec d'entraînement"""
        mock_train.side_effect = Exception("Erreur d'entraînement")
        
        result = train_ml_model('dropout_risk')
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertEqual(result['error'], "Erreur d'entraînement")
    
    @patch('apps.ai_analytics.ml_models.ModelTrainer.train_performance_model')
    def test_train_performance_model(self, mock_train):
        """Test d'entraînement du modèle de performance"""
        mock_train.return_value = {
            'success': True,
            'metrics': {
                'mse': 0.15,
                'r2_score': 0.78
            }
        }
        
        result = train_ml_model('performance_prediction')
        
        self.assertTrue(result['success'])
        mock_train.assert_called_once()
    
    def test_train_invalid_model_type(self):
        """Test avec type de modèle invalide"""
        result = train_ml_model('invalid_model')
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('Type de modèle non supporté', result['error'])
    
    @patch('apps.ai_analytics.ml_models.ModelTrainer.train_dropout_model')
    def test_train_model_with_retry(self, mock_train):
        """Test de retry automatique en cas d'échec temporaire"""
        # Premier appel échoue, deuxième réussit
        mock_train.side_effect = [
            Exception("Erreur temporaire"),
            {
                'success': True,
                'metrics': {'accuracy': 0.85}
            }
        ]
        
        # Simuler le retry
        with patch('apps.ai_analytics.tasks.train_ml_model.retry') as mock_retry:
            mock_retry.side_effect = Retry("Retry")
            
            with self.assertRaises(Retry):
                train_ml_model('dropout_risk')
            
            mock_retry.assert_called_once()


class StudentRiskAnalysisTaskTest(TestCase):
    """Tests pour l'analyse de risque individuelle"""
    
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test School",
            subdomain="test"
        )
        
        self.student_user = User.objects.create_user(
            email="student@test.com",
            password="testpass123",
            first_name="Test",
            last_name="Student",
            user_type="student"
        )
        
        self.student = Student.objects.create(
            tenant=self.tenant,
            user=self.student_user,
            student_number="STU001",
            admission_date=timezone.now().date()
        )
    
    @patch('apps.ai_analytics.analyzers.collect_student_data')
    @patch('apps.ai_analytics.ml_models.DropoutRiskModel.predict_dropout_risk')
    def test_analyze_student_risk_success(self, mock_predict, mock_collect):
        """Test d'analyse de risque réussie"""
        # Mock des données collectées
        mock_collect.return_value = {
            'attendance_rate': 0.85,
            'average_grade': 12.5,
            'absences_count': 10,
            'late_arrivals': 5,
            'sanctions_count': 1
        }
        
        # Mock de la prédiction
        mock_predict.return_value = {
            'dropout_probability': 0.35,
            'risk_level': 'modéré',
            'risk_score': 0.35,
            'main_risk_factors': [
                {
                    'factor': 'Assiduité',
                    'value': 0.85,
                    'importance': 0.3,
                    'impact': 'positif'
                }
            ]
        }
        
        result = analyze_student_risk(str(self.student.id))
        
        self.assertTrue(result['success'])
        self.assertIn('risk_profile', result)
        self.assertEqual(result['risk_profile']['risk_level'], 'modéré')
        
        # Vérifier qu'un profil de risque a été créé/mis à jour
        risk_profile = RiskProfile.objects.filter(student=self.student).first()
        self.assertIsNotNone(risk_profile)
        self.assertEqual(risk_profile.risk_level, 'modéré')
    
    @patch('apps.ai_analytics.analyzers.collect_student_data')
    def test_analyze_student_risk_insufficient_data(self, mock_collect):
        """Test avec données insuffisantes"""
        mock_collect.return_value = {}
        
        result = analyze_student_risk(str(self.student.id))
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('Données insuffisantes', result['error'])
    
    def test_analyze_nonexistent_student(self):
        """Test avec étudiant inexistant"""
        fake_id = '12345678-1234-1234-1234-123456789012'
        
        result = analyze_student_risk(fake_id)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('Étudiant non trouvé', result['error'])
    
    @patch('apps.ai_analytics.analyzers.collect_student_data')
    @patch('apps.ai_analytics.ml_models.DropoutRiskModel.predict_dropout_risk')
    @patch('apps.ai_analytics.tasks.check_and_send_alerts.delay')
    def test_analyze_high_risk_triggers_alert(self, mock_alert_task, mock_predict, mock_collect):
        """Test qu'un risque élevé déclenche une alerte"""
        mock_collect.return_value = {
            'attendance_rate': 0.5,
            'average_grade': 6.0,
            'absences_count': 30
        }
        
        mock_predict.return_value = {
            'dropout_probability': 0.9,
            'risk_level': 'élevé',
            'risk_score': 0.9
        }
        
        analyze_student_risk(str(self.student.id))
        
        # Vérifier qu'une tâche d'alerte a été déclenchée
        mock_alert_task.assert_called()


class BulkAnalysisTaskTest(TestCase):
    """Tests pour les analyses en masse"""
    
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test School",
            subdomain="test"
        )
        
        # Créer plusieurs étudiants
        self.students = []
        for i in range(3):
            user = User.objects.create_user(
                email=f"student{i}@test.com",
                password="testpass123",
                first_name=f"Student{i}",
                last_name="Test",
                user_type="student"
            )
            student = Student.objects.create(
                tenant=self.tenant,
                user=user,
                student_number=f"STU00{i}",
                admission_date=timezone.now().date()
            )
            self.students.append(student)
    
    @patch('apps.ai_analytics.tasks.analyze_student_risk.delay')
    def test_daily_risk_analysis(self, mock_analyze):
        """Test de l'analyse quotidienne"""
        result = daily_risk_analysis()
        
        self.assertTrue(result['success'])
        self.assertGreater(result['students_analyzed'], 0)
        
        # Vérifier que l'analyse a été lancée pour chaque étudiant
        self.assertEqual(mock_analyze.call_count, len(self.students))
    
    @patch('apps.ai_analytics.analyzers.detect_patterns')
    def test_weekly_pattern_detection(self, mock_detect):
        """Test de détection de patterns hebdomadaires"""
        mock_detect.return_value = {
            'patterns_found': [
                {
                    'type': 'absence_spike',
                    'affected_students': 2,
                    'severity': 'medium'
                }
            ],
            'recommendations': [
                'Surveiller les absences en début de semaine'
            ]
        }
        
        result = weekly_pattern_detection()
        
        self.assertTrue(result['success'])
        self.assertIn('patterns', result)
        self.assertEqual(len(result['patterns']), 1)


class AppreciationGenerationTaskTest(TestCase):
    """Tests pour la génération d'appréciations"""
    
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test School",
            subdomain="test"
        )
        
        self.student_user = User.objects.create_user(
            email="student@test.com",
            password="testpass123",
            first_name="Marie",
            last_name="Dupont",
            user_type="student"
        )
        
        self.student = Student.objects.create(
            tenant=self.tenant,
            user=self.student_user,
            student_number="STU001",
            admission_date=timezone.now().date()
        )
    
    @patch('apps.ai_modules.appreciation_generator.AppreciationGenerator.generate_appreciation')
    def test_generate_appreciation_task_success(self, mock_generate):
        """Test de génération d'appréciation via tâche"""
        mock_generate.return_value = {
            'content': 'Excellente progression en mathématiques.',
            'confidence': 0.92,
            'metadata': {
                'type': 'bulletin',
                'generated_at': timezone.now().isoformat()
            }
        }
        
        result = generate_appreciation_task(
            str(self.student.id),
            'math',
            'T1',
            {'type': 'bulletin', 'tone': 'bienveillant'}
        )
        
        self.assertTrue(result['success'])
        self.assertIn('appreciation', result)
        self.assertEqual(result['appreciation']['confidence'], 0.92)
    
    @patch('apps.ai_modules.appreciation_generator.AppreciationGenerator.generate_appreciation')
    def test_generate_appreciation_task_failure(self, mock_generate):
        """Test d'échec de génération"""
        mock_generate.side_effect = Exception("Erreur de génération")
        
        result = generate_appreciation_task(
            str(self.student.id),
            'math',
            'T1'
        )
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)


class AlertsTaskTest(TestCase):
    """Tests pour les tâches de gestion d'alertes"""
    
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test School",
            subdomain="test"
        )
        
        self.student_user = User.objects.create_user(
            email="student@test.com",
            password="testpass123",
            first_name="Paul",
            last_name="Martin",
            user_type="student"
        )
        
        self.student = Student.objects.create(
            tenant=self.tenant,
            user=self.student_user,
            student_number="STU001",
            admission_date=timezone.now().date()
        )
        
        self.risk_profile = RiskProfile.objects.create(
            tenant=self.tenant,
            student=self.student,
            academic_year="2023-2024",
            risk_score=0.85,
            risk_level="élevé"
        )
    
    @patch('apps.messaging.tasks.send_notification.delay')
    def test_check_and_send_alerts_high_risk(self, mock_send):
        """Test d'envoi d'alertes pour risque élevé"""
        result = check_and_send_alerts(str(self.risk_profile.id))
        
        self.assertTrue(result['success'])
        self.assertGreater(result['alerts_created'], 0)
        
        # Vérifier qu'une alerte a été créée
        alert = Alert.objects.filter(risk_profile=self.risk_profile).first()
        self.assertIsNotNone(alert)
        self.assertEqual(alert.priority, 'high')
        
        # Vérifier qu'une notification a été envoyée
        mock_send.assert_called()
    
    def test_check_and_send_alerts_low_risk(self):
        """Test pour risque faible (pas d'alerte)"""
        # Modifier le profil pour un risque faible
        self.risk_profile.risk_score = 0.2
        self.risk_profile.risk_level = 'faible'
        self.risk_profile.save()
        
        result = check_and_send_alerts(str(self.risk_profile.id))
        
        self.assertTrue(result['success'])
        self.assertEqual(result['alerts_created'], 0)
    
    @patch('apps.messaging.tasks.send_notification.delay')
    def test_check_and_send_alerts_duplicate_prevention(self, mock_send):
        """Test de prévention des alertes en double"""
        # Créer une alerte existante
        Alert.objects.create(
            tenant=self.tenant,
            risk_profile=self.risk_profile,
            message="Alerte existante",
            priority="high",
            alert_type="risk_detection"
        )
        
        result = check_and_send_alerts(str(self.risk_profile.id))
        
        # Aucune nouvelle alerte ne devrait être créée
        self.assertEqual(result['alerts_created'], 0)
        
        # Vérifier qu'il n'y a toujours qu'une seule alerte
        alert_count = Alert.objects.filter(risk_profile=self.risk_profile).count()
        self.assertEqual(alert_count, 1)


class TaskIntegrationTest(TestCase):
    """Tests d'intégration entre les différentes tâches"""
    
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test School",
            subdomain="test"
        )
        
        self.student_user = User.objects.create_user(
            email="student@test.com",
            password="testpass123",
            first_name="Integration",
            last_name="Test",
            user_type="student"
        )
        
        self.student = Student.objects.create(
            tenant=self.tenant,
            user=self.student_user,
            student_number="STU001",
            admission_date=timezone.now().date()
        )
    
    @patch('apps.ai_analytics.analyzers.collect_student_data')
    @patch('apps.ai_analytics.ml_models.DropoutRiskModel.predict_dropout_risk')
    @patch('apps.messaging.tasks.send_notification.delay')
    def test_full_risk_analysis_workflow(self, mock_notify, mock_predict, mock_collect):
        """Test du workflow complet d'analyse de risque"""
        # Setup des mocks
        mock_collect.return_value = {
            'attendance_rate': 0.5,
            'average_grade': 7.0,
            'absences_count': 25
        }
        
        mock_predict.return_value = {
            'dropout_probability': 0.88,
            'risk_level': 'élevé',
            'risk_score': 0.88,
            'main_risk_factors': [
                {
                    'factor': 'Absentéisme',
                    'importance': 0.4,
                    'impact': 'négatif'
                }
            ]
        }
        
        # Lancer l'analyse
        analysis_result = analyze_student_risk(str(self.student.id))
        
        # Vérifications
        self.assertTrue(analysis_result['success'])
        
        # Vérifier que le profil de risque a été créé
        risk_profile = RiskProfile.objects.filter(student=self.student).first()
        self.assertIsNotNone(risk_profile)
        self.assertEqual(risk_profile.risk_level, 'élevé')
        
        # Lancer la vérification d'alertes
        alert_result = check_and_send_alerts(str(risk_profile.id))
        
        # Vérifier qu'une alerte a été créée et envoyée
        self.assertTrue(alert_result['success'])
        self.assertGreater(alert_result['alerts_created'], 0)
        
        alert = Alert.objects.filter(risk_profile=risk_profile).first()
        self.assertIsNotNone(alert)
        self.assertEqual(alert.priority, 'high')
        
        # Vérifier qu'une notification a été envoyée
        mock_notify.assert_called()


# Tests de performance et de charge
class PerformanceTest(TestCase):
    """Tests de performance pour les tâches critiques"""
    
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Performance Test School",
            subdomain="perf-test"
        )
        
        # Créer un grand nombre d'étudiants pour les tests de performance
        self.students = []
        for i in range(50):  # 50 étudiants pour le test
            user = User.objects.create_user(
                email=f"perf_student{i}@test.com",
                password="testpass123",
                first_name=f"Student{i}",
                last_name="Perf",
                user_type="student"
            )
            student = Student.objects.create(
                tenant=self.tenant,
                user=user,
                student_number=f"PERF{i:03d}",
                admission_date=timezone.now().date()
            )
            self.students.append(student)
    
    @patch('apps.ai_analytics.tasks.analyze_student_risk.delay')
    def test_daily_analysis_performance(self, mock_analyze):
        """Test de performance pour l'analyse quotidienne"""
        import time
        
        start_time = time.time()
        result = daily_risk_analysis()
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        self.assertTrue(result['success'])
        self.assertLess(execution_time, 10.0)  # Doit s'exécuter en moins de 10 secondes
        self.assertEqual(mock_analyze.call_count, len(self.students))
    
    def test_memory_usage_bulk_operations(self):
        """Test d'utilisation mémoire pour les opérations en masse"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Créer beaucoup de profils de risque
        profiles = []
        for student in self.students:
            profile = RiskProfile.objects.create(
                tenant=self.tenant,
                student=student,
                academic_year="2023-2024",
                risk_score=0.5,
                risk_level="modéré"
            )
            profiles.append(profile)
        
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after - memory_before
        
        # L'augmentation de mémoire ne devrait pas être excessive
        self.assertLess(memory_increase, 100)  # Moins de 100MB d'augmentation