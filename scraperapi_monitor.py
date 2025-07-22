import requests
import feedparser

# --- Configuration ---
SCRAPERAPI_KEY = "cd06c95002214ffbe6708dbaca1c7c28"
# On cible le flux RSS, qui est une source de données plus propre
TARGET_URL = "https://www.binance.com/en/support/announcement/rss.xml"

# Mots-clés pour filtrer les annonces
KEYWORDS = [
    "airdrop", "launchpool", "launchpad", "megadrop", 
    "listing", "rewards", "competition"
]

# Construire l'URL de l'API pour ScraperAPI. Pas besoin de rendu JS pour un flux RSS.
api_url = f"http://api.scraperapi.com/?api_key={SCRAPERAPI_KEY}&url={TARGET_URL}"

print("Interrogation du flux RSS de Binance via ScraperAPI...")

try:
    # Effectuer la requête à ScraperAPI
    response = requests.get(api_url)
    response.raise_for_status()

    # Le contenu du flux RSS est dans la réponse de ScraperAPI
    rss_content = response.content

    # Analyser le contenu RSS avec feedparser
    feed = feedparser.parse(rss_content)

    print("\n--- Annonces Pertinentes Trouvées via ScraperAPI & RSS ---\n")
    
    found_items = 0
    if not feed.entries:
        print("Le flux RSS est vide ou n'a pas pu être analysé, même via ScraperAPI.")
    else:
        for entry in feed.entries:
            title = entry.title.lower()

            if any(keyword in title for keyword in KEYWORDS):
                found_items += 1
                print(f"Titre : {entry.title}")
                print(f"Lien  : {entry.link}")
                print(f"Date  : {entry.published}\n---")

    if found_items == 0:
        print("Aucune annonce pertinente trouvée dans les dernières publications du flux RSS.")

except requests.exceptions.RequestException as e:
    print(f"\nUne erreur est survenue lors de la communication avec ScraperAPI : {e}")
except Exception as e:
    print(f"\nUne erreur inattendue est survenue : {e}")