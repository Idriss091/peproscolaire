# PeproScolaire Frontend 🎨

Interface utilisateur moderne pour PeproScolaire - Application de gestion scolaire avec modules IA.

[![Vue.js](https://img.shields.io/badge/Vue.js-3.4-brightgreen)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-blue)](https://tailwindcss.com/)
[![Vite](https://img.shields.io/badge/Vite-5.0-purple)](https://vitejs.dev/)

## 🚀 Démarrage rapide

```bash
# Installation des dépendances
npm install

# Lancement du serveur de développement
npm run dev

# Build pour la production
npm run build

# Prévisualisation du build
npm run preview
```

L'application sera accessible sur **http://localhost:5173/**

## 🏗️ Architecture technique

### Stack Frontend
- **Framework** : Vue.js 3 avec Composition API
- **Langage** : TypeScript pour le typage statique
- **Styling** : Tailwind CSS + Headless UI pour les composants
- **State Management** : Pinia pour la gestion d'état
- **Routing** : Vue Router 4 avec guards d'authentification
- **Build Tool** : Vite pour un développement rapide
- **Icons** : Heroicons pour une iconographie cohérente

## 🎯 Fonctionnalités implémentées

### ✅ Interface utilisateur complète

#### 🔐 Authentification et navigation
- Page de connexion moderne avec validation
- Système de rôles (Élève, Parent, Professeur, Admin)
- Navigation latérale contextuelle selon le profil
- Guards de route pour la sécurité

#### 📊 Tableaux de bord
- Dashboard personnalisé par rôle utilisateur
- Statistiques en temps réel
- Widgets interactifs
- Navigation rapide vers les modules

#### 📝 Module de gestion des notes
- Interface de saisie optimisée
- Gestion des évaluations complète
- Calculs automatiques de moyennes
- Génération de bulletins avec aperçu PDF
- Saisie en masse pour les classes
- Évaluation par compétences

#### 📅 Module emploi du temps
- Vue calendaire intuitive
- Filtres avancés multiples
- Navigation temporelle
- Export PDF/iCal (interface prête)
- Design responsive

#### 👥 Module vie scolaire
- Gestion des absences et justificatifs
- Feuilles d'appel optimisées
- Suivi comportemental
- Sanctions disciplinaires
- Statistiques par élève/classe

### 🤖 Modules IA (100% Frontend implémenté)

#### 1. 🧠 Détection du décrochage scolaire
- **Dashboard IA** avec métriques de performance (87.5% précision)
- **Analyse des élèves** à risque avec scoring temps réel
- **Prédictions intelligentes** avec niveaux de confiance
- **Plans d'intervention** automatisés
- **Rapports d'analyse** exportables

#### 2. ✨ Générateur d'appréciations IA
- **Interface de génération** avec configuration avancée
- **Types d'appréciations** multiples (bulletin, matière, progrès)
- **Sélection flexible** par classe ou individuelle
- **Workflow de validation** complet
- **Historique** avec gestion des versions

## 🎨 Système de design

### Composants UI réutilisables
- BaseButton, BaseCard, BaseModal
- BaseBadge, BaseInput, BaseTable
- Design System cohérent
- Responsive mobile-first

## 🔧 Scripts disponibles

```bash
npm run dev          # Serveur de développement
npm run build        # Build production
npm run preview      # Prévisualisation du build
npm run lint         # Linting du code
npm run type-check   # Vérification TypeScript
```

## 📱 Routes principales

- `/` - Tableau de bord principal
- `/grades` - Module notes et évaluations
- `/timetable` - Module emploi du temps
- `/attendance` - Module vie scolaire
- `/ai-dropout-detection` - Module IA détection décrochage
- `/ai-appreciation-generator` - Module IA générateur appréciations

## 🔄 Intégration API

Le frontend est préparé pour l'intégration avec l'API Django :
- Services API avec Axios configuré
- Gestion des erreurs centralisée
- Types TypeScript pour les réponses
- Stores Pinia pour l'état global

## 🧪 IDE recommandé

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (désactiver Vetur)

---

**Frontend PeproScolaire** - Interface moderne pour la gestion scolaire intelligente 🎓✨
