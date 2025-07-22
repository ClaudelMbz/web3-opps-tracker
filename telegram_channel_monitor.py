import asyncio
import json
import os
from telegram import Bot
from telegram.error import TelegramError

# --- Configuration ---
BOT_TOKEN = "7699564056:AAFW0RpupzOVFBUjDfEDbk_XAe5UXR5L_5k"
SOURCE_CHANNEL_ID = -1002096587825  # ID du canal à surveiller (Crypto_RewardsHub)
DESTINATION_CHAT_ID = 7886553560     # Votre ID personnel pour recevoir les messages
STATE_FILE = "telegram_monitor_state.json" # Fichier pour sauvegarder le dernier message traité

async def main():
    """
    Fonction principale pour initialiser le bot et lancer la surveillance.
    """
    bot = Bot(token=BOT_TOKEN)
    
    # Charger l'ID du dernier message traité
    last_message_id = 0
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
            last_message_id = state.get('last_message_id', 0)
    
    print("Moniteur de canal Telegram démarré.")
    print(f"Surveillance du canal : {SOURCE_CHANNEL_ID}")
    print(f"Dernier message traité : {last_message_id}")

    while True:
        try:
            # Récupérer les mises à jour (nouveaux messages) depuis le dernier message traité
            updates = await bot.get_updates(offset=last_message_id + 1, timeout=20, allowed_updates=["channel_post"])

            for update in updates:
                if update.channel_post:
                    message = update.channel_post
                    
                    # Vérifier si le message vient bien du canal que l'on veut surveiller
                    if message.chat.id == SOURCE_CHANNEL_ID:
                        text_to_check = message.text or message.caption or ""
                        text_to_check = text_to_check.lower()

                        # Condition de filtrage
                        is_relevant = "binance" in text_to_check or "https://www.binance.com/" in text_to_check

                        if is_relevant:
                            print(f"Message pertinent trouvé (ID: {message.message_id})! Transfert en cours...")
                            try:
                                # Transférer le message à la destination
                                await bot.forward_message(
                                    chat_id=DESTINATION_CHAT_ID,
                                    from_chat_id=SOURCE_CHANNEL_ID,
                                    message_id=message.message_id
                                )
                                print("Message transféré avec succès.")
                            except TelegramError as e:
                                print(f"Erreur lors du transfert du message : {e}")
                    
                    # Mettre à jour l'ID du dernier message traité
                    last_message_id = update.update_id

            # Sauvegarder le nouvel ID du dernier message
            with open(STATE_FILE, 'w') as f:
                json.dump({'last_message_id': last_message_id}, f)

        except TelegramError as e:
            print(f"Une erreur Telegram est survenue : {e}")
            # Attendre un peu avant de réessayer en cas de problème réseau
            await asyncio.sleep(30)
        except Exception as e:
            print(f"Une erreur inattendue est survenue : {e}")
            break # Arrêter en cas d'erreur grave

        # Attendre avant la prochaine vérification
        await asyncio.sleep(10)

if __name__ == "__main__":
    # Lancer la boucle d'événements asynchrones
    asyncio.run(main())
