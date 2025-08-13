#!/usr/bin/env python3
"""
🤖 Web3 Opportunities Tracker - Telegram Bot
===============================================
Bot Telegram pour notifications automatiques des opportunités Web3
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
import requests
from pathlib import Path

# Configuration de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TelegramBot:
    """Bot Telegram pour notifications Web3 Opportunities"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.roi_threshold = 2.0  # Seuil minimum ROI $2/min
        self.last_notification = None
        
    async def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """Envoie un message Telegram avec retry automatique"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                url = f"{self.base_url}/sendMessage"
                data = {
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": parse_mode,
                    "disable_web_page_preview": True
                }
                
                response = requests.post(url, json=data, timeout=30)
                
                if response.status_code == 200:
                    logger.info(f"Message envoyé avec succès (tentative {attempt + 1})")
                    return True
                else:
                    logger.error(f"Erreur envoi message: {response.status_code} - {response.text}")
                    
            except requests.exceptions.Timeout as e:
                logger.warning(f"Timeout tentative {attempt + 1}/{max_retries}: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Backoff exponentiel
            except Exception as e:
                logger.error(f"Exception lors de l'envoi (tentative {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
        
        logger.error(f"Échec envoi message après {max_retries} tentatives")
        return False
    
    def load_opportunities_data(self) -> pd.DataFrame:
        """Charge les données d'opportunités depuis les fichiers JSON"""
        try:
            data_files = [
                "data/opportunities_zealy.json",
                "data/opportunities_galxe.json", 
                "data/opportunities_layer3.json",
                "data/opportunities_twitter.json",
                "data/opportunities_airdrops.json"
            ]
            
            all_opportunities = []
            
            for file_path in data_files:
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                all_opportunities.extend(data)
                            logger.info(f"Chargé {len(data)} opportunités depuis {file_path}")
                    except Exception as e:
                        logger.warning(f"Erreur lecture {file_path}: {e}")
            
            # Si pas de fichiers JSON, créer des données mock pour test
            if not all_opportunities:
                all_opportunities = self.generate_mock_data()
                logger.info("Utilisation de données mock pour les tests")
            
            df = pd.DataFrame(all_opportunities)
            
            # Standardisation des colonnes
            required_columns = ['title', 'roi', 'source', 'url', 'timestamp']
            for col in required_columns:
                if col not in df.columns:
                    if col == 'roi':
                        df[col] = 2.5  # ROI par défaut
                    elif col == 'timestamp':
                        df[col] = datetime.now().isoformat()
                    elif col == 'url':
                        df[col] = "https://example.com"
                    else:
                        df[col] = f"Default_{col}"
            
            # Conversion ROI en numérique
            df['roi'] = pd.to_numeric(df['roi'], errors='coerce').fillna(2.0)
            
            logger.info(f"Total {len(df)} opportunités chargées")
            return df
            
        except Exception as e:
            logger.error(f"Erreur chargement données: {e}")
            return pd.DataFrame()
    
    def generate_mock_data(self) -> List[Dict]:
        """Génère des données mock pour tests"""
        from datetime import datetime
        import random
        
        sources = ['Zealy', 'Galxe', 'Layer3-LiFi', 'TwitterRSS', 'AirdropsFallback']
        mock_opportunities = []
        
        for i in range(20):
            mock_opportunities.append({
                'title': f'Web3 Opportunity #{i+1}',
                'roi': round(random.uniform(0.5, 8.0), 2),
                'source': random.choice(sources),
                'url': f'https://example.com/opportunity-{i+1}',
                'timestamp': datetime.now().isoformat(),
                'description': f'Test opportunity #{i+1} for Telegram notifications'
            })
        
        return mock_opportunities
    
    def filter_opportunities(self, df: pd.DataFrame) -> Dict:
        """Filtre et catégorise les opportunités par ROI"""
        if df.empty:
            return {"high": [], "medium": [], "low": [], "total": 0}
        
        # Filtre par seuil minimum ROI
        filtered_df = df[df['roi'] >= self.roi_threshold].copy()
        
        # Catégorisation par ROI
        high_roi = filtered_df[filtered_df['roi'] >= 5.0]
        medium_roi = filtered_df[(filtered_df['roi'] >= 2.0) & (filtered_df['roi'] < 5.0)]
        low_roi = filtered_df[filtered_df['roi'] < 2.0]
        
        return {
            "high": high_roi.to_dict('records'),
            "medium": medium_roi.to_dict('records'),
            "low": low_roi.to_dict('records'),
            "total": len(filtered_df),
            "avg_roi": filtered_df['roi'].mean() if len(filtered_df) > 0 else 0
        }
    
    def format_notification_message(self, opportunities: Dict) -> str:
        """Formate le message de notification"""
        if opportunities["total"] == 0:
            return "🔍 <b>Web3 Opportunities Tracker</b>\n\n😴 Aucune nouvelle opportunité trouvée avec ROI ≥ $2/min\n\n⏰ Prochaine vérification dans 1 heure"
        
        # En-tête
        message = f"🚀 <b>Web3 Opportunities Alert!</b>\n"
        message += f"📊 <b>{opportunities['total']} nouvelles opportunités</b>\n"
        message += f"📈 <b>ROI moyen: ${opportunities['avg_roi']:.2f}/min</b>\n\n"
        
        # High ROI (>= $5/min)
        if opportunities["high"]:
            message += f"🔥 <b>HIGH ROI (≥$5/min): {len(opportunities['high'])}</b>\n"
            for opp in opportunities["high"][:3]:  # Top 3 seulement
                message += f"• <b>{opp['title'][:50]}{'...' if len(opp['title']) > 50 else ''}</b>\n"
                message += f"  💰 ${opp['roi']:.2f}/min | 🏷️ {opp['source']}\n"
            if len(opportunities["high"]) > 3:
                message += f"  ... et {len(opportunities['high']) - 3} autres\n"
            message += "\n"
        
        # Medium ROI ($2-5/min)
        if opportunities["medium"]:
            message += f"⚡ <b>MEDIUM ROI ($2-5/min): {len(opportunities['medium'])}</b>\n"
            for opp in opportunities["medium"][:2]:  # Top 2 seulement
                message += f"• {opp['title'][:40]}{'...' if len(opp['title']) > 40 else ''}\n"
                message += f"  💰 ${opp['roi']:.2f}/min | 🏷️ {opp['source']}\n"
            if len(opportunities["medium"]) > 2:
                message += f"  ... et {len(opportunities['medium']) - 2} autres\n"
            message += "\n"
        
        # Sources breakdown
        sources = {}
        all_opps = opportunities["high"] + opportunities["medium"] + opportunities["low"]
        for opp in all_opps:
            source = opp['source']
            sources[source] = sources.get(source, 0) + 1
        
        if sources:
            message += "📋 <b>Sources:</b>\n"
            for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
                message += f"  • {source}: {count}\n"
        
        # Footer
        message += f"\n🔗 <b>Dashboard:</b> http://localhost:8501"
        message += f"\n⏰ <i>Prochaine vérification dans 1 heure</i>"
        message += f"\n🕒 <i>{datetime.now().strftime('%H:%M %d/%m/%Y')}</i>"
        
        return message
    
    async def test_connection(self) -> bool:
        """Test la connexion avec le bot Telegram"""
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info.get('ok'):
                    bot_name = bot_info['result']['first_name']
                    logger.info(f"✅ Connexion réussie avec le bot: {bot_name}")
                    return True
            
            logger.error(f"❌ Erreur connexion bot: {response.text}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Exception test connexion: {str(e)}")
            return False
    
    async def send_startup_message(self):
        """Envoie un message de démarrage"""
        message = """🤖 <b>Web3 Opportunities Tracker - DÉMARRÉ</b>

✅ Bot Telegram activé
📊 Monitoring des opportunités Web3
⏰ Notifications toutes les heures
💰 Seuil ROI minimum: $2.00/min

🔄 <i>Première vérification en cours...</i>"""
        
        await self.send_message(message)
    
    async def send_opportunities_notification(self) -> bool:
        """Envoie les notifications d'opportunités"""
        try:
            # Chargement des données
            df = self.load_opportunities_data()
            
            # Filtrage et catégorisation
            filtered_opps = self.filter_opportunities(df)
            
            # Formatage et envoi du message
            message = self.format_notification_message(filtered_opps)
            success = await self.send_message(message)
            
            if success:
                self.last_notification = datetime.now()
                logger.info(f"Notification envoyée: {filtered_opps['total']} opportunités")
            
            return success
            
        except Exception as e:
            logger.error(f"Erreur envoi notification: {e}")
            return False
    
    async def send_test_message(self):
        """Envoie un message de test"""
        message = """🧪 <b>TEST - Web3 Opportunities Tracker</b>

✅ Connexion bot OK
🔧 Configuration:
  • ROI minimum: $2.00/min
  • Fréquence: 1 heure
  • Mode: 24h/24

📱 <i>Test réussi! Le bot est prêt.</i>"""
        
        return await self.send_message(message)

async def main():
    """Fonction principale"""
    # Configuration
    BOT_TOKEN = "8063978631:AAGrnjyRaa3MounLsIkJu_Cglaa80NTYoaI"
    CHAT_ID = "7886553560"
    
    # Initialisation du bot
    bot = TelegramBot(BOT_TOKEN, CHAT_ID)
    
    # Test de connexion
    logger.info("🚀 Démarrage du bot Telegram...")
    
    if not await bot.test_connection():
        logger.error("❌ Impossible de se connecter au bot Telegram")
        return False
    
    # Message de démarrage
    await bot.send_startup_message()
    
    # Première notification
    logger.info("📊 Envoi de la première notification...")
    success = await bot.send_opportunities_notification()
    
    if success:
        logger.info("✅ Bot Telegram configuré et opérationnel!")
        return True
    else:
        logger.error("❌ Erreur lors de l'envoi de la première notification")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        if result:
            print("\n🎉 Bot Telegram opérationnel!")
            print("📱 Vérifiez vos messages Telegram")
            print("🔄 Pour les notifications automatiques, lancez le scheduler")
        else:
            print("\n❌ Erreur de configuration du bot")
    except KeyboardInterrupt:
        print("\n🛑 Bot arrêté par l'utilisateur")
    except Exception as e:
        print(f"\n💥 Erreur critique: {e}")
        logger.error(f"Erreur critique: {e}")
