# main.py - Pipeline de scraping consolidé
import sys
import os
import time
import json
from datetime import datetime
import schedule
import hashlib
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Ajouter le chemin des modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'scrapers')))

from scrapers.galxe_scraper import GalxeScraperEnhanced
from scrapers.zealy_scraper import ZealyScraper
from scrapers.twitter_rss_scraper import TwitterRSSScraper
from scrapers.layer3_scraper import Layer3Scraper

def run_pipeline():
    """
    Exécute le pipeline complet de scraping pour toutes les sources,
    consolide les données et les sauvegarde.
    """
    print(f"🚀 Démarrage du pipeline de scraping consolidé - {datetime.now().isoformat()}")
    all_opportunities = []

    # --- 1. Scraper Galxe ---
    try:
        print("\n--- Source: Galxe ---")
        galxe_scraper = GalxeScraperEnhanced()
        galxe_quests = galxe_scraper.scrape_galxe_campaigns(pages=1)
        if galxe_quests:
            all_opportunities.extend(galxe_quests)
            print(f"✅ Galxe: {len(galxe_quests)} opportunités récupérées.")
        else:
            print("⚠️ Galxe: Aucune opportunité récupérée.")
    except Exception as e:
        print(f"❌ Erreur lors du scraping de Galxe: {e}")

    # --- 2. Scraper Zealy ---
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

    # --- 3. Scraper Layer3 ---
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

    # --- 4. Traitement et Sauvegarde ---
    if not all_opportunities:
        print("\n⚠️ Aucune opportunité n'a été récupérée au total. Fin du pipeline.")
        return

    # Ajout d'un hash unique pour la déduplication
    processed_opportunities = []
    for opp in all_opportunities:
        # Créer une chaîne de caractères unique pour chaque opportunité
        unique_string = f"{opp.get('source')}-{opp.get('id')}-{opp.get('title')}"
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
        
    print(f"\n🎉 Pipeline terminé avec succès!")
    print(f"💾 {len(processed_opportunities)} opportunités totales sauvegardées dans {filename}")

def schedule_jobs():
    """Planifie l'exécution régulière du pipeline."""
    print("⚙️ Planification du pipeline toutes les 2 heures.")
    run_pipeline()  # Exécute une fois au démarrage
    
    schedule.every(2).hours.do(run_pipeline)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    try:
        schedule_jobs()
    except KeyboardInterrupt:
        print("\n🛑 Planificateur arrêté par l'utilisateur.")
