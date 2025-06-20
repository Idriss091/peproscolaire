"""
Commande Django pour migrer tous les tenants
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from apps.tenants.models import Tenant
from apps.tenants.utils import set_schema, get_current_schema
import time


class Command(BaseCommand):
    help = 'Applique les migrations Django à tous les tenants actifs'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            type=str,
            help='Migrer uniquement un schéma spécifique'
        )
        
        parser.add_argument(
            '--app',
            type=str,
            help='Migrer uniquement une application spécifique'
        )
        
        parser.add_argument(
            '--fake',
            action='store_true',
            help='Marquer les migrations comme appliquées sans les exécuter'
        )
        
        parser.add_argument(
            '--plan',
            action='store_true',
            help='Afficher le plan de migration sans l\'exécuter'
        )
        
        parser.add_argument(
            '--skip-public',
            action='store_true',
            help='Ne pas migrer le schéma public'
        )
    
    def handle(self, *args, **options):
        # Sauvegarder le schéma actuel
        original_schema = get_current_schema()
        
        try:
            # Si un schéma spécifique est demandé
            if options['schema']:
                self._migrate_schema(options['schema'], options)
                return
            
            # Migrer le schéma public d'abord (sauf si skip-public)
            if not options['skip_public']:
                self.stdout.write("Migration du schéma public...")
                set_schema('public')
                self._run_migration('public', options)
            
            # Récupérer tous les tenants actifs
            tenants = Tenant.objects.filter(is_active=True)
            total_tenants = tenants.count()
            
            if total_tenants == 0:
                self.stdout.write(self.style.WARNING("Aucun tenant actif trouvé."))
                return
            
            self.stdout.write(f"\nMigration de {total_tenants} tenant(s)...")
            
            # Migrer chaque tenant
            for i, tenant in enumerate(tenants, 1):
                self.stdout.write(f"\n[{i}/{total_tenants}] Migration de {tenant.schema_name} ({tenant.school.name})...")
                
                try:
                    start_time = time.time()
                    self._migrate_schema(tenant.schema_name, options)
                    elapsed_time = time.time() - start_time
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ {tenant.schema_name} migré avec succès en {elapsed_time:.2f}s"
                        )
                    )
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"✗ Erreur lors de la migration de {tenant.schema_name}: {str(e)}"
                        )
                    )
                    # Continuer avec les autres tenants
                    continue
            
            self.stdout.write(self.style.SUCCESS("\n✓ Migration terminée pour tous les tenants!"))
            
        finally:
            # Restaurer le schéma original
            set_schema(original_schema)
    
    def _migrate_schema(self, schema_name, options):
        """
        Migre un schéma spécifique
        """
        # Changer vers le schéma cible
        set_schema(schema_name)
        
        # Exécuter la migration
        self._run_migration(schema_name, options)
    
    def _run_migration(self, schema_name, options):
        """
        Exécute la commande migrate avec les options appropriées
        """
        migrate_kwargs = {
            'verbosity': 1,
            'interactive': False,
        }
        
        if options['app']:
            migrate_kwargs['app_label'] = options['app']
        
        if options['fake']:
            migrate_kwargs['fake'] = True
        
        if options['plan']:
            migrate_kwargs['plan'] = True
        
        # Afficher les migrations en attente si --plan
        if options['plan']:
            self.stdout.write(f"\nPlan de migration pour {schema_name}:")
        
        # Exécuter la migration
        call_command('migrate', **migrate_kwargs)