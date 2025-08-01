#!/usr/bin/env python3
"""
Script de diagnostic pour analyser le contenu RSS et identifier 
pourquoi si peu d'opportunités sont détectées
"""

from scrapers.twitter_rss_scraper import TwitterRSSScraper
import json

def diagnostic_complet():
    print("🔍 DIAGNOSTIC RSS COMPLET")
    print("=" * 60)
    
    scraper = TwitterRSSScraper()
    
    # 1. Test de connectivité détaillé
    print("\n1️⃣ TEST DE CONNECTIVITÉ")
    scraper.test_connection()
    
    # 2. Analyse des entrées récupérées
    print("\n2️⃣ ANALYSE DES ENTRÉES RÉCUPÉRÉES")
    
    # Flux principaux
    print("\n📡 Flux principaux:")
    rss_entries = scraper.fetch_opportunities(max_entries=10)
    print(f"Total récupéré: {len(rss_entries)} entrées")
    
    if rss_entries:
        print("\n🔍 Échantillon du contenu récupéré:")
        for i, entry in enumerate(rss_entries[:3], 1):
            print(f"\n--- Entrée {i} ---")
            print(f"Titre: {entry['title']}")
            print(f"Résumé: {entry.get('summary', 'N/A')[:200]}...")
            print(f"Lien: {entry['link']}")
            print(f"Source: {entry['source_feed']}")
    
    # Fallbacks
    print("\n🔄 Flux fallbacks:")
    fallback_entries = scraper.fetch_fallback_opportunities(max_entries=10)
    print(f"Total fallback: {len(fallback_entries)} entrées")
    
    if fallback_entries:
        print("\n🔍 Échantillon fallback:")
        for i, entry in enumerate(fallback_entries[:3], 1):
            print(f"\n--- Fallback {i} ---")
            print(f"Titre: {entry['title']}")
            print(f"Résumé: {entry.get('summary', 'N/A')[:200]}...")
            print(f"Lien: {entry['link']}")
            print(f"Source: {entry['source_feed']}")
    
    # 3. Test de filtrage par mots-clés
    print("\n3️⃣ ANALYSE DU FILTRAGE")
    all_entries = rss_entries + fallback_entries
    
    # Analyse des mots-clés actuels
    current_keywords_main = ['airdrop', 'quest', 'task', 'reward', 'earn', 'free']
    current_keywords_fallback = ['airdrop', 'free', 'earn', 'reward', 'giveaway', 'claim']
    
    print(f"\n🔍 Mots-clés actuels (principaux): {current_keywords_main}")
    print(f"🔍 Mots-clés actuels (fallbacks): {current_keywords_fallback}")
    
    matched_main = 0
    matched_fallback = 0
    rejected_titles = []
    
    for entry in all_entries:
        title_lower = entry['title'].lower()
        is_fallback = entry.get('is_fallback', False)
        
        if is_fallback:
            keywords = current_keywords_fallback
            if any(keyword in title_lower for keyword in keywords):
                matched_fallback += 1
            else:
                rejected_titles.append((entry['title'], 'fallback'))
        else:
            keywords = current_keywords_main
            if any(keyword in title_lower for keyword in keywords):
                matched_main += 1
            else:
                rejected_titles.append((entry['title'], 'main'))
    
    print(f"\n📊 Résultats filtrage par mots-clés:")
    print(f"   ✅ Principales acceptées: {matched_main}")
    print(f"   ✅ Fallbacks acceptées: {matched_fallback}")
    print(f"   ❌ Total rejetées: {len(rejected_titles)}")
    
    # 4. Analyse des titres rejetés
    print("\n4️⃣ TITRES REJETÉS (échantillon)")
    for i, (title, source_type) in enumerate(rejected_titles[:10]):
        print(f"   {i+1}. [{source_type}] {title[:80]}...")
    
    # 5. Test de détection de langue
    print("\n5️⃣ TEST DÉTECTION DE LANGUE")
    english_count = 0
    non_english_count = 0
    
    for entry in all_entries[:20]:  # Test sur échantillon
        full_text = f"{entry['title']} {entry.get('summary', '')}"
        is_english = scraper.is_english_content(full_text)
        if is_english:
            english_count += 1
        else:
            non_english_count += 1
            print(f"   ❌ Non-anglais détecté: {entry['title'][:60]}...")
    
    print(f"\n📊 Détection langue (sur {english_count + non_english_count} échantillons):")
    print(f"   ✅ Anglais: {english_count}")
    print(f"   ❌ Non-anglais: {non_english_count}")
    
    # 6. Recommandations
    print("\n6️⃣ RECOMMANDATIONS")
    
    total_entries = len(all_entries)
    total_matched = matched_main + matched_fallback
    
    if total_matched / total_entries < 0.2:  # Moins de 20% de correspondance
        print("🚨 PROBLÈME MAJEUR: Filtrage trop strict!")
        print("   → Étendre la liste des mots-clés")
        print("   → Considérer des termes crypto généraux")
        
    if non_english_count > english_count:
        print("🚨 PROBLÈME: Détection de langue trop stricte")
        print("   → Ajuster les seuils de détection")
        
    # 7. Suggestions d'amélioration
    print("\n7️⃣ MOTS-CLÉS SUGGÉRÉS")
    crypto_keywords = [
        'crypto', 'blockchain', 'defi', 'nft', 'token', 'coin',
        'testnet', 'mainnet', 'staking', 'yield', 'farming',
        'trading', 'swap', 'liquidity', 'bridge', 'layer2',
        'whitelist', 'presale', 'ido', 'ico', 'launch'
    ]
    print(f"   Mots-clés crypto: {crypto_keywords}")
    
    opportunity_keywords = [
        'opportunity', 'campaign', 'event', 'competition',
        'contest', 'giveaway', 'bonus', 'incentive', 'program'
    ]
    print(f"   Mots-clés opportunités: {opportunity_keywords}")

if __name__ == "__main__":
    diagnostic_complet()
