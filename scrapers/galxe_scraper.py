# scrapers/galxe_scraper_enhanced.py
import requests
from datetime import datetime
from diskcache import Cache
from bs4 import BeautifulSoup

import time
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from galxe_requests import ScraperAPIBalancer

# Cache disque pour éviter les requêtes répétées
cache = Cache("galxe_cache", expire=3600)

class GalxeScraperEnhanced:
    def __init__(self):
        self.balancer = ScraperAPIBalancer()
        self.last_used_account = None
        self.session = requests.Session()
        self.daily_requests = 0
        self.fallback_active = False
        self.stats_file = "scraper_stats.json"
        self._load_daily_stats()
        
    def _load_daily_stats(self):
        """Charger les statistiques du jour"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    stats = json.load(f)
                    if stats.get('date') == datetime.now().strftime('%Y-%m-%d'):
                        self.daily_requests = stats.get('total_requests', 0)
                        self.fallback_active = stats.get('fallback_active', False)
        except Exception as e:
            print(f"⚠️  Erreur chargement stats: {e}")
    
    def _save_daily_stats(self):
        """Sauvegarder les statistiques"""
        try:
            stats = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'total_requests': self.daily_requests,
                'fallback_active': self.fallback_active,
                'last_update': datetime.now().isoformat()
            }
            with open(self.stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
        except Exception as e:
            print(f"⚠️  Erreur sauvegarde stats: {e}")
    
    def get_scraping_method(self):
        """Détermine la méthode de scraping optimale"""
        if self.daily_requests > 150:  # Seuil critique
            print("🚨 Seuil critique atteint - Activation Playwright")
            self.fallback_active = True
            return "playwright"
        elif self.fallback_active:
            print("🔄 Mode fallback actif")
            return "playwright"
        else:
            return "scraperapi"
    
    def scrape_page(self, url, priority=False, max_retries=3):
        """Scrape une page avec retry et fallback intelligent"""
        method = self.get_scraping_method()
        
        for attempt in range(max_retries):
            try:
                if method == "scraperapi":
                    html = self._scrape_with_api(url, priority, attempt)
                    return self.parse_quests(html)
                else:
                    html = self._scrape_with_playwright(url, attempt)
                    return self.parse_quests(html)
                    
            except Exception as e:
                print(f"❌ Tentative {attempt + 1}/{max_retries} échouée: {str(e)}")
                
                if attempt < max_retries - 1:
                    # Basculer vers Playwright en cas d'erreur API
                    if method == "scraperapi" and any(keyword in str(e).lower() 
                                                    for keyword in ["quota", "limit", "timeout", "timed out"]):
                        print("🔄 Basculement vers Playwright")
                        method = "playwright"
                        self.fallback_active = True
                    
                    # Délai progressif
                    wait_time = 2 ** attempt
                    print(f"⏳ Attente {wait_time}s avant retry...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Échec après {max_retries} tentatives: {str(e)}")
    
    def _scrape_with_api(self, url, priority=False, attempt=0):
        """Scraping avec ScraperAPI"""
        is_priority = priority or url.endswith("tab=live") or "explore" in url
        account_key = self.balancer.get_accounts_batch(batch_size=1, url=url)[0]
        self.last_used_account = account_key
        
        params = {
            "api_key": account_key,
            "url": url,
            "render": "true",
            "wait_for": "div.campaign-item", # Sélecteur corrigé
            "timeout": 60000, # Timeout augmenté à 60s
            "country_code": "us"
        }
        
        print(f"🔄 ScraperAPI - Tentative {attempt + 1} - {url} - Compte {account_key[:8]}...")
        
        response = self.session.get(
            "http://api.scraperapi.com", 
            params=params,
            timeout=65  # Timeout HTTP augmenté
        )
        
        if response.status_code == 200:
            self.daily_requests += 1
            self._save_daily_stats()
            print(f"✅ ScraperAPI réussi - {len(response.text)} caractères")
            return response.text
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
    
    def _scrape_with_playwright(self, url, attempt=0):
        """Scraping avec Playwright"""
        try:
            from playwright.sync_api import sync_playwright
            
            print(f"🎭 Playwright - Tentative {attempt + 1} - {url}")
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
                page = browser.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                
                try:
                    page.wait_for_selector("div.campaign-item", timeout=30000) # Sélecteur corrigé
                except Exception as e:
                    print(f"⚠️  Sélecteur 'div.campaign-item' non trouvé, continuons... Erreur: {e}")
                
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(3)
                
                html = page.content()
                browser.close()
                
                print(f"✅ Playwright réussi - {len(html)} caractères")
                return html
                
        except Exception as e:
            print(f"❌ Playwright échoué: {str(e)}")
            raise

    def parse_quests(self, html):
        """Parse le HTML pour extraire les données des quêtes en JSON."""
        if not html:
            return []
        soup = BeautifulSoup(html, 'html.parser')
        quests = []
        for item in soup.select("div.campaign-item"): # Sélecteur corrigé
            title_element = item.select_one("h5.card-title a")
            link_element = item.select_one("a")
            
            if title_element and link_element:
                title = title_element.text.strip()
                link = "https://galxe.com" + link_element["href"]
                quests.append({
                    "title": title,
                    "link": link,
                    "source": "Galxe"
                })
        print(f"📊 {len(quests)} quêtes parsées.")
        return quests

    def scrape_galxe_campaigns(self, pages=5, delay=3):
        """Scrape plusieurs pages de campagnes Galxe"""
        all_quests = []
        
        for page_num in range(1, pages + 1):
            url = f"https://galxe.com/explore?page={page_num}"
            
            try:
                print(f"\n📄 Page {page_num}/{pages}")
                quests_data = self.scrape_page(url, priority=True)
                all_quests.extend(quests_data)
                
                # Délai entre les pages
                if page_num < pages:
                    print(f"⏳ Pause {delay}s...")
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"❌ Échec page {page_num}: {str(e)}")
        
        return all_quests
    
    def get_detailed_stats(self):
        """Statistiques détaillées"""
        return {
            "accounts_usage": self.balancer.usage,
            "total_requests_today": self.daily_requests,
            "fallback_active": self.fallback_active,
            "last_account_used": self.last_used_account[:8] if self.last_used_account else None,
            "scraping_method": self.get_scraping_method(),
            "remaining_quota": 166 - self.daily_requests
        }


# Test complet
if __name__ == "__main__":
    scraper = GalxeScraperEnhanced()
    
    print("🚀 Test du scraper enhanced")
    print(f"📊 Statistiques initiales: {scraper.get_detailed_stats()}")
    
    # Test avec une page
    test_url = "https://galxe.com/explore?page=1"
    quests = scraper.scrape_page(test_url, priority=True)
    
    print(f"\n📊 Statistiques finales: {scraper.get_detailed_stats()}")
    if quests:
        print(f"📄 {len(quests)} quêtes récupérées. Premier résultat: {quests[0]}")
    else:
        print("Aucune quête récupérée.")