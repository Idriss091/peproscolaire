"""
Tests pour les vues d'authentification
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.authentication.models import PasswordResetToken

User = get_user_model()


@pytest.fixture
def api_client():
    """Fixture pour le client API"""
    return APIClient()


@pytest.fixture
def create_user():
    """Fixture pour créer un utilisateur de test"""
    def _create_user(**kwargs):
        defaults = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)
    return _create_user


@pytest.mark.django_db
class TestRegistrationView:
    """Tests pour l'inscription"""
    
    def test_successful_registration(self, api_client):
        """Test d'inscription réussie"""
        url = reverse('authentication:register')
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'user_type': 'student'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert 'tokens' in response.data
        assert response.data['user']['email'] == 'newuser@example.com'
        assert User.objects.filter(email='newuser@example.com').exists()
    
    def test_registration_password_mismatch(self, api_client):
        """Test d'inscription avec mots de passe différents"""
        url = reverse('authentication:register')
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'newpass123',
            'password_confirm': 'differentpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data
    
    def test_registration_duplicate_email(self, api_client, create_user):
        """Test d'inscription avec email déjà existant"""
        create_user(email='existing@example.com')
        
        url = reverse('authentication:register')
        data = {
            'email': 'existing@example.com',
            'username': 'newuser',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data


@pytest.mark.django_db
class TestLoginView:
    """Tests pour la connexion"""
    
    def test_successful_login(self, api_client, create_user):
        """Test de connexion réussie"""
        user = create_user(
            email='login@example.com',
            password='loginpass123'
        )
        
        url = reverse('authentication:login')
        data = {
            'email': 'login@example.com',
            'password': 'loginpass123'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'user' in response.data
        assert 'tokens' in response.data
        assert response.data['user']['email'] == 'login@example.com'
    
    def test_login_invalid_credentials(self, api_client, create_user):
        """Test de connexion avec mauvais identifiants"""
        create_user(
            email='login@example.com',
            password='correctpass123'
        )
        
        url = reverse('authentication:login')
        data = {
            'email': 'login@example.com',
            'password': 'wrongpass123'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_inactive_user(self, api_client, create_user):
        """Test de connexion avec utilisateur inactif"""
        user = create_user(
            email='inactive@example.com',
            password='inactivepass123'
        )
        user.is_active = False
        user.save()
        
        url = reverse('authentication:login')
        data = {
            'email': 'inactive@example.com',
            'password': 'inactivepass123'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLogoutView:
    """Tests pour la déconnexion"""
    
    def test_successful_logout(self, api_client, create_user):
        """Test de déconnexion réussie"""
        user = create_user()
        api_client.force_authenticate(user=user)
        
        url = reverse('authentication:logout')
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Déconnexion réussie !'
    
    def test_logout_unauthenticated(self, api_client):
        """Test de déconnexion sans authentification"""
        url = reverse('authentication:logout')
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserProfileView:
    """Tests pour le profil utilisateur"""
    
    def test_get_profile(self, api_client, create_user):
        """Test de récupération du profil"""
        user = create_user()
        api_client.force_authenticate(user=user)
        
        url = reverse('authentication:profile')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email
    
    def test_update_profile(self, api_client, create_user):
        """Test de mise à jour du profil"""
        user = create_user()
        api_client.force_authenticate(user=user)
        
        url = reverse('authentication:profile')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '+33612345678'
        }
        
        response = api_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['first_name'] == 'Updated'
        
        user.refresh_from_db()
        assert user.first_name == 'Updated'
    
    def test_profile_unauthenticated(self, api_client):
        """Test d'accès au profil sans authentification"""
        url = reverse('authentication:profile')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestPasswordReset:
    """Tests pour la réinitialisation de mot de passe"""
    
    def test_password_reset_request(self, api_client, create_user):
        """Test de demande de réinitialisation"""
        user = create_user(email='reset@example.com')
        
        url = reverse('authentication:password-reset')
        data = {'email': 'reset@example.com'}
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert PasswordResetToken.objects.filter(user=user).exists()
    
    def test_password_reset_invalid_email(self, api_client):
        """Test avec email inexistant"""
        url = reverse('authentication:password-reset')
        data = {'email': 'nonexistent@example.com'}
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_password_reset_confirm(self, api_client, create_user):
        """Test de confirmation de réinitialisation"""
        user = create_user()
        token = PasswordResetToken.objects.create(user=user)
        
        url = reverse('authentication:password-reset-confirm')
        data = {
            'token': str(token.token),
            'password': 'newpassword123',
            'password_confirm': 'newpassword123'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        
        user.refresh_from_db()
        assert user.check_password('newpassword123')
        
        token.refresh_from_db()
        assert token.is_used


@pytest.mark.django_db
class TestChangePassword:
    """Tests pour le changement de mot de passe"""
    
    def test_change_password_success(self, api_client, create_user):
        """Test de changement de mot de passe réussi"""
        user = create_user(password='oldpass123')
        api_client.force_authenticate(user=user)
        
        url = reverse('authentication:password-change')
        data = {
            'old_password': 'oldpass123',
            'new_password': 'newpass123'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        
        user.refresh_from_db()
        assert user.check_password('newpass123')
    
    def test_change_password_wrong_old(self, api_client, create_user):
        """Test avec ancien mot de passe incorrect"""
        user = create_user(password='correctpass123')
        api_client.force_authenticate(user=user)
        
        url = reverse('authentication:password-change')
        data = {
            'old_password': 'wrongpass123',
            'new_password': 'newpass123'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'old_password' in response.data