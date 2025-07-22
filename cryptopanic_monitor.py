import requests
import json

# --- Configuration ---
CRYPTO_PANIC_API_KEY = "bdbe636bba2ecd8d597781a67a1275eec332d90b"
API_URL = "https://cryptopanic.com/api/v1/posts/"

# Mots-clés à rechercher dans les titres des nouvelles (en minuscules)
KEYWORDS = [
    "airdrop", "launchpool", "launchpad", "megadrop",
    "listing", "rewards", "competition"
]

print("Interrogation de l'API de CryptoPanic pour les nouvelles sur Binance...")

try:
    params = {
        "auth_token": CRYPTO_PANIC_API_KEY,
        "public": "true",
        "currencies": "BNB" 
    }

    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    data = response.json()

    # --- Affichage des données brutes reçues ---
    print("\n--- DONNÉES BRUTES REÇUES DE CRYPTOPANIC ---\n")
    print(json.dumps(data, indent=4))
    print("\n--- FIN DES DONNÉES BRUTES ---\n")
    # ---------------------------------------------

    if 'results' in data and data['results']:
        print("\n--- Filtrage des nouvelles pertinentes ---\n")
        
        found_items = 0
        for post in data['results']:
            title = post.get('title', '').lower()

            if any(keyword in title for keyword in KEYWORDS):
                found_items += 1
                print(f"Titre : {post.get('title', 'Titre non disponible')}")
                if post.get('source'):
                    print(f"Source: {post.get('source', {}).get('title', 'Source non disponible')}")
                print(f"Lien  : {post.get('url', 'Lien non disponible')}\n---")

        if found_items == 0:
            print("Aucune nouvelle correspondant à vos mots-clés n'a été trouvée après filtrage.")

    else:
        print("Aucune nouvelle trouvée sur CryptoPanic pour Binance en ce moment.")

except requests.exceptions.RequestException as e:
    print(f"\nUne erreur est survenue lors de la communication avec l'API de CryptoPanic : {e}")
except Exception as e:
    print(f"\nUne erreur inattendue est survenue : {e}")