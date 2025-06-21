"""
API d'authentification simple pour tester la connexion frontend
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from apps.authentication.models import User
from rest_framework_simplejwt.tokens import RefreshToken
import json

@csrf_exempt
def login_api(request):
    """Endpoint de connexion simple"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({'detail': 'Identifiant et mot de passe requis'}, status=400)
        
        # Authentifier l'utilisateur (par email ou username)
        user = authenticate(request, username=username, password=password)
        
        # Si l'auth par username échoue, essayer par email
        if user is None:
            try:
                # Chercher l'utilisateur par username ou email
                if '@' in username:
                    user_obj = User.objects.get(email=username)
                else:
                    user_obj = User.objects.get(username=username)
                # Authentifier avec l'email (comme défini dans AUTH_USER_MODEL)
                user = authenticate(request, username=user_obj.email, password=password)
            except User.DoesNotExist:
                pass
        
        if user is None:
            return JsonResponse({'detail': 'Identifiants incorrects'}, status=401)
        
        if not user.is_active:
            return JsonResponse({'detail': 'Compte désactivé'}, status=401)
        
        # Générer les tokens JWT
        refresh = RefreshToken.for_user(user)
        
        # Réponse avec les tokens et info utilisateur
        return JsonResponse({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'user_type': getattr(user, 'user_type', 'teacher'),  # Type utilisateur si disponible
                'is_active': user.is_active,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'date_joined': user.date_joined.isoformat()
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'JSON invalide'}, status=400)
    except Exception as e:
        return JsonResponse({'detail': 'Erreur serveur'}, status=500)

@csrf_exempt  
def current_user_api(request):
    """Endpoint pour récupérer l'utilisateur actuel"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    # Vérifier l'authentification via le token JWT
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return JsonResponse({'detail': 'Token manquant'}, status=401)
    
    token = auth_header.split(' ')[1]
    
    try:
        from rest_framework_simplejwt.tokens import UntypedToken
        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
        from django.contrib.auth import get_user_model
        
        # Valider le token
        UntypedToken(token)
        
        # Décoder le token pour récupérer l'utilisateur
        import jwt
        from django.conf import settings
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decoded_token.get('user_id')
        
        # Récupérer l'utilisateur
        User = get_user_model()
        user = User.objects.get(id=user_id)
        
        return JsonResponse({
            'id': str(user.id),
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'user_type': user.user_type,
            'is_active': user.is_active,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'date_joined': user.date_joined.isoformat()
        })
        
    except (InvalidToken, TokenError, jwt.DecodeError, User.DoesNotExist):
        return JsonResponse({'detail': 'Token invalide'}, status=401)
    except Exception as e:
        return JsonResponse({'detail': 'Erreur serveur'}, status=500)