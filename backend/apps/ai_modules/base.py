"""
Classes de base pour les modules IA
"""
import openai
from django.conf import settings
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class BaseAIModule(ABC):
    """Classe de base pour tous les modules IA"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', None)
        if self.api_key:
            openai.api_key = self.api_key
        self.model = getattr(settings, 'AI_MODEL', 'gpt-3.5-turbo')
        
    @abstractmethod
    def generate(self, **kwargs):
        """Méthode principale de génération"""
        pass
    
    def _call_api(self, messages, temperature=0.7, max_tokens=1000):
        """Appeler l'API OpenAI"""
        try:
            if not self.api_key:
                # Mode démo sans API
                return self._demo_response()
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Erreur API IA: {str(e)}")
            return self._fallback_response()
    
    @abstractmethod
    def _demo_response(self):
        """Réponse de démonstration si pas d'API"""
        pass
    
    @abstractmethod
    def _fallback_response(self):
        """Réponse de secours en cas d'erreur"""
        pass