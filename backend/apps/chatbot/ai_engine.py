import re
import json
import logging
import openai
import requests
from typing import Dict, List, Tuple, Optional
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from .models import ChatbotIntent, ChatbotKnowledgeBase, ChatbotMessage
from ..ai_modules.base import BaseAIModule

User = get_user_model()
logger = logging.getLogger(__name__)


class ChatbotAIEngine(BaseAIModule):
    """
    Moteur IA pour le chatbot PeproScolaire
    """
    
    def __init__(self):
        super().__init__()
        self.model_name = "gpt-3.5-turbo"
        self.max_tokens = 150
        self.temperature = 0.7
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        self.knowledge_vectors = None
        self.knowledge_items = []
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """Charge et vectorise la base de connaissances"""
        try:
            knowledge_items = ChatbotKnowledgeBase.objects.filter(status='active')
            if knowledge_items.exists():
                self.knowledge_items = list(knowledge_items)
                texts = [item.content for item in self.knowledge_items]
                self.knowledge_vectors = self.vectorizer.fit_transform(texts)
                logger.info(f"Base de connaissances chargée: {len(self.knowledge_items)} éléments")
            else:
                logger.warning("Aucun élément actif dans la base de connaissances")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la base de connaissances: {e}")
    
    def process_message(self, message: str, user: User, conversation_id: str) -> Dict:
        """
        Traite un message utilisateur et génère une réponse
        """
        start_time = timezone.now()
        
        try:
            # 1. Analyse de l'intention
            intent_result = self._analyze_intent(message)
            
            # 2. Recherche dans la base de connaissances
            knowledge_result = self._search_knowledge_base(message)
            
            # 3. Génération de la réponse
            response = self._generate_response(
                message=message,
                user=user,
                conversation_id=conversation_id,
                intent=intent_result,
                knowledge=knowledge_result
            )
            
            # Calcul du temps de réponse
            response_time = (timezone.now() - start_time).total_seconds() * 1000
            response['response_time_ms'] = int(response_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement du message: {e}")
            return self._get_error_response()
    
    def _analyze_intent(self, message: str) -> Dict:
        """Analyse l'intention du message"""
        try:
            # Normaliser le message
            normalized_message = message.lower().strip()
            
            # Rechercher des correspondances avec les intentions prédéfinies
            intents = ChatbotIntent.objects.filter(is_active=True).order_by('-priority')
            
            best_match = None
            best_score = 0.0
            
            for intent in intents:
                score = self._calculate_intent_score(normalized_message, intent)
                if score > best_score:
                    best_score = score
                    best_match = intent
            
            if best_match and best_score > 0.6:
                return {
                    'intent': best_match.name,
                    'confidence_score': best_score,
                    'action_type': best_match.action_type,
                    'action_parameters': best_match.action_parameters,
                    'requires_auth': best_match.requires_authentication,
                    'requires_admin': best_match.requires_admin
                }
            
            # Utiliser l'IA pour analyser l'intention si aucune correspondance
            return self._analyze_intent_with_ai(message)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse d'intention: {e}")
            return {'intent': 'unknown', 'confidence_score': 0.0}
    
    def _calculate_intent_score(self, message: str, intent: ChatbotIntent) -> float:
        """Calcule le score de correspondance pour une intention"""
        score = 0.0
        pattern_count = len(intent.patterns)
        
        if pattern_count == 0:
            return 0.0
        
        for pattern in intent.patterns:
            # Recherche de mots-clés
            if isinstance(pattern, str):
                if pattern.lower() in message:
                    score += 1.0
            # Recherche par expression régulière
            elif isinstance(pattern, dict) and pattern.get('type') == 'regex':
                if re.search(pattern['pattern'], message, re.IGNORECASE):
                    score += pattern.get('weight', 1.0)
        
        return score / pattern_count
    
    def _analyze_intent_with_ai(self, message: str) -> Dict:
        """Utilise l'IA pour analyser l'intention"""
        try:
            if not self.openai_available:
                return {'intent': 'general', 'confidence_score': 0.5}
            
            prompt = f"""
            Analysez l'intention de ce message d'un étudiant dans un système scolaire:
            
            Message: "{message}"
            
            Catégories possibles:
            - support: Questions techniques
            - academic: Aide aux devoirs, cours
            - administrative: Procédures, inscriptions
            - orientation: Conseils d'orientation
            - social: Problèmes personnels, sociaux
            - emergency: Situations d'urgence
            - general: Autres questions
            
            Répondez en JSON avec l'intention et un score de confiance (0-1).
            """
            
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            return {
                'intent': result.get('intent', 'general'),
                'confidence_score': result.get('confidence', 0.5)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse IA: {e}")
            return {'intent': 'general', 'confidence_score': 0.3}
    
    def _search_knowledge_base(self, message: str, limit: int = 3) -> List[Dict]:
        """Recherche dans la base de connaissances"""
        try:
            if not self.knowledge_vectors or not self.knowledge_items:
                return []
            
            # Vectoriser la requête
            query_vector = self.vectorizer.transform([message])
            
            # Calculer les similarités
            similarities = cosine_similarity(query_vector, self.knowledge_vectors).flatten()
            
            # Trouver les meilleurs résultats
            top_indices = np.argsort(similarities)[::-1][:limit]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0.3:  # Seuil minimum de similarité
                    knowledge_item = self.knowledge_items[idx]
                    results.append({
                        'title': knowledge_item.title,
                        'content': knowledge_item.content,
                        'knowledge_type': knowledge_item.knowledge_type,
                        'category': knowledge_item.category,
                        'similarity_score': float(similarities[idx]),
                        'id': str(knowledge_item.id)
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche dans la base de connaissances: {e}")
            return []
    
    def _generate_response(self, message: str, user: User, conversation_id: str, 
                          intent: Dict, knowledge: List[Dict]) -> Dict:
        """Génère la réponse du chatbot"""
        try:
            # Vérifier si une réponse prédéfinie existe
            predefined_response = self._get_predefined_response(intent, knowledge)
            if predefined_response:
                return predefined_response
            
            # Générer une réponse contextuelle avec l'IA
            if self.openai_available:
                return self._generate_ai_response(message, user, intent, knowledge)
            
            # Réponse de fallback
            return self._get_fallback_response(intent, knowledge)
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de réponse: {e}")
            return self._get_error_response()
    
    def _get_predefined_response(self, intent: Dict, knowledge: List[Dict]) -> Optional[Dict]:
        """Récupère une réponse prédéfinie si disponible"""
        try:
            intent_name = intent.get('intent')
            if not intent_name:
                return None
            
            # Chercher l'intention dans la base
            try:
                intent_obj = ChatbotIntent.objects.get(name=intent_name, is_active=True)
                if intent_obj.responses:
                    import random
                    response_text = random.choice(intent_obj.responses)
                    
                    return {
                        'message': response_text,
                        'message_type': 'text',
                        'intent': intent_name,
                        'confidence_score': intent['confidence_score'],
                        'quick_replies': self._get_quick_replies(intent_name),
                        'needs_human': False
                    }
            except ChatbotIntent.DoesNotExist:
                pass
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de réponse prédéfinie: {e}")
            return None
    
    def _generate_ai_response(self, message: str, user: User, 
                            intent: Dict, knowledge: List[Dict]) -> Dict:
        """Génère une réponse avec l'IA"""
        try:
            # Construire le contexte
            context = self._build_context(user, intent, knowledge)
            
            prompt = f"""
            Tu es un assistant IA pour PeproScolaire, un système de gestion scolaire.
            Tu aides les étudiants, parents et enseignants.
            
            Contexte utilisateur:
            {context}
            
            Message de l'utilisateur: "{message}"
            
            Base de connaissances pertinente:
            {self._format_knowledge_for_prompt(knowledge)}
            
            Intention détectée: {intent.get('intent', 'inconnue')}
            
            Réponds de manière helpful, précise et bienveillante.
            Si tu ne peux pas répondre, propose de contacter un humain.
            Limite ta réponse à 200 mots maximum.
            """
            
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            response_text = response.choices[0].message.content.strip()
            
            return {
                'message': response_text,
                'message_type': 'text',
                'intent': intent.get('intent'),
                'confidence_score': intent.get('confidence_score'),
                'quick_replies': self._get_quick_replies(intent.get('intent')),
                'suggestions': self._get_suggestions(knowledge),
                'needs_human': self._needs_human_assistance(intent, response_text),
                'tokens_used': response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération IA: {e}")
            return self._get_fallback_response(intent, knowledge)
    
    def _build_context(self, user: User, intent: Dict, knowledge: List[Dict]) -> str:
        """Construit le contexte pour l'IA"""
        context_parts = []
        
        # Informations utilisateur
        context_parts.append(f"Utilisateur: {user.get_full_name() or user.username}")
        
        if hasattr(user, 'profile'):
            if hasattr(user.profile, 'role'):
                context_parts.append(f"Rôle: {user.profile.role}")
        
        # Contexte temporel
        context_parts.append(f"Date: {timezone.now().strftime('%Y-%m-%d %H:%M')}")
        
        return "\n".join(context_parts)
    
    def _format_knowledge_for_prompt(self, knowledge: List[Dict]) -> str:
        """Formate la base de connaissances pour le prompt"""
        if not knowledge:
            return "Aucune information pertinente trouvée."
        
        formatted = []
        for item in knowledge[:3]:  # Limite à 3 éléments
            formatted.append(f"- {item['title']}: {item['content'][:200]}...")
        
        return "\n".join(formatted)
    
    def _get_fallback_response(self, intent: Dict, knowledge: List[Dict]) -> Dict:
        """Génère une réponse de fallback"""
        intent_name = intent.get('intent', 'unknown')
        
        fallback_responses = {
            'support': "Je peux vous aider avec les questions techniques. Pouvez-vous me donner plus de détails sur votre problème ?",
            'academic': "Je suis là pour vous aider avec vos questions académiques. De quel sujet avez-vous besoin d'aide ?",
            'administrative': "Pour les questions administratives, je peux vous orienter. Quelle procédure vous intéresse ?",
            'orientation': "Je peux vous donner des conseils d'orientation. Quel est votre domaine d'intérêt ?",
            'emergency': "Si c'est une urgence, contactez immédiatement votre établissement ou les services d'urgence.",
            'unknown': "Je ne suis pas sûr de comprendre votre question. Pouvez-vous la reformuler ?"
        }
        
        message = fallback_responses.get(intent_name, fallback_responses['unknown'])
        
        # Ajouter des suggestions basées sur la base de connaissances
        if knowledge:
            suggestions = [item['title'] for item in knowledge[:3]]
        else:
            suggestions = ["Contacter le support", "Voir la FAQ", "Parler à un conseiller"]
        
        return {
            'message': message,
            'message_type': 'text',
            'intent': intent_name,
            'confidence_score': intent.get('confidence_score', 0.5),
            'suggestions': suggestions,
            'needs_human': intent_name in ['emergency', 'unknown']
        }
    
    def _get_error_response(self) -> Dict:
        """Réponse en cas d'erreur"""
        return {
            'message': "Je rencontre une difficulté technique. Un conseiller va vous contacter sous peu.",
            'message_type': 'text',
            'intent': 'error',
            'confidence_score': 1.0,
            'needs_human': True,
            'quick_replies': [
                {'text': 'Contacter le support', 'action': 'contact_support'},
                {'text': 'Réessayer plus tard', 'action': 'retry_later'}
            ]
        }
    
    def _get_quick_replies(self, intent: str) -> List[Dict]:
        """Génère des réponses rapides basées sur l'intention"""
        quick_replies_map = {
            'support': [
                {'text': 'Problème de connexion', 'action': 'login_help'},
                {'text': 'Mot de passe oublié', 'action': 'password_reset'},
                {'text': 'Autre problème', 'action': 'other_support'}
            ],
            'academic': [
                {'text': 'Voir mes notes', 'action': 'view_grades'},
                {'text': 'Planning des cours', 'action': 'view_schedule'},
                {'text': 'Devoirs à rendre', 'action': 'view_homework'}
            ],
            'administrative': [
                {'text': 'Certificat de scolarité', 'action': 'request_certificate'},
                {'text': 'Absence à justifier', 'action': 'justify_absence'},
                {'text': 'Contact administration', 'action': 'contact_admin'}
            ]
        }
        
        return quick_replies_map.get(intent, [])
    
    def _get_suggestions(self, knowledge: List[Dict]) -> List[str]:
        """Génère des suggestions basées sur la base de connaissances"""
        if not knowledge:
            return []
        
        return [item['title'] for item in knowledge[:3]]
    
    def _needs_human_assistance(self, intent: Dict, response_text: str) -> bool:
        """Détermine si une assistance humaine est nécessaire"""
        intent_name = intent.get('intent', '')
        confidence = intent.get('confidence_score', 0.0)
        
        # Critères pour redirection vers un humain
        if intent_name in ['emergency', 'unknown']:
            return True
        
        if confidence < 0.4:
            return True
        
        # Mots-clés indiquant un besoin d'assistance
        human_keywords = ['urgent', 'grave', 'problème important', 'ne comprends pas', 'aide personnalisée']
        if any(keyword in response_text.lower() for keyword in human_keywords):
            return True
        
        return False
    
    def update_knowledge_base(self):
        """Met à jour la base de connaissances vectorisée"""
        self._load_knowledge_base()
        logger.info("Base de connaissances mise à jour")
    
    def get_conversation_summary(self, conversation_id: str) -> str:
        """Génère un résumé de conversation"""
        try:
            messages = ChatbotMessage.objects.filter(
                conversation_id=conversation_id
            ).order_by('timestamp')
            
            if not messages.exists():
                return "Aucun message dans cette conversation."
            
            # Limiter aux 10 derniers messages
            recent_messages = messages[:10]
            conversation_text = "\n".join([
                f"{msg.get_sender_display()}: {msg.content}"
                for msg in recent_messages
            ])
            
            if self.openai_available:
                prompt = f"""
                Résumez cette conversation de support client:
                
                {conversation_text}
                
                Résumé en 2-3 phrases maximum, en français.
                """
                
                response = openai.ChatCompletion.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=100,
                    temperature=0.3
                )
                
                return response.choices[0].message.content.strip()
            
            return f"Conversation avec {len(recent_messages)} messages échangés."
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du résumé: {e}")
            return "Erreur lors de la génération du résumé."