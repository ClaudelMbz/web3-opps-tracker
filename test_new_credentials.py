#!/usr/bin/env python3
# Test simple avec le nouveau compte de service

import sys
import os
from datetime import datetime

# Ajouter le chemin du module storage
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'storage'))

from google_sheets_auth import GoogleSheetsAuth

def test_new_service_account():
    """Test avec le nouveau compte de service"""
    print("🧪 === TEST NOUVEAU COMPTE DE SERVICE ===\n")
    
    credentials_file = "web3oppstracker-9663d96f6a7e.json"
    
    # Vérifier que le fichier existe
    if not os.path.exists(credentials_file):
        print(f"❌ Fichier credentials non trouvé: {credentials_file}")
        return False
    
    print(f"✅ Fichier credentials trouvé: {credentials_file}")
    
    # Test avec données simples
    test_data = [
        {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'title': 'Test Nouveau Service Account',
            'source': 'Test_Service',
            'reward': '100 USD',
            'estimated_time': 5,
            'roi': 20.0,
            'url': 'https://test-service-account.com',
            'hash': 'new_service_test_001'
        }
    ]
    
    try:
        # Initialiser avec nouveau credentials
        gs_auth = GoogleSheetsAuth(credentials_file)
        
        print("🔐 Tentative d'authentification...")
        gs_auth.authenticate()
        
        print("📊 Création/ouverture de la feuille...")
        sheet = gs_auth.setup_google_sheets()
        
        print("📝 Ajout des données de test...")
        gs_auth.push_to_sheets(test_data)
        
        # Afficher l'URL de la feuille
        sheet_url = gs_auth.get_sheet_url()
        if sheet_url:
            print(f"\n🔗 SUCCÈS ! Feuille créée: {sheet_url}")
        
        print("\n✅ Test réussi avec le nouveau compte de service !")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors du test: {e}")
        print(f"Type d'erreur: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_new_service_account()
    if success:
        print("\n🎉 Le nouveau compte de service fonctionne !")
    else:
        print("\n⚠️ Le nouveau compte de service a des problèmes.")
