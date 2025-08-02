#!/usr/bin/env python3
import json
import re

def extract_numeric_value(reward_str):
    """Extrait la valeur numérique d'une chaîne de récompense"""
    if not reward_str or reward_str == 'unknown':
        return 0
    
    # Chercher les montants en dollars
    dollar_match = re.search(r'\$(\d+(?:,\d+)*(?:\.\d+)?)', str(reward_str))
    if dollar_match:
        return float(dollar_match.group(1).replace(',', ''))
    
    # Chercher les BTC
    btc_match = re.search(r'(\d+(?:\.\d+)?)\s*BTC', str(reward_str), re.IGNORECASE)
    if btc_match:
        # Convertir BTC en USD (estimation ~100,000 USD par BTC)
        return float(btc_match.group(1)) * 100000
    
    # Pour les estimations
    if 'estimated' in str(reward_str).lower():
        if '10-30' in str(reward_str):
            return 20  # moyenne
        elif '50-100' in str(reward_str):
            return 75  # moyenne
        elif '20-50' in str(reward_str):
            return 35  # moyenne
        elif '5-20' in str(reward_str):
            return 12.5  # moyenne
        else:
            return 20  # défaut pour estimated
    
    return 0

# Charger les données d'analyse
with open('direct_rss_analysis_20250801_173006.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Analyser les opportunités directes
direct_opportunities = [opp for opp in data['analysis_details'] if opp['is_direct']]
total_direct_reward = 0
rewards_breakdown = []

print('=== ANALYSE DES RECOMPENSES DIRECTES ===')
print(f'Ratio identifie: {data["direct_ratio"]}% d\'opportunites directes ({data["direct_opportunities"]} sur {data["total_opportunities"]})')
print()

for opp in direct_opportunities:
    reward_value = extract_numeric_value(opp['reward'])
    total_direct_reward += reward_value
    rewards_breakdown.append({
        'title': opp['title'][:50] + '...',
        'reward': opp['reward'],
        'value_usd': reward_value,
        'confidence': opp['confidence']
    })

# Trier par valeur décroissante
rewards_breakdown.sort(key=lambda x: x['value_usd'], reverse=True)

print('=== TOP RECOMPENSES DIRECTES PAR VALEUR ===')
for i, reward in enumerate(rewards_breakdown[:10], 1):
    print(f'{i:2d}. ${reward["value_usd"]:,.0f} USD - {reward["title"]}')
    print(f'    Recompense originale: {reward["reward"]} | Confiance: {reward["confidence"]}%')
    print()

print('=== RESUME FINANCIER ===')
print(f'Recompense totale estimee des opportunites directes: ${total_direct_reward:,.0f} USD')
print(f'Recompense moyenne par opportunite directe: ${total_direct_reward/len(direct_opportunities):,.0f} USD')
print(f'Ratio d\'opportunites directes: {data["direct_ratio"]}%')
print()

# Calculer les récompenses par niveau de confiance
high_confidence_rewards = sum(r['value_usd'] for r in rewards_breakdown if r['confidence'] >= 80)
medium_confidence_rewards = sum(r['value_usd'] for r in rewards_breakdown if 50 <= r['confidence'] < 80)
low_confidence_rewards = sum(r['value_usd'] for r in rewards_breakdown if r['confidence'] < 50)

print('=== REPARTITION PAR NIVEAU DE CONFIANCE ===')
print(f'Haute confiance (>=80%): ${high_confidence_rewards:,.0f} USD ({data["high_confidence_direct"]} opportunites)')
print(f'Confiance moyenne (50-79%): ${medium_confidence_rewards:,.0f} USD ({data["medium_confidence_direct"]} opportunites)')
print(f'Faible confiance (<50%): ${low_confidence_rewards:,.0f} USD ({data["low_confidence_direct"]} opportunites)')
