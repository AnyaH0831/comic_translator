// Load custom font from extension
const fontURL = chrome.runtime.getURL('fonts/Bangers-Regular.ttf');

const fontFace = new FontFace('Bangers', `url(${fontURL})`);
fontFace.load().then((loadedFont) => {
    document.fonts.add(loadedFont);
    console.log('Bangers font loaded!');
}).catch((error) => {
    console.error('Font loading failed:', error);
});


//Bar toggle
const _existingBar = document.getElementById('comic-translator-bar');

if (_existingBar) {
    const isHidden = _existingBar.style.display === 'none' || _existingBar.style.display === '';
    _existingBar.style.display = isHidden ? 'flex' : 'none';
    document.body.style.marginTop = isHidden ? '60px' : '';
} else {
    

let topBar = null;
let overlays = [];
let barVisible = false;
let isScanning = false;
let abortController = null;

function createTopBar() {
    if (topBar) return;

    topBar = document.createElement('div');
    topBar.id = 'comic-translator-bar';
    topBar.style.cssText = `
        position: fixed; 
        top: 0;
        left: 0;
        width: 100%;
        height: 60px;
        background: #E2EAFC;
        color: #173E99;
        z-index: 999999;
        display: flex;
        align-items: center;
        padding: 0 20px;
        box-sizing: border-box;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        font-family: 'Bangers', cursive, -apple-system, sans-serif;
    `;

    topBar.innerHTML = `
        <h3 style="margin: 0; flex-shrink: 0;"> Comic Translator</h3>

        <select id="ct-source-lang" style="margin-left: 20px; padding: 8px; border-radius: 5px; border: none;">
            <option value="English">English</option>
            <option value="Korean" selected>Korean</option>
        </select>

        <span style="margin: 0 10px;">→</span>

        <select id="ct-target-lang" style="padding: 8px; border-radius: 5px; border: none;">
            <option value="English" selected>English</option>
            <option value="Chinese">Chinese</option>
        </select>

        <select id="ct-translator" style="margin-left: 20px; padding: 8px; border-radius: 5px; border: none;">
            <option value="google" selected>Google Translate</option>
            <option value="llm">LLM (Groq)</option>
        </select>

        <button id="ct-scan" style="margin-left: 10px; padding: 8px 20px; background: #B6CCFE; color: #173E99; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">
             ▶ Scan
        </button>

        <button id="ct-clear" style="margin-left: 10px; padding: 8px 20px; background: rgb(100, 6, 6); color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">
             Clear
        </button>

        <div id="ct-progress" 
            style="margin-left: auto; 
                    display: none;
                    align-items: center;">
            <span id="ct-progress-text" style="margin-right: 10px;"> 0 / 0</span>
            <div style="width: 200px; height: 8px; background: #c0c0c0; border-radius: 4px; overflow: hidden;">
                <div id="ct-progress-bar" style="width: 0%; height: 100%; background: #173E99; transition: width 0.3s;"></div>
            </div>
        </div>
    `;

    topBar.style.display = 'none';
    document.body.prepend(topBar);

    document.getElementById('ct-scan').addEventListener('click', scanPage);
    document.getElementById('ct-clear').addEventListener('click', clearOverlays);
}

function toggleBar() {
    if (!topBar) createTopBar();
    barVisible = !barVisible;
    topBar.style.display = barVisible ? 'flex' : 'none';
    document.body.style.marginTop = barVisible ? '60px' : '';
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        createTopBar();
        toggleBar(); 
    });
} else {
    createTopBar();
    toggleBar();
}

// Use this to load images so the overlay actually shows on the page
// async function loadAllImages() {
//     const originalScroll = window.scrollY;

//     document.body.style.overflow = 'hidden';
//     const scrollContainer = document.scrollingElement || document.documentElement;

//     return new Promise((resolve) => {
//         // let lastHeight = document.body.scrollHeight;
//         let scrollAttempts = 0;
//         const maxAttempts = 50;

//         const scrollInternal = setInterval(() => {
//             scrollContainer.scrollTop += window.innerHeight;
//             scrollAttempts++;

//             const newHeight = scrollContainer.scrollHeight;

//             if (scrollContainer.scrollTop + window.innerHeight >= newHeight || scrollAttempts >= maxAttempts) {
//                 clearInterval(scrollInterval);
                
//                 // Restore viewport
//                 scrollContainer.scrollTop = originalScroll;
//                 document.body.style.overflow = '';
                
//                 setTimeout(() => resolve(), 500);
//             }
//         }, 50);
//     })
// } 

async function loadAllImages() {
    const originalScroll = window.scrollY;
    
    // Create loading overlay with spinner
    const loadingOverlay = document.createElement('div');
    loadingOverlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.95);
        z-index: 9999999;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: Arial, sans-serif;
    `;
    loadingOverlay.innerHTML = `
        <div style="text-align: center;">
            <div class="spinner" style="
                border: 4px solid #f3f3f3;
                border-top: 4px solid #173E99;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            "></div>
            <div style="font-size: 18px; color: #173E99;">Loading comic images...</div>
            <div style="font-size: 14px; margin-top: 5px; opacity: 0.7; color: #173E99;">Please wait</div>
        </div>
    `;    
    
    // Add spinner animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(loadingOverlay);

    return new Promise((resolve) => {
        let scrollAttempts = 0;
        const maxAttempts = 50;
        
        const scrollInterval = setInterval(() => {
            window.scrollBy(0, window.innerHeight);
            scrollAttempts++;
            
            const newHeight = document.body.scrollHeight;
            
            if (window.scrollY + window.innerHeight >= newHeight || scrollAttempts >= maxAttempts) {
                clearInterval(scrollInterval);
                window.scrollTo(0, originalScroll);
                
                // Remove overlay and style
                loadingOverlay.remove();
                style.remove();
                
                setTimeout(() => resolve(), 300);
            }
        }, 50);
    });
}

async function scanPage() {

    if (isScanning){
        console.log('Scan already in progress, canceling previous scan...');
        if (abortController){
            abortController.abort();
        }
        clearOverlays();
        isScanning = false;
    }

    isScanning = true;
    abortController = new AbortController();
    const signal = abortController.signal;

    const sourceLang = document.getElementById('ct-source-lang').value;
    const targetLang = document.getElementById('ct-target-lang').value;
    const translator = document.getElementById('ct-translator').value;

    const progressDiv = document.getElementById('ct-progress');
    const progressBar = document.getElementById('ct-progress-bar');
    const progressText = document.getElementById('ct-progress-text');

    progressDiv.style.display = 'flex';
    progressText.textContent = 'Loading images...';
    progressBar.style.width = '0%';

    try{
        await loadAllImages();

        const images = Array.from(document.querySelectorAll('img'))
            .filter(img => img.offsetWidth >= 300);

        if (images.length === 0) {
            alert('No comic images found! Try scrolling down to load images.');
            progressDiv.style.display = 'none';
            return;
        } 

        clearOverlays();

        progressText.textContent = `0 / ${images.length}`;
        progressBar.style.width = '0%';

        // const progressDiv = document.getElementById('ct-progress');
        // const progressBar = document.getElementById('ct-progress-bar');
        // const progressText = document.getElementById('ct-progress-text');

        progressDiv.style.display = 'flex';
        progressText.textContent = `0 / ${images.length}`;
        progressBar.style.width = '0%';
 
        for (let i = 0; i < images.length; i++) {
            const img = images[i];

            console.log(`\nImage ${i + 1}/${images.length}:`);
            console.log(`  URL: ${img.src.substring(0, 80)}...`);
            console.log(`  Position: (${img.getBoundingClientRect().top}, ${img.getBoundingClientRect().left})`);

            progressText.textContent = `${i + 1} / ${images.length}`;
            progressBar.style.width = `${((i + 1) / images.length) * 100}%`;

            try {
                // Send URL to background.js, worker fetches bypass CORS via host_permissions
                const response = await new Promise((resolve, reject) => {
                    if (!chrome?.runtime?.id) {
                        reject(new Error('Extension context invalidated. Please reload the page (F5) and try again.'));
                        return;
                    }
                    chrome.runtime.sendMessage(
                        { action: 'fetchImage', url: img.src, translator, targetLang, sourceLang },
                        (res) => {
                            if (chrome.runtime.lastError) reject(new Error(chrome.runtime.lastError.message));
                            else resolve(res);
                        }
                    );
                });

                console.log(`Got Response:`, response);

                if (response && response.results) {
                    console.log(`${response.results.length} text blocks found`);
                    renderOverlays(img, response.results);
                }else{
                    console.log('No results');
                }
            } catch (error) {
                console.error('Error processing image:', img.src, error);
            }
        }

        setTimeout(() => {
            progressDiv.style.display = 'none';
        }, 2000);
    } catch(error){
        if (error.message === 'Scan cancelled'){
            console.log('Scan cancelled by user');
        }else{
            console.error('Scan error:', error);
        }
        progressDiv.style.display = 'none';
    }finally{
        isScanning = false;
        abortController = null;
    }
    
}


function renderOverlays(imgElement, results) {
    const imgRect = imgElement.getBoundingClientRect();
    const imgNaturalWidth = imgElement.naturalWidth;
    const imgNaturalHeight = imgElement.naturalHeight;

    const targetLang = document.getElementById('ct-target-lang').value;

    results.forEach(result => {
        const bbox = result.bbox;
        const xs = bbox.map(point => point[0]);
        const ys = bbox.map(point => point[1]);
        const minX = Math.min(...xs);
        const minY = Math.min(...ys);
        const maxX = Math.max(...xs);
        const maxY = Math.max(...ys);

        const scaleX = imgRect.width / imgNaturalWidth;
        const scaleY = imgRect.height / imgNaturalHeight;

        const boxWidth = (maxX - minX) * scaleX;
        const boxHeight = (maxY - minY) * scaleY;


        let displayText = result.translated;
        let fontFamily = 'Arial, sans-serif';

        if (targetLang === 'English'){
            displayText = displayText.toUpperCase();
            // fontFamily = '"Comic Sans MS", "Bangers", "Imapct", cursive, sans-serif';
            fontFamily = '"Bangers", "Comic Sans MS", cursive';
            // fontFamily = '"BangersCustom", "Comic Sans MS", "Arial Black", sans-serif';
            // fontFamily = '"Bradley Hand", "Comic Sans MS", "Marker Felt", cursive';
        }


        const tempDiv = document.createElement('div');
        tempDiv.style.cssText = `
            position: absolute;
            visibility: hidden;
            width: ${boxWidth - 12}px;
            font-family: ${fontFamily};
            font-weight: normal;
            word-wrap: break-word;
            overflow-wrap: break-word;
            line-height: 1.1;
            padding: 6px;
            box-sizing: border-box;
        `;

        tempDiv.textContent = displayText;
        document.body.appendChild(tempDiv);

        let minSize = 10;
        let maxSize = 40;
        let optimalSize = minSize;

        while (minSize <= maxSize){
            const testSize = Math.floor((minSize+maxSize)/2);
            tempDiv.style.fontSize = testSize + 'px';

            if (tempDiv.scrollHeight <= boxHeight-12){
                optimalSize = testSize;
                minSize=testSize+1;

            }else{
                maxSize = testSize-1;
            }
        }


        document.body.removeChild(tempDiv);

        const fontSize = Math.max(12, Math.min(optimalSize, 52));

        // const textLength = displayText.length;

        // const estimatedCharsPerLine = Math.floor(boxWidth/12)
        // const estimatedLines = Math.max(1, Math.ceil(textLength/estimatedCharsPerLine));

        // const fontSizeByHeight = boxHeight/(estimatedLines*1.3);
        // const fontSizeByWidth = boxWidth/(estimatedCharsPerLine * 0.65);

        // const fontSize = Math.max(12, Math.min(fontSizeByHeight, fontSizeByWidth, 24));

        // const baseFontSize = Math.sqrt(boxWidth*boxHeight)/5;
        // const fontSize = Math.max(14, Math.min(baseFontSize, 22));

        // const charCount = displayText.length;
        // const avgCharWidth = 0.6;
        // const lines = Math.ceil((charCount * avgCharWidth * boxHeight * 0.2)/boxWidth) || 1;


        // let fontSize = Math.min(
        //     boxHeight/(lines*1.3),
        //     boxWidth/(charCount/lines*avgCharWidth),
        //     28
        // )

        // fontSize = Math.max(fontSize, 14);



        // const estimatedFontSize = Math.max(12, Math.min(boxHeight*0.15, 24));

        // const textLength = displayText.length;
        // const availableWidth = boxWidth - padding * 2;
        // const availableHeight = boxHeight - padding *2;


        // let fontSize = Math.min(
        //     availableHeight/3,
        //     availableWidth/(textLength*0.6),
        //     20
        // );

        // fontSize = Math.max(fontSize, 10);

        let bgColor;
        let textColor;

        if (result.colors && result.colors.bg){
            bgColor = result.colors.bg;
        }else{
            bgColor = 'white';
        }

        if (result.colors && result.colors.text){
            textColor = result.colors.text;
        }else{
            textColor = 'black';
        }

        const overlay = document.createElement('div');
        overlay.className = 'comic-translator-overlay';
        overlay.dataset.imageId = imgElement.src;

        overlay.style.cssText = `
            position: absolute;
            left: ${imgRect.left + window.scrollX + minX * scaleX}px;
            top: ${imgRect.top + window.scrollY + minY * scaleY}px;
            width: ${boxWidth}px;
            height: ${boxHeight}px;
            background: ${bgColor};
            color: ${textColor};
            padding: 8px;
            font-size: ${fontSize}px;
            font-weight: bold;
            font-family: ${fontFamily};
            letter-spacing: ${targetLang === 'English' ? '0.5px':'normal'};
            line-height: 1.2;
            z-index: 999998;
            pointer-events: none;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            word-wrap: break-word;
            overflow-wrap: break-word;
            overflow: hidden;
            box-sizing: border-box;
        `;

        overlay.style.setProperty('font-family', fontFamily, 'important');

        overlay.textContent = displayText;
        document.body.appendChild(overlay);
        overlays.push(overlay);

        console.log('Applied font-family:', overlay.style.fontFamily);
        console.log('Computed font:', window.getComputedStyle(overlay).fontFamily);
    }); 
}   

function clearOverlays() {
    overlays.forEach(o => o.remove());
    overlays = [];
}

} 