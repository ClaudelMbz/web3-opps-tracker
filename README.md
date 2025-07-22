# 🚀 Web3 Opportunities Tracker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

**Système automatisé de détection, filtrage et notification d'opportunités Web3** (airdrops, bounties, quêtes) à haut rendement.

## 📋 Table des matières

- [🎯 Objectifs](#-objectifs)
- [🏗️ Architecture](#️-architecture)
- [⚡ Installation Rapide](#-installation-rapide)
- [🔧 Configuration](#-configuration)
- [🚀 Utilisation](#-utilisation)
- [📊 Fonctionnalités](#-fonctionnalités)
- [🧪 Tests](#-tests)
- [📈 Monitoring](#-monitoring)
- [🔐 Sécurité](#-sécurité)
- [🤝 Contribution](#-contribution)

## 🎯 Objectifs

- **200+ opportunités/jour** : Scraping automatisé multi-sources
- **ROI > $2/min** : Filtrage intelligent des opportunités rentables
- **100% automatisé** : Notifications Telegram instantanées
- **Durée de vie 6-12 mois** : Architecture évolutive

## 🏗️ Architecture

```
Web3-Opps-Tracker/
├── 📁 scrapers/           # Scrapers pour chaque plateforme
│   ├── galxe_scraper.py   # API GraphQL Galxe
│   └── zealy_scraper.py   # API REST Zealy (✅ ROI intégré)
├── 📁 processing/         # Filtrage et traitement
├── 📁 monitoring/         # Métriques et alertes
├── 📁 tests/             # Tests unitaires
├── 🐳 docker-compose.yml # Infrastructure (Vault, Grafana)
├── 🔐 vault_manager.py   # Gestion sécurisée des secrets
└── ⚙️ main.py            # Pipeline principal
```

### 🏢 Infrastructure

- **🔐 HashiCorp Vault** : Stockage sécurisé des clés API
- **📊 Prometheus + Grafana** : Monitoring temps réel
- **🐳 Docker** : Conteneurisation des services
- **🔄 n8n** : Orchestration des workflows

## ⚡ Installation Rapide

### 1. Prérequis

```bash
# Windows
choco install docker-desktop git python
# Ou télécharger manuellement

# Linux/macOS
sudo apt install docker docker-compose git python3-pip
```

### 2. Installation

```bash
git clone https://github.com/ClaudelMbz/web3-opps-tracker.git
cd web3-opps-tracker

# Environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# Dépendances
pip install -r requirements.txt
playwright install chromium
```

### 3. Services Docker

```bash
# Lancer Vault + Monitoring
docker network create web3-net
docker run -d --name vault --network web3-net -p 8200:8200 \
  -e VAULT_DEV_ROOT_TOKEN_ID="web3root" vault:latest
```

## 🔧 Configuration

### 1. Variables d'environnement

Créer un fichier `.env` :

```env
# Vault
VAULT_ADDR=http://localhost:8200
VAULT_TOKEN=web3root

# API Keys (stockées dans Vault)
ZEALY_API_KEY=votre_cle_zealy
GALXE_API_KEY=votre_cle_galxe

# Telegram
BOT_TOKEN=votre_bot_token
MY_CHAT_ID=votre_chat_id
```

### 2. Configuration Vault

```bash
# Stocker les secrets
python vault_manager.py
```

## 🚀 Utilisation

### 🎯 Scraping simple

```bash
# Tester Zealy
python scrapers/zealy_scraper.py

# Tester Galxe
python scrapers/galxe_scraper.py

# Pipeline complet
python main.py
```

### 📊 Résultats

Les opportunités sont sauvegardées dans :
- `data/opportunities_YYYYMMDD.json`
- Triées par **ROI décroissant**
- Filtrées par seuil `ROI > $2/min`

## 📊 Fonctionnalités

### ✅ Scrapers Disponibles

| Plateforme | Status | ROI | Pagination | Notes |
|-----------|--------|-----|------------|-------|
| **Zealy** | ✅ Opérationnel | ✅ Calculé | ✅ Auto | API REST stable |
| **Galxe** | ✅ Opérationnel | 🔄 En cours | ✅ Auto | GraphQL + fallback |
| Twitter RSS | 🔄 Prévu J5 | - | ✅ Auto | Fallback feeds |
| CryptoPanic | 🔄 Prévu J5 | - | ✅ Auto | News filtering |

### 🧮 Calcul ROI

```python
# Conversion automatique des devises
currency_rates = {
    "XP": 0.01,      # 1 XP = $0.01
    "POINTS": 0.005, # 1 POINT = $0.005  
    "TOKENS": 1.0,   # 1 TOKEN = $1.00
    "GAL": 2.5,      # 1 GAL = $2.50
    "USD": 1.0       # 1 USD = $1.00
}

roi_usd_per_min = (reward × rate) / time_estimate
```

### 📈 Métriques Suivies

- **Volume** : Opportunités/jour par source
- **Qualité** : % ROI > seuil
- **Performance** : Latence API, taux d'erreur
- **Rentabilité** : Gain estimé vs coût infrastructure

## 🧪 Tests

```bash
# Tests unitaires
python -m pytest tests/ -v

# Coverage
python -m pytest tests/ --cov=scrapers --cov-report=html

# Test d'intégration
python tests/integration_test.py
```

## 📈 Monitoring

### Dashboard Grafana
- **URL** : http://localhost:3000
- **Login** : admin/admin
- **Métriques** : Latence, volume, erreurs

### Alertes Telegram
- Échecs de scraping
- Dépassement de quotas
- Opportunités > seuil ROI

## 🔐 Sécurité

### 🔑 Gestion des Secrets

```bash
# Toutes les clés API sont dans Vault
vault kv get secret/zealy/api
vault kv get secret/galxe/api
```

### 🛡️ Bonnes Pratiques

- ✅ Aucune clé en plain-text dans le code
- ✅ .env exclu du versioning
- ✅ Chiffrement des tokens Vault
- ✅ Rotation périodique des clés

## 🚧 Roadmap

### Phase Actuelle : **Jour 4/23** ✅
- [x] Infrastructure (Vault, Docker, Git)
- [x] Scraper Zealy avec ROI
- [x] Scraper Galxe avec GraphQL
- [x] Tests unitaires
- [ ] Pipeline multi-sources
- [ ] Filtrage avancé

### Prochaines Phases
- **J5-J8** : Twitter/RSS, Pipeline ETL, Google Sheets
- **J9-J12** : Dashboard Streamlit, n8n workflows  
- **J13-J15** : CI/CD, Documentation, Production
- **J16-J18** : NLP, Cache Redis, Optimisations

## 📊 Performance

### Benchmarks Actuels
- **Zealy** : 14 quêtes récupérées en ~2s
- **Galxe** : Variable selon campagnes actives
- **Mémoire** : ~50MB par scraper
- **ROI moyen** : $0.01-$0.30/min selon sources

### Objectifs Production
- **Débit** : 200+ opp/jour consolidées
- **Latence** : \< 5min notification après publication
- **Disponibilité** : 99.5% uptime
- **Coût** : \< $75/mois infrastructure

## 🤝 Contribution

### Développement Local

```bash
# Fork le repo
git clone https://github.com/YOUR_USERNAME/web3-opps-tracker.git

# Branche feature
git checkout -b feature/nouveau-scraper

# Commits
git commit -m "✨ Add Layer3 scraper with ROI"

# Tests avant push
python -m pytest tests/
python scrapers/new_scraper.py
```

### Ajout de Nouveaux Scrapers

1. Hériter de `BaseScraper` dans `scrapers/`
2. Implémenter `fetch_data()` et `parse_data()`
3. Ajouter calcul ROI avec `calculate_roi()`
4. Tests unitaires dans `tests/`
5. Documentation dans README

## 📞 Support

- **Issues** : [GitHub Issues](https://github.com/ClaudelMbz/web3-opps-tracker/issues)
- **Discussions** : [GitHub Discussions](https://github.com/ClaudelMbz/web3-opps-tracker/discussions)
- **Email** : claudelmubenzem90@gmail.com

## 📄 Licence

MIT License - voir [LICENSE](LICENSE) pour plus de détails.

---

⭐ **Star le repo si ce projet vous aide !** ⭐

**Développé avec ❤️ par [Claudel Mubenzem](https://github.com/ClaudelMbz)**
