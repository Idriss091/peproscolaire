# 🚀 Guide de Démarrage Rapide - PeproScolaire Frontend

## ✅ État du Projet

### Ce qui fonctionne déjà :
- ✅ **Configuration Vue.js 3 + TypeScript + Vite**
- ✅ **Système d'authentification complet** (login, logout, guards de route)
- ✅ **Layout principal responsive** avec navigation par rôle
- ✅ **Composants UI de base** (boutons, cards, modals, etc.)
- ✅ **Dashboard basique** avec statistiques par type d'utilisateur
- ✅ **Router configuré** avec protection des routes
- ✅ **Support multi-tenant** via sous-domaines
- ✅ **Stores Pinia** pour la gestion d'état
- ✅ **API client** avec gestion automatique des tokens

## 🛠️ Installation et Configuration

### 1. Prérequis
```bash
# Node.js 18+ et npm
node --version
npm --version
```

### 2. Installation des dépendances
```bash
cd frontend/peproscolaire-ui
npm install
```

### 3. Démarrage du serveur de développement
```bash
# Option 1: Depuis le dossier frontend
npm run dev

# Option 2: Script global depuis la racine
./scripts/start-frontend.sh
```

L'application sera accessible sur : **http://localhost:5173**

## 🎪 Fonctionnalités à tester

### **1. Authentification (Mock)**
- **URL** : http://localhost:5173/login
- **Comptes de test** :
  ```
  Email: admin@example.com    | Mot de passe: password
  Email: teacher@example.com  | Mot de passe: password  
  Email: student@example.com  | Mot de passe: password
  ```
- **Tests** :
  - Connexion avec différents rôles
  - Validation des champs de formulaire
  - Messages d'erreur
  - Redirection automatique

### **2. Dashboard Principal**
- **URL** : http://localhost:5173/dashboard
- **Fonctionnalités** :
  - 📊 Statistiques en temps réel
  - 📈 Graphiques de distribution des risques
  - 🚨 Alertes récentes
  - 👥 Élèves à risque élevé
  - 🔄 Statut de connexion temps réel

### **3. Profils de Risque**
- **URL** : http://localhost:5173/risk-detection/profiles
- **Tests disponibles** :
  - Filtrage par niveau de risque
  - Recherche d'élèves
  - Vue détaillée des profils
  - Activation de la surveillance
  - Analyse manuelle des risques

### **4. Gestion des Alertes**
- **URL** : http://localhost:5173/risk-detection/alerts
- **Fonctionnalités** :
  - Liste des alertes avec filtres
  - Priorités visuelles (urgent, élevé, normal)
  - Traitement des alertes avec formulaire détaillé
  - Configuration des alertes automatiques (admin)
  - Notifications en temps réel

### **5. Plans d'Intervention**
- **URL** : http://localhost:5173/risk-detection/interventions
- **Tests** :
  - Création de nouveaux plans
  - Gestion des objectifs et actions
  - Suivi de progression
  - Attribution de participants
  - Changement de statut des plans

### **6. Notifications Temps Réel**
- **Cloche de notification** (coin supérieur droit)
- **Tests** :
  - Panel de notifications
  - Marquer comme lu
  - Navigation vers les détails
  - Statut de connexion WebSocket

### **7. Paramètres et Testing**
- **URL** : http://localhost:5173/settings
- **Testeur WebSocket** (admin uniquement) :
  - Simulation d'événements en temps réel
  - Test de notifications
  - Test d'alertes urgentes
  - Messages personnalisés

## 🧪 Tests Automatisés

### Lancer les tests unitaires
```bash
npm run test:run        # Tests une fois
npm run test:coverage   # Tests avec couverture
npm run test:ui        # Interface de test Vitest
```

### Couverture actuelle
- **Composants UI** : BaseButton, BaseInput, BaseCard, etc.
- **Stores** : Auth, Notifications, Risk Detection
- **Services** : WebSocket, API Client
- **Intégration** : Dashboard, Navigation

## 📱 Interface Utilisateur

### **Design System**
- **Couleurs** : Palette cohérente avec thème scolaire
- **Composants** : Library complète de composants réutilisables
- **Responsive** : Optimisé mobile/tablet/desktop
- **Accessibilité** : Standards WCAG respectés

### **Navigation**
- **Menu principal** : Dashboard, Détection des risques, Paramètres
- **Breadcrumbs** : Navigation contextuelle
- **États de chargement** : Spinners et squelettes
- **Messages d'erreur** : Gestion centralisée

## 🔧 Fonctionnalités Techniques

### **État de l'application**
- **Pinia Store** : Gestion d'état centralisée
- **Vue Router** : Navigation avec gardes d'authentification
- **TypeScript** : Typage complet
- **Tailwind CSS** : Styling utilitaire

### **Données simulées**
- **Utilisateurs** : 3 types (admin, teacher, student)
- **Profils de risque** : Différents niveaux et scores
- **Alertes** : Priorités et statuts variés
- **Plans d'intervention** : Objectifs et actions
- **Notifications** : Messages temps réel

### **API Mock**
- Toutes les requêtes API sont simulées
- Délais réalistes pour les appels
- Gestion des erreurs et timeouts
- Pagination simulée

## 🎮 Scénarios de Test Recommandés

### **Scénario 1 : Administrateur**
1. Se connecter en tant qu'admin
2. Voir le dashboard complet
3. Configurer les alertes automatiques
4. Tester le simulateur WebSocket
5. Gérer les plans d'intervention

### **Scénario 2 : Enseignant**
1. Se connecter en tant qu'enseignant
2. Consulter les élèves à risque
3. Créer un plan d'intervention
4. Traiter une alerte
5. Suivre les notifications

### **Scénario 3 : Navigation et UX**
1. Tester la navigation entre les sections
2. Utiliser les filtres et recherches
3. Vérifier la responsivité mobile
4. Tester les formulaires et validations
5. Observer les animations et transitions

## 🐛 Limitations actuelles

### **Backend manquant**
- Pas de persistance des données
- Authentification simulée
- WebSocket en mode démo
- Pas d'algorithmes d'IA réels

### **Fonctionnalités à venir**
- Intégration backend Django
- Algorithmes de détection des risques
- Rapports et exports
- Tests E2E avec Playwright
- PWA et notifications push

## 🔍 Débogage

### **Vue DevTools**
- Disponible sur http://localhost:5173/__devtools__/
- Inspection des composants et stores
- Timeline des événements

### **Console navigateur**
- Messages de debug détaillés
- Erreurs API simulées
- États WebSocket

### **Network Tab**
- Requêtes API simulées
- Timing des appels
- Structures de données

## 📊 Métriques de Code

### **Qualité**
```bash
npm run lint          # ESLint
npm run type-check    # TypeScript
npm run format        # Prettier
```

### **Performance**
- Bundle optimisé avec Vite
- Lazy loading des routes
- Composants optimisés
- Images responsives

## 🚀 Prochaines étapes

### **Phase suivante : Backend Django**
1. Configuration de l'environnement Django
2. Modèles de données et migrations
3. APIs REST avec Django REST Framework
4. Authentification JWT
5. Algorithmes d'IA pour la détection des risques
6. WebSocket avec Django Channels
7. Tâches asynchrones avec Celery
8. Tests backend complets

### **Intégration finale**
1. Connexion frontend ↔ backend
2. Tests d'intégration complets
3. Déploiement et CI/CD
4. Documentation utilisateur
5. Formation et mise en production

---

**🎉 L'interface frontend est entièrement fonctionnelle en mode démo !**

Vous pouvez naviguer dans toute l'application, tester toutes les fonctionnalités, et voir le design final. Le développement du backend Django sera la prochaine étape pour avoir une application complète et fonctionnelle.