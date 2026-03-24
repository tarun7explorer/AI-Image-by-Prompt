# AI Prompt Refiner for Image Generation

Live Link -[https://huggingface.co/spaces/tarun2525tej/AI-Image-generation]

## Overview

This project is a lightweight AI system that improves user prompts and generates high-quality images using diffusion models.

Users often give very short prompts like:

"dragon"

Such prompts produce poor quality images.

This system automatically expands the prompt into a cinematic, detailed description and then generates an AI image.

The goal of the project is to demonstrate:

- Prompt Engineering
- Diffusion Model Integration
- AI Backend API Development
- FastAPI Deployment
- HuggingFace Inference Usage
- Frontend + Backend Integration

---

## How It Works

1. User enters a simple prompt
2. System refines the prompt into a detailed cinematic description
3. Refined prompt is sent to a diffusion model via HuggingFace API
4. AI image is generated
5. Image is displayed and can be downloaded

## Tech Stack

- Python
- FastAPI
- HuggingFace Inference API
- Stable Diffusion / FLUX
- Vanilla JavaScript
- HTML / CSS

## Features

- Automatic prompt refinement
- Cinematic prompt expansion
- High quality AI image generation
- Clean UI
- Image download support
- Lightweight architecture
- Easy deployment on HuggingFace Spaces

## To Run Locally

Install dependencies:
pip install -r requirements.txt

Run server:
uvicorn main:app --reload

Open browser & Test:
http://127.0.0.1:8000
