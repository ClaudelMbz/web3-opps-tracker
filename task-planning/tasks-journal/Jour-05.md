# 🗓️ JOUR 5 : Scrapers Secondaires (Twitter/RSS & Fallbacks)

## 🎯 Objectif Principal
Ajouter les sources Twitter/RSS et fallbacks (airdrops.io) pour compléter l'agrégation multi-sources et atteindre 100% de couverture des opportunités Web3.

---

## 📊 Résumé des Tâches

| ID | Tâche | Priorité | Durée | Status | Tags |
|---|---|---|---|---|---|
| T001 | Setup Twitter RSS | 🔥 CRITIQUE | 30min | ⏳ À faire | `🌐 WEB3` `📚 DOC` |
| T002 | Scraper RSS Feed | ⚡ HAUTE | 30min | ⏳ À faire | `💻 DEV` `🗄️ DATA` |
| T003 | Fallback airdrops.io | ⚡ HAUTE | 30min | ⏳ À faire | `💻 DEV` `🌐 WEB3` |
| T004 | Détection langue | 📋 MOYENNE | 30min | ⏳ À faire | `💻 DEV` `🧪 TEST` |
| T005 | Intégration pipeline | ⚡ HAUTE | 30min | ⏳ À faire | `💻 DEV` `🔧 DEBUG` |

---

# 🎯 TÂCHE T001 : Setup Twitter RSS

## 🎯 Métadonnées
- **ID** : T001
- **Priorité** : 🔥 CRITIQUE
- **Durée estimée** : 30min
- **Statut** : ⏳ À faire
- **Tags** : `🌐 WEB3` `📚 DOC` `⚙️ CONFIG`

## 📖 Contexte

### **Pourquoi** 
Twitter est une source majeure d'opportunités Web3 early-stage. Les comptes comme @AirdropAlert annoncent en avant-première les nouvelles opportunités.

### **Contexte** 
Utiliser feedparser pour récupérer les flux RSS de comptes Twitter spécialisés. Plus stable qu'une API Twitter payante.

### **Impact** 
Sans Twitter/RSS, on perd ~20% des opportunités précoces qui ne sont pas encore sur Galxe/Zealy.

## 🛠️ Exécution

### **Quoi faire**
Installer feedparser et créer la structure de base pour le scraper RSS.

### **Comment**
1. **Installer feedparser** :
   ```bash
   pip install feedparser langdetect
   ```
2. **Créer la structure** :
   ```bash
   touch scrapers/twitter_rss_scraper.py
   ```
3. **Implémenter la classe de base** :
   ```python
   import feedparser
   import requests
   from datetime import datetime
   from langdetect import detect

   class TwitterRSSScraper:
       def __init__(self):
           self.feeds = [
               "https://twitrss.me/twitter_user/?AirdropAlert",
               "https://twitrss.me/twitter_user/?AirdropNews",
               "https://twitrss.me/twitter_user/?CryptoAirdrops"
           ]
           
       def test_connection(self):
           """Test la connectivité aux feeds RSS"""
           for feed_url in self.feeds:
               try:
                   response = requests.head(feed_url, timeout=5)
                   print(f"✅ {feed_url}: {response.status_code}")
               except Exception as e:
                   print(f"❌ {feed_url}: {str(e)}")
   ```
4. **Tester la configuration** :
   ```bash
   python -c "
   from scrapers.twitter_rss_scraper import TwitterRSSScraper
   s = TwitterRSSScraper()
   s.test_connection()
   "
   ```

### **Outils requis**
- **feedparser** : Parsing des flux RSS
- **langdetect** : Détection de langue
- **requests** : Validation des URLs

### **Critères de succès**
- [ ] feedparser installé avec succès
- [ ] Classe TwitterRSSScraper créée
- [ ] URLs RSS configurées et testées
- [ ] Connectivité confirmée

## 🔗 Relations

### **Prérequis**
- Environnement Python fonctionnel
- Accès internet pour les flux RSS

### **Dépendants**
- T002 utilisera cette configuration
- Pipeline global (T005) dépend de ce setup

### **Références**
- User_Deepseek_Discuss.txt lignes 132-137
- Pattern des autres scrapers (Galxe, Zealy)

## 📋 Suivi

### **Prochaines étapes**
Implémenter la méthode de récupération des flux RSS.

### **Points de validation**
- Tous les feeds répondent correctement
- Pas de timeout sur les connexions
- Structure de classe cohérente

### **Risques identifiés**
- **Risque 1** : Service twitrss.me indisponible → **Mitigation** : Multiples feeds de backup
- **Risque 2** : Rate limiting → **Mitigation** : Délais entre requêtes

---

# 🎯 TÂCHE T002 : Scraper RSS Feed

## 🎯 Métadonnées
- **ID** : T002
- **Priorité** : ⚡ HAUTE
- **Durée estimée** : 30min
- **Statut** : ⏳ À faire
- **Tags** : `💻 DEV` `🗄️ DATA` `🐍 PYTHON`

## 📖 Contexte

### **Pourquoi** 
Il faut extraire et parser les données des flux RSS pour les convertir au format standardisé du projet.

### **Contexte** 
Les flux RSS contiennent titre, lien, date de publication. Il faut extraire les informations pertinentes et estimer les récompenses.

### **Impact** 
C'est le cœur du scraper RSS, sans cela pas de données exploitables.

## 🛠️ Exécution

### **Quoi faire**
Implémenter les méthodes fetch_opportunities() et parse_rss_data() pour récupérer et normaliser les données RSS.

### **Comment**
1. **Ajouter la méthode de fetch** :
   ```python
   def fetch_opportunities(self, max_entries=20):
       """Récupère les opportunités depuis les flux RSS"""
       all_entries = []
       
       for feed_url in self.feeds:
           try:
               print(f"📡 Scraping {feed_url}")
               feed = feedparser.parse(feed_url)
               
               for entry in feed.entries[:max_entries]:
                   all_entries.append({
                       'title': entry.title,
                       'link': entry.link,
                       'published': entry.get('published', ''),
                       'summary': entry.get('summary', ''),
                       'source_feed': feed_url
                   })
                   
           except Exception as e:
               print(f"❌ Erreur {feed_url}: {str(e)}")
               continue
       
       return all_entries
   ```
2. **Implémenter le parsing** :
   ```python
   def parse_rss_data(self, rss_entries):
       """Transforme les entrées RSS en format standard"""
       opportunities = []
       
       for entry in rss_entries:
           # Filtrage basique des opportunités
           title_lower = entry['title'].lower()
           if any(keyword in title_lower for keyword in ['airdrop', 'quest', 'task', 'reward']):
               
               # Estimation basique de la récompense
               estimated_reward = self._estimate_reward(entry['title'], entry.get('summary', ''))
               
               opportunities.append({
                   'id': f"rss_{hash(entry['link'])}",
                   'title': entry['title'],
                   'description': entry.get('summary', ''),
                   'reward': estimated_reward,
                   'estimated_time': 5,  # Valeur par défaut
                   'deadline': None,
                   'source': 'TwitterRSS',
                   'url': entry['link'],
                   'published_date': entry.get('published', '')
               })
       
       return opportunities
   ```
3. **Ajouter l'estimation de récompense** :
   ```python
   def _estimate_reward(self, title, summary):
       """Estime la récompense basée sur le titre et résumé"""
       text = f"{title} {summary}".lower()
       
       # Recherche de montants explicites
       import re
       amounts = re.findall(r'\$(\d+)', text)
       if amounts:
           return f"${amounts[0]}"
       
       # Estimation basée sur des mots-clés
       if 'major' in text or 'huge' in text:
           return "$50-100 estimated"
       elif 'medium' in text:
           return "$20-50 estimated"
       else:
           return "$5-20 estimated"
   ```

### **Outils requis**
- **feedparser** : Parsing RSS
- **re** : Expressions régulières pour extraction
- **hash()** : Génération d'IDs uniques

### **Critères de succès**
- [ ] fetch_opportunities() récupère des données
- [ ] parse_rss_data() normalise au format standard
- [ ] Estimation des récompenses fonctionnelle
- [ ] Filtrage des opportunités pertinentes

## 🔗 Relations

### **Prérequis**
- T001 (Setup) terminé avec succès
- Flux RSS accessibles et fonctionnels

### **Dépendants**
- T003 (Fallback) suivra le même pattern
- T005 (Intégration) utilisera ces données

### **Références**
- Format de données standardisé (Galxe/Zealy)
- Discussions DeepSeek lignes 134-136

## 📋 Suivi

### **Prochaines étapes**
Ajouter le scraper fallback airdrops.io.

### **Points de validation**
- Données extraites au bon format
- Estimation des récompenses cohérente
- Pas d'erreurs de parsing

### **Risques identifiés**
- **Risque 1** : Flux RSS vide → **Mitigation** : Vérification de la date
- **Risque 2** : Parsing d'HTML dans RSS → **Mitigation** : Nettoyage du texte

---

# 🎯 TÂCHE T003 : Fallback airdrops.io

## 🎯 Métadonnées
- **ID** : T003
- **Priorité** : ⚡ HAUTE
- **Durée estimée** : 30min
- **Statut** : ⏳ À faire
- **Tags** : `💻 DEV` `🌐 WEB3` `🗄️ DATA`

## 📖 Contexte

### **Pourquoi** 
airdrops.io est un site de référence pour les opportunités crypto. Ajouter cette source augmente la résilience et la couverture.

### **Contexte** 
Utiliser leur flux RSS public pour récupérer les annonces d'airdrops et opportunités.

### **Impact** 
Source de backup critique si Twitter/RSS principal échoue. Diversification des sources.

## 🛠️ Exécution

### **Quoi faire**
Étendre le scraper RSS pour inclure airdrops.io comme source fallback.

### **Comment**
1. **Ajouter la source fallback** :
   ```python
   # Dans __init__ de TwitterRSSScraper
   self.fallback_feeds = [
       "https://airdrops.io/feed/",
       "https://coinairdrops.com/feed/",
       "https://cryptoairdrops.com/feed/"
   ]
   ```
2. **Méthode de fallback** :
   ```python
   def fetch_fallback_opportunities(self, max_entries=15):
       """Récupère depuis les sources fallback"""
       fallback_entries = []
       
       for feed_url in self.fallback_feeds:
           try:
               print(f"🔄 Fallback scraping {feed_url}")
               feed = feedparser.parse(feed_url)
               
               for entry in feed.entries[:max_entries]:
                   fallback_entries.append({
                       'title': entry.title,
                       'link': entry.link,
                       'published': entry.get('published', ''),
                       'summary': entry.get('summary', ''),
                       'source_feed': feed_url,
                       'is_fallback': True
                   })
                   
           except Exception as e:
               print(f"⚠️ Fallback failed {feed_url}: {str(e)}")
               continue
       
       return fallback_entries
   ```
3. **Intégrer dans parse_rss_data** :
   ```python
   # Modifier parse_rss_data pour gérer les fallbacks
   def parse_rss_data(self, rss_entries):
       opportunities = []
       
       for entry in rss_entries:
           title_lower = entry['title'].lower()
           
           # Critères plus stricts pour les fallbacks
           if entry.get('is_fallback', False):
               keywords = ['airdrop', 'free', 'earn', 'reward', 'giveaway']
           else:
               keywords = ['airdrop', 'quest', 'task', 'reward']
           
           if any(keyword in title_lower for keyword in keywords):
               # ... reste du code de parsing
               source_name = 'AirdropsFallback' if entry.get('is_fallback') else 'TwitterRSS'
               
               opportunities.append({
                   # ... champs standards
                   'source': source_name,
                   # ... reste des champs
               })
       
       return opportunities
   ```

### **Outils requis**
- **feedparser** : Même outil que T002
- **Logic de fallback** : Gestion des erreurs

### **Critères de succès**
- [ ] Sources fallback configurées
- [ ] Méthode fetch_fallback_opportunities() fonctionnelle
- [ ] Intégration dans le parsing principal
- [ ] Distinction entre sources principales et fallback

## 🔗 Relations

### **Prérequis**
- T002 (Scraper RSS) fonctionnel
- Pattern de parsing établi

### **Dépendants**
- T005 (Intégration) utilisera toutes les sources
- Résilience globale du système

### **Références**
- User_Deepseek_Discuss.txt ligne 135 (fallback RSS)
- Architecture résiliente du projet

## 📋 Suivi

### **Prochaines étapes**
Ajouter la détection de langue pour filtrer le contenu anglais.

### **Points de validation**
- Sources fallback accessibles
- Données récupérées avec succès
- Pas de doublons avec sources principales

### **Risques identifiés**
- **Risque 1** : Tous les fallbacks échouent → **Mitigation** : Cache des dernières données
- **Risque 2** : Contenu de mauvaise qualité → **Mitigation** : Filtrage strict

---

# 🎯 TÂCHE T004 : Détection Langue

## 🎯 Métadonnées
- **ID** : T004
- **Priorité** : 📋 MOYENNE
- **Durée estimée** : 30min
- **Statut** : ⏳ À faire
- **Tags** : `💻 DEV` `🧪 TEST` `🗄️ DATA`

## 📖 Contexte

### **Pourquoi** 
Les flux RSS contiennent du contenu en plusieurs langues. Il faut filtrer pour ne garder que l'anglais.

### **Contexte** 
Utiliser langdetect pour identifier la langue et filtrer automatiquement le contenu non-anglais.

### **Impact** 
Améliore la qualité des données et réduit le bruit dans les opportunités détectées.

## 🛠️ Exécution

### **Quoi faire**
Ajouter la détection de langue avec filtrage automatique du contenu non-anglais.

### **Comment**
1. **Ajouter la méthode de détection** :
   ```python
   from langdetect import detect, DetectorFactory
   
   # Assurer des résultats reproductibles
   DetectorFactory.seed = 0
   
   def is_english_content(self, text):
       """Détecte si le contenu est en anglais"""
       try:
           # Nettoyer le texte
           clean_text = text.replace('\n', ' ').replace('\t', ' ')
           if len(clean_text.strip()) < 10:
               return True  # Trop court pour détecter, on garde
           
           detected_lang = detect(clean_text)
           return detected_lang == 'en'
           
       except Exception as e:
           print(f"⚠️ Language detection failed: {str(e)}")
           return True  # En cas d'erreur, on garde le contenu
   ```
2. **Intégrer dans parse_rss_data** :
   ```python
   def parse_rss_data(self, rss_entries):
       opportunities = []
       
       for entry in rss_entries:
           # Vérification de la langue
           full_text = f"{entry['title']} {entry.get('summary', '')}"
           if not self.is_english_content(full_text):
               print(f"🌐 Skipped non-English: {entry['title'][:50]}...")
               continue
           
           # ... reste de la logique de parsing
           
       print(f"🔍 Filtered {len(opportunities)} English opportunities")
       return opportunities
   ```
3. **Ajouter des tests de validation** :
   ```python
   def test_language_detection(self):
       """Test la détection de langue"""
       english_text = "Free airdrop for early adopters"
       french_text = "Airdrop gratuit pour les premiers utilisateurs"
       spanish_text = "Airdrop gratis para los primeros usuarios"
       
       assert self.is_english_content(english_text) == True
       assert self.is_english_content(french_text) == False
       assert self.is_english_content(spanish_text) == False
       
       print("✅ Language detection tests passed")
   ```

### **Outils requis**
- **langdetect** : Détection automatique de langue
- **String processing** : Nettoyage du texte

### **Critères de succès**
- [ ] Méthode is_english_content() fonctionnelle
- [ ] Intégration dans le pipeline de parsing
- [ ] Tests de validation qui passent
- [ ] Filtrage efficace du contenu non-anglais

## 🔗 Relations

### **Prérequis**
- T002 et T003 terminés
- langdetect installé (fait dans T001)

### **Dépendants**
- Qualité des données pour le pipeline global
- ROI calculations plus précis (Jour 6)

### **Références**
- User_Deepseek_Discuss.txt ligne 136 (filtrage langue)
- Standards de qualité des données

## 📋 Suivi

### **Prochaines étapes**
Intégrer tous les scrapers RSS dans le pipeline principal.

### **Points de validation**
- Détection précise de l'anglais
- Pas de faux positifs/négatifs
- Performance acceptable

### **Risques identifiés**
- **Risque 1** : Faux négatifs sur l'anglais → **Mitigation** : Seuil de confiance ajustable
- **Risque 2** : Performance lente → **Mitigation** : Cache des résultats

---

# 🎯 TÂCHE T005 : Intégration Pipeline

## 🎯 Métadonnées
- **ID** : T005
- **Priorité** : ⚡ HAUTE
- **Durée estimée** : 30min
- **Statut** : ⏳ À faire
- **Tags** : `💻 DEV` `🔧 DEBUG` `🌐 WEB3`

## 📖 Contexte

### **Pourquoi** 
Il faut intégrer le scraper RSS dans le pipeline global pour avoir 3 sources complètes : Galxe + Zealy + RSS.

### **Contexte** 
Modifier main.py pour orchestrer les trois scrapers et créer un fichier de sortie unifié.

### **Impact** 
Atteint l'objectif de couverture complète des opportunités Web3 quotidiennes.

## 🛠️ Exécution

### **Quoi faire**
Mettre à jour main.py pour inclure le scraper RSS et fusionner toutes les données.

### **Comment**
1. **Mettre à jour main.py** :
   ```python
   from scrapers.galxe_scraper import GalxeScraper
   from scrapers.zealy_scraper import ZealyScraper
   from scrapers.twitter_rss_scraper import TwitterRSSScraper
   import json
   import time

   def run_full_pipeline():
       print("🚀 Démarrage pipeline complet (3 sources)")
       
       # Initialiser tous les scrapers
       scrapers = {
           'galxe': GalxeScraper(),
           'zealy': ZealyScraper(),
           'rss': TwitterRSSScraper()
       }
       
       all_opportunities = []
       stats = {}
       
       # Scraping Galxe
       try:
           print("📊 Scraping Galxe...")
           galxe_data = scrapers['galxe'].fetch_quests(limit=50)
           if galxe_data:
               galxe_ops = scrapers['galxe'].parse_quests(galxe_data)
               all_opportunities.extend(galxe_ops)
               stats['galxe'] = len(galxe_ops)
               print(f"✅ {len(galxe_ops)} opportunités Galxe")
       except Exception as e:
           print(f"❌ Galxe failed: {str(e)}")
           stats['galxe'] = 0
       
       # Scraping Zealy
       try:
           print("📊 Scraping Zealy...")
           zealy_data = scrapers['zealy'].fetch_quests(limit=50)
           if zealy_data:
               zealy_ops = scrapers['zealy'].parse_quests(zealy_data)
               all_opportunities.extend(zealy_ops)
               stats['zealy'] = len(zealy_ops)
               print(f"✅ {len(zealy_ops)} opportunités Zealy")
       except Exception as e:
           print(f"❌ Zealy failed: {str(e)}")
           stats['zealy'] = 0
       
       # Scraping RSS (principal + fallback)
       try:
           print("📊 Scraping RSS feeds...")
           rss_entries = scrapers['rss'].fetch_opportunities(max_entries=30)
           fallback_entries = scrapers['rss'].fetch_fallback_opportunities(max_entries=20)
           
           all_rss_entries = rss_entries + fallback_entries
           rss_ops = scrapers['rss'].parse_rss_data(all_rss_entries)
           all_opportunities.extend(rss_ops)
           stats['rss'] = len(rss_ops)
           print(f"✅ {len(rss_ops)} opportunités RSS")
       except Exception as e:
           print(f"❌ RSS failed: {str(e)}")
           stats['rss'] = 0
       
       # Sauvegarde avec métadonnées
       timestamp = int(time.time())
       result = {
           'timestamp': timestamp,
           'sources': stats,
           'total_opportunities': len(all_opportunities),
           'opportunities': all_opportunities
       }
       
       filename = f"data/full_pipeline_{timestamp}.json"
       with open(filename, "w") as f:
           json.dump(result, f, indent=2)
       
       print(f"💾 Pipeline terminé: {len(all_opportunities)} opportunités → {filename}")
       print(f"📊 Stats: Galxe({stats.get('galxe', 0)}) + Zealy({stats.get('zealy', 0)}) + RSS({stats.get('rss', 0)})")

   if __name__ == "__main__":
       run_full_pipeline()
   ```
2. **Test de l'intégration complète** :
   ```bash
   python main.py
   ```
3. **Validation des données** :
   ```bash
   # Vérifier la diversité des sources
   jq '.opportunities[] | .source' data/full_pipeline_*.json | sort | uniq -c
   
   # Vérifier les stats
   jq '.sources' data/full_pipeline_*.json
   ```

### **Outils requis**
- **JSON** : Sauvegarde des données
- **jq** : Validation (optionnel)
- **Exception handling** : Résilience

### **Critères de succès**
- [ ] Pipeline exécute sans crash
- [ ] Données des 3 sources présentes
- [ ] Métadonnées et stats correctes
- [ ] Gestion d'erreurs par source

## 🔗 Relations

### **Prérequis**
- T001-T004 terminés avec succès
- Galxe et Zealy scrapers fonctionnels

### **Dépendants**
- Calcul ROI (Jour 6) utilisera ces données complètes
- Dashboard (Jour 9) affichera ces statistiques

### **Références**
- Architecture pipeline final du projet
- User_Deepseek_Discuss.txt lignes 137-140

## 📋 Suivi

### **Prochaines étapes**
Jour 6 : Calcul ROI et déduplication sur les données multi-sources.

### **Points de validation**
- Toutes les sources exécutées
- Données cohérentes et complètes
- Statistiques correctes

### **Risques identifiés**
- **Risque 1** : Une source bloque tout → **Mitigation** : Try/catch par source
- **Risque 2** : Données incohérentes → **Mitigation** : Validation des formats

---

## 📈 Métriques de la Journée

### **Planification**
- **Nombre de tâches** : 5
- **Durée totale estimée** : 2h30
- **Priorités** : 1 critique, 3 hautes, 1 moyenne

### **Coverage Goal**
- **Sources ajoutées** : 3+ (Twitter RSS + fallbacks)
- **Coverage estimée** : 90%+ des opportunités Web3
- **Résilience** : Fallbacks multiples

---

## 🔄 Instructions Spéciales pour l'Agent

### **Ordre d'exécution recommandé**
1. T001 (Setup RSS) - Infrastructure critique
2. T002 (Scraper RSS) - Core functionality 
3. T003 (Fallbacks) - Résilience
4. T004 (Language detection) - Qualité des données
5. T005 (Integration) - Pipeline complet

### **Points d'attention**
- ⚠️ Tester chaque feed RSS individuellement
- ⚠️ Vérifier la détection de langue sur différents exemples
- ⚠️ S'assurer que les fallbacks fonctionnent en cas d'échec principal

### **Ressources utiles**
- Documentation feedparser : https://feedparser.readthedocs.io/
- langdetect examples : https://pypi.org/project/langdetect/
- Flux RSS de test disponibles

---

## 🎯 Objectifs de Validation

À la fin de cette journée, l'agent doit avoir :
- ✅ Pipeline 3-sources fonctionnel (Galxe + Zealy + RSS)
- ✅ Fallbacks configurés pour la résilience  
- ✅ Filtrage par langue (anglais uniquement)
- ✅ Gestion d'erreurs robuste
- ✅ Couverture estimée >90% des opportunités Web3

---

*Créé le : 22 juillet 2025*  
*Basé sur : User_Deepseek_Discuss.txt lignes 132-140*  
*Prochaine étape : Jour 6 - Processing & ROI (Calcul ROI, déduplication)*
