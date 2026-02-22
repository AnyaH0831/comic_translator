
chrome.runtime.onMessage.addListener(async (message, sender, sendResponse) => {
    const images = document.querySelectorAll('img');

    const filteredImg = Array.from(images).filter(image => image.offsetWidth >= 300);
    
    // const canvas = document.createElement('canvas');
    // const ctx = canvas.getContext('2d');

    // canvas.width = filteredImg[0].naturalWidth;
    // canvas.height = filteredImg[0].naturalHeight;

    // ctx.drawImage(filteredImg[0], 0, 0);

    // const base64 = canvas.toDataURL('image/jpeg').split(',')[1];
    // console.log(base64.substring(0,100));

    chrome.runtime.sendMessage(
        {
        action: 'fetchImage',
        url: filteredImg[0].src
    },

    (response) => {
        console.log(response);
    }
    
    );


    sendResponse({count: filteredImg.length});
    // console.log(filteredImg.length);
    return true;
}) 

