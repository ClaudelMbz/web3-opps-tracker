# 🔧 Guide de Configuration Notion - Jour 7

## 🎯 Objectif
Configurer Notion comme outil de collaboration et documentation pour le Web3 Opportunities Tracker.

## 📋 Étapes de Configuration

### 1. **Créer une Intégration Notion**

1. Aller sur [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Cliquer sur **"Create new integration"**
3. Remplir les informations :
   - **Name** : `Web3-Opps-Tracker`
   - **Logo** : (Optionnel)
   - **Associated workspace** : Sélectionner votre workspace
4. Cliquer **"Submit"**
5. **IMPORTANT** : Copier le **"Internal Integration Token"** (commence par `ntn_`)

### 2. **Configuration des Variables d'Environnement**

Ajouter dans votre fichier `.env` :

```env
# Notion Configuration
NOTION_TOKEN=votre_token_integration_ici
NOTION_DATABASE_ID=votre_database_id_ici
```

## 🧪 Test de Configuration

Exécuter le test :
```bash
python storage/notion_integration.py
```

**Résultat attendu :**
- ✅ Connexion Notion réussie
- ✅ Test d'ajout d'une opportunité
- ✅ Vérification dans votre base Notion

---

💡 **Jour 7 validé avec 3/3 services opérationnels !**
