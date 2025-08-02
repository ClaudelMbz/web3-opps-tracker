def filter_by_roi(opportunities, min_roi=2.0):
    """Filtre les opportunités par ROI minimum et les trie par ROI décroissant."""
    filtered = []
    
    for op in opportunities:
        roi = op.get('roi', 0)
        if roi >= min_roi:
            filtered.append(op)
    
    # Trier par ROI décroissant
    filtered_sorted = sorted(filtered, key=lambda x: x.get('roi', 0), reverse=True)
    
    print(f"💰 Filtrage ROI (≥${min_roi}/min): {len(opportunities)} → {len(filtered_sorted)} opportunités")
    
    if filtered_sorted:
        highest_roi = filtered_sorted[0].get('roi', 0)
        lowest_roi = filtered_sorted[-1].get('roi', 0)
        avg_roi = sum(op.get('roi', 0) for op in filtered_sorted) / len(filtered_sorted)
        print(f"📊 ROI: Min=${lowest_roi:.2f}/min, Max=${highest_roi:.2f}/min, Avg=${avg_roi:.2f}/min")
    
    return filtered_sorted

def categorize_by_roi(opportunities):
    """Catégorise les opportunités par niveau de ROI."""
    high_roi = []      # ≥ $5/min
    medium_roi = []    # $2-5/min
    low_roi = []       # < $2/min
    
    for op in opportunities:
        roi = op.get('roi', 0)
        if roi >= 5.0:
            high_roi.append(op)
        elif roi >= 2.0:
            medium_roi.append(op)
        else:
            low_roi.append(op)
    
    print(f"🎯 Catégorisation ROI:")
    print(f"  🔥 Haute (≥$5/min): {len(high_roi)} opportunités")
    print(f"  ⚡ Moyenne ($2-5/min): {len(medium_roi)} opportunités") 
    print(f"  📋 Faible (<$2/min): {len(low_roi)} opportunités")
    
    return {
        'high': high_roi,
        'medium': medium_roi,
        'low': low_roi
    }
