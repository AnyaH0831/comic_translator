chrome.runtime.onMessage.addListener((message) => {
    const images = document.querySelectorAll('img');

    console.log(images.length);
}) 