import unittest
import os
import sys
from unittest.mock import patch, MagicMock
# Ajoute le dossier racine au PYTHONPATH pour permettre l'import du module scrapers
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scrapers.zealy_scraper import ZealyScraper

class TestZealyScraper(unittest.TestCase):
    """Tests unitaires pour le ZealyScraper."""

    @patch("scrapers.zealy_scraper.requests.get")
    @patch("scrapers.zealy_scraper.VaultManager")
    def test_fetch_success(self, mock_vault, mock_get):
        """Doit récupérer une page de quêtes sans erreur."""
        # Mock du secret Vault
        mock_vault.return_value.retrieve_secret.return_value = {"api_key": "fake-key"}

        # Mock d'une réponse HTTP OK
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "id": "q1",
                "name": "Quest 1",
                "difficulty": "easy",
                "reward": {"amount": 50, "currency": "XP"},
                "startDate": "2025-07-01",
                "endDate": "2025-07-10",
                "description": "Une quête test."
            }
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        scraper = ZealyScraper()
        quests = scraper.fetch_all_quests(max_pages=1)
        self.assertEqual(len(quests), 1)
        self.assertEqual(quests[0]["id"], "q1")

    @patch("scrapers.zealy_scraper.requests.get")
    @patch("scrapers.zealy_scraper.VaultManager")
    def test_fetch_pagination(self, mock_vault, mock_get):
        """Doit gérer la pagination et ne renvoyer que le nombre demandé."""
        mock_vault.return_value.retrieve_secret.return_value = {"api_key": "fake-key"}

        # Fabrique 3 pages : 20 + 20 + 5 = 45 quêtes
        def make_page(start, end):
            return [{"id": f"q{i}", "name": f"Quest {i}"} for i in range(start, end)]

        mock_get.side_effect = [
            MagicMock(json=MagicMock(return_value=make_page(1, 21)), raise_for_status=MagicMock()),
            MagicMock(json=MagicMock(return_value=make_page(21, 41)), raise_for_status=MagicMock()),
            MagicMock(json=MagicMock(return_value=make_page(41, 46)), raise_for_status=MagicMock()),
        ]

        scraper = ZealyScraper()
        quests = scraper.fetch_all_quests(max_pages=3)
        self.assertEqual(len(quests), 45)
        self.assertEqual(quests[-1]["id"], "q45")

    @patch("scrapers.zealy_scraper.VaultManager")
    def test_parse_quests(self, mock_vault):
        """Vérifie le mapping easy/medium/hard vers le temps estimé."""
        mock_vault.return_value.retrieve_secret.return_value = {"api_key": "fake-key"}

        raw = [
            {
                "id": "z1",
                "name": "Quest Z1",
                "difficulty": "hard",
                "reward": {"amount": 100},
            }
        ]

        scraper = ZealyScraper()
        parsed = scraper.parse_quests(raw)
        self.assertEqual(parsed[0]["time_est_min"], 10)
        self.assertEqual(parsed[0]["source"], "Zealy")

if __name__ == "__main__":
    unittest.main()
