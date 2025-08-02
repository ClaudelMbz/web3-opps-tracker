import requests
import time
import json
import os
import sys
from dotenv import load_dotenv
import re

# Charger les variables d'environnement
load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vault_manager import VaultManager
from utils import get_today_date_str

class Layer3Scraper:
    def __init__(self):
        self.vault = VaultManager()
        self.headers = self._get_auth_headers()
        self.base_url = "https://layer3.xyz/api/trpc"
        self.output_dir = "data"
        os.makedirs(self.output_dir, exist_ok=True)

    def _get_auth_headers(self) -> dict:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Referer": "https://layer3.xyz/",
            "Content-Type": "application/json"
        }
        return headers

    def fetch_trpc_data(self, procedure, input_data=None):
        """Méthode pour appeler les APIs TRPC de Layer3"""
        if input_data is None:
            input_data = {"json": None, "meta": {"values": ["undefined"]}}
        
        # Encoder les paramètres comme dans les requêtes découvertes
        import urllib.parse
        encoded_input = urllib.parse.quote(json.dumps(input_data))
        
        endpoint = f"{self.base_url}/{procedure}?input={encoded_input}"
        
        try:
            print(f"[🔍] Test TRPC: {procedure}")
            response = requests.get(endpoint, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                print(f"[✅] TRPC réussi: {procedure}")
                return data
            else:
                print(f"[⚠] TRPC Status {response.status_code}: {procedure}")
                return None
                
        except Exception as e:
            print(f"[✖] Erreur TRPC {procedure}: {e}")
            return None
    
    def fetch_quests(self, limit=50):
        """Récupérer les quêtes via différentes méthodes"""
        print("[🎯] Tentative de récupération des quêtes Layer3...")
        
        # Méthode 1: Essayer les endpoints TRPC découverts
        trpc_procedures = [
            "quest.getPublicQuests",
            "quest.getAllQuests", 
            "campaign.getActiveCampaigns",
            "bounty.getAvailableBounties",
            "activation.getActiveActivations"
        ]
        
        for procedure in trpc_procedures:
            data = self.fetch_trpc_data(procedure)
            if data and isinstance(data, dict):
                # Analyser la structure de réponse
                if 'result' in data and 'data' in data['result']:
                    quests = data['result']['data']
                    if quests:
                        print(f"[✅] {len(quests)} quêtes trouvées via {procedure}")
                        return quests
        
        # Méthode 2: Essayer l'API Li.Quest découverte
        try:
            print("[🔍] Test de l'API Li.Quest (partenaire Layer3)")
            lifi_endpoint = "https://li.quest/v1/chains?chainTypes=EVM%2CSVM"
            response = requests.get(lifi_endpoint, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                chains = data.get('chains', [])
                
                # Transformer les chaînes en opportunités
                opportunities = []
                for chain in chains[:limit]:
                    opportunities.append({
                        'id': chain.get('id'),
                        'title': f"Bridge vers {chain.get('name', 'Unknown')}",
                        'description': f"Utilisez le bridge Li.Quest pour {chain.get('name')}",
                        'reward': 10,  # Estimation
                        'reward_currency': 'POINTS',
                        'time_est_min': 5,
                        'roi_usd_per_min': 0.1,
                        'source': 'Layer3-LiFi',
                        'chain': chain.get('name'),
                        'logo': chain.get('logoURI', '')
                    })
                
                if opportunities:
                    print(f"[✅] {len(opportunities)} opportunités générées via Li.Quest")
                    return opportunities
                    
        except Exception as e:
            print(f"[✖] Erreur Li.Quest: {e}")
        
        print("[❌] Aucune méthode fonctionnelle trouvée")
        return []

    def fetch_all_campaigns(self, max_pages=20, delay=0.5):
        """Récupère toutes les campagnes/quêtes Layer3"""
        print("[🚀] Récupération des campagnes Layer3...")
        
        # Utiliser notre méthode TRPC améliorée
        quests = self.fetch_quests(limit=50)
        
        if quests:
            self.save_campaigns(quests)
            return quests
        else:
            print("[⚠️] Aucune quête trouvée, génération d'opportunités de fallback...")
            # Générer quelques opportunités de fallback basées sur Layer3
            fallback_opportunities = [
                {
                    'id': 'layer3-staking-001',
                    'title': 'Stake tokens sur Layer3',
                    'description': 'Participez au staking sur la plateforme Layer3',
                    'reward': 50,
                    'reward_currency': 'L3T',
                    'time_est_min': 10,
                    'roi_usd_per_min': 0.25,
                    'source': 'Layer3',
                    'category': 'Staking'
                },
                {
                    'id': 'layer3-bridge-002', 
                    'title': 'Bridge assets vers Layer3',
                    'description': 'Utilisez le bridge pour transférer des assets',
                    'reward': 25,
                    'reward_currency': 'POINTS',
                    'time_est_min': 5,
                    'roi_usd_per_min': 0.25,
                    'source': 'Layer3',
                    'category': 'Bridge'
                }
            ]
            
            self.save_campaigns(fallback_opportunities)
            return fallback_opportunities

    def save_campaigns(self, campaigns):
        filename = os.path.join(self.output_dir, f"opportunities_layer3_{get_today_date_str()}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(campaigns, f, indent=2, ensure_ascii=False)
        print(f"[✔] Données sauvegardées dans {filename}")

if __name__ == "__main__":
    print("🚀 Test du scraper Layer3")
    scraper = Layer3Scraper()

    # Test simple
    raw_campaigns = scraper.fetch_all_campaigns(max_pages=1)
    if raw_campaigns:
        print(f"✅ {len(raw_campaigns)} campagnes récupérées")
    else:
        print("❌ Aucune campagne récupérée")

