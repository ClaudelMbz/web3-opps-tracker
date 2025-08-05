#!/usr/bin/env python3
# storage/notion_integration.py - Intégration Notion pour Jour 7

import requests
import json
from datetime import datetime
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class NotionIntegration:
    def __init__(self, notion_token=None, database_id=None):
        self.notion_token = notion_token or os.getenv('NOTION_TOKEN')
        self.database_id = database_id or os.getenv('NOTION_DATABASE_ID')
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
    def validate_connection(self) -> bool:
        """Valide la connexion à Notion"""
        try:
            if not self.notion_token:
                print("❌ Token Notion manquant")
                return False
                
            # Test de connexion
            response = requests.get(
                f"{self.base_url}/users/me",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_info = response.json()
                print(f"✅ Connexion Notion réussie - Utilisateur: {user_info.get('name', 'N/A')}")
                return True
            else:
                print(f"❌ Erreur connexion Notion: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur validation Notion: {e}")
            return False
    
    def add_opportunity(self, opportunity: Dict[str, Any]) -> bool:
        """Ajoute une opportunité à la base de données Notion"""
        try:
            if not self.database_id:
                print("❌ Database ID Notion manquant")
                return False
            
            # Calculer la priorité basée sur le ROI
            roi = opportunity.get('roi', 0)
            if roi >= 10:
                priority = "🔥 High"
            elif roi >= 5:
                priority = "⚡ Medium"
            else:
                priority = "📝 Low"
            
            page_data = {
                "parent": {"database_id": self.database_id},
                "properties": {
                    "Title": {
                        "title": [
                            {"text": {"content": opportunity.get('title', 'Untitled')}}
                        ]
                    },
                    "Source": {
                        "select": {"name": opportunity.get('source', 'Unknown')}
                    },
                    "Reward": {
                        "rich_text": [
                            {"text": {"content": str(opportunity.get('reward', ''))}}
                        ]
                    },
                    "ROI": {"number": float(opportunity.get('roi', 0))},
                    "Time": {"number": int(opportunity.get('estimated_time', 0))},
                    "Status": {"select": {"name": "New"}},
                    "Priority": {"select": {"name": priority}},
                    "URL": {"url": opportunity.get('url', '')},
                    "Date": {
                        "date": {
                            "start": opportunity.get('timestamp', datetime.now().isoformat())[:10]
                        }
                    },
                    "Hash": {
                        "rich_text": [
                            {"text": {"content": opportunity.get('hash', '')}}
                        ]
                    }
                }
            }
            
            response = requests.post(
                f"{self.base_url}/pages",
                headers=self.headers,
                json=page_data,
                timeout=15
            )
            
            if response.status_code == 200:
                return True
            else:
                print(f"❌ Erreur ajout Notion: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur ajout opportunité: {e}")
            return False
    
    def sync_opportunities(self, opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synchronise plusieurs opportunités vers Notion"""
        if not opportunities:
            print("⚠️ Aucune opportunité à synchroniser")
            return {"success": 0, "errors": 0}
        
        results = {"success": 0, "errors": 0}
        
        for opportunity in opportunities:
            if self.add_opportunity(opportunity):
                results["success"] += 1
            else:
                results["errors"] += 1
        
        print(f"📊 Notion Sync: {results['success']} réussies, {results['errors']} erreurs")
        return results

def test_notion_integration():
    """Test de l'intégration Notion"""
    print("🧪 === TEST INTÉGRATION NOTION ===\n")
    
    notion = NotionIntegration()
    if not notion.validate_connection():
        print("⚠️ Configuration Notion nécessaire - voir NOTION_SETUP_GUIDE.md")
        return False
    
    # Test avec une opportunité
    test_opportunity = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'title': 'Test Notion Integration',
        'source': 'Galxe',
        'reward': '100 USD',
        'estimated_time': 5,
        'roi': 20.0,
        'url': 'https://galxe.com/test',
        'hash': 'notion_test_001'
    }
    
    results = notion.sync_opportunities([test_opportunity])
    
    if results["success"] > 0:
        print("✅ Test Notion RÉUSSI")
        return True
    else:
        print("❌ Test Notion ÉCHOUÉ")
        return False

if __name__ == "__main__":
    test_notion_integration()
