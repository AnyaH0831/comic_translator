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
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
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

async function scanPage() {
    const sourceLang = document.getElementById('ct-source-lang').value;
    const targetLang = document.getElementById('ct-target-lang').value;
    const translator = document.getElementById('ct-translator').value;

    const images = Array.from(document.querySelectorAll('img'))
        .filter(img => img.offsetWidth >= 300);

    if (images.length === 0) {
        alert('No comic images found! Try scrolling down to load images.');
        return;
    }

    clearOverlays();

    const progressDiv = document.getElementById('ct-progress');
    const progressBar = document.getElementById('ct-progress-bar');
    const progressText = document.getElementById('ct-progress-text');

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
}


function renderOverlays(imgElement, results) {
    const imgRect = imgElement.getBoundingClientRect();
    const imgNaturalWidth = imgElement.naturalWidth;
    const imgNaturalHeight = imgElement.naturalHeight;

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

        const padding = 10;
        const boxWidth = (maxX - minX) * scaleX;
        const boxHeight = (maxY - minY) * scaleY;

        const overlay = document.createElement('div');
        overlay.className = 'comic-translator-overlay';

        overlay.dataset.imageId = imgElement.src;

        overlay.style.cssText = `
            position: absolute;
            left: ${imgRect.left + window.scrollX + minX * scaleX - padding}px;
            top: ${imgRect.top + window.scrollY + minY * scaleY - padding}px;
            width: ${boxWidth + padding * 2}px;
            min-height: ${boxHeight + padding*2}px;
            background: rgba(255, 255, 255, 0.95);
            color: black;
            padding: 8px;
            font-size: 14px;
            font-weight: bold;
            border: 2px solid #ccc;
            border-radius: 6px;
            z-index: 999998;
            pointer-events: none;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            word-wrap: break-word;
            overflow-wrap: break-word;
            box-sizing: border-box;
        `;
        overlay.textContent = result.translated;
        document.body.appendChild(overlay);
        overlays.push(overlay);
    });
}

function clearOverlays() {
    overlays.forEach(o => o.remove());
    overlays = [];
}

} 

