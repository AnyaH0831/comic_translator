from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import base64
import io 
import os
from PIL import Image
import cv2

from paddleocr import PaddleOCR
import numpy as np

app = FastAPI()
# custom_model_path = os.path.abspath('output/custom_model/best_accuracy')

# ocr = PaddleOCR(use_angle_cls=True, lang='en', drop_score=0.1)
# ocr = PaddleOCR(
#     use_angle_cls=True,
#     rec_model_dir='./inference_model',
#     # use_gpu=False
#     lang='en',
#     drop_score=0.1
# )

from paddleocr import PaddleOCR
from paddleocr.tools.infer.predict_rec import TextRecognizer

base_path = os.path.dirname(os.path.abspath(__file__))


from paddleocr.tools.infer import utility
# from paddleocr.tools.infer.predict_rec import TextRecognizer
from paddleocr.tools.infer.predict_det import TextDetector


# def init_ocr_engine():
#     return PaddleOCR(
#         rec_model_dir=os.path.join(base_path, "inference_model"),
#         rec_char_dict_path=os.path.join(base_path, "PaddleOCR/ppocr/utils/en_dict.txt"),
#         rec_algorithm='SVTR_LCNet', 
#         rec_image_shape="3, 48, 320",
#         use_angle_cls=True,
#         det_limit_side_len=15000, 

#         det_db_thresh=0.3,
#         det_db_box_thresh=0.5,
#         det_vertical_text=True, 
#         use_gpu=False,
#         show_log=True,
#         rec_batch_num=1,          
#         limited_max_width=320,
#         limited_type='max'
#     )

# # Initialize the engine
# ocr = init_ocr_engine()

# def init_ocr_system():
#     det_engine = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False, det_limit_side_len=15000, show_log=False)
    
#     parser = utility.init_args()
#     args = parser.parse_args(args=[])
#     args.rec_model_dir = "./inference_model"
#     args.rec_char_dict_path = "PaddleOCR/ppocr/utils/en_dict.txt"
#     args.rec_algorithm = "SVTR"
#     args.rec_image_shape = "3, 48, 320"
#     args.rec_batch_num = 1
#     args.use_gpu = False
    
#     rec_engine = TextRecognizer(args)
#     return det_engine, rec_engine

# det_engine, rec_engine = init_ocr_system()

default_det_path = os.path.join(os.path.expanduser("~"), ".paddleocr", "whl", "det", "en", "en_PP-OCRv3_det_infer")

def init_ocr_system():
   
    parser = utility.init_args()
    args = parser.parse_args(args=[])
    

    args.det_model_dir = default_det_path 
    args.det_algorithm = 'DB'

    # Global Settings
    args.use_gpu = False
    args.det_limit_side_len = 15000
    args.det_db_thresh = 0.3
    args.det_db_box_thresh = 0.5
   
    det_engine = TextDetector(args)
    
    args.rec_model_dir = os.path.join(base_path, "inference_model")
    # args.rec_char_dict_path = "PaddleOCR/ppocr/utils/en_dict.txt
    args.rec_char_dict_path = os.path.join(base_path, "en_dict.txt")
    args.rec_algorithm = "SVTR"
    args.rec_image_shape = "3, 48, 320"
    args.limited_max_width = 320
    args.rec_batch_num = 1
    args.limited_type = "max"
    args.use_space_char = False 
    rec_engine = TextRecognizer(args)
    return det_engine, rec_engine

det_engine, rec_engine = init_ocr_system()




app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class TranslateRequest(BaseModel):
    image: str 




@app.post("/translate")
async def translate(request: TranslateRequest):
    try:
        decoded_bytes = base64.b64decode(request.image)
        imagePIL = Image.open(io.BytesIO(decoded_bytes)).convert('RGB')
        
        img = cv2.cvtColor(np.array(imagePIL), cv2.COLOR_RGB2BGR)

        # Detect boxes
        dt_boxes, _ = det_engine(img)
        
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
                if crop.size == 0: continue

                rec_res, _ = rec_engine([crop])

                if rec_res and len(rec_res) > 0:
                    text, score = rec_res[0]
                    print(f"Prediction: {text} | Score: {score:.4f}")
                    final_results.append([box.tolist(), (text, float(score))])

        return {"results": final_results}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}, 500