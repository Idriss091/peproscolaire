"""
Tests pour les modèles d'analyse IA
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from django.utils import timezone

from .models import RiskProfile, RiskIndicator, Alert, InterventionPlan
from .ml_models import DropoutRiskModel, AcademicPerformancePredictor, ModelTrainer
from apps.schools.models import School, Class
from apps.student_records.models import Student
from apps.tenants.models import Tenant

User = get_user_model()


class DropoutRiskModelTest(TestCase):
    """Tests pour le modèle de détection de décrochage"""
    
    def setUp(self):
        self.risk_model = DropoutRiskModel()
    
    def test_feature_extraction_basic(self):
        """Test d'extraction des features de base"""
        student_data = {
            'attendance_rate': 0.85,
            'average_grade': 12.5,
            'absences_count': 15,
            'late_arrivals': 8,
            'sanctions_count': 2,
            'homework_completion_rate': 0.7
        }
        
        features = self.risk_model.extract_features(student_data)
        
        self.assertIsInstance(features, list)
        self.assertEqual(len(features), 18)  # Nombre attendu de features
        self.assertEqual(features[0], 0.85)  # attendance_rate
        self.assertEqual(features[1], 12.5)  # average_grade
    
    def test_feature_extraction_with_missing_data(self):
        """Test d'extraction avec données manquantes"""
        student_data = {
            'attendance_rate': 0.9,
            'average_grade': None,  # Donnée manquante
            'absences_count': 5
        }
        
        features = self.risk_model.extract_features(student_data)
        
        # Vérifier que les valeurs par défaut sont utilisées
        self.assertEqual(features[1], 10.0)  # Valeur par défaut pour average_grade
    
    def test_predict_dropout_risk_high(self):
        """Test de prédiction pour un risque élevé"""
        # Données simulant un élève à haut risque
        high_risk_data = {
            'attendance_rate': 0.6,  # Faible assiduité
            'average_grade': 6.0,    # Notes faibles
            'absences_count': 30,    # Beaucoup d'absences
            'late_arrivals': 20,
            'sanctions_count': 8,
            'homework_completion_rate': 0.3
        }
        
        result = self.risk_model.predict_dropout_risk(high_risk_data)
        
        self.assertIn('dropout_probability', result)
        self.assertIn('risk_level', result)
        self.assertIn('main_risk_factors', result)
        self.assertGreater(result['dropout_probability'], 0.7)  # Risque élevé
        self.assertEqual(result['risk_level'], 'élevé')
    
    def test_predict_dropout_risk_low(self):
        """Test de prédiction pour un risque faible"""
        # Données simulant un élève à faible risque
        low_risk_data = {
            'attendance_rate': 0.95,
            'average_grade': 16.0,
            'absences_count': 2,
            'late_arrivals': 1,
            'sanctions_count': 0,
            'homework_completion_rate': 0.9
        }
        
        result = self.risk_model.predict_dropout_risk(low_risk_data)
        
        self.assertLess(result['dropout_probability'], 0.3)  # Risque faible
        self.assertEqual(result['risk_level'], 'faible')
    
    def test_get_risk_factors_importance(self):
        """Test de récupération de l'importance des facteurs"""
        factors = self.risk_model.get_risk_factors_importance()
        
        self.assertIsInstance(factors, list)
        self.assertGreater(len(factors), 0)
        
        # Vérifier la structure des facteurs
        factor = factors[0]
        self.assertIn('factor', factor)
        self.assertIn('importance', factor)
        self.assertIn('impact', factor)


class ModelTrainerTest(TestCase):
    """Tests pour l'entraînement des modèles"""
    
    def setUp(self):
        self.trainer = ModelTrainer()
    
    @patch('apps.ai_analytics.ml_models.ModelTrainer._load_training_data')
    def test_train_dropout_model_success(self, mock_load_data):
        """Test d'entraînement réussi du modèle de décrochage"""
        # Mock des données d'entraînement
        mock_load_data.return_value = (
            [[0.8, 12.0, 10, 3, 1, 0.8] for _ in range(100)],  # Features
            [0, 1, 0, 1, 0] * 20  # Labels
        )
        
        result = self.trainer.train_dropout_model(save_model=False)
        
        self.assertTrue(result['success'])
        self.assertIn('metrics', result)
        self.assertIn('accuracy', result['metrics'])
        self.assertGreater(result['metrics']['accuracy'], 0.5)
    
    def test_evaluate_model(self):
        """Test d'évaluation du modèle"""
        # Données de test simples
        test_features = [[0.9, 15.0, 2, 1, 0, 0.9], [0.6, 8.0, 25, 10, 5, 0.4]]
        test_labels = [0, 1]
        
        metrics = self.trainer.evaluate_model(test_features, test_labels)
        
        self.assertIn('accuracy', metrics)
        self.assertIn('precision', metrics)
        self.assertIn('recall', metrics)
        self.assertIn('f1_score', metrics)
        self.assertIn('confusion_matrix', metrics)
    
    def test_generate_synthetic_data(self):
        """Test de génération de données synthétiques"""
        features, labels = self.trainer.generate_synthetic_data(100)
        
        self.assertEqual(len(features), 100)
        self.assertEqual(len(labels), 100)
        self.assertEqual(len(features[0]), 18)  # Nombre de features
        
        # Vérifier que les labels sont valides (0 ou 1)
        self.assertTrue(all(label in [0, 1] for label in labels))


class RiskProfileModelTest(TestCase):
    """Tests pour le modèle RiskProfile"""
    
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
            name="École Primaire Test",
            address="123 Rue Test",
            phone="0123456789",
            email="test@example.com"
        )
        
        # Créer une classe
        self.class_obj = Class.objects.create(
            tenant=self.tenant,
            school=self.school,
            name="6ème A",
            level="6ème",
            academic_year="2023-2024"
        )
        
        # Créer un utilisateur étudiant
        self.student_user = User.objects.create_user(
            email="student@test.com",
            password="testpass123",
            first_name="Jean",
            last_name="Dupont",
            user_type="student"
        )
        
        # Créer un étudiant
        self.student = Student.objects.create(
            tenant=self.tenant,
            user=self.student_user,
            student_number="STU001",
            admission_date=timezone.now().date()
        )
        
        # Créer des indicateurs de risque
        self.indicator1 = RiskIndicator.objects.create(
            tenant=self.tenant,
            name="Absentéisme",
            description="Taux d'absence élevé",
            threshold_value=0.8,
            weight=0.3,
            category="attendance"
        )
    
    def test_create_risk_profile(self):
        """Test de création d'un profil de risque"""
        risk_profile = RiskProfile.objects.create(
            tenant=self.tenant,
            student=self.student,
            academic_year="2023-2024",
            risk_score=0.75,
            risk_level="modéré",
            last_analysis=timezone.now()
        )
        
        self.assertEqual(risk_profile.student, self.student)
        self.assertEqual(risk_profile.risk_level, "modéré")
        self.assertEqual(risk_profile.risk_score, 0.75)
        self.assertFalse(risk_profile.is_monitored)
    
    def test_risk_profile_update_level_on_score_change(self):
        """Test de mise à jour automatique du niveau de risque"""
        risk_profile = RiskProfile.objects.create(
            tenant=self.tenant,
            student=self.student,
            academic_year="2023-2024",
            risk_score=0.3,
            risk_level="faible"
        )
        
        # Mettre à jour le score pour déclencher un risque élevé
        risk_profile.risk_score = 0.9
        risk_profile.save()
        
        # Le niveau devrait être automatiquement mis à jour
        risk_profile.refresh_from_db()
        self.assertEqual(risk_profile.risk_level, "élevé")
    
    def test_risk_profile_str_method(self):
        """Test de la méthode __str__"""
        risk_profile = RiskProfile.objects.create(
            tenant=self.tenant,
            student=self.student,
            academic_year="2023-2024",
            risk_score=0.6,
            risk_level="modéré"
        )
        
        expected_str = f"Jean Dupont - Risque modéré (60%)"
        self.assertEqual(str(risk_profile), expected_str)


class AlertModelTest(TestCase):
    """Tests pour le modèle Alert"""
    
    def setUp(self):
        # Setup similaire à RiskProfileModelTest
        self.tenant = Tenant.objects.create(
            name="Test School",
            subdomain="test",
            description="École de test"
        )
        
        self.school = School.objects.create(
            tenant=self.tenant,
            name="École Test",
            address="123 Rue Test",
            phone="0123456789",
            email="test@example.com"
        )
        
        self.student_user = User.objects.create_user(
            email="student@test.com",
            password="testpass123",
            first_name="Marie",
            last_name="Martin",
            user_type="student"
        )
        
        self.student = Student.objects.create(
            tenant=self.tenant,
            user=self.student_user,
            student_number="STU002",
            admission_date=timezone.now().date()
        )
        
        self.risk_profile = RiskProfile.objects.create(
            tenant=self.tenant,
            student=self.student,
            academic_year="2023-2024",
            risk_score=0.85,
            risk_level="élevé"
        )
    
    def test_create_alert(self):
        """Test de création d'une alerte"""
        alert = Alert.objects.create(
            tenant=self.tenant,
            risk_profile=self.risk_profile,
            message="Risque de décrochage détecté",
            priority="high",
            alert_type="risk_detection"
        )
        
        self.assertEqual(alert.risk_profile, self.risk_profile)
        self.assertEqual(alert.priority, "high")
        self.assertFalse(alert.is_acknowledged)
    
    def test_alert_acknowledge(self):
        """Test d'accusé de réception d'une alerte"""
        alert = Alert.objects.create(
            tenant=self.tenant,
            risk_profile=self.risk_profile,
            message="Test alert",
            priority="medium"
        )
        
        # Créer un utilisateur pour l'accusé de réception
        teacher_user = User.objects.create_user(
            email="teacher@test.com",
            password="testpass123",
            first_name="Prof",
            last_name="Enseignant",
            user_type="teacher"
        )
        
        alert.acknowledge(teacher_user, "Intervention planifiée")
        
        self.assertTrue(alert.is_acknowledged)
        self.assertEqual(alert.acknowledged_by, teacher_user)
        self.assertIsNotNone(alert.acknowledged_at)
        self.assertEqual(alert.actions_taken, "Intervention planifiée")
    
    def test_alert_auto_priority(self):
        """Test de priorité automatique basée sur le risque"""
        # Alerte pour risque élevé -> priorité high
        high_risk_profile = RiskProfile.objects.create(
            tenant=self.tenant,
            student=self.student,
            academic_year="2023-2024",
            risk_score=0.9,
            risk_level="élevé"
        )
        
        alert = Alert.objects.create(
            tenant=self.tenant,
            risk_profile=high_risk_profile,
            message="Risque critique"
        )
        
        # La priorité devrait être automatiquement définie à 'high'
        self.assertEqual(alert.priority, "high")


class InterventionPlanModelTest(TestCase):
    """Tests pour le modèle InterventionPlan"""
    
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test School",
            subdomain="test"
        )
        
        self.student_user = User.objects.create_user(
            email="student@test.com",
            password="testpass123",
            first_name="Paul",
            last_name="Durand",
            user_type="student"
        )
        
        self.student = Student.objects.create(
            tenant=self.tenant,
            user=self.student_user,
            student_number="STU003",
            admission_date=timezone.now().date()
        )
        
        self.risk_profile = RiskProfile.objects.create(
            tenant=self.tenant,
            student=self.student,
            academic_year="2023-2024",
            risk_score=0.8,
            risk_level="élevé"
        )
        
        self.coordinator = User.objects.create_user(
            email="coordinator@test.com",
            password="testpass123",
            first_name="Coord",
            last_name="Inateur",
            user_type="teacher"
        )
    
    def test_create_intervention_plan(self):
        """Test de création d'un plan d'intervention"""
        plan = InterventionPlan.objects.create(
            tenant=self.tenant,
            risk_profile=self.risk_profile,
            coordinator=self.coordinator,
            title="Plan de remédiation",
            description="Accompagnement personnalisé",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
            objectives=["Améliorer l'assiduité", "Remonter les notes"],
            planned_actions=["Entretien hebdomadaire", "Soutien scolaire"]
        )
        
        self.assertEqual(plan.title, "Plan de remédiation")
        self.assertEqual(plan.status, "en_cours")
        self.assertEqual(len(plan.objectives), 2)
        self.assertEqual(len(plan.planned_actions), 2)
    
    def test_intervention_plan_effectiveness(self):
        """Test d'évaluation de l'efficacité"""
        plan = InterventionPlan.objects.create(
            tenant=self.tenant,
            risk_profile=self.risk_profile,
            coordinator=self.coordinator,
            title="Test Plan",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30)
        )
        
        # Évaluer l'efficacité
        plan.evaluate_effectiveness("Amélioration notable", 8)
        
        self.assertEqual(plan.effectiveness_score, 8)
        self.assertEqual(plan.outcomes, "Amélioration notable")
        self.assertEqual(plan.status, "terminé")
    
    def test_intervention_plan_duration_property(self):
        """Test du calcul de la durée"""
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=20)
        
        plan = InterventionPlan.objects.create(
            tenant=self.tenant,
            risk_profile=self.risk_profile,
            coordinator=self.coordinator,
            title="Test Plan",
            start_date=start_date,
            end_date=end_date
        )
        
        self.assertEqual(plan.duration_days, 20)