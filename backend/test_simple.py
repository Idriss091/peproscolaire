"""
Test simple pour vérifier que Django fonctionne
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class SimpleTest(TestCase):
    def test_basic_django_functionality(self):
        """Test que Django fonctionne correctement"""
        self.assertTrue(True)
    
    def test_user_model_exists(self):
        """Test que le modèle User existe"""
        self.assertTrue(hasattr(User, 'objects'))