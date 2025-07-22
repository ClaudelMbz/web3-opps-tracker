# 🗓️ Jour 1 : Infrastructure de Base

## 🎯 Objectif du Jour
- Mettre en place l’infrastructure de base : Docker, Git, Python, et Vault pour sécuriser les clés.

---

## ⏰ Créneau 1 : 0:00 - 0:30
**Tâche :** Installation de Docker  
**Action :**
```bash
sudo apt update && sudo apt install docker.io docker-compose
```
**Livrable :** Docker fonctionnel (`docker --version` OK)

---

## ⏰ Créneau 2 : 0:30 - 1:00
**Tâche :** Configuration Git  
**Action :**
```bash
git init && echo ".env\nvault/\n__pycache__/" > .gitignore
```
**Livrable :** Dépôt Git prêt (`git status` clean)

---

## ⏰ Créneau 3 : 1:00 - 1:30
**Tâche :** Environnement Python  
**Action :**
```bash
python -m venv venv && source venv/bin/activate && pip install requests hvac
```
**Livrable :** Librairies installées (`pip list`)

---

## ⏰ Créneau 4 : 1:30 - 2:00
**Tâche :** Lancer Vault  
**Action :**
```bash
docker run -d --name vault -p 8200:8200 vault
```
**Livrable :** Vault accessible (`http://localhost:8200`)

---

## ⏰ Créneau 5 : 2:00 - 2:30
**Tâche :** Stocker une clé  
**Action :**
```bash
vault write secret/data/wallets/airdrop1 api_key="12345"
```
**Livrable :** Clé lisible (`vault read secret/...`)

---

## 📜 Vérification Finale
- [ ] Docker installé et fonctionnel
- [ ] Git configué avec .gitignore
- [ ] Environnement Python avec librairies requises
- [ ] Vault opérationnel et accessible
- [ ] Clé API stockée correctement

---

## 🚀 Prochaines Étapes (Jour 2)
- Monitoring avec Prometheus et Grafana
- Développement Scraper Galxe

---

*Note : Sauvegardez le token root de Vault dans un endroit sûr.*
