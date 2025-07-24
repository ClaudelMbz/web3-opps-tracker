# 🗓️ Jour 10 : n8n Workflows Avancés

## 🎯 Objectif du Jour
- Créer des workflows n8n sophistiqués
- Implémenter la logique conditionnelle
- Configurer les triggers et schedules
- Optimiser les performances des workflows

---

## ⏰ Créneau 1 : 0:00 - 0:30
**Tâche :** Workflow Conditionnel  
**Action :**
```javascript
// Node IF - Condition sur ROI
if (items[0].json.roi >= 5.0) {
  return [items];  // Route "High ROI"
} else if (items[0].json.roi >= 2.0) {
  return [[], items];  // Route "Medium ROI"
} else {
  return [[], [], items];  // Route "Low ROI"
}
```
**Livrable :** Workflow avec branchement conditionnel

---

## ⏰ Créneau 2 : 0:30 - 1:00
**Tâche :** Schedule & Triggers  
**Action :**
- Cron Trigger : "0 */2 * * *" (toutes les 2h)
- Webhook Trigger : pour déclenchement externe
- Error Workflow : gestion des erreurs
- Retry Logic : 3 tentatives avec backoff
**Livrable :** Système de triggers robuste

---

## ⏰ Créneau 3 : 1:00 - 1:30
**Tâche :** Workflow de Notification Avancé  
**Action :**
```javascript
// Node Function - Template de message avancé
const highROI = items.filter(item => item.json.roi >= 5.0);
const mediumROI = items.filter(item => item.json.roi >= 2.0 && item.json.roi < 5.0);

const message = `🚀 Web3 Opportunities Alert!

🔥 HIGH ROI (>$5/min): ${highROI.length}
${highROI.slice(0,3).map(item => `• ${item.json.title} ($${item.json.roi}/min)`).join('\n')}

⚡ MEDIUM ROI ($2-5/min): ${mediumROI.length}

📊 Total: ${items.length} nouvelles opportunités
📈 ROI moyen: $${(items.reduce((sum, item) => sum + item.json.roi, 0) / items.length).toFixed(2)}/min

🔗 Dashboard: http://localhost:8501`;

return [{json: {message}}];
```
**Livrable :** Notifications intelligentes par niveau de ROI

---

## ⏰ Créneau 4 : 1:30 - 2:00
**Tâche :** Workflow de Backup  
**Action :**
- Node Google Drive : sauvegarde hebdomadaire
- Node Email : rapport quotidien
- Node File System : backup local JSON
- Node Compression : archivage des anciennes données
**Livrable :** Système de backup automatisé

---

## ⏰ Créneau 5 : 2:00 - 2:30
**Tâche :** Monitoring & Alertes  
**Action :**
```javascript
// Node Function - Health Check
const now = new Date();
const lastRun = new Date(items[0].json.lastExecution);
const timeDiff = (now - lastRun) / (1000 * 60); // minutes

if (timeDiff > 150) { // > 2h30
  return [{
    json: {
      alert: "CRITICAL",
      message: "❌ Scraper down depuis " + Math.round(timeDiff) + " minutes",
      timestamp: now.toISOString()
    }
  }];
}

return [{json: {status: "OK", lastRun: timeDiff}}];
```
**Livrable :** Système d'alertes proactif

---

## 📜 Vérification Finale
- [ ] Workflows conditionnels fonctionnels
- [ ] Scheduling automatique configuré
- [ ] Notifications par niveau de priorité
- [ ] Backup automatique opérationnel
- [ ] Alertes de santé du système
- [ ] Logs détaillés des exécutions

---

## 📊 Workflows Avancés Créés
1. **Smart-Notification** : Alertes contextuelles
2. **Auto-Backup** : Sauvegarde multi-cible
3. **Health-Monitor** : Surveillance proactive
4. **ROI-Optimizer** : Filtrage intelligent
5. **Error-Handler** : Gestion d'erreurs centralisée

---

## 🚀 Prochaines Étapes (Jour 11)
- Tests et notifications
- Bot Telegram interactif
- Validation end-to-end

---

*Note : Exporter les workflows n8n en JSON pour versioning*
