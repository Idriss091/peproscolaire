"""
Commande Django pour attendre que la base de données soit prête
"""
import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Commande pour attendre la disponibilité de la base de données"""
    
    def handle(self, *args, **options):
        self.stdout.write('En attente de la base de données...')
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
                db_conn.cursor()
            except OperationalError:
                self.stdout.write('Base de données non disponible, attente de 1 seconde...')
                time.sleep(1)
        
        self.stdout.write(self.style.SUCCESS('Base de données disponible!'))