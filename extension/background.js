chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'fetchImage'){
        fetch(message.url)
            .then(res => res.blob())
            .then(blob => {
                const reader = new FileReader();
                reader.onloadend = () => {
                    const base64 = reader.result.split(',')[1];

                    fetch('http://localhost:8000/translate', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({image: base64})
                    })

                    .then(res => res.json())
                    .then(data => {
                        sendResponse(data);
                    }); 
              
                };

                reader.readAsDataURL(blob);
            })
        return true;
    }
})