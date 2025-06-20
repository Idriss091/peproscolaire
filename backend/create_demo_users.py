#!/usr/bin/env python
"""
Script pour créer des utilisateurs de démonstration
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_minimal')
django.setup()

from django.contrib.auth.models import User

def create_demo_users():
    """Créer des utilisateurs de démonstration"""
    
    users = [
        {
            'username': 'demo',
            'email': 'demo@example.com',
            'password': 'demo123',
            'first_name': 'Jean',
            'last_name': 'Professeur',
            'is_staff': False
        },
        {
            'username': 'teacher',
            'email': 'teacher@example.com', 
            'password': 'demo123',
            'first_name': 'Marie',
            'last_name': 'Enseignant',
            'is_staff': False
        },
        {
            'username': 'student',
            'email': 'student@example.com',
            'password': 'demo123', 
            'first_name': 'Paul',
            'last_name': 'Élève',
            'is_staff': False
        }
    ]
    
    for user_data in users:
        username = user_data['username']
        
        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(username=username).exists():
            print(f"✓ Utilisateur '{username}' existe déjà")
            continue
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )
        user.is_staff = user_data['is_staff']
        user.save()
        
        print(f"✓ Utilisateur '{username}' créé")
    
    print(f"\n🎉 Utilisateurs de démonstration créés avec succès!")
    print(f"Connectez-vous avec:")
    print(f"  • demo / demo123")
    print(f"  • teacher / demo123") 
    print(f"  • student / demo123")
    print(f"  • admin / demo123 (superuser)")

if __name__ == "__main__":
    create_demo_users()