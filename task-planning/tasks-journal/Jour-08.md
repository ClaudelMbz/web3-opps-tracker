# 🗓️ Jour 8 : Automatisation n8n

## 🎯 Objectif du Jour
- Développer les workflows n8n avancés
- Créer l'automatisation Google Sheets ↔ Notion
- Implémenter les notifications Telegram intelligentes
- Tester l'orchestration complète avec filtrage ROI

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
**Tâche :** Workflow ETL Notion  
**Action :**
- Créer workflow "Web3-ETL-Notion-Pipeline"
- Webhook Trigger → Réception des données du pipeline
- Node Function → Transformation et calcul priorité ROI
- Node HTTP Request → Synchronisation vers Notion Database
**Livrable :** Workflow ETL Notion fonctionnel

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
**Tâche :** Orchestration Notion + Telegram  
**Action :**
- Workflow "Smart-Notification" (alertes par niveau ROI)
- Workflow "Notion-Sync" (synchronisation bidirectionnelle)
- Workflow "ROI-Filter" (🔥 High, ⚡ Medium, 📝 Low)
- Test pipeline complet Google Sheets → Notion → Telegram
**Livrable :** Automatisation intelligente opérationnelle

---

## 📜 Vérification Finale
- [ ] Workflows n8n avancés opérationnels
- [ ] Synchronisation Sheets ↔ Notion fonctionnelle
- [ ] Notifications Telegram par priorité ROI
- [ ] Filtrage automatique High/Medium/Low ROI
- [ ] Properties Notion (Priority, Status) mises à jour
- [ ] Pipeline end-to-end sans erreur

---

## 📊 Workflows Créés
1. **Web3-Notion-Sync** : Google Sheets → Notion avec priorités
2. **Smart-ROI-Filter** : Filtrage 🔥 High (>$10) ⚡ Medium (>$5) 📝 Low
3. **Intelligent-Notifications** : Alertes Telegram contextuelles
4. **Notion-Status-Manager** : Gestion automatique des statuts

---

## 🚀 Prochaines Étapes (Jour 9)
- Dashboard Streamlit pour visualisation
- Métriques et KPIs
- Interface utilisateur

---

*Note : Sauvegarder les workflows n8n dans ./n8n_data pour persistance*
