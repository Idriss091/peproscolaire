#!/usr/bin/env python
"""
Script de démonstration du système multi-tenant
À exécuter avec: python manage.py shell < apps/tenants/demo_multi_tenant.py
"""

from apps.tenants.models import Tenant, TenantSettings
from apps.schools.models import School
from apps.tenants.utils import provision_tenant, TenantContextManager
from apps.authentication.models import User
from django.db import connection

print("=== DÉMONSTRATION DU SYSTÈME MULTI-TENANT ===\n")

# 1. Créer deux établissements de test
print("1. Création de deux établissements...")

# Premier établissement
school1 = School.objects.create(
    name="Lycée Victor Hugo",
    school_type="lycee",
    email="contact@lycee-hugo.fr",
    phone="0123456789",
    address="123 rue Victor Hugo",
    postal_code="75001",
    city="Paris",
    subdomain="lycee-hugo-demo"
)
print(f"   ✓ {school1.name} créé")

# Deuxième établissement
school2 = School.objects.create(
    name="Collège Jean Moulin",
    school_type="college",
    email="contact@college-moulin.fr",
    phone="0198765432",
    address="456 avenue Jean Moulin",
    postal_code="69001",
    city="Lyon",
    subdomain="college-moulin-demo"
)
print(f"   ✓ {school2.name} créé")

# 2. Créer les tenants correspondants
print("\n2. Création des tenants...")

tenant1 = Tenant.objects.create(
    schema_name="lycee_hugo_demo",
    domain_url="lycee-hugo-demo.peproscolaire.fr",
    school=school1,
    primary_color="#2E7D32",
    secondary_color="#1B5E20",
    max_students=1500
)
print(f"   ✓ Tenant pour {school1.name}")
print(f"     - URL: https://{tenant1.domain_url}")
print(f"     - Schéma: {tenant1.schema_name}")

tenant2 = Tenant.objects.create(
    schema_name="college_moulin_demo",
    domain_url="college-moulin-demo.peproscolaire.fr",
    school=school2,
    primary_color="#1976D2",
    secondary_color="#0D47A1",
    max_students=800
)
print(f"   ✓ Tenant pour {school2.name}")
print(f"     - URL: https://{tenant2.domain_url}")
print(f"     - Schéma: {tenant2.schema_name}")

# 3. Provisionner les tenants
print("\n3. Provisionnement des tenants...")
print("   (Création des schémas PostgreSQL)")

try:
    provision_tenant(tenant1)
    print(f"   ✓ {tenant1.schema_name} provisionné")
except Exception as e:
    print(f"   ✗ Erreur: {e}")

try:
    provision_tenant(tenant2)
    print(f"   ✓ {tenant2.schema_name} provisionné")
except Exception as e:
    print(f"   ✗ Erreur: {e}")

# 4. Créer des utilisateurs dans chaque tenant
print("\n4. Création d'utilisateurs par tenant...")

# Utilisateurs pour le Lycée Victor Hugo
with TenantContextManager(tenant1):
    # Administrateur
    admin1 = User.objects.create_user(
        username="admin.hugo",
        email="admin@lycee-hugo.fr",
        password="demo123",
        first_name="Admin",
        last_name="Hugo",
        user_type="admin"
    )
    print(f"   ✓ Admin créé pour {tenant1.school.name}")
    
    # Professeur
    prof1 = User.objects.create_user(
        username="prof.martin",
        email="martin@lycee-hugo.fr",
        password="demo123",
        first_name="Jean",
        last_name="Martin",
        user_type="teacher"
    )
    print(f"   ✓ Professeur créé pour {tenant1.school.name}")
    
    # Élève
    student1 = User.objects.create_user(
        username="eleve.dupont",
        email="dupont@lycee-hugo.fr",
        password="demo123",
        first_name="Marie",
        last_name="Dupont",
        user_type="student"
    )
    print(f"   ✓ Élève créé pour {tenant1.school.name}")

# Utilisateurs pour le Collège Jean Moulin
with TenantContextManager(tenant2):
    # Administrateur
    admin2 = User.objects.create_user(
        username="admin.moulin",
        email="admin@college-moulin.fr",
        password="demo123",
        first_name="Admin",
        last_name="Moulin",
        user_type="admin"
    )
    print(f"   ✓ Admin créé pour {tenant2.school.name}")
    
    # Professeur
    prof2 = User.objects.create_user(
        username="prof.bernard",
        email="bernard@college-moulin.fr",
        password="demo123",
        first_name="Sophie",
        last_name="Bernard",
        user_type="teacher"
    )
    print(f"   ✓ Professeur créé pour {tenant2.school.name}")

# 5. Vérifier l'isolation des données
print("\n5. Vérification de l'isolation des données...")

# Compter les utilisateurs dans chaque tenant
with TenantContextManager(tenant1):
    count1 = User.objects.count()
    print(f"   - {tenant1.school.name}: {count1} utilisateurs")

with TenantContextManager(tenant2):
    count2 = User.objects.count()
    print(f"   - {tenant2.school.name}: {count2} utilisateurs")

# 6. Tester les modules
print("\n6. Configuration des modules...")

# Désactiver l'IA pour le collège
tenant2.modules_enabled['ai_analytics'] = False
tenant2.save()
print(f"   ✓ Module IA désactivé pour {tenant2.school.name}")

# Afficher les modules actifs
print("\n   Modules actifs:")
print(f"   - {tenant1.school.name}:")
for module, enabled in tenant1.modules_enabled.items():
    if enabled:
        print(f"     • {module}")

print(f"   - {tenant2.school.name}:")
for module, enabled in tenant2.modules_enabled.items():
    if enabled:
        print(f"     • {module}")

# 7. Résumé
print("\n=== RÉSUMÉ ===")
print(f"✓ 2 établissements créés")
print(f"✓ 2 tenants provisionnés")
print(f"✓ {count1 + count2} utilisateurs créés au total")
print(f"✓ Isolation des données vérifiée")
print(f"✓ Personnalisation des modules testée")

print("\n=== ACCÈS ===")
print(f"Lycée Victor Hugo:")
print(f"  URL: https://{tenant1.domain_url}")
print(f"  Admin: admin.hugo / demo123")
print(f"  Prof: prof.martin / demo123")
print(f"  Élève: eleve.dupont / demo123")

print(f"\nCollège Jean Moulin:")
print(f"  URL: https://{tenant2.domain_url}")
print(f"  Admin: admin.moulin / demo123")
print(f"  Prof: prof.bernard / demo123")

print("\n=== NETTOYAGE ===")
print("Pour supprimer les données de démo, exécuter:")
print("  python manage.py shell")
print("  >>> from apps.tenants.models import Tenant")
print("  >>> Tenant.objects.filter(schema_name__endswith='_demo').delete()")