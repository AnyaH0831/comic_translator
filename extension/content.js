
chrome.runtime.onMessage.addListener(async (message, sender, sendResponse) => {
    const images = document.querySelectorAll('img');

    const filteredImg = Array.from(images).filter(image => image.offsetWidth >= 300);
    
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    canvas.width = filteredImg[0].naturalWidth;
    canvas.height = filteredImg[0].naturalHeight;

    ctx.drawImage(filteredImg[0], 0, 0);

    const base64 = canvas.toDataURL('image/jpeg').split(',')[1];
    console.log(base64.substring(0,100));

    sendResponse({count: filteredImg.length});
    // console.log(filteredImg.length);

    const response = await fetch('http://localhost:8000/translate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({image: base64})
    });

    const data = await response.json();
    console.log(data);
}) 

