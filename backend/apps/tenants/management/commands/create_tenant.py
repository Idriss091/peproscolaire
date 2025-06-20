"""
Commande Django pour créer un nouveau tenant
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.tenants.models import Tenant, TenantSettings
from apps.schools.models import School
from apps.tenants.utils import provision_tenant
import re


class Command(BaseCommand):
    help = 'Crée un nouveau tenant avec son schéma PostgreSQL'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            type=str,
            required=True,
            help='Nom de l\'établissement'
        )
        
        parser.add_argument(
            '--subdomain',
            type=str,
            required=True,
            help='Sous-domaine (ex: lycee-morvan)'
        )
        
        parser.add_argument(
            '--type',
            type=str,
            choices=['college', 'lycee', 'lycee_pro'],
            default='lycee',
            help='Type d\'établissement'
        )
        
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='Email de contact de l\'établissement'
        )
        
        parser.add_argument(
            '--phone',
            type=str,
            required=True,
            help='Téléphone de l\'établissement'
        )
        
        parser.add_argument(
            '--address',
            type=str,
            required=True,
            help='Adresse de l\'établissement'
        )
        
        parser.add_argument(
            '--postal-code',
            type=str,
            required=True,
            help='Code postal'
        )
        
        parser.add_argument(
            '--city',
            type=str,
            required=True,
            help='Ville'
        )
        
        parser.add_argument(
            '--max-students',
            type=int,
            default=1000,
            help='Nombre maximum d\'élèves'
        )
        
        parser.add_argument(
            '--primary-color',
            type=str,
            default='#1976D2',
            help='Couleur principale (format hex)'
        )
        
        parser.add_argument(
            '--secondary-color',
            type=str,
            default='#424242',
            help='Couleur secondaire (format hex)'
        )
        
        parser.add_argument(
            '--provision',
            action='store_true',
            help='Provisionner immédiatement le tenant'
        )
    
    def handle(self, *args, **options):
        # Validation du sous-domaine
        subdomain = options['subdomain'].lower()
        if not re.match(r'^[a-z0-9-]+$', subdomain):
            raise CommandError('Le sous-domaine ne doit contenir que des lettres minuscules, chiffres et tirets')
        
        # Générer le nom du schéma à partir du sous-domaine
        schema_name = subdomain.replace('-', '_')
        
        # Construire l'URL complète
        domain_url = f"{subdomain}.peproscolaire.fr"
        
        try:
            with transaction.atomic():
                # Vérifier que le sous-domaine n'existe pas déjà
                if Tenant.objects.filter(domain_url=domain_url).exists():
                    raise CommandError(f'Le domaine {domain_url} existe déjà')
                
                # Créer l'établissement
                school = School.objects.create(
                    name=options['name'],
                    school_type=options['type'],
                    email=options['email'],
                    phone=options['phone'],
                    address=options['address'],
                    postal_code=options['postal_code'],
                    city=options['city'],
                    subdomain=subdomain
                )
                
                self.stdout.write(f"École créée: {school.name}")
                
                # Créer le tenant
                tenant = Tenant.objects.create(
                    schema_name=schema_name,
                    domain_url=domain_url,
                    school=school,
                    max_students=options['max_students'],
                    primary_color=options['primary_color'],
                    secondary_color=options['secondary_color']
                )
                
                self.stdout.write(f"Tenant créé: {tenant.domain_url}")
                
                # Provisionner si demandé
                if options['provision']:
                    self.stdout.write("Provisionnement du tenant...")
                    provision_tenant(tenant)
                    self.stdout.write(self.style.SUCCESS(f"Tenant {domain_url} provisionné avec succès!"))
                else:
                    self.stdout.write(self.style.WARNING(
                        f"Tenant créé mais non provisionné. "
                        f"Utilisez 'python manage.py provision_tenant {schema_name}' pour le provisionner."
                    ))
                
                # Afficher les informations de connexion
                self.stdout.write("\n" + "="*50)
                self.stdout.write(self.style.SUCCESS("TENANT CRÉÉ AVEC SUCCÈS"))
                self.stdout.write("="*50)
                self.stdout.write(f"URL: https://{domain_url}")
                self.stdout.write(f"Schéma: {schema_name}")
                self.stdout.write(f"École: {school.name}")
                self.stdout.write(f"Type: {school.get_school_type_display()}")
                self.stdout.write(f"Max élèves: {tenant.max_students}")
                self.stdout.write("="*50 + "\n")
                
        except Exception as e:
            raise CommandError(f'Erreur lors de la création du tenant: {str(e)}')