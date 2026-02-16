document.getElementById('scanBtn').addEventListener('click', async () => {
    const [tab] = await chrome.tabs.query({active:true, currentWindow: true});
    chrome.tabs.sendMessage(tab.id, {action: 'scan'});
    const response = await chrome.tabs.sendMessage(tab.id, {action: 'scan'});
    document.getElementById('result').innerHTML = response.count;
});


