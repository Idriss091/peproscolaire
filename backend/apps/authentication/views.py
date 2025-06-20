"""
Vues API pour l'authentification
"""
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import uuid

from .models import PasswordResetToken
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    ChangePasswordSerializer
)

User = get_user_model()


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Endpoint de vérification de santé de l'API"""
    return Response({
        'status': 'healthy',
        'message': 'PeproScolaire API is running',
        'timestamp': request.META.get('HTTP_HOST', 'localhost'),
        'version': '1.0.0'
    })


class RegisterView(generics.CreateAPIView):
    """
    Vue pour l'inscription d'un nouvel utilisateur
    Accessible publiquement
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Création de l'utilisateur
        user = serializer.save()
        
        # Génération des tokens JWT
        refresh = RefreshToken.for_user(user)
        
        # Sérialisation des données utilisateur
        user_serializer = UserSerializer(user)
        
        return Response({
            'user': user_serializer.data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Inscription réussie !'
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    Vue pour la connexion utilisateur
    Retourne les tokens JWT et les informations utilisateur
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    
    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Génération des tokens JWT
        refresh = RefreshToken.for_user(user)
        
        # Sérialisation des données utilisateur
        user_serializer = UserSerializer(user)
        
        return Response({
            'user': user_serializer.data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Connexion réussie !'
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    Vue pour la déconnexion
    Invalide le refresh token
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({
                'message': 'Déconnexion réussie !'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Token invalide'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Vue pour récupérer et mettre à jour le profil utilisateur
    Accessible uniquement à l'utilisateur connecté
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'user': serializer.data,
            'message': 'Profil mis à jour avec succès !'
        })


class PasswordResetRequestView(APIView):
    """
    Vue pour demander une réinitialisation de mot de passe
    Envoie un email avec un lien de réinitialisation
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # Création du token de réinitialisation
        reset_token = PasswordResetToken.objects.create(user=user)
        
        # Préparation de l'email
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{reset_token.token}"
        context = {
            'user': user,
            'reset_url': reset_url
        }
        
        # Email HTML
        html_message = render_to_string(
            'emails/password_reset.html',
            context
        )
        plain_message = strip_tags(html_message)
        
        # Envoi de l'email
        send_mail(
            subject='Réinitialisation de votre mot de passe - PeproScolaire',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False
        )
        
        return Response({
            'message': 'Un email de réinitialisation a été envoyé.'
        }, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """
    Vue pour confirmer la réinitialisation du mot de passe
    Vérifie le token et met à jour le mot de passe
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        reset_token = serializer.validated_data['reset_token']
        new_password = serializer.validated_data['password']
        
        # Mise à jour du mot de passe
        user = reset_token.user
        user.set_password(new_password)
        user.save()
        
        # Marquage du token comme utilisé
        reset_token.is_used = True
        reset_token.save()
        
        return Response({
            'message': 'Mot de passe réinitialisé avec succès !'
        }, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    """
    Vue pour changer le mot de passe (utilisateur connecté)
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    
    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        # Mise à jour du mot de passe
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'message': 'Mot de passe modifié avec succès !'
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_token(request):
    """
    Endpoint pour vérifier la validité d'un token
    Utile pour le frontend
    """
    if request.user.is_authenticated:
        serializer = UserSerializer(request.user)
        return Response({
            'valid': True,
            'user': serializer.data
        })
    else:
        return Response({
            'valid': False
        }, status=status.HTTP_401_UNAUTHORIZED)