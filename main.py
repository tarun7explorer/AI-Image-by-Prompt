import base64
import io
import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image

from image_generator import generate_image
from llm_refiner import refine_prompt
from schemas import RefineRequest, GenerateRequest

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI(title="AI Prompt Refiner Image Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/refine")
async def api_refine(body: RefineRequest):
    try:
        result = refine_prompt(body.basic_prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate")
async def api_generate(body: GenerateRequest):
    try:
        image_bytes = generate_image(body.refined_prompt)
        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        return {
            "image_base64": image_b64,
            "refined_prompt": body.refined_prompt,
            "optimization_report": [
                "Added artistic style keywords",
                "Enhanced lighting and cinematic details",
                "Improved scene composition",
                "Included high-resolution quality boosters"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
