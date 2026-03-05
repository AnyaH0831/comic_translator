
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    const images = document.querySelectorAll('img');
    const filteredImg = Array.from(images).filter(image => image.offsetWidth >= 300);
    const translator = message.translator || 'llm';

    filteredImg.forEach(img => {
        chrome.runtime.sendMessage(
            {
                action: 'fetchImage',
                url: img.src,
                translator
            },
            (response) => {
                if (!response || !response.results) return;

                const imgRect = img.getBoundingClientRect();
                const imgNaturalWidth = img.naturalWidth;
                const imgNaturalHeight = img.naturalHeight;

                response.results.forEach(result => {
                    const bbox = result.bbox;
                    const xs = bbox.map(point => point[0]);
                    const ys = bbox.map(point => point[1]);
                    const minX = Math.min(...xs);
                    const minY = Math.min(...ys);
                    const maxX = Math.max(...xs);
                    const maxY = Math.max(...ys);

                    const scaleX = imgRect.width / imgNaturalWidth;
                    const scaleY = imgRect.height / imgNaturalHeight;

                    const overlay = document.createElement('div');
                    overlay.style.position = 'absolute';
                    overlay.style.left = (imgRect.left + window.scrollX + minX * scaleX) + 'px';
                    overlay.style.top = (imgRect.top + window.scrollY + minY * scaleY) + 'px';
                    overlay.style.width = ((maxX - minX) * scaleX) + 'px';
                    overlay.style.height = ((maxY - minY) * scaleY) + 'px';
                    overlay.style.backgroundColor = 'rgba(255, 255, 255, 0.9)';
                    overlay.style.color = 'black';
                    overlay.style.padding = '5px';
                    overlay.style.fontSize = '14px';
                    overlay.style.fontWeight = 'bold';
                    overlay.style.border = '1px solid #ccc';
                    overlay.style.zIndex = '9999';
                    overlay.style.pointerEvents = 'none';
                    overlay.textContent = result.translated;

                    document.body.appendChild(overlay);
                });
            }
        );
    });

    sendResponse({ count: filteredImg.length });
    return true;
});
