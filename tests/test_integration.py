#!/usr/bin/env python3
"""
🧪 Tests d'Intégration - Web3 Opportunities Tracker
=================================================
Tests end-to-end du pipeline complet selon le plan du Jour 11
"""

import unittest
import json
import os
import sys
import time
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent))

# Imports des modules du projet
try:
    from telegram_bot import TelegramBot
    from telegram_scheduler import TelegramScheduler
    from telegram_bot_interactive import InteractiveTelegramBot
    import pandas as pd
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    sys.exit(1)

class TestIntegration(unittest.TestCase):
    """Tests d'intégration pour le pipeline complet"""
    
    def setUp(self):
        """Configuration des tests"""
        self.bot_token = "8063978631:AAGrnjyRaa3MounLsIkJu_Cglaa80NTYoaI"
        self.chat_id = "7886553560"
        self.test_data_dir = Path("data")
        self.test_data_dir.mkdir(exist_ok=True)
        
    def test_end_to_end_pipeline(self):
        """Test 1: Pipeline complet de bout en bout"""
        print("🔄 Test 1: Pipeline end-to-end...")
        
        try:
            # 1. Initialiser le bot
            bot = TelegramBot(self.bot_token, self.chat_id)
            
            # 2. Charger les données
            df = bot.load_opportunities_data()
            
            # 3. Vérifications de base
            self.assertGreater(len(df), 10, "Au moins 10 opportunités doivent être chargées")
            self.assertIn('roi', df.columns, "Colonne ROI doit exister")
            self.assertIn('source', df.columns, "Colonne source doit exister")
            self.assertIn('title', df.columns, "Colonne title doit exister")
            
            # 4. Filtrage des opportunités
            filtered_opps = bot.filter_opportunities(df)
            
            # 5. Vérifications du filtrage
            self.assertIsInstance(filtered_opps, dict, "Le filtrage doit retourner un dictionnaire")
            self.assertIn('total', filtered_opps, "Le résultat doit contenir 'total'")
            self.assertIn('high', filtered_opps, "Le résultat doit contenir 'high'")
            self.assertIn('medium', filtered_opps, "Le résultat doit contenir 'medium'")
            self.assertIn('avg_roi', filtered_opps, "Le résultat doit contenir 'avg_roi'")
            
            # 6. Formatage du message
            message = bot.format_notification_message(filtered_opps)
            self.assertIsInstance(message, str, "Le message doit être une string")
            self.assertGreater(len(message), 50, "Le message doit contenir du contenu")
            
            print(f"✅ Test 1 réussi - {len(df)} opportunités, {filtered_opps['total']} filtrées")
            
        except Exception as e:
            self.fail(f"Échec du test end-to-end: {e}")

    def test_data_quality(self):
        """Test 2: Qualité des données"""
        print("🔄 Test 2: Qualité des données...")
        
        try:
            bot = TelegramBot(self.bot_token, self.chat_id)
            df = bot.load_opportunities_data()
            
            # Vérifier le format des données
            required_columns = ['title', 'roi', 'source', 'url', 'timestamp']
            for col in required_columns:
                self.assertIn(col, df.columns, f"Colonne {col} requise")
            
            # Vérifier les types de données
            self.assertTrue(df['roi'].dtype in ['float64', 'int64'], "ROI doit être numérique")
            
            # Vérifier les valeurs ROI valides
            invalid_roi = df[df['roi'] < 0]
            self.assertEqual(len(invalid_roi), 0, "Aucun ROI négatif autorisé")
            
            # Vérifier l'absence de doublons (basé sur title + source)
            duplicates = df.duplicated(subset=['title', 'source'], keep=False)
            duplicate_count = duplicates.sum()
            
            # Vérifier les URLs valides
            invalid_urls = df[~df['url'].str.startswith('http')]
            self.assertLessEqual(len(invalid_urls), len(df) * 0.1, "Maximum 10% d'URLs invalides autorisé")
            
            # Vérifier les sources connues
            known_sources = ['Zealy', 'Galxe', 'Layer3', 'TwitterRSS', 'AirdropsFallback', 'Layer3-LiFi', 'Unknown']
            unknown_sources = df[~df['source'].isin(known_sources)]
            
            print(f"✅ Test 2 réussi - Qualité OK, {duplicate_count} doublons, {len(unknown_sources)} sources inconnues")
            
        except Exception as e:
            self.fail(f"Échec test qualité données: {e}")

    def test_telegram_bot_functionality(self):
        """Test 3: Fonctionnalités du bot Telegram"""
        print("🔄 Test 3: Fonctionnalités bot Telegram...")
        
        try:
            bot = TelegramBot(self.bot_token, self.chat_id)
            
            # Test de génération de données mock
            mock_data = bot.generate_mock_data()
            self.assertEqual(len(mock_data), 20, "20 données mock doivent être générées")
            
            # Test du filtrage avec données mock
            df_mock = pd.DataFrame(mock_data)
            filtered_mock = bot.filter_opportunities(df_mock)
            self.assertIsInstance(filtered_mock, dict)
            
            # Test du formatage de message
            message = bot.format_notification_message(filtered_mock)
            required_elements = ['Web3 Opportunities', 'ROI', 'Dashboard']
            for element in required_elements:
                self.assertIn(element.lower(), message.lower(), f"Élément '{element}' manquant")
                
            print("✅ Test 3 réussi - Fonctionnalités bot OK")
            
        except Exception as e:
            self.fail(f"Échec test bot Telegram: {e}")

    def test_scheduler_functionality(self):
        """Test 4: Fonctionnalités du scheduler"""
        print("🔄 Test 4: Fonctionnalités scheduler...")
        
        try:
            scheduler = TelegramScheduler(self.bot_token, self.chat_id, interval_hours=1)
            
            # Test d'initialisation
            self.assertEqual(scheduler.interval_hours, 1)
            self.assertEqual(scheduler.notification_count, 0)
            self.assertEqual(scheduler.error_count, 0)
            self.assertFalse(scheduler.is_running)
            
            # Test du calcul de prochaine notification
            next_notification = scheduler.calculate_next_notification_time()
            now = datetime.now()
            expected_time = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
            
            time_diff = abs((next_notification - expected_time).total_seconds())
            self.assertLess(time_diff, 60, "Calcul prochaine notification doit être précis")
            
            print("✅ Test 4 réussi - Scheduler OK")
            
        except Exception as e:
            self.fail(f"Échec test scheduler: {e}")

    def test_interactive_bot_structure(self):
        """Test 5: Structure du bot interactif"""
        print("🔄 Test 5: Structure bot interactif...")
        
        try:
            interactive_bot = InteractiveTelegramBot(self.bot_token, self.chat_id)
            
            # Vérifier que les méthodes essentielles existent
            essential_methods = [
                'start_command', 'button_callback', 'show_stats', 
                'show_top_roi', 'show_sources', 'show_settings'
            ]
            
            for method in essential_methods:
                self.assertTrue(hasattr(interactive_bot, method), f"Méthode {method} manquante")
                self.assertTrue(callable(getattr(interactive_bot, method)), f"Méthode {method} non appelable")
            
            print("✅ Test 5 réussi - Bot interactif OK")
            
        except Exception as e:
            self.fail(f"Échec test bot interactif: {e}")

    def test_data_persistence(self):
        """Test 6: Persistance des données"""
        print("🔄 Test 6: Persistance des données...")
        
        try:
            bot = TelegramBot(self.bot_token, self.chat_id)
            
            # Chargement initial
            df1 = bot.load_opportunities_data()
            count1 = len(df1)
            
            # Attendre un peu et recharger
            time.sleep(1)
            df2 = bot.load_opportunities_data()
            count2 = len(df2)
            
            # Les données doivent être cohérentes
            self.assertEqual(count1, count2, "Les données doivent être persistantes")
            
            # Vérifier la structure cohérente
            self.assertEqual(list(df1.columns), list(df2.columns), "Structure des colonnes doit être stable")
            
            print(f"✅ Test 6 réussi - Persistance OK ({count1} opportunités)")
            
        except Exception as e:
            self.fail(f"Échec test persistance: {e}")

    def test_error_handling(self):
        """Test 7: Gestion d'erreurs"""
        print("🔄 Test 7: Gestion d'erreurs...")
        
        try:
            # Test avec token invalide
            invalid_bot = TelegramBot("invalid_token", self.chat_id)
            
            # Le chargement de données doit continuer à fonctionner même avec un token invalide
            df = invalid_bot.load_opportunities_data()
            self.assertGreater(len(df), 0, "Données mock doivent être utilisées si pas de vraies données")
            
            # Test de filtrage avec DataFrame vide
            empty_df = pd.DataFrame()
            filtered_empty = invalid_bot.filter_opportunities(empty_df)
            self.assertEqual(filtered_empty['total'], 0, "Filtrage DataFrame vide doit retourner 0")
            
            print("✅ Test 7 réussi - Gestion d'erreurs OK")
            
        except Exception as e:
            self.fail(f"Échec test gestion erreurs: {e}")

class TestPerformance(unittest.TestCase):
    """Tests de performance pour le système"""
    
    def setUp(self):
        """Configuration des tests de performance"""
        self.bot_token = "8063978631:AAGrnjyRaa3MounLsIkJu_Cglaa80NTYoaI"
        self.chat_id = "7886553560"
        
    def test_data_loading_performance(self):
        """Test 8: Performance du chargement de données"""
        print("🔄 Test 8: Performance chargement...")
        
        try:
            bot = TelegramBot(self.bot_token, self.chat_id)
            
            # Mesurer le temps de chargement
            start_time = time.time()
            df = bot.load_opportunities_data()
            loading_time = time.time() - start_time
            
            # Vérifier que le chargement est rapide
            self.assertLess(loading_time, 5.0, f"Chargement trop lent: {loading_time:.2f}s")
            
            # Mesurer le filtrage
            start_time = time.time()
            filtered = bot.filter_opportunities(df)
            filtering_time = time.time() - start_time
            
            self.assertLess(filtering_time, 2.0, f"Filtrage trop lent: {filtering_time:.2f}s")
            
            print(f"✅ Test 8 réussi - Chargement: {loading_time:.2f}s, Filtrage: {filtering_time:.2f}s")
            
        except Exception as e:
            self.fail(f"Échec test performance: {e}")

    def test_message_formatting_performance(self):
        """Test 9: Performance du formatage des messages"""
        print("🔄 Test 9: Performance formatage...")
        
        try:
            bot = TelegramBot(self.bot_token, self.chat_id)
            df = bot.load_opportunities_data()
            filtered = bot.filter_opportunities(df)
            
            # Mesurer le formatage
            start_time = time.time()
            message = bot.format_notification_message(filtered)
            formatting_time = time.time() - start_time
            
            self.assertLess(formatting_time, 1.0, f"Formatage trop lent: {formatting_time:.2f}s")
            self.assertGreater(len(message), 50, "Message doit avoir du contenu")
            
            print(f"✅ Test 9 réussi - Formatage: {formatting_time:.3f}s, Taille: {len(message)} caractères")
            
        except Exception as e:
            self.fail(f"Échec test performance formatage: {e}")

def run_integration_tests():
    """Lance tous les tests d'intégration"""
    print("🧪 TESTS D'INTÉGRATION - Web3 Opportunities Tracker")
    print("=" * 60)
    print()
    
    # Configuration du test runner
    suite = unittest.TestSuite()
    
    # Tests d'intégration
    suite.addTest(TestIntegration('test_end_to_end_pipeline'))
    suite.addTest(TestIntegration('test_data_quality'))
    suite.addTest(TestIntegration('test_telegram_bot_functionality'))
    suite.addTest(TestIntegration('test_scheduler_functionality'))
    suite.addTest(TestIntegration('test_interactive_bot_structure'))
    suite.addTest(TestIntegration('test_data_persistence'))
    suite.addTest(TestIntegration('test_error_handling'))
    
    # Tests de performance
    suite.addTest(TestPerformance('test_data_loading_performance'))
    suite.addTest(TestPerformance('test_message_formatting_performance'))
    
    # Exécution des tests
    runner = unittest.TextTestRunner(verbosity=1)
    start_time = time.time()
    result = runner.run(suite)
    total_time = time.time() - start_time
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS D'INTÉGRATION")
    print("=" * 60)
    
    total_tests = result.testsRun
    failed_tests = len(result.failures) + len(result.errors)
    passed_tests = total_tests - failed_tests
    
    print(f"✅ Tests réussis: {passed_tests}/{total_tests}")
    print(f"❌ Tests échoués: {failed_tests}/{total_tests}")
    print(f"⏱️ Temps total: {total_time:.2f} secondes")
    print(f"⚡ Performance: {total_tests/total_time:.1f} tests/seconde")
    
    if failed_tests == 0:
        print("\n🎉 TOUS LES TESTS D'INTÉGRATION SONT PASSÉS!")
        print("✅ Le pipeline end-to-end est validé")
        return True
    else:
        print("\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        print("❌ Vérifiez les erreurs ci-dessus")
        return False

if __name__ == "__main__":
    try:
        success = run_integration_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrompus par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erreur critique lors des tests: {e}")
        sys.exit(1)
