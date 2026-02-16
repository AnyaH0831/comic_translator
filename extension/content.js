chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    const images = document.querySelectorAll('img');

    const filteredImg = Array.from(images).filter(image => image.offsetWidth >= 300);
    
    sendResponse({count: filteredImg.length});
    // console.log(filteredImg.length);
}) 