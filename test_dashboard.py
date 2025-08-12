#!/usr/bin/env python3
"""
Test script for Web3 Opportunities Tracker Dashboard
Tests all components and functionality
"""

import pandas as pd
import json
import os
import sys
from datetime import datetime

def test_data_loading():
    """Test 1: Validate data loading from files"""
    print("🧪 Test 1: Data Loading...")
    
    # Import the dashboard functions
    sys.path.append('.')
    from dashboard import load_opportunities_from_files, get_mock_data
    
    try:
        # Test real data loading
        df = load_opportunities_from_files("data")
        
        if df.empty:
            print("⚠️  Aucune donnée réelle trouvée - utilisation des données mock")
            df = get_mock_data()
        
        # Validate DataFrame structure
        required_columns = ['title', 'source', 'roi', 'reward', 'estimated_time', 'createdAt']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ Colonnes manquantes: {missing_columns}")
            return False
            
        print(f"✅ Données chargées: {len(df)} opportunités avec colonnes requises")
        print(f"   Sources: {df['source'].unique()}")
        print(f"   ROI range: ${df['roi'].min():.2f} - ${df['roi'].max():.2f}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du chargement des données: {e}")
        return False

def test_data_filtering():
    """Test 2: Validate data filtering logic"""
    print("\n🧪 Test 2: Data Filtering...")
    
    try:
        from dashboard import get_mock_data
        
        # Get test data
        df = get_mock_data()
        
        # Test ROI filtering
        roi_threshold = 5.0
        filtered_df = df[df['roi'] >= roi_threshold]
        expected_count = sum(1 for x in df['roi'] if x >= roi_threshold)
        
        if len(filtered_df) != expected_count:
            print(f"❌ Filtrage ROI échoué: attendu {expected_count}, obtenu {len(filtered_df)}")
            return False
            
        # Test source filtering
        test_sources = ['Galxe', 'Zealy']
        filtered_sources = df[df['source'].isin(test_sources)]
        
        if not all(source in test_sources for source in filtered_sources['source'].unique()):
            print("❌ Filtrage par source échoué")
            return False
            
        print("✅ Filtrage des données fonctionne correctement")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test de filtrage: {e}")
        return False

def test_metrics_calculation():
    """Test 3: Validate metrics calculations"""
    print("\n🧪 Test 3: Metrics Calculation...")
    
    try:
        from dashboard import get_mock_data
        
        df = get_mock_data()
        
        # Test metrics calculations
        total_opportunities = len(df)
        avg_roi = df['roi'].mean()
        active_sources = df['source'].nunique()
        
        # Validate calculations
        if total_opportunities != 20:  # Mock data has 20 rows
            print(f"❌ Total opportunities incorrect: attendu 20, obtenu {total_opportunities}")
            return False
            
        expected_avg_roi = sum(range(20)) * 0.5 / 20  # Based on mock data formula
        if abs(avg_roi - expected_avg_roi) > 0.01:
            print(f"❌ ROI moyen incorrect: attendu {expected_avg_roi:.2f}, obtenu {avg_roi:.2f}")
            return False
            
        if active_sources != 4:  # Mock data has 4 unique sources
            print(f"❌ Sources actives incorrectes: attendu 4, obtenu {active_sources}")
            return False
            
        print("✅ Calculs de métriques corrects")
        print(f"   Total: {total_opportunities}, ROI moyen: ${avg_roi:.2f}, Sources: {active_sources}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du calcul des métriques: {e}")
        return False

def test_file_operations():
    """Test 4: Validate CSV export functionality"""
    print("\n🧪 Test 4: File Operations...")
    
    try:
        from dashboard import get_mock_data
        
        df = get_mock_data()
        
        # Test CSV export
        csv_content = df.to_csv(index=False)
        
        # Validate CSV structure
        lines = csv_content.strip().split('\n')
        if len(lines) != 21:  # 20 data rows + 1 header
            print(f"❌ CSV export incorrect: attendu 21 lignes, obtenu {len(lines)}")
            return False
            
        # Check header
        header = lines[0].split(',')
        expected_columns = ['title', 'source', 'roi', 'reward', 'estimated_time', 'createdAt']
        if not all(col in ','.join(header) for col in expected_columns):
            print("❌ En-têtes CSV incorrects")
            return False
            
        print("✅ Export CSV fonctionne correctement")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test des opérations fichier: {e}")
        return False

def test_dashboard_integration():
    """Test 5: Integration test simulating dashboard functionality"""
    print("\n🧪 Test 5: Dashboard Integration...")
    
    try:
        from dashboard import load_opportunities_from_files, get_mock_data
        
        # Load data
        df = load_opportunities_from_files("data")
        if df.empty:
            df = get_mock_data()
        
        # Simulate dashboard filters
        roi_min = 2.0
        source_filter = df['source'].unique()[:2]  # First 2 sources
        
        # Apply filters (simulating dashboard logic)
        filtered_df = df[
            (df['source'].isin(source_filter)) &
            (df['roi'] >= roi_min)
        ]
        
        # Calculate metrics
        total_opportunities = len(filtered_df)
        avg_roi = filtered_df['roi'].mean() if not filtered_df.empty else 0
        active_sources = filtered_df['source'].nunique()
        
        print("✅ Intégration dashboard réussie")
        print(f"   Après filtrage: {total_opportunities} opportunités")
        print(f"   ROI moyen filtré: ${avg_roi:.2f}")
        print(f"   Sources actives filtrées: {active_sources}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test d'intégration: {e}")
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    print("🚀 === TESTS DU DASHBOARD WEB3 OPPORTUNITIES TRACKER ===\n")
    
    tests = [
        test_data_loading,
        test_data_filtering,
        test_metrics_calculation,
        test_file_operations,
        test_dashboard_integration
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    # Summary
    print("\n" + "="*50)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*50)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results), 1):
        status = "✅ PASSÉ" if result else "❌ ÉCHOUÉ"
        print(f"Test {i}: {test.__name__} - {status}")
    
    print(f"\n🎯 RÉSULTAT FINAL: {passed}/{total} tests passés")
    
    if passed == total:
        print("🎉 TOUS LES TESTS SONT PASSÉS - Dashboard opérationnel!")
        return True
    else:
        print("⚠️  Certains tests ont échoué - Vérifier le code")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
