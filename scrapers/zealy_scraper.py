import requests
import time
import json

import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vault_manager import VaultManager
from utils import get_today_date_str

class ZealyScraper:
    def __init__(self):
        # Récupération du token Vault via variable d'environnement dans VaultManager
        self.vault = VaultManager()
        self.headers = self._get_auth_headers()
        self.subdomain = "aipioneers"
        self.base_url = f"https://api-v1.zealy.io/communities/{self.subdomain}/quests"
        self.output_dir = "data"
        os.makedirs(self.output_dir, exist_ok=True)

    def _get_auth_headers(self):
        # Utiliser directement les variables d'environnement au lieu du Vault
        api_key = os.getenv("ZEALY_API_KEY")
        if not api_key:
            raise ValueError("ZEALY_API_KEY not found in environment variables")
        return {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }

    def fetch_all_quests(self, max_pages=20, delay=0.5):
        all_quests = []
        page = 1

        while page <= max_pages:
            url = f"{self.base_url}?page={page}&limit=20"
            try:
                response = requests.get(url, headers=self.headers, timeout=15)
                response.raise_for_status()
                data = response.json()

                # La réponse est une liste ou dict avec clé 'data'
                quests = data if isinstance(data, list) else data.get("data", [])

                if not quests:
                    print(f"[ℹ] Aucune quête trouvée à la page {page}. Fin du scraping.")
                    break

                all_quests.extend(quests)
                print(f"[→] Page {page} : {len(quests)} quêtes extraites")
                page += 1
                time.sleep(delay)
            except Exception as e:
                print(f"[✖] Erreur Zealy API (page {page}): {e}")
                break

        self.save_quests(all_quests)
        return all_quests

    def calculate_roi(self, reward_amount, time_est_min, currency="XP"):
        """Calcul ROI en $/min avec conversion des devises"""
        # Taux de conversion approximatifs (à ajuster selon le marché)
        currency_rates = {
            "XP": 0.01,      # 1 XP = $0.01
            "POINTS": 0.005, # 1 POINT = $0.005
            "TOKENS": 1.0,   # 1 TOKEN = $1.00
            "GAL": 2.5,      # 1 GAL = $2.50
            "USD": 1.0       # 1 USD = $1.00
        }
        
        usd_value = reward_amount * currency_rates.get(currency.upper(), 0.01)
        return round(usd_value / max(time_est_min, 1), 4)  # Éviter division par 0
    
    def _extract_numeric_reward(self, value):
        """Extrait la valeur numérique d'un reward (gère les strings et nombres)"""
        if isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, str):
            # Essayer d'extraire le nombre d'une string comme "100 XP" ou "100"
            import re
            match = re.search(r'([0-9]+(?:\.[0-9]+)?)', str(value))
            if match:
                return float(match.group(1))
            return 0.0
        return 0.0
    
    def validate_quest_data(self, quest):
        """Valide les données d'une quête"""
        required_fields = ["id", "name"]
        for field in required_fields:
            if not quest.get(field):
                return False
        return True

    def parse_quests(self, raw_quests):
        difficulty_map = {"easy": 1, "medium": 3, "hard": 10}
        parsed = []
        
        for q in raw_quests:
            # Validation des données
            if not self.validate_quest_data(q):
                print(f"[⚠] Quête invalide ignorée: {q.get('id', 'Unknown')}")
                continue
                
            time_est = difficulty_map.get(q.get("difficulty", "medium"), 3)

            reward_data = q.get("reward", {})
            reward_amount = 0
            reward_currency = "XP"

            if isinstance(reward_data, list):
                if reward_data:
                    first_reward = reward_data[0]
                    reward_amount = self._extract_numeric_reward(first_reward.get("value", 0))
                    reward_currency = first_reward.get("type", "XP").upper()
            elif isinstance(reward_data, dict):
                reward_amount = self._extract_numeric_reward(reward_data.get("amount", 0))
                reward_currency = reward_data.get("currency", "XP")
            else:
                # Fallback : essayer de parser directement les champs de la quête
                reward_amount = self._extract_numeric_reward(q.get("xp", 0))
                reward_currency = "XP"
            
            # Calcul du ROI
            roi_usd_per_min = self.calculate_roi(reward_amount, time_est, reward_currency)

            parsed.append({
                "id": q.get("id"),
                "title": q.get("name"),
                "description": q.get("description", ""),
                "reward": reward_amount,
                "reward_currency": reward_currency,
                "time_est_min": time_est,
                "roi_usd_per_min": roi_usd_per_min,
                "start_time": q.get("startDate", ""),
                "end_time": q.get("endDate", ""),
                "source": "Zealy"
            })
        
        # Trier par ROI décroissant
        parsed.sort(key=lambda x: x["roi_usd_per_min"], reverse=True)
        return parsed

    def save_quests(self, quests):
        filename = os.path.join(self.output_dir, f"opportunities_zealy_{get_today_date_str()}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(quests, f, indent=2, ensure_ascii=False)
        print(f"[✔] Données sauvegardées dans {filename}")

    def fetch_quests(self, limit=50):
        """Méthode simplifiée pour récupérer un nombre limité de quêtes"""
        url = f"{self.base_url}?limit={limit}"
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # La réponse est une liste ou dict avec clé 'data'
            quests = data if isinstance(data, list) else data.get("data", [])
            print(f"[→] {len(quests)} quêtes récupérées de Zealy")
            return quests
        except Exception as e:
            print(f"[✖] Erreur Zealy API: {e}")
            return []


if __name__ == "__main__":
    print("🚀 Test du scraper Zealy")
    scraper = ZealyScraper()
    
    # Test simple
    raw_quests = scraper.fetch_quests(limit=10)
    if raw_quests:
        parsed_quests = scraper.parse_quests(raw_quests)
        print(f"✅ {len(parsed_quests)} quêtes parsées")
        if parsed_quests:
            print(f"📋 Première quête: {parsed_quests[0]['title']}")
    else:
        print("❌ Aucune quête récupérée")
