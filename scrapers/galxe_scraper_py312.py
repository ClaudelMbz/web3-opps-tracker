# scrapers/galxe_scraper_py312.py
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import time
import json

class GalxeScraperPy312:
    def __init__(self):
        self.session = requests.Session()
        self.daily_requests = 0
        self.stats_file = "scraper_stats.json"
        self._load_daily_stats()
        
    def _load_daily_stats(self):
        """Charger les statistiques du jour"""
        try:
            if json.loads(open(self.stats_file, 'r').read()):
                with open(self.stats_file, 'r') as f:
                    stats = json.load(f)
                    if stats.get('date') == datetime.now().strftime('%Y-%m-%d'):
                        self.daily_requests = stats.get('total_requests', 0)
        except Exception as e:
            pass
    
    def _save_daily_stats(self):
        """Sauvegarder les statistiques"""
        try:
            stats = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'total_requests': self.daily_requests,
                'last_update': datetime.now().isoformat()
            }
            with open(self.stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
        except Exception as e:
            pass
    
    def scrape_page_with_playwright(self, url, max_retries=2):
        """Scrape une page avec Playwright pour le contenu dynamique"""
        for attempt in range(max_retries):
            try:
                from playwright.sync_api import sync_playwright
                
                print(f"🎭 Playwright - Tentative {attempt + 1} - {url}")
                
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
                    page = browser.new_page()
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    
                    try:
                        # Attendre le container grid
                        page.wait_for_selector("div.GridFlowContainer_grid-flow__m_iqK", timeout=30000)
                        # Attendre le contenu dynamique
                        page.wait_for_timeout(8000)
                        # Essayer d'attendre les éléments de quête
                        page.wait_for_selector("div.GridFlowContainer_grid-flow__m_iqK > *", timeout=25000)
                        print("✅ Éléments détectés dans le grid!")
                    except Exception as e:
                        print(f"⚠️  Éléments non détectés dans le délai, continuons... {e}")
                    
                    # Scroll pour déclencher plus de contenu
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(3)
                    
                    html = page.content()
                    browser.close()
                    
                    print(f"✅ Playwright réussi - {len(html)} caractères")
                    return self.parse_quests(html)
                    
            except ImportError:
                print("❌ Playwright non disponible, fallback vers requête simple")
                return self.scrape_page_simple(url)
            except Exception as e:
                print(f"❌ Tentative {attempt + 1}/{max_retries} échouée: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    print("🔄 Fallback vers requête simple")
                    return self.scrape_page_simple(url)
        
        return []
    
    def scrape_page_simple(self, url):
        """Scrape avec requête HTTP simple (fallback)"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
            }
            response = self.session.get(url, headers=headers, timeout=30)
            self.daily_requests += 1
            self._save_daily_stats()
            
            print(f"✅ Requête simple réussie - {len(response.text)} caractères")
            return self.parse_quests(response.text)
        except Exception as e:
            print(f"❌ Requête simple échouée: {e}")
            return []

    def parse_quests(self, html):
        """Parse le HTML pour extraire les données des quêtes"""
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        quests = []
        
        print("🔍 Analyse du HTML...")
        
        # Vérifier le container grid
        grid_container = soup.select_one("div.GridFlowContainer_grid-flow__m_iqK")
        if grid_container:
            child_count = len(grid_container.find_all())
            print(f"✅ Container grid trouvé avec {child_count} éléments enfants")
        else:
            print("❌ Container grid non trouvé")
        
        # Sélecteurs à tester dans l'ordre de priorité
        selectors_to_try = [
            "div.GridFlowContainer_grid-flow__m_iqK > div",
            "div.GridFlowContainer_grid-flow__m_iqK > *",
            "div[class*='card']",
            "div[class*='Card']", 
            "a[href*='/space/']",
            "a[href*='/quest/']",
            "a[href*='/campaign/']",
            "main a[href]"
        ]
        
        found_items = []
        for selector in selectors_to_try:
            items = soup.select(selector)
            if items:
                print(f"✅ {selector}: {len(items)} éléments trouvés")
                found_items = items
                break
        
        if not found_items:
            print("❌ Aucun élément trouvé")
            return []
        
        print(f"🔄 Traitement de {len(found_items)} éléments...")
        
        for item in found_items:
            try:
                # Chercher un lien
                link_element = item if item.name == 'a' else item.select_one('a')
                if not link_element:
                    continue
                    
                href = link_element.get('href', '')
                if not href:
                    continue
                    
                # Filtrer les liens pertinents
                if not any(path in href for path in ['/space/', '/quest/', '/campaign/']):
                    continue
                    
                # Extraire le titre
                title = ""
                title_candidates = [
                    link_element.get_text().strip(),
                    item.get_text().strip() if item != link_element else "",
                ]
                
                for candidate in title_candidates:
                    if candidate and len(candidate) > 3:
                        # Nettoyer le titre (supprimer les caractères indésirables)
                        title = candidate.replace('\n', ' ').replace('\t', ' ')
                        title = ' '.join(title.split())  # Normaliser les espaces
                        title = title[:150]  # Limiter la longueur
                        break
                
                if not title:
                    title = f"Quest from {href}"
                
                # Construire l'URL complète
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
                continue
        
        # Supprimer les doublons
        seen_links = set()
        unique_quests = []
        for quest in quests:
            if quest['link'] not in seen_links:
                seen_links.add(quest['link'])
                unique_quests.append(quest)
        
        print(f"📊 {len(unique_quests)} quêtes uniques parsées.")
        return unique_quests

    def scrape_galxe_campaigns(self, pages=5, delay=3):
        """Scrape plusieurs pages de campagnes Galxe"""
        all_quests = []
        
        for page_num in range(1, pages + 1):
            url = f"https://galxe.com/explore?page={page_num}"
            
            try:
                print(f"\n📄 Page {page_num}/{pages}")
                quests_data = self.scrape_page_with_playwright(url)
                all_quests.extend(quests_data)
                
                # Délai entre les pages
                if page_num < pages:
                    print(f"⏳ Pause {delay}s...")
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"❌ Échec page {page_num}: {str(e)}")
        
        print(f"\n🎉 Scraping terminé! Total: {len(all_quests)} quêtes récupérées")
        return all_quests

# Test direct
if __name__ == "__main__":
    scraper = GalxeScraperPy312()
    
    print("🚀 Test du scraper Galxe Python 3.12")
    
    # Test avec une page
    test_url = "https://galxe.com/explore?page=1"
    quests = scraper.scrape_page_with_playwright(test_url)
    
    if quests:
        print(f"\n📄 {len(quests)} quêtes récupérées:")
        for i, quest in enumerate(quests[:5]):
            print(f"  {i+1}. {quest['title'][:50]}...")
            print(f"     {quest['link']}")
    else:
        print("❌ Aucune quête récupérée.")
