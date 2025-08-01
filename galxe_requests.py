from datetime import datetime
import random
from dotenv import load_dotenv
from vault_manager import VaultManager

# Charger les variables d'environnement
load_dotenv()

class ScraperAPIBalancer:
    def __init__(self):
        self.vault = VaultManager()
        self.accounts = self._load_accounts()
        self.usage = {acc: 0 for acc in self.accounts}
        self.priority_hours = [6, 10, 16]  # UTC hours

    def _load_accounts(self):
        accounts = []
        for i in range(1, 9):
            path = f"scraperapi/account{i}"
            secret = self.vault.retrieve_secret(path)
            accounts.append(secret["api_key"])
        return accounts

    def get_accounts_batch(self, batch_size=3, url=None):
        """
        Retourne une liste de clés variées selon la stratégie,
        de taille batch_size.
        """
        now_utc = datetime.utcnow()
        selected_keys = []

        # Stratégie 1 : Si heure critique, choisir batch_size clés parmi les 4 priorités
        if now_utc.hour in self.priority_hours:
            selected_keys = random.sample(self.accounts[:4], min(batch_size, 4))
        
        else:
            # Stratégie 2 : Priorité géographique
            geo_account = self._get_geo_account(now_utc)
            if self.usage.get(geo_account, 0) < 33:
                selected_keys.append(geo_account)

            # Compléter avec clés les moins utilisées pour atteindre batch_size
            remaining = batch_size - len(selected_keys)
            if remaining > 0:
                # Trier comptes par usage croissant, exclure déjà sélectionnés
                candidates = [acc for acc in self.accounts if acc not in selected_keys]
                candidates_sorted = sorted(candidates, key=lambda acc: self.usage.get(acc, 0))
                selected_keys.extend(candidates_sorted[:remaining])

        # Met à jour l'usage pour chaque clé sélectionnée
        for key in selected_keys:
            self.usage[key] = self.usage.get(key, 0) + 1

        return selected_keys

    def _get_geo_account(self, time):
        geo_mapping = {
            0: self.accounts[4],  # Asie
            8: self.accounts[5],  # Europe
            16: self.accounts[6], # Amérique
        }
        return geo_mapping.get(time.hour % 8, self.accounts[7])
