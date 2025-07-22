import os
from telethon import TelegramClient
from dotenv import load_dotenv

# --- Configuration ---
# Charge les variables d'environnement du fichier .env
load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')

# Le nom du fichier de session doit être EXACTEMENT le même que dans app.py
session_name = 'telegram_user_session'

# --- Validation ---
if not all([api_id, api_hash]):
    raise ValueError("API_ID ou API_HASH est manquant dans le fichier .env. Veuillez les ajouter.")

print("Lancement de la création de la session...")
print("Telethon va vous demander de vous connecter.")
print("Veuillez entrer votre numéro de téléphone, puis le code reçu sur Telegram.")

# Le 'with' garantit que le client se connecte et se déconnecte proprement
# C'est pendant cette connexion que le fichier .session est créé
try:
    with TelegramClient(session_name, int(api_id), api_hash) as client:
        if client.is_connected():
            print("\n----------------------------------------------------")
            print("✅ Connexion réussie !")
            print(f"Le fichier de session '{session_name}.session' a été créé avec succès.")
            print("Vous pouvez maintenant l'ajouter à votre dépôt Git.")
            print("----------------------------------------------------")
        else:
            print("\n❌ La connexion a échoué. Veuillez vérifier vos identifiants.")

except Exception as e:
    print(f"\nUne erreur est survenue : {e}")

