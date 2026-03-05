document.getElementById('scanBtn').addEventListener('click', async () => {
    const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
    const result = document.getElementById('result');
    const translator = document.getElementById('translatorSelect').value;
    result.textContent = 'Scanning...';
    document.getElementById('scanBtn').disabled = true;

    chrome.tabs.sendMessage(tab.id, {action: 'scan', translator}, (response) => {
        if (response && response.count !== undefined) {
            result.textContent = `Found ${response.count} image(s). Translating in background...`;
        } else {
            result.textContent = 'No images found.';
        }
        document.getElementById('scanBtn').disabled = false;
    });
});
