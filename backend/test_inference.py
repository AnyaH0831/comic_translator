from paddleocr import PaddleOCR
import os

# Path to exported inference model
rec_model_dir = './output/inference_model'

# Path to validation images and labels
val_img_dir = './training_data/val'  
labels_path = os.path.join(val_img_dir, 'labels.txt')
              
# Load OCR model
ocr = PaddleOCR(text_recognition_model_dir=rec_model_dir, use_textline_orientation=False, lang='en')

# Read a few samples from labels.txt
with open(labels_path, 'r', encoding='utf-8') as f:
    samples = [line.strip().split('\t') for line in f.readlines()[:5]]  # First 5 samples

for img_name, gt_text in samples:
    img_path = os.path.join(val_img_dir, img_name)
    result = ocr.ocr(img_path)
    pred_text = result[0][1][0] if result and result[0] and len(result[0]) > 1 else ''
    print(f"Image: {img_name}")
    print(f"Ground Truth: {gt_text}") 
    print(f"Prediction: {pred_text}")
    print('-'*40)
