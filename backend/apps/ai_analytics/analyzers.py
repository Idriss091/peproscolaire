"""
Analyseurs pour collecter les données des élèves
"""
from django.db.models import Avg, Count, Q, F, Sum
from django.utils import timezone
from datetime import datetime, timedelta
import numpy as np


class StudentDataAnalyzer:
    """
    Analyse les données d'un élève pour la détection de risques
    """
    
    def __init__(self, student, period_days=30):
        self.student = student
        self.period_days = period_days
        self.end_date = timezone.now().date()
        self.start_date = self.end_date - timedelta(days=period_days)
        
    def collect_all_data(self):
        """
        Collecter toutes les données nécessaires pour l'analyse
        """
        data = {
            'student_id': str(self.student.id),
            'analysis_date': self.end_date.isoformat(),
            'features': {}
        }
        
        # Collecter les différentes catégories de données
        data['features'].update(self._collect_academic_data())
        data['features'].update(self._collect_attendance_data())
        data['features'].update(self._collect_behavioral_data())
        data['features'].update(self._collect_engagement_data())
        data['features'].update(self._collect_social_data())
        data['features'].update(self._collect_demographic_data())
        
        return data
    
    def _collect_academic_data(self):
        """Collecter les données académiques"""
        from apps.grades.models import Grade, GeneralAverage, SubjectAverage
        
        # Notes récentes
        recent_grades = Grade.objects.filter(
            student=self.student,
            evaluation__date__range=[self.start_date, self.end_date],
            score__isnull=False
        )
        
        if recent_grades.exists():
            scores = list(recent_grades.values_list('normalized_score', flat=True))
            avg_grade = np.mean(scores)
            grade_variance = np.var(scores)
        else:
            avg_grade = 10.0
            grade_variance = 0.0
        
        # Tendance des notes
        grade_trend = self._calculate_grade_trend()
        
        # Moyennes par matière
        subject_averages = SubjectAverage.objects.filter(
            student=self.student,
            grading_period__end_date__gte=self.start_date
        )
        
        failed_subjects = subject_averages.filter(average__lt=10).count()
        
        # Dernière moyenne générale
        last_general_avg = GeneralAverage.objects.filter(
            student=self.student
        ).order_by('-grading_period__end_date').first()
        
        current_average = float(last_general_avg.average) if last_general_avg and last_general_avg.average else 10.0
        
        return {
            'average_grade': float(avg_grade),
            'grade_variance': float(grade_variance),
            'grade_trend': float(grade_trend),
            'failed_subjects': failed_subjects,
            'current_average': current_average
        }
    
    def _calculate_grade_trend(self):
        """Calculer la tendance des notes"""
        from apps.grades.models import Grade
        
        # Diviser la période en deux
        mid_date = self.start_date + timedelta(days=self.period_days // 2)
        
        first_half_grades = Grade.objects.filter(
            student=self.student,
            evaluation__date__range=[self.start_date, mid_date],
            score__isnull=False
        ).aggregate(avg=Avg('normalized_score'))['avg']
        
        second_half_grades = Grade.objects.filter(
            student=self.student,
            evaluation__date__range=[mid_date, self.end_date],
            score__isnull=False
        ).aggregate(avg=Avg('normalized_score'))['avg']
        
        if first_half_grades and second_half_grades:
            return second_half_grades - first_half_grades
        return 0.0
    
    def _collect_attendance_data(self):
        """Collecter les données d'assiduité"""
        from apps.attendance.models import Attendance, AttendanceStatus
        
        attendances = Attendance.objects.filter(
            student=self.student,
            date__range=[self.start_date, self.end_date]
        )
        
        total = attendances.count()
        if total == 0:
            return {
                'absence_rate': 0.0,
                'unjustified_absence_rate': 0.0,
                'tardiness_rate': 0.0,
                'consecutive_absences': 0
            }
        
        absences = attendances.filter(status=AttendanceStatus.ABSENT)
        unjustified = absences.filter(is_justified=False)
        tardiness = attendances.filter(status=AttendanceStatus.LATE)
        
        # Calculer les absences consécutives
        consecutive = self._calculate_consecutive_absences(attendances)
        
        return {
            'absence_rate': float(absences.count() / total * 100),
            'unjustified_absence_rate': float(unjustified.count() / total * 100),
            'tardiness_rate': float(tardiness.count() / total * 100),
            'consecutive_absences': consecutive
        }
    
    def _calculate_consecutive_absences(self, attendances):
        """Calculer le nombre maximum d'absences consécutives"""
        ordered = attendances.order_by('date').values('date', 'status')
        
        max_consecutive = 0
        current_consecutive = 0
        
        for attendance in ordered:
            if attendance['status'] == 'absent':
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return max_consecutive
    
    def _collect_behavioral_data(self):
        """Collecter les données comportementales"""
        from apps.attendance.models import Sanction, StudentBehavior
        
        sanctions = Sanction.objects.filter(
            student=self.student,
            date__range=[self.start_date, self.end_date]
        )
        
        behaviors = StudentBehavior.objects.filter(
            student=self.student,
            date__range=[self.start_date, self.end_date]
        )
        
        positive_behaviors = behaviors.filter(behavior_type='positive').count()
        negative_behaviors = behaviors.filter(behavior_type='negative').count()
        
        # Score de participation basé sur les comportements
        if positive_behaviors + negative_behaviors > 0:
            participation_score = (positive_behaviors / (positive_behaviors + negative_behaviors)) * 10
        else:
            participation_score = 5.0
        
        return {
            'behavior_incidents': negative_behaviors,
            'sanctions_count': sanctions.count(),
            'positive_behaviors': positive_behaviors,
            'participation_score': float(participation_score)
        }
    
    def _collect_engagement_data(self):
        """Collecter les données d'engagement"""
        from apps.homework.models import Homework, StudentWork
        
        # Devoirs de la période
        homework_list = Homework.objects.filter(
            class_group__students__student=self.student,
            due_date__range=[self.start_date, self.end_date]
        )
        
        total_homework = homework_list.count()
        if total_homework == 0:
            return {
                'homework_completion_rate': 100.0,
                'late_homework_rate': 0.0,
                'average_study_time': 60.0
            }
        
        # Travaux rendus
        submitted_work = StudentWork.objects.filter(
            student=self.student,
            homework__in=homework_list,
            status__in=['submitted', 'late', 'returned']
        )
        
        late_work = submitted_work.filter(status='late')
        
        completion_rate = (submitted_work.count() / total_homework) * 100
        late_rate = (late_work.count() / total_homework) * 100
        
        # Temps d'étude moyen (basé sur time_spent_minutes)
        avg_study_time = submitted_work.filter(
            time_spent_minutes__isnull=False
        ).aggregate(avg=Avg('time_spent_minutes'))['avg'] or 60.0
        
        return {
            'homework_completion_rate': float(completion_rate),
            'late_homework_rate': float(late_rate),
            'average_study_time': float(avg_study_time)
        }
    
    def _collect_social_data(self):
        """Collecter les données sociales"""
        from apps.messaging.models import Message, MessageRecipient
        
        # Messages envoyés (indicateur d'interaction)
        sent_messages = Message.objects.filter(
            sender=self.student,
            sent_at__date__range=[self.start_date, self.end_date]
        ).count()
        
        # Messages reçus
        received_messages = MessageRecipient.objects.filter(
            recipient=self.student,
            message__sent_at__date__range=[self.start_date, self.end_date]
        ).count()
        
        # Score d'intégration basique
        interaction_score = min(10, (sent_messages + received_messages) / 5)
        
        # Activités extrascolaires (à implémenter)
        extracurricular = 0  # Placeholder
        
        return {
            'social_integration_score': float(interaction_score),
            'extracurricular_activities': extracurricular
        }
    
    def _collect_demographic_data(self):
        """Collecter les données démographiques"""
        from apps.student_records.models import StudentRecord
        
        try:
            record = StudentRecord.objects.get(student=self.student)
            
            # Calculer l'âge
            if hasattr(self.student, 'profile') and self.student.profile.date_of_birth:
                age = (timezone.now().date() - self.student.profile.date_of_birth).days // 365
            else:
                age = 15  # Âge par défaut
            
            # Risque lié à la situation familiale
            family_risk_mapping = {
                'parents_together': 0,
                'separated': 1,
                'divorced': 1,
                'single_parent': 2,
                'guardian': 2,
                'foster': 3,
                'other': 1,
            }
            family_risk = family_risk_mapping.get(record.family_situation, 0)
            
            # Support à la maison (basé sur le nombre de responsables avec autorité parentale)
            has_support = record.guardians.filter(has_custody=True).count() >= 1
            
            # Temps dans l'école
            months_in_school = (self.end_date - record.entry_date).days // 30
            
            return {
                'age': age,
                'family_situation_risk': family_risk,
                'has_support_at_home': int(has_support),
                'months_in_school': months_in_school
            }
            
        except StudentRecord.DoesNotExist:
            # Valeurs par défaut si pas de dossier
            return {
                'age': 15,
                'family_situation_risk': 0,
                'has_support_at_home': 1,
                'months_in_school': 12
            }


class ClassRiskAnalyzer:
    """
    Analyse les risques au niveau d'une classe
    """
    
    def __init__(self, class_group):
        self.class_group = class_group
        
    def analyze_class_risks(self):
        """Analyser les risques de toute la classe"""
        students = self.class_group.students.filter(is_active=True)
        
        risk_distribution = {
            'very_low': 0,
            'low': 0,
            'moderate': 0,
            'high': 0,
            'critical': 0
        }
        
        at_risk_students = []
        
        for enrollment in students:
            student = enrollment.student
            
            # Récupérer ou calculer le profil de risque
            from apps.ai_analytics.models import RiskProfile
            
            try:
                profile = RiskProfile.objects.get(
                    student=student,
                    academic_year=self.class_group.academic_year
                )
                
                risk_distribution[profile.risk_level] += 1
                
                if profile.risk_level in ['high', 'critical']:
                    at_risk_students.append({
                        'student': student,
                        'risk_level': profile.risk_level,
                        'risk_score': profile.risk_score,
                        'main_factors': profile.risk_factors
                    })
                    
            except RiskProfile.DoesNotExist:
                risk_distribution['low'] += 1
        
        # Calculer les métriques de classe
        total_students = students.count()
        at_risk_percentage = (
            (risk_distribution['high'] + risk_distribution['critical']) / total_students * 100
            if total_students > 0 else 0
        )
        
        return {
            'class_id': str(self.class_group.id),
            'class_name': str(self.class_group),
            'total_students': total_students,
            'risk_distribution': risk_distribution,
            'at_risk_percentage': at_risk_percentage,
            'at_risk_students': sorted(
                at_risk_students,
                key=lambda x: x['risk_score'],
                reverse=True
            )[:10],  # Top 10 élèves à risque
            'recommendations': self._generate_class_recommendations(
                risk_distribution,
                at_risk_percentage
            )
        }
    
    def _generate_class_recommendations(self, distribution, at_risk_percentage):
        """Générer des recommandations pour la classe"""
        recommendations = []
        
        if at_risk_percentage > 30:
            recommendations.append({
                'priority': 'high',
                'action': 'Intervention urgente au niveau de la classe',
                'details': 'Plus de 30% des élèves sont à risque. Une action collective est nécessaire.'
            })
        
        if distribution['critical'] > 2:
            recommendations.append({
                'priority': 'high',
                'action': 'Cellule de crise pour les cas critiques',
                'details': f"{distribution['critical']} élèves en situation critique nécessitent une attention immédiate."
            })
        
        if distribution['high'] > 5:
            recommendations.append({
                'priority': 'medium',
                'action': 'Renforcer le soutien scolaire',
                'details': 'Mettre en place des groupes de soutien pour les élèves en difficulté.'
            })
        
        return recommendations


class StudentRiskAnalyzer:
    """
    Analyseur de risque pour un élève spécifique
    """
    
    def __init__(self, student, academic_year):
        self.student = student
        self.academic_year = academic_year
        self.data_analyzer = StudentDataAnalyzer(student)
        
    def analyze_comprehensive_risk(self):
        """Analyse complète du risque d'un élève"""
        # Collecter toutes les données
        data = self.data_analyzer.collect_all_data()
        features = data['features']
        
        # Calculer les scores de risque par catégorie
        academic_risk = self._calculate_academic_risk(features)
        attendance_risk = self._calculate_attendance_risk(features)
        behavioral_risk = self._calculate_behavioral_risk(features)
        social_risk = self._calculate_social_risk(features)
        
        # Score de risque global pondéré
        risk_score = (
            academic_risk * 0.35 +
            attendance_risk * 0.25 +
            behavioral_risk * 0.20 +
            social_risk * 0.20
        )
        
        # Probabilité de décrochage basée sur le modèle
        dropout_probability = self._calculate_dropout_probability(features, risk_score)
        
        # Génération des recommandations
        recommendations = self._generate_recommendations({
            'academic': academic_risk,
            'attendance': attendance_risk,
            'behavioral': behavioral_risk,
            'social': social_risk
        })
        
        # Actions prioritaires
        priority_actions = self._identify_priority_actions(features, risk_score)
        
        return {
            'risk_score': min(100, max(0, risk_score)),
            'academic_risk': academic_risk,
            'attendance_risk': attendance_risk,
            'behavioral_risk': behavioral_risk,
            'social_risk': social_risk,
            'risk_factors': self._identify_risk_factors(features),
            'indicators': features,
            'dropout_probability': dropout_probability,
            'predicted_final_average': self._predict_final_average(features),
            'recommendations': recommendations,
            'priority_actions': priority_actions
        }
    
    def _calculate_academic_risk(self, features):
        """Calculer le risque académique"""
        risk = 0
        
        # Moyenne actuelle
        current_avg = features.get('current_average', 10)
        if current_avg < 8:
            risk += 30
        elif current_avg < 10:
            risk += 20
        elif current_avg < 12:
            risk += 10
        
        # Tendance des notes
        grade_trend = features.get('grade_trend', 0)
        if grade_trend < -2:
            risk += 25
        elif grade_trend < -1:
            risk += 15
        elif grade_trend < 0:
            risk += 5
        
        # Matières échouées
        failed_subjects = features.get('failed_subjects', 0)
        risk += failed_subjects * 5
        
        # Variance des notes (instabilité)
        variance = features.get('grade_variance', 0)
        if variance > 4:
            risk += 10
        
        return min(100, risk)
    
    def _calculate_attendance_risk(self, features):
        """Calculer le risque d'assiduité"""
        risk = 0
        
        # Taux d'absence
        absence_rate = features.get('absence_rate', 0)
        if absence_rate > 20:
            risk += 40
        elif absence_rate > 15:
            risk += 30
        elif absence_rate > 10:
            risk += 20
        elif absence_rate > 5:
            risk += 10
        
        # Absences injustifiées
        unjustified_rate = features.get('unjustified_absence_rate', 0)
        risk += unjustified_rate * 2
        
        # Retards
        tardiness_rate = features.get('tardiness_rate', 0)
        risk += tardiness_rate * 1.5
        
        # Absences consécutives
        consecutive = features.get('consecutive_absences', 0)
        if consecutive > 5:
            risk += 20
        elif consecutive > 3:
            risk += 10
        
        return min(100, risk)
    
    def _calculate_behavioral_risk(self, features):
        """Calculer le risque comportemental"""
        risk = 0
        
        # Incidents comportementaux
        incidents = features.get('behavior_incidents', 0)
        risk += incidents * 8
        
        # Sanctions
        sanctions = features.get('sanctions_count', 0)
        risk += sanctions * 12
        
        # Score de participation
        participation = features.get('participation_score', 5)
        if participation < 3:
            risk += 25
        elif participation < 5:
            risk += 15
        elif participation < 7:
            risk += 5
        
        return min(100, risk)
    
    def _calculate_social_risk(self, features):
        """Calculer le risque social"""
        risk = 0
        
        # Intégration sociale
        social_score = features.get('social_integration_score', 5)
        if social_score < 2:
            risk += 30
        elif social_score < 4:
            risk += 20
        elif social_score < 6:
            risk += 10
        
        # Situation familiale
        family_risk = features.get('family_situation_risk', 0)
        risk += family_risk * 8
        
        # Support à la maison
        has_support = features.get('has_support_at_home', 1)
        if not has_support:
            risk += 15
        
        # Activités extrascolaires (facteur protecteur)
        activities = features.get('extracurricular_activities', 0)
        if activities == 0:
            risk += 10
        
        return min(100, risk)
    
    def _calculate_dropout_probability(self, features, risk_score):
        """Calculer la probabilité de décrochage"""
        # Modèle simplifié basé sur les facteurs de risque
        base_probability = risk_score / 100 * 0.3
        
        # Facteurs aggravants
        if features.get('consecutive_absences', 0) > 7:
            base_probability += 0.2
        
        if features.get('current_average', 10) < 8:
            base_probability += 0.15
        
        if features.get('sanctions_count', 0) > 2:
            base_probability += 0.1
        
        # Facteurs protecteurs
        if features.get('social_integration_score', 5) > 7:
            base_probability -= 0.05
        
        if features.get('has_support_at_home', 1):
            base_probability -= 0.1
        
        return max(0, min(1, base_probability))
    
    def _predict_final_average(self, features):
        """Prédire la moyenne finale"""
        current_avg = features.get('current_average', 10)
        trend = features.get('grade_trend', 0)
        
        # Prédiction simple basée sur la tendance
        predicted = current_avg + (trend * 2)
        
        # Ajustements basés sur les autres facteurs
        if features.get('homework_completion_rate', 100) < 70:
            predicted -= 1
        
        if features.get('absence_rate', 0) > 15:
            predicted -= 1.5
        
        if features.get('behavior_incidents', 0) > 3:
            predicted -= 1
        
        return max(0, min(20, predicted))
    
    def _identify_risk_factors(self, features):
        """Identifier les facteurs de risque principaux"""
        factors = {}
        
        # Facteurs académiques
        if features.get('current_average', 10) < 10:
            factors['low_academic_performance'] = {
                'severity': 'high' if features['current_average'] < 8 else 'medium',
                'value': features['current_average'],
                'description': 'Moyenne générale faible'
            }
        
        if features.get('grade_trend', 0) < -1:
            factors['declining_grades'] = {
                'severity': 'high' if features['grade_trend'] < -2 else 'medium',
                'value': features['grade_trend'],
                'description': 'Tendance négative des notes'
            }
        
        # Facteurs d'assiduité
        if features.get('absence_rate', 0) > 10:
            factors['high_absenteeism'] = {
                'severity': 'critical' if features['absence_rate'] > 20 else 'high',
                'value': features['absence_rate'],
                'description': 'Taux d\'absence élevé'
            }
        
        if features.get('consecutive_absences', 0) > 3:
            factors['consecutive_absences'] = {
                'severity': 'high' if features['consecutive_absences'] > 5 else 'medium',
                'value': features['consecutive_absences'],
                'description': 'Absences consécutives préoccupantes'
            }
        
        # Facteurs comportementaux
        if features.get('behavior_incidents', 0) > 2:
            factors['behavioral_issues'] = {
                'severity': 'high',
                'value': features['behavior_incidents'],
                'description': 'Incidents comportementaux répétés'
            }
        
        # Facteurs sociaux
        if features.get('social_integration_score', 5) < 4:
            factors['social_isolation'] = {
                'severity': 'medium',
                'value': features['social_integration_score'],
                'description': 'Faible intégration sociale'
            }
        
        return factors
    
    def _generate_recommendations(self, risk_scores):
        """Générer des recommandations personnalisées"""
        recommendations = []
        
        # Recommandations académiques
        if risk_scores['academic'] > 30:
            recommendations.append("Mettre en place un soutien scolaire personnalisé")
            recommendations.append("Réviser les méthodes d'apprentissage")
        
        # Recommandations d'assiduité
        if risk_scores['attendance'] > 25:
            recommendations.append("Renforcer le suivi d'assiduité")
            recommendations.append("Organiser un entretien avec la famille")
        
        # Recommandations comportementales
        if risk_scores['behavioral'] > 25:
            recommendations.append("Mettre en place un suivi comportemental")
            recommendations.append("Envisager un accompagnement psychopédagogique")
        
        # Recommandations sociales
        if risk_scores['social'] > 20:
            recommendations.append("Favoriser l'intégration dans des activités de groupe")
            recommendations.append("Renforcer le lien avec les familles")
        
        return recommendations
    
    def _identify_priority_actions(self, features, risk_score):
        """Identifier les actions prioritaires"""
        actions = []
        
        if risk_score > 70:
            actions.append("Convocation urgente de l'équipe éducative")
        
        if features.get('consecutive_absences', 0) > 5:
            actions.append("Contact immédiat avec la famille")
        
        if features.get('current_average', 10) < 8:
            actions.append("Mise en place d'un tutorat")
        
        if features.get('behavior_incidents', 0) > 3:
            actions.append("Entretien avec le conseiller d'éducation")
        
        return actions


class PatternDetector:
    """
    Détecteur de patterns de risque
    """
    
    def __init__(self):
        self.patterns = {
            'monday_absenteeism': self._detect_monday_pattern,
            'grade_drop_pattern': self._detect_grade_drop_pattern,
            'escalating_behavior': self._detect_escalating_behavior,
            'social_withdrawal': self._detect_social_withdrawal
        }
    
    def detect_patterns(self, student, lookback_days=90):
        """Détecter tous les patterns pour un élève"""
        detected_patterns = []
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=lookback_days)
        
        for pattern_name, detector in self.patterns.items():
            try:
                result = detector(student, start_date, end_date)
                if result:
                    detected_patterns.append({
                        'name': pattern_name,
                        'severity': result.get('severity', 'medium'),
                        'description': result.get('description', ''),
                        'evidence': result.get('evidence', []),
                        'detected_at': timezone.now().isoformat()
                    })
            except Exception as e:
                logger.error(f"Erreur détection pattern {pattern_name}: {e}")
        
        return detected_patterns
    
    def _detect_monday_pattern(self, student, start_date, end_date):
        """Détecter un pattern d'absence le lundi"""
        from apps.attendance.models import Attendance
        
        # Récupérer tous les lundis de la période
        attendances = Attendance.objects.filter(
            student=student,
            date__range=[start_date, end_date],
            date__week_day=2  # Lundi
        )
        
        total_mondays = attendances.count()
        absent_mondays = attendances.filter(status='absent').count()
        
        if total_mondays > 4 and absent_mondays / total_mondays > 0.4:
            return {
                'severity': 'high',
                'description': f'Absence récurrente le lundi ({absent_mondays}/{total_mondays})',
                'evidence': [f'{absent_mondays} absences sur {total_mondays} lundis']
            }
        
        return None
    
    def _detect_grade_drop_pattern(self, student, start_date, end_date):
        """Détecter une chute brutale des notes"""
        from apps.grades.models import Grade
        
        # Diviser la période en deux
        mid_date = start_date + timedelta(days=(end_date - start_date).days // 2)
        
        first_half = Grade.objects.filter(
            student=student,
            evaluation__date__range=[start_date, mid_date],
            score__isnull=False
        ).aggregate(avg=Avg('normalized_score'))['avg']
        
        second_half = Grade.objects.filter(
            student=student,
            evaluation__date__range=[mid_date, end_date],
            score__isnull=False
        ).aggregate(avg=Avg('normalized_score'))['avg']
        
        if first_half and second_half and (first_half - second_half) > 3:
            return {
                'severity': 'high',
                'description': f'Chute significative des notes (-{first_half - second_half:.1f} points)',
                'evidence': [f'Moyenne 1ère période: {first_half:.1f}', f'Moyenne 2ème période: {second_half:.1f}']
            }
        
        return None
    
    def _detect_escalating_behavior(self, student, start_date, end_date):
        """Détecter une escalade comportementale"""
        from apps.attendance.models import Sanction
        
        # Diviser en 3 périodes
        period_length = (end_date - start_date).days // 3
        
        periods = []
        for i in range(3):
            period_start = start_date + timedelta(days=i * period_length)
            period_end = start_date + timedelta(days=(i + 1) * period_length)
            
            sanctions = Sanction.objects.filter(
                student=student,
                date__range=[period_start, period_end]
            ).count()
            
            periods.append(sanctions)
        
        # Vérifier si escalade
        if len(periods) >= 2 and periods[-1] > periods[0] and periods[-1] > 2:
            return {
                'severity': 'high',
                'description': 'Escalade comportementale détectée',
                'evidence': [f'Sanctions par période: {periods}']
            }
        
        return None
    
    def _detect_social_withdrawal(self, student, start_date, end_date):
        """Détecter un retrait social"""
        from apps.messaging.models import Message
        
        # Messages par mois
        monthly_messages = []
        current_date = start_date
        
        while current_date < end_date:
            month_end = min(current_date + timedelta(days=30), end_date)
            
            message_count = Message.objects.filter(
                sender=student,
                sent_at__date__range=[current_date, month_end]
            ).count()
            
            monthly_messages.append(message_count)
            current_date = month_end + timedelta(days=1)
        
        # Vérifier la tendance
        if len(monthly_messages) >= 2:
            if monthly_messages[-1] < monthly_messages[0] / 2 and monthly_messages[0] > 5:
                return {
                    'severity': 'medium',
                    'description': 'Diminution significative des interactions sociales',
                    'evidence': [f'Messages par mois: {monthly_messages}']
                }
        
        return None


class InterventionAnalyzer:
    """
    Analyseur d'efficacité des interventions
    """
    
    def __init__(self, intervention_plan):
        self.plan = intervention_plan
        self.student = intervention_plan.risk_profile.student
        
    def evaluate_effectiveness(self):
        """Évaluer l'efficacité du plan d'intervention"""
        if not self.plan.start_date:
            return {'error': 'Plan pas encore démarré'}
        
        # Données avant intervention
        before_data = self._get_data_before_intervention()
        
        # Données après intervention
        after_data = self._get_data_after_intervention()
        
        # Calculer les améliorations
        improvements = self._calculate_improvements(before_data, after_data)
        
        # Score d'efficacité automatique
        auto_score = self._calculate_auto_score(improvements)
        
        return {
            'before_data': before_data,
            'after_data': after_data,
            'improvements': improvements,
            'auto_score': auto_score,
            'summary': self._generate_summary(improvements, auto_score)
        }
    
    def _get_data_before_intervention(self):
        """Récupérer les données d'avant l'intervention"""
        end_date = self.plan.start_date
        start_date = end_date - timedelta(days=30)
        
        analyzer = StudentDataAnalyzer(self.student, period_days=30)
        analyzer.start_date = start_date
        analyzer.end_date = end_date
        
        return analyzer.collect_all_data()['features']
    
    def _get_data_after_intervention(self):
        """Récupérer les données d'après l'intervention"""
        start_date = self.plan.start_date + timedelta(days=7)  # Délai d'adaptation
        end_date = timezone.now().date()
        
        if (end_date - start_date).days < 14:
            return None  # Pas assez de données
        
        analyzer = StudentDataAnalyzer(self.student, period_days=(end_date - start_date).days)
        analyzer.start_date = start_date
        analyzer.end_date = end_date
        
        return analyzer.collect_all_data()['features']
    
    def _calculate_improvements(self, before, after):
        """Calculer les améliorations"""
        if not after:
            return {}
        
        improvements = {}
        
        # Métriques à comparer (plus c'est haut, mieux c'est)
        positive_metrics = ['current_average', 'homework_completion_rate', 'participation_score']
        
        # Métriques à comparer (plus c'est bas, mieux c'est)
        negative_metrics = ['absence_rate', 'behavior_incidents', 'late_homework_rate']
        
        for metric in positive_metrics:
            if metric in before and metric in after:
                improvements[metric] = after[metric] - before[metric]
        
        for metric in negative_metrics:
            if metric in before and metric in after:
                improvements[metric] = before[metric] - after[metric]  # Inversion pour amélioration positive
        
        return improvements
    
    def _calculate_auto_score(self, improvements):
        """Calculer un score d'efficacité automatique"""
        if not improvements:
            return None
        
        total_score = 0
        count = 0
        
        # Pondération des améliorations
        weights = {
            'current_average': 3,
            'absence_rate': 2,
            'homework_completion_rate': 2,
            'behavior_incidents': 1.5,
            'participation_score': 1
        }
        
        for metric, improvement in improvements.items():
            if metric in weights:
                # Normaliser l'amélioration sur une échelle de 0-10
                normalized = min(10, max(0, improvement * 2 + 5))
                total_score += normalized * weights[metric]
                count += weights[metric]
        
        return total_score / count if count > 0 else 5
    
    def _generate_summary(self, improvements, auto_score):
        """Générer un résumé de l'évaluation"""
        if not improvements:
            return "Pas assez de données pour évaluer l'efficacité"
        
        positive_changes = [k for k, v in improvements.items() if v > 0]
        negative_changes = [k for k, v in improvements.items() if v < 0]
        
        summary = f"Score d'efficacité: {auto_score:.1f}/10. "
        
        if positive_changes:
            summary += f"Améliorations: {', '.join(positive_changes)}. "
        
        if negative_changes:
            summary += f"Détériorations: {', '.join(negative_changes)}. "
        
        if auto_score >= 7:
            summary += "Intervention très efficace."
        elif auto_score >= 5:
            summary += "Intervention modérément efficace."
        else:
            summary += "Intervention peu efficace, révision nécessaire."
        
        return summary