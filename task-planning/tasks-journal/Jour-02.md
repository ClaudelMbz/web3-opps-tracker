# 🗓️ Jour 2 : Monitoring (Prometheus/Grafana)

## 🎯 Objectif du Jour
- Mettre en place le monitoring avec Prometheus et Grafana
- Configurer les dashboards de surveillance
- Tester les métriques et alertes de base

---

## ⏰ Créneau 1 : 0:00 - 0:30
**Tâche :** Benchmark VPS  
**Action :**
```bash
htop  # Analyser CPU/mémoire
nmon  # Rapport de performance
ping -c 10 google.com  # Test latence réseau
```
**Livrable :** Rapport de performance PDF

---

## ⏰ Créneau 2 : 0:30 - 1:00
**Tâche :** Installation Prometheus  
**Action :**
```bash
# Ajout à docker-compose.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    networks:
      - web3-net
```
**Livrable :** Prometheus UP sur port 9090

---

## ⏰ Créneau 3 : 1:00 - 1:30
**Tâche :** Installation Grafana  
**Action :**
```bash
# Ajout à docker-compose.yml
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    networks:
      - web3-net
```
**Livrable :** Grafana UP sur port 3000

---

## ⏰ Créneau 4 : 1:30 - 2:00
**Tâche :** Configuration Data Source  
**Action :**
- Ouvrir Grafana (admin/admin)
- Ajouter Prometheus data source : http://prometheus:9090
- Tester la connexion
**Livrable :** Datasource Prometheus connecté

---

## ⏰ Créneau 5 : 2:00 - 2:30
**Tâche :** POC Dashboard  
**Action :**
- Créer un dashboard "Web3 Scrapers"
- Ajouter panneau "System Metrics"
- Configurer alerte basique CPU > 80%
**Livrable :** Dashboard opérationnel avec métriques

---

## 📜 Vérification Finale
- [ ] Prometheus collecte les métriques
- [ ] Grafana affiche les données
- [ ] Dashboard "Web3 Scrapers" créé
- [ ] Alerte CPU configurée
- [ ] docker-compose.yml mis à jour

---

## 🚀 Prochaines Étapes (Jour 3)
- Développement du Scraper Galxe
- Intégration des métriques custom
- Tests de performance

---

*Note : Sauvegarder la configuration Grafana dans data/grafana pour persistance.*
