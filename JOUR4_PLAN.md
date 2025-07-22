# 📅 JOUR 4 : Scraper Zealy (API REST) - Plan Détaillé

## 🎯 Objectif du Jour 4
Améliorer et optimiser le scraper Zealy existant, ajouter des tests unitaires, intégrer avec le pipeline principal, et créer une version robuste pour la production.

## ✅ État Actuel (Acquis)
- ✅ Scraper Zealy fonctionnel (14 quêtes récupérées)
- ✅ Intégration Vault opérationnelle 
- ✅ Parsing des données réussi
- ✅ Format de sortie standardisé

---

## 📋 Plan Détaillé (2h30 = 5 créneaux × 30 min)

### 🕐 Créneau 1 (0:00-0:30) : Optimisation du Scraper Zealy
**Objectif** : Améliorer la robustesse et les performances

**Tâches** :
1. Ajouter la gestion des erreurs réseau (retry, timeout)
2. Implémenter le calcul du ROI automatique
3. Ajouter la validation des données d'entrée
4. Optimiser le parsing pour différents types de rewards

**Code à implémenter** :
```python
# Ajouter dans ZealyScraper
def calculate_roi(self, reward_amount, time_est_min, currency="XP"):
    """Calcul ROI en $/min"""
    # Conversion XP vers $ (exemple: 1 XP = $0.01)
    currency_rates = {"XP": 0.01, "POINTS": 0.005, "TOKENS": 1.0}
    usd_value = reward_amount * currency_rates.get(currency, 0.01)
    return usd_value / max(time_est_min, 1)  # Éviter division par 0
```

### 🕐 Créneau 2 (0:30-1:00) : Tests Unitaires
**Objectif** : Créer une suite de tests complète

**Tâches** :
1. Créer `tests/test_zealy_scraper.py`
2. Tests pour l'authentification Vault
3. Tests pour le parsing de différents formats de réponse
4. Tests pour le calcul du ROI
5. Mock des appels API

### 🕐 Créneau 3 (1:00-1:30) : Intégration Multi-Sources
**Objectif** : Fusionner Galxe + Zealy dans un pipeline unique

**Tâches** :
1. Modifier `main.py` pour inclure les deux scrapers
2. Normaliser le format de sortie (schema commun)
3. Déduplication inter-sources (hash MD5)
4. Agrégation des résultats

### 🕐 Créneau 4 (1:30-2:00) : Filtrage et ROI
**Objectif** : Implémenter le filtrage intelligent

**Tâches** :
1. Créer `processing/filters.py`
2. Filtrer ROI > $2/min
3. Filtrer par statut (actif, non expiré)
4. Ranking par score composite (ROI × facilité)

### 🕐 Créneau 5 (2:00-2:30) : Stockage et Export
**Objectif** : Sauvegarder et exporter les résultats

**Tâches** :
1. Export JSON horodaté
2. Export CSV pour analyse
3. Statistiques du run (nombre d'opportunités, ROI moyen)
4. Logs structurés

---

## 🧪 Tests à Valider

### ✅ Test 1 : Scraper Zealy Individual
```bash
python scrapers/zealy_scraper.py
# Attendu: "✅ X quêtes parsées"
```

### ✅ Test 2 : Pipeline Complet
```bash
python main.py
# Attendu: Agrégation Galxe + Zealy
```

### ✅ Test 3 : Tests Unitaires
```bash
python -m pytest tests/test_zealy_scraper.py -v
# Attendu: Tous les tests passent
```

### ✅ Test 4 : Calcul ROI
```bash
# Vérifier que les opportunités sont triées par ROI décroissant
```

---

## 📊 Livrables Attendus

1. **scrapers/zealy_scraper.py** : Version optimisée avec ROI
2. **tests/test_zealy_scraper.py** : Suite de tests complète
3. **processing/filters.py** : Module de filtrage
4. **main.py** : Pipeline consolidé Galxe + Zealy
5. **data/opportunities_YYYYMMDD_HHMMSS.json** : Export horodaté
6. **JOUR4_RAPPORT.md** : Rapport d'exécution

---

## 🔧 Commandes Clés

```bash
# Activer l'environnement
venv\Scripts\activate

# Tester Zealy seul
python scrapers\zealy_scraper.py

# Tester pipeline complet
python main.py

# Lancer les tests
python -m pytest tests/ -v

# Vérifier les données
dir data\
type data\opportunities_*.json
```

---

## 🎯 Critères de Succès

- [ ] Scraper Zealy robuste (gestion erreurs)
- [ ] Tests unitaires > 90% coverage
- [ ] Pipeline Galxe + Zealy fonctionnel
- [ ] Filtrage ROI > $2/min opérationnel
- [ ] Export de données structurées
- [ ] Documentation des API utilisées

---

## 🔄 Prochaines Étapes (Jour 5)

1. Scraper Twitter/RSS
2. Module fallback (si API down)
3. Monitoring des quotas API
4. Cache des résultats

## 📝 Notes Techniques

- API Zealy: `https://api-v1.zealy.io/communities/aipioneers/quests`
- Limite: 20 quêtes/page, pagination disponible
- Headers: `x-api-key` requis
- Format: JSON avec structure `data[]` ou array direct
- ROI: Calculé sur `reward/time_estimate` avec conversion currency
