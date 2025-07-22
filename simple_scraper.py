import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

URL = "https://www.binance.com/en/support/announcement/list/93"
SCREENSHOT_FILE = "debug_screenshot.png"

print(f"Lancement d'une navigation simulée pour : {URL}")

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) # headless=False pour voir le navigateur s'ouvrir
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        print("Navigation vers l'URL...")
        page.goto(URL, wait_until='domcontentloaded', timeout=60000)
        
        print("Attente de 5 secondes pour le chargement dynamique...")
        time.sleep(5)
        
        print(f"Prise d'une capture d'écran : {SCREENSHOT_FILE}")
        page.screenshot(path=SCREENSHOT_FILE)

        html_content = page.content()
        browser.close()

    soup = BeautifulSoup(html_content, 'html.parser')
    selector = "a.css-s61a6s"
    announcements = soup.select(selector)

    if announcements:
        print(f"\n--- Succès ! Annonces trouvées via la navigation simulée ---")
        for ann in announcements:
            title = ann.text.strip()
            href = ann.get('href')
            full_url = f"https://www.binance.com{href}" if href and href.startswith('/') else href
            print(f"Titre : {title}\nLien  : {full_url}\n---")
    else:
        print(f"\n!!! Échec. Aucune annonce trouvée.")
        print(f"Une capture d'écran a été sauvegardée ici : {SCREENSHOT_FILE}")
        print("Veuillez l'examiner pour comprendre ce que le navigateur voit.")

except Exception as e:
    print(f"\nUne erreur est survenue : {e}")

