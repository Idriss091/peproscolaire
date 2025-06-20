"""
Tests pour les vues de l'API AI Analytics
"""
import pytest
import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone

from .models import RiskProfile, Alert, InterventionPlan
from apps.schools.models import School, Class
from apps.student_records.models import Student
from apps.tenants.models import Tenant

User = get_user_model()


class AIAnalyticsAPITestCase(TestCase):
    """Classe de base pour les tests d'API AI Analytics"""
    
    def setUp(self):
        # Créer un tenant de test
        self.tenant = Tenant.objects.create(
            name="Test School",
            subdomain="test",
            description="École de test"
        )
        
        # Créer une école
        self.school = School.objects.create(
            tenant=self.tenant,
            name="École Test",
            address="123 Rue Test",
            phone="0123456789",
            email="test@example.com"
        )
        
        # Créer des utilisateurs
        self.admin_user = User.objects.create_user(
            email="admin@test.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            user_type="admin"
        )
        
        self.teacher_user = User.objects.create_user(
            email="teacher@test.com",
            password="testpass123",
            first_name="Teacher",
            last_name="User",
            user_type="teacher"
        )
        
        self.student_user = User.objects.create_user(
            email="student@test.com",
            password="testpass123",
            first_name="Student",
            last_name="User",
            user_type="student"
        )
        
        # Créer un étudiant
        self.student = Student.objects.create(
            tenant=self.tenant,
            user=self.student_user,
            student_number="STU001",
            admission_date=timezone.now().date()
        )
        
        # Client API
        self.client = APIClient()


class GenerateAppreciationAPITest(AIAnalyticsAPITestCase):
    """Tests pour l'endpoint de génération d'appréciations"""
    
    def setUp(self):
        super().setUp()
        self.url = reverse('ai_analytics:generate-appreciation')
    
    def test_generate_appreciation_success(self):
        """Test de génération d'appréciation réussie"""
        self.client.force_authenticate(user=self.teacher_user)
        
        data = {
            'student_id': str(self.student.id),
            'subject_id': 'math',
            'period_id': 'T1',
            'options': {
                'type': 'bulletin',
                'tone': 'bienveillant',
                'length': 'standard'
            }
        }
        
        with patch('apps.ai_modules.appreciation_generator.AppreciationGenerator.generate_appreciation') as mock_generate:
            mock_generate.return_value = {
                'content': 'Excellente progression en mathématiques. L\'élève fait preuve d\'un engagement remarquable.',
                'confidence': 0.92,
                'metadata': {
                    'type': 'bulletin',
                    'tone': 'bienveillant',
                    'length': 'standard',
                    'generated_at': timezone.now().isoformat(),
                    'model_version': '1.0'
                }
            }
            
            response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('appreciation', response.data)
        self.assertIn('student', response.data)
        self.assertEqual(response.data['student']['name'], 'Student User')
    
    def test_generate_appreciation_missing_student(self):
        """Test avec étudiant inexistant"""
        self.client.force_authenticate(user=self.teacher_user)
        
        data = {
            'student_id': '12345678-1234-1234-1234-123456789012',
            'subject_id': 'math',
            'period_id': 'T1'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_generate_appreciation_unauthorized(self):
        """Test sans authentification"""
        data = {
            'student_id': str(self.student.id),
            'subject_id': 'math',
            'period_id': 'T1'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_generate_appreciation_invalid_data(self):
        """Test avec données invalides"""
        self.client.force_authenticate(user=self.teacher_user)
        
        data = {
            'student_id': 'invalid-id',
            'subject_id': '',
            'period_id': ''
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class GenerateMultipleAppreciationsAPITest(AIAnalyticsAPITestCase):
    """Tests pour l'endpoint de génération multiple d'appréciations"""
    
    def setUp(self):
        super().setUp()
        self.url = reverse('ai_analytics:generate-multiple-appreciations')
        
        # Créer des étudiants supplémentaires
        self.student2_user = User.objects.create_user(
            email="student2@test.com",
            password="testpass123",
            first_name="Student2",
            last_name="User",
            user_type="student"
        )
        
        self.student2 = Student.objects.create(
            tenant=self.tenant,
            user=self.student2_user,
            student_number="STU002",
            admission_date=timezone.now().date()
        )
    
    def test_generate_multiple_appreciations_success(self):
        """Test de génération multiple réussie"""
        self.client.force_authenticate(user=self.teacher_user)
        
        data = {
            'student_ids': [str(self.student.id), str(self.student2.id)],
            'subject_id': 'french',
            'period_id': 'T2',
            'options': {
                'type': 'bulletin',
                'tone': 'motivant',
                'length': 'détaillée'
            }
        }
        
        with patch('apps.ai_modules.appreciation_generator.AppreciationGenerator.generate_appreciation') as mock_generate:
            mock_generate.side_effect = [
                {
                    'content': 'Très bon travail en français.',
                    'confidence': 0.88,
                    'metadata': {'type': 'bulletin', 'generated_at': timezone.now().isoformat()}
                },
                {
                    'content': 'Progrès notable en expression écrite.',
                    'confidence': 0.85,
                    'metadata': {'type': 'bulletin', 'generated_at': timezone.now().isoformat()}
                }
            ]
            
            response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['total_students'], 2)
        self.assertEqual(response.data['successful_generations'], 2)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_generate_multiple_appreciations_partial_failure(self):
        """Test avec échecs partiels"""
        self.client.force_authenticate(user=self.teacher_user)
        
        data = {
            'student_ids': [str(self.student.id), str(self.student2.id)],
            'subject_id': 'math',
            'period_id': 'T1'
        }
        
        with patch('apps.ai_modules.appreciation_generator.AppreciationGenerator.generate_appreciation') as mock_generate:
            mock_generate.side_effect = [
                {
                    'content': 'Appréciation générée avec succès.',
                    'confidence': 0.9,
                    'metadata': {'generated_at': timezone.now().isoformat()}
                },
                Exception("Erreur de génération")
            ]
            
            response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['successful_generations'], 1)
        self.assertEqual(response.data['failed_generations'], 1)


class PredictStudentRiskAPITest(AIAnalyticsAPITestCase):
    """Tests pour l'endpoint de prédiction de risque"""
    
    def setUp(self):
        super().setUp()
        self.url = reverse('ai_analytics:predict-student-risk')
    
    def test_predict_student_risk_success(self):
        """Test de prédiction de risque réussie"""
        self.client.force_authenticate(user=self.teacher_user)
        
        data = {
            'student_id': str(self.student.id)
        }
        
        with patch('apps.ai_analytics.ml_models.DropoutRiskModel.predict_dropout_risk') as mock_predict:
            mock_predict.return_value = {
                'dropout_probability': 0.25,
                'risk_level': 'faible',
                'risk_score': 0.25,
                'main_risk_factors': [
                    {
                        'factor': 'Assiduité',
                        'value': 0.95,
                        'importance': 0.3,
                        'impact': 'positif'
                    }
                ],
                'recommendations': [
                    {
                        'priority': 'low',
                        'action': 'Maintenir les bonnes habitudes',
                        'details': 'Continuer sur cette voie'
                    }
                ]
            }
            
            response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('student', response.data)
        self.assertIn('prediction', response.data)
        self.assertEqual(response.data['prediction']['risk_level'], 'faible')
    
    def test_predict_student_risk_high_risk(self):
        """Test de prédiction pour risque élevé"""
        self.client.force_authenticate(user=self.teacher_user)
        
        data = {
            'student_id': str(self.student.id)
        }
        
        with patch('apps.ai_analytics.ml_models.DropoutRiskModel.predict_dropout_risk') as mock_predict:
            mock_predict.return_value = {
                'dropout_probability': 0.85,
                'risk_level': 'élevé',
                'risk_score': 0.85,
                'main_risk_factors': [
                    {
                        'factor': 'Absentéisme',
                        'value': 0.4,
                        'importance': 0.4,
                        'impact': 'négatif'
                    }
                ],
                'recommendations': [
                    {
                        'priority': 'high',
                        'action': 'Intervention immédiate',
                        'details': 'Planifier un entretien avec l\'élève et sa famille'
                    }
                ]
            }
            
            response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['prediction']['risk_level'], 'élevé')
        self.assertGreater(response.data['prediction']['dropout_probability'], 0.8)


class AIModelStatusAPITest(AIAnalyticsAPITestCase):
    """Tests pour l'endpoint de statut des modèles IA"""
    
    def setUp(self):
        super().setUp()
        self.url = reverse('ai_analytics:ai-model-status')
    
    def test_get_model_status_success(self):
        """Test de récupération du statut des modèles"""
        self.client.force_authenticate(user=self.teacher_user)
        
        with patch('apps.ai_analytics.ml_models.DropoutRiskModel.get_model_performance') as mock_performance:
            mock_performance.return_value = {
                'accuracy': 0.87,
                'precision': 0.82,
                'recall': 0.85,
                'f1_score': 0.83,
                'auc': 0.91
            }
            
            response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('models', response.data)
        self.assertIn('dropout_risk', response.data['models'])
        self.assertIn('appreciation_generator', response.data['models'])
        self.assertIn('global_metrics', response.data)
    
    def test_get_model_status_unauthorized(self):
        """Test sans authentification"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TrainAIModelAPITest(AIAnalyticsAPITestCase):
    """Tests pour l'endpoint d'entraînement des modèles IA"""
    
    def setUp(self):
        super().setUp()
        self.url = reverse('ai_analytics:train-ai-model')
    
    def test_train_model_success(self):
        """Test d'entraînement de modèle réussi"""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'model_type': 'dropout_risk',
            'force_retrain': False
        }
        
        with patch('apps.ai_analytics.tasks.train_ml_model.delay') as mock_task:
            mock_task.return_value.id = 'task-123'
            
            response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('task_id', response.data)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['task_id'], 'task-123')
    
    def test_train_model_unauthorized(self):
        """Test sans permission admin"""
        self.client.force_authenticate(user=self.teacher_user)
        
        data = {
            'model_type': 'dropout_risk'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_train_model_invalid_type(self):
        """Test avec type de modèle invalide"""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'model_type': 'invalid_model'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AIDashboardMetricsAPITest(AIAnalyticsAPITestCase):
    """Tests pour l'endpoint des métriques du dashboard IA"""
    
    def setUp(self):
        super().setUp()
        self.url = reverse('ai_analytics:ai-dashboard-metrics')
        
        # Créer des profils de risque pour les tests
        self.risk_profile1 = RiskProfile.objects.create(
            tenant=self.tenant,
            student=self.student,
            academic_year="2023-2024",
            risk_score=0.8,
            risk_level="élevé"
        )
    
    def test_get_dashboard_metrics_success(self):
        """Test de récupération des métriques du dashboard"""
        self.client.force_authenticate(user=self.teacher_user)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('model_performance', response.data)
        self.assertIn('risk_distribution', response.data)
        self.assertIn('total_profiles', response.data)
        self.assertIn('high_risk_count', response.data)
        self.assertIn('average_risk_score', response.data)
    
    def test_dashboard_metrics_calculation(self):
        """Test du calcul des métriques"""
        self.client.force_authenticate(user=self.teacher_user)
        
        # Créer plusieurs profils avec différents niveaux de risque
        RiskProfile.objects.create(
            tenant=self.tenant,
            student=self.student,
            academic_year="2023-2024",
            risk_score=0.2,
            risk_level="faible"
        )
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data['total_profiles'], 0)
        
        # Vérifier la distribution des risques
        risk_dist = response.data['risk_distribution']
        total_count = sum(risk_dist.values())
        self.assertEqual(total_count, response.data['total_profiles'])


class RiskProfileViewSetTest(AIAnalyticsAPITestCase):
    """Tests pour le ViewSet des profils de risque"""
    
    def setUp(self):
        super().setUp()
        self.list_url = reverse('ai_analytics:risk-profiles-list')
        
        # Créer des profils de risque
        self.risk_profile = RiskProfile.objects.create(
            tenant=self.tenant,
            student=self.student,
            academic_year="2023-2024",
            risk_score=0.7,
            risk_level="modéré"
        )
    
    def test_list_risk_profiles(self):
        """Test de listage des profils de risque"""
        self.client.force_authenticate(user=self.teacher_user)
        
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_filter_risk_profiles_by_level(self):
        """Test de filtrage par niveau de risque"""
        self.client.force_authenticate(user=self.teacher_user)
        
        url = f"{self.list_url}?risk_level=modéré"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for profile in response.data['results']:
            self.assertEqual(profile['risk_level'], 'modéré')
    
    def test_analyze_risk_profile(self):
        """Test d'analyse d'un profil de risque"""
        self.client.force_authenticate(user=self.teacher_user)
        
        url = reverse('ai_analytics:risk-profiles-analyze', kwargs={'pk': self.risk_profile.pk})
        
        with patch('apps.ai_analytics.tasks.analyze_student_risk.delay') as mock_task:
            mock_task.return_value.id = 'analyze-task-123'
            
            response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('task_id', response.data)