"""
Tests d'intégration pour les modules IA
"""
import pytest
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from django.utils import timezone
from datetime import timedelta
import json

from .models import RiskProfile, Alert, InterventionPlan
from .tasks import analyze_student_risk, check_and_send_alerts
from apps.schools.models import School, Class
from apps.student_records.models import Student
from apps.tenants.models import Tenant

User = get_user_model()


class AIModulesIntegrationTest(TransactionTestCase):
    """Tests d'intégration pour le workflow complet des modules IA"""
    
    def setUp(self):
        # Configuration de base
        self.tenant = Tenant.objects.create(
            name="Integration Test School",
            subdomain="integration-test",
            description="École pour tests d'intégration"
        )
        
        self.school = School.objects.create(
            tenant=self.tenant,
            name="École d'Intégration",
            address="123 Rue Test",
            phone="0123456789",
            email="test@integration.com"
        )
        
        self.class_obj = Class.objects.create(
            tenant=self.tenant,
            school=self.school,
            name="6ème Test",
            level="6ème",
            academic_year="2023-2024"
        )
        
        # Utilisateurs
        self.admin_user = User.objects.create_user(
            email="admin@integration.com",
            password="testpass123",
            first_name="Admin",
            last_name="Integration",
            user_type="admin"
        )
        
        self.teacher_user = User.objects.create_user(
            email="teacher@integration.com",
            password="testpass123",
            first_name="Teacher",
            last_name="Integration",
            user_type="teacher"
        )
        
        self.student_user = User.objects.create_user(
            email="student@integration.com",
            password="testpass123",
            first_name="Student",
            last_name="AtRisk",
            user_type="student"
        )
        
        self.student = Student.objects.create(
            tenant=self.tenant,
            user=self.student_user,
            student_number="INT001",
            admission_date=timezone.now().date()
        )
        
        self.client = APIClient()
    
    @patch('apps.ai_analytics.analyzers.collect_student_data')
    @patch('apps.ai_analytics.ml_models.DropoutRiskModel.predict_dropout_risk')
    @patch('apps.messaging.tasks.send_notification.delay')
    def test_complete_risk_analysis_workflow(self, mock_notify, mock_predict, mock_collect):
        """Test du workflow complet : analyse → profil → alerte → intervention"""
        
        # 1. Setup des mocks pour simuler un élève à haut risque
        mock_collect.return_value = {
            'attendance_rate': 0.45,
            'average_grade': 6.5,
            'absences_count': 35,
            'late_arrivals': 20,
            'sanctions_count': 8,
            'homework_completion_rate': 0.3,
            'participation_rate': 0.2
        }
        
        mock_predict.return_value = {
            'dropout_probability': 0.92,
            'risk_level': 'élevé',
            'risk_score': 0.92,
            'main_risk_factors': [
                {
                    'factor': 'Absentéisme',
                    'value': 0.45,
                    'importance': 0.4,
                    'impact': 'très négatif'
                },
                {
                    'factor': 'Notes faibles',
                    'value': 6.5,
                    'importance': 0.3,
                    'impact': 'négatif'
                }
            ],
            'recommendations': [
                {
                    'priority': 'critical',
                    'action': 'Intervention urgente',
                    'details': 'Convoquer la famille immédiatement'
                }
            ]
        }
        
        # 2. Lancer l'analyse de risque
        analysis_result = analyze_student_risk(str(self.student.id))
        
        # Vérifications de l'analyse
        self.assertTrue(analysis_result['success'])
        self.assertEqual(analysis_result['risk_profile']['risk_level'], 'élevé')
        
        # 3. Vérifier que le profil de risque a été créé
        risk_profile = RiskProfile.objects.filter(student=self.student).first()
        self.assertIsNotNone(risk_profile)
        self.assertEqual(risk_profile.risk_level, 'élevé')
        self.assertGreater(risk_profile.risk_score, 0.9)
        
        # 4. Déclencher la vérification d'alertes
        alert_result = check_and_send_alerts(str(risk_profile.id))
        
        # Vérifications des alertes
        self.assertTrue(alert_result['success'])
        self.assertGreater(alert_result['alerts_created'], 0)
        
        # 5. Vérifier qu'une alerte a été créée
        alert = Alert.objects.filter(risk_profile=risk_profile).first()
        self.assertIsNotNone(alert)
        self.assertEqual(alert.priority, 'high')
        self.assertFalse(alert.is_acknowledged)
        
        # 6. Vérifier qu'une notification a été envoyée
        mock_notify.assert_called()
        
        # 7. Simuler la création d'un plan d'intervention via l'API
        self.client.force_authenticate(user=self.teacher_user)
        
        intervention_data = {
            'risk_profile': str(risk_profile.id),
            'title': 'Plan d\'intervention urgent',
            'description': 'Accompagnement intensif pour Student AtRisk',
            'start_date': timezone.now().date().isoformat(),
            'end_date': (timezone.now().date() + timedelta(days=60)).isoformat(),
            'objectives': [
                'Améliorer l\'assiduité à 85%',
                'Remonter la moyenne à 10/20',
                'Réduire les sanctions'
            ],
            'planned_actions': [
                'Entretien hebdomadaire avec l\'élève',
                'Rencontre avec les parents',
                'Suivi par le conseiller d\'éducation',
                'Cours de soutien'
            ],
            'resources_needed': 'Heures de soutien supplémentaires',
            'success_criteria': 'Amélioration mesurable de l\'assiduité et des notes'
        }
        
        intervention_url = reverse('ai_analytics:intervention-plans-list')
        response = self.client.post(intervention_url, intervention_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 8. Vérifier que le plan d'intervention a été créé
        intervention_plan = InterventionPlan.objects.filter(risk_profile=risk_profile).first()
        self.assertIsNotNone(intervention_plan)
        self.assertEqual(intervention_plan.title, 'Plan d\'intervention urgent')
        self.assertEqual(intervention_plan.status, 'en_cours')
        self.assertEqual(len(intervention_plan.objectives), 3)
        
        # 9. Acquitter l'alerte
        acknowledge_url = reverse('ai_analytics:alerts-acknowledge', kwargs={'pk': alert.id})
        acknowledge_data = {
            'actions_taken': 'Plan d\'intervention créé et famille convoquée'
        }
        response = self.client.post(acknowledge_url, acknowledge_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 10. Vérifier que l'alerte a été acquittée
        alert.refresh_from_db()
        self.assertTrue(alert.is_acknowledged)
        self.assertEqual(alert.acknowledged_by, self.teacher_user)
        self.assertIsNotNone(alert.acknowledged_at)
    
    def test_appreciation_generation_workflow(self):
        """Test du workflow de génération d'appréciations"""
        
        self.client.force_authenticate(user=self.teacher_user)
        
        # 1. Générer une appréciation simple
        appreciation_url = reverse('ai_analytics:generate-appreciation')
        appreciation_data = {
            'student_id': str(self.student.id),
            'subject_id': 'math',
            'period_id': 'T1',
            'options': {
                'type': 'bulletin',
                'tone': 'bienveillant',
                'length': 'standard',
                'focus_areas': ['notes', 'comportement'],
                'temperature': 0.7
            }
        }
        
        with patch('apps.ai_modules.appreciation_generator.AppreciationGenerator.generate_appreciation') as mock_generate:
            mock_generate.return_value = {
                'content': 'Student AtRisk montre des difficultés en mathématiques mais fait preuve de volonté. Il serait bénéfique de renforcer le travail personnel et de solliciter de l\'aide.',
                'confidence': 0.85,
                'metadata': {
                    'type': 'bulletin',
                    'tone': 'bienveillant',
                    'length': 'standard',
                    'generated_at': timezone.now().isoformat(),
                    'model_version': '1.0',
                    'focus_areas': ['notes', 'comportement']
                }
            }
            
            response = self.client.post(appreciation_url, appreciation_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('appreciation', response.data)
        self.assertEqual(response.data['student']['name'], 'Student AtRisk')
        
        # 2. Générer des appréciations multiples pour une classe
        multiple_url = reverse('ai_analytics:generate-multiple-appreciations')
        multiple_data = {
            'class_id': str(self.class_obj.id),
            'subject_id': 'french',
            'period_id': 'T2',
            'options': {
                'type': 'conseil_classe',
                'tone': 'motivant',
                'length': 'détaillée'
            }
        }
        
        with patch('apps.ai_modules.appreciation_generator.AppreciationGenerator.generate_appreciation') as mock_generate:
            mock_generate.return_value = {
                'content': 'En français, Student AtRisk doit fournir plus d\'efforts pour améliorer son expression écrite.',
                'confidence': 0.78,
                'metadata': {
                    'type': 'conseil_classe',
                    'tone': 'motivant',
                    'length': 'détaillée',
                    'generated_at': timezone.now().isoformat(),
                    'model_version': '1.0'
                }
            }
            
            response = self.client.post(multiple_url, multiple_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertGreater(response.data['total_students'], 0)
    
    def test_model_training_workflow(self):
        """Test du workflow d'entraînement des modèles"""
        
        self.client.force_authenticate(user=self.admin_user)
        
        # 1. Vérifier le statut initial des modèles
        status_url = reverse('ai_analytics:ai-model-status')
        response = self.client.get(status_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('models', response.data)
        
        # 2. Lancer l'entraînement du modèle de décrochage
        train_url = reverse('ai_analytics:train-ai-model')
        train_data = {
            'model_type': 'dropout_risk',
            'force_retrain': True
        }
        
        with patch('apps.ai_analytics.tasks.train_ml_model.delay') as mock_train:
            mock_train.return_value.id = 'training-task-123'
            
            response = self.client.post(train_url, train_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('task_id', response.data)
        self.assertEqual(response.data['task_id'], 'training-task-123')
        
        # 3. Vérifier les métriques du dashboard
        metrics_url = reverse('ai_analytics:ai-dashboard-metrics')
        response = self.client.get(metrics_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('model_performance', response.data)
        self.assertIn('risk_distribution', response.data)
        self.assertIn('total_profiles', response.data)
    
    def test_api_permissions_and_security(self):
        """Test des permissions et de la sécurité des APIs"""
        
        # 1. Test sans authentification
        status_url = reverse('ai_analytics:ai-model-status')
        response = self.client.get(status_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # 2. Test avec utilisateur étudiant (permissions limitées)
        self.client.force_authenticate(user=self.student_user)
        
        train_url = reverse('ai_analytics:train-ai-model')
        train_data = {'model_type': 'dropout_risk'}
        response = self.client.post(train_url, train_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 3. Test avec utilisateur enseignant (permissions moyennes)
        self.client.force_authenticate(user=self.teacher_user)
        
        # Peut voir le statut
        response = self.client.get(status_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Ne peut pas entraîner
        response = self.client.post(train_url, train_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 4. Test avec administrateur (toutes permissions)
        self.client.force_authenticate(user=self.admin_user)
        
        with patch('apps.ai_analytics.tasks.train_ml_model.delay') as mock_train:
            mock_train.return_value.id = 'admin-task-456'
            response = self.client.post(train_url, train_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    @patch('apps.ai_analytics.analyzers.collect_student_data')
    @patch('apps.ai_analytics.ml_models.DropoutRiskModel.predict_dropout_risk')
    def test_bulk_analysis_performance(self, mock_predict, mock_collect):
        """Test de performance pour l'analyse en masse"""
        
        # Créer plusieurs étudiants
        students = []
        for i in range(10):  # 10 étudiants pour le test
            user = User.objects.create_user(
                email=f"bulk_student_{i}@test.com",
                password="testpass123",
                first_name=f"Student{i}",
                last_name="Bulk",
                user_type="student"
            )
            student = Student.objects.create(
                tenant=self.tenant,
                user=user,
                student_number=f"BULK{i:03d}",
                admission_date=timezone.now().date()
            )
            students.append(student)
        
        # Setup des mocks
        mock_collect.return_value = {
            'attendance_rate': 0.8,
            'average_grade': 12.0,
            'absences_count': 10
        }
        
        mock_predict.return_value = {
            'dropout_probability': 0.3,
            'risk_level': 'faible',
            'risk_score': 0.3
        }
        
        # Lancer l'analyse pour tous les étudiants
        import time
        start_time = time.time()
        
        results = []
        for student in students:
            result = analyze_student_risk(str(student.id))
            results.append(result)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Vérifications
        self.assertEqual(len(results), 10)
        self.assertTrue(all(result['success'] for result in results))
        self.assertLess(execution_time, 30.0)  # Moins de 30 secondes pour 10 étudiants
        
        # Vérifier que tous les profils ont été créés
        created_profiles = RiskProfile.objects.filter(
            student__in=students
        ).count()
        self.assertEqual(created_profiles, 10)
    
    def test_error_handling_and_recovery(self):
        """Test de gestion d'erreurs et de récupération"""
        
        self.client.force_authenticate(user=self.teacher_user)
        
        # 1. Test avec étudiant inexistant
        appreciation_url = reverse('ai_analytics:generate-appreciation')
        bad_data = {
            'student_id': '12345678-1234-1234-1234-123456789012',
            'subject_id': 'math',
            'period_id': 'T1'
        }
        
        response = self.client.post(appreciation_url, bad_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # 2. Test avec données invalides
        bad_data = {
            'student_id': 'invalid-uuid',
            'subject_id': '',
            'period_id': ''
        }
        
        response = self.client.post(appreciation_url, bad_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # 3. Test de prédiction avec données insuffisantes
        with patch('apps.ai_analytics.analyzers.collect_student_data') as mock_collect:
            mock_collect.return_value = {}  # Pas de données
            
            result = analyze_student_risk(str(self.student.id))
            self.assertFalse(result['success'])
            self.assertIn('Données insuffisantes', result['error'])
    
    def test_data_consistency_across_operations(self):
        """Test de cohérence des données entre les opérations"""
        
        self.client.force_authenticate(user=self.teacher_user)
        
        # 1. Créer un profil de risque via analyse
        with patch('apps.ai_analytics.analyzers.collect_student_data') as mock_collect, \
             patch('apps.ai_analytics.ml_models.DropoutRiskModel.predict_dropout_risk') as mock_predict:
            
            mock_collect.return_value = {
                'attendance_rate': 0.7,
                'average_grade': 11.0,
                'absences_count': 15
            }
            
            mock_predict.return_value = {
                'dropout_probability': 0.6,
                'risk_level': 'modéré',
                'risk_score': 0.6
            }
            
            analyze_student_risk(str(self.student.id))
        
        # 2. Vérifier que le profil existe
        risk_profile = RiskProfile.objects.get(student=self.student)
        self.assertEqual(risk_profile.risk_level, 'modéré')
        
        # 3. Prédire à nouveau le risque via API
        predict_url = reverse('ai_analytics:predict-student-risk')
        predict_data = {'student_id': str(self.student.id)}
        
        with patch('apps.ai_analytics.ml_models.DropoutRiskModel.predict_dropout_risk') as mock_predict:
            mock_predict.return_value = {
                'dropout_probability': 0.65,
                'risk_level': 'modéré',
                'risk_score': 0.65,
                'main_risk_factors': [],
                'recommendations': []
            }
            
            response = self.client.post(predict_url, predict_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['prediction']['risk_level'], 'modéré')
        
        # 4. Vérifier la cohérence du profil
        risk_profile.refresh_from_db()
        self.assertEqual(risk_profile.risk_level, 'modéré')
        
        # 5. Vérifier les métriques du dashboard
        metrics_url = reverse('ai_analytics:ai-dashboard-metrics')
        response = self.client.get(metrics_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data['total_profiles'], 0)
        
        # Le profil modéré doit être comptabilisé
        risk_dist = response.data['risk_distribution']
        self.assertGreater(risk_dist['moderate'], 0)


class PerformanceIntegrationTest(TestCase):
    """Tests de performance pour les opérations critiques"""
    
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Performance Test",
            subdomain="perf-test"
        )
        
        # Créer de nombreux étudiants
        self.students = []
        for i in range(50):
            user = User.objects.create_user(
                email=f"perf_student_{i}@test.com",
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
    
    def test_dashboard_metrics_performance(self):
        """Test de performance pour le calcul des métriques"""
        
        # Créer des profils de risque
        for i, student in enumerate(self.students):
            risk_level = ['faible', 'modéré', 'élevé'][i % 3]
            risk_score = [0.2, 0.5, 0.8][i % 3]
            
            RiskProfile.objects.create(
                tenant=self.tenant,
                student=student,
                academic_year="2023-2024",
                risk_score=risk_score,
                risk_level=risk_level
            )
        
        # Mesurer le temps de calcul des métriques
        import time
        from django.db import connection
        
        start_time = time.time()
        start_queries = len(connection.queries)
        
        # Simuler l'appel API
        from .views import ai_dashboard_metrics
        from django.test import RequestFactory
        from django.contrib.auth import get_user_model
        
        factory = RequestFactory()
        request = factory.get('/ai-analytics/ai/dashboard/metrics/')
        request.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test",
            user_type="teacher"
        )
        
        # Mock du tenant
        request.tenant = self.tenant
        
        response = ai_dashboard_metrics(request)
        
        end_time = time.time()
        end_queries = len(connection.queries)
        
        execution_time = end_time - start_time
        queries_count = end_queries - start_queries
        
        # Assertions de performance
        self.assertLess(execution_time, 2.0)  # Moins de 2 secondes
        self.assertLess(queries_count, 10)  # Moins de 10 requêtes SQL
        
        # Vérifier la réponse
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertEqual(response_data['total_profiles'], 50)
        
        # Vérifier la distribution
        risk_dist = response_data['risk_distribution']
        expected_count_per_level = 50 // 3  # Environ 16-17 par niveau
        self.assertGreater(risk_dist['low'], 10)
        self.assertGreater(risk_dist['moderate'], 10)
        self.assertGreater(risk_dist['high'], 10)