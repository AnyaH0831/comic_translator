from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import base64
import io 
from PIL import Image

from paddleocr import PaddleOCR
import numpy as np

app = FastAPI()
ocr = PaddleOCR(use_angle_cls=True, lang='en', drop_score=0.1)

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
    
    print(request.image[:50])

    decoded_bytes = base64.b64decode(request.image) 

    imagePIL = Image.open(io.BytesIO(decoded_bytes))

    imagePIL.save('debug_image.jpg')
    print(f"Saved image: {imagePIL.size}")

    

    img_array = np.array(imagePIL)
    result = ocr.ocr(img_array)

    print("Full OCR result:")
    print(result)
    print(f"Type: {type(result)}")
    if result and len(result) > 0:
        print(f"First element: {result[0]}")


    returnBody = {
        "results": result
    }
    return returnBody

 