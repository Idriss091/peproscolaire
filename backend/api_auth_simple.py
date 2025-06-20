"""
API d'authentification simple pour tester la connexion frontend
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
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
        
        # Authentifier l'utilisateur
        user = authenticate(username=username, password=password)
        
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
                'user_type': 'teacher',  # Type par défaut pour les tests
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
    
    # Pour les tests, retourner un utilisateur par défaut
    return JsonResponse({
        'id': 1,
        'username': 'demo',
        'first_name': 'Jean',
        'last_name': 'Professeur',
        'email': 'demo@example.com',
        'user_type': 'teacher',
        'is_active': True,
        'last_login': '2024-01-15T10:00:00Z',
        'date_joined': '2024-01-01T10:00:00Z'
    })