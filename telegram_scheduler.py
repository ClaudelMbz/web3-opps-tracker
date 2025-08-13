#!/usr/bin/env python3
"""
⏰ Web3 Opportunities Tracker - Scheduler Telegram
==================================================
Scheduler automatique pour les notifications Telegram toutes les heures
"""

import asyncio
import signal
import sys
import logging
from datetime import datetime, timedelta
from typing import Optional
from telegram_bot import TelegramBot

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_scheduler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TelegramScheduler:
    """Scheduler pour les notifications Telegram automatiques"""
    
    def __init__(self, bot_token: str, chat_id: str, interval_hours: int = 1):
        self.bot = TelegramBot(bot_token, chat_id)
        self.interval_hours = interval_hours
        self.is_running = False
        self.next_notification = None
        self.notification_count = 0
        self.error_count = 0
        self.start_time = None
        
    def signal_handler(self, signum, frame):
        """Gestionnaire pour arrêt propre"""
        logger.info("🛑 Signal d'arrêt reçu, arrêt du scheduler...")
        self.is_running = False
    
    async def health_check(self) -> bool:
        """Vérification de la santé du système"""
        try:
            # Test connexion bot
            if not await self.bot.test_connection():
                logger.error("❌ Échec test connexion bot")
                self.error_count += 1
                return False
            
            # Vérifications système
            import os
            import psutil
            
            # Utilisation mémoire
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > 90:
                logger.warning(f"⚠️ Utilisation mémoire élevée: {memory_percent}%")
            
            # Espace disque
            disk_usage = psutil.disk_usage('.').percent
            if disk_usage > 90:
                logger.warning(f"⚠️ Espace disque faible: {disk_usage}%")
            
            logger.info(f"✅ Health check OK - RAM: {memory_percent}%, Disk: {disk_usage}%")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur health check: {e}")
            self.error_count += 1
            return False
    
    async def send_daily_report(self):
        """Envoie un rapport quotidien (à 8h00)"""
        try:
            now = datetime.now()
            if now.hour == 8 and now.minute < 30:  # Entre 8h00 et 8h30
                uptime = now - self.start_time if self.start_time else timedelta(0)
                
                message = f"""📊 <b>Rapport Quotidien - Web3 Opportunities Tracker</b>

⏰ <b>Statistiques 24h:</b>
  • Notifications envoyées: {self.notification_count}
  • Erreurs: {self.error_count}
  • Uptime: {uptime.days} jours, {uptime.seconds//3600}h{(uptime.seconds//60)%60}min

🔧 <b>Configuration:</b>
  • Fréquence: {self.interval_hours}h
  • Seuil ROI: $2.00/min
  • Mode: 24h/24

📱 <i>Système opérationnel</i>"""
                
                await self.bot.send_message(message)
                logger.info("📊 Rapport quotidien envoyé")
                
        except Exception as e:
            logger.error(f"❌ Erreur rapport quotidien: {e}")
    
    async def send_error_alert(self, error_msg: str):
        """Envoie une alerte d'erreur si trop d'erreurs consécutives"""
        if self.error_count >= 3:
            message = f"""🚨 <b>ALERTE SYSTÈME - Web3 Opportunities Tracker</b>

❌ <b>Erreurs consécutives détectées:</b> {self.error_count}

🔍 <b>Dernière erreur:</b>
{error_msg}

⏰ <b>Heure:</b> {datetime.now().strftime('%H:%M %d/%m/%Y')}

🔧 <i>Vérification système requise</i>"""
            
            try:
                await self.bot.send_message(message)
                logger.info("🚨 Alerte d'erreur envoyée")
            except:
                logger.error("❌ Impossible d'envoyer l'alerte d'erreur")
    
    async def run_notification_cycle(self):
        """Exécute un cycle de notification"""
        try:
            logger.info(f"🔄 Cycle de notification #{self.notification_count + 1}")
            
            # Health check
            if not await self.health_check():
                await self.send_error_alert("Health check failed")
                return False
            
            # Envoi notification
            success = await self.bot.send_opportunities_notification()
            
            if success:
                self.notification_count += 1
                self.error_count = 0  # Reset compteur erreurs
                logger.info(f"✅ Notification #{self.notification_count} envoyée avec succès")
            else:
                self.error_count += 1
                logger.error(f"❌ Échec notification (erreur #{self.error_count})")
                await self.send_error_alert(f"Notification failed (attempt #{self.error_count})")
            
            # Rapport quotidien si nécessaire
            await self.send_daily_report()
            
            return success
            
        except Exception as e:
            self.error_count += 1
            error_msg = f"Exception dans cycle notification: {str(e)}"
            logger.error(error_msg)
            await self.send_error_alert(error_msg)
            return False
    
    def calculate_next_notification_time(self) -> datetime:
        """Calcule l'heure de la prochaine notification"""
        now = datetime.now()
        next_time = now + timedelta(hours=self.interval_hours)
        
        # Aligner sur l'heure exacte (ex: 14:00 au lieu de 14:23)
        next_time = next_time.replace(minute=0, second=0, microsecond=0)
        
        return next_time
    
    async def start_scheduler(self):
        """Démarre le scheduler de notifications"""
        logger.info("🚀 Démarrage du scheduler Telegram...")
        self.start_time = datetime.now()
        self.is_running = True
        
        # Configuration des signaux pour arrêt propre
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Test initial de connexion
        if not await self.bot.test_connection():
            logger.error("❌ Impossible de se connecter au bot Telegram")
            return False
        
        # Message de démarrage
        await self.bot.send_startup_message()
        logger.info("✅ Scheduler initialisé avec succès")
        
        # Première notification immédiate
        await self.run_notification_cycle()
        
        # Boucle principale
        while self.is_running:
            try:
                # Calculer temps d'attente jusqu'à la prochaine notification
                self.next_notification = self.calculate_next_notification_time()
                wait_seconds = (self.next_notification - datetime.now()).total_seconds()
                
                if wait_seconds > 0:
                    logger.info(f"⏰ Prochaine notification: {self.next_notification.strftime('%H:%M %d/%m/%Y')}")
                    logger.info(f"💤 Attente de {wait_seconds/60:.1f} minutes...")
                    
                    # Attendre avec vérifications périodiques
                    while wait_seconds > 0 and self.is_running:
                        sleep_time = min(300, wait_seconds)  # Max 5 minutes à la fois
                        await asyncio.sleep(sleep_time)
                        wait_seconds -= sleep_time
                
                # Exécuter le cycle de notification si toujours en cours
                if self.is_running:
                    await self.run_notification_cycle()
                
            except Exception as e:
                self.error_count += 1
                logger.error(f"❌ Erreur dans la boucle principale: {e}")
                await self.send_error_alert(f"Erreur boucle principale: {str(e)}")
                
                # Pause avant redémarrage
                await asyncio.sleep(300)  # 5 minutes
        
        logger.info("🛑 Scheduler arrêté")
        return True
    
    async def stop_scheduler(self):
        """Arrête le scheduler proprement"""
        self.is_running = False
        
        # Message d'arrêt
        message = f"""🛑 <b>Web3 Opportunities Tracker - ARRÊTÉ</b>

📊 <b>Statistiques finales:</b>
  • Notifications envoyées: {self.notification_count}
  • Erreurs: {self.error_count}
  • Durée fonctionnement: {datetime.now() - self.start_time if self.start_time else 'N/A'}

🔄 <i>Scheduler arrêté proprement</i>"""
        
        try:
            await self.bot.send_message(message)
        except:
            logger.warning("⚠️ Impossible d'envoyer le message d'arrêt")

async def main():
    """Fonction principale du scheduler"""
    # Configuration
    BOT_TOKEN = "8063978631:AAGrnjyRaa3MounLsIkJu_Cglaa80NTYoaI"
    CHAT_ID = "7886553560"
    INTERVAL_HOURS = 1  # Notifications toutes les heures
    
    # Initialisation du scheduler
    scheduler = TelegramScheduler(BOT_TOKEN, CHAT_ID, INTERVAL_HOURS)
    
    try:
        # Démarrage du scheduler
        await scheduler.start_scheduler()
        
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"💥 Erreur critique du scheduler: {e}")
    finally:
        # Arrêt propre
        await scheduler.stop_scheduler()

if __name__ == "__main__":
    try:
        print("🚀 Démarrage du Scheduler Telegram...")
        print("📱 Notifications toutes les heures")
        print("🛑 Ctrl+C pour arrêter proprement")
        print("-" * 50)
        
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n🛑 Scheduler arrêté par l'utilisateur")
    except Exception as e:
        print(f"\n💥 Erreur critique: {e}")
        sys.exit(1)
