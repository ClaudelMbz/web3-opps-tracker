#!/usr/bin/env python3
"""
Test simplifié pour vérifier si le fix Galxe fonctionne
"""

import sys
import os
import json
from datetime import datetime

# Add path for imports
sys.path.insert(0, os.path.abspath('.'))

try:
    import requests
    from bs4 import BeautifulSoup
    
    print("✅ Imports réussis")
    
    # Test avec une requête simple d'abord
    print("\n🔄 Test de base avec Galxe...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get("https://galxe.com/explore", headers=headers, timeout=30)
        print(f"✅ Requête réussie: {response.status_code}, {len(response.text)} caractères")
        
        # Test du parsing
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Vérifier si la structure grid existe
        grid_container = soup.select_one("div.GridFlowContainer_grid-flow__m_iqK")
        if grid_container:
            print(f"✅ Container grid trouvé")
            child_count = len(grid_container.find_all())
            print(f"📊 Éléments enfants dans le grid: {child_count}")
        else:
            print("❌ Container grid non trouvé")
        
        # Tester les sélecteurs de la nouvelle logique
        selectors_to_test = [
            "div.GridFlowContainer_grid-flow__m_iqK > div",
            "div.GridFlowContainer_grid-flow__m_iqK > *", 
            "a[href*='/space/']",
            "a[href*='/quest/']",
            "main a[href]"
        ]
        
        results = {}
        for selector in selectors_to_test:
            items = soup.select(selector)
            results[selector] = len(items)
            if len(items) > 0:
                print(f"✅ {selector}: {len(items)} éléments trouvés")
            else:
                print(f"❌ {selector}: aucun élément")
        
        # Résumé du diagnostic
        print(f"\n📊 DIAGNOSTIC:")
        print(f"- Container grid présent: {'✅' if grid_container else '❌'}")
        print(f"- Total sélecteurs testés: {len(selectors_to_test)}")
        print(f"- Sélecteurs avec résultats: {sum(1 for count in results.values() if count > 0)}")
        
        # Si aucun lien /space/ n'est trouvé, c'est normal - contenu dynamique
        space_links = results.get("a[href*='/space/']", 0)
        if space_links == 0:
            print("⚠️  Aucun lien /space/ trouvé - NORMAL, contenu chargé dynamiquement")
            print("🔧 Solution: utiliser ScraperAPI avec wait_for ou Playwright")
        
        # Sauvegarder le résultat pour référence
        diagnostic_result = {
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "grid_container_found": grid_container is not None,
            "selector_results": results,
            "recommendation": "Use ScraperAPI with wait_for parameter or Playwright for dynamic content"
        }
        
        with open("galxe_diagnostic.json", "w", encoding='utf-8') as f:
            json.dump(diagnostic_result, f, indent=2, ensure_ascii=False)
        
        print("💾 Résultats sauvegardés dans galxe_diagnostic.json")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("Vérifiez que l'environnement virtuel est activé et que les dépendances sont installées")
