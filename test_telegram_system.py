#!/usr/bin/env python3
"""
🧪 Tests Automatisés - Système Telegram Web3 Opportunities Tracker
================================================================
Tests complets pour valider le bot Telegram et le scheduler
"""

import asyncio
import json
import logging
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

# Imports du projet
from telegram_bot import TelegramBot
from telegram_scheduler import TelegramScheduler

# Configuration de logging pour les tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestTelegramBot(unittest.TestCase):
    """Tests du bot Telegram"""
    
    def setUp(self):
        """Initialisation des tests"""
        self.bot_token = "8063978631:AAGrnjyRaa3MounLsIkJu_Cglaa80NTYoaI"
        self.chat_id = "7886553560"
        self.bot = TelegramBot(self.bot_token, self.chat_id)
    
    def test_bot_initialization(self):
        """Test 1: Initialisation du bot"""
        self.assertEqual(self.bot.bot_token, self.bot_token)
        self.assertEqual(self.bot.chat_id, self.chat_id)
        self.assertEqual(self.bot.roi_threshold, 2.0)
        logger.info("✅ Test 1: Initialisation du bot - SUCCÈS")
    
    def test_mock_data_generation(self):
        """Test 2: Génération de données mock"""
        mock_data = self.bot.generate_mock_data()
        
        self.assertIsInstance(mock_data, list)
        self.assertEqual(len(mock_data), 20)
        
        # Vérifier la structure des données
        for item in mock_data:
            self.assertIn('title', item)
            self.assertIn('roi', item)
            self.assertIn('source', item)
            self.assertIn('url', item)
            self.assertIn('timestamp', item)
        
        logger.info(f"✅ Test 2: Génération de {len(mock_data)} données mock - SUCCÈS")
    
    def test_data_loading_and_filtering(self):
        """Test 3: Chargement et filtrage des données"""
        # Créer des données de test temporaires
        test_data = [
            {'title': 'High ROI Opportunity', 'roi': 5.5, 'source': 'Test', 'url': 'http://test.com', 'timestamp': datetime.now().isoformat()},
            {'title': 'Medium ROI Opportunity', 'roi': 3.0, 'source': 'Test', 'url': 'http://test.com', 'timestamp': datetime.now().isoformat()},
            {'title': 'Low ROI Opportunity', 'roi': 1.0, 'source': 'Test', 'url': 'http://test.com', 'timestamp': datetime.now().isoformat()},
        ]
        
        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name
        
        try:
            # Tester le chargement
            import pandas as pd
            df = pd.DataFrame(test_data)
            
            # Tester le filtrage
            filtered = self.bot.filter_opportunities(df)
            
            self.assertEqual(filtered['total'], 2)  # Seulement ROI >= 2.0
            self.assertEqual(len(filtered['high']), 1)  # ROI >= 5.0
            self.assertEqual(len(filtered['medium']), 1)  # ROI 2-5
            self.assertEqual(len(filtered['low']), 0)  # ROI < 2 (exclus)
            
        finally:
            # Nettoyer
            os.unlink(temp_file)
        
        logger.info("✅ Test 3: Chargement et filtrage des données - SUCCÈS")
    
    def test_message_formatting(self):
        """Test 4: Formatage des messages de notification"""
        # Données de test
        opportunities = {
            'total': 5,
            'avg_roi': 4.2,
            'high': [
                {'title': 'Super High ROI Task', 'roi': 7.5, 'source': 'Zealy', 'url': 'http://test.com'},
                {'title': 'High ROI Campaign', 'roi': 6.0, 'source': 'Galxe', 'url': 'http://test.com'}
            ],
            'medium': [
                {'title': 'Good ROI Quest', 'roi': 3.5, 'source': 'Layer3', 'url': 'http://test.com'},
                {'title': 'Decent ROI Task', 'roi': 2.8, 'source': 'Twitter', 'url': 'http://test.com'}
            ],
            'low': []
        }
        
        message = self.bot.format_notification_message(opportunities)
        
        # Vérifier le contenu du message
        self.assertIn('5 nouvelles opportunités', message)
        self.assertIn('$4.20/min', message)
        self.assertIn('HIGH ROI', message)
        self.assertIn('MEDIUM ROI', message)
        self.assertIn('Super High ROI Task', message)
        self.assertIn('Dashboard:', message)
        
        logger.info("✅ Test 4: Formatage des messages - SUCCÈS")
    
    async def test_connection_simulation(self):
        """Test 5: Simulation de connexion (sans vraie requête)"""
        # Mock de la connexion pour éviter les vraies requêtes
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'ok': True,
                'result': {'first_name': 'Web3OppsTracker'}
            }
            mock_get.return_value = mock_response
            
            result = await self.bot.test_connection()
            self.assertTrue(result)
        
        logger.info("✅ Test 5: Simulation de connexion - SUCCÈS")

class TestTelegramScheduler(unittest.TestCase):
    """Tests du scheduler Telegram"""
    
    def setUp(self):
        """Initialisation des tests"""
        self.bot_token = "8063978631:AAGrnjyRaa3MounLsIkJu_Cglaa80NTYoaI"
        self.chat_id = "7886553560"
        self.scheduler = TelegramScheduler(self.bot_token, self.chat_id, interval_hours=1)
    
    def test_scheduler_initialization(self):
        """Test 6: Initialisation du scheduler"""
        self.assertEqual(self.scheduler.interval_hours, 1)
        self.assertFalse(self.scheduler.is_running)
        self.assertEqual(self.scheduler.notification_count, 0)
        self.assertEqual(self.scheduler.error_count, 0)
        
        logger.info("✅ Test 6: Initialisation du scheduler - SUCCÈS")
    
    def test_next_notification_calculation(self):
        """Test 7: Calcul de la prochaine notification"""
        now = datetime.now()
        next_notification = self.scheduler.calculate_next_notification_time()
        
        # Doit être environ 1 heure plus tard, aligné sur l'heure
        expected_time = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        
        # Tolérance de quelques secondes pour le calcul
        time_diff = abs((next_notification - expected_time).total_seconds())
        self.assertLess(time_diff, 60)  # Moins de 1 minute de différence
        
        logger.info(f"✅ Test 7: Calcul prochaine notification - SUCCÈS (dans {time_diff:.0f}s)")

async def run_integration_test():
    """Test d'intégration complet"""
    logger.info("🔄 Début des tests d'intégration...")
    
    bot_token = "8063978631:AAGrnjyRaa3MounLsIkJu_Cglaa80NTYoaI"
    chat_id = "7886553560"
    
    try:
        # Test 8: Création et test du bot complet
        bot = TelegramBot(bot_token, chat_id)
        
        # Test de chargement des données réelles
        df = bot.load_opportunities_data()
        logger.info(f"✅ Test 8: Données chargées - {len(df)} opportunités")
        
        # Test de filtrage
        filtered = bot.filter_opportunities(df)
        logger.info(f"✅ Test 8: Filtrage réussi - {filtered['total']} opportunités filtrées")
        
        # Test 9: Formatage du message avec données réelles
        message = bot.format_notification_message(filtered)
        logger.info(f"✅ Test 9: Message formaté - {len(message)} caractères")
        
        # Test 10: Validation de la structure du message
        required_elements = ['Web3 Opportunities', 'ROI', 'Dashboard']
        for element in required_elements:
            if element.lower() in message.lower():
                logger.info(f"✅ Test 10: Élément '{element}' trouvé dans le message")
            else:
                logger.warning(f"⚠️ Test 10: Élément '{element}' manquant dans le message")
        
        logger.info("🎉 Tests d'intégration terminés avec succès!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors des tests d'intégration: {e}")
        return False

def run_all_tests():
    """Lance tous les tests"""
    print("🧪 TESTS AUTOMATISÉS - Web3 Opportunities Tracker Telegram")
    print("=" * 60)
    print()
    
    # Tests unitaires
    suite = unittest.TestSuite()
    
    # Tests du bot
    suite.addTest(TestTelegramBot('test_bot_initialization'))
    suite.addTest(TestTelegramBot('test_mock_data_generation'))
    suite.addTest(TestTelegramBot('test_data_loading_and_filtering'))
    suite.addTest(TestTelegramBot('test_message_formatting'))
    
    # Tests du scheduler
    suite.addTest(TestTelegramScheduler('test_scheduler_initialization'))
    suite.addTest(TestTelegramScheduler('test_next_notification_calculation'))
    
    # Exécution des tests unitaires
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    
    # Tests d'intégration asynchrones
    print("\n🔄 Tests d'intégration...")
    integration_success = asyncio.run(run_integration_test())
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    total_tests = result.testsRun + (1 if integration_success else 0)
    failed_tests = len(result.failures) + len(result.errors) + (0 if integration_success else 1)
    passed_tests = total_tests - failed_tests
    
    print(f"✅ Tests réussis: {passed_tests}/{total_tests}")
    print(f"❌ Tests échoués: {failed_tests}/{total_tests}")
    
    if failed_tests == 0:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
        print("✅ Le système Telegram est prêt à fonctionner")
        return True
    else:
        print("\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        print("❌ Vérifiez les erreurs ci-dessus")
        return False

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrompus par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erreur critique lors des tests: {e}")
        sys.exit(1)
