# FICHIER SUPPRIMÉ POUR DES RAISONS DE SÉCURITÉ
# Ce fichier contenait des références hardcodées à credentials.json
# et un SHEET_ID exposé
# 
# Pour réimplémenter Google Sheets de façon sécurisée :
# 1. Utiliser des variables d'environnement (.env)
# 2. Stocker les credentials via Vault ou variables d'environnement
# 3. Ne jamais exposer d'IDs ou de clés en dur dans le code
#
# Exemple de réimplémentation sécurisée :
# 
# import os
# from google.oauth2.service_account import Credentials
# from dotenv import load_dotenv
# 
# load_dotenv()
# 
# class SecureGoogleSheetsManager:
#     def __init__(self):
#         # Récupération sécurisée des credentials depuis l'environnement
#         self.service_account_info = {
#             "type": os.getenv("GOOGLE_TYPE"),
#             "project_id": os.getenv("GOOGLE_PROJECT_ID"),
#             "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
#             "private_key": os.getenv("GOOGLE_PRIVATE_KEY"),
#             "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
#             "client_id": os.getenv("GOOGLE_CLIENT_ID"),
#             "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
#             "token_uri": os.getenv("GOOGLE_TOKEN_URI")
#         }
#         self.sheet_id = os.getenv("GOOGLE_SHEET_ID")
