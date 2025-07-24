# 🗓️ Jour 7 : Stockage (Google Sheets & Airtable)

## 🎯 Objectif du Jour
- Configurer l'intégration Google Sheets
- Mettre en place Airtable comme base collaborative
- Implémenter la synchronisation automatique des données
- Créer les webhooks pour notifications

---

## ⏰ Créneau 1 : 0:00 - 0:30
**Tâche :** Authentification Google Sheets  
**Action :**
```bash
pip install gspread oauth2client
# Créer service account Google Cloud
# Télécharger credentials.json
# Configurer OAuth2 pour gspread
```
**Livrable :** Authentification Google Sheets validée

---

## ⏰ Créneau 2 : 0:30 - 1:00
**Tâche :** Création Feuille Google  
**Action :**
```python
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def setup_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", 
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    
    # Créer feuille "Web3 Opportunities"
    sheet = client.create("Web3-Opportunities-Tracker")
    worksheet = sheet.get_worksheet(0)
    
    # Headers
    headers = ["Date", "Title", "Source", "Reward", "Time", "ROI", "Link", "Hash"]
    worksheet.append_row(headers)
```
**Livrable :** Feuille Google Sheets créée avec en-têtes

---

## ⏰ Créneau 3 : 1:00 - 1:30
**Tâche :** Push Data vers Sheets  
**Action :**
```python
def push_to_sheets(opportunities, worksheet):
    for op in opportunities:
        row = [
            op.get('timestamp', ''),
            op.get('title', ''),
            op.get('source', ''),
            op.get('reward', ''),
            op.get('estimated_time', ''),
            op.get('roi', ''),
            op.get('url', ''),
            op.get('hash', '')
        ]
        worksheet.append_row(row)
    print(f"✅ {len(opportunities)} opportunités ajoutées à Google Sheets")
```
**Livrable :** Données synchronisées dans Google Sheets

---

## ⏰ Créneau 4 : 1:30 - 2:00
**Tâche :** Configuration Airtable  
**Action :**
```bash
pip install pyairtable
# Créer base "CryptoMicroOps" sur airtable.com
# Configurer API Key et Base ID
```
```python
from pyairtable import Table

def setup_airtable():
    api_key = vault.retrieve_secret("airtable/api")["api_key"]
    base_id = "appXXXXXXXXXXXXXX"
    table = Table(api_key, base_id, "Opportunities")
    
    # Créer vue filtrée "ROI > 2"
    return table
```
**Livrable :** Base Airtable configurée avec table "Opportunities"

---

## ⏰ Créneau 5 : 2:00 - 2:30
**Tâche :** Intégration Dual Storage  
**Action :**
```python
def sync_to_storage(opportunities):
    # 1. Google Sheets (backup principal)
    sheet = setup_google_sheets()
    push_to_sheets(opportunities, sheet.get_worksheet(0))
    
    # 2. Airtable (collaboration)
    table = setup_airtable()
    for op in opportunities:
        table.create({
            'Title': op['title'],
            'Source': op['source'],
            'ROI': op['roi'],
            'Status': 'New'
        })
    
    print("🔄 Synchronisation dual storage terminée")
```
**Livrable :** Pipeline dual storage Google Sheets + Airtable

---

## 📜 Vérification Finale
- [ ] Google Sheets accessible et éditable
- [ ] Airtable base créée avec vues filtrées
- [ ] Synchronisation automatique fonctionnelle
- [ ] Pas de doublons entre les deux systèmes
- [ ] Webhook Airtable configuré (optionnel)
- [ ] Tests de récupération des données

---

## 📊 Structure des Données
```
Google Sheets : [Date|Title|Source|Reward|Time|ROI|Link|Hash]
Airtable      : [Title|Source|ROI|Status|Tags|Priority]
```

---

## 🚀 Prochaines Étapes (Jour 8)
- Configuration n8n pour automatisation
- Workflows de notification
- Intégration Telegram Bot

---

*Note : Sauvegarder credentials.json dans Vault, pas en local*
