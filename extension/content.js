// Load custom font from extension
const fontURL = chrome.runtime.getURL('fonts/Bangers-Regular.ttf');

const fontFace = new FontFace('Bangers', `url(${fontURL})`);
fontFace.load().then((loadedFont) => {
    document.fonts.add(loadedFont);
    // console.log('Bangers font loaded!');
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
let overlayVisible = true;  

function createTopBar() {
    if (topBar) return;

    topBar = document.createElement('div');

    topBar.id = 'comic-translator-bar'
   
    topBar.style.cssText = `
        position: fixed; 
        top: 0;
        left: 0;
        width: 100%;
        height: 50px;
        background: linear-gradient(135deg, #111827  100%) !important;
        color: #ffffff !important;
        z-index: 999999 !important;
        display: flex !important; 
        align-items: center !important;
        padding: 0 20px !important;
        box-sizing: border-box !important;
        box-shadow: 0 4px 20px rgba(0, 145, 173, 0.4);
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace !important;
        border-bottom: 4px solid #0091ad;
    `;

    topBar.innerHTML = `

        <div id='ct-progress-bar' style='position: absolute; top:0; left:0; width:0%; height: 4px; background: #00ffcc; transition: width 0.3s; z-index:10;'></div>
        <h3 style="margin: 0; flex-shrink: 0;"> Comic Translator</h3>

        <select id="ct-source-lang">
            <option value="English">English</option>
            <option value="Korean" selected>Korean</option>
        </select>  

        <span style="margin: 0 10px;">→</span>

        <select id="ct-target-lang">
            <option value="English" selected>English</option>
            <option value="Chinese">Chinese</option>    
        </select>   

        <div style="display: flex; justify-content: flex-end; width: 100%;">
            <button id="ct-scan" style="min-width: 50px; margin-right: 10px; padding: 4px 10px; background: #0091ad; color: white; border: none; border-radius: 2px; cursor: pointer; font-weight: bold; font-size: 14px">
                Scan
            </button>   

            <button id="ct-toggle" style="margin-right: 10px; padding: 4px 10px; background: #5c4d7d; color: white; border: none; border-radius: 2px; cursor: pointer; font-weight: bold; font-size: 14px">
                Hide
            </button>
            <button id="ct-clear" style=" padding: 4px 10px; background: #a01a58; color: white; border: none; border-radius: 2px; cursor: pointer; font-weight: bold; font-size: 14px">
                Clear
            </button>            
 
        </div>
    `; 

    

    const style = document.createElement('style');
    style.textContent = `
        #comic-translator-bar h3 {
            color: white !important;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace !important;
            font-weight: normal;
            font-size: 14px;
        }

        #ct-scan:hover {
            box-shadow: 0 0 25px rgba(0, 145, 173, 0.8) !important;
            transform: translateY(-2px);
        }
        #ct-toggle:hover {
            box-shadow: 0 0 25px rgba(92, 77, 125, 0.8) !important;   
            transform: translateY(-2px);
        }
        #ct-clear:hover {
            box-shadow: 0 0 25px rgba(183, 9, 76, 0.8) !important;
            transform: translateY(-2px);
        }

        #ct-source-lang, 
        #ct-target-lang {
            appearance: none !important;
            -webkit-appearance: none !important;
            width: 130px !important;
            margin-left: 20px !important;
            padding: 4px 8px !important;
            border-radius: 2px !important;
            border: none;
            background: #1a1a2e !important;
            color: #e9ecef !important;
            font-weight: bold !important;
            font-size: 13px !important;
            cursor: pointer !important;
        }

        #ct-source-lang option,
        #ct-target-lang option {
            background: #1a1a2e !important;
            color: #e9ecef !important;
        }

        #ct-source-lang option:checked,  
        #ct-target-lang option:checked {
            background: #b7094c !important;  
            color: white !important;
            font-weight: bold !important; 
        }

        #ct-source-lang:hover,
        #ct-target-lang:hover {
            font-weight: bold !important;
            color: #b7094c !important;
        }

        #ct-source-lang:focus,
        #ct-target-lang:focus {
            outline: none !important;
            color: #b7094c !important;
        }

    `;

    document.head.appendChild(style);


    topBar.style.display = 'none';
    document.body.prepend(topBar);

    document.getElementById('ct-scan').addEventListener('click', scanPage);
    document.getElementById('ct-toggle').addEventListener('click', toggleOverlays);
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


 
async function loadAllImages() {

    window.scrollTo(0,0);
    await new Promise(resolve => setTimeout(resolve, 500));

    const originalScroll = window.scrollY;
    
    // Create loading overlay with spinner
    const loadingOverlay = document.createElement('div');
    loadingOverlay.style.cssText = `
        position: fixed !important;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.95) !important;
        z-index: 9999999;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace !important;
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
        const maxAttempts = 200;
        
        const scrollInterval = setInterval(() => {
            window.scrollBy(0, window.innerHeight);
            scrollAttempts++;
            
            const newHeight = document.body.scrollHeight;
            
            if (window.scrollY + window.innerHeight >= newHeight || scrollAttempts >= maxAttempts) {
                clearInterval(scrollInterval);

                setTimeout(() => {
                    window.scrollTo(0, originalScroll);
                    loadingOverlay.remove();
                    style.remove();
                    resolve();
                }, 3000);  

                // window.scrollTo(0, originalScroll);
                
                // loadingOverlay.remove();
                // style.remove();
                
                // setTimeout(() => resolve(), 300);
            }
        }, 100);
    });
}

async function scanPage() {

    const scanBtn = document.getElementById('ct-scan');
    

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
    // const translator = document.getElementById('ct-translator').value;

    // const progressDiv = document.getElementById('ct-progress');
    const progressBar = document.getElementById('ct-progress-bar');

    scanBtn.innerText = 'Waking up server...'
    scanBtn.disabled = true;

    progressBar.style.width = '0%';

    try{
        await loadAllImages();

        scanBtn.innerText = 'Scanning...';

        const images = Array.from(document.querySelectorAll('img'))
            .filter(img => {

                if (img.offsetWidth < 300 || img.offsetHeight < 100){
                    return false;
                }

                if (img.src.includes('bg_transparency.png')){
                    return false;
                }

                if (img.naturalWidth<= 1|| img.naturalHeight <= 1){
                    console.log(`Skipping placeholder image: ${img.src.substring(0,50)}...`);
                    return false
                }

                return true;
 
                // img.offsetWidth >= 300);
                // }
            }); 
        if (images.length === 0) {
            alert('No comic images found! Try scrolling down to load images.');
            // progressDiv.style.display = 'none';
            return;
        } 

        clearOverlays();

        // progressText.textContent = `0 / ${images.length}`;
        progressBar.style.width = '0%';

        // const progressDiv = document.getElementById('ct-progress');
        // const progressBar = document.getElementById('ct-progress-bar');
        // const progressText = document.getElementById('ct-progress-text');

        // progressDiv.style.display = 'flex';
        // progressText.textContent = `0 / ${images.length}`;
        progressBar.style.width = '0%';
 
        for (let i = 0; i < images.length; i++) {
            const img = images[i];

            if (signal.aborted){
                break;
            }

            const current = i+1;
            const total = images.length
            const percent = (current/total)*100;

            // progressText.textContent = `${i + 1} / ${images.length}`;
            progressBar.style.width = `${((i + 1) / images.length) * 100}%`;
            scanBtn.innerText = `Scanning ${current}/${total}`;

            try {

                let base64Image;

                try{
                    const imgBlob = await fetch(img.src).then(r=> r.blob());
                    const reader = new FileReader();

                    base64Image = await new Promise((resolve, reject) => {
                        reader.onloadend = () => {
                            const base64 = reader.result.split(',')[1];
                            resolve(base64);
                        };
                        reader.onerror = reject;
                        reader.readAsDataURL(imgBlob);
                    });
     
                }catch (fetchError){
                    // console.log('Direct fetch failed, using background script...');

                    const bgResponse = await new Promise((resolve, reject) => {
                        if (!chrome?.runtime?.id) {      
                            reject(new Error('Extension context invalidated. Please reload the page (F5) and try again.'));
                            return;
                        }
                        chrome.runtime.sendMessage(
                            { action: 'fetchImage', url: img.src, targetLang, sourceLang },
                            (res) => {
                                if (chrome.runtime.lastError) reject(new Error(chrome.runtime.lastError.message));
                                else resolve(res);
                            }
                        );   
                    });

                    if (bgResponse && bgResponse.results) {
                        // console.log(`${bgResponse.results.length} text blocks found`);
                        renderOverlays(img, bgResponse.results);
                        continue; // Skip to next image
                    } else if (bgResponse && bgResponse.error) {
                        console.error('Background fetch error:', bgResponse.error);
                        continue;
                    }
                }

                if (base64Image) {
                    // const backendResponse = await fetch('http://localhost:8000/translate', {
                    const backendResponse = await fetch('http://155.248.218.39:8000/translate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            image: base64Image,
                            translator: 'auto',
                            target_lang: targetLang,
                            source_lang: sourceLang
                        })
                    });

                    if (!backendResponse.ok) {
                        const errorText = await backendResponse.text();
                        console.error(`Backend error ${backendResponse.status}:`, errorText);
                        continue;
                    }

                    const response = await backendResponse.json();

                    // console.log(`Got Response:`, response);

                    if (response && response.results) {
                        console.log(`${response.results.length} text blocks found`);
                        renderOverlays(img, response.results);
                    } else {
                        console.log('No results', response);
                    }
                }
                scanBtn.innerText = 'Scan';
                scanBtn.disabled = false;
                // const backendResponse = await fetch('http://localhost:8000/translate',{
                //     method: 'POST',
                //     headers: {'Content-Type': 'application/json'},
                //     body: JSON.stringify({
                //         image: base64Image,
                //         translator: 'auto',
                //         target_lang: targetLang,
                //         source_lang: sourceLang
                //     })
                // });

                // const response = await backendResponse.json();

                // console.log(`Got Response:`, response);

                // // Send URL to background.js, worker fetches bypass CORS via host_permissions
                // const response = await new Promise((resolve, reject) => {
                //     if (!chrome?.runtime?.id) {
                //         reject(new Error('Extension context invalidated. Please reload the page (F5) and try again.'));
                //         return;
                //     }
                //     chrome.runtime.sendMessage(
                //         { action: 'fetchImage', url: img.src, targetLang, sourceLang },
                //         (res) => {
                //             if (chrome.runtime.lastError) reject(new Error(chrome.runtime.lastError.message));
                //             else resolve(res);
                //         }  
                //     );
                // });
               
                // if (response && response.results) {
                //     console.log(`${response.results.length} text blocks found`);
                //     renderOverlays(img, response.results);
                // }else{
                //     console.log('No results');
                // }
            } catch (error) {
                console.error('Error processing image:', img.src, error);
                scanBtn.innerText = 'Scan';
                scanBtn.disabled = false;
            }
        }

        setTimeout(() => {
            // progressDiv.style.display = 'none';
        }, 2000);
    } catch(error){
        if (error.message === 'Scan cancelled'){
            console.log('Scan cancelled by user');
        }else{
            console.error('Scan error:', error);
        }
        // progressDiv.style.display = 'none';
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
            font-family: ${fontFamily} !important;
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
            font-weight: normal;
            font-family: ${fontFamily} !important;
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

        // console.log('Applied font-family:', overlay.style.fontFamily);
        // console.log('Computed font:', window.getComputedStyle(overlay).fontFamily);
    }); 
}   

function clearOverlays() {
    overlays.forEach(o => o.remove());
    overlays = [];
    overlayVisible = true;

    const toggleBtn = document.getElementById('ct-toggle');
    if (toggleBtn) {
        toggleBtn.textContent = 'Hide';
    }
} 

function toggleOverlays() {
    overlayVisible = !overlayVisible;
    const toggleBtn = document.getElementById('ct-toggle');

    overlays.forEach(overlay => {
        overlay.style.display = overlayVisible ? 'flex':'none';
    });

    toggleBtn.textContent = overlayVisible ? 'Hide': 'Show';
}
}
