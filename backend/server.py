from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import base64
import io 
import os
from PIL import Image
import cv2
  
import numpy as np
from paddleocr import PaddleOCR
from paddleocr.tools.infer.predict_rec import TextRecognizer

app = FastAPI()

base_path = os.path.dirname(os.path.abspath(__file__))

from paddleocr.tools.infer import utility
from paddleocr.tools.infer.predict_det import TextDetector

from deep_translator import GoogleTranslator
_google_translator_en = GoogleTranslator(source='ko', target='en')
_google_translator_zh = GoogleTranslator(source='ko', target='zh-CN')
_google_translator_en_from_en = GoogleTranslator(source='en', target='zh-CN')


from dotenv import load_dotenv
load_dotenv()

from groq import Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# ocr = PaddleOCR(
#     use_angle_cls=True,
#     lang='korean',
#     # rec_model_dir='./crnn_inference',
#     rec_model_dir='./crnn_korean_h_inference',

#     rec_algorithm='CRNN',
#     use_gpu=False,
#     show_log=False
# )


default_det_path = os.path.join(os.path.expanduser("~"), ".paddleocr", "whl", "det", "en", "en_PP-OCRv3_det_infer")

def init_ocr_system():
   
    # ocr_korean = PaddleOCR(
    #     use_angle_cls = True,
    #     lang = 'korean',
    #     rec_model_dir = './crnn_korean_h_inference',
    #     rec_algorithm = 'CRNN',
    #     use_gpu=False,
    #     show_log=False,
    #     det_db_thresh=0.3,
    #     det_db_box_thresh=0.5
    # )

    # ocr_english = PaddleOCR(
    #     use_angle_cls = True,
    #     lang='en',
    #     rec_model_dir='./crnn_inference',
    #     rec_algorithm = 'CRNN',
    #     use_gpu=False,
    #     show_log=False,
    #     det_db_thresh=0.2,
    #     det_db_box_thresh=0.3
    # )

    parser = utility.init_args()
    args = parser.parse_args(args=[])
    
    default_det_path = os.path.join(os.path.expanduser("~"), ".paddleocr", "whl", "det", "en", "en_PP-OCRv3_det_infer")
    args.det_model_dir = default_det_path 
    args.det_algorithm = 'DB'

    
    
    
    

    # Global Settings
    args.use_gpu = False
    args.det_limit_side_len = 15000
    args.det_db_thresh = 0.3
    args.det_db_box_thresh = 0.5
   
    det_engine_korean = TextDetector(args)
        
    # English
    args.det_db_thresh = 0.2
    args.det_db_box_thresh = 0.3
    det_engine_english = TextDetector(args)

    # args.rec_model_dir = os.path.join(base_path, "crnn_inference")
    args.rec_model_dir = os.path.join(base_path, "crnn_korean_h_inference")
    args.rec_char_dict_path = os.path.join(base_path, "korean_dict.txt")
    args.rec_algorithm = "CRNN"
    args.rec_image_shape = "3, 48, 320"
    args.limited_max_width = 320
    args.rec_batch_num = 1
    args.limited_type = "max"
    args.use_space_char = True 
    rec_engine_korean = TextRecognizer(args)

    args.rec_model_dir = os.path.join(base_path, "crnn_inference")
    args.rec_char_dict_path = os.path.join(base_path, "en_dict.txt")
    args.rec_algorithm = "CRNN"
    args.rec_image_shape = "3, 32, 320"
    rec_engine_english = TextRecognizer(args)

    return ocr_korean, ocr_english, det_engine_korean, det_engine_english, rec_engine_korean, rec_engine_english

ocr_korean, ocr_english, det_engine_korean, det_engine_english, rec_engine_korean, rec_engine_english = init_ocr_system()


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
    lang_codes = {
        'Korean': 'ko',
        'English': 'en',
        'Chinese': 'zh-CN'
    }

    source_code = lang_codes.get(source_lang, 'en')
    target_code = lang_codes.get(target_lang, 'en')

    return _translators.get((source_code, target_code))

def group_nearby_boxes(results, distance_threshold=100, translator='llm', target_lang='English', source_lang='Korean'):
    """Group text boxes that are close together vertically"""
   
    if not results:
        return []
    
    sorted_results = sorted(results, key=lambda r:min(point[1] for point in r['bbox']))

    grouped = []
    current_group = [sorted_results[0]]

    for i in range(1, len(sorted_results)):
        prev_box = current_group[-1]['bbox']
        curr_box = sorted_results[i]['bbox']

        prev_y = sum(point[1] for point in prev_box) / 4
        curr_y = sum(point[1] for point in curr_box)/4

        if abs(curr_y - prev_y) < distance_threshold:
            current_group.append(sorted_results[i])
        else:
            grouped.append(current_group)
            current_group = [sorted_results[i]]

    grouped.append(current_group)


    combined = []

    for group in grouped:
        combined_text = ' '.join(item['original'] for item in group)
        combined_bbox = group[0]['bbox']
        if translator == 'google':
            gt = get_translator(source_lang, target_lang)

            if gt: 
                translated_text = gt.translate(combined_text)
            else:
                translated_text = combined_text

            # if source_lang == 'English':
            #     translated_text = _google_translator_en_from_en.translate(combined_text)
            # elif target_lang == 'Chinese':
            #     translated_text = _google_translator_zh.translate(combined_text)
            # else:
            #     translated_text = _google_translator_en.translate(combined_text)
        else:
            translated_text = translate_with_llm(combined_text, source_lang=source_lang, target_lang=target_lang)
        combined.append({
            'bbox': combined_bbox,
            'original': combined_text, 
            'translated': translated_text, 
            'confidence': max(item['confidence'] for item in group)
        })
    
    return combined

class TranslateRequest(BaseModel):
    image: str
    translator: str = 'llm'
    target_lang: str = 'English'
    source_lang: str = 'Korean' 

@app.post("/translate")
async def translate(request: TranslateRequest):
    try:
        print("===================DEBUGING=================")
        print(f"Source: {request.source_lang} to Target: {request.target_lang}")
        print(f"Translator: {request.translator}")

        decoded_bytes = base64.b64decode(request.image)
        imagePIL = Image.open(io.BytesIO(decoded_bytes)).convert('RGB')
        
        img = cv2.cvtColor(np.array(imagePIL), cv2.COLOR_RGB2BGR)

        ocr = ocr_korean if request.source_lang == 'Korean' else ocr_english
        result = ocr.ocr(img, cls=False)
        # Detect boxes
        # det_engine = det_engine_korean if request.source_lang == 'Korean' else det_engine_english
        # rec_engine = rec_engine_korean if request.source_lang == 'Korean' else rec_engine_english

        # dt_boxes, _ = det_engine(img) 
        # print(f"Detected {len(dt_boxes) if dt_boxes is not None else 0} text boxes")
        final_results = []

        if result and result[0]:
            for line in result[0]:
                box = line[0]
                text, score = line[1]
                print(f"Prediction: {text} | Score: {score:.4f}")
                final_results.append({
                    'bbox': box,
                    'original': text,
                    'confidence': float(score)
                })
        print(f"\n=== Grouping {len(final_results)} boxes ===")
        final_results = group_nearby_boxes(
            final_results, 
            translator=request.translator, 
            target_lang=request.target_lang, 
            source_lang=request.source_lang
        )
        print(f"Grouped into {len(final_results)} blocks\n")

        # if dt_boxes is not None and len(dt_boxes) > 0:
        #     for box in dt_boxes:
        #         pts = np.array(box, dtype=np.float32)
        #         x1, y1 = pts.min(axis=0).astype(int)
        #         x2, y2 = pts.max(axis=0).astype(int)
                
        #         p = 3
        #         x1, y1 = max(0, x1-p), max(0, y1-p)
        #         x2, y2 = min(img.shape[1], x2+p), min(img.shape[0], y2+p)
                
        #         crop = img[y1:y2, x1:x2]
        #         if crop.size == 0: continue
  
        #         # rec_engine = rec_engine_korean if request.source_lang == 'Korean' else rec_engine_english
        #         rec_res, _ = rec_engine([crop])

        #         if rec_res and len(rec_res) > 0:
        #             text, score = rec_res[0]
        #             print(f"Prediction: {text} | Score: {score:.4f}")
        #             final_results.append({
        #                 'bbox': box.tolist(),
        #                 'original': text,
        #                 'confidence': float(score)
        #             })
        
        # final_results = group_nearby_boxes(final_results, translator=request.translator, target_lang=request.target_lang, source_lang=request.source_lang)
        return {"results": final_results}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}, 500


def translate_with_llm(text, source_lang='Korean', target_lang='English'):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        stream=False,
        messages=[
            {"role": "system", "content": "You are a translator. Only output the translation, nothing else. If no text is provided please output nothing."},
            {"role": "user", "content": f"Translate this {source_lang} comic dialogue to {target_lang}: {text}\n\nTranslation:"}
        ]
    )
    return response.choices[0].message.content 