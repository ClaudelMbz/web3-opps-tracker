# Setup Environment - Web3 Opps Tracker

Ce fichier contient toutes les commandes nécessaires pour restaurer rapidement l'environnement de développement du projet Web3-Opps-Tracker.

## ⚠️ Prérequis
- Python 3.12+ installé
- Git configuré
- Vault binaire disponible (téléchargé depuis HashiCorp)

## 🚀 Commands de Setup Rapide

### 1. Navigation vers le projet
```powershell
cd D:\Web3-Opps-Tracker
```

### 2. Activation de l'environnement virtuel
```powershell
# Si la venv existe déjà
venv\Scripts\Activate.ps1

# Si la venv n'existe pas, la créer :
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Installation des dépendances
```powershell
pip install -r requirements.txt
```

### 4. Démarrage de Vault en mode développement
```powershell
# Démarrer Vault (dans un terminal séparé)
vault server -dev -dev-root-token-id="web3root"
```

### 5. Configuration des variables d'environnement Vault
```powershell
# Dans un nouveau terminal
$env:VAULT_ADDR="http://127.0.0.1:8200"
$env:VAULT_TOKEN="web3root"
```

### 6. Configuration du moteur KV dans Vault
```powershell
# Activer le moteur KV v2
vault auth -method=token token="web3root"
vault secrets enable -version=2 kv
```

### 7. Injection des secrets dans Vault
```powershell
# Secrets Zealy
vault kv put kv/zealy api_key="votre_clé_zealy_ici"

# Secrets Galxe
vault kv put kv/galxe api_key="votre_clé_galxe_ici"

# Secrets ScraperAPI pour Galxe
vault kv put kv/scraperapi api_key="votre_clé_scraperapi_ici"
```

### 8. Test de fonctionnement des scrapers
```powershell
# Test Zealy Scraper
python -m pytest tests/test_zealy_scraper.py -v

# Test Galxe Scraper (si les clés API sont configurées)
python src/scrapers/galxe_scraper.py

# Test Zealy Scraper direct
python src/scrapers/zealy_scraper.py
```

### 9. Vérification de l'état du projet
```powershell
# Vérifier les derniers commits
git log --oneline -5

# Vérifier l'état git
git status

# Vérifier la structure des fichiers essentiels
ls src/scrapers/
ls tests/
ls daily_logs/
```

## 🔧 Commandes de Debug/Maintenance

### Vérifier la connexion Vault
```powershell
vault status
vault kv get kv/zealy
```

### Réinstaller les dépendances si nécessaire
```powershell
pip install --upgrade -r requirements.txt
```

### Nettoyer et recréer la venv si problème
```powershell
Remove-Item -Recurse -Force venv
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 📋 Checklist de Vérification

- [ ] Python 3.12+ activé dans venv
- [ ] Toutes les dépendances installées
- [ ] Vault démarré et accessible sur http://127.0.0.1:8200
- [ ] Variables d'environnement VAULT_ADDR et VAULT_TOKEN configurées
- [ ] Moteur KV v2 activé dans Vault
- [ ] Secrets API injectés dans Vault (zealy, galxe, scraperapi)
- [ ] Tests Zealy passent avec succès
- [ ] Scrapers fonctionnent sans erreur de connexion Vault

## 🎯 Résultat Attendu

Après exécution de ces commandes, vous devriez pouvoir :
1. Exécuter `python src/scrapers/zealy_scraper.py` sans erreur
2. Voir les données Zealy récupérées et parsées
3. Lancer les tests avec `pytest tests/` et voir tous les tests passer
4. Continuer le développement du jour suivant directement

## 📝 Notes Importantes

- Le token Vault en développement est `"web3root"` (avec guillemets)
- Le serveur Vault dev doit être redémarré à chaque session
- Les secrets API doivent être réinjectés si Vault est redémarré
- La venv doit être réactivée à chaque nouvelle session terminal

---
*Dernière mise à jour : Jour 4 - Scrapers Zealy et Galxe opérationnels*
