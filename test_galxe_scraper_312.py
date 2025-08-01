#!/usr/bin/env python3
"""
Test du scraper Galxe avec Python 3.12 - Version simplifiée
"""

import requests
from bs4 import BeautifulSoup
import time
import json

def test_scraper_api_simulation():
    """Simule ScraperAPI avec Playwright pour tester le contenu dynamique"""
    try:
        from playwright.sync_api import sync_playwright
        
        print("🎭 Test avec Playwright pour le contenu dynamique...")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Aller sur la page
            print("🔄 Chargement de https://galxe.com/explore...")
            page.goto("https://galxe.com/explore", wait_until="domcontentloaded", timeout=60000)
            
            try:
                # Attendre le container grid
                print("⏳ Attente du container grid...")
                page.wait_for_selector("div.GridFlowContainer_grid-flow__m_iqK", timeout=30000)
                
                # Attendre un peu plus pour le contenu dynamique
                print("⏳ Attente du contenu dynamique...")
                page.wait_for_timeout(10000)  # 10 secondes
                
                # Essayer de détecter des éléments de quête
                try:
                    page.wait_for_selector("div.GridFlowContainer_grid-flow__m_iqK > *", timeout=20000)
                    print("✅ Éléments détectés dans le grid!")
                except:
                    print("⚠️  Pas d'éléments détectés dans le grid, continuons...")
                
                # Scroll pour déclencher le chargement
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(3)
                
                # Récupérer le HTML final
                html = page.content()
                browser.close()
                
                print(f"✅ HTML récupéré: {len(html)} caractères")
                return html
                
            except Exception as e:
                print(f"⚠️  Erreur lors de l'attente: {e}")
                html = page.content()
                browser.close()
                return html
                
    except ImportError:
        print("❌ Playwright non disponible, utilisation de requests simple")
        return None
    except Exception as e:
        print(f"❌ Erreur Playwright: {e}")
        return None

def parse_quests_advanced(html):
    """Parse le HTML avec la logique améliorée"""
    if not html:
        return []
        
    soup = BeautifulSoup(html, 'html.parser')
    quests = []
    
    print("🔍 Analyse du HTML avec logique avancée...")
    
    # Vérifier le container grid
    grid_container = soup.select_one("div.GridFlowContainer_grid-flow__m_iqK")
    if grid_container:
        child_count = len(grid_container.find_all())
        print(f"✅ Container grid trouvé avec {child_count} éléments enfants")
    else:
        print("❌ Container grid non trouvé")
    
    # Sélecteurs à tester dans l'ordre de priorité
    selectors_to_try = [
        "div.GridFlowContainer_grid-flow__m_iqK > div",
        "div.GridFlowContainer_grid-flow__m_iqK > *",
        "div[class*='card']",
        "div[class*='Card']", 
        "a[href*='/space/']",
        "a[href*='/quest/']",
        "a[href*='/campaign/']",
        "main a[href]"
    ]
    
    found_items = []
    for selector in selectors_to_try:
        items = soup.select(selector)
        if items:
            print(f"✅ {selector}: {len(items)} éléments trouvés")
            found_items = items
            break
        else:
            print(f"❌ {selector}: aucun élément")
    
    if not found_items:
        print("❌ Aucun élément trouvé avec tous les sélecteurs")
        return []
    
    print(f"🔄 Traitement de {len(found_items)} éléments...")
    
    for item in found_items:
        try:
            # Chercher un lien
            link_element = item if item.name == 'a' else item.select_one('a')
            if not link_element:
                continue
                
            href = link_element.get('href', '')
            if not href:
                continue
                
            # Filtrer les liens pertinents
            if not any(path in href for path in ['/space/', '/quest/', '/campaign/']):
                continue
                
            # Extraire le titre
            title = ""
            title_candidates = [
                link_element.get_text().strip(),
                item.get_text().strip() if item != link_element else "",
            ]
            
            for candidate in title_candidates:
                if candidate and len(candidate) > 3:
                    title = candidate[:100]
                    break
            
            if not title:
                title = f"Quest from {href}"
            
            # Construire l'URL complète
            if href.startswith('/'):
                full_link = "https://galxe.com" + href
            elif href.startswith('http'):
                full_link = href
            else:
                full_link = "https://galxe.com/" + href
            
            quests.append({
                "title": title,
                "link": full_link,
                "source": "Galxe"
            })
            
        except Exception as e:
            print(f"⚠️  Erreur lors du parsing d'un élément: {e}")
            continue
    
    # Supprimer les doublons
    seen_links = set()
    unique_quests = []
    for quest in quests:
        if quest['link'] not in seen_links:
            seen_links.add(quest['link'])
            unique_quests.append(quest)
    
    print(f"📊 {len(unique_quests)} quêtes uniques trouvées")
    return unique_quests

def main():
    print("🚀 Test du scraper Galxe amélioré avec Python 3.12\n")
    
    # Test 1: HTML statique (pour comparaison)
    print("=== TEST 1: HTML STATIQUE ===")
    try:
        response = requests.get("https://galxe.com/explore", timeout=30)
        static_quests = parse_quests_advanced(response.text)
        print(f"Résultat HTML statique: {len(static_quests)} quêtes\n")
    except Exception as e:
        print(f"Erreur HTML statique: {e}\n")
        static_quests = []
    
    # Test 2: Contenu dynamique avec Playwright
    print("=== TEST 2: CONTENU DYNAMIQUE ===")
    dynamic_html = test_scraper_api_simulation()
    if dynamic_html:
        dynamic_quests = parse_quests_advanced(dynamic_html)
        print(f"Résultat contenu dynamique: {len(dynamic_quests)} quêtes\n")
        
        # Sauvegarder les résultats
        results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "static_quests_count": len(static_quests),
            "dynamic_quests_count": len(dynamic_quests),
            "static_quests": static_quests,
            "dynamic_quests": dynamic_quests,
            "improvement": len(dynamic_quests) - len(static_quests)
        }
        
        with open("galxe_test_results.json", "w", encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print("=== RÉSUMÉ ===")
        print(f"📊 HTML statique: {len(static_quests)} quêtes")
        print(f"📊 Contenu dynamique: {len(dynamic_quests)} quêtes")
        print(f"📈 Amélioration: +{len(dynamic_quests) - len(static_quests)} quêtes")
        
        if len(dynamic_quests) > 0:
            print("✅ LE PROBLÈME EST RÉSOLU!")
            print("🎯 Exemples de quêtes trouvées:")
            for i, quest in enumerate(dynamic_quests[:3]):
                print(f"  {i+1}. {quest['title']}")
                print(f"     {quest['link']}")
        else:
            print("❌ Le problème persiste, investigation supplémentaire nécessaire")
        
        print(f"\n💾 Résultats sauvegardés dans galxe_test_results.json")
    else:
        print("❌ Impossible de tester le contenu dynamique")

if __name__ == "__main__":
    main()
