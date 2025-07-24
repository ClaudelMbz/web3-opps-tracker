# 🗓️ Jour 12 : Monitoring & Alertes

## 🎯 Objectif du Jour
- Configurer le monitoring avancé avec alertes
- Implémenter les healthchecks automatiques
- Créer un système de surveillance proactive
- Intégrer les métriques business

---

## ⏰ Créneau 1 : 0:00 - 0:30
**Tâche :** Healthcheck Script  
**Action :**
```python
# healthcheck.py
import requests
import psutil
from datetime import datetime

def check_system_health():
    checks = {
        'cpu_usage': psutil.cpu_percent() < 80,
        'memory_usage': psutil.virtual_memory().percent < 85,
        'disk_space': psutil.disk_usage('/').percent < 90,
        'vault_status': check_vault_health(),
        'scrapers_status': check_scrapers_health()
    }
    
    return {
        'timestamp': datetime.now().isoformat(),
        'overall_status': all(checks.values()),
        'checks': checks
    }
```
**Livrable :** Script de healthcheck complet

---

## ⏰ Créneau 2 : 0:30 - 1:00
**Tâche :** Cron Job Monitoring  
**Action :**
```bash
# Ajout à crontab
*/5 * * * * cd /project && python healthcheck.py >> logs/health.log 2>&1
0 */6 * * * cd /project && python backup_check.py
0 9 * * * cd /project && python daily_report.py
```
```python
# daily_report.py
def generate_daily_report():
    stats = {
        'opportunities_found': count_daily_opportunities(),
        'avg_roi': calculate_avg_roi(),
        'sources_active': check_active_sources(),
        'errors': count_daily_errors()
    }
    send_daily_telegram_report(stats)
```
**Livrable :** Surveillance automatique avec cron

---

## ⏰ Créneau 3 : 1:00 - 1:30
**Tâche :** Alertes Prometheus  
**Action :**
```yaml
# prometheus_rules.yml
groups:
  - name: web3_scraper_alerts
    rules:
      - alert: ScraperDown
        expr: up{job="web3_scraper"} == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Web3 Scraper is down"
          
      - alert: LowOpportunityCount
        expr: daily_opportunities_count < 50
        for: 10m
        labels:
          severity: warning
```
**Livrable :** Règles d'alertes Prometheus configurées

---

## ⏰ Créneau 4 : 1:30 - 2:00
**Tâche :** Dashboard Grafana Avancé  
**Action :**
- Panneau "System Health" (CPU, RAM, Disk)
- Panneau "Scraper Performance" (latence, success rate)
- Panneau "Business Metrics" (ROI, opportunités/jour)
- Alertes visuelles avec seuils
**Livrable :** Dashboard Grafana complet avec alertes

---

## ⏰ Créneau 5 : 2:00 - 2:30
**Tâche :** Intégration Telegram Alertes  
**Action :**
```python
# alert_manager.py
class AlertManager:
    def __init__(self):
        self.telegram_bot = TelegramBot()
        
    def send_critical_alert(self, message, data=None):
        self.telegram_bot.send_message(
            f"🚨 CRITICAL ALERT\n{message}\n\nTimestamp: {datetime.now()}"
        )
        
    def send_warning(self, message):
        self.telegram_bot.send_message(f"⚠️ WARNING\n{message}")
        
    def send_info(self, message):
        self.telegram_bot.send_message(f"ℹ️ INFO\n{message}")
```
**Livrable :** Système d'alertes Telegram intégré

---

## 📜 Vérification Finale
- [ ] Healthchecks s'exécutent toutes les 5 minutes
- [ ] Alertes Prometheus configurées et fonctionnelles
- [ ] Dashboard Grafana avec seuils d'alerte
- [ ] Notifications Telegram automatiques
- [ ] Logs structurés et archivés
- [ ] Métriques business trackées

---

## 📊 Métriques Surveillées
- **Système** : CPU, RAM, Disk, Network
- **Application** : Latence, Success Rate, Error Rate
- **Business** : Opportunités/jour, ROI moyen, Sources actives
- **Sécurité** : Vault status, API quotas

---

## 🚀 Prochaines Étapes (Jour 13)
- Tests et CI/CD
- Pipeline GitHub Actions
- Automatisation des déploiements

---

*Note : Configurer les seuils d'alerte selon l'environnement (dev/prod)*
