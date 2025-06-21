# 🎯 Guide de Démonstration PeproScolaire

Ce guide vous explique comment préparer et réaliser une démonstration complète de PeproScolaire pour un établissement scolaire.

## 📋 Table des matières

1. [Prérequis](#prérequis)
2. [Installation en local](#installation-en-local)
3. [Préparation de la démonstration](#préparation-de-la-démonstration)
4. [Scénario de démonstration](#scénario-de-démonstration)
5. [Comptes de test](#comptes-de-test)
6. [Points clés à présenter](#points-clés-à-présenter)
7. [FAQ et objections courantes](#faq-et-objections-courantes)

---

## 🔧 Prérequis

### Système requis
- **Python 3.11+**
- **Node.js 18+** 
- **Git**
- **Navigateur web moderne** (Chrome, Firefox, Safari, Edge)

### Vérification des prérequis
```bash
python --version    # Python 3.11+
node --version      # v18+
npm --version       # 8+
git --version       # 2.30+
```

---

## 🚀 Installation en local

### 1. Clonage du projet
```bash
git clone https://github.com/votre-org/peproscolaire.git
cd peproscolaire
```

### 2. Configuration du backend (Django)
```bash
cd backend

# Création de l'environnement virtuel
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installation des dépendances
pip install -r requirements.txt

# Configuration de la base de données
python manage.py migrate

# Génération des données de démonstration
python manage.py setup_demo_school --force
```

### 3. Configuration du frontend (Vue.js)
```bash
cd ../frontend/peproscolaire-ui

# Installation des dépendances
npm install

# Configuration de l'environnement
cp .env.example .env.local
```

### 4. Lancement de l'application

**Terminal 1 - Backend :**
```bash
cd backend
source venv/bin/activate
python manage.py runserver 127.0.0.1:8000
```

**Terminal 2 - Frontend :**
```bash
cd frontend/peproscolaire-ui
npm run dev
```

### 5. Vérification de l'installation
- **Frontend :** http://localhost:5173/
- **API Backend :** http://127.0.0.1:8000/api/
- **Admin Django :** http://127.0.0.1:8000/admin/

---

## 🎬 Préparation de la démonstration

### Configuration recommandée
1. **Écran principal :** Application web (navigateur en plein écran)
2. **Écran secondaire :** Documentation, notes, données techniques
3. **Connexion internet :** Stable pour éviter les latences
4. **Sauvegarde :** Avoir des captures d'écran en cas de problème technique

### Données de démonstration incluses
- **Établissement :** Collège Demo PeproScolaire
- **Année scolaire :** 2025-2026
- **5 classes :** 6A (21 élèves), 6B (20 élèves), 5A, 4A, 3A (20 élèves chacune)
- **11 professeurs** avec spécialités variées
- **140 parents** liés aux élèves
- **322 évaluations** avec plus de 6 500 notes
- **15 devoirs** répartis sur les matières
- **20 messages** de démonstration

---

## 🎭 Scénario de démonstration

### Phase 1: Vue d'ensemble (5 min)
> **"Bonjour, je vais vous présenter PeproScolaire, une solution complète de gestion scolaire pensée spécifiquement pour les collèges et lycées français."**

1. **Page d'accueil :** Présentation de l'interface moderne
2. **Architecture :** Expliquer SaaS vs On-Premise
3. **Sécurité :** Chiffrement, conformité RGPD
4. **Multi-utilisateurs :** Professeurs, élèves, parents, administration

### Phase 2: Interface Professeur (10 min)
**Connexion :** `demo` / `demo123`

#### A. Tableau de bord professeur
- Vue d'ensemble des classes
- Prochains cours et événements
- Notifications importantes

#### B. Gestion des notes
- Créer une nouvelle évaluation
- Saisir des notes rapidement
- Visualiser les statistiques de classe
- Générer des graphiques de progression

#### C. Cahier de texte numérique
- Ajouter un cours avec contenu pédagogique
- Assigner un devoir avec fichiers joints
- Planifier une évaluation

#### D. Communication
- Envoyer un message aux parents
- Notification d'absence
- Suivi des travaux non rendus

### Phase 3: Interface Élève (8 min)
**Connexion :** `eleve` / `demo123`

#### A. Tableau de bord élève
- Emploi du temps personnalisé
- Prochains devoirs à rendre
- Dernières notes et moyennes

#### B. Suivi pédagogique
- Consulter les notes par matière
- Télécharger les cours et ressources
- Rendre un devoir numérique

#### C. Communication
- Messages des professeurs
- Notifications importantes
- Calendrier personnel

### Phase 4: Interface Parent (7 min)
**Connexion :** `parent` / `demo123`

#### A. Suivi de l'enfant
- Tableau de bord avec synthèse
- Évolution des notes et moyennes
- Absences et retards

#### B. Communication école-famille
- Messages des professeurs
- Convocations et rendez-vous
- Validation des sorties scolaires

#### C. Bulletins et bilans
- Consultation des bulletins
- Téléchargement PDF
- Historique des évaluations

### Phase 5: Interface Administration (10 min)
**Connexion :** `admin` / `demo123`

#### A. Gestion des utilisateurs
- Création en masse d'élèves
- Attribution des classes
- Gestion des professeurs

#### B. Configuration établissement
- Paramétrage des périodes
- Création des emplois du temps
- Configuration des matières

#### C. Analyses et rapports
- Statistiques globales
- Taux de réussite par classe
- Tableaux de bord pour le suivi des risques élèves (basés sur les données actuelles, avec moteur de prédiction IA en cours de finalisation)

#### D. Administration système
- Sauvegarde des données
- Gestion des permissions
- Logs de sécurité

---

## 🔐 Comptes de test

| Type | Identifiant | Mot de passe | Description |
|------|-------------|--------------|-------------|
| 👨‍🏫 **Professeur** | `demo` | `demo123` | Professeur principal avec toutes les fonctionnalités |
| 👨‍🎓 **Élève** | `eleve` | `demo123` | Élève de 6A avec notes et devoirs |
| 👨‍👩‍👧 **Parent** | `parent` | `demo123` | Parent d'élève avec accès au suivi |
| 🔧 **Admin** | `admin` | `demo123` | Administrateur avec tous les droits |

---

## 💡 Points clés à présenter

### Avantages compétitifs
1. **🚀 Modernité :** Interface responsive, moderne et intuitive
2. **🔒 Sécurité :** Chiffrement bout-en-bout, conformité RGPD
3. **🤖 IA intégrée :** Génération d'appréciations, suggestions de devoirs, chatbot pédagogique. D'autres modules IA (comme la détection de décrochage et le matching intelligent de stages) disposent d'interfaces prêtes avec un développement backend en cours ou planifié.
4. **📱 Multi-plateforme :** Web, mobile (iOS/Android)
5. **🔧 Flexibilité :** SaaS ou On-Premise selon les besoins
6. **🇫🇷 Français :** Conçu pour le système éducatif français

### Fonctionnalités uniques
- **Interface pour l'analyse** du décrochage scolaire (moteur de prédiction IA en développement, permettant déjà de visualiser les facteurs de risque basés sur les données existantes)
- **Suggestions automatiques** de devoirs par IA (fonctionnel via OpenAI)
- **Génération d'appréciations** par IA (fonctionnel via OpenAI)
- **Chatbot pédagogique** intégré (fonctionnel via OpenAI et base de connaissances locale)
- **Communication unifiée** école-famille
- **Tableau de bord personnalisé** par profil utilisateur
- **Gestion avancée** des compétences
- **Conformité totale** avec les exigences françaises

### Arguments économiques
- **ROI rapide :** Gain de temps administratif de 40%
- **Formation incluse :** Accompagnement complet
- **Support technique :** 7j/7 pendant la période critique
- **Évolutivité :** Tarification selon le nombre d'élèves
- **Maintenance :** Mises à jour automatiques incluses

---

## ❓ FAQ et objections courantes

### "C'est trop compliqué pour nos professeurs..."
> **Réponse :** L'interface a été conçue avec des professeurs. Formation de 2h maximum, interface intuitive, aide contextuelle disponible partout.

### "Nous avons déjà un système..."
> **Réponse :** Migration automatique des données, période de transition accompagnée, fonctionnement en parallèle possible pendant 1 mois.

### "Et la sécurité des données ?"
> **Réponse :** Hébergement France, certification ISO 27001, chiffrement AES-256, sauvegardes quotidiennes, conformité RGPD totale.

### "Quel est le coût réel ?"
> **Réponse :** 
> - **SaaS :** 2-4€/élève/mois tout inclus
> - **On-Premise :** Licence annuelle + support
> - **Formation :** Incluse dans l'abonnement
> - **Migration :** Gratuite

### "Et si vous disparaissez ?"
> **Réponse :** Code source déposé chez huissier, garantie de récupération des données, partenaires de confiance pour la continuité.

### "Intégration avec nos outils existants ?"
> **Réponse :** API complète, connecteurs standard (LDAP, ENT, SIECLE), développement sur mesure possible.

---

## 🎯 Conseils pour réussir la démonstration

### Avant la démo
- [ ] Tester tous les comptes 24h avant
- [ ] Préparer 3-4 scénarios selon le profil client
- [ ] Avoir des données de l'établissement (nb élèves, classes...)
- [ ] Préparer les réponses aux objections spécifiques

### Pendant la démo
- [ ] Commencer par identifier les besoins prioritaires
- [ ] Montrer d'abord ce qui intéresse le plus le client
- [ ] Laisser l'interlocuteur manipuler l'interface
- [ ] Personnaliser avec le nom de leur établissement
- [ ] Noter toutes les questions pour le suivi

### Après la démo
- [ ] Envoyer un récapitulatif dans les 24h
- [ ] Proposer une période d'essai gratuite
- [ ] Planifier un appel de suivi
- [ ] Préparer un devis personnalisé

---

## 🔄 Maintenance de l'environnement de démo

### Régénération des données
```bash
# Effacer et recréer la démonstration
python manage.py setup_demo_school --force
```

### Mise à jour du système
```bash
# Backend
cd backend
git pull
pip install -r requirements.txt
python manage.py migrate

# Frontend  
cd frontend/peproscolaire-ui
git pull
npm install
npm run build
```

### Sauvegarde avant démo importante
```bash
# Sauvegarde de la base de données
cp backend/demo.db backend/demo_backup_$(date +%Y%m%d).db
```

---

## 📞 Support et contact

- **Documentation technique :** https://docs.peproscolaire.fr
- **Support commercial :** commercial@peproscolaire.fr
- **Support technique :** support@peproscolaire.fr
- **Urgences :** +33 1 XX XX XX XX

---

*Dernière mise à jour : $(date +"%d/%m/%Y")*
*Version de la démo : 1.0*

**🚀 Bonne démonstration !**