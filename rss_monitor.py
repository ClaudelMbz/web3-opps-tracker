import feedparser
import requests

BINANCE_RSS_URL = "https://www.binance.com/en/support/announcement/rss.xml"
KEYWORDS = [
    "airdrop", "launchpool", "launchpad", "megadrop", 
    "listing", "rewards", "competition"
]

print(f"Téléchargement du flux RSS de Binance : {BINANCE_RSS_URL}")

try:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(BINANCE_RSS_URL, headers=headers)
    response.raise_for_status()

    # Sauvegarder le contenu brut dans un fichier pour le débogage
    with open("binance_feed_from_python.xml", "wb") as f:
        f.write(response.content)
    print("Le contenu brut du flux a été sauvegardé dans 'binance_feed_from_python.xml'")

    # Fournir le contenu téléchargé à feedparser
    feed = feedparser.parse(response.content)

    # --- Affichage des données brutes ---
    print("\n--- 10 DERNIÈRES ANNONCES BRUTES TÉLÉCHARGÉES ---\n")
    if not feed.entries:
        print("Le flux RSS semble vide ou n'a pas pu être analysé.")
    else:
        for entry in feed.entries[:10]: # On affiche les 10 premières
            print(f"Titre : {entry.title}")
            print(f"Lien  : {entry.link}\n---")
    # ------------------------------------

    print("\n--- RECHERCHE D'ANNONCES PERTINENTES (FILTRAGE) ---\n")
    
    found_items = 0
    for entry in feed.entries:
        title = entry.title.lower()
        if any(keyword in title for keyword in KEYWORDS):
            found_items += 1
            print(f"TROUVÉ - Titre : {entry.title}")
            print(f"Lien           : {entry.link}")
            print(f"Date           : {entry.published}\n---")

    if found_items == 0:
        print("Aucune annonce pertinente trouvée après filtrage.")

except requests.exceptions.RequestException as e:
    print(f"\nUne erreur est survenue lors du téléchargement du flux RSS : {e}")
except Exception as e:
    print(f"\nUne erreur inattendue est survenue : {e}")
