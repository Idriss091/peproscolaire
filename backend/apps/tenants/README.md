# Module Multi-Tenant pour PeproScolaire

Ce module implémente un système multi-tenant complet pour PeproScolaire, permettant à chaque établissement d'avoir son propre espace isolé avec personnalisation de l'interface.

## Architecture

### Isolation des données
- **Approche** : Schémas PostgreSQL séparés
- **Avantages** : Isolation forte, sécurité maximale, performances optimales
- **Structure** : Un schéma par établissement + schéma `public` pour les données partagées

### Personnalisation
- Logo de l'établissement
- Couleurs principales (primary/secondary)
- Nom et favicon personnalisés
- Modules activables/désactivables

## Installation

1. Ajouter l'application dans `INSTALLED_APPS` (déjà fait) :
```python
INSTALLED_APPS = [
    'apps.tenants',  # Doit être en premier
    # ... autres apps
]
```

2. Ajouter les middlewares (déjà fait) :
```python
MIDDLEWARE = [
    # ...
    'apps.tenants.middleware.TenantMiddleware',
    'apps.tenants.middleware.TenantSecurityMiddleware',
    # ...
]
```

3. Configurer le router de base de données (déjà fait) :
```python
DATABASE_ROUTERS = [
    'apps.tenants.db_router.TenantDatabaseRouter',
]
```

4. Migrer la base de données :
```bash
python manage.py migrate
```

## Utilisation

### Créer un nouveau tenant

#### Via la commande Django :
```bash
python manage.py create_tenant \
    --name "Lycée Victor Hugo" \
    --subdomain "lycee-hugo" \
    --type lycee \
    --email "contact@lycee-hugo.fr" \
    --phone "0123456789" \
    --address "123 rue Victor Hugo" \
    --postal-code "75001" \
    --city "Paris" \
    --max-students 1500 \
    --primary-color "#2E7D32" \
    --secondary-color "#1B5E20" \
    --provision
```

#### Via l'API (super-admin uniquement) :
```bash
POST /api/v1/tenants/
{
    "school_name": "Lycée Victor Hugo",
    "school_type": "lycee",
    "subdomain": "lycee-hugo",
    "email": "contact@lycee-hugo.fr",
    "phone": "0123456789",
    "address": "123 rue Victor Hugo",
    "postal_code": "75001",
    "city": "Paris",
    "primary_color": "#2E7D32",
    "secondary_color": "#1B5E20",
    "max_students": 1500,
    "provision_now": true
}
```

### Lister les tenants
```bash
python manage.py list_tenants --detailed
```

### Migrer tous les tenants
```bash
python manage.py migrate_tenants
```

### Migrer un tenant spécifique
```bash
python manage.py migrate_tenants --schema lycee_hugo
```

## API Endpoints

### Gestion des tenants (super-admin)
- `GET /api/v1/tenants/` - Liste tous les tenants
- `POST /api/v1/tenants/` - Crée un nouveau tenant
- `GET /api/v1/tenants/{id}/` - Détails d'un tenant
- `PATCH /api/v1/tenants/{id}/` - Met à jour un tenant
- `DELETE /api/v1/tenants/{id}/` - Supprime un tenant

### Actions sur les tenants
- `POST /api/v1/tenants/{id}/provision/` - Provisionne un tenant
- `POST /api/v1/tenants/{id}/activate/` - Active un tenant
- `POST /api/v1/tenants/{id}/deactivate/` - Désactive un tenant
- `GET /api/v1/tenants/{id}/stats/` - Statistiques du tenant
- `POST /api/v1/tenants/{id}/update_modules/` - Active/désactive des modules
- `POST /api/v1/tenants/{id}/add_domain/` - Ajoute un domaine alternatif

### Tenant actuel (tous les utilisateurs authentifiés)
- `GET /api/v1/current-tenant/info/` - Informations du tenant actuel
- `GET /api/v1/current-tenant/theme/` - Thème du tenant actuel
- `GET /api/v1/current-tenant/modules/` - Modules activés

## Configuration DNS

Pour que le système fonctionne, vous devez configurer :

1. **DNS Wildcard** : `*.peproscolaire.fr` → IP du serveur
2. **Certificat SSL Wildcard** : Pour HTTPS sur tous les sous-domaines

## Permissions

### IsSuperAdmin
Accès complet à la gestion des tenants

### IsTenantAdmin
Administration du tenant actuel uniquement

### IsTenantMember
Membre du tenant actuel

### CanAccessModule
Vérifie que le module est activé pour le tenant

## Personnalisation de l'interface

Les variables suivantes sont disponibles dans tous les templates :

```django
{{ theme.primary_color }}      # Couleur principale
{{ theme.secondary_color }}    # Couleur secondaire
{{ theme.logo_url }}          # URL du logo
{{ theme.favicon_url }}       # URL du favicon
{{ theme.school_name }}       # Nom de l'établissement
{{ modules_enabled }}         # Dict des modules activés
{{ tenant_features }}         # Fonctionnalités disponibles
```

### Exemple d'utilisation dans un template :
```html
{% extends "base_tenant.html" %}

{% block content %}
<div class="welcome-message">
    <h1>Bienvenue à {{ theme.school_name }}</h1>
    
    {% if modules_enabled.ai_analytics %}
    <div class="ai-feature">
        <!-- Fonctionnalité IA disponible -->
    </div>
    {% endif %}
</div>
{% endblock %}
```

## Stockage des fichiers

Les fichiers sont automatiquement isolés par tenant :
```
mediafiles/
├── tenant_1/
│   ├── avatars/
│   ├── documents/
│   └── school_assets/
├── tenant_2/
│   └── ...
└── shared/
    └── system/
```

## Monitoring et quotas

### Vérifier l'utilisation d'un tenant :
```python
from apps.tenants.storage import tenant_storage

# Espace utilisé en GB
usage_gb = tenant_storage.get_tenant_usage_gb()

# Vérifier si un fichier peut être uploadé
can_upload = tenant_storage.check_tenant_quota(file_size_bytes)
```

### Limites par défaut :
- Élèves : 1000 (configurable)
- Stockage : 50 GB (configurable)
- Modules : Tous sauf IA (configurable)

## Sécurité

1. **Isolation stricte** : Impossible d'accéder aux données d'un autre tenant
2. **Validation des domaines** : Seuls les domaines enregistrés sont acceptés
3. **Audit trail** : Toutes les actions sont loggées
4. **Backup séparé** : Chaque schéma peut être sauvegardé indépendamment

## Troubleshooting

### Erreur "Tenant non trouvé"
- Vérifier que le domaine est correctement configuré
- Vérifier que le tenant est actif
- Vérifier le cache (peut être vidé avec `cache.clear()`)

### Erreur de migration
- S'assurer que le schéma existe : `python manage.py migrate_tenants --schema nom_schema`
- Vérifier les logs pour plus de détails

### Performance
- Utiliser le cache Redis pour les requêtes fréquentes
- Monitorer l'utilisation des schémas avec `pg_stat_user_tables`

## Développement

### Ajouter un nouveau modèle tenant-aware :
```python
from apps.tenants.models import TenantAwareModel

class MonModele(TenantAwareModel):
    # Vos champs ici
    pass
```

### Exécuter du code dans le contexte d'un tenant :
```python
from apps.tenants.utils import TenantContextManager

with TenantContextManager(tenant):
    # Code exécuté dans le contexte du tenant
    users = User.objects.all()  # Ne retourne que les users du tenant
```

### Ajouter une permission de module :
```python
from apps.tenants.permissions import CanAccessModule

class CanAccessMyModule(CanAccessModule):
    module_name = 'my_module'
```

## Support

Pour toute question ou problème, consulter :
- La documentation complète : `/docs/multi-tenant/`
- Les logs : `backend/logs/tenant.log`
- L'équipe technique : tech@peproscolaire.fr