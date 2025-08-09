#!/usr/bin/env python3
"""
Test script pour vérifier la connexion Google Sheets
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from storage.google_sheets_auth import GoogleSheetsAuth

def test_google_sheets_connection():
    """Test la connexion à Google Sheets"""
    try:
        print("🔧 Initialisation de l'authentification Google Sheets...")
        
        # Initialiser l'authentification
        gs_auth = GoogleSheetsAuth('credentials.json')
        
        print("🔐 Tentative d'authentification...")
        gs_auth.authenticate()
        
        print("✅ Authentification réussie !")
        
        # Lister quelques feuilles de calcul disponibles (optionnel)
        try:
            print("📊 Tentative de listage des feuilles de calcul...")
            sheets = gs_auth.client.list()
            print(f"✅ Connexion confirmée ! {len(sheets)} feuilles de calcul trouvées.")
            
            # Afficher les premières feuilles (maximum 5)
            for i, sheet in enumerate(sheets[:5]):
                print(f"  📋 {i+1}. {sheet.title}")
                
        except Exception as e:
            print(f"⚠️  Impossible de lister les feuilles: {e}")
            print("   (L'authentification a fonctionné mais pas d'accès aux feuilles)")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'authentification: {e}")
        return False

if __name__ == "__main__":
    print("=== Test de connexion Google Sheets ===")
    success = test_google_sheets_connection()
    
    if success:
        print("\n🎉 Test terminé avec succès !")
    else:
        print("\n💥 Test échoué. Vérifiez vos credentials et permissions.")
