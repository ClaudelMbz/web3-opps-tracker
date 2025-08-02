#!/usr/bin/env python3
"""
Analyseur d'opportunités directes - Web3 Opportunities Tracker
Calcule le ratio des opportunités réalisables immédiatement (≤ 3 jours)
"""

import re
import json
from datetime import datetime, timedelta
from scrapers.twitter_rss_scraper import TwitterRSSScraper
from scrapers.galxe_scraper import GalxeScraperEnhanced
from scrapers.zealy_scraper import ZealyScraper

class DirectOpportunityAnalyzer:
    def __init__(self):
        """Initialise l'analyseur d'opportunités directes"""
        self.direct_indicators = [
            # Indicateurs de récompense immédiate
            "instant", "immediate", "now", "today", "direct payment",
            "receive now", "get paid", "claim now", "available now",
            "instant reward", "immediate payout", "quick reward",
            
            # Indicateurs temporels courts (≤ 3 jours)
            "24 hours", "48 hours", "72 hours", "1 day", "2 days", "3 days",
            "within hours", "same day", "next day", "tomorrow",
            
            # Mots-clés français
            "immédiat", "maintenant", "aujourd'hui", "demain", 
            "24h", "48h", "72h", "reçu maintenant", "paiement direct",
            
            # Termes de récompense directe
            "airdrop live", "live drop", "active drop", "claim active",
            "whitelist open", "minting live", "presale active",
            "bonus active", "reward active"
        ]
        
        # Exclusions (opportunités à long terme)
        self.long_term_indicators = [
            "mainnet", "launch in", "coming soon", "q1", "q2", "q3", "q4",
            "next month", "next year", "2025", "2026", "upcoming",
            "testnet reward", "future airdrop", "potential reward",
            "estimated", "possible", "expected in",
            
            # Français
            "bientôt", "prochainement", "futur", "estimé", "possible"
        ]
        
    def is_direct_opportunity(self, opportunity):
        """
        Détermine si une opportunité est directe (réalisable ≤ 3 jours)
        """
        title = opportunity.get('title', '').lower()
        description = opportunity.get('description', '').lower()
        text = f"{title} {description}"
        
        # Score de directness
        direct_score = 0
        long_term_score = 0
        
        # Vérifier les indicateurs directs
        for indicator in self.direct_indicators:
            if indicator in text:
                direct_score += 1
        
        # Vérifier les exclusions long terme
        for exclusion in self.long_term_indicators:
            if exclusion in text:
                long_term_score += 1
        
        # Analyse des montants (montants précis = plus direct)
        if re.search(r'\$\d+', text) or re.search(r'\d+\s*(usdt|usdc|eth|btc)', text):
            direct_score += 2
        
        # Analyse des deadlines
        if re.search(r'deadline|expires|ends', text):
            direct_score += 1
        
        # Analyse des statuts actifs
        if re.search(r'active|live|open|available', text):
            direct_score += 2
        
        # Score final
        final_score = direct_score - (long_term_score * 2)
        
        return {
            'is_direct': final_score >= 2,
            'confidence': min(100, max(0, final_score * 20)),
            'direct_score': direct_score,
            'long_term_score': long_term_score,
            'indicators_found': [ind for ind in self.direct_indicators if ind in text]
        }
    
    def analyze_opportunities(self, opportunities):
        """Analyse une liste d'opportunités et calcule les ratios"""
        results = {
            'total_opportunities': len(opportunities),
            'direct_opportunities': 0,
            'indirect_opportunities': 0,
            'direct_ratio': 0.0,
            'analysis_details': [],
            'high_confidence_direct': 0,
            'medium_confidence_direct': 0,
            'low_confidence_direct': 0
        }
        
        for opp in opportunities:
            analysis = self.is_direct_opportunity(opp)
            
            analysis_detail = {
                'id': opp.get('id', 'unknown'),
                'title': opp.get('title', '')[:60] + '...',
                'source': opp.get('source', 'unknown'),
                'reward': opp.get('reward', 'unknown'),
                'is_direct': analysis['is_direct'],
                'confidence': analysis['confidence'],
                'indicators_found': analysis['indicators_found']
            }
            
            results['analysis_details'].append(analysis_detail)
            
            if analysis['is_direct']:
                results['direct_opportunities'] += 1
                
                # Classification par niveau de confiance
                if analysis['confidence'] >= 80:
                    results['high_confidence_direct'] += 1
                elif analysis['confidence'] >= 50:
                    results['medium_confidence_direct'] += 1
                else:
                    results['low_confidence_direct'] += 1
            else:
                results['indirect_opportunities'] += 1
        
        # Calcul du ratio
        if results['total_opportunities'] > 0:
            results['direct_ratio'] = (results['direct_opportunities'] / results['total_opportunities']) * 100
        
        return results
    
    def run_full_analysis(self):
        """Lance une analyse complète sur toutes les sources"""
        print("🔍 Analyse des opportunités directes - Web3 Opportunities Tracker")
        print("=" * 70)
        
        all_opportunities = []
        
        # 1. Analyse Twitter/RSS
        print("\n📡 Récupération des opportunités Twitter/RSS...")
        try:
            rss_scraper = TwitterRSSScraper()
            rss_entries = rss_scraper.fetch_all_opportunities(max_entries=10)
            rss_opportunities = rss_scraper.parse_rss_data(rss_entries)
            all_opportunities.extend(rss_opportunities)
            print(f"✅ {len(rss_opportunities)} opportunités RSS récupérées")
        except Exception as e:
            print(f"⚠️ Erreur RSS: {str(e)}")
        
        # 2. Analyse Galxe (si disponible)
        print("\n🌌 Récupération des opportunités Galxe...")
        try:
            galxe_scraper = GalxeScraperEnhanced()
            # Scraper quelques pages Galxe pour test
            galxe_opportunities = galxe_scraper.scrape_page("https://app.galxe.com/quest", max_retries=1)
            if galxe_opportunities:
                all_opportunities.extend(galxe_opportunities)
                print(f"✅ {len(galxe_opportunities)} opportunités Galxe récupérées")
            else:
                print("⚠️ Aucune opportunité Galxe disponible")
        except Exception as e:
            print(f"⚠️ Erreur Galxe: {str(e)}")
        
        # 3. Analyse Zealy (si disponible)
        print("\n⚡ Récupération des opportunités Zealy...")
        try:
            zealy_scraper = ZealyScraper()
            raw_quests = zealy_scraper.fetch_quests(limit=20)
            if raw_quests:
                zealy_opportunities = zealy_scraper.parse_quests(raw_quests)
                all_opportunities.extend(zealy_opportunities)
                print(f"✅ {len(zealy_opportunities)} opportunités Zealy récupérées")
            else:
                print("⚠️ Aucune opportunité Zealy disponible")
        except Exception as e:
            print(f"⚠️ Erreur Zealy: {str(e)}")
        
        print(f"\n📊 Total des opportunités collectées: {len(all_opportunities)}")
        
        if not all_opportunities:
            print("❌ Aucune opportunité trouvée pour l'analyse")
            return None
        
        # Analyse des opportunités directes
        print("\n🎯 Analyse des opportunités directes...")
        results = self.analyze_opportunities(all_opportunities)
        
        # Affichage des résultats
        self.display_results(results)
        
        # Sauvegarde des résultats
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"direct_opportunities_analysis_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Résultats sauvegardés dans: {filename}")
        
        return results
    
    def display_results(self, results):
        """Affiche les résultats de l'analyse de manière formatée"""
        print("\n" + "=" * 70)
        print("📈 RÉSULTATS DE L'ANALYSE DES OPPORTUNITÉS DIRECTES")
        print("=" * 70)
        
        print(f"\n📊 STATISTIQUES GLOBALES:")
        print(f"  • Total des opportunités analysées: {results['total_opportunities']}")
        print(f"  • Opportunités directes (≤ 3 jours): {results['direct_opportunities']}")
        print(f"  • Opportunités indirectes (> 3 jours): {results['indirect_opportunities']}")
        print(f"  • RATIO D'OPPORTUNITÉS DIRECTES: {results['direct_ratio']:.1f}%")
        
        print(f"\n🎯 RÉPARTITION PAR NIVEAU DE CONFIANCE:")
        print(f"  • Haute confiance (≥80%): {results['high_confidence_direct']} opportunités")
        print(f"  • Confiance moyenne (50-79%): {results['medium_confidence_direct']} opportunités")
        print(f"  • Faible confiance (<50%): {results['low_confidence_direct']} opportunités")
        
        # Top opportunités directes
        direct_opps = [opp for opp in results['analysis_details'] if opp['is_direct']]
        direct_opps.sort(key=lambda x: x['confidence'], reverse=True)
        
        print(f"\n🏆 TOP 10 OPPORTUNITÉS DIRECTES (par confiance):")
        for i, opp in enumerate(direct_opps[:10], 1):
            confidence_emoji = "🟢" if opp['confidence'] >= 80 else "🟡" if opp['confidence'] >= 50 else "🔴"
            print(f"  {i:2d}. {confidence_emoji} [{opp['confidence']:3.0f}%] {opp['title']}")
            print(f"      💰 {opp['reward']} | 🔗 {opp['source']}")
            if opp['indicators_found']:
                print(f"      🎯 Indicateurs: {', '.join(opp['indicators_found'][:3])}")
            print()
        
        # Analyse par source
        source_analysis = {}
        for opp in results['analysis_details']:
            source = opp['source']
            if source not in source_analysis:
                source_analysis[source] = {'total': 0, 'direct': 0}
            source_analysis[source]['total'] += 1
            if opp['is_direct']:
                source_analysis[source]['direct'] += 1
        
        print(f"\n📋 ANALYSE PAR SOURCE:")
        for source, data in source_analysis.items():
            ratio = (data['direct'] / data['total']) * 100 if data['total'] > 0 else 0
            print(f"  • {source:15s}: {data['direct']:2d}/{data['total']:2d} ({ratio:5.1f}%)")
        
        print("\n" + "=" * 70)
        
        # Recommandations
        if results['direct_ratio'] >= 50:
            print("✅ EXCELLENT: Plus de 50% d'opportunités directes!")
        elif results['direct_ratio'] >= 30:
            print("🟡 BON: Ratio d'opportunités directes acceptable")
        else:
            print("🔴 AMÉLIORATION NÉCESSAIRE: Ratio d'opportunités directes faible")
        
        print("=" * 70)

if __name__ == "__main__":
    analyzer = DirectOpportunityAnalyzer()
    analyzer.run_full_analysis()
