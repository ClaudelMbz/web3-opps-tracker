# 🗓️ Jour 6 : Processing & ROI (Calcul ROI, Déduplication)

## 🎯 Objectif du Jour
- Implémenter le calcul automatique du ROI
- Créer le système de déduplication avancé
- Filtrer les opportunités par rentabilité
- Optimiser le pipeline de traitement des données

---

## ⏰ Créneau 1 : 0:00 - 0:30
**Tâche :** Calcul ROI  
**Action :**
```python
# Créer processing/roi_calculator.py
def calculate_roi(reward_amount, time_est_min, currency="USD"):
    currency_rates = {"XP": 0.01, "GAL": 0.50, "POINTS": 0.005}
    usd_value = reward_amount * currency_rates.get(currency, 1.0)
    return usd_value / max(time_est_min, 1)  # $/min
```
**Livrable :** Module ROI calculator fonctionnel

---

## ⏰ Créneau 2 : 0:30 - 1:00
**Tâche :** Hash de Déduplication  
**Action :**
```python
import hashlib
def hash_opportunity(title, link, description=""):
    content = f"{title}|{link}|{description}"
    return hashlib.md5(content.encode()).hexdigest()
    
def deduplicate_opportunities(opportunities):
    seen_hashes = set()
    unique_ops = []
    for op in opportunities:
        hash_key = hash_opportunity(op['title'], op.get('url', ''))
        if hash_key not in seen_hashes:
            seen_hashes.add(hash_key)
            unique_ops.append(op)
    return unique_ops
```
**Livrable :** Système de déduplication opérationnel

---

## ⏰ Créneau 3 : 1:00 - 1:30
**Tâche :** Filtrage ROI  
**Action :**
```python
def filter_by_roi(opportunities, min_roi=2.0):
    filtered = []
    for op in opportunities:
        if op.get('roi', 0) >= min_roi:
            filtered.append(op)
    return sorted(filtered, key=lambda x: x.get('roi', 0), reverse=True)
```
**Livrable :** Pipeline de filtrage par ROI > $2/min

---

## ⏰ Créneau 4 : 1:30 - 2:00
**Tâche :** Tests Processing  
**Action :**
```python
# tests/test_processing.py
import unittest
from processing.roi_calculator import calculate_roi
from processing.deduplication import deduplicate_opportunities

class TestProcessing(unittest.TestCase):
    def test_roi_calculation(self):
        roi = calculate_roi(100, 5, "XP")  # 100 XP in 5 min
        self.assertEqual(roi, 0.2)  # $0.20/min
```
**Livrable :** Tests unitaires processing > 95% coverage

---

## ⏰ Créneau 5 : 2:00 - 2:30
**Tâche :** Intégration Pipeline  
**Action :**
```python
# Modifier main.py
from processing.roi_calculator import calculate_roi
from processing.deduplication import deduplicate_opportunities

def process_opportunities(all_opportunities):
    # 1. Calcul ROI
    for op in all_opportunities:
        op['roi'] = calculate_roi(op.get('reward_amount', 10), 
                                 op.get('estimated_time', 5))
    
    # 2. Déduplication
    unique_ops = deduplicate_opportunities(all_opportunities)
    
    # 3. Filtrage
    filtered_ops = filter_by_roi(unique_ops, min_roi=2.0)
    
    return filtered_ops
```
**Livrable :** Pipeline complet avec ROI et filtrage

---

## 📜 Vérification Finale
- [ ] ROI calculé automatiquement pour chaque opportunité
- [ ] Déduplication efficace (hash MD5)
- [ ] Filtrage ROI > $2/min fonctionnel
- [ ] Tests processing passants
- [ ] Pipeline intégré dans main.py
- [ ] Export avec métriques ROI

---

## 🚮 Métriques Attendues
- **Opportunités avant filtrage** : 100-150
- **Après déduplication** : 80-120
- **Après filtrage ROI** : 40-60
- **ROI moyen** : $3-5/min

---

## 🚀 Prochaines Étapes (Jour 7)
- Intégration Google Sheets
- Configuration Airtable
- Webhook pour notifications

---

*Note : Ajuster les taux de conversion currency_rates selon les données du marché*
