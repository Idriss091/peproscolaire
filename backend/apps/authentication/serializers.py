"""
Serializers pour l'API d'authentification
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, UserProfile, PasswordResetToken


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer pour le profil utilisateur"""
    
    class Meta:
        model = UserProfile
        fields = [
            'avatar', 'date_of_birth', 'address', 'postal_code', 'city',
            'emergency_contact_name', 'emergency_contact_phone',
            'email_notifications', 'sms_notifications', 'bio'
        ]


class UserSerializer(serializers.ModelSerializer):
    """Serializer pour les informations utilisateur"""
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'user_type', 'phone_number', 'is_active',
            'is_verified', 'created_at', 'profile'
        ]
        read_only_fields = ['id', 'created_at', 'is_verified']


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer pour l'inscription d'un nouvel utilisateur"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'password_confirm',
            'first_name', 'last_name', 'user_type', 'phone_number'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        """Validation personnalisée"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Les mots de passe ne correspondent pas."
            })
        
        # Supprimer password_confirm car non nécessaire pour la création
        attrs.pop('password_confirm')
        return attrs
    
    def create(self, validated_data):
        """Création de l'utilisateur avec profil"""
        # Création de l'utilisateur
        user = User.objects.create_user(**validated_data)
        
        # Création automatique du profil
        UserProfile.objects.create(user=user)
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer pour la connexion"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validation des credentials"""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            # Authentification via email
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    "Email ou mot de passe incorrect."
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    "Ce compte a été désactivé."
                )
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                "Email et mot de passe sont requis."
            )


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer pour demander une réinitialisation de mot de passe"""
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Vérification de l'existence de l'email"""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Aucun compte n'est associé à cette adresse email."
            )
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer pour confirmer la réinitialisation du mot de passe"""
    token = serializers.UUIDField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validation du token et des mots de passe"""
        token = attrs.get('token')
        
        # Vérification du token
        try:
            reset_token = PasswordResetToken.objects.get(
                token=token,
                is_used=False
            )
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError({
                "token": "Token invalide ou déjà utilisé."
            })
        
        # Vérification de l'expiration
        if reset_token.is_expired():
            raise serializers.ValidationError({
                "token": "Ce token a expiré."
            })
        
        # Vérification des mots de passe
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Les mots de passe ne correspondent pas."
            })
        
        attrs['reset_token'] = reset_token
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer pour changer le mot de passe (utilisateur connecté)"""
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    
    def validate_old_password(self, value):
        """Vérification de l'ancien mot de passe"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                "L'ancien mot de passe est incorrect."
            )
        return value