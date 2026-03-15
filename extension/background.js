chrome.action.onClicked.addListener((tab) => {
    chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ['content.js']
    }); 
});

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
                return fetch('http://localhost:8000/translate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image: base64,
                        translator: message.translator || 'llm',
                        target_lang: message.targetLang || 'English',
                        source_lang: message.sourceLang || 'Korean'
                    })
                });
            })
            .then(res => res.json())
            .then(data => sendResponse(data))
            .catch(err => {
                console.error('Error:', err);
                sendResponse({ error: err.message });
            });
        return true; // keep message channel open for async response
    }
})