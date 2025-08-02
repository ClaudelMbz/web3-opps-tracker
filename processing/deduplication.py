import hashlib

def hash_opportunity(title, link, description=""):
    """Génère un hash unique pour une opportunité basé sur titre, lien et description."""
    content = f"{title}|{link}|{description}"
    return hashlib.md5(content.encode()).hexdigest()

def deduplicate_opportunities(opportunities):
    """Supprime les opportunités en double basé sur le hash."""
    seen_hashes = set()
    unique_ops = []
    
    for op in opportunities:
        hash_key = hash_opportunity(
            op.get('title', ''), 
            op.get('url', ''), 
            op.get('description', '')
        )
        
        if hash_key not in seen_hashes:
            seen_hashes.add(hash_key)
            op['hash'] = hash_key  # Ajouter le hash à l'opportunité
            unique_ops.append(op)
    
    print(f"🔄 Déduplication: {len(opportunities)} → {len(unique_ops)} opportunités uniques")
    return unique_ops
