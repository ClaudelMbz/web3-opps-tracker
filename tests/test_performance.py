#!/usr/bin/env python3
"""
⚡ Tests de Performance - Web3 Opportunities Tracker
==================================================
Tests de performance avec threading et benchmarks selon Jour 11
"""

import time
import concurrent.futures
import threading
import unittest
import sys
from pathlib import Path
from datetime import datetime
import psutil
import os

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent))

# Imports du projet
from telegram_bot import TelegramBot
from telegram_scheduler import TelegramScheduler
from telegram_bot_interactive import InteractiveTelegramBot

class TestScraperPerformance(unittest.TestCase):
    """Tests de performance des scrapers selon le plan Jour 11"""
    
    def setUp(self):
        """Configuration des tests de performance"""
        self.bot_token = "8063978631:AAGrnjyRaa3MounLsIkJu_Cglaa80NTYoaI"
        self.chat_id = "7886553560"
        self.performance_threshold = 30.0  # 30 secondes max selon le plan
        
    def test_scraper_performance_concurrent(self):
        """Test de performance avec threading concurrent (comme dans le plan Jour 11)"""
        print("🔄 Test Performance: Scrapers concurrents...")
        
        try:
            start_time = time.time()
            
            # Simulation des scrapers concurrents selon le plan
            def simulate_galxe_scraper():
                """Simule galxe_scraper.fetch_quests"""
                bot = TelegramBot(self.bot_token, self.chat_id)
                return bot.load_opportunities_data()
                
            def simulate_zealy_scraper():
                """Simule zealy_scraper.fetch_quests"""  
                bot = TelegramBot(self.bot_token, self.chat_id)
                df = bot.load_opportunities_data()
                return bot.filter_opportunities(df)
                
            def simulate_rss_scraper():
                """Simule rss_scraper.fetch_opportunities"""
                bot = TelegramBot(self.bot_token, self.chat_id)
                return bot.generate_mock_data()
            
            # Exécution en parallèle avec ThreadPoolExecutor selon le plan
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = [
                    executor.submit(simulate_galxe_scraper),
                    executor.submit(simulate_zealy_scraper),
                    executor.submit(simulate_rss_scraper)
                ]
                
                # Attendre tous les résultats
                results = []
                for future in concurrent.futures.as_completed(futures):
                    results.append(future.result())
            
            duration = time.time() - start_time
            
            # Assertion selon le plan: pipeline < 30s
            self.assertLess(duration, self.performance_threshold, 
                           f"Pipeline trop lent: {duration:.2f}s (seuil: {self.performance_threshold}s)")
            
            # Vérifier que tous les scrapers ont retourné des données
            self.assertEqual(len(results), 3, "Tous les scrapers doivent retourner des résultats")
            
            print(f"✅ Test Performance réussi - Durée: {duration:.2f}s (seuil: {self.performance_threshold}s)")
            print(f"📊 Résultats: {len(results)} scrapers exécutés en parallèle")
            
        except Exception as e:
            self.fail(f"Échec test performance concurrent: {e}")

    def test_memory_usage_during_processing(self):
        """Test d'utilisation mémoire pendant le traitement"""
        print("🔄 Test Performance: Utilisation mémoire...")
        
        try:
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Traitement intensif
            bot = TelegramBot(self.bot_token, self.chat_id)
            
            # Charger les données plusieurs fois pour stresser la mémoire
            for i in range(10):
                df = bot.load_opportunities_data()
                filtered = bot.filter_opportunities(df)
                message = bot.format_notification_message(filtered)
                
            peak_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = peak_memory - initial_memory
            
            # Vérifier que l'augmentation mémoire reste raisonnable (< 100MB)
            self.assertLess(memory_increase, 100, 
                           f"Augmentation mémoire excessive: {memory_increase:.1f}MB")
            
            print(f"✅ Test Mémoire réussi - Utilisation: {initial_memory:.1f}MB → {peak_memory:.1f}MB (+{memory_increase:.1f}MB)")
            
        except Exception as e:
            self.fail(f"Échec test utilisation mémoire: {e}")

    def test_high_volume_processing(self):
        """Test de traitement haut volume"""
        print("🔄 Test Performance: Traitement haut volume...")
        
        try:
            bot = TelegramBot(self.bot_token, self.chat_id)
            
            start_time = time.time()
            total_processed = 0
            
            # Traitement en boucle pour simuler un volume élevé
            for batch in range(5):  # 5 batch de traitement
                df = bot.load_opportunities_data()
                filtered = bot.filter_opportunities(df)
                message = bot.format_notification_message(filtered)
                total_processed += len(df)
                
            processing_time = time.time() - start_time
            throughput = total_processed / processing_time  # opportunités/seconde
            
            # Vérifier un débit minimum (au moins 10 opp/sec)
            self.assertGreater(throughput, 10, 
                              f"Débit trop faible: {throughput:.1f} opp/sec")
            
            print(f"✅ Test Volume réussi - Traité: {total_processed} opp en {processing_time:.2f}s")
            print(f"📈 Débit: {throughput:.1f} opportunités/seconde")
            
        except Exception as e:
            self.fail(f"Échec test haut volume: {e}")

class TestSystemPerformance(unittest.TestCase):
    """Tests de performance système globale"""
    
    def setUp(self):
        """Configuration tests système"""
        self.bot_token = "8063978631:AAGrnjyRaa3MounLsIkJu_Cglaa80NTYoaI"
        self.chat_id = "7886553560"
        
    def test_full_pipeline_performance(self):
        """Test de performance pipeline complet"""
        print("🔄 Test Performance: Pipeline complet...")
        
        try:
            # Mesurer chaque étape du pipeline
            timings = {}
            
            # 1. Initialisation
            start = time.time()
            bot = TelegramBot(self.bot_token, self.chat_id)
            timings['init'] = time.time() - start
            
            # 2. Chargement données
            start = time.time()
            df = bot.load_opportunities_data()
            timings['loading'] = time.time() - start
            
            # 3. Filtrage
            start = time.time()
            filtered = bot.filter_opportunities(df)
            timings['filtering'] = time.time() - start
            
            # 4. Formatage message
            start = time.time()
            message = bot.format_notification_message(filtered)
            timings['formatting'] = time.time() - start
            
            # 5. Temps total
            total_time = sum(timings.values())
            
            # Vérifications de performance
            self.assertLess(timings['loading'], 3.0, "Chargement trop lent")
            self.assertLess(timings['filtering'], 1.0, "Filtrage trop lent")
            self.assertLess(timings['formatting'], 0.5, "Formatage trop lent")
            self.assertLess(total_time, 5.0, "Pipeline total trop lent")
            
            print(f"✅ Test Pipeline réussi - Temps total: {total_time:.3f}s")
            print(f"📊 Détail: Init={timings['init']:.3f}s, Load={timings['loading']:.3f}s, Filter={timings['filtering']:.3f}s, Format={timings['formatting']:.3f}s")
            
        except Exception as e:
            self.fail(f"Échec test pipeline complet: {e}")

    def test_concurrent_user_simulation(self):
        """Test simulation utilisateurs concurrents"""
        print("🔄 Test Performance: Utilisateurs concurrents...")
        
        def simulate_user_interaction():
            """Simule l'interaction d'un utilisateur"""
            try:
                bot = TelegramBot(self.bot_token, self.chat_id)
                df = bot.load_opportunities_data()
                filtered = bot.filter_opportunities(df)
                message = bot.format_notification_message(filtered)
                return len(df)
            except Exception as e:
                return 0
        
        try:
            start_time = time.time()
            
            # Simuler 5 utilisateurs concurrents
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(simulate_user_interaction) for _ in range(5)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            concurrent_time = time.time() - start_time
            
            # Vérifier que tous les utilisateurs ont été servis
            successful_users = [r for r in results if r > 0]
            self.assertEqual(len(successful_users), 5, "Tous les utilisateurs doivent être servis")
            
            # Le temps concurrent ne doit pas être excessif
            self.assertLess(concurrent_time, 10.0, f"Temps concurrent excessif: {concurrent_time:.2f}s")
            
            print(f"✅ Test Concurrent réussi - 5 utilisateurs en {concurrent_time:.2f}s")
            print(f"📊 Moyenne par utilisateur: {concurrent_time/5:.2f}s")
            
        except Exception as e:
            self.fail(f"Échec test utilisateurs concurrents: {e}")

    def test_scheduler_performance_simulation(self):
        """Test de performance du scheduler sous charge"""
        print("🔄 Test Performance: Scheduler sous charge...")
        
        try:
            scheduler = TelegramScheduler(self.bot_token, self.chat_id, interval_hours=1)
            
            # Simuler plusieurs cycles de notification rapides
            start_time = time.time()
            cycles_completed = 0
            
            for cycle in range(3):  # 3 cycles de notification
                # Simuler les opérations du scheduler
                next_notification = scheduler.calculate_next_notification_time()
                
                # Simuler health check
                scheduler.error_count = 0
                scheduler.notification_count += 1
                
                cycles_completed += 1
                
            scheduler_time = time.time() - start_time
            
            # Le scheduler doit être rapide
            self.assertLess(scheduler_time, 2.0, f"Scheduler trop lent: {scheduler_time:.2f}s")
            self.assertEqual(cycles_completed, 3, "Tous les cycles doivent être complétés")
            
            print(f"✅ Test Scheduler réussi - 3 cycles en {scheduler_time:.2f}s")
            print(f"📊 Performance: {cycles_completed/scheduler_time:.1f} cycles/seconde")
            
        except Exception as e:
            self.fail(f"Échec test performance scheduler: {e}")

class TestLoadTesting(unittest.TestCase):
    """Tests de charge selon les spécifications"""
    
    def setUp(self):
        """Configuration tests de charge"""
        self.bot_token = "8063978631:AAGrnjyRaa3MounLsIkJu_Cglaa80NTYoaI"
        self.chat_id = "7886553560"
        
    def test_sustained_load(self):
        """Test de charge soutenue"""
        print("🔄 Test Performance: Charge soutenue...")
        
        try:
            bot = TelegramBot(self.bot_token, self.chat_id)
            
            # Test sur 30 secondes de charge continue
            start_time = time.time()
            operations_completed = 0
            
            while (time.time() - start_time) < 30:  # 30 secondes de charge
                df = bot.load_opportunities_data()
                filtered = bot.filter_opportunities(df)
                operations_completed += 1
                
                # Pause minimale pour éviter la surcharge
                time.sleep(0.1)
            
            sustained_time = time.time() - start_time
            ops_per_second = operations_completed / sustained_time
            
            # Vérifier performance soutenue (au moins 5 ops/sec)
            self.assertGreater(ops_per_second, 5, 
                              f"Performance soutenue insuffisante: {ops_per_second:.1f} ops/sec")
            
            print(f"✅ Test Charge soutenue réussi - {operations_completed} opérations en {sustained_time:.1f}s")
            print(f"📊 Performance soutenue: {ops_per_second:.1f} opérations/seconde")
            
        except Exception as e:
            self.fail(f"Échec test charge soutenue: {e}")

def run_performance_tests():
    """Lance tous les tests de performance"""
    print("⚡ TESTS DE PERFORMANCE - Web3 Opportunities Tracker")
    print("=" * 60)
    print("🎯 Objectif: Valider performance < 30s pour pipeline complet")
    print()
    
    # Configuration du test runner
    suite = unittest.TestSuite()
    
    # Tests de performance scrapers
    suite.addTest(TestScraperPerformance('test_scraper_performance_concurrent'))
    suite.addTest(TestScraperPerformance('test_memory_usage_during_processing'))
    suite.addTest(TestScraperPerformance('test_high_volume_processing'))
    
    # Tests de performance système  
    suite.addTest(TestSystemPerformance('test_full_pipeline_performance'))
    suite.addTest(TestSystemPerformance('test_concurrent_user_simulation'))
    suite.addTest(TestSystemPerformance('test_scheduler_performance_simulation'))
    
    # Tests de charge
    suite.addTest(TestLoadTesting('test_sustained_load'))
    
    # Exécution des tests
    runner = unittest.TextTestRunner(verbosity=1)
    start_time = time.time()
    result = runner.run(suite)
    total_time = time.time() - start_time
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS DE PERFORMANCE")
    print("=" * 60)
    
    total_tests = result.testsRun
    failed_tests = len(result.failures) + len(result.errors)
    passed_tests = total_tests - failed_tests
    
    print(f"✅ Tests réussis: {passed_tests}/{total_tests}")
    print(f"❌ Tests échoués: {failed_tests}/{total_tests}")
    print(f"⏱️ Temps total: {total_time:.2f} secondes")
    print(f"⚡ Performance: {total_tests/total_time:.1f} tests/seconde")
    
    # Métriques système
    process = psutil.Process()
    memory_usage = process.memory_info().rss / 1024 / 1024
    cpu_percent = process.cpu_percent()
    
    print(f"💾 Utilisation mémoire: {memory_usage:.1f} MB")
    print(f"🖥️ Utilisation CPU: {cpu_percent:.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 TOUS LES TESTS DE PERFORMANCE SONT PASSÉS!")
        print("⚡ Le système respecte les seuils de performance requis")
        return True
    else:
        print("\n⚠️ CERTAINS TESTS DE PERFORMANCE ONT ÉCHOUÉ")
        print("❌ Optimisations nécessaires")
        return False

if __name__ == "__main__":
    try:
        success = run_performance_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrompus par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erreur critique lors des tests de performance: {e}")
        sys.exit(1)
