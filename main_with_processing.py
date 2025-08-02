# main_with_processing.py - Pipeline avec processing ROI et déduplication intégrés
import sys
import os
import time
import json
from datetime import datetime
import hashlib
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajouter le chemin des modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'scrapers')))

from scrapers.galxe_scraper import GalxeScraperEnhanced
from scrapers.zealy_scraper import ZealyScraper
from scrapers.twitter_rss_scraper import TwitterRSSScraper
from scrapers.layer3_scraper import Layer3Scraper
from processing.pipeline import process_opportunities

def run_pipeline_with_processing():
    """
    Exécute le pipeline complet avec processing ROI et déduplication.
    """
    print(f"🚀 Démarrage du pipeline avec processing - {datetime.now().isoformat()}")
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

    # --- 4. Scraper RSS/Twitter ---
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

    # --- 5. Processing avec ROI et déduplication ---
    if not all_opportunities:
        print("\n⚠️ Aucune opportunité n'a été récupérée au total. Fin du pipeline.")
        return

    # Traitement avec le pipeline de processing Jour 6
    result = process_opportunities(all_opportunities, min_roi=2.0)

    # --- 6. Sauvegarde avec métadonnées complètes ---
    timestamp = int(time.time())
    output_dir = "data/opportunities"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    filename = f"{output_dir}/processed_opportunities_{timestamp}.json"
    
    # Ajouter métadonnées temporelles
    final_result = {
        'timestamp': timestamp,
        'datetime': datetime.now().isoformat(),
        'pipeline_version': 'Jour_6_Processing',
        'processing_stats': result['stats'],
        'categories': result['categories'],
        'processed_opportunities': result['processed_opportunities']
    }
    
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(final_result, f, indent=2, ensure_ascii=False)
        
    # --- 7. Statistiques détaillées ---
    processed_ops = result['processed_opportunities']
    stats = result['stats']
    categories = result['categories']
    
    print(f"\n🎉 Pipeline avec processing terminé avec succès!")
    print(f"📊 Statistiques de processing:")
    print(f"   📥 Opportunités brutes: {stats['total_raw']}")
    print(f"   🔄 Après déduplication: {stats['after_deduplication']}")
    print(f"   ⚡ Après filtrage ROI: {stats['after_roi_filter']}")
    print(f"   💎 ROI moyen: ${stats['avg_roi']}/min")
    print(f"   🚀 ROI maximum: ${stats['max_roi']}/min")
    
    print(f"\n🎯 Catégorisation par ROI:")
    print(f"   🔥 Haute (≥$5/min): {len(categories['high'])} opportunités")
    print(f"   ⚡ Moyenne ($2-5/min): {len(categories['medium'])} opportunités")
    print(f"   📋 Faible (<$2/min): {len(categories['low'])} opportunités")
    
    print(f"\n💾 {len(processed_ops)} opportunités finales sauvegardées dans {filename}")
    
    # Afficher quelques exemples des meilleures opportunités
    if processed_ops:
        print(f"\n🏆 Top 5 opportunités par ROI:")
        for i, opp in enumerate(processed_ops[:5]):
            title = opp.get('title', 'Sans titre')[:50]
            source = opp.get('source', 'Inconnu')
            roi = opp.get('roi', 0)
            print(f"  {i+1}. [{source}] {title}... (${roi:.2f}/min)")

def run_test_processing():
    """Test rapide du système de processing."""
    print("🧪 Test du système de processing\n")
    
    # Données de test
    test_opportunities = [
        {
            'title': 'High ROI Airdrop',
            'reward': '100 USD',
            'time_est_min': 10,
            'source': 'Test',
            'url': 'https://test1.com'
        },
        {
            'title': 'Medium ROI Quest',  
            'reward': '500 XP',
            'time_est_min': 5,
            'source': 'Test',
            'url': 'https://test2.com'
        },
        {
            'title': 'Low ROI Task',
            'reward': '10 POINTS',
            'time_est_min': 20,
            'source': 'Test', 
            'url': 'https://test3.com'
        },
        # Doublon pour tester la déduplication
        {
            'title': 'High ROI Airdrop',
            'reward': '100 USD',
            'time_est_min': 10,
            'source': 'Test',
            'url': 'https://test1.com'
        }
    ]
    
    result = process_opportunities(test_opportunities, min_roi=1.0)
    
    print(f"\n✅ Test terminé:")
    print(f"📊 {result['stats']['after_roi_filter']} opportunités après processing")
    print(f"💎 ROI moyen: ${result['stats']['avg_roi']}/min")

if __name__ == "__main__":
    try:
        # Vérifier les arguments
        if len(sys.argv) > 1 and sys.argv[1] == "--test":
            run_test_processing()
        else:
            run_pipeline_with_processing()
    except KeyboardInterrupt:
        print("\n🛑 Pipeline arrêté par l'utilisateur.")
    except Exception as e:
        print(f"\n❌ Erreur critique: {e}")
        import traceback
        traceback.print_exc()
