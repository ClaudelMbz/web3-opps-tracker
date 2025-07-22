import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headless=True si tu veux sans interface
        page = await browser.new_page()
        await page.goto("https://example.com")
        print("Titre de la page :", await page.title())
        await page.screenshot(path="screenshot.png")
        await browser.close()

asyncio.run(run())
# Ce script utilise Playwright pour ouvrir une page web, afficher son titre et prendre une capture d'écran.