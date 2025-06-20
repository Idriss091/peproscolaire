"""
Module IA pour générer des appréciations
"""
from .base import BaseAIModule
import random
import json
import re
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class AppreciationGenerator(BaseAIModule):
    """Générateur d'appréciations pour les bulletins"""
    
    def generate_appreciation(self, student, subject, average, period, options=None):
        """
        Générer une appréciation pour un élève
        
        Args:
            student: Instance de l'élève
            subject: Instance de la matière  
            average: Moyenne de l'élève
            period: Période d'évaluation
            options: Options de génération (type, ton, longueur, etc.)
        """
        try:
            if not options:
                options = {}
            
            # Analyser le profil complet de l'élève
            profile = self._analyze_comprehensive_profile(student, subject, average, period)
            
            # Adapter selon les options
            appreciation_type = options.get('type', 'bulletin')
            tone = options.get('tone', 'bienveillant')
            length = options.get('length', 'standard')
            focus_areas = options.get('focus_areas', [])
            
            # Construire le prompt adapté
            prompt = self._build_advanced_prompt(profile, appreciation_type, tone, length, focus_areas)
            
            # Messages pour l'API
            messages = self._build_messages(prompt, tone)
            
            # Appeler l'API avec gestion d'erreur
            appreciation = self._call_api_with_retry(messages, options)
            
            # Post-traitement et validation
            final_appreciation = self._advanced_post_process(appreciation, profile, options)
            
            # Enregistrer pour amélioration future
            self._log_generation(student, subject, final_appreciation, options)
            
            return {
                'content': final_appreciation,
                'confidence': self._calculate_confidence(final_appreciation, profile),
                'metadata': {
                    'type': appreciation_type,
                    'tone': tone,
                    'length': length,
                    'generated_at': timezone.now().isoformat(),
                    'model_version': getattr(self, 'model_version', '1.0')
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur génération appréciation pour {student}: {e}")
            return self._get_fallback_appreciation(student, subject, average, period)
    
    def generate_multiple_appreciations(self, students_data, options=None):
        """Générer des appréciations pour plusieurs élèves"""
        results = []
        
        for data in students_data:
            try:
                result = self.generate_appreciation(
                    data['student'],
                    data['subject'], 
                    data['average'],
                    data['period'],
                    options
                )
                results.append({
                    'student_id': str(data['student'].id),
                    'appreciation': result,
                    'status': 'success'
                })
            except Exception as e:
                logger.error(f"Erreur génération pour {data['student']}: {e}")
                results.append({
                    'student_id': str(data['student'].id),
                    'appreciation': None,
                    'status': 'error',
                    'error': str(e)
                })
        
        return results
    
    def _analyze_comprehensive_profile(self, student, subject, average, period):
        """Analyser le profil complet de l'élève avec plus de données"""
        from apps.grades.models import Grade, SubjectAverage, Evaluation
        from apps.attendance.models import Attendance, StudentBehavior
        from apps.homework.models import StudentWork
        from django.db.models import Avg, Count
        
        profile = {
            'name': student.first_name,
            'subject': subject.name if subject else 'Matière générale',
            'average': float(average) if average else None,
            'level': self._get_level(average),
            'progression': 'stable',
            'behavior': 'correct',
            'participation': 'moyenne',
            'homework': 'régulier',
            'attendance': 'satisfaisante',
            'strengths': [],
            'areas_for_improvement': [],
            'recent_trend': 'stable'
        }
        
        # Analyser la progression sur plusieurs périodes
        if subject:
            previous_averages = SubjectAverage.objects.filter(
                student=student,
                subject=subject,
                grading_period__academic_year=period.academic_year
            ).order_by('grading_period__number')
            
            if previous_averages.count() >= 2:
                trend = self._calculate_trend(previous_averages)
                profile['progression'] = trend['label']
                profile['recent_trend'] = trend['direction']
        
        # Analyser les évaluations récentes
        recent_grades = Grade.objects.filter(
            student=student,
            evaluation__subject=subject,
            evaluation__date__range=[period.start_date, period.end_date]
        ).order_by('-evaluation__date')
        
        if recent_grades.exists():
            profile['recent_performance'] = self._analyze_recent_performance(recent_grades)
        
        # Analyser le comportement et la participation
        behaviors = StudentBehavior.objects.filter(
            student=student,
            date__range=[period.start_date, period.end_date]
        )
        
        behavior_analysis = self._analyze_behavior(behaviors)
        profile.update(behavior_analysis)
        
        # Analyser les devoirs
        homework_analysis = self._analyze_homework_completion(student, period)
        profile.update(homework_analysis)
        
        # Analyser l'assiduité
        attendance_analysis = self._analyze_attendance(student, period)
        profile.update(attendance_analysis)
        
        # Identifier les points forts et axes d'amélioration
        profile['strengths'], profile['areas_for_improvement'] = self._identify_strengths_and_improvements(profile)
        
        return profile
    
    def _calculate_trend(self, averages):
        """Calculer la tendance sur plusieurs périodes"""
        if averages.count() < 2:
            return {'label': 'stable', 'direction': 'stable'}
        
        values = [float(avg.average) for avg in averages if avg.average]
        if len(values) < 2:
            return {'label': 'stable', 'direction': 'stable'}
        
        # Calculer la pente de régression linéaire simple
        n = len(values)
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * values[i] for i in range(n))
        x2_sum = sum(i**2 for i in range(n))
        
        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum**2)
        
        if slope > 0.5:
            return {'label': 'en nette progression', 'direction': 'rising'}
        elif slope > 0.2:
            return {'label': 'en progression', 'direction': 'rising'}
        elif slope < -0.5:
            return {'label': 'en baisse importante', 'direction': 'falling'}
        elif slope < -0.2:
            return {'label': 'en léger recul', 'direction': 'falling'}
        else:
            return {'label': 'stable', 'direction': 'stable'}
    
    def _analyze_recent_performance(self, grades):
        """Analyser les performances récentes"""
        scores = [float(grade.normalized_score) for grade in grades if grade.normalized_score]
        
        if not scores:
            return {'consistency': 'indéterminée', 'recent_average': None}
        
        recent_avg = sum(scores) / len(scores)
        variance = sum((score - recent_avg)**2 for score in scores) / len(scores)
        
        consistency = 'régulière' if variance < 4 else 'irrégulière'
        
        return {
            'consistency': consistency,
            'recent_average': recent_avg,
            'variance': variance,
            'best_grade': max(scores),
            'worst_grade': min(scores)
        }
    
    def _analyze_behavior(self, behaviors):
        """Analyser le comportement de l'élève"""
        positive_count = behaviors.filter(behavior_type='positive').count()
        negative_count = behaviors.filter(behavior_type='negative').count()
        
        if positive_count > negative_count * 2:
            behavior = 'exemplaire'
            participation = 'très active'
        elif positive_count > negative_count:
            behavior = 'bon'
            participation = 'active'
        elif negative_count > positive_count:
            behavior = 'à améliorer'
            participation = 'passive'
        else:
            behavior = 'correct'
            participation = 'moyenne'
        
        return {
            'behavior': behavior,
            'participation': participation,
            'positive_behaviors': positive_count,
            'negative_behaviors': negative_count
        }
    
    def _analyze_homework_completion(self, student, period):
        """Analyser la qualité du travail personnel"""
        from apps.homework.models import StudentWork, Homework
        
        homework_assigned = Homework.objects.filter(
            class_group__students__student=student,
            due_date__range=[period.start_date, period.end_date]
        ).count()
        
        if homework_assigned == 0:
            return {'homework': 'non applicable', 'homework_rate': None}
        
        homework_done = StudentWork.objects.filter(
            student=student,
            homework__due_date__range=[period.start_date, period.end_date],
            status__in=['submitted', 'returned']
        ).count()
        
        completion_rate = homework_done / homework_assigned * 100
        
        if completion_rate >= 90:
            homework_quality = 'excellent'
        elif completion_rate >= 75:
            homework_quality = 'bon'
        elif completion_rate >= 50:
            homework_quality = 'irrégulier'
        else:
            homework_quality = 'insuffisant'
        
        return {
            'homework': homework_quality,
            'homework_rate': completion_rate
        }
    
    def _analyze_attendance(self, student, period):
        """Analyser l'assiduité"""
        from apps.attendance.models import Attendance
        
        attendances = Attendance.objects.filter(
            student=student,
            date__range=[period.start_date, period.end_date]
        )
        
        total = attendances.count()
        if total == 0:
            return {'attendance': 'indéterminée', 'absence_rate': None}
        
        absences = attendances.filter(status='absent').count()
        absence_rate = absences / total * 100
        
        if absence_rate <= 2:
            attendance = 'excellente'
        elif absence_rate <= 5:
            attendance = 'bonne'
        elif absence_rate <= 10:
            attendance = 'correcte'
        else:
            attendance = 'préoccupante'
        
        return {
            'attendance': attendance,
            'absence_rate': absence_rate
        }
    
    def _identify_strengths_and_improvements(self, profile):
        """Identifier les points forts et axes d'amélioration"""
        strengths = []
        improvements = []
        
        # Points forts
        if profile.get('level') in ['excellent', 'très bon']:
            strengths.append('Excellents résultats académiques')
        
        if profile.get('behavior') in ['exemplaire', 'bon']:
            strengths.append('Comportement positif')
        
        if profile.get('homework') in ['excellent', 'bon']:
            strengths.append('Travail personnel sérieux')
        
        if profile.get('attendance') in ['excellente', 'bonne']:
            strengths.append('Assiduité remarquable')
        
        if profile.get('progression') in ['en progression', 'en nette progression']:
            strengths.append('Progression encourageante')
        
        # Axes d'amélioration
        if profile.get('level') in ['fragile', 'insuffisant']:
            improvements.append('Renforcement des acquis fondamentaux')
        
        if profile.get('behavior') == 'à améliorer':
            improvements.append('Amélioration du comportement en classe')
        
        if profile.get('homework') in ['irrégulier', 'insuffisant']:
            improvements.append('Régularité dans le travail personnel')
        
        if profile.get('attendance') == 'préoccupante':
            improvements.append('Amélioration de l\'assiduité')
        
        if profile.get('participation') == 'passive':
            improvements.append('Participation plus active en cours')
        
        return strengths, improvements
    
    def _build_advanced_prompt(self, profile, appreciation_type, tone, length, focus_areas):
        """Construire un prompt avancé pour l'IA"""
        # Prompts système selon le type
        system_prompts = {
            'bulletin': "Tu es un professeur expérimenté qui rédige des appréciations de bulletin scolaire. Tes appréciations sont constructives, personnalisées et encourageantes.",
            'conseil_classe': "Tu es un professeur principal préparant le conseil de classe. Tes appréciations sont synthétiques et orientées vers l'orientation.",
            'parents': "Tu rédiges une appréciation destinée aux parents, claire et bienveillante, expliquant les progrès et besoins de leur enfant.",
            'orientation': "Tu es un conseiller d'orientation aidant à la préparation de l'orientation future de l'élève."
        }
        
        # Contraintes de longueur
        length_constraints = {
            'courte': "2-3 phrases maximum, très synthétique",
            'standard': "3-4 phrases, équilibrée entre synthèse et détail",
            'détaillée': "4-6 phrases, analyse approfondie avec conseils précis"
        }
        
        # Tons disponibles
        tone_instructions = {
            'bienveillant': "Ton bienveillant et encourageant, même pour les difficultés",
            'neutre': "Ton professionnel et objectif, factuel",
            'motivant': "Ton particulièrement encourageant et stimulant",
            'ferme': "Ton ferme mais juste, pour recadrer si nécessaire"
        }
        
        prompt = f"""Contexte de l'élève :
- Prénom : {profile['name']}
- Matière : {profile['subject']}
- Moyenne : {profile['average']}/20 (niveau {profile['level']})
- Progression : {profile['progression']}
- Comportement : {profile['behavior']}
- Participation : {profile['participation']}
- Travail personnel : {profile['homework']}
- Assiduité : {profile['attendance']}

Points forts identifiés : {', '.join(profile['strengths']) if profile['strengths'] else 'À identifier'}
Axes d'amélioration : {', '.join(profile['areas_for_improvement']) if profile['areas_for_improvement'] else 'À identifier'}

Consignes de rédaction :
- Type d'appréciation : {appreciation_type}
- Ton : {tone_instructions.get(tone, tone_instructions['bienveillant'])}
- Longueur : {length_constraints.get(length, length_constraints['standard'])}
"""
        
        if focus_areas:
            prompt += f"\n- Axes prioritaires à mentionner : {', '.join(focus_areas)}"
        
        prompt += f"""

Rédige une appréciation qui :
1. Utilise le prénom de l'élève
2. Mentionne les points forts avant les difficultés
3. Donne des conseils constructifs et réalisables
4. Reste positive même en cas de difficultés
5. Évite les formulations négatives ou décourageantes
6. S'adapte au niveau et à la situation de l'élève

L'appréciation doit être prête à être copiée directement dans un bulletin."""
        
        return prompt
    
    def _build_messages(self, prompt, tone):
        """Construire les messages pour l'API"""
        system_message = {
            "role": "system", 
            "content": "Tu es un professeur expérimenté spécialisé dans la rédaction d'appréciations scolaires constructives et personnalisées."
        }
        
        user_message = {
            "role": "user",
            "content": prompt
        }
        
        return [system_message, user_message]
    
    def _call_api_with_retry(self, messages, options):
        """Appeler l'API avec retry et fallback"""
        max_retries = options.get('max_retries', 2)
        
        for attempt in range(max_retries + 1):
            try:
                temperature = options.get('temperature', 0.7)
                max_tokens = options.get('max_tokens', 200)
                
                result = self._call_api(messages, temperature=temperature, max_tokens=max_tokens)
                
                if result and len(result.strip()) > 20:
                    return result
                    
            except Exception as e:
                logger.warning(f"Tentative {attempt + 1} échouée: {e}")
                if attempt == max_retries:
                    raise e
        
        return None
    
    def _advanced_post_process(self, appreciation, profile, options):
        """Post-traitement avancé de l'appréciation"""
        if not appreciation or len(appreciation.strip()) < 20:
            return self._get_smart_default_appreciation(profile)
        
        # Nettoyage de base
        appreciation = appreciation.strip()
        
        # Supprimer les guillemets en début/fin
        appreciation = re.sub(r'^["\']|["\']$', '', appreciation)
        
        # Corriger la ponctuation
        appreciation = self._fix_punctuation(appreciation)
        
        # Vérifier la présence du prénom
        if profile['name'].lower() not in appreciation.lower():
            appreciation = self._add_name_if_missing(appreciation, profile['name'])
        
        # Ajuster la longueur selon les options
        length = options.get('length', 'standard')
        appreciation = self._adjust_length(appreciation, length)
        
        # Validation finale
        if len(appreciation) < 30:
            return self._get_smart_default_appreciation(profile)
        
        return appreciation
    
    def _fix_punctuation(self, text):
        """Corriger la ponctuation"""
        # Ajouter un point final si nécessaire
        if not text.endswith(('.', '!', '?')):
            text += '.'
        
        # Corriger les espaces autour de la ponctuation
        text = re.sub(r'\s+([,.!?])', r'\1', text)
        text = re.sub(r'([,.!?])([A-Za-z])', r'\1 \2', text)
        
        return text
    
    def _add_name_if_missing(self, appreciation, name):
        """Ajouter le prénom si manquant"""
        if name.lower() not in appreciation.lower():
            # Essayer d'insérer le prénom naturellement
            if appreciation.startswith(('Élève', 'Etudiant', 'Il ', 'Elle ')):
                appreciation = appreciation.replace('Élève', name, 1)
                appreciation = appreciation.replace('Etudiant', name, 1)
                appreciation = appreciation.replace('Il ', f'{name} ', 1)
                appreciation = appreciation.replace('Elle ', f'{name} ', 1)
            else:
                # Ajouter au début
                appreciation = f"{name} : {appreciation.lower()}"
        
        return appreciation
    
    def _adjust_length(self, appreciation, target_length):
        """Ajuster la longueur de l'appréciation"""
        sentences = appreciation.split('. ')
        
        if target_length == 'courte' and len(sentences) > 3:
            return '. '.join(sentences[:2]) + '.'
        elif target_length == 'détaillée' and len(sentences) < 4:
            # Garde le texte tel quel, on ne peut pas l'allonger artificiellement
            return appreciation
        
        return appreciation
    
    def _calculate_confidence(self, appreciation, profile):
        """Calculer un score de confiance de la génération"""
        confidence = 0.5  # Base
        
        # Bonus si contient le prénom
        if profile['name'].lower() in appreciation.lower():
            confidence += 0.2
        
        # Bonus selon la longueur appropriée
        word_count = len(appreciation.split())
        if 20 <= word_count <= 60:
            confidence += 0.2
        
        # Bonus si structure cohérente
        if '. ' in appreciation:  # Plusieurs phrases
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _log_generation(self, student, subject, appreciation, options):
        """Enregistrer la génération pour amélioration future"""
        try:
            # Pour l'instant, juste logger
            logger.info(f"Appréciation générée pour {student.first_name} en {subject}: "
                       f"{len(appreciation)} caractères, options: {options}")
        except Exception as e:
            logger.error(f"Erreur logging génération: {e}")
    
    def _get_fallback_appreciation(self, student, subject, average, period):
        """Appréciation de secours en cas d'erreur complète"""
        profile = self._analyze_student_profile(student, subject, average, period)
        
        return {
            'content': self._get_smart_default_appreciation(profile),
            'confidence': 0.3,
            'metadata': {
                'type': 'fallback',
                'generated_at': timezone.now().isoformat(),
                'is_default': True
            }
        }
    
    def _get_smart_default_appreciation(self, profile):
        """Appréciation par défaut intelligente"""
        templates = self._get_enhanced_templates()
        
        level = profile.get('level', 'satisfaisant')
        progression = profile.get('progression', 'stable')
        behavior = profile.get('behavior', 'correct')
        
        # Choisir le template selon le contexte
        template_key = level
        if progression in ['en progression', 'en nette progression']:
            template_key += '_progression'
        elif behavior == 'à améliorer':
            template_key += '_comportement'
        
        templates_for_level = templates.get(template_key, templates.get(level, templates['satisfaisant']))
        template = random.choice(templates_for_level)
        
        return template.format(
            name=profile['name'],
            subject=profile['subject'],
            progression=profile['progression'],
            behavior=profile['behavior']
        )
    
    def _get_enhanced_templates(self):
        """Templates améliorés par contexte"""
        return {
            'excellent': [
                "{name} obtient d'excellents résultats en {subject}. Le travail fourni est remarquable et constant. Continuez dans cette voie !",
                "Trimestre excellent pour {name}. La qualité du travail et l'implication en classe sont exemplaires.",
                "{name} démontre une maîtrise remarquable en {subject}. L'attitude studieuse et les efforts constants sont à souligner."
            ],
            'excellent_progression': [
                "{name} réalise un parcours exceptionnel en {subject}. La progression constante témoigne d'un travail sérieux et efficace.",
                "Excellents résultats et belle progression pour {name}. Cette dynamique positive est très encourageante."
            ],
            'très bon': [
                "{name} réalise un très bon trimestre en {subject}. Les efforts sont constants et les résultats encourageants.",
                "Très bon niveau atteint par {name}. Le travail régulier et l'investissement portent leurs fruits.",
                "{name} fait preuve de sérieux et d'efficacité en {subject}. Les résultats obtenus sont très satisfaisants."
            ],
            'bon': [
                "{name} obtient de bons résultats en {subject}. L'attitude positive et les efforts fournis sont appréciables.",
                "Bon trimestre pour {name}. Le travail est régulier et les progrès visibles. Poursuivez vos efforts !",
                "{name} démontre de bonnes capacités en {subject}. Avec de la constance, les résultats peuvent encore s'améliorer."
            ],
            'satisfaisant': [
                "{name} obtient des résultats satisfaisants en {subject}. Un travail plus approfondi permettrait de progresser davantage.",
                "Niveau satisfaisant pour {name}. Il convient d'approfondir le travail personnel pour consolider les acquis.",
                "{name} peut mieux faire en {subject}. Les capacités sont présentes, il faut les exploiter davantage."
            ],
            'fragile': [
                "{name} rencontre quelques difficultés en {subject}. Un travail plus soutenu et régulier est nécessaire pour progresser.",
                "Résultats fragiles pour {name}. Il est important de reprendre les notions de base et de demander de l'aide si nécessaire.",
                "{name} doit fournir des efforts supplémentaires en {subject}. Avec de la méthode et de la persévérance, les progrès viendront."
            ],
            'insuffisant': [
                "{name} doit impérativement se mobiliser en {subject}. Un accompagnement personnalisé et un travail assidu sont indispensables.",
                "Niveau insuffisant pour {name}. Il est urgent de revoir les fondamentaux et de s'investir davantage dans cette matière.",
                "{name} nécessite un suivi renforcé en {subject}. Les difficultés actuelles peuvent être surmontées avec un travail adapté."
            ]
        }
    
    def _analyze_student_profile(self, student, subject, average, period):
        """Analyser le profil de l'élève"""
        from apps.grades.models import Grade, SubjectAverage
        from apps.attendance.models import Attendance, StudentBehavior
        
        profile = {
            'name': student.first_name,
            'subject': subject.name,
            'average': float(average) if average else None,
            'level': self._get_level(average),
            'progression': 'stable',
            'behavior': 'correct',
            'participation': 'moyenne',
            'homework': 'régulier'
        }
        
        # Analyser la progression
        previous_avg = SubjectAverage.objects.filter(
            student=student,
            subject=subject,
            grading_period__number__lt=period.number
        ).order_by('-grading_period__number').first()
        
        if previous_avg and previous_avg.average and average:
            diff = float(average - previous_avg.average)
            if diff > 1:
                profile['progression'] = 'en progrès'
            elif diff < -1:
                profile['progression'] = 'en baisse'
        
        # Analyser le comportement
        behaviors = StudentBehavior.objects.filter(
            student=student,
            date__range=[period.start_date, period.end_date]
        )
        
        positive_count = behaviors.filter(behavior_type='positive').count()
        negative_count = behaviors.filter(behavior_type='negative').count()
        
        if positive_count > negative_count * 2:
            profile['behavior'] = 'excellent'
        elif negative_count > positive_count:
            profile['behavior'] = 'à améliorer'
        
        return profile
    
    def _get_level(self, average):
        """Déterminer le niveau selon la moyenne"""
        if not average:
            return 'non évalué'
        
        avg = float(average)
        if avg >= 16:
            return 'excellent'
        elif avg >= 14:
            return 'très bon'
        elif avg >= 12:
            return 'bon'
        elif avg >= 10:
            return 'satisfaisant'
        elif avg >= 8:
            return 'fragile'
        else:
            return 'insuffisant'
    
    def _build_prompt(self, profile):
        """Construire le prompt pour l'IA"""
        prompt = f"""Rédige une appréciation de bulletin scolaire pour :
- Élève : {profile['name']}
- Matière : {profile['subject']}
- Moyenne : {profile['average']}/20
- Niveau : {profile['level']}
- Progression : {profile['progression']}
- Comportement : {profile['behavior']}

L'appréciation doit être :
- Bienveillante et constructive
- Personnalisée (utiliser le prénom)
- Entre 2 et 4 phrases
- Incluant des conseils pour progresser
- Évitant les formulations négatives
"""
        
        return prompt
    
    def _post_process(self, appreciation, profile):
        """Post-traiter l'appréciation générée"""
        if not appreciation or len(appreciation) < 20:
            # Utiliser une appréciation par défaut
            return self._get_default_appreciation(profile)
        
        # Nettoyer
        appreciation = appreciation.strip()
        
        # S'assurer qu'elle se termine par un point
        if not appreciation.endswith('.'):
            appreciation += '.'
        
        # Limiter la longueur
        if len(appreciation) > 300:
            # Couper à la dernière phrase complète
            sentences = appreciation.split('. ')
            appreciation = '. '.join(sentences[:3]) + '.'
        
        return appreciation
    
    def _get_default_appreciation(self, profile):
        """Appréciation par défaut selon le profil"""
        templates = {
            'excellent': [
                "{name} obtient d'excellents résultats en {subject}. Le travail est sérieux et régulier. Continuez ainsi !",
                "Trimestre excellent pour {name}. La participation active et la qualité du travail sont remarquables.",
            ],
            'très bon': [
                "{name} réalise un très bon trimestre en {subject}. Les efforts sont constants et payants.",
                "Très bon niveau en {subject}. {name} fait preuve de sérieux et d'implication.",
            ],
            'bon': [
                "{name} obtient de bons résultats en {subject}. L'attitude est positive. Poursuivez vos efforts.",
                "Bon trimestre pour {name}. Le travail est régulier et les résultats encourageants.",
            ],
            'satisfaisant': [
                "{name} obtient des résultats satisfaisants. Des efforts supplémentaires permettraient de progresser.",
                "Niveau satisfaisant en {subject}. {name} doit approfondir davantage le travail personnel.",
            ],
            'fragile': [
                "{name} rencontre des difficultés en {subject}. Un travail plus régulier est nécessaire.",
                "Résultats fragiles. {name} doit fournir plus d'efforts et demander de l'aide si besoin.",
            ],
            'insuffisant': [
                "{name} doit impérativement se ressaisir en {subject}. Un suivi personnalisé est recommandé.",
                "Niveau insuffisant. {name} doit revoir les bases et s'investir davantage dans la matière.",
            ]
        }
        
        level = profile.get('level', 'satisfaisant')
        template = random.choice(templates.get(level, templates['satisfaisant']))
        
        return template.format(
            name=profile['name'],
            subject=profile['subject']
        )
    
    def _demo_response(self):
        """Réponse de démonstration"""
        return "Élève sérieux et motivé. Les résultats sont encourageants. Continuez vos efforts."
    
    def _fallback_response(self):
        """Réponse de secours"""
        return "Trimestre satisfaisant. Poursuivez vos efforts."