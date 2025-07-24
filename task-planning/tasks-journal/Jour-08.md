# 🗓️ Jour 8 : Automatisation n8n

## 🎯 Objectif du Jour
- Installer et configurer n8n pour l'orchestration des workflows
- Créer les workflows automatisés
- Intégrer avec Airtable et Google Sheets
- Tester l'automatisation end-to-end

---

## ⏰ Créneau 1 : 0:00 - 0:30
**Tâche :** Installation n8n  
**Action :**
```bash
# Ajout à docker-compose.yml
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=admin123
    volumes:
      - ./n8n_data:/home/node/.n8n
    networks:
      - web3-net
```
**Livrable :** n8n accessible sur http://localhost:5678

---

## ⏰ Créneau 2 : 0:30 - 1:00
**Tâche :** Workflow ETL de Base  
**Action :**
- Créer workflow "Web3-ETL-Pipeline"
- Node HTTP Request → Python scraper
- Node Function → Transformation des données
- Node Airtable → Stockage
**Livrable :** Workflow ETL basique fonctionnel

---

## ⏰ Créneau 3 : 1:00 - 1:30
**Tâche :** Node Google Sheets  
**Action :**
```javascript
// Node Function pour Google Sheets
const processedData = items[0].json.opportunities.map(op => {
  return {
    Date: new Date().toISOString(),
    Title: op.title,
    Source: op.source,
    ROI: op.roi,
    Link: op.url
  };
});

return processedData.map(data => ({json: data}));
```
**Livrable :** Node Google Sheets configuré et testé

---

## ⏰ Créneau 4 : 1:30 - 2:00
**Tâche :** Node Telegram Bot  
**Action :**
```bash
# Créer bot avec @BotFather
# Récupérer token et chat_id
```
```javascript
// Message Template
const message = `🚀 Nouvelles opportunités Web3!
📊 ${items.length} opportunités trouvées
💰 ROI moyen: $${avgROI}/min
🔗 Voir détails: [Google Sheets Link]`;
```
**Livrable :** Notifications Telegram automatiques

---

## ⏰ Créneau 5 : 2:00 - 2:30
**Tâche :** Orchestration Complète  
**Action :**
- Workflow "Scraper-Schedule" (toutes les 2h)
- Workflow "ROI-Filter" (filtre > $2/min)  
- Workflow "Notification" (si > 10 nouvelles opportunités)
- Test end-to-end complet
**Livrable :** Automatisation complète fonctionnelle

---

## 📜 Vérification Finale
- [ ] n8n interface accessible
- [ ] Workflow ETL exécute sans erreur
- [ ] Données synchronisées Sheets ↔ Airtable
- [ ] Notifications Telegram reçues
- [ ] Scheduling automatique (cron)
- [ ] Logs d'exécution disponibles

---

## 📊 Workflows Créés
1. **Web3-ETL-Pipeline** : Scraping → Processing → Storage
2. **ROI-Filter-Workflow** : Filtrage avancé par ROI
3. **Notification-Workflow** : Alertes Telegram
4. **Backup-Workflow** : Sauvegarde quotidienne

---

## 🚀 Prochaines Étapes (Jour 9)
- Dashboard Streamlit pour visualisation
- Métriques et KPIs
- Interface utilisateur

---

*Note : Sauvegarder les workflows n8n dans ./n8n_data pour persistance*
