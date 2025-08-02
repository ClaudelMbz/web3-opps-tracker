# main_py312.py - Pipeline de scraping consolidé pour Python 3.12
import sys
import os
import time
import json
from datetime import datetime
import hashlib

# Ajouter le chemin des modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'scrapers')))

try:
    from galxe_scraper_py312 import GalxeScraperPy312
    GALXE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Galxe scraper non disponible: {e}")
    GALXE_AVAILABLE = False

# Tentative d'import du scraper Zealy (si disponible)
try:
    from zealy_scraper import ZealyScraper
    ZEALY_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Zealy scraper non disponible: {e}")
    ZEALY_AVAILABLE = False

# Tentative d'import du scraper Layer3 (si disponible)
try:
    from layer3_scraper import Layer3Scraper
    LAYER3_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Layer3 scraper non disponible: {e}")
    LAYER3_AVAILABLE = False

# Tentative d'import du scraper RSS/Twitter (si disponible)
try:
    from twitter_rss_scraper import TwitterRSSScraper
    RSS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  RSS scraper non disponible: {e}")
    RSS_AVAILABLE = False

def run_pipeline():
    """
    Exécute le pipeline complet de scraping pour toutes les sources,
    consolide les données et les sauvegarde.
    """
    print(f"🚀 Démarrage du pipeline de scraping consolidé Python 3.12 - {datetime.now().isoformat()}")
    all_opportunities = []

    # --- 1. Scraper Galxe ---
    if GALXE_AVAILABLE:
        try:
            print("\n--- Source: Galxe ---")
            galxe_scraper = GalxeScraperPy312()
            galxe_quests = galxe_scraper.scrape_galxe_campaigns(pages=1)
            if galxe_quests:
                all_opportunities.extend(galxe_quests)
                print(f"✅ Galxe: {len(galxe_quests)} opportunités récupérées.")
            else:
                print("⚠️ Galxe: Aucune opportunité récupérée.")
        except Exception as e:
            print(f"❌ Erreur lors du scraping de Galxe: {e}")
    else:
        print("\n--- Source: Galxe ---")
        print("❌ Scraper Galxe non disponible")

    # --- 2. Scraper Zealy ---
    if ZEALY_AVAILABLE:
        try:
            print("\n--- Source: Zealy ---")
            zealy_scraper = ZealyScraper()
            zealy_raw_data = zealy_scraper.fetch_quests(limit=100)
            zealy_quests = zealy_scraper.parse_quests(zealy_raw_data)
            if zealy_quests:
                all_opportunities.extend(zealy_quests)
                print(f"✅ Zealy: {len(zealy_quests)} opportunités récupérées.")
            else:
                print("⚠️ Zealy: Aucune opportunité récupérée.")
        except Exception as e:
            print(f"❌ Erreur lors du scraping de Zealy: {e}")
    else:
        print("\n--- Source: Zealy ---")
        print("❌ Scraper Zealy non disponible (dépendances manquantes)")

    # --- 3. Scraper Layer3 ---
    if LAYER3_AVAILABLE:
        try:
            print("\n--- Source: Layer3 ---")
            layer3_scraper = Layer3Scraper()
            layer3_quests = layer3_scraper.fetch_all_campaigns(max_pages=1)
            if layer3_quests:
                all_opportunities.extend(layer3_quests)
                print(f"✅ Layer3: {len(layer3_quests)} opportunités récupérées.")
            else:
                print("⚠️ Layer3: Aucune opportunité récupérée.")
        except Exception as e:
            print(f"❌ Erreur lors du scraping de Layer3: {e}")
    else:
        print("\n--- Source: Layer3 ---")
        print("❌ Scraper Layer3 non disponible (dépendances manquantes)")

    # --- 4. Scraper RSS/Twitter ---
    if RSS_AVAILABLE:
        try:
            print("\n--- Source: RSS/Twitter ---")
            rss_scraper = TwitterRSSScraper()
            
            # Récupération des flux principaux
            rss_entries = rss_scraper.fetch_opportunities(max_entries=30)
            
            # Récupération des fallbacks
            fallback_entries = rss_scraper.fetch_fallback_opportunities(max_entries=20)
            
            # Combinaison des deux sources
            all_rss_entries = rss_entries + fallback_entries
            
            if all_rss_entries:
                rss_opportunities = rss_scraper.parse_rss_data(all_rss_entries)
                all_opportunities.extend(rss_opportunities)
                print(f"✅ RSS: {len(rss_opportunities)} opportunités récupérées.")
            else:
                print("⚠️ RSS: Aucune opportunité récupérée.")
        except Exception as e:
            print(f"❌ Erreur lors du scraping RSS: {e}")
    else:
        print("\n--- Source: RSS/Twitter ---")
        print("❌ Scraper RSS non disponible (dépendances manquantes)")

    # --- 4. Traitement et Sauvegarde ---
    if not all_opportunities:
        print("\n⚠️ Aucune opportunité n'a été récupérée au total. Fin du pipeline.")
        return

    # Ajout d'un hash unique pour la déduplication
    processed_opportunities = []
    for opp in all_opportunities:
        # Créer une chaîne de caractères unique pour chaque opportunité
        unique_string = f"{opp.get('source')}-{opp.get('id', '')}-{opp.get('title')}"
        opp['hash'] = hashlib.md5(unique_string.encode()).hexdigest()
        processed_opportunities.append(opp)

    # Sauvegarder les données consolidées
    timestamp = int(time.time())
    output_dir = "data/opportunities"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    filename = f"{output_dir}/opportunities_{timestamp}.json"
    
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(processed_opportunities, f, indent=2, ensure_ascii=False)
    
    # Statistiques détaillées
    galxe_count = len([opp for opp in processed_opportunities if opp.get('source') == 'Galxe'])
    zealy_count = len([opp for opp in processed_opportunities if opp.get('source') == 'Zealy'])
    rss_count = len([opp for opp in processed_opportunities if opp.get('source') in ['TwitterRSS', 'AirdropsFallback']])
    
    print(f"\n🎉 Pipeline terminé avec succès!")
    print(f"📊 Galxe: {galxe_count} opportunités")
    print(f"📊 Zealy: {zealy_count} opportunités")
    print(f"📊 RSS/Twitter: {rss_count} opportunités")
    print(f"💾 {len(processed_opportunities)} opportunités totales sauvegardées dans {filename}")
    
    # Afficher quelques exemples
    if processed_opportunities:
        print(f"\n🎯 Exemples d'opportunités récupérées:")
        for i, opp in enumerate(processed_opportunities[:5]):
            title = opp.get('title', 'Sans titre')[:60]
            source = opp.get('source', 'Inconnu')
            print(f"  {i+1}. [{source}] {title}...")

def run_single_test():
    """Test rapide avec une seule page"""
    print("🧪 Test rapide - Une page seulement\n")
    
    if GALXE_AVAILABLE:
        print("--- Test Galxe ---")
        try:
            galxe_scraper = GalxeScraperPy312()
            quests = galxe_scraper.scrape_page_with_playwright("https://galxe.com/explore?page=1")
            print(f"✅ Test réussi: {len(quests)} quêtes trouvées")
            
            if quests:
                print("🎯 Premières quêtes:")
                for i, quest in enumerate(quests[:3]):
                    print(f"  {i+1}. {quest['title'][:50]}...")
                    print(f"     {quest['link']}")
        except Exception as e:
            print(f"❌ Test échoué: {e}")
    else:
        print("❌ Galxe scraper non disponible")

if __name__ == "__main__":
    try:
        # Vérifier les arguments
        if len(sys.argv) > 1 and sys.argv[1] == "--test":
            run_single_test()
        else:
            run_pipeline()
    except KeyboardInterrupt:
        print("\n🛑 Pipeline arrêté par l'utilisateur.")
    except Exception as e:
        print(f"\n❌ Erreur critique: {e}")
        import traceback
        traceback.print_exc()
