# 🗓️ Jour 3 : Scraper Galxe (API GraphQL)

## 🎯 Objectif du Jour
- Développer un scraper pour l'API GraphQL de Galxe
- Intégrer l'authentification Vault
- Tester le parsing des données et créer les tests unitaires

---

## ⏰ Créneau 1 : 0:00 - 0:30
**Tâche :** Structure du Code  
**Action :**
```python
# Créer scrapers/galxe_scraper.py
import requests
import json
from vault_manager import VaultManager

class GalxeScraper:
    GRAPHQL_URL = "https://graphigo.prd.galaxy.eco/query"
    
    def __init__(self):
        self.vault = VaultManager()
        self.headers = self._get_auth_headers()
```
**Livrable :** Fichier scrapers/galxe_scraper.py créé

---

## ⏰ Créneau 2 : 0:30 - 1:00
**Tâche :** Requête GraphQL  
**Action :**
```python
def fetch_quests(self, space_id="1", limit=50):
    query = """
    query GetQuests($spaceId: ID!, $limit: Int!) {
        space(id: $spaceId) {
            quests(first: $limit) {
                edges {
                    node {
                        id title description reward
                        startTime endTime
                    }
                }
            }
        }
    }
    """
    # Implémentation avec gestion d'erreurs
```
**Livrable :** Méthode fetch_quests() fonctionnelle

---

## ⏰ Créneau 3 : 1:00 - 1:30
**Tâche :** Parsing des Données  
**Action :**
```python
def parse_quests(self, raw_data):
    if not raw_data or "data" not in raw_data:
        return []
    
    quests = []
    edges = raw_data["data"]["space"]["quests"]["edges"]
    
    for edge in edges:
        node = edge["node"]
        quests.append({
            "id": node["id"],
            "title": node["title"],
            "source": "Galxe"
        })
```
**Livrable :** Format de données standardisé

---

## ⏰ Créneau 4 : 1:30 - 2:00
**Tâche :** Tests Unitaires  
**Action :**
```python
# Créer tests/test_galxe_scraper.py
import unittest
from unittest.mock import patch
from scrapers.galxe_scraper import GalxeScraper

class TestGalxeScraper(unittest.TestCase):
    @patch('scrapers.galxe_scraper.requests.post')
    def test_fetch_success(self, mock_post):
        # Mock API response et tests
```
**Livrable :** Tests unitaires passants

---

## ⏰ Créneau 5 : 2:00 - 2:30
**Tâche :** Intégration Complète  
**Action :**
```python
# Créer main.py
from scrapers.galxe_scraper import GalxeScraper
import json, time

def run_galxe_scraper():
    scraper = GalxeScraper()
    raw_data = scraper.fetch_quests(limit=100)
    quests = scraper.parse_quests(raw_data)
    
    # Sauvegarde JSON horodatée
```
**Livrable :** Pipeline Galxe fonctionnel avec export JSON

---

## 📜 Vérification Finale
- [ ] GalxeScraper classe créée et importable
- [ ] Intégration Vault pour authentification
- [ ] Requête GraphQL fonctionnelle
- [ ] Parsing au format standardisé
- [ ] Tests unitaires > 90% success
- [ ] Export JSON avec timestamp

---

## 🚀 Prochaines Étapes (Jour 4)
- Développement du Scraper Zealy
- Intégration multi-sources
- Calcul du ROI

---

*Note : Sauvegarder les clés API Galxe dans Vault via vault_manager.py*
