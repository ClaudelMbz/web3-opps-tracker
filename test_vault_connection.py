#!/usr/bin/env python3
"""
Test de connexion Vault avant versioning
"""

import os
from vault_manager import VaultManager

def test_vault_connection():
    """Test simple de la connexion Vault"""
    try:
        # Initialiser VaultManager
        vault = VaultManager()
        
        # Vérifier l'authentification
        if vault.client.is_authenticated():
            print("✅ Connexion Vault réussie")
            
            # Test de lecture d'un secret existant
            try:
                test_secret = vault.retrieve_secret('scrapers/zealy')
                print(f"✅ Lecture du secret Zealy réussie (clés: {list(test_secret.keys())})")
                return True
            except Exception as e:
                print(f"⚠️  Erreur lors de la lecture du secret: {e}")
                return False
        else:
            print("❌ Authentification Vault échouée")
            return False
            
    except Exception as e:
        print(f"❌ Erreur de connexion Vault: {e}")
        return False

if __name__ == "__main__":
    success = test_vault_connection()
    if success:
        print("\n🎉 Vault est opérationnel - prêt pour le versioning!")
    else:
        print("\n💥 Problème avec Vault - à résoudre avant versioning")
