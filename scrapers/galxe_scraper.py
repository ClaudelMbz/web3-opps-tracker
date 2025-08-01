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
            "wait_for": "div.GridFlowContainer_grid-flow__m_iqK > *", # Wait for grid items to load
            "timeout": 90000, # Timeout augmenté à 90s
            "country_code": "us"
        }
        
        print(f"🔄 ScraperAPI - Tentative {attempt + 1} - {url} - Compte {account_key[:8]}...")
        
        response = self.session.get(
            "http://api.scraperapi.com", 
            params=params,
            timeout=120  # Timeout HTTP augmenté pour le contenu dynamique
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
                    # Wait for the main grid container
                    page.wait_for_selector("div.GridFlowContainer_grid-flow__m_iqK", timeout=30000)
                    # Wait a bit more for content to load
                    page.wait_for_timeout(5000)
                    # Try to wait for actual quest cards to appear
                    page.wait_for_selector("div.GridFlowContainer_grid-flow__m_iqK > *", timeout=30000)
                except Exception as e:
                    print(f"⚠️  Grid container or quest items not found, trying anyway... Erreur: {e}")
                    # Even if we can't find items, continue - sometimes they load after timeout
                
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
        
        # Debug: Print some HTML to understand the structure
        print(f"🔍 Analyzing HTML structure...")
        
        # Look for the main grid container
        grid_container = soup.select_one("div.GridFlowContainer_grid-flow__m_iqK")
        if grid_container:
            print(f"✅ Found grid container with {len(grid_container.find_all())} child elements")
        else:
            print("❌ Grid container not found")
        
        # Try multiple possible selectors for quest cards
        selectors_to_try = [
            # Grid items
            "div.GridFlowContainer_grid-flow__m_iqK > div",
            "div.GridFlowContainer_grid-flow__m_iqK > *",
            # Card-like elements
            "div[class*='card']",
            "div[class*='Card']", 
            "div[class*='item']",
            "div[class*='Item']",
            # Links to spaces/campaigns
            "a[href*='/space/']",
            "a[href*='/quest/']",
            "a[href*='/campaign/']",
            # Look for any links in the main content area
            "main a[href]"
        ]
        
        found_items = []
        for selector in selectors_to_try:
            items = soup.select(selector)
            if items:
                print(f"✅ Found {len(items)} items with selector: {selector}")
                found_items.extend(items)
                break  # Use the first working selector
        
        if not found_items:
            print("❌ No quest items found with any selector")
            # Debug: show some sample HTML
            print("Sample HTML structure:")
            main_content = soup.select_one("main")
            if main_content:
                print(main_content.prettify()[:1000] + "...")
            return []
        
        # Extract quest information from found items
        for item in found_items:
            try:
                # Try to find a link
                link_element = item if item.name == 'a' else item.select_one('a')
                if not link_element:
                    continue
                    
                href = link_element.get('href', '')
                if not href:
                    continue
                    
                # Only keep links that look like space/quest/campaign links  
                if not any(path in href for path in ['/space/', '/quest/', '/campaign/']):
                    continue
                    
                # Extract title
                title = ""
                # Try different ways to get the title
                title_candidates = [
                    link_element.get_text().strip(),
                    item.get_text().strip() if item != link_element else "",
                ]
                
                for candidate in title_candidates:
                    if candidate and len(candidate) > 3:  # Reasonable title length
                        title = candidate[:100]  # Limit title length
                        break
                
                if not title:
                    title = f"Quest from {href}"
                
                # Build full URL
                if href.startswith('/'):
                    full_link = "https://galxe.com" + href
                elif href.startswith('http'):
                    full_link = href
                else:
                    full_link = "https://galxe.com/" + href
                
                quests.append({
                    "title": title,
                    "link": full_link,
                    "source": "Galxe"
                })
                
            except Exception as e:
                print(f"⚠️  Error parsing item: {e}")
                continue
        
        # Remove duplicates based on link
        seen_links = set()
        unique_quests = []
        for quest in quests:
            if quest['link'] not in seen_links:
                seen_links.add(quest['link'])
                unique_quests.append(quest)
        
        print(f"📊 {len(unique_quests)} unique quêtes parsées.")
        return unique_quests

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