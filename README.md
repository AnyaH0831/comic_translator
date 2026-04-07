# README

This is a chrome extension that help you translate your comics while you read! Some common platforms such as Webtoon and Kakao Pages are supported. If there are too many images or tasks happening at the same time, the loading may be slow so please be patient. There's a progress bar at the top of to show you the image upload and translation progress. 

Please install the chrome extension from the link and go to a comic site like Webtoon or Kakao Pages. Click the puzzle icon in the top right and select PanelSync then you will see the bar at the top of the page!

### Currently the supported languages:
Source Languages: English, Korean
Target Languages: English, Chinese

Please be sure to select the correct languages when you translate!

## Tech Stack

### Frontend
- JavaScript
- HTML/CSS

### Backend
- Python
- FastAPI

### Database
- Generated synthetic data using Python (train_ocr.py)

### Model Training
This project used two custom trained OCR inferences where it is able to recognize text from English and Korean. 

- PaddleOCR
- Kaggle (platform for training)

## Current Limitations:
- The current server is very limited so multiple tasks may not be supported. 
- Cannot stop translating during the process


## Logs
Model training failed 3 times
- SVTR: training worked out fine but after connecting to project it does not work
    - Might be too precise or trained incorrectly
- Too less data: If less than 20k the accuracy may be too low

CRNN models works for both English and Korean
 
