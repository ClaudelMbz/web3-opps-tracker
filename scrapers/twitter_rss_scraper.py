import feedparser
import requests
from datetime import datetime
from langdetect import detect, DetectorFactory
import hashlib
import re
import time
from googletrans import Translator

# Assurer des résultats reproductibles pour langdetect
DetectorFactory.seed = 0

class TwitterRSSScraper:
    def __init__(self):
        """Initialise le scraper Twitter RSS avec les flux principaux et fallback"""
        # Flux RSS spécialisés en opportunités et airdrops (EN + FR + Twitter)
        self.feeds = [
            # Sources alternatives pour airdrops et opportunités crypto
            "https://forkast.news/feed/",  # Forkast News - crypto news avec opportunités
            "https://cointelegraph.com/rss",  # Cointelegraph - actualités crypto
            "https://decrypt.co/feed",  # Decrypt - Web3 et opportunités
            "https://thedefiant.io/feed/",  # The Defiant - DeFi opportunities
            
            # Sources anglaises traditionnelles
            "https://beincrypto.com/feed/",  # BeInCrypto - couvre les airdrops
            "https://cryptopotato.com/feed/",  # CryptoPotato - opportunités crypto
            "https://www.cryptonews.com/feed/",  # CryptoNews - actualités + opportunités
            
            # Sources françaises
            "https://cryptonaute.fr/feed/",  # Cryptonaute - actualités crypto FR
            "https://www.cryptoast.fr/feed/"  # Cryptoast - crypto français
        ]
        
        # Sources fallback spécialisées (sites d'airdrops)
        self.fallback_feeds = [
            "https://airdrops.io/feed/",  # Principal site d'airdrops - 15-20 opp/jour
            "https://coinairdrops.com/feed/",  # Airdrops vérifiés - 10-15 opp/jour
            "https://cryptoairdrops.com/feed/",  # Alternative - 5-10 opp/jour
            "https://airdropalert.com/feed/",  # Alertes d'airdrops - 10-15 opp/jour
            "https://earnifi.com/feed/",  # Opportunités DeFi - 5-10 opp/jour
            "https://dappradar.com/blog/feed",  # DApp opportunities - 5-8 opp/jour
        ]
        
        # Configuration
        self.timeout = 10
        self.max_retries = 2
        
        # Traducteur Google
        self.translator = Translator()
        self.translation_cache = {}  # Cache pour éviter les traductions répétées
        
    def test_connection(self):
        """Test la connectivité aux feeds RSS"""
        print("🔍 Test de connectivité aux flux RSS...")
        
        # Test des flux principaux
        print("\n📱 Flux Twitter RSS:")
        for feed_url in self.feeds:
            self._test_single_feed(feed_url)
            
        # Test des fallbacks
        print("\n🔄 Flux Fallback:")
        for feed_url in self.fallback_feeds:
            self._test_single_feed(feed_url)
            
    def _test_single_feed(self, feed_url):
        """Test un seul flux RSS"""
        try:
            response = requests.head(feed_url, timeout=self.timeout)
            if response.status_code == 200:
                print(f"✅ {feed_url}: OK ({response.status_code})")
            else:
                print(f"⚠️ {feed_url}: {response.status_code}")
        except requests.exceptions.Timeout:
            print(f"⏰ {feed_url}: Timeout")
        except Exception as e:
            print(f"❌ {feed_url}: {str(e)}")
            
    def fetch_opportunities(self, max_entries=20):
        """Récupère les opportunités depuis les flux RSS principaux"""
        print(f"📡 Récupération des opportunités RSS (max: {max_entries})...")
        all_entries = []
        
        for feed_url in self.feeds:
            try:
                print(f"📊 Scraping {feed_url}")
                feed = feedparser.parse(feed_url)
                
                if hasattr(feed, 'entries') and feed.entries:
                    for entry in feed.entries[:max_entries]:
                        all_entries.append({
                            'title': entry.title,
                            'link': entry.link,
                            'published': entry.get('published', ''),
                            'summary': entry.get('summary', entry.get('description', '')),
                            'source_feed': feed_url,
                            'is_fallback': False
                        })
                    print(f"  ✅ {len(feed.entries[:max_entries])} entrées récupérées")
                else:
                    print(f"  ⚠️ Aucune entrée trouvée")
                    
            except Exception as e:
                print(f"  ❌ Erreur {feed_url}: {str(e)}")
                continue
                
        print(f"📊 Total: {len(all_entries)} entrées RSS principales")
        return all_entries
        
    def fetch_fallback_opportunities(self, max_entries=15):
        """Récupère depuis les sources fallback"""
        print(f"🔄 Récupération fallback (max: {max_entries})...")
        fallback_entries = []
        
        for feed_url in self.fallback_feeds:
            try:
                print(f"🔄 Fallback scraping {feed_url}")
                feed = feedparser.parse(feed_url)
                
                if hasattr(feed, 'entries') and feed.entries:
                    for entry in feed.entries[:max_entries]:
                        fallback_entries.append({
                            'title': entry.title,
                            'link': entry.link,
                            'published': entry.get('published', ''),
                            'summary': entry.get('summary', entry.get('description', '')),
                            'source_feed': feed_url,
                            'is_fallback': True
                        })
                    print(f"  ✅ {len(feed.entries[:max_entries])} entrées fallback")
                else:
                    print(f"  ⚠️ Aucune entrée fallback")
                    
            except Exception as e:
                print(f"  ⚠️ Fallback failed {feed_url}: {str(e)}")
                continue
                
        print(f"🔄 Total fallback: {len(fallback_entries)} entrées")
        return fallback_entries
        
    def fetch_all_opportunities(self, max_entries=15):
        """Récupère toutes les opportunités (principales + fallback) avec déduplication"""
        print(f"🚀 Récupération complète des opportunités (max: {max_entries} par source)...")
        
        # Récupération des flux principaux
        main_entries = self.fetch_opportunities(max_entries)
        
        # Récupération des flux fallback
        fallback_entries = self.fetch_fallback_opportunities(max_entries)
        
        # Combinaison
        all_entries = main_entries + fallback_entries
        
        # Déduplication basée sur l'URL
        seen_urls = set()
        deduplicated_entries = []
        
        for entry in all_entries:
            if entry['link'] not in seen_urls:
                seen_urls.add(entry['link'])
                deduplicated_entries.append(entry)
            else:
                print(f"🔄 Duplicate removed: {entry['title'][:30]}...")
        
        print(f"📊 Total après déduplication: {len(deduplicated_entries)} entrées uniques")
        return deduplicated_entries
        
    def is_supported_language(self, text):
        """Détecte si le contenu est en anglais, français OU espagnol"""
        try:
            # Nettoyer le texte
            clean_text = text.replace('\n', ' ').replace('\t', ' ').strip()
            if len(clean_text) < 10:
                return True  # Trop court pour détecter, on garde
            
            detected_lang = detect(clean_text)
            # Accepter l'anglais, le français, l'espagnol, le portugais
            # + langues parfois confondues par langdetect (lt=lituanien, ko=coréen peuvent être des faux positifs)
            return detected_lang in ['en', 'fr', 'es', 'pt', 'lt']
            
        except Exception as e:
            # En cas d'erreur, on garde le contenu
            return True
            
    def translate_to_english(self, text, source_lang='auto'):
        """Traduit un texte vers l'anglais en utilisant Google Translate"""
        try:
            # Vérifier le cache
            cache_key = f"{source_lang}:{text[:50]}"
            if cache_key in self.translation_cache:
                return self.translation_cache[cache_key]
            
            # Traduire
            translation = self.translator.translate(text, src=source_lang, dest='en')
            translated_text = translation.text
            
            # Mettre en cache
            self.translation_cache[cache_key] = translated_text
            
            return translated_text
            
        except Exception as e:
            print(f"⚠️ Erreur de traduction: {str(e)}")
            return text  # Retourner le texte original en cas d'erreur
            
    def _estimate_reward(self, title, summary):
        """Estime la récompense basée sur le titre et résumé"""
        text = f"{title} {summary}".lower()
        
        # Recherche de montants explicites
        amounts = re.findall(r'\$(\d+)', text)
        if amounts:
            return f"${amounts[0]}"
            
        # Recherche de crypto amounts
        crypto_amounts = re.findall(r'(\d+)\s*(usdt|usdc|eth|btc)', text)
        if crypto_amounts:
            amount, token = crypto_amounts[0]
            return f"{amount} {token.upper()}"
        
        # Estimation basée sur des mots-clés
        if any(word in text for word in ['major', 'huge', 'massive', 'big']):
            return "$50-100 estimated"
        elif any(word in text for word in ['medium', 'good', 'decent']):
            return "$20-50 estimated"
        elif any(word in text for word in ['small', 'mini', 'quick']):
            return "$5-20 estimated"
        else:
            return "$10-30 estimated"
            
    def parse_rss_data(self, rss_entries):
        """Transforme les entrées RSS en format standard"""
        print(f"🔍 Parsing {len(rss_entries)} entrées RSS...")
        opportunities = []
        
        for entry in rss_entries:
            try:
                # Vérification de la langue (anglais, français ET espagnol)
                full_text = f"{entry['title']} {entry.get('summary', '')}"
                detected_lang = 'en'  # Par défaut
                
                try:
                    detected_lang = detect(full_text)
                except:
                    pass
                
                if not self.is_supported_language(full_text):
                    print(f"🌐 Skipped ({detected_lang}): {entry['title'][:50]}...")
                    continue
                
                # Traduction si nécessaire (espagnol vers anglais)
                original_title = entry['title']
                original_summary = entry.get('summary', '')
                
                if detected_lang == 'es':
                    print(f"🏪 Traducing from Spanish: {original_title[:30]}...")
                    translated_title = self.translate_to_english(original_title, 'es')
                    translated_summary = self.translate_to_english(original_summary, 'es') if original_summary else ''
                    
                    # Utiliser les versions traduites pour le filtrage
                    title_for_filtering = translated_title
                    summary_for_filtering = translated_summary
                else:
                    title_for_filtering = original_title
                    summary_for_filtering = original_summary
                
                # Filtrage basique des opportunités
                title_lower = title_for_filtering.lower()
                
                # Mots-clés élargis pour capturer plus d'opportunités (anglais + français)
                if entry.get('is_fallback', False):
                    # Fallbacks: mots-clés directs d'opportunités
                    keywords = [
                        # Anglais
                        'airdrop', 'free', 'earn', 'reward', 'giveaway', 'claim',
                        'bonus', 'incentive', 'campaign', 'contest', 'competition',
                        'whitelist', 'presale', 'launch', 'testnet', 'mainnet',
                        # Français
                        'gratuit', 'gagner', 'récompense', 'cadeau', 'concours',
                        'campagne', 'bonus', 'lancement'
                    ]
                else:
                    # Principaux: mots-clés crypto + opportunités
                    keywords = [
                        # Opportunités directes (anglais)
                        'airdrop', 'quest', 'task', 'reward', 'earn', 'free',
                        'giveaway', 'bonus', 'incentive', 'campaign', 'event',
                        'contest', 'competition', 'opportunity', 'program',
                        # Crypto/DeFi terms (anglais)
                        'defi', 'nft', 'token', 'staking', 'yield', 'farming',
                        'trading', 'swap', 'liquidity', 'bridge', 'layer2',
                        'whitelist', 'presale', 'ido', 'ico', 'launch',
                        'testnet', 'mainnet', 'alpha', 'beta',
                        # Termes français
                        'gratuit', 'gagner', 'récompense', 'jeton', 'crypto',
                        'blockchain', 'opportunité', 'programme', 'concours',
                        'campagne', 'lancement', 'finance', 'investir'
                    ]
                
                if any(keyword in title_lower for keyword in keywords):
                    # Estimation de la récompense
                    estimated_reward = self._estimate_reward(entry['title'], entry.get('summary', ''))
                    
                    # Génération d'ID unique
                    unique_id = f"rss_{hashlib.md5(entry['link'].encode()).hexdigest()[:8]}"
                    
                    # Source name
                    source_name = 'AirdropsFallback' if entry.get('is_fallback') else 'TwitterRSS'
                    
                    opportunities.append({
                        'id': unique_id,
                        'title': entry['title'],
                        'description': entry.get('summary', ''),
                        'reward': estimated_reward,
                        'estimated_time': 5,  # Valeur par défaut en minutes
                        'deadline': None,
                        'source': source_name,
                        'url': entry['link'],
                        'published_date': entry.get('published', ''),
                        'source_feed': entry.get('source_feed', ''),
                        'scraped_at': datetime.now().isoformat()
                    })
                    
            except Exception as e:
                print(f"⚠️ Erreur parsing entry: {str(e)}")
                continue
        
        print(f"🔍 Filtered {len(opportunities)} opportunities (EN/FR/ES)")
        return opportunities
        
    def test_language_detection(self):
        """Test la détection de langue"""
        print("🧪 Test de détection de langue...")
        
        test_cases = [
            ("Free airdrop for early adopters", True, "English"),
            ("Airdrop gratuit pour les premiers utilisateurs", True, "French"),
            ("Oportunidad de airdrop gratis para los primeros usuarios que se registren en esta plataforma de criptomonedas", True, "Spanish"),  # Texte plus long
            ("🎁 NEW AIRDROP ALERT! 💰", True, "English with emojis")
        ]
        
        for text, expected, description in test_cases:
            result = self.is_supported_language(text)
            
            # Debug: montrer quelle langue est détectée
            try:
                detected_lang = detect(text)
                debug_info = f"(detected: {detected_lang})"
            except:
                debug_info = "(detection failed)"
            
            status = "✅" if result == expected else "❌"
            print(f"{status} {description}: {result} {debug_info} (expected: {expected})")
            
        print("🧪 Language detection tests completed")

# Test du scraper si exécuté directement
if __name__ == "__main__":
    print("🚀 Test du Twitter RSS Scraper")
    print("=" * 50)
    
    scraper = TwitterRSSScraper()
    
    # Test de connectivité
    scraper.test_connection()
    
    # Test de détection de langue
    print("\n" + "=" * 50)
    scraper.test_language_detection()
    
    # Test de récupération complète (limité pour les tests)
    print("\n" + "=" * 50)
    print("🧪 Test du scraping complet avec déduplication...")
    
    # Test avec la nouvelle méthode complète
    all_entries = scraper.fetch_all_opportunities(max_entries=5)
    if all_entries:
        opportunities = scraper.parse_rss_data(all_entries)
        print(f"\n🎯 Opportunités trouvées au total: {len(opportunities)}")
        
        # Analyse par source
        twitter_count = sum(1 for opp in opportunities if opp['source'] == 'TwitterRSS')
        fallback_count = sum(1 for opp in opportunities if opp['source'] == 'AirdropsFallback')
        
        print(f"📊 Répartition:")
        print(f"  - Twitter/RSS: {twitter_count} opportunités")
        print(f"  - Fallback: {fallback_count} opportunités")
        
        print(f"\n🏆 Top 5 opportunités:")
        for i, opp in enumerate(opportunities[:5], 1):
            print(f"{i}. {opp['title'][:50]}... | {opp['reward']} | {opp['source']}")
            
        # Estimation du volume quotidien
        daily_estimate = len(opportunities) * 4  # Estimation x4 pour 24h
        print(f"\n📈 Estimation quotidienne: ~{daily_estimate} opportunités/jour")
    else:
        print("⚠️ Aucune opportunité trouvée")
    
    print("\n✅ Tests terminés!")
