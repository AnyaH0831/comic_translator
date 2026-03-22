from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import base64, io, os
from PIL import Image
import cv2
import numpy as np
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
from groq import Groq

import json
 
# PaddleOCR low-level imports
from paddleocr.tools.infer import utility
from paddleocr.tools.infer.predict_det import TextDetector
from paddleocr.tools.infer.predict_rec import TextRecognizer

from datetime import datetime
from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential
                                
AZURE_KEY = os.getenv("AZURE_TRANSLATOR_KEY")
AZURE_REGION = os.getenv("AZURE_TRANSLATOR_REGION")  # e.g., "eastus"
AZURE_ENDPOINT = "https://api.cognitive.microsofttranslator.com"

azure_client = TextTranslationClient(
    credential=AzureKeyCredential(AZURE_KEY),
    region=AZURE_REGION
)

USAGE_FILE = "azure_usage.json"
MONTHLY_LIMIT = 2_000_000 

def get_current_month():
    return datetime.now().strftime("%Y-%m")

def load_usage():
    if not os.path.exists(USAGE_FILE):
        return {"month": get_current_month(), "characters_used": 0}
    with open(USAGE_FILE, 'r') as f:
        data = json.load(f)
    
    if data.get("month") != get_current_month():
        data = {"month": get_current_month(), "characters_used": 0 }

    return data

def save_usage(usage):
    with open(USAGE_FILE, 'w') as f:
        json.dump(usage, f)

def translate_with_azure(text, source_lang='ko', target_lang='en'):
    usage = load_usage()

    char_count = len(text)
    if usage["characters_used"] + char_count >  MONTHLY_LIMIT:
        print(f"AZURE QUOTA EXCEEDED ({usage['characters_used']}/{MONTHLY_LIMIT})")
        return None
    
    try:
        response = azure_client.translate(
            body=[text],
            from_language=source_lang,
            to_language=[target_lang]
        )

        translated = response[0].translations[0].text

        usage["characters_used"] += char_count
        save_usage(usage)

        print(f"AZURE USAGE: {usage['characters_used']:,}/{MONTHLY_LIMIT:,} chars this month")

        return translated
    
    except Exception as e:
        print(f"Azure translation error: {e}")
        return None     

def translation_text(text, source_lang='korean', target_lang='English', translator='auto'):
    lang_codes = {'Korean': 'ko', 'English': 'en', 'Chinese': 'zh'}
    source_code = lang_codes.get(source_lang, 'ko')
    target_code = lang_codes.get(target_lang, 'en')

    if translator in ['auto', 'azure']:
        azure_result = translate_with_azure(text, source_code, target_code)
        if azure_result:
            return azure_result
        else:
            print("Azure unavailable, falling back to Groq")   
    return translate_with_llm(text, source_lang, target_lang)    

load_dotenv()

app = FastAPI()
base_path = os.path.dirname(os.path.abspath(__file__))
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def init_ocr_system():
    parser = utility.init_args()
    args = parser.parse_args(args=[])
    
    # DETECTOR
    default_det_path = os.path.join(os.path.expanduser("~"), ".paddleocr", "whl", "det", "en", "en_PP-OCRv3_det_infer")
    args.det_model_dir = default_det_path 
    args.det_algorithm = 'DB'
    args.use_gpu = False
    args.det_limit_side_len = 15000
    args.det_db_thresh = 0.3
    args.det_db_box_thresh = 0.5
    det_engine = TextDetector(args)
    
    # KOREAN RECOGNIZER
    args.rec_model_dir = os.path.join(base_path, "crnn_korean_h_inference")
    args.rec_char_dict_path = os.path.join(base_path, "korean_dict.txt")
    args.rec_algorithm = "CRNN"
    args.rec_image_shape = "3, 48, 320"
    args.use_space_char = True 
    rec_engine_korean = TextRecognizer(args)
   
    # ENGLISH RECOGNIZER
    args.rec_model_dir = os.path.join(base_path, "crnn_inference")
    args.rec_char_dict_path = os.path.join(base_path, "en_dict.txt")
    args.rec_algorithm = "CRNN"
    args.rec_image_shape = "3, 32, 320"
    args.use_space_char = True
    rec_engine_english = TextRecognizer(args)

    return det_engine, rec_engine_korean, rec_engine_english

det_engine, rec_engine_korean, rec_engine_english = init_ocr_system()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

_translators = {
    ('ko', 'en'): GoogleTranslator(source='ko', target='en'),
    ('ko', 'zh-CN'): GoogleTranslator(source='ko', target='zh-CN'),
    ('en', 'zh-CN'): GoogleTranslator(source='en', target='zh-CN'),
    ('en', 'ko'): GoogleTranslator(source='en', target='ko')
}

def get_translator(source_lang, target_lang):
    lang_codes = {'Korean': 'ko', 'English': 'en', 'Chinese': 'zh-CN'}
    source_code = lang_codes.get(source_lang, 'en')
    target_code = lang_codes.get(target_lang, 'en')
    return _translators.get((source_code, target_code))

def group_nearby_boxes(results, distance_threshold=100, translator='llm', target_lang='English', source_lang='Korean'):
    if not results:
        return []
    
    sorted_results = sorted(results, key=lambda r: min(point[1] for point in r['bbox']))
    grouped = [[sorted_results[0]]]
    
    for i in range(1, len(sorted_results)):
        prev_y = sum(point[1] for point in grouped[-1][-1]['bbox']) / 4
        curr_y = sum(point[1] for point in sorted_results[i]['bbox']) / 4
        
        if abs(curr_y - prev_y) < distance_threshold:
            grouped[-1].append(sorted_results[i])
        else:
            grouped.append([sorted_results[i]])
    
    combined = []
    for group in grouped:
        combined_text = ' '.join(item['original'] for item in group)
        
        if translator == 'google':
            gt = get_translator(source_lang, target_lang)
            translated_text = gt.translate(combined_text) if gt else combined_text
        else:
            translated_text = translate_with_llm(combined_text, source_lang, target_lang)
        
        all_points = []
        for item in group:
            all_points.extend(item['bbox'])

        xs = [point[0] for point in all_points]
        ys = [point[1] for point in all_points]

        combined_bbox = [
            [min(xs), min(ys)],
            [max(xs), min(ys)],
            [max(xs), max(ys)],
            [min(xs), max(ys)]
        ]

        combined.append({
            'bbox': combined_bbox,
            'original': combined_text,
            'translated': translated_text,
            'confidence': max(item['confidence'] for item in group),
            'colors': group[0].get('colors', {'bg': 'rgb(255,255,255)', 'text': 'rgb(0,0,0)'})
        })
    
    return combined

def detect_colors(crop):
    """Detect dominant background and text colors from crop"""
    h, w = crop.shape[:2]

    edge_pixels = np.vstack([
        crop[0:5, :].reshape(-1,3),
        crop[-5:, :].reshape(-1,3),
        crop[:, 0:5].reshape(-1,3),
        crop[:, -5:].reshape(-1,3)
    ])

    # pixels = crop.reshape(-1, 3)
    unique, counts = np.unique(edge_pixels, axis=0, return_counts=True)

    # sorted_indices = counts.argsort()[::-1]

    # bg_color = unique[sorted_indices[0]]
    bg_color = unique[counts.argmax()]
    bg_brightness = (0.299*bg_color[2] + 0.587 * bg_color[1] + 0.114*bg_color[0])

    if bg_brightness < 128:
        text_color = np.array([255,255,255])
    else:
        text_color = np.array([0,0,0])

    print(f"    Colors: BG brightness={bg_brightness:.0f}, bg=rgb({bg_color[2]},{bg_color[1]},{bg_color[0]}), text=rgb({text_color[2]},{text_color[1]},{text_color[0]})")

    # text_color = 255 - bg_color

    return{
        'bg': f'rgb({bg_color[2]}, {bg_color[1]}, {bg_color[0]})',
        'text': f'rgb({text_color[2]}, {text_color[1]}, {text_color[0]})'
    }


class TranslateRequest(BaseModel):
    image: str
    translator: str = 'llm'
    target_lang: str = 'English'
    source_lang: str = 'Korean'

@app.post("/translate")
async def translate(request: TranslateRequest):
    try: 
        print(f"\n=== {request.source_lang} → {request.target_lang} ({request.translator}) ===")

        decoded_bytes = base64.b64decode(request.image)
        imagePIL = Image.open(io.BytesIO(decoded_bytes)).convert('RGB')
        img = cv2.cvtColor(np.array(imagePIL), cv2.COLOR_RGB2BGR)

        rec_engine = rec_engine_korean if request.source_lang == 'Korean' else rec_engine_english
        
        dt_boxes, _ = det_engine(img)
        print(f"Detected {len(dt_boxes) if dt_boxes is not None else 0} text boxes")
        
        final_results = []
        if dt_boxes is not None and len(dt_boxes) > 0:
            for box in dt_boxes:
                pts = np.array(box, dtype=np.float32)
                x1, y1 = pts.min(axis=0).astype(int)
                x2, y2 = pts.max(axis=0).astype(int)
                
                p = 3
                x1, y1 = max(0, x1-p), max(0, y1-p)
                x2, y2 = min(img.shape[1], x2+p), min(img.shape[0], y2+p)
                
                crop = img[y1:y2, x1:x2]
                if crop.size == 0:
                    continue
                 
                rec_res, _ = rec_engine([crop])
                if rec_res and len(rec_res) > 0:
                    text, score = rec_res[0]
                    
                    if score >= 0.70:
                        colors = detect_colors(crop)
                        print(f"  {text} ({score:.2f})")

                        final_results.append({
                            'bbox': box.tolist(),
                            'original': text,
                            'confidence': float(score),
                            'colors': colors
                        })

        
        final_results = group_nearby_boxes(final_results, translator=request.translator, 
                                          target_lang=request.target_lang, source_lang=request.source_lang)
        
        return {"results": final_results}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}, 500

def translate_with_llm(text, source_lang='Korean', target_lang='English'):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        messages=[
            {"role": "system", "content": "You are a translator. Only output the translation."},
            {"role": "user", "content": f"Translate this {source_lang} comic dialogue to {target_lang}: {text}\n\nTranslation:"}
        ]
    )
    return response.choices[0].message.content 