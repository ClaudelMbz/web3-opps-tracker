// Modification suggérée pour la fonction sendPromptToN8n
async function sendPromptToN8n(promptText, algorithm) {
  console.log(`PromptGenie: Sending to n8n. Algorithm: ${algorithm}`);
  try {
    // AJOUTER TIMEOUT DE 60 SECONDES
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 secondes max
    
    const response = await fetch(N8N_WEBHOOK_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: promptText, algorithm: algorithm }),
      signal: controller.signal // Ajouter le signal d'abort
    });
    
    clearTimeout(timeoutId); // Annuler le timeout si succès
    
    if (!response.ok) throw new Error(`n8n webhook responded with status: ${response.status}`);
    const result = await response.json();
    console.log("PromptGenie: Received response from n8n.");
    return result.improvedPrompt;
  } catch (error) {
    if (error.name === 'AbortError') {
      console.error("PromptGenie: Request timed out after 60 seconds.");
      return "Request timed out. Please try again with a shorter prompt.";
    }
    console.error("PromptGenie: Error communicating with n8n.", error);
    return null;
  }
}
