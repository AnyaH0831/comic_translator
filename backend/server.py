from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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

    returnBody = {
        "status": "Received"
    }
    return returnBody

# @app.get("/api/data")
# def get_data():
#     return {"message": "Hello from FastAPI backend!"}       