import gspread
import json
import os
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import traceback

# Configuration initiale
load_dotenv()

class GoogleSheetsManager:
    def __init__(self):
        self.client = None
        self.sheet = None
        
    def validate_credentials(self, file_path='credentials.json'):
        """Valide le fichier credentials.json"""
        try:
            with open(file_path) as f:
                creds_data = json.load(f)
            
            required_fields = [
                'type', 'project_id', 'private_key_id', 'private_key',
                'client_email', 'client_id', 'auth_uri', 'token_uri',
                'auth_provider_x509_cert_url', 'client_x509_cert_url'
            ]
            
            if missing := [f for f in required_fields if f not in creds_data]:
                print(f"❌ Champs manquants: {', '.join(missing)}")
                return False
            
            print("✅ Fichier credentials.json valide")
            return True
            
        except FileNotFoundError:
            print(f"❌ Fichier introuvable: {file_path}")
            return False
        except json.JSONDecodeError:
            print(f"❌ Fichier JSON invalide: {file_path}")
            return False

    def connect(self):
        """Établit la connexion à Google Sheets"""
        try:
            if not self.validate_credentials():
                return False
                
            creds = Credentials.from_service_account_file(
                'credentials.json',
                scopes=[
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive'
                ]
            )
            
            self.client = gspread.authorize(creds)
            return True
            
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            traceback.print_exc()
            return False

    def open_sheet(self, sheet_id, sheet_name=None):
        """Ouvre une feuille spécifique"""
        try:
            spreadsheet = self.client.open_by_key(sheet_id)
            self.sheet = spreadsheet.worksheet(sheet_name) if sheet_name else spreadsheet.sheet1
            print(f"✅ Feuille ouverte: {self.sheet.title}")
            return True
        except Exception as e:
            print(f"❌ Impossible d'ouvrir la feuille: {e}")
            return False

    def update_cell(self, cell, value):
        """Met à jour une cellule (méthode moderne)"""
        try:
            # Méthode recommandée sans avertissement
            self.sheet.update(values=[[value]], range_name=cell)
            print(f"📝 Cellule {cell} mise à jour: '{value}'")
            return True
        except Exception as e:
            print(f"❌ Échec de mise à jour: {e}")
            return False

    def read_cell(self, cell):
        """Lit une cellule"""
        try:
            value = self.sheet.acell(cell).value
            print(f"📖 Valeur lue depuis {cell}: '{value}'")
            return value
        except Exception as e:
            print(f"❌ Échec de lecture: {e}")
            return None

def main():
    # Configuration
    SHEET_ID = "1mAZENtCNuVFz0bis22HpUYIFwa-BGo0Lq74IhwUltPo"
    CELL_TO_UPDATE = 'A1'
    TEST_MESSAGE = '✅ Connexion réussie !'

    # Initialisation
    gs_manager = GoogleSheetsManager()
    
    # Connexion
    if not gs_manager.connect():
        print("❌ Échec de la connexion")
        return
    
    # Ouverture de la feuille
    if not gs_manager.open_sheet(SHEET_ID):
        print("❌ Échec d'ouverture de la feuille")
        return
    
    # Mise à jour de cellule
    if not gs_manager.update_cell(CELL_TO_UPDATE, TEST_MESSAGE):
        print("❌ Échec de l'écriture")
        return
    
    # Lecture de vérification
    gs_manager.read_cell(CELL_TO_UPDATE)

if __name__ == "__main__":
    main()