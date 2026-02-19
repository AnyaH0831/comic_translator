chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'fetchImage'){
        fetch(message.url)
            .then(res => res.blob())
            .then(blob => {
                const reader = new FileReader();
                reader.onloaded = () => {
                    const base64 = reader.result.split(',')[1];
                    sendResponse({base64});
                }

                reader.readAsDataURL(blob);
            })
        return true;
    }
})