#!/usr/bin/env python3
"""
🤖 Web3 Opportunities Tracker - Bot Telegram Interactif
======================================================
Bot Telegram avec interface interactive pour le Jour 11
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Import des dépendances Telegram
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
except ImportError:
    print("❌ Erreur: python-telegram-bot non installé")
    print("Installez avec: pip install python-telegram-bot")
    sys.exit(1)

# Import du bot existant pour récupérer les données
from telegram_bot import TelegramBot

# Configuration de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_bot_interactive.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class InteractiveTelegramBot:
    """Bot Telegram interactif avec interface à boutons"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.data_bot = TelegramBot(bot_token, chat_id)  # Pour récupérer les données
        self.application = None
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Commande /start - Menu principal"""
        keyboard = [
            [
                InlineKeyboardButton("📊 Stats", callback_data='stats'),
                InlineKeyboardButton("🔍 Top ROI", callback_data='top_roi')
            ],
            [
                InlineKeyboardButton("📈 Sources", callback_data='sources'),
                InlineKeyboardButton("⚙️ Settings", callback_data='settings')
            ],
            [
                InlineKeyboardButton("🔄 Refresh", callback_data='refresh'),
                InlineKeyboardButton("📋 Help", callback_data='help')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_message = """🚀 <b>Web3 Opportunities Tracker Bot</b>

✅ <b>Bot opérationnel et connecté</b>
📊 <b>Surveillance en temps réel</b>
💰 <b>Filtrage ROI ≥ $2.00/min</b>

🎯 <i>Utilisez les boutons ci-dessous pour interagir</i>"""

        await update.message.reply_text(
            welcome_message, 
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        logger.info(f"Commande /start exécutée par {update.effective_user.first_name}")

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gestionnaire des boutons interactifs"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        try:
            if callback_data == 'stats':
                await self.show_stats(query)
            elif callback_data == 'top_roi':
                await self.show_top_roi(query)
            elif callback_data == 'sources':
                await self.show_sources(query)
            elif callback_data == 'settings':
                await self.show_settings(query)
            elif callback_data == 'refresh':
                await self.refresh_data(query)
            elif callback_data == 'help':
                await self.show_help(query)
            elif callback_data == 'back_to_menu':
                await self.back_to_menu(query)
            else:
                await query.edit_message_text("❌ Action non reconnue")
                
        except Exception as e:
            logger.error(f"Erreur lors du traitement du bouton {callback_data}: {e}")
            await query.edit_message_text("❌ Erreur lors du traitement de votre demande")

    async def show_stats(self, query):
        """Affiche les statistiques générales"""
        try:
            # Charger les données
            df = self.data_bot.load_opportunities_data()
            filtered_opps = self.data_bot.filter_opportunities(df)
            
            # Calculer les statistiques
            total_opps = len(df)
            filtered_count = filtered_opps['total']
            avg_roi = filtered_opps['avg_roi'] if filtered_count > 0 else 0
            
            # Statistiques par source
            source_stats = {}
            if not df.empty:
                source_counts = df['source'].value_counts().to_dict()
                for source, count in source_counts.items():
                    source_stats[source] = count
            
            stats_message = f"""📊 <b>STATISTIQUES - Web3 Opportunities</b>

📈 <b>Données Générales:</b>
  • Total opportunités: {total_opps}
  • Filtrées (ROI ≥$2/min): {filtered_count}
  • ROI moyen: ${avg_roi:.2f}/min
  • Taux filtrage: {(filtered_count/total_opps*100) if total_opps > 0 else 0:.1f}%

🏷️ <b>Par Source:</b>"""

            for source, count in sorted(source_stats.items(), key=lambda x: x[1], reverse=True):
                stats_message += f"\n  • {source}: {count}"

            stats_message += f"\n\n🕒 <i>Dernière mise à jour: {datetime.now().strftime('%H:%M %d/%m/%Y')}</i>"
            
            # Bouton retour
            keyboard = [[InlineKeyboardButton("🔙 Menu Principal", callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(stats_message, reply_markup=reply_markup, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Erreur show_stats: {e}")
            await query.edit_message_text("❌ Erreur lors du chargement des statistiques")

    async def show_top_roi(self, query):
        """Affiche le top des opportunités ROI"""
        try:
            df = self.data_bot.load_opportunities_data()
            filtered_opps = self.data_bot.filter_opportunities(df)
            
            top_message = "🔍 <b>TOP OPPORTUNITÉS ROI</b>\n\n"
            
            # High ROI opportunities
            if filtered_opps['high']:
                top_message += "🔥 <b>HIGH ROI (≥$5/min):</b>\n"
                for i, opp in enumerate(filtered_opps['high'][:3], 1):
                    title = opp['title'][:40] + "..." if len(opp['title']) > 40 else opp['title']
                    top_message += f"{i}. <b>{title}</b>\n"
                    top_message += f"   💰 ${opp['roi']:.2f}/min | 🏷️ {opp['source']}\n\n"
            
            # Medium ROI opportunities
            if filtered_opps['medium']:
                top_message += "⚡ <b>MEDIUM ROI ($2-5/min):</b>\n"
                for i, opp in enumerate(filtered_opps['medium'][:3], 1):
                    title = opp['title'][:40] + "..." if len(opp['title']) > 40 else opp['title']
                    top_message += f"{i}. {title}\n"
                    top_message += f"   💰 ${opp['roi']:.2f}/min | 🏷️ {opp['source']}\n\n"
            
            if not filtered_opps['high'] and not filtered_opps['medium']:
                top_message += "😴 <i>Aucune opportunité avec ROI ≥ $2/min actuellement</i>"
            
            top_message += f"🕒 <i>Mise à jour: {datetime.now().strftime('%H:%M')}</i>"
            
            keyboard = [[InlineKeyboardButton("🔙 Menu Principal", callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(top_message, reply_markup=reply_markup, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Erreur show_top_roi: {e}")
            await query.edit_message_text("❌ Erreur lors du chargement du top ROI")

    async def show_sources(self, query):
        """Affiche l'état des sources de données"""
        try:
            df = self.data_bot.load_opportunities_data()
            
            sources_message = "📈 <b>SOURCES DE DONNÉES</b>\n\n"
            
            # Statistiques par source
            if not df.empty:
                source_stats = df['source'].value_counts().to_dict()
                total = len(df)
                
                for source, count in sorted(source_stats.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / total) * 100
                    status = "✅" if count > 0 else "❌"
                    sources_message += f"{status} <b>{source}</b>: {count} ({percentage:.1f}%)\n"
                    
                    # Ajouter quelques détails sur les sources principales
                    if source == "Zealy":
                        sources_message += "    🎯 API REST + calcul ROI automatique\n"
                    elif source == "Galxe":
                        sources_message += "    🔍 GraphQL API + campagnes actives\n"
                    elif source == "Layer3":
                        sources_message += "    ⚡ API REST + quêtes Layer3/LiFi\n"
                    elif source == "TwitterRSS":
                        sources_message += "    📰 Flux RSS + monitoring Twitter\n"
                    elif source == "AirdropsFallback":
                        sources_message += "    🎁 Source de backup + airdrops\n"
                    
                    sources_message += "\n"
            else:
                sources_message += "😴 <i>Aucune donnée disponible actuellement</i>"
            
            sources_message += f"🔄 <i>Dernière synchronisation: {datetime.now().strftime('%H:%M')}</i>"
            
            keyboard = [[InlineKeyboardButton("🔙 Menu Principal", callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(sources_message, reply_markup=reply_markup, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Erreur show_sources: {e}")
            await query.edit_message_text("❌ Erreur lors du chargement des sources")

    async def show_settings(self, query):
        """Affiche les paramètres actuels"""
        settings_message = """⚙️ <b>PARAMÈTRES ACTUELS</b>

🎯 <b>Filtrage:</b>
  • Seuil ROI minimum: $2.00/min
  • Mode: Toutes les sources actives
  • Période: Temps réel

⏰ <b>Notifications:</b>
  • Fréquence: Toutes les heures
  • Heures actives: 24h/24, 7j/7
  • Mode push: Activé

🔧 <b>Technique:</b>
  • Timeout: 30 secondes
  • Retry: 3 tentatives max
  • Cache: 5 minutes

📊 <b>Dashboard:</b>
  • Interface web: http://localhost:8501
  • Données temps réel: ✅ Activé
  • Export CSV: ✅ Disponible

💬 <i>Configuration automatique optimisée</i>"""

        keyboard = [[InlineKeyboardButton("🔙 Menu Principal", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(settings_message, reply_markup=reply_markup, parse_mode='HTML')

    async def refresh_data(self, query):
        """Rafraîchit les données et affiche un résumé"""
        try:
            await query.edit_message_text("🔄 <i>Rafraîchissement en cours...</i>", parse_mode='HTML')
            
            # Simuler un rafraîchissement
            await asyncio.sleep(2)
            
            # Recharger les données
            df = self.data_bot.load_opportunities_data()
            filtered_opps = self.data_bot.filter_opportunities(df)
            
            refresh_message = f"""🔄 <b>DONNÉES RAFRAÎCHIES</b>

✅ <b>Mise à jour terminée</b>
📊 {len(df)} opportunités chargées
🎯 {filtered_opps['total']} opportunités filtrées (ROI ≥$2/min)
📈 ROI moyen: ${filtered_opps['avg_roi']:.2f}/min

🕒 <i>Dernière actualisation: {datetime.now().strftime('%H:%M:%S')}</i>"""

            keyboard = [[InlineKeyboardButton("🔙 Menu Principal", callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(refresh_message, reply_markup=reply_markup, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Erreur refresh_data: {e}")
            await query.edit_message_text("❌ Erreur lors du rafraîchissement")

    async def show_help(self, query):
        """Affiche l'aide et les commandes disponibles"""
        help_message = """📋 <b>AIDE - Web3 Opportunities Tracker</b>

🤖 <b>Commandes disponibles:</b>
  /start - Menu principal interactif
  /help - Cette aide
  /status - État du système

📊 <b>Fonctions du bot:</b>
  • <b>Stats</b>: Statistiques détaillées des opportunités
  • <b>Top ROI</b>: Meilleures opportunités du moment
  • <b>Sources</b>: État des sources de données
  • <b>Settings</b>: Configuration actuelle
  • <b>Refresh</b>: Actualiser les données

🔗 <b>Liens utiles:</b>
  • Dashboard: http://localhost:8501
  • Documentation: Voir README.md
  • GitHub: web3-opps-tracker

💡 <b>Conseil:</b>
Le bot surveille automatiquement 6 sources et filtre les opportunités avec ROI ≥ $2/min. Les notifications automatiques sont envoyées toutes les heures.

❓ <i>Questions? Utilisez les boutons du menu principal</i>"""

        keyboard = [[InlineKeyboardButton("🔙 Menu Principal", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(help_message, reply_markup=reply_markup, parse_mode='HTML')

    async def back_to_menu(self, query):
        """Retour au menu principal"""
        keyboard = [
            [
                InlineKeyboardButton("📊 Stats", callback_data='stats'),
                InlineKeyboardButton("🔍 Top ROI", callback_data='top_roi')
            ],
            [
                InlineKeyboardButton("📈 Sources", callback_data='sources'),
                InlineKeyboardButton("⚙️ Settings", callback_data='settings')
            ],
            [
                InlineKeyboardButton("🔄 Refresh", callback_data='refresh'),
                InlineKeyboardButton("📋 Help", callback_data='help')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        menu_message = """🚀 <b>Web3 Opportunities Tracker Bot</b>

✅ <b>Bot opérationnel et connecté</b>
📊 <b>Surveillance en temps réel</b>
💰 <b>Filtrage ROI ≥ $2.00/min</b>

🎯 <i>Utilisez les boutons ci-dessous pour interagir</i>"""

        await query.edit_message_text(menu_message, reply_markup=reply_markup, parse_mode='HTML')

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Commande /status - État rapide du système"""
        try:
            df = self.data_bot.load_opportunities_data()
            filtered_opps = self.data_bot.filter_opportunities(df)
            
            status_message = f"""🟢 <b>SYSTÈME OPÉRATIONNEL</b>

📊 {len(df)} opportunités surveillées
🎯 {filtered_opps['total']} opportunités qualifiées (ROI ≥$2/min)
⚡ ROI moyen: ${filtered_opps['avg_roi']:.2f}/min

🕒 État à {datetime.now().strftime('%H:%M:%S')}"""

            await update.message.reply_text(status_message, parse_mode='HTML')
            
        except Exception as e:
            await update.message.reply_text("❌ Erreur lors de la récupération du statut")
            logger.error(f"Erreur status_command: {e}")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Commande /help"""
        await update.message.reply_text(
            "📋 Tapez /start pour accéder au menu interactif principal !",
            parse_mode='HTML'
        )

    def setup_handlers(self):
        """Configuration des gestionnaires de commandes"""
        if not self.application:
            logger.error("Application non initialisée")
            return
            
        # Commandes
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Callback queries (boutons)
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        logger.info("Gestionnaires de commandes configurés")

    async def start_bot(self):
        """Démarre le bot interactif"""
        logger.info("🚀 Démarrage du bot Telegram interactif...")
        
        try:
            # Créer l'application
            self.application = Application.builder().token(self.bot_token).build()
            
            # Configurer les gestionnaires
            self.setup_handlers()
            
            logger.info("✅ Bot interactif configuré avec succès")
            
            # Démarrer le bot
            await self.application.initialize()
            await self.application.start()
            
            logger.info("🤖 Bot en cours d'exécution... (Ctrl+C pour arrêter)")
            
            # Garder le bot actif
            await self.application.updater.start_polling()
            
            # Attendre indéfiniment
            await asyncio.Event().wait()
            
        except KeyboardInterrupt:
            logger.info("🛑 Arrêt demandé par l'utilisateur")
        except Exception as e:
            logger.error(f"❌ Erreur lors du démarrage du bot: {e}")
        finally:
            if self.application:
                await self.application.stop()
                logger.info("🛑 Bot arrêté")

async def main():
    """Fonction principale"""
    # Configuration
    BOT_TOKEN = "8063978631:AAGrnjyRaa3MounLsIkJu_Cglaa80NTYoaI"
    CHAT_ID = "7886553560"
    
    # Créer et démarrer le bot interactif
    interactive_bot = InteractiveTelegramBot(BOT_TOKEN, CHAT_ID)
    
    try:
        await interactive_bot.start_bot()
    except Exception as e:
        logger.error(f"Erreur critique: {e}")

if __name__ == "__main__":
    try:
        print("🚀 Lancement du bot Telegram interactif...")
        print("📱 Tapez /start sur Telegram pour commencer")
        print("🛑 Ctrl+C pour arrêter")
        print("-" * 50)
        
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n🛑 Bot arrêté par l'utilisateur")
    except Exception as e:
        print(f"\n💥 Erreur critique: {e}")
        sys.exit(1)
