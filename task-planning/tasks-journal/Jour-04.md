# 🗓️ JOUR 4 : Scraper Zealy (API REST)

## 🎯 Objectif Principal
Développer un scraper pour l'API REST de Zealy, l'intégrer avec Vault, et le tester complètement.

---

## 📊 Résumé des Tâches

| ID | Tâche | Priorité | Durée | Status | Tags |
|---|---|---|---|---|---|
| T001 | Structure code Zealy | 🔥 CRITIQUE | 30min | ⏳ À faire | `💻 DEV` `🌐 WEB3` |
| T002 | Appel API REST | 🔥 CRITIQUE | 30min | ⏳ À faire | `🌐 WEB3` `⚙️ CONFIG` |
| T003 | Parsing données | ⚡ HAUTE | 30min | ⏳ À faire | `💻 DEV` `🗄️ DATA` |
| T004 | Tests unitaires | ⚡ HAUTE | 30min | ⏳ À faire | `🧪 TEST` |
| T005 | Intégration complète | 📋 MOYENNE | 30min | ⏳ À faire | `💻 DEV` `🔧 DEBUG` |

---

# 🎯 TÂCHE T001 : Structure Code Zealy

## 🎯 Métadonnées
- **ID** : T001
- **Priorité** : 🔥 CRITIQUE
- **Durée estimée** : 30min
- **Statut** : ⏳ À faire
- **Tags** : `💻 DEV` `🌐 WEB3` `🐍 PYTHON`

## 📖 Contexte

### **Pourquoi** 
Zealy est une plateforme majeure d'engagement Web3 avec des quêtes rémunérées. Leur API REST est plus simple que GraphQL, parfait pour débuter l'agrégation multi-sources.

### **Contexte** 
Après Galxe (GraphQL), Zealy utilise une API REST classique. Plus facile à implémenter, excellente pour valider notre pipeline de parsing standardisé.

### **Impact** 
Sans Zealy, on perd ~30% des opportunités quotidiennes. C'est une source majeure pour les early-stage projects.

## 🛠️ Exécution

### **Quoi faire**
Créer le fichier `scrapers/zealy_scraper.py` avec la classe `ZealyScraper` suivant le même pattern que Galxe.

### **Comment**
1. **Créer la structure** :
   ```bash
   # Dans le dossier scrapers/
   touch zealy_scraper.py
   ```
2. **Implémenter la classe de base** :
   ```python
   import requests
   import json
   from vault_manager import VaultManager

   class ZealyScraper:
       API_BASE = "https://zealy.io/api/v1"
       
       def __init__(self):
           self.vault = VaultManager()
           self.headers = self._get_auth_headers()
           
       def _get_auth_headers(self):
           secrets = self.vault.retrieve_secret("zealy/api")
           return {
               "X-API-Key": secrets["api_key"],
               "Content-Type": "application/json"
           }
   ```
3. **Valider la structure** :
   ```bash
   python -c "from scrapers.zealy_scraper import ZealyScraper; print('✅ Classe créée')"
   ```

### **Outils requis**
- **Python 3.8+** : Langage principal
- **requests** : HTTP client
- **vault_manager** : Gestion des secrets

### **Critères de succès**
- [ ] Fichier `zealy_scraper.py` créé
- [ ] Classe `ZealyScraper` importable
- [ ] Intégration Vault fonctionnelle
- [ ] Headers d'authentification configurés

## 🔗 Relations

### **Prérequis**
- Vault opérationnel (Jour 1-2)
- vault_manager.py fonctionnel
- Secrets Zealy stockés dans Vault

### **Dépendants**
- T002 (Appel API) dépend de cette structure
- T005 (Intégration) utilise cette classe

### **Références**
- Discussions DeepSeek : lignes 126-131 du fichier User_Deepseek_Discuss.txt
- Pattern établi avec GalxeScraper (Jour 3)

## 📋 Suivi

### **Prochaines étapes**
Implémenter la méthode `fetch_quests()` pour récupérer les données via l'API REST.

### **Points de validation**
- Import sans erreur
- Connexion Vault réussie
- Headers correctement formatés

### **Risques identifiés**
- **Risque 1** : Clé API Zealy invalide → **Mitigation** : Tester avec curl d'abord
- **Risque 2** : Rate limiting → **Mitigation** : Ajouter retry logic

---

# 🎯 TÂCHE T002 : Appel API REST

## 🎯 Métadonnées
- **ID** : T002
- **Priorité** : 🔥 CRITIQUE
- **Durée estimée** : 30min
- **Statut** : ⏳ À faire
- **Tags** : `🌐 WEB3` `⚙️ CONFIG` `🐍 PYTHON`

## 📖 Contexte

### **Pourquoi** 
L'API Zealy est le point d'entrée pour récupérer les quêtes disponibles. Contrairement à GraphQL, l'API REST est plus directe et stable.

### **Contexte** 
Zealy expose ses quêtes via `GET /quests` avec pagination. Format de réponse JSON classique avec métadonnées.

### **Impact** 
Sans l'appel API, impossible de récupérer les données. C'est le cœur du scraper.

## 🛠️ Exécution

### **Quoi faire**
Implémenter la méthode `fetch_quests()` pour récupérer les quêtes via l'endpoint REST de Zealy.

### **Comment**
1. **Ajouter la méthode à la classe** :
   ```python
   def fetch_quests(self, limit=50, status="active"):
       """Récupère les quêtes Zealy via API REST"""
       endpoint = f"{self.API_BASE}/quests"
       params = {
           "limit": limit,
           "status": status,
           "sort": "created_at:desc"
       }
       
       try:
           response = requests.get(
               endpoint,
               headers=self.headers,
               params=params,
               timeout=10
           )
           response.raise_for_status()
           return response.json()
       except Exception as e:
           print(f"Erreur API Zealy: {str(e)}")
           return None
   ```
2. **Test de connexion** :
   ```bash
   python -c "
   from scrapers.zealy_scraper import ZealyScraper
   s = ZealyScraper()
   print('Status:', s.fetch_quests(limit=1))
   "
   ```
3. **Validation réponse** :
   - Vérifier le format JSON retourné
   - Identifier les champs importants : `id`, `title`, `reward`, `deadline`

### **Outils requis**
- **requests** : Client HTTP
- **Zealy API Key** : Authentification

### **Critères de succès**
- [ ] Méthode `fetch_quests()` retourne des données JSON
- [ ] Gestion d'erreurs implémentée
- [ ] Timeout configuré (10s max)
- [ ] Status code 200 confirmé

## 🔗 Relations

### **Prérequis**
- T001 (Structure code) terminé
- Clé API Zealy valide dans Vault

### **Dépendants**
- T003 (Parsing) utilisera ces données
- T004 (Tests) validera cette méthode

### **Références**
- Documentation API Zealy
- Pattern GalxeScraper pour la gestion d'erreurs

## 📋 Suivi

### **Prochaines étapes**
Parser les données JSON retournées pour les normaliser.

### **Points de validation**
- Réponse API non-null
- Format JSON valide
- Presence des champs attendus

### **Risques identifiés**
- **Risque 1** : Rate limiting (429) → **Mitigation** : Exponential backoff
- **Risque 2** : API down → **Mitigation** : Fallback vers cache

---

# 🎯 TÂCHE T003 : Parsing Données

## 🎯 Métadonnées
- **ID** : T003
- **Priorité** : ⚡ HAUTE
- **Durée estimée** : 30min
- **Statut** : ⏳ À faire
- **Tags** : `💻 DEV` `🗄️ DATA` `🐍 PYTHON`

## 📖 Contexte

### **Pourquoi** 
Les données brutes de l'API doivent être normalisées dans un format standard commun avec Galxe pour la suite du pipeline.

### **Contexte** 
Zealy retourne un format différent de Galxe. Il faut extraire et normaliser : titre, récompense, temps estimé, deadline.

### **Impact** 
Sans parsing cohérent, impossible de calculer le ROI et de filtrer efficacement.

## 🛠️ Exécution

### **Quoi faire**
Créer la méthode `parse_quests()` qui transforme la réponse API en format standardisé.

### **Comment**
1. **Analyser la structure de réponse Zealy** :
   ```json
   {
     "data": [
       {
         "id": "quest_123",
         "title": "Complete Twitter Follow",
         "description": "Follow our Twitter account",
         "xp_reward": 100,
         "estimated_time": 2,
         "deadline": "2024-01-31T23:59:59Z",
         "status": "active"
       }
     ]
   }
   ```
2. **Implémenter le parsing** :
   ```python
   def parse_quests(self, raw_data):
       """Transforme la réponse Zealy en format standard"""
       if not raw_data or "data" not in raw_data:
           return []
       
       quests = []
       for quest in raw_data["data"]:
           quests.append({
               "id": quest["id"],
               "title": quest["title"],
               "description": quest.get("description", ""),
               "reward": f"{quest['xp_reward']} XP",
               "estimated_time": quest.get("estimated_time", 5),
               "deadline": quest.get("deadline"),
               "source": "Zealy"
           })
       
       return quests
   ```
3. **Test du parsing** :
   ```python
   # Test avec données mockées
   sample_data = {"data": [{"id": "test", "title": "Test Quest", "xp_reward": 50}]}
   parsed = scraper.parse_quests(sample_data)
   assert len(parsed) == 1
   assert parsed[0]["source"] == "Zealy"
   ```

### **Outils requis**
- **Python JSON** : Manipulation données
- **Données de test** : Validation parsing

### **Critères de succès**
- [ ] Méthode `parse_quests()` créée
- [ ] Format de sortie standardisé
- [ ] Gestion des champs manquants
- [ ] Source "Zealy" ajoutée

## 🔗 Relations

### **Prérequis**
- T002 (Appel API) doit fonctionner
- Structure de données API connue

### **Dépendants**
- Calcul ROI (Jour 6) utilisera ces données normalisées
- Tests d'intégration valideront ce format

### **Références**
- Format GalxeScraper pour cohérence
- Pipeline ETL global du projet

## 📋 Suivi

### **Prochaines étapes**
Écrire les tests unitaires pour valider le parsing.

### **Points de validation**
- Format cohérent avec autres scrapers
- Gestion des erreurs de parsing
- Champs obligatoires présents

### **Risques identifiés**
- **Risque 1** : Structure API change → **Mitigation** : Validation schema
- **Risque 2** : Champs manquants → **Mitigation** : Valeurs par défaut

---

# 🎯 TÂCHE T004 : Tests Unitaires

## 🎯 Métadonnées
- **ID** : T004
- **Priorité** : ⚡ HAUTE
- **Durée estimée** : 30min
- **Statut** : ⏳ À faire
- **Tags** : `🧪 TEST` `💻 DEV` `🐍 PYTHON`

## 📖 Contexte

### **Pourquoi** 
Les tests garantissent la fiabilité du scraper Zealy et permettent de détecter les régressions lors des évolutions.

### **Contexte** 
Suite au développement, il faut valider chaque méthode avec des données mockées pour éviter la dépendance à l'API réelle.

### **Impact** 
Sans tests, impossible de garantir la stabilité lors des déploiements automatiques.

## 🛠️ Exécution

### **Quoi faire**
Créer le fichier `tests/test_zealy_scraper.py` avec les tests pour toutes les méthodes développées.

### **Comment**
1. **Créer le fichier de tests** :
   ```bash
   touch tests/test_zealy_scraper.py
   ```
2. **Implémenter les tests** :
   ```python
   import unittest
   from unittest.mock import patch, Mock
   from scrapers.zealy_scraper import ZealyScraper

   class TestZealyScraper(unittest.TestCase):
       
       @patch('scrapers.zealy_scraper.requests.get')
       def test_fetch_quests_success(self, mock_get):
           # Mock successful API response
           mock_response = Mock()
           mock_response.status_code = 200
           mock_response.json.return_value = {
               "data": [{
                   "id": "test_quest",
                   "title": "Test Quest",
                   "xp_reward": 100,
                   "estimated_time": 3
               }]
           }
           mock_get.return_value = mock_response
           
           scraper = ZealyScraper()
           result = scraper.fetch_quests(limit=1)
           
           self.assertIsNotNone(result)
           self.assertIn("data", result)

       @patch('scrapers.zealy_scraper.requests.get')
       def test_fetch_quests_failure(self, mock_get):
           # Mock API failure
           mock_get.side_effect = Exception("API Error")
           
           scraper = ZealyScraper()
           result = scraper.fetch_quests()
           
           self.assertIsNone(result)

       def test_parse_quests(self):
           scraper = ZealyScraper()
           sample_data = {
               "data": [{
                   "id": "q1",
                   "title": "Test Quest",
                   "xp_reward": 50,
                   "estimated_time": 2
               }]
           }
           
           parsed = scraper.parse_quests(sample_data)
           
           self.assertEqual(len(parsed), 1)
           self.assertEqual(parsed[0]["source"], "Zealy")
           self.assertEqual(parsed[0]["reward"], "50 XP")

   if __name__ == "__main__":
       unittest.main()
   ```
3. **Exécuter les tests** :
   ```bash
   python -m unittest tests/test_zealy_scraper.py -v
   ```

### **Outils requis**
- **unittest** : Framework de tests Python
- **unittest.mock** : Mock des dépendances externes

### **Critères de succès**
- [ ] Tous les tests passent (OK)
- [ ] Couverture des méthodes principales
- [ ] Tests d'erreur inclus
- [ ] Mock des appels externes

## 🔗 Relations

### **Prérequis**
- T001, T002, T003 terminés
- Structure de test établie (dossier tests/)

### **Dépendants**
- CI/CD utilisera ces tests
- Tests d'intégration (Jour 12) s'appuieront dessus

### **Références**
- Tests GalxeScraper comme référence
- Standards de test du projet

## 📋 Suivi

### **Prochaines étapes**
Intégrer le scraper dans le pipeline principal.

### **Points de validation**
- 100% des tests passent
- Couverture de code satisfaisante
- Tests d'erreurs inclus

### **Risques identifiés**
- **Risque 1** : Faux positifs → **Mitigation** : Tests edge cases
- **Risque 2** : Dépendances externes → **Mitigation** : Mocks complets

---

# 🎯 TÂCHE T005 : Intégration Complète

## 🎯 Métadonnées
- **ID** : T005
- **Priorité** : 📋 MOYENNE
- **Durée estimée** : 30min
- **Statut** : ⏳ À faire
- **Tags** : `💻 DEV` `🔧 DEBUG` `🌐 WEB3`

## 📖 Contexte

### **Pourquoi** 
Il faut intégrer le scraper Zealy dans le script principal `main.py` pour créer un pipeline multi-sources Galxe + Zealy.

### **Contexte** 
Le script main.py doit maintenant orchestrer les deux scrapers et agréger leurs données dans un format cohérent.

### **Impact** 
Sans intégration, le scraper Zealy reste isolé et n'apporte pas de valeur au pipeline global.

## 🛠️ Exécution

### **Quoi faire**
Modifier `main.py` pour inclure le scraper Zealy et fusionner les données avec Galxe.

### **Comment**
1. **Mettre à jour main.py** :
   ```python
   from scrapers.galxe_scraper import GalxeScraper
   from scrapers.zealy_scraper import ZealyScraper
   import json
   import time

   def run_all_scrapers():
       print("🚀 Démarrage pipeline multi-sources")
       
       # Initialiser scrapers
       galxe = GalxeScraper()
       zealy = ZealyScraper()
       
       all_opportunities = []
       
       # Scraping Galxe
       print("📊 Scraping Galxe...")
       galxe_data = galxe.fetch_quests(limit=50)
       if galxe_data:
           opportunities_galxe = galxe.parse_quests(galxe_data)
           all_opportunities.extend(opportunities_galxe)
           print(f"✅ {len(opportunities_galxe)} opportunités Galxe")
       
       # Scraping Zealy
       print("📊 Scraping Zealy...")
       zealy_data = zealy.fetch_quests(limit=50)
       if zealy_data:
           opportunities_zealy = zealy.parse_quests(zealy_data)
           all_opportunities.extend(opportunities_zealy)
           print(f"✅ {len(opportunities_zealy)} opportunités Zealy")
       
       # Sauvegarde agrégée
       timestamp = int(time.time())
       filename = f"data/all_opportunities_{timestamp}.json"
       with open(filename, "w") as f:
           json.dump(all_opportunities, f, indent=2)
       
       print(f"💾 {len(all_opportunities)} opportunités totales → {filename}")

   if __name__ == "__main__":
       run_all_scrapers()
   ```
2. **Test d'intégration** :
   ```bash
   python main.py
   ```
3. **Validation du fichier de sortie** :
   ```bash
   # Vérifier que le JSON contient des données des deux sources
   jq '.[] | .source' data/all_opportunities_*.json | sort | uniq
   # Doit afficher : "Galxe" et "Zealy"
   ```

### **Outils requis**
- **JSON** : Manipulation des données
- **jq** : Validation des données (optionnel)

### **Critères de succès**
- [ ] main.py exécute sans erreur
- [ ] Données Galxe et Zealy présentes
- [ ] Fichier JSON agrégé créé
- [ ] Sources distinctes identifiées

## 🔗 Relations

### **Prérequis**
- T001-T004 terminés
- GalxeScraper fonctionnel (Jour 3)

### **Dépendants**
- Calcul ROI (Jour 6) utilisera ces données agrégées
- Dashboard (Jour 9) affichera ces métriques

### **Références**
- Pipeline ETL global du projet
- Architecture multi-sources prévue

## 📋 Suivi

### **Prochaines étapes**
Ajouter les scrapers Twitter/RSS (Jour 5) au pipeline.

### **Points de validation**
- Exécution complète sans erreur
- Données des deux sources présentes
- Format JSON cohérent

### **Risques identifiés**
- **Risque 1** : Une source échoue, tout s'arrête → **Mitigation** : Gestion d'erreurs par source
- **Risque 2** : Doublons entre sources → **Mitigation** : Déduplication (Jour 6)

---

## 📈 Métriques de la Journée

### **Planification**
- **Nombre de tâches** : 5
- **Durée totale estimée** : 2h30
- **Priorités** : 2 critiques, 2 hautes, 1 moyenne

### **Dépendances**
- **Tâches bloquantes** : 2 (T001, T002)
- **Tâches indépendantes** : 0 (toutes séquentielles)

### **Domaines couverts**
- **Développement** : 4 tâches
- **Tests** : 1 tâche
- **Configuration** : 1 tâche

---

## 🔄 Instructions Spéciales pour l'Agent

### **Ordre d'exécution recommandé**
1. T001 (Structure) - Base obligatoire
2. T002 (API) - Dépend de T001
3. T003 (Parsing) - Dépend de T002
4. T004 (Tests) - Validation complète
5. T005 (Intégration) - Finalisation

### **Points d'attention**
- ⚠️ Vérifier que Vault contient les secrets Zealy avant de commencer
- ⚠️ Tester chaque étape avant de passer à la suivante
- ⚠️ Garder le même pattern que GalxeScraper pour la cohérence

### **Ressources utiles**
- Documentation API Zealy : https://docs.zealy.io/api
- Pattern GalxeScraper du Jour 3
- Tests unitaires existants comme référence

---

## 🎯 Objectifs de Validation

À la fin de cette journée, l'agent doit avoir :
- ✅ Un scraper Zealy fonctionnel et testé
- ✅ Une intégration multi-sources (Galxe + Zealy)
- ✅ Des tests unitaires qui passent
- ✅ Un fichier JSON avec opportunités des deux sources
- ✅ Une base solide pour ajouter d'autres sources

---

*Créé le : 22 juillet 2025*  
*Basé sur : User_Deepseek_Discuss.txt lignes 126-145*  
*Prochaine étape : Jour 5 - Scrapers Secondaires (Twitter/RSS)*
