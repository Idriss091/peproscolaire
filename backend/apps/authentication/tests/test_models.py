"""
Tests pour les modèles d'authentification
"""
import pytest
from django.contrib.auth import get_user_model
from apps.authentication.models import UserProfile, PasswordResetToken
from datetime import timedelta
from django.utils import timezone

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Tests pour le modèle User"""
    
    def test_create_user(self):
        """Test de création d'un utilisateur standard"""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        assert user.email == 'test@example.com'
        assert user.username == 'testuser'
        assert user.check_password('testpass123')
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser
        assert user.user_type == 'student'
    
    def test_create_superuser(self):
        """Test de création d'un superutilisateur"""
        admin = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        
        assert admin.is_staff
        assert admin.is_superuser
        assert admin.user_type == 'student'  # Par défaut
    
    def test_user_str_representation(self):
        """Test de la représentation string de l'utilisateur"""
        user = User(
            email='test@example.com',
            first_name='John',
            last_name='Doe',
            user_type='teacher'
        )
        
        assert str(user) == "John Doe (teacher)"
    
    def test_get_full_name(self):
        """Test de la méthode get_full_name"""
        user = User(
            email='test@example.com',
            first_name='Jane',
            last_name='Smith'
        )
        
        assert user.get_full_name() == "Jane Smith"
    
    def test_email_as_username_field(self):
        """Test que l'email est bien le champ de connexion"""
        assert User.USERNAME_FIELD == 'email'


@pytest.mark.django_db
class TestUserProfileModel:
    """Tests pour le modèle UserProfile"""
    
    def test_profile_creation(self):
        """Test de création automatique du profil"""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        # Le profil devrait être créé via le signal
        profile = UserProfile.objects.create(user=user)
        
        assert profile.user == user
        assert profile.email_notifications is True
        assert profile.sms_notifications is False
    
    def test_profile_str_representation(self):
        """Test de la représentation string du profil"""
        user = User(first_name='Test', last_name='User')
        profile = UserProfile(user=user)
        
        assert str(profile) == "Profil de Test User"


@pytest.mark.django_db
class TestPasswordResetToken:
    """Tests pour le modèle PasswordResetToken"""
    
    def test_token_creation(self):
        """Test de création d'un token de réinitialisation"""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        token = PasswordResetToken.objects.create(user=user)
        
        assert token.user == user
        assert not token.is_used
        assert token.token is not None
    
    def test_token_expiration(self):
        """Test de l'expiration du token"""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        # Token non expiré
        token_valid = PasswordResetToken.objects.create(user=user)
        assert not token_valid.is_expired()
        
        # Token expiré (créé il y a plus de 24h)
        token_expired = PasswordResetToken.objects.create(user=user)
        token_expired.created_at = timezone.now() - timedelta(hours=25)
        token_expired.save()
        
        assert token_expired.is_expired()