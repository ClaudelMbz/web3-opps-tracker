import unittest
import sys
import os

# Ajouter le chemin du projet pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from processing.roi_calculator import calculate_roi
from processing.deduplication import deduplicate_opportunities, hash_opportunity
from processing.roi_filter import filter_by_roi, categorize_by_roi

class TestROICalculator(unittest.TestCase):
    
    def test_roi_calculation_xp(self):
        """Test calcul ROI avec XP."""
        roi = calculate_roi(100, 5, "XP")  # 100 XP en 5 min
        self.assertEqual(roi, 0.2)  # $0.20/min
    
    def test_roi_calculation_gal(self):
        """Test calcul ROI avec GAL."""
        roi = calculate_roi(10, 5, "GAL")  # 10 GAL en 5 min
        self.assertEqual(roi, 1.0)  # $1.00/min
    
    def test_roi_calculation_usd(self):
        """Test calcul ROI avec USD."""
        roi = calculate_roi(50, 10, "USD")  # $50 en 10 min
        self.assertEqual(roi, 5.0)  # $5.00/min
    
    def test_roi_zero_time(self):
        """Test calcul ROI avec temps zéro (éviter division par 0)."""
        roi = calculate_roi(100, 0, "USD")
        self.assertEqual(roi, 100.0)  # Temps minimum = 1

class TestDeduplication(unittest.TestCase):
    
    def test_hash_opportunity(self):
        """Test génération de hash."""
        hash1 = hash_opportunity("Test Title", "https://test.com", "Description")
        hash2 = hash_opportunity("Test Title", "https://test.com", "Description")
        self.assertEqual(hash1, hash2)  # Même contenu = même hash
    
    def test_different_hash(self):
        """Test hash différents pour contenu différent."""
        hash1 = hash_opportunity("Title 1", "https://test1.com")
        hash2 = hash_opportunity("Title 2", "https://test2.com")
        self.assertNotEqual(hash1, hash2)
    
    def test_deduplicate_opportunities(self):
        """Test déduplication des opportunités."""
        opportunities = [
            {'title': 'Test 1', 'url': 'https://test1.com', 'description': 'Desc 1'},
            {'title': 'Test 2', 'url': 'https://test2.com', 'description': 'Desc 2'},
            {'title': 'Test 1', 'url': 'https://test1.com', 'description': 'Desc 1'},  # Doublon
        ]
        
        unique_ops = deduplicate_opportunities(opportunities)
        self.assertEqual(len(unique_ops), 2)  # 3 → 2 après déduplication
        
        # Vérifier que les hash sont ajoutés
        for op in unique_ops:
            self.assertIn('hash', op)

class TestROIFilter(unittest.TestCase):
    
    def setUp(self):
        """Préparer les données de test."""
        self.opportunities = [
            {'title': 'High ROI', 'roi': 6.0},
            {'title': 'Medium ROI', 'roi': 3.0},
            {'title': 'Low ROI', 'roi': 1.5},
            {'title': 'Zero ROI', 'roi': 0.0},
        ]
    
    def test_filter_by_roi(self):
        """Test filtrage par ROI minimum."""
        filtered = filter_by_roi(self.opportunities, min_roi=2.0)
        self.assertEqual(len(filtered), 2)  # High et Medium ROI
        
        # Vérifier le tri décroissant
        self.assertEqual(filtered[0]['roi'], 6.0)  # High ROI en premier
        self.assertEqual(filtered[1]['roi'], 3.0)  # Medium ROI en second
    
    def test_categorize_by_roi(self):
        """Test catégorisation par niveau de ROI."""
        categories = categorize_by_roi(self.opportunities)
        
        self.assertEqual(len(categories['high']), 1)    # ≥ $5/min
        self.assertEqual(len(categories['medium']), 1)  # $2-5/min
        self.assertEqual(len(categories['low']), 2)     # < $2/min

class TestIntegration(unittest.TestCase):
    
    def test_full_processing_pipeline(self):
        """Test du pipeline complet de processing."""
        # Données de test avec doublons
        raw_opportunities = [
            {'title': 'Airdrop 1', 'url': 'https://test1.com', 'reward_amount': 100, 'time_est_min': 5, 'currency': 'XP'},
            {'title': 'Airdrop 2', 'url': 'https://test2.com', 'reward_amount': 50, 'time_est_min': 10, 'currency': 'USD'},
            {'title': 'Airdrop 1', 'url': 'https://test1.com', 'reward_amount': 100, 'time_est_min': 5, 'currency': 'XP'},  # Doublon
        ]
        
        # 1. Calcul ROI
        for op in raw_opportunities:
            op['roi'] = calculate_roi(
                op.get('reward_amount', 10),
                op.get('time_est_min', 5),
                op.get('currency', 'USD')
            )
        
        # 2. Déduplication
        unique_ops = deduplicate_opportunities(raw_opportunities)
        self.assertEqual(len(unique_ops), 2)  # 3 → 2
        
        # 3. Filtrage ROI
        filtered_ops = filter_by_roi(unique_ops, min_roi=2.0)
        self.assertEqual(len(filtered_ops), 1)  # Seulement Airdrop 2 ($5/min)

if __name__ == '__main__':
    # Configurer la sortie des tests
    unittest.main(verbosity=2)
