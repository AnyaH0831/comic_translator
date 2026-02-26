# Test 1: Check if the model files are correct
import os
print("Model files:", os.listdir('./inference_model'))

# Test 2: Try using PaddleOCR's high-level API instead
from paddleocr import PaddleOCR
ocr_test = PaddleOCR(
    use_angle_cls=False,
    lang='en',
    rec_model_dir='./inference_model',
    rec_char_dict_path='./en_dict.txt',
    use_gpu=False
)

# Test 3: Run OCR on the synthetic HELLO image
result = ocr_test.ocr('test_synthetic.png', cls=False)
print("Result:", result)