chrome.action.onClicked.addListener((tab) => {
    chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ['content.js']
    }); 
});

const BACKEND_URL = 'http://155.248.218.39:8000/translate';

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function postToBackendWithRetry(payload, maxAttempts = 4) {
    let lastError = null;

    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
        try {
            const res = await fetch(BACKEND_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                return await res.json();
            }

            const errorText = await res.text();
            const transient = [502, 503, 504].includes(res.status);

            if (transient && attempt < maxAttempts) {
                await sleep(1500 * attempt);
                continue;
            }

            throw new Error(`Backend error ${res.status}: ${errorText}`);
        } catch (err) {
            lastError = err;

            if (attempt < maxAttempts) {
                await sleep(1500 * attempt);
                continue;
            }
        }
    }

    throw lastError || new Error('Backend request failed after retries');
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'fetchImage') {
        // Fetch the image URL here (service worker bypasses CORS with host_permissions)
        fetch(message.url)
            .then(res => { 
                if (!res.ok) throw new Error(`Image fetch failed: ${res.status}`);
                return res.arrayBuffer();
            })
            .then(buffer => {
                const bytes = new Uint8Array(buffer);
                let binary = '';
                for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i]);
                const base64 = btoa(binary);
                return postToBackendWithRetry({
                    image: base64,
                    translator: message.translator || 'auto',
                    target_lang: message.targetLang || 'English',
                    source_lang: message.sourceLang || 'Korean'
                });
            })
            .then(data => sendResponse(data))
            .catch(err => {
                console.error('Error:', err);
                sendResponse({ error: err.message });
            });
        return true; // keep message channel open for async response
    }
})