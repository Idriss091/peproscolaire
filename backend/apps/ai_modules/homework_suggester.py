"""
Module IA pour suggérer des devoirs
"""
from .base import BaseAIModule
import json
import random


class HomeworkSuggester(BaseAIModule):
    """Générateur de suggestions de devoirs"""
    
    def generate_suggestions(self, chapter, subject_id, class_level, 
                           lesson_objectives=None, key_concepts=None, 
                           difficulty='medium', count=3):
        """Générer des suggestions de devoirs"""
        
        # Construire le prompt
        prompt = self._build_prompt(
            chapter, subject_id, class_level,
            lesson_objectives, key_concepts, difficulty
        )
        
        # Appeler l'API
        messages = [
            {
                "role": "system",
                "content": "Tu es un assistant pédagogique expert en création de devoirs scolaires."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = self._call_api(messages, temperature=0.8)
        
        # Parser la réponse
        try:
            suggestions = self._parse_response(response)
            return suggestions[:count]
        except:
            return self._demo_response()
    
    def generate_personalized_suggestions(self, subject_id, class_level, 
                                        chapter, teacher_style, 
                                        avoid_repetition=True):
        """Générer des suggestions personnalisées selon le style du prof"""
        
        # Adapter le prompt au style
        base_suggestions = self.generate_suggestions(
            chapter=chapter,
            subject_id=subject_id,
            class_level=class_level,
            difficulty=teacher_style.get('difficulty_preference', 'medium')
        )
        
        # Personnaliser selon le style
        for suggestion in base_suggestions:
            # Adapter la durée
            suggestion['duration'] = teacher_style.get('avg_duration', 30)
            
            # Adapter le style d'instructions
            if teacher_style.get('instruction_style') == 'detailed':
                suggestion['instructions'] = self._expand_instructions(
                    suggestion.get('instructions', '')
                )
        
        return base_suggestions
    
    def _build_prompt(self, chapter, subject_id, class_level, 
                     lesson_objectives, key_concepts, difficulty):
        """Construire le prompt pour l'IA"""
        
        prompt = f"""Génère {3} suggestions de devoirs pour :
- Niveau : {class_level}
- Chapitre : {chapter}
- Difficulté : {difficulty}
"""
        
        if lesson_objectives:
            prompt += f"\n- Objectifs : {lesson_objectives}"
        
        if key_concepts:
            prompt += f"\n- Notions clés : {key_concepts}"
        
        prompt += """

Pour chaque devoir, fournis au format JSON :
{
    "title": "Titre du devoir",
    "description": "Description détaillée",
    "instructions": "Instructions pour les élèves",
    "difficulty": "easy/medium/hard",
    "duration": durée estimée en minutes,
    "type": "exercices/recherche/rédaction/projet"
}
"""
        
        return prompt
    
    def _parse_response(self, response):
        """Parser la réponse de l'IA"""
        # Essayer de parser le JSON
        try:
            # Extraire le JSON de la réponse
            import re
            json_matches = re.findall(r'\{[^}]+\}', response)
            
            suggestions = []
            for match in json_matches:
                try:
                    suggestion = json.loads(match)
                    suggestions.append(suggestion)
                except:
                    pass
            
            return suggestions
        except:
            # Si échec, créer des suggestions basiques
            return self._demo_response()
    
    def _expand_instructions(self, instructions):
        """Développer les instructions pour un style détaillé"""
        expanded = instructions
        
        additions = [
            "\n\nConseils méthodologiques :",
            "- Commencez par lire attentivement l'énoncé",
            "- Identifiez les notions clés à utiliser",
            "- Rédigez vos réponses de manière structurée",
            "- Relisez-vous avant de rendre"
        ]
        
        return expanded + "\n".join(additions)
    
    def _demo_response(self):
        """Réponse de démonstration"""
        templates = [
            {
                "title": "Exercices d'application - {}",
                "description": "Série d'exercices pour pratiquer les notions vues en cours sur {}",
                "instructions": "Faire les exercices dans l'ordre. Bien détailler les calculs.",
                "difficulty": "medium",
                "duration": 30,
                "type": "exercices"
            },
            {
                "title": "Recherche documentaire - {}",
                "description": "Recherche sur {} avec présentation des résultats",
                "instructions": "Rechercher des informations fiables et citer les sources.",
                "difficulty": "medium",
                "duration": 45,
                "type": "recherche"
            },
            {
                "title": "Rédaction - {}",
                "description": "Rédiger un texte argumenté sur {}",
                "instructions": "Introduction, développement en 2 parties, conclusion.",
                "difficulty": "hard",
                "duration": 60,
                "type": "rédaction"
            }
        ]
        
        # Sélectionner aléatoirement et personnaliser
        suggestions = []
        for _ in range(3):
            template = random.choice(templates).copy()
            template['title'] = template['title'].format("le chapitre")
            template['description'] = template['description'].format("les notions du chapitre")
            suggestions.append(template)
        
        return suggestions
    
    def _fallback_response(self):
        """Réponse de secours"""
        return [{
            "title": "Devoir sur le chapitre",
            "description": "Exercices et questions sur les notions étudiées",
            "instructions": "À faire avec soin",
            "difficulty": "medium",
            "duration": 30,
            "type": "exercices"
        }]