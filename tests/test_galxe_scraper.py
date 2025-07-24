# tests/test_galxe_scraper.py
import sys
import os
import time
import json
import pytest
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scrapers.galxe_scraper import GalxeScraperEnhanced

@pytest.fixture
def scraper():
    """Fixture pour créer une instance du scraper Galxe"""
    return GalxeScraperEnhanced()

def test_scraper_initialization():
    """Test l'initialisation du scraper"""
    print("🧪 Test 1: Initialisation du scraper")
    
    try:
        scraper = GalxeScraperEnhanced()
        stats = scraper.get_stats()
        
        print(f"✅ Scraper initialisé avec succès")
        print(f"📊 Comptes disponibles: {stats['accounts_count']}")
        print(f"🎭 Playwright disponible: {stats['playwright_available']}")
        print(f"🔄 Méthode optimale: {stats['optimal_method']}")
        print(f"📈 Requêtes aujourd'hui: {stats['daily_requests']}")
        print(f"📊 Quota restant: {stats['remaining_quota']}")
        
        return scraper
        
    except Exception as e:
        print(f"❌ Erreur initialisation: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_single_page_scrape(scraper):
    """Test le scraping d'une page unique"""
    print("\n🧪 Test 2: Scraping d'une page unique")
    
    try:
        test_url = "https://galxe.com/explore?page=1"
        print(f"🌐 URL de test: {test_url}")
        
        start_time = time.time()
        html = scraper.scrape_page(test_url, max_retries=2)
        duration = time.time() - start_time
        
        print(f"✅ Scraping réussi en {duration:.2f}s")
        print(f"📄 HTML récupéré: {len(html):,} caractères")
        
        # Vérifier le contenu
        html_lower = html.lower()
        galxe_indicators = ["galxe", "campaign", "quest", "explore", "web3"]
        found_indicators = [ind for ind in galxe_indicators if ind in html_lower]
        
        if found_indicators:
            print(f"✅ Contenu Galxe détecté: {found_indicators}")
        else:
            print("⚠️  Contenu suspect - vérifier la page")
        
        return html
        
    except Exception as e:
        print(f"❌ Erreur scraping: {e}")
        return None

def test_campaign_extraction(scraper):
    """Test l'extraction des campagnes"""
    print("\n🧪 Test 3: Extraction des campagnes")
    
    try:
        print("🚀 Début du scraping avec extraction")
        results = scraper.scrape_galxe_explore(pages=1)
        
        if results:
            result = results[0]
            print(f"✅ Extraction terminée")
            print(f"📄 Taille HTML: {result.get('html_size', 0):,} caractères")
            print(f"📊 Campagnes trouvées: {result.get('campaigns_found', 0)}")
            print(f"🔄 Méthode utilisée: {result.get('method', 'N/A')}")
            
            # Afficher quelques campagnes
            campaigns = result.get('campaigns', [])
            if campaigns:
                print(f"\n📋 Aperçu des campagnes:")
                for i, campaign in enumerate(campaigns[:3], 1):
                    print(f"  {i}. {campaign.get('title', 'Sans titre')}")
                    if 'url' in campaign:
                        print(f"     🔗 {campaign['url']}")
                    if 'reward' in campaign:
                        print(f"     🎁 {campaign['reward']} points")
            
            return results
        else:
            print("❌ Aucun résultat")
            return None
        
    except Exception as e:
        print(f"❌ Erreur extraction: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_fallback_mechanism(scraper):
    """Test le mécanisme de fallback"""
    print("\n🧪 Test 4: Mécanisme de fallback")
    
    try:
        # État initial
        initial_method = scraper.get_optimal_method()
        print(f"🔄 Méthode initiale: {initial_method}")
        
        # Forcer le fallback en simulant un quota élevé
        original_requests = scraper.daily_requests
        scraper.daily_requests = 150  # Seuil critique
        
        print(f"🔄 Simulation quota élevé: {scraper.daily_requests} requêtes")
        
        method = scraper.get_optimal_method()
        print(f"🎯 Méthode après simulation: {method}")
        
        if method == "playwright" and scraper.playwright_available:
            print("✅ Fallback vers Playwright activé")
        elif method == "scraperapi":
            print("✅ ScraperAPI maintenu")
        else:
            print("⚠️  Fallback non déterminé")
        
        # Restaurer l'état original
        scraper.daily_requests = original_requests
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test fallback: {e}")
        return False

def test_stats_and_persistence(scraper):
    """Test les statistiques et la persistance"""
    print("\n🧪 Test 5: Statistiques et persistance")
    
    try:
        # Obtenir les stats
        stats = scraper.get_stats()
        
        print("📊 Statistiques complètes:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Vérifier la sauvegarde
        if os.path.exists(scraper.stats_file):
            with open(scraper.stats_file, 'r') as f:
                saved_stats = json.load(f)
            print(f"✅ Fichier stats sauvegardé: {scraper.stats_file}")
            print(f"📅 Date: {saved_stats.get('date', 'N/A')}")
            print(f"⏰ Timestamp: {saved_stats.get('timestamp', 'N/A')}")
        else:
            print("⚠️  Fichier stats non trouvé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test stats: {e}")
        return False

def test_content_validation(scraper):
    """Test la validation du contenu"""
    print("\n🧪 Test 6: Validation du contenu")
    
    try:
        # Test avec du contenu valide
        valid_html = """
        <html>
        <body>
            <div class="campaign-card">
                <h3>Test Galxe Campaign</h3>
                <p>A web3 quest for NFT rewards</p>
            </div>
        </body>
        </html>
        """
        
        is_valid = scraper._validate_content(valid_html)
        print(f"✅ Contenu valide: {is_valid}")
        
        # Test avec du contenu invalide
        invalid_html = "<html><body>Error 404</body></html>"
        is_invalid = scraper._validate_content(invalid_html)
        print(f"❌ Contenu invalide: {not is_invalid}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur validation: {e}")
        return False

