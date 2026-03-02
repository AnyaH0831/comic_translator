import paddle
import numpy as np
import cv2
import os

class CustomSVTROCR:
    def __init__(self, model_path='./inference_model/inference'):
        # 1. Load the inference model
        self.predictor = paddle.jit.load(model_path)
        self.predictor.eval()
        
        # 2. Load the EXACT dictionary from your Kaggle training
        # Ensure en_dict.txt is in the same folder as this script
        if not os.path.exists('./en_dict.txt'):
            raise FileNotFoundError("Place your en_dict.txt in this folder!")
            
        with open('./en_dict.txt', 'r', encoding='utf-8') as f:
            # PaddleOCR uses index 0 for 'Blank'. 
            # We store the characters in a list starting from index 1.
            self.char_dict = [line.strip('\n').strip('\r') for line in f]
    
    def preprocess(self, img):
        # 1. SVTR is VERY sensitive to color. 
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # 2. Resize to 320x48 (Linear is best for SVTR)
        img = cv2.resize(img, (320, 48), interpolation=cv2.INTER_LINEAR)
        
        # 3. CRITICAL: SVTR Normalization (Standard for PaddleOCR)
        # If you skip this, the model predicts E-E-E or D,D,D every time.
        img = img.astype('float32')
        img = (img / 255.0 - 0.5) / 0.5
        
        img = img.transpose(2, 0, 1)
        return paddle.to_tensor(np.expand_dims(img, 0))

    def decode_ctc(self, preds):
        preds_idx = paddle.argmax(preds, axis=2).numpy()[0]
        
        text = []
        prev_idx = -1
        # INDEX 0 IS THE BLANK (BACKGROUND) - DO NOT MAP THIS TO '0'
        blank_idx = 0 
        
        for idx in preds_idx:
            if idx != blank_idx and idx != prev_idx:
                # Model Index 1 -> Your Dict Line 0 ('0')
                # Model Index 21 -> Your Dict Line 20 ('E'?)
                dict_pos = int(idx - 1) 
                if 0 <= dict_pos < len(self.char_dict):
                    text.append(self.char_dict[dict_pos])
            prev_idx = idx
        return "".join(text)

    
    def recognize(self, img_path):
        # Load image (OpenCV loads as BGR)
        img = cv2.imread(img_path)
        if img is None:
            return "Error: Image not found"
            
        # SVTR models are often trained on RGB. If results are gibberish, 
        # uncomment the next line to swap BGR to RGB:
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Run the pipeline
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_tensor = self.preprocess(img)
        with paddle.no_grad():
            preds = self.predictor(img_tensor)
            print("Raw Indices:", paddle.argmax(preds, axis=2).numpy()[0])
            unique_indices = np.unique(paddle.argmax(preds, axis=2).numpy()[0])
            print(f"Unique Predicted Indices: {unique_indices}")
            
        # Decode the mathematical output into text
        result_text = self.decode_ctc(preds)
        return result_text

# --- RUN THE TEST ---
if __name__ == '__main__':
    ocr = CustomSVTROCR()
    
    # Replace 'test_image.png' with your "No Way!" image file name
    image_to_test = 'test_2.png' 
    
    
    if os.path.exists(image_to_test):
        text = ocr.recognize(image_to_test)
        print(f"--- OCR RESULT ---")
        print(f"Recognized: {text}")
        print(f"------------------")
    else:
        print(f"Please put '{image_to_test}' in the folder to test.")