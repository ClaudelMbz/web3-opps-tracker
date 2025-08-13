# Optimisations RAG - Réduire le temps de réponse

## 1. Réduire le topK dans le Vector Store
- **Actuellement** : topK = 10
- **Recommandation** : Réduire à topK = 3-5
- **Impact** : Moins de documents récupérés = recherche plus rapide

## 2. Optimiser les modèles utilisés

### Modèle principal (deepseek-r1)
- **Problème** : deepseek-r1 est un modèle de reasoning qui peut être lent
- **Alternative rapide** : 
  - `deepseek/deepseek-chat` (plus rapide)
  - `meta-llama/llama-3.1-8b-instruct:free`
  - `microsoft/phi-3.5-mini-128k-instruct:free`

### Embeddings Mistral
- **Alternative plus rapide** : Utiliser des embeddings locaux ou plus légers

## 3. Optimisations d'architecture

### A. Mise en cache
```javascript
// Ajouter un cache pour les requêtes similaires
const cacheKey = `rag_${hash(prompt)}`;
if (cache.has(cacheKey)) {
    return cache.get(cacheKey);
}
```

### B. Parallélisation conditionnelle
- Séparer les tâches simples (Primer) des complexes (Mastermind)
- Pour Primer : bypass le vector store complètement

### C. Timeout et fallback
```javascript
// Ajouter des timeouts
const timeout = 30000; // 30 secondes max
```

## 4. Modifications immédiates

### Configuration Vector Store optimisée :
```json
{
  "topK": 3,
  "options": {
    "includeMetadata": false,
    "scoreThreshold": 0.7
  }
}
```

### Modèle plus rapide pour le chat :
```json
{
  "model": "meta-llama/llama-3.1-8b-instruct:free",
  "options": {
    "temperature": 0.3,
    "max_tokens": 1000
  }
}
```

## 5. Optimisations du prompt système

### Prompt raccourci pour cas simples :
```text
Tu es un expert en optimisation de prompts. 
Réponds directement sans explication.
Langue : {{ détectée automatiquement }}
```

## 6. Monitoring des performances

### Ajouter des logs de timing :
```javascript
const startTime = Date.now();
// ... traitement
const endTime = Date.now();
console.log(`Temps de traitement: ${endTime - startTime}ms`);
```
