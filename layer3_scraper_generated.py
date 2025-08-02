
# Code généré automatiquement par Layer3 Reverse Engineer
import requests
import json

class Layer3ScraperGenerated:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://layer3.xyz/'
        }
        
    def fetch_quests(self):
        endpoints = [
            "https://li.quest/v1/chains?chainTypes=EVM%2CSVM",
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, headers=self.headers, timeout=15)
                if response.status_code == 200:
                    return response.json()
            except Exception as e:
                print(f"Erreur: {e}")
                continue
        return []
