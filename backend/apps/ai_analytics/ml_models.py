"""
Modèles de Machine Learning pour la détection des risques
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import joblib
import logging
from datetime import datetime, timedelta
from django.conf import settings
import os

logger = logging.getLogger(__name__)


class DropoutRiskModel:
    """
    Modèle de prédiction du risque de décrochage scolaire
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.model_path = os.path.join(
            settings.BASE_DIR, 'ai_models', 'dropout_risk_model.pkl'
        )
        self.scaler_path = os.path.join(
            settings.BASE_DIR, 'ai_models', 'dropout_risk_scaler.pkl'
        )
        
    def prepare_features(self, student_data):
        """
        Préparer les caractéristiques pour le modèle
        """
        features = {}
        
        # Caractéristiques académiques
        features['avg_grade'] = student_data.get('average_grade', 10.0)
        features['grade_trend'] = student_data.get('grade_trend', 0.0)
        features['failed_subjects'] = student_data.get('failed_subjects', 0)
        features['grade_variance'] = student_data.get('grade_variance', 0.0)
        
        # Caractéristiques d'assiduité
        features['absence_rate'] = student_data.get('absence_rate', 0.0)
        features['unjustified_absence_rate'] = student_data.get('unjustified_absence_rate', 0.0)
        features['tardiness_rate'] = student_data.get('tardiness_rate', 0.0)
        features['consecutive_absences'] = student_data.get('consecutive_absences', 0)
        
        # Caractéristiques comportementales
        features['behavior_incidents'] = student_data.get('behavior_incidents', 0)
        features['sanctions_count'] = student_data.get('sanctions_count', 0)
        features['positive_behaviors'] = student_data.get('positive_behaviors', 0)
        
        # Caractéristiques d'engagement
        features['homework_completion_rate'] = student_data.get('homework_completion_rate', 100.0)
        features['late_homework_rate'] = student_data.get('late_homework_rate', 0.0)
        features['participation_score'] = student_data.get('participation_score', 5.0)
        
        # Caractéristiques sociales
        features['social_integration_score'] = student_data.get('social_integration_score', 5.0)
        features['extracurricular_activities'] = student_data.get('extracurricular_activities', 0)
        
        # Caractéristiques familiales
        features['family_situation_risk'] = student_data.get('family_situation_risk', 0)
        features['has_support_at_home'] = student_data.get('has_support_at_home', 1)
        
        # Caractéristiques temporelles
        features['months_in_school'] = student_data.get('months_in_school', 12)
        features['age'] = student_data.get('age', 15)
        
        return features
    
    def train(self, training_data):
        """
        Entraîner le modèle
        """
        # Préparer les données
        X = []
        y = []
        
        for record in training_data:
            features = self.prepare_features(record['features'])
            X.append(list(features.values()))
            y.append(record['dropped_out'])
        
        self.feature_names = list(features.keys())
        
        X = np.array(X)
        y = np.array(y)
        
        # Diviser les données
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Normaliser les données
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Entraîner le modèle
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Évaluer le modèle
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_test, y_pred, average='binary'
        )
        
        logger.info(f"Modèle entraîné - Accuracy: {accuracy:.3f}, "
                   f"Precision: {precision:.3f}, Recall: {recall:.3f}, "
                   f"F1: {f1:.3f}")
        
        # Sauvegarder le modèle
        self.save_model()
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'feature_importance': dict(zip(
                self.feature_names,
                self.model.feature_importances_
            ))
        }
    
    def predict(self, student_data):
        """
        Prédire le risque pour un élève
        """
        if not self.model:
            self.load_model()
        
        features = self.prepare_features(student_data)
        X = np.array([list(features.values())])
        
        # Normaliser
        X_scaled = self.scaler.transform(X)
        
        # Prédiction
        dropout_probability = self.model.predict_proba(X_scaled)[0][1]
        risk_level = self._calculate_risk_level(dropout_probability)
        
        # Facteurs de risque principaux
        feature_importance = self.model.feature_importances_
        feature_values = X[0]
        
        risk_factors = []
        for i, (name, importance) in enumerate(zip(self.feature_names, feature_importance)):
            if importance > 0.05:  # Seuil d'importance
                risk_factors.append({
                    'factor': name,
                    'value': feature_values[i],
                    'importance': float(importance),
                    'impact': self._calculate_impact(name, feature_values[i])
                })
        
        risk_factors.sort(key=lambda x: x['importance'], reverse=True)
        
        return {
            'dropout_probability': float(dropout_probability),
            'risk_level': risk_level,
            'risk_score': float(dropout_probability * 100),
            'main_risk_factors': risk_factors[:5],
            'recommendations': self._generate_recommendations(risk_factors)
        }
    
    def _calculate_risk_level(self, probability):
        """Calculer le niveau de risque"""
        if probability >= 0.8:
            return 'critical'
        elif probability >= 0.6:
            return 'high'
        elif probability >= 0.4:
            return 'moderate'
        elif probability >= 0.2:
            return 'low'
        else:
            return 'very_low'
    
    def _calculate_impact(self, factor_name, value):
        """Calculer l'impact d'un facteur"""
        # Définir les seuils pour chaque facteur
        thresholds = {
            'absence_rate': {'high': 20, 'critical': 40},
            'avg_grade': {'low': 10, 'critical': 8},
            'homework_completion_rate': {'low': 70, 'critical': 50},
            'behavior_incidents': {'high': 3, 'critical': 5},
            'grade_trend': {'negative': -2, 'critical': -5},
        }
        
        if factor_name not in thresholds:
            return 'unknown'
        
        factor_thresholds = thresholds[factor_name]
        
        # Logique inversée pour certains facteurs (plus c'est bas, plus c'est risqué)
        if factor_name in ['avg_grade', 'homework_completion_rate']:
            if value <= factor_thresholds.get('critical', 0):
                return 'critical'
            elif value <= factor_thresholds.get('low', 10):
                return 'high'
            else:
                return 'moderate'
        else:
            # Logique normale (plus c'est haut, plus c'est risqué)
            if value >= factor_thresholds.get('critical', float('inf')):
                return 'critical'
            elif value >= factor_thresholds.get('high', float('inf')):
                return 'high'
            else:
                return 'moderate'
    
    def _generate_recommendations(self, risk_factors):
        """Générer des recommandations basées sur les facteurs de risque"""
        recommendations = []
        
        for factor in risk_factors[:3]:  # Top 3 facteurs
            factor_name = factor['factor']
            impact = factor['impact']
            
            if factor_name == 'absence_rate' and impact in ['high', 'critical']:
                recommendations.append({
                    'priority': 'high',
                    'action': 'Mettre en place un suivi d\'assiduité renforcé',
                    'details': 'Contacter la famille et identifier les causes des absences'
                })
            
            elif factor_name == 'avg_grade' and impact in ['high', 'critical']:
                recommendations.append({
                    'priority': 'high',
                    'action': 'Organiser du soutien scolaire',
                    'details': 'Identifier les matières en difficulté et proposer un accompagnement personnalisé'
                })
            
            elif factor_name == 'homework_completion_rate' and impact in ['high', 'critical']:
                recommendations.append({
                    'priority': 'medium',
                    'action': 'Aide aux devoirs',
                    'details': 'Proposer un temps d\'étude supervisé ou un tutorat par les pairs'
                })
            
            elif factor_name == 'behavior_incidents' and impact in ['high', 'critical']:
                recommendations.append({
                    'priority': 'high',
                    'action': 'Suivi comportemental',
                    'details': 'Rencontre avec le CPE et mise en place d\'un contrat de comportement'
                })
            
            elif factor_name == 'social_integration_score' and impact in ['high', 'critical']:
                recommendations.append({
                    'priority': 'medium',
                    'action': 'Favoriser l\'intégration sociale',
                    'details': 'Proposer des activités de groupe et un parrainage par des pairs'
                })
        
        return recommendations
    
    def save_model(self):
        """Sauvegarder le modèle et le scaler"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        
        # Sauvegarder aussi les noms des features
        feature_path = os.path.join(
            os.path.dirname(self.model_path), 'features.pkl'
        )
        joblib.dump(self.feature_names, feature_path)
    
    def load_model(self):
        """Charger le modèle et le scaler"""
        try:
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            
            feature_path = os.path.join(
                os.path.dirname(self.model_path), 'features.pkl'
            )
            self.feature_names = joblib.load(feature_path)
            
            logger.info("Modèle de risque de décrochage chargé avec succès")
        except FileNotFoundError:
            logger.warning("Modèle non trouvé, utilisation du modèle par défaut")
            self._initialize_default_model()
    
    def _initialize_default_model(self):
        """Initialiser un modèle par défaut"""
        # Modèle simple pour démarrer
        self.model = RandomForestClassifier(
            n_estimators=50,
            max_depth=5,
            random_state=42
        )
        
        # Entraînement minimal avec des données synthétiques
        n_samples = 1000
        n_features = 18
        
        # Générer des données synthétiques
        np.random.seed(42)
        X = np.random.randn(n_samples, n_features)
        
        # Créer des labels avec une logique simple
        y = (X[:, 0] < -1) | (X[:, 1] > 1.5)  # Règles arbitraires
        
        # Entraîner
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        self.model.fit(X_scaled, y)
        
        # Définir les noms des features
        self.feature_names = [
            'avg_grade', 'grade_trend', 'failed_subjects', 'grade_variance',
            'absence_rate', 'unjustified_absence_rate', 'tardiness_rate',
            'consecutive_absences', 'behavior_incidents', 'sanctions_count',
            'positive_behaviors', 'homework_completion_rate', 'late_homework_rate',
            'participation_score', 'social_integration_score',
            'extracurricular_activities', 'family_situation_risk',
            'has_support_at_home'
        ]


class AcademicPerformancePredictor:
    """
    Modèle de prédiction des performances académiques
    """
    
    def __init__(self):
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.scaler = StandardScaler()
        
    def predict_final_grade(self, student_data, current_progress=0.5):
        """
        Prédire la note finale probable
        
        Args:
            student_data: Données de l'élève
            current_progress: Progression dans l'année (0-1)
        """
        features = self._prepare_features(student_data, current_progress)
        
        # Pour l'instant, utiliser une formule simple
        # En production, utiliser le modèle entraîné
        current_avg = student_data.get('current_average', 10.0)
        trend = student_data.get('grade_trend', 0.0)
        
        # Projection simple
        remaining_progress = 1 - current_progress
        predicted_change = trend * remaining_progress * 2  # Facteur d'amplification
        
        predicted_average = current_avg + predicted_change
        
        # Limiter entre 0 et 20
        predicted_average = max(0, min(20, predicted_average))
        
        # Calculer l'intervalle de confiance
        confidence_interval = self._calculate_confidence_interval(
            predicted_average, current_progress
        )
        
        return {
            'predicted_average': float(predicted_average),
            'confidence_interval': confidence_interval,
            'probability_pass': float(predicted_average >= 10) * 0.8 + 0.1,  # Simplifié
            'key_factors': self._identify_key_factors(student_data)
        }
    
    def _prepare_features(self, student_data, progress):
        """Préparer les features pour le modèle"""
        # Similaire à DropoutRiskModel mais adapté pour la régression
        features = {
            'current_average': student_data.get('current_average', 10.0),
            'grade_trend': student_data.get('grade_trend', 0.0),
            'homework_completion': student_data.get('homework_completion_rate', 100.0),
            'attendance_rate': 100 - student_data.get('absence_rate', 0.0),
            'progress': progress,
            'study_time': student_data.get('average_study_time', 60),
            'participation': student_data.get('participation_score', 5.0)
        }
        return features
    
    def _calculate_confidence_interval(self, prediction, progress):
        """Calculer l'intervalle de confiance"""
        # Plus on avance dans l'année, plus la prédiction est précise
        uncertainty = 2.0 * (1 - progress)
        
        return {
            'lower': float(max(0, prediction - uncertainty)),
            'upper': float(min(20, prediction + uncertainty)),
            'confidence': float(0.95 - 0.2 * (1 - progress))  # 75% à 95%
        }
    
    def _identify_key_factors(self, student_data):
        """Identifier les facteurs clés affectant la performance"""
        factors = []
        
        # Analyser les tendances
        if student_data.get('grade_trend', 0) < -1:
            factors.append({
                'factor': 'Baisse des notes',
                'impact': 'negative',
                'suggestion': 'Identifier les difficultés récentes'
            })
        
        if student_data.get('homework_completion_rate', 100) < 80:
            factors.append({
                'factor': 'Devoirs incomplets',
                'impact': 'negative',
                'suggestion': 'Améliorer l\'organisation du travail personnel'
            })
        
        if student_data.get('absence_rate', 0) > 10:
            factors.append({
                'factor': 'Absences fréquentes',
                'impact': 'negative',
                'suggestion': 'Rattraper les cours manqués'
            })
        
        return factors


class ModelTrainer:
    """
    Entraîneur de modèles ML avec données réelles
    """
    
    def __init__(self):
        self.dropout_model = DropoutRiskModel()
        self.performance_model = AcademicPerformancePredictor()
        
    def generate_training_data(self, academic_year=None, min_samples=100):
        """
        Générer des données d'entraînement à partir des données réelles
        """
        from apps.ai_analytics.analyzers import StudentDataAnalyzer
        from apps.schools.models import AcademicYear, Enrollment
        from apps.ai_analytics.models import RiskProfile
        from django.utils import timezone
        
        if not academic_year:
            # Prendre l'année précédente pour avoir des données complètes
            academic_year = AcademicYear.objects.filter(
                end_date__lt=timezone.now().date()
            ).order_by('-end_date').first()
            
        if not academic_year:
            logger.warning("Aucune année scolaire complète trouvée")
            return []
        
        training_data = []
        
        # Récupérer tous les élèves de l'année
        enrollments = Enrollment.objects.filter(
            academic_year=academic_year,
            is_active=True
        ).select_related('student')
        
        for enrollment in enrollments:
            try:
                student = enrollment.student
                
                # Analyser les données de l'élève
                analyzer = StudentDataAnalyzer(student, period_days=180)  # 6 mois de données
                data = analyzer.collect_all_data()
                
                # Déterminer si l'élève a décroché (approximation)
                dropped_out = self._determine_dropout_status(student, academic_year)
                
                training_record = {
                    'student_id': str(student.id),
                    'features': data['features'],
                    'dropped_out': dropped_out,
                    'academic_year': str(academic_year.id)
                }
                
                training_data.append(training_record)
                
            except Exception as e:
                logger.error(f"Erreur lors de la génération de données pour {student}: {e}")
                continue
        
        logger.info(f"Données d'entraînement générées: {len(training_data)} échantillons")
        
        # Si pas assez de données réelles, compléter avec des données synthétiques
        if len(training_data) < min_samples:
            synthetic_data = self._generate_synthetic_data(min_samples - len(training_data))
            training_data.extend(synthetic_data)
            logger.info(f"Ajouté {len(synthetic_data)} échantillons synthétiques")
        
        return training_data
    
    def _determine_dropout_status(self, student, academic_year):
        """
        Déterminer si un élève a décroché (heuristique)
        """
        from apps.attendance.models import Attendance
        from apps.grades.models import GeneralAverage
        from django.db.models import Avg
        from datetime import timedelta
        
        # Critères de décrochage (heuristiques)
        # 1. Taux d'absence très élevé en fin d'année
        end_period_start = academic_year.end_date - timedelta(days=60)
        end_absences = Attendance.objects.filter(
            student=student,
            date__range=[end_period_start, academic_year.end_date],
            status='absent'
        ).count()
        
        total_end_days = Attendance.objects.filter(
            student=student,
            date__range=[end_period_start, academic_year.end_date]
        ).count()
        
        end_absence_rate = end_absences / total_end_days * 100 if total_end_days > 0 else 0
        
        # 2. Moyenne finale très faible
        final_average = GeneralAverage.objects.filter(
            student=student,
            grading_period__academic_year=academic_year
        ).order_by('-grading_period__end_date').first()
        
        final_avg_score = float(final_average.average) if final_average and final_average.average else 10.0
        
        # 3. Pas d'inscription l'année suivante
        from apps.schools.models import Enrollment
        next_year = AcademicYear.objects.filter(
            start_date__year=academic_year.start_date.year + 1
        ).first()
        
        continued_next_year = Enrollment.objects.filter(
            student=student,
            academic_year=next_year
        ).exists() if next_year else True  # Assumer continuation si pas d'année suivante
        
        # Critères de décrochage
        dropped_out = (
            end_absence_rate > 50 or  # Plus de 50% d'absence en fin d'année
            final_avg_score < 6 or   # Moyenne < 6
            not continued_next_year   # Pas d'inscription année suivante
        )
        
        return dropped_out
    
    def _generate_synthetic_data(self, count):
        """
        Générer des données synthétiques réalistes
        """
        import random
        
        synthetic_data = []
        
        for i in range(count):
            # Générer des caractéristiques réalistes
            features = {}
            
            # Corrélations réalistes entre variables
            if random.random() < 0.3:  # 30% d'élèves en difficulté
                # Profil à risque
                features['current_average'] = random.uniform(5, 9)
                features['absence_rate'] = random.uniform(15, 40)
                features['homework_completion_rate'] = random.uniform(30, 70)
                features['behavior_incidents'] = random.randint(2, 8)
                dropped_out = random.random() < 0.7  # 70% de chance de décrochage
            else:
                # Profil normal
                features['current_average'] = random.uniform(10, 18)
                features['absence_rate'] = random.uniform(0, 10)
                features['homework_completion_rate'] = random.uniform(80, 100)
                features['behavior_incidents'] = random.randint(0, 2)
                dropped_out = random.random() < 0.05  # 5% de chance de décrochage
            
            # Autres caractéristiques
            features['grade_trend'] = random.uniform(-3, 3)
            features['failed_subjects'] = random.randint(0, 5)
            features['grade_variance'] = random.uniform(0, 6)
            features['unjustified_absence_rate'] = features['absence_rate'] * random.uniform(0.3, 0.8)
            features['tardiness_rate'] = random.uniform(0, 15)
            features['consecutive_absences'] = random.randint(0, 10)
            features['sanctions_count'] = random.randint(0, 5)
            features['positive_behaviors'] = random.randint(0, 10)
            features['late_homework_rate'] = (100 - features['homework_completion_rate']) * random.uniform(0.2, 0.6)
            features['participation_score'] = random.uniform(1, 10)
            features['social_integration_score'] = random.uniform(1, 10)
            features['extracurricular_activities'] = random.randint(0, 3)
            features['family_situation_risk'] = random.randint(0, 3)
            features['has_support_at_home'] = random.choice([0, 1])
            features['months_in_school'] = random.randint(6, 24)
            features['age'] = random.randint(11, 18)
            features['average_study_time'] = random.uniform(30, 180)
            
            synthetic_data.append({
                'student_id': f'synthetic_{i}',
                'features': features,
                'dropped_out': dropped_out,
                'academic_year': 'synthetic'
            })
        
        return synthetic_data
    
    def train_dropout_model(self, training_data=None, save_model=True):
        """
        Entraîner le modèle de détection de décrochage
        """
        if not training_data:
            training_data = self.generate_training_data()
        
        if len(training_data) < 50:
            logger.warning("Pas assez de données d'entraînement, utilisation du modèle par défaut")
            self.dropout_model._initialize_default_model()
            return {'success': False, 'reason': 'insufficient_data'}
        
        logger.info(f"Entraînement du modèle avec {len(training_data)} échantillons")
        
        # Entraîner le modèle
        results = self.dropout_model.train(training_data)
        
        if save_model:
            self.dropout_model.save_model()
        
        # Enregistrer les métriques d'entraînement
        self._save_training_metrics(results, 'dropout_risk', len(training_data))
        
        return {
            'success': True,
            'metrics': results,
            'training_samples': len(training_data)
        }
    
    def _save_training_metrics(self, metrics, model_type, sample_count):
        """
        Sauvegarder les métriques d'entraînement
        """
        try:
            from django.utils import timezone
            # Pour l'instant, juste logger les métriques
            # Plus tard, on pourra créer un modèle ModelTrainingLog
            logger.info(f"Métriques {model_type}: Accuracy={metrics.get('accuracy', 0):.3f}, "
                       f"F1={metrics.get('f1_score', 0):.3f}, Échantillons={sample_count}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des métriques: {e}")
    
    def evaluate_model_performance(self):
        """
        Évaluer les performances du modèle sur des données récentes
        """
        try:
            # Générer des données de test récentes
            test_data = self.generate_training_data(min_samples=20)
            
            if len(test_data) < 10:
                return {'error': 'Pas assez de données de test'}
            
            # Séparer features et labels
            X_test = []
            y_test = []
            
            for record in test_data:
                features = self.dropout_model.prepare_features(record['features'])
                X_test.append(list(features.values()))
                y_test.append(record['dropped_out'])
            
            X_test = np.array(X_test)
            y_test = np.array(y_test)
            
            # Charger le modèle et évaluer
            if not self.dropout_model.model:
                self.dropout_model.load_model()
            
            # Normaliser les données de test
            X_test_scaled = self.dropout_model.scaler.transform(X_test)
            
            # Prédictions
            y_pred = self.dropout_model.model.predict(X_test_scaled)
            y_prob = self.dropout_model.model.predict_proba(X_test_scaled)[:, 1]
            
            # Calculer les métriques
            from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score
            
            accuracy = accuracy_score(y_test, y_pred)
            precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='binary')
            
            try:
                auc = roc_auc_score(y_test, y_prob)
            except:
                auc = None
            
            return {
                'accuracy': float(accuracy),
                'precision': float(precision),
                'recall': float(recall),
                'f1_score': float(f1),
                'auc': float(auc) if auc else None,
                'test_samples': len(test_data),
                'model_version': getattr(self.dropout_model, 'model_version', '1.0')
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'évaluation du modèle: {e}")
            return {'error': str(e)}
    
    def retrain_if_needed(self, performance_threshold=0.8):
        """
        Ré-entraîner le modèle si les performances sont insuffisantes
        """
        try:
            # Évaluer les performances actuelles
            performance = self.evaluate_model_performance()
            
            if 'error' in performance:
                logger.info("Impossible d'évaluer les performances, ré-entraînement préventif")
                return self.train_dropout_model()
            
            current_f1 = performance.get('f1_score', 0)
            
            if current_f1 < performance_threshold:
                logger.info(f"Performances insuffisantes (F1: {current_f1:.3f}), ré-entraînement nécessaire")
                return self.train_dropout_model()
            else:
                logger.info(f"Performances satisfaisantes (F1: {current_f1:.3f}), pas de ré-entraînement nécessaire")
                return {'success': False, 'reason': 'performance_adequate', 'metrics': performance}
                
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de ré-entraînement: {e}")
            return {'success': False, 'error': str(e)}