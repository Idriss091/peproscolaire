"""
Commande Django pour lister tous les tenants
"""
from django.core.management.base import BaseCommand
from django.db.models import Count
from apps.tenants.models import Tenant
from apps.authentication.models import User
from apps.tenants.utils import execute_on_tenant
from tabulate import tabulate
import humanize


class Command(BaseCommand):
    help = 'Liste tous les tenants avec leurs informations'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--active-only',
            action='store_true',
            help='Afficher uniquement les tenants actifs'
        )
        
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Afficher des informations détaillées'
        )
        
        parser.add_argument(
            '--format',
            type=str,
            choices=['table', 'csv', 'json'],
            default='table',
            help='Format de sortie'
        )
    
    def handle(self, *args, **options):
        # Récupérer les tenants
        queryset = Tenant.objects.select_related('school')
        
        if options['active_only']:
            queryset = queryset.filter(is_active=True)
        
        tenants = queryset.order_by('created_on')
        
        if not tenants.exists():
            self.stdout.write(self.style.WARNING("Aucun tenant trouvé."))
            return
        
        # Préparer les données
        if options['detailed']:
            data = self._get_detailed_data(tenants)
        else:
            data = self._get_basic_data(tenants)
        
        # Afficher selon le format demandé
        if options['format'] == 'table':
            self._display_table(data, options['detailed'])
        elif options['format'] == 'csv':
            self._display_csv(data)
        elif options['format'] == 'json':
            self._display_json(data)
    
    def _get_basic_data(self, tenants):
        """
        Récupère les données de base des tenants
        """
        data = []
        for tenant in tenants:
            data.append({
                'ID': tenant.id,
                'École': tenant.school.name,
                'Type': tenant.school.get_school_type_display(),
                'Domaine': tenant.domain_url,
                'Schéma': tenant.schema_name,
                'Actif': '✓' if tenant.is_active else '✗',
                'Créé le': tenant.created_on.strftime('%d/%m/%Y'),
            })
        return data
    
    def _get_detailed_data(self, tenants):
        """
        Récupère les données détaillées des tenants
        """
        data = []
        for tenant in tenants:
            # Compter les utilisateurs dans ce tenant
            try:
                user_counts = execute_on_tenant(tenant, self._count_users)
            except:
                user_counts = {'total': 0, 'students': 0, 'teachers': 0, 'parents': 0}
            
            # Calculer l'espace utilisé
            from apps.tenants.storage import tenant_storage
            try:
                storage_gb = tenant_storage.get_tenant_usage_gb()
            except:
                storage_gb = 0
            
            data.append({
                'ID': tenant.id,
                'École': tenant.school.name,
                'Type': tenant.school.get_school_type_display(),
                'Domaine': tenant.domain_url,
                'Schéma': tenant.schema_name,
                'Actif': '✓' if tenant.is_active else '✗',
                'Élèves': f"{user_counts['students']}/{tenant.max_students}",
                'Profs': user_counts['teachers'],
                'Parents': user_counts['parents'],
                'Stockage': f"{storage_gb:.2f}/{tenant.max_storage_gb} GB",
                'Modules': self._format_modules(tenant.modules_enabled),
                'Créé le': tenant.created_on.strftime('%d/%m/%Y'),
                'Provisionné': '✓' if tenant.provisioned_at else '✗',
            })
        return data
    
    def _count_users(self):
        """
        Compte les utilisateurs par type
        """
        counts = User.objects.values('user_type').annotate(count=Count('id'))
        result = {
            'total': User.objects.count(),
            'students': 0,
            'teachers': 0,
            'parents': 0,
        }
        
        for item in counts:
            if item['user_type'] == 'student':
                result['students'] = item['count']
            elif item['user_type'] == 'teacher':
                result['teachers'] = item['count']
            elif item['user_type'] == 'parent':
                result['parents'] = item['count']
        
        return result
    
    def _format_modules(self, modules):
        """
        Formate la liste des modules activés
        """
        if not modules:
            return "Aucun"
        
        active_modules = [k for k, v in modules.items() if v]
        return f"{len(active_modules)} actifs"
    
    def _display_table(self, data, detailed):
        """
        Affiche les données sous forme de tableau
        """
        if not data:
            return
        
        # En-têtes du tableau
        headers = list(data[0].keys())
        
        # Données du tableau
        rows = [list(item.values()) for item in data]
        
        # Afficher le tableau
        self.stdout.write("\n" + tabulate(rows, headers=headers, tablefmt='grid'))
        
        # Résumé
        total = len(data)
        active = sum(1 for item in data if item['Actif'] == '✓')
        
        self.stdout.write(f"\nTotal: {total} tenant(s) | Actifs: {active} | Inactifs: {total - active}")
    
    def _display_csv(self, data):
        """
        Affiche les données au format CSV
        """
        import csv
        import sys
        
        if not data:
            return
        
        writer = csv.DictWriter(sys.stdout, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    
    def _display_json(self, data):
        """
        Affiche les données au format JSON
        """
        import json
        
        # Convertir les dates en chaînes
        for item in data:
            for key, value in item.items():
                if hasattr(value, 'strftime'):
                    item[key] = value.isoformat()
        
        self.stdout.write(json.dumps(data, indent=2, ensure_ascii=False))