// This is the vanilla JS equivalent of `import cssText from "data-text:./style.css"`
// It contains all the necessary TailwindCSS classes for the UI to render correctly.
const cssText = `
  button { background: none; border: none; padding: 0; margin: 0; font: inherit; color: inherit; cursor: pointer; text-align: inherit; }
  :host { font-family: 'Inter', sans-serif; }
  .prompt-genie-container { position: fixed; bottom: 40px; right: 40px; z-index: 9999; cursor: pointer; }
  .prompt-genie-icon-wrapper { width: 59px; height: 59px; transition: transform 0.2s ease-in-out; }
  .prompt-genie-container:hover .prompt-genie-icon-wrapper { transform: scale(1.15); }
  .prompt-genie-popup { position: fixed; bottom: 115px; right: 40px; width: 100%; max-width: 400px; z-index: 10001; display: none; flex-direction: column; font-family: 'Inter', sans-serif; }
  .bg-gray-800 { background-color: #1f2937; }
  .rounded-xl { border-radius: 0.75rem; }
  .shadow-lg { box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05); }
  .p-6 { padding: 1rem; }
  .flex { display: flex; }
  .justify-between { justify-content: space-between; }
  .mb-6 { margin-bottom: 1rem; }
  .border-b { border-bottom-width: 1px; }
  .border-gray-700 { border-color: #374151; }
  .pb-2 { padding-bottom: 0.5rem; }
  .text-orange-400 { color: #fb923c; }
  .font-semibold { font-weight: 600; }
  .border-b-2 { border-bottom-width: 2px; }
  .border-orange-400 { border-color: #fb923c; }
  .text-gray-400 { color: #9ca3af; }
  .hover\:text-white:hover { color: #ffffff; }
  .text-lg { font-size: 1.125rem; }
  .mb-4 { margin-bottom: 0.75rem; }
  .text-white { color: #ffffff; }
  .space-y-4 > :not([hidden]) ~ :not([hidden]) { margin-top: 0.5rem; }
  .bg-gray-700\/30 { background-color: rgba(55, 65, 81, 0.3); }
  .border { border-width: 1px; }
  .border-gray-600 { border-color: #4b5563; }
  .rounded-lg { border-radius: 0.5rem; }
  .p-4 { padding: 0.65rem; }
  .cursor-pointer { cursor: pointer; }
  .hover\:bg-gray-600\/40:hover { background-color: rgba(75, 85, 99, 0.4); }
  .transition { transition-property: background-color, border-color, color, fill, stroke, opacity, box-shadow, transform, filter, backdrop-filter, -webkit-backdrop-filter; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); transition-duration: 150ms; }
  .items-center { align-items: center; }
  .gap-3 { gap: 0.75rem; }
  .text-xl { font-size: 1.25rem; }
  .text-sm { font-size: 0.875rem; }
  .text-gray-300 { color: #d1d5db; }
  .text-pink-400 { color: #f472b6; }
  .mt-6 { margin-top: 1rem; }
  .w-full { width: 100%; }
  .mt-4 { margin-top: 1rem; }
  .bg-orange-400 { background-color: #fb923c; }
  .hover\\:bg-orange-500:hover { background-color: #f97316; }
  .text-black { color: #000000; }
  .font-bold { font-weight: 700; }
  .py-2 { padding-top: 0.5rem; padding-bottom: 0.5rem; }
  .px-4 { padding-left: 1rem; padding-right: 1rem; }
  .rounded-md { border-radius: 0.375rem; }
  .bg-orange-900\\/40 { background-color: rgba(124, 45, 18, 0.4); }
  .hover\\:bg-orange-900\\/60:hover { background-color: rgba(124, 45, 18, 0.6); }
  .bg-gray-700\\/50 { background-color: rgba(55, 65, 81, 0.5); }
  .opacity-50 { opacity: 0.5; }
  .relative { position: relative; }
  .gap-1 { gap: 0.25rem; }
  .bg-orange-500 { background-color: #f97316; }
  .text-xs { font-size: 0.75rem; line-height: 1rem; }
  .px-2 { padding-left: 0.5rem; padding-right: 0.5rem; }
  .py-0\\.5 { padding-top: 0.125rem; padding-bottom: 0.125rem; }
`;

console.log("PromptGenie: Content script loaded. Waiting for full page load.");

// =================================================================================
// CONFIGURATION
// =================================================================================
const N8N_WEBHOOK_URL = 'https://joeiiii.app.n8n.cloud/webhook/promptengineer';

// =================================================================================
// SVG ICON
// =================================================================================
const BRAIN_SVG = `
<svg width="59" height="59" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="24" cy="24" r="23" fill="#4A4D62"/>
  <circle cx="24" cy="24" r="22" fill="#23263A"/>
  <g fill="white"><path d="M23.5,36 C18,38 12,32 14,26 C16,20 20,14 23.5,14 V 36 Z"/><path d="M24.5,36 C30,38 36,32 34,26 C32,20 28,14 24.5,14 V 36 Z"/></g>
</svg>
`;

// =================================================================================
// PLATFORM-SPECIFIC LOGIC
// =================================================================================

function getPlatformConfig() {
    const hostname = window.location.hostname;

    // For ChatGPT
    if (hostname.includes('openai.com') || hostname.includes('chatgpt.com')) {
        const editor = document.getElementById('prompt-textarea');
        if (!editor) return null;
        return {
            read: () => editor.textContent,
            write: (text) => {
                editor.textContent = text;
                editor.dispatchEvent(new Event('input', { bubbles: true }));
            },
            getOverlayContainer: () => editor.parentElement,
        };
    }

    // For DeepSeek
    if (hostname.includes('deepseek.com')) {
        const promptTextarea = document.querySelector('#chat-input');
        if (!promptTextarea) return null;
        return {
            read: () => promptTextarea.value,
            write: (text) => {
                promptTextarea.value = text;
                promptTextarea.dispatchEvent(new Event('input', { bubbles: true }));
            },
            getOverlayContainer: () => promptTextarea.parentElement,
        };
    }

    // For Gemini
    if (hostname.includes('gemini.google.com')) {
        const editor = document.querySelector('.ql-editor');
        if (!editor) return null;
        return {
            read: () => editor.textContent,
            write: (text) => {
                editor.innerHTML = `<p>${text}</p>`;
                editor.dispatchEvent(new Event('input', { bubbles: true }));
            },
            getOverlayContainer: () => editor.parentElement,
        };
    }

    return null; // Host not supported
}


// =================================================================================
// CORE LOGIC WITH MINIMUM 1 MINUTE TIMEOUT
// =================================================================================

async function sendPromptToN8n(promptText, algorithm) {
  console.log(`PromptGenie: Sending to n8n. Algorithm: ${algorithm}`);
  
  const startTime = Date.now();
  const MINIMUM_WAIT_TIME = 60000; // 1 minute - only for error display
  const MAXIMUM_WAIT_TIME = 120000; // 2 minutes maximum
  
  try {
    // Create AbortController for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), MAXIMUM_WAIT_TIME);
    
    const response = await fetch(N8N_WEBHOOK_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: promptText, algorithm: algorithm }),
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      // For errors, wait minimum time if response was too quick
      const elapsedTime = Date.now() - startTime;
      if (elapsedTime < MINIMUM_WAIT_TIME) {
        console.log(`PromptGenie: Error occurred at ${elapsedTime}ms. Waiting ${MINIMUM_WAIT_TIME - elapsedTime}ms more before showing error...`);
        await new Promise(resolve => setTimeout(resolve, MINIMUM_WAIT_TIME - elapsedTime));
      }
      throw new Error(`n8n webhook responded with status: ${response.status}`);
    }
    
    const result = await response.json();
    const elapsedTime = Date.now() - startTime;
    
    // DEBUG: Log the full response structure
    console.log('PromptGenie: Full response received:', result);
    console.log('PromptGenie: improvedPrompt value:', result.improvedPrompt);
    
    // For SUCCESS: Display immediately regardless of time
    console.log(`PromptGenie: Response received successfully in ${elapsedTime}ms. Displaying immediately.`);
    
    // Handle different response structures
    let improvedPrompt;
    
    // Handle array response format: [{'output': '...'}]
    if (Array.isArray(result) && result.length > 0) {
      improvedPrompt = result[0].output || result[0].improvedPrompt;
    } else {
      // Handle object response format: {'improvedPrompt': '...'}
      improvedPrompt = result.improvedPrompt || result.output || result.prompt || result.text;
    }
    
    if (!improvedPrompt) {
      console.error('PromptGenie: No valid prompt found in response. Available keys:', Array.isArray(result) ? Object.keys(result[0] || {}) : Object.keys(result));
      return null;
    }
    
    return improvedPrompt;
    
  } catch (error) {
    // For errors, ensure minimum wait time to avoid looking broken
    const elapsedTime = Date.now() - startTime;
    if (elapsedTime < MINIMUM_WAIT_TIME) {
      console.log(`PromptGenie: Error occurred at ${elapsedTime}ms. Waiting ${MINIMUM_WAIT_TIME - elapsedTime}ms more before showing error...`);
      await new Promise(resolve => setTimeout(resolve, MINIMUM_WAIT_TIME - elapsedTime));
    }
    
    if (error.name === 'AbortError') {
      console.error(`PromptGenie: Request timed out after ${MAXIMUM_WAIT_TIME/1000} seconds.`);
      return "Request timed out. The server took too long to respond. Please try again with a shorter prompt.";
    }
    
    console.error("PromptGenie: Error communicating with n8n.", error);
    return null;
  }
}

function injectUI() {
  // 1. CHECK IF ALREADY INJECTED
  if (document.getElementById('prompt-genie-host')) {
    console.log("PromptGenie: UI host already present. Aborting injection.");
    return;
  }
  console.log("PromptGenie: Injecting UI components.");

  // 2. CREATE THE HOST ELEMENT ON THE MAIN PAGE
  const host = document.createElement('div');
  host.id = 'prompt-genie-host';
  document.body.appendChild(host);

  // 3. CREATE THE SHADOW ROOT
  const shadowRoot = host.attachShadow({ mode: 'open' });

  // 4. INJECT CSS AND HTML
  shadowRoot.innerHTML = `
    <style>${cssText}</style>
    
    <div id="prompt-genie-container" class="prompt-genie-container">
      <div class="prompt-genie-icon-wrapper">${BRAIN_SVG}</div>
    </div>

    <div id="prompt-genie-popup" class="prompt-genie-popup bg-gray-800 rounded-xl shadow-lg p-6">
      <div class="flex justify-between mb-6 border-b border-gray-700 pb-2">
        <button class="text-orange-400 font-semibold border-b-2 border-orange-400 pb-1">Optimize</button>
        <button class="text-gray-400 hover:text-white">Saved Prompts</button>
      </div>

      <h2 class="text-lg font-semibold mb-4 text-white">Choose an optimization algorithm</h2>

      <div class="space-y-4">
        <!-- Primer Option -->
        <div id="primerOption" class="bg-gray-700/30 border border-gray-600 rounded-lg p-4 cursor-pointer hover:bg-gray-600/40 transition">
          <div class="flex items-center gap-3">
            <div class="text-orange-400 text-xl">⚡</div>
            <div>
              <h3 class="font-semibold text-white">Primer</h3>
              <p class="text-sm text-gray-300">The fastest algorithm for quick prompts that get the job done</p>
            </div>
          </div>
        </div>

        <!-- AI Amplifier Option (PRO) -->
        <div class="bg-gray-700/50 border border-gray-600 rounded-lg p-4 opacity-50 relative">
          <div class="flex items-center gap-3">
            <div class="text-gray-300 text-xl">🔍</div>
            <div>
              <h3 class="font-semibold text-gray-300 flex items-center gap-1">
                AI Amplifier 
                <span class="bg-orange-500 text-black text-xs font-bold px-2 py-0.5 rounded-md">PRO</span>
              </h3>
              <p class="text-sm text-gray-400">Upgrade to PRO to unlock this advanced algorithm</p>
            </div>
          </div>
        </div>

        <!-- Mastermind Option -->
        <div id="mastermindOption" class="bg-gray-700/30 border border-gray-600 rounded-lg p-4 hover:bg-gray-600/40 transition cursor-pointer">
          <div class="flex items-center gap-3">
            <div class="text-pink-400 text-xl">🧠</div>
            <div>
              <h3 class="font-semibold text-white">Mastermind</h3>
              <p class="text-sm text-gray-300">Most advanced algorithm adding sections for context, approach and instruction</p>
            </div>
          </div>
        </div>
      </div>

      <div class="mt-6">
        <button id="optimizePromptButton" class="w-full mt-4 bg-orange-400 hover:bg-orange-500 text-black font-bold py-2 px-4 rounded-md transition">
          Optimize Prompt
        </button>
      </div>
    </div>
  `;

  // 5. GET REFERENCES TO ELEMENTS
  const container = shadowRoot.getElementById('prompt-genie-container');
  const popup = shadowRoot.getElementById('prompt-genie-popup');

  // 6. ATTACH EVENT LISTENERS FOR POPUP
  let hideTimeout;
  const showPopup = () => { clearTimeout(hideTimeout); popup.style.display = 'flex'; };
  const hidePopup = () => { hideTimeout = setTimeout(() => { popup.style.display = 'none'; }, 200); };
  container.addEventListener('mouseenter', showPopup);
  container.addEventListener('mouseleave', hidePopup);
  popup.addEventListener('mouseenter', showPopup);
  popup.addEventListener('mouseleave', hidePopup);

  // 7. ATTACH EVENT LISTENERS FOR ALGORITHM SELECTION
  let currentSelectedOption = null;
  const algorithmOptions = popup.querySelectorAll('#primerOption, #mastermindOption');
  
  algorithmOptions.forEach(option => {
    option.addEventListener('click', () => {
      if (currentSelectedOption) {
        currentSelectedOption.classList.remove('bg-orange-900/40', 'border-orange-400');
        currentSelectedOption.classList.add('bg-gray-700/30', 'border-gray-600');
      }
      
      option.classList.add('bg-orange-900/40', 'border-orange-400');
      option.classList.remove('bg-gray-700/30', 'border-gray-600');
      
      currentSelectedOption = option;
    });
  });

  // 8. ATTACH EVENT LISTENER FOR OPTIMIZE BUTTON
  shadowRoot.addEventListener('click', async (event) => {
    const optimizeButton = event.target.closest('#optimizePromptButton');
    if (!optimizeButton) return;

    const platform = getPlatformConfig();
    if (!platform) {
      alert("PromptGenie Error: This website is not supported.");
      return;
    }

    const originalPrompt = platform.read();
    if (originalPrompt === null || !originalPrompt.trim()) {
      alert("PromptGenie: The prompt is empty. Please type something first.");
      return;
    }

    let selectedOptionName = null;
    if (currentSelectedOption) {
      const h3 = currentSelectedOption.querySelector('h3');
      if (h3 && h3.textContent) {
        selectedOptionName = h3.textContent.trim();
      }
    }

    if (!selectedOptionName) {
        alert("PromptGenie: Please select an optimization algorithm first.");
        return;
    }

    // --- Loading Overlay ---
    const overlayContainer = platform.getOverlayContainer();
    if (!overlayContainer) {
        console.error("PromptGenie: Could not find overlay container.");
        return;
    }
    const overlay = document.createElement('div');
    Object.assign(overlay.style, {
      position: 'absolute', top: '0', left: '0', width: '100%', height: '100%',
      borderRadius: '0.75rem', pointerEvents: 'none', zIndex: '10',
      background: 'repeating-linear-gradient(45deg, rgba(0,0,0,0), rgba(0,0,0,0) 10px, rgba(0,0,0,0.15) 10px, rgba(0,0,0,0.15) 20px)',
      backgroundSize: '200% 200%', animation: 'prompt-genie-wave-animation 2s linear infinite'
    });
    const keyframes = `@keyframes prompt-genie-wave-animation { 0% { background-position: 0% 0%; } 100% { background-position: 100% 100%; } }`;
    const styleSheet = document.createElement("style");
    styleSheet.innerText = keyframes;
    document.head.appendChild(styleSheet);
    
    if (window.getComputedStyle(overlayContainer).position === 'static') {
      overlayContainer.style.position = 'relative';
    }
    overlayContainer.appendChild(overlay);
    popup.style.display = 'none';
    // --- End Loading Overlay ---

    const improvedPrompt = await sendPromptToN8n(originalPrompt, selectedOptionName);

    overlay.remove();
    styleSheet.remove();

    if (improvedPrompt) {
      platform.write(improvedPrompt);
    } else {
      alert("PromptGenie Error: The optimization request failed. Please check the console for details.");
    }
  });
}

// =================================================================================
// INITIALIZATION
// =================================================================================
function startInjection() {
    setTimeout(() => {
        console.log("PromptGenie: Attempting to inject UI after full page load and delay.");
        injectUI();
    }, 2000);
}

window.addEventListener('load', startInjection);
