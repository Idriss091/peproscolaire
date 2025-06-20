# ⚡ Démarrage Rapide - PeproScolaire

Lancez PeproScolaire en 5 minutes avec Docker ! 🚀

## 🎯 Prérequis minimum
- **Docker** + **Docker Compose** installés
- **4 GB RAM** disponibles  
- **5 GB** d'espace disque

## 🚀 Lancement express

### 1. Récupérer le projet
```bash
git clone https://github.com/your-username/peproscolaire.git
cd peproscolaire
```

### 2. Lancer l'application
```bash
# Démarrer tous les services en une commande
docker-compose up -d

# Attendre que tous les services soient prêts (2-3 minutes)
docker-compose logs -f
```

### 3. Initialiser les données
```bash
# Créer la base de données et charger les données de démo
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py loaddata demo_data.json
docker-compose exec backend python manage.py train_ai_models
```

## 🎮 Accès à l'application

**L'application est prête !** Rendez-vous sur : **http://localhost:3000**

### 👤 Comptes de test inclus

| Rôle | Identifiant | Mot de passe |
|------|-------------|--------------|
| **Admin** | `admin@college-demo.fr` | `demo123` |
| **Professeur** | `prof.martin@college-demo.fr` | `demo123` |
| **Élève** | `eleve.dupont@college-demo.fr` | `demo123` |
| **Parent** | `parent.dupont@college-demo.fr` | `demo123` |

## 🤖 Tester les modules IA en 2 minutes

### 1. **Détection de décrochage** (Compte Professeur)
```
Navigation : Menu IA → Détection de risque
→ Voir le dashboard ML avec métriques temps réel
→ Analyser les élèves à risque avec scoring IA
```

### 2. **Générateur d'appréciations** (Compte Professeur) 
```
Navigation : Menu IA → Appréciations IA
→ Sélectionner la classe "3ème A"
→ Générer des appréciations automatiques
→ Prévisualiser et valider les résultats
```

### 3. **Chatbot pédagogique** (Tous comptes)
```
Interface : Widget chat en bas à droite
→ Cliquer sur l'icône de conversation
→ Tester les suggestions contextuelles
→ Poser des questions sur les notes/devoirs
```

### 4. **Gestion des stages** (Compte Élève)
```
Navigation : Menu → Stages  
→ Explorer le dashboard avec statistiques
→ Rechercher des offres avec filtres IA
→ Simuler une candidature
```

## 🎨 Découvrir l'interface moderne

- **🎨 Design system** : Thème éducatif avec couleurs et animations modernes
- **📱 Responsive** : Testé mobile, tablette et desktop  
- **⌨️ Raccourcis** : `Ctrl/Cmd + K` pour recherche globale
- **🔔 Notifications** : Centre complet avec filtres
- **⚡ Actions rapides** : Bouton `+` pour accès rapide
- **🌙 Thème sombre** : Basculer dans le menu utilisateur

## 📊 Données de démonstration

**Incluses dans la démo :**
- **150+ élèves** sur 12 classes (6ème à Terminale)
- **25 professeurs** avec spécialités
- **500+ notes** avec moyennes calculées
- **200+ absences** avec justificatifs
- **Historique IA** : Données pour modèles ML entraînés

## 🔧 Commandes utiles

```bash
# Voir les logs en temps réel
docker-compose logs -f

# Redémarrer un service spécifique
docker-compose restart backend

# Arrêter l'application
docker-compose down

# Réinitialiser les données
docker-compose exec backend python manage.py flush
docker-compose exec backend python manage.py loaddata demo_data.json
```

## 🆘 Résolution de problèmes

### ❌ Port déjà utilisé
```bash
# Modifier les ports dans docker-compose.yml
ports:
  - "3001:3000"  # Au lieu de 3000:3000
```

### ❌ Services ne démarrent pas
```bash
# Reconstruire les images
docker-compose down
docker-compose up --build
```

### ❌ Base de données vide
```bash
# Recharger les données de démonstration
docker-compose exec backend python manage.py loaddata demo_data.json
```

## 🚀 Prêt pour la production ?

1. **Configurer les variables d'environnement** (clés API, domaines)
2. **Utiliser une base PostgreSQL externe** 
3. **Configurer SSL/TLS** avec certificats
4. **Ajuster les ressources** selon la charge attendue

→ Consultez le [Guide de déploiement](DEPLOYMENT.md) pour les détails

## 🎯 Prochaines étapes

Une fois PeproScolaire lancé :

1. **Explorer les 4 rôles utilisateur** avec les comptes de test
2. **Tester tous les modules IA** avec les données de démo
3. **Configurer votre établissement** via l'interface admin
4. **Importer vos vraies données** ou créer vos utilisateurs
5. **Personnaliser les paramètres IA** selon vos besoins

**Félicitations ! 🎉 PeproScolaire est opérationnel avec tous ses modules IA.**

Pour toute question : consultez la [documentation complète](README.md) ou les [guides détaillés](GUIDE_INSTALLATION.md).

---

*PeproScolaire - L'école intelligente du futur, disponible aujourd'hui* ✨