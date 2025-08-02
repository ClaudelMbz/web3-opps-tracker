import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os

class Layer3ReverseEngineer:
    def __init__(self):
        self.captured_requests = []
        self.api_endpoints = []
        self.auth_headers = {}
        
    def setup_driver_with_logging(self):
        """Configure Chrome avec logging des requêtes réseau"""
        # Activer les logs de performance pour capturer les requêtes réseau
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'performance': 'ALL'}
        
        options = Options()
        options.add_argument('--enable-logging')
        options.add_argument('--log-level=0')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        
        # Mode normal (non-headless) pour éviter la détection
        # options.add_argument('--headless')
        
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        driver = webdriver.Chrome(options=options)
        return driver
        
    def capture_network_requests(self, url="https://layer3.xyz/quests", duration=30):
        """Capture les requêtes réseau pendant la navigation"""
        print(f"🔍 Démarrage de l'analyse réseau pour {url}")
        print(f"⏱️  Durée de capture : {duration} secondes")
        
        driver = self.setup_driver_with_logging()
        
        try:
            # Naviguer vers la page
            print("🌐 Navigation vers Layer3...")
            driver.get(url)
            
            # Attendre le chargement complet
            print("⏳ Attente du chargement complet...")
            time.sleep(10)
            
            # Essayer de faire défiler pour déclencher plus de requêtes
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            
            # Capturer les logs de performance
            print("📊 Analyse des requêtes réseau...")
            logs = driver.get_log('performance')
            
            for log_entry in logs:
                try:
                    message = json.loads(log_entry['message'])
                    
                    # Filtrer les requêtes HTTP/HTTPS
                    if message['message']['method'] == 'Network.responseReceived':
                        response = message['message']['params']['response']
                        url_req = response['url']
                        
                        # Filtrer les requêtes API potentielles
                        if self._is_api_request(url_req):
                            print(f"🎯 API trouvée: {url_req}")
                            
                            request_info = {
                                'url': url_req,
                                'method': response.get('method', 'GET'),
                                'status': response['status'],
                                'headers': response.get('headers', {}),
                                'timestamp': log_entry['timestamp']
                            }
                            
                            self.captured_requests.append(request_info)
                            
                            # Extraire les headers d'authentification
                            self._extract_auth_headers(response.get('headers', {}))
                            
                except Exception as e:
                    continue
                    
            # Essayer d'identifier les endpoints spécifiques
            self._analyze_captured_requests()
            
        except Exception as e:
            print(f"❌ Erreur lors de la capture: {e}")
            
        finally:
            driver.quit()
            
        return self.captured_requests
    
    def _is_api_request(self, url):
        """Détermine si une URL est probablement une API"""
        api_indicators = [
            '/api/',
            '/graphql',
            '/v1/',
            '/v2/',
            'quests',
            'campaigns',
            'bounties',
            '.json',
            'layer3.xyz'
        ]
        
        return any(indicator in url.lower() for indicator in api_indicators)
    
    def _extract_auth_headers(self, headers):
        """Extrait les headers d'authentification"""
        auth_keys = ['authorization', 'x-api-key', 'bearer', 'x-auth-token', 'cookie']
        
        for key, value in headers.items():
            if any(auth_key in key.lower() for auth_key in auth_keys):
                self.auth_headers[key] = value
                print(f"🔐 Header d'auth trouvé: {key}")
    
    def _analyze_captured_requests(self):
        """Analyse les requêtes capturées pour identifier les patterns"""
        print(f"\n📈 Analyse de {len(self.captured_requests)} requêtes capturées:")
        
        for req in self.captured_requests:
            print(f"  • {req['method']} {req['url']} - Status: {req['status']}")
            
            # Identifier les endpoints de quêtes
            if any(keyword in req['url'].lower() for keyword in ['quest', 'campaign', 'bounty']):
                self.api_endpoints.append(req['url'])
                
    def test_discovered_apis(self):
        """Teste les APIs découvertes"""
        print(f"\n🧪 Test de {len(self.api_endpoints)} endpoints découverts:")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://layer3.xyz/'
        }
        
        # Ajouter les headers d'authentification découverts
        headers.update(self.auth_headers)
        
        working_endpoints = []
        
        for endpoint in self.api_endpoints:
            try:
                print(f"🔗 Test: {endpoint}")
                response = requests.get(endpoint, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    print(f"✅ Succès! Status: {response.status_code}")
                    
                    # Analyser la structure de réponse
                    try:
                        data = response.json()
                        print(f"📋 Structure: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                        working_endpoints.append({
                            'url': endpoint,
                            'data_structure': list(data.keys()) if isinstance(data, dict) else str(type(data)),
                            'sample_data': data if len(str(data)) < 500 else str(data)[:500] + "..."
                        })
                    except:
                        print("📋 Réponse non-JSON")
                        
                else:
                    print(f"❌ Échec: Status {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Erreur: {e}")
                
        return working_endpoints
    
    def generate_scraper_code(self, working_endpoints):
        """Génère le code du scraper basé sur les découvertes"""
        if not working_endpoints:
            print("❌ Aucun endpoint fonctionnel trouvé pour générer le code")
            return
            
        print(f"\n🛠️  Génération du code scraper pour {len(working_endpoints)} endpoints:")
        
        scraper_code = '''
# Code généré automatiquement par Layer3 Reverse Engineer
import requests
import json

class Layer3ScraperGenerated:
    def __init__(self):
        self.headers = {
'''
        
        # Ajouter les headers découverts
        for key, value in self.auth_headers.items():
            scraper_code += f'            "{key}": "{value}",\n'
            
        scraper_code += '''            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://layer3.xyz/'
        }
        
    def fetch_quests(self):
        endpoints = [
'''
        
        # Ajouter les endpoints fonctionnels
        for endpoint_info in working_endpoints:
            scraper_code += f'            "{endpoint_info["url"]}",\n'
            
        scraper_code += '''        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, headers=self.headers, timeout=15)
                if response.status_code == 200:
                    return response.json()
            except Exception as e:
                print(f"Erreur: {e}")
                continue
        return []
'''
        
        # Sauvegarder le code généré
        with open('layer3_scraper_generated.py', 'w', encoding='utf-8') as f:
            f.write(scraper_code)
            
        print("💾 Code scraper sauvegardé dans 'layer3_scraper_generated.py'")
        return scraper_code

def main():
    engineer = Layer3ReverseEngineer()
    
    print("🚀 Layer3 Reverse Engineering Tool")
    print("=" * 50)
    
    # Étape 1: Capturer les requêtes réseau
    captured = engineer.capture_network_requests(duration=30)
    
    if not captured:
        print("❌ Aucune requête API capturée. Le site utilise peut-être une protection avancée.")
        return
    
    # Étape 2: Tester les APIs découvertes
    working_endpoints = engineer.test_discovered_apis()
    
    # Étape 3: Générer le code scraper
    if working_endpoints:
        engineer.generate_scraper_code(working_endpoints)
        print(f"\n🎉 Reverse engineering terminé!")
        print(f"📊 {len(working_endpoints)} endpoint(s) fonctionnel(s) découvert(s)")
    else:
        print("\n⚠️  Aucun endpoint fonctionnel trouvé. Layer3 pourrait nécessiter une authentification utilisateur.")

if __name__ == "__main__":
    main()
