# 📋 Décisions Techniques - Web3 Opportunities Tracker

## 🎯 Vue d'ensemble

Ce document consigne les décisions techniques majeures prises au cours du développement du projet Web3 Opportunities Tracker.
 Chaque décision est motivée par des besoins spécifiques ou contraintes identifiées durant la conception ou l'exécution du projet.

## 🏗️ Décisions Structurantes

### 1. **Choix de l'Architecture**
- **Décision** : 
  - Utiliser une architecture microservices pour assurer la scalabilité et la maintenance.
  - Chaque service doit être suffisamment découplé pour permettre des déploiements indépendants sans affecter les autres services.
- **Motivation** : 
  - Faciliter les mises à jour indépendantes par service.
  - Permettre une scalabilité horizontale selon les besoins de chaque service.

### 2. **Sélection de la Base de Données**
- **Décision** : 
  - Utiliser PostgreSQL pour le stockage des données transactionnelles et Redis pour un cache performant.
- **Motivation** :
  - PostgreSQL offre une robustesse et une capacité de traitement de requêtes complexes tout en assurant la fiabilité des transactions.
  - Redis permet d'accélérer l'accès aux données fréquemment lues.

## 🔧 Outils et Technologies Choisies

### 3. **Language de Programmation**
- **Décision** :
  - Utiliser Python pour le backend pour sa bibliothèque riche et sa large adoption dans les applications web et blockchain.
- **Motivation** :
  - Rapidité de développement et richesse de l'écosystème.
  - Grande communauté assurant un support continu.

### 4. **Framework Frontend**
- **Décision** :
  - Adopter React.js pour la construction de l'interface utilisateur.
- **Motivation** :
  - Forte adoptabilité au sein de la communauté web moderne assurant une vaste accumulation de ressources d'apprentissage et utilisation de composants réutilisables.

## 🔄 Décision de Processus

### 5. **Gestion du Développement**
- **Décision** :
  - Adopter la méthodologie Agile et réaliser des sprints de développement de 2 semaines.
- **Motivation** :
  - Garantir la flexibilité nécessaire à l'accueil de changements fréquents de priorités ou technologies.

### 6. **Outils de Collaboration**
- **Décision** :
  - Utiliser GitHub Projects pour le suivi des tâches et GitHub Actions pour les pipelines CI/CD.
- **Motivation** :
  - Outils intégrés réduisant les frictions entre le code et la gestion de projet, simplifiant le pipeline de déploiement.

---

## 🔄 Processus de Révision des Décisions

Les décisions listées peuvent être réévaluées régulièrement pour s'adapter aux évolutions technologiques ou aux nouvelles contraintes de projet. 
Des revues trimestrielles permettent de valider ou ajuster ces décisions en vue d'optimiser le processus de développement et d'améliorer les résultats finaux atteints par le projet.
