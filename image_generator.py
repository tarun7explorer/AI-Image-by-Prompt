"""
image_generator.py — Generates an image via HuggingFace's router using
the text-to-image task endpoint.

Updated for the new router.huggingface.co API (2026).
Uses FLUX.1-dev via black-forest-labs provider — best free quality on HF.
Falls back to stabilityai/sdxl if needed.
"""

import os
import io
import time
import logging
import requests
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

HF_API_TOKEN: str | None = os.getenv("HUGGINGFACE_API_KEY")

# New router URL format for image generation tasks
IMAGE_MODEL = "black-forest-labs/FLUX.1-schnell"
HF_IMAGE_URL = f"https://router.huggingface.co/hf-inference/models/{IMAGE_MODEL}"

# Fallback model if primary fails
FALLBACK_MODEL   = "stabilityai/stable-diffusion-xl-base-1.0"
FALLBACK_IMAGE_URL = f"https://router.huggingface.co/hf-inference/models/{FALLBACK_MODEL}"

REQUEST_TIMEOUT_SECONDS = 120
MAX_RETRIES      = 3
RETRY_BACKOFF    = 8

OUTPUT_FORMAT    = "JPEG"
OUTPUT_QUALITY   = 90
MAX_DIMENSION    = 1024


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_jpeg(raw_bytes: bytes) -> bytes:
    """Decode raw bytes → PIL Image → JPEG bytes."""
    try:
        img = Image.open(io.BytesIO(raw_bytes))
    except Exception as exc:
        raise ValueError(f"Response is not a valid image: {exc}") from exc

    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    if max(img.size) > MAX_DIMENSION:
        img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)
        logger.info("Resized to %s", img.size)

    buf = io.BytesIO()
    img.save(buf, format=OUTPUT_FORMAT, quality=OUTPUT_QUALITY, optimize=True)
    return buf.getvalue()


def _post_image(url: str, prompt: str, headers: dict) -> bytes:
    """
    POST to a HF image generation endpoint and return JPEG bytes.
    Handles 503 (model loading) and 429 (rate limit) with retries.
    Raises RuntimeError on unrecoverable errors.
    """
    payload = {
        "inputs": prompt,
        "parameters": {
            "num_inference_steps": 4 if "schnell" in url else 30,
            "guidance_scale":      0.0 if "schnell" in url else 7.5,
        },
    }

    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        logger.info("Image gen attempt %d/%d → %s", attempt, MAX_RETRIES, url)
        try:
            resp = requests.post(
                url, headers=headers, json=payload,
                timeout=REQUEST_TIMEOUT_SECONDS
            )

            if resp.status_code == 503:
                try:
                    wait = resp.json().get("estimated_time", RETRY_BACKOFF)
                except Exception:
                    wait = RETRY_BACKOFF
                logger.warning("503 model loading — waiting %.0fs", wait)
                time.sleep(float(wait) + 2)
                continue

            if resp.status_code == 429:
                wait = RETRY_BACKOFF * attempt
                logger.warning("429 rate limit — waiting %ds", wait)
                time.sleep(wait)
                continue

            if resp.status_code == 401:
                raise RuntimeError(
                    "HuggingFace 401 Unauthorized. "
                    "Check your token at https://huggingface.co/settings/tokens"
                )

            if resp.status_code in (404, 410):
                raise RuntimeError(
                    f"Model endpoint returned {resp.status_code}. "
                    f"URL: {url}"
                )

            resp.raise_for_status()

            # Check for JSON error body masquerading as 200
            ct = resp.headers.get("Content-Type", "")
            if "application/json" in ct:
                body = resp.json()
                err = body.get("error", "")
                if err:
                    raise RuntimeError(f"HF error payload: {err}")

            if not resp.content:
                raise ValueError("Empty response body from image API.")

            return _to_jpeg(resp.content)

        except requests.exceptions.Timeout:
            last_error = f"Timeout after {REQUEST_TIMEOUT_SECONDS}s (attempt {attempt})"
            logger.warning(last_error)
        except requests.exceptions.ConnectionError as exc:
            last_error = f"Connection error: {exc}"
            logger.warning(last_error)
        except (ValueError, RuntimeError):
            raise

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_BACKOFF)

    raise RuntimeError(
        f"Image generation failed after {MAX_RETRIES} attempts. "
        f"Last error: {last_error}"
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_image(refined_prompt: str) -> bytes:
    """
    Generate an image from a refined SD prompt.
    Tries FLUX.1-schnell first, falls back to SDXL on failure.

    Returns JPEG bytes.
    """
    if not HF_API_TOKEN:
        raise RuntimeError(
            "HUGGINGFACE_API_KEY is not set. Add it to your .env file."
        )

    if not refined_prompt or not refined_prompt.strip():
        raise ValueError("refined_prompt must not be empty.")

    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type":  "application/json",
        "Accept":        "image/jpeg",
    }

    # Try primary model (FLUX.1-schnell — fast & free)
    try:
        logger.info("Trying primary model: %s", IMAGE_MODEL)
        return _post_image(HF_IMAGE_URL, refined_prompt.strip(), headers)
    except RuntimeError as primary_err:
        logger.warning("Primary model failed (%s) — trying fallback SDXL", primary_err)

    # Fallback to SDXL
    try:
        logger.info("Trying fallback model: %s", FALLBACK_MODEL)
        return _post_image(FALLBACK_IMAGE_URL, refined_prompt.strip(), headers)
    except RuntimeError as fallback_err:
        raise RuntimeError(
            f"Both image models failed.\n"
            f"Primary ({IMAGE_MODEL}): {primary_err}\n"
            f"Fallback ({FALLBACK_MODEL}): {fallback_err}"
        )