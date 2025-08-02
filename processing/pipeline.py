from .roi_calculator import calculate_roi
from .deduplication import deduplicate_opportunities
from .roi_filter import filter_by_roi, categorize_by_roi
import re

def extract_reward_info(opportunity):
    """Extrait les informations de récompense d'une opportunité."""
    reward_amount = 10  # Valeur par défaut
    currency = "USD"
    time_est_min = 5   # Valeur par défaut
    
    # Extraire reward_amount et currency
    if 'reward' in opportunity:
        reward_str = str(opportunity['reward'])
        
        # Chercher des montants numériques
        amount_match = re.search(r'(\d+(?:\.\d+)?)', reward_str)
        if amount_match:
            reward_amount = float(amount_match.group(1))
        
        # Déterminer la devise
        reward_str_upper = reward_str.upper()
        if 'XP' in reward_str_upper:
            currency = 'XP'
        elif 'GAL' in reward_str_upper:
            currency = 'GAL'
        elif 'POINTS' in reward_str_upper or 'POINT' in reward_str_upper:
            currency = 'POINTS'
        elif '$' in reward_str or 'USD' in reward_str_upper:
            currency = 'USD'
    
    # Extraire time_est_min
    if 'time_est_min' in opportunity:
        time_est_min = opportunity['time_est_min']
    elif 'estimated_time' in opportunity:
        time_est_min = opportunity['estimated_time']
    
    return reward_amount, currency, time_est_min

def process_opportunities(all_opportunities, min_roi=2.0):
    """Pipeline complet de processing des opportunités."""
    print(f"\n🔧 === DÉBUT DU PROCESSING ===")
    print(f"📊 Opportunités brutes: {len(all_opportunities)}")
    
    # 1. Calcul ROI pour chaque opportunité
    print(f"\n💰 Étape 1: Calcul du ROI...")
    for op in all_opportunities:
        reward_amount, currency, time_est_min = extract_reward_info(op)
        
        # Calculer le ROI
        roi = calculate_roi(reward_amount, time_est_min, currency)
        op['roi'] = round(roi, 4)
        
        # Ajouter les détails pour traçabilité
        op['reward_amount_extracted'] = reward_amount
        op['currency_detected'] = currency
        op['time_estimated'] = time_est_min
    
    # 2. Déduplication
    print(f"\n🔄 Étape 2: Déduplication...")
    unique_ops = deduplicate_opportunities(all_opportunities)
    
    # 3. Filtrage par ROI
    print(f"\n⚡ Étape 3: Filtrage ROI (≥${min_roi}/min)...")
    filtered_ops = filter_by_roi(unique_ops, min_roi=min_roi)
    
    # 4. Catégorisation
    print(f"\n🎯 Étape 4: Catégorisation...")
    categories = categorize_by_roi(unique_ops)  # Sur toutes les uniques, pas seulement filtrées
    
    # 5. Statistiques finales
    print(f"\n📈 === RÉSULTATS FINAUX ===")
    print(f"📊 Opportunités après processing: {len(filtered_ops)}")
    if filtered_ops:
        avg_roi = sum(op['roi'] for op in filtered_ops) / len(filtered_ops)
        max_roi = max(op['roi'] for op in filtered_ops)
        min_roi_actual = min(op['roi'] for op in filtered_ops)
        print(f"💎 ROI moyen: ${avg_roi:.2f}/min")
        print(f"🚀 ROI maximum: ${max_roi:.2f}/min")
        print(f"📋 ROI minimum: ${min_roi_actual:.2f}/min")
    
    result = {
        'processed_opportunities': filtered_ops,
        'categories': categories,
        'stats': {
            'total_raw': len(all_opportunities),
            'after_deduplication': len(unique_ops),
            'after_roi_filter': len(filtered_ops),
            'avg_roi': round(sum(op['roi'] for op in filtered_ops) / len(filtered_ops), 2) if filtered_ops else 0,
            'max_roi': round(max(op['roi'] for op in filtered_ops), 2) if filtered_ops else 0,
        }
    }
    
    return result
