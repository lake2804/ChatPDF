"""
Vision module for processing images using Google Gemini Vision API.
Provides OCR and image captioning capabilities.
"""
import base64
import io
from typing import Optional
from google import genai
from google.genai import types
from app.config import GOOGLE_API_KEY, VISION_MODEL
import logging

logger = logging.getLogger(__name__)

# Initialize Google GenAI client
if not GOOGLE_API_KEY:
    logger.warning("GOOGLE_API_KEY is not set. Vision features may not work.")
    client = None
else:
    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
    except Exception as e:
        logger.error(f"Failed to initialize Google GenAI client: {e}")
        client = None


def get_image_mime_type(image_bytes: bytes) -> str:
    """Detect MIME type from image bytes."""
    img = io.BytesIO(image_bytes)
    from PIL import Image
    pil_img = Image.open(img)
    format_map = {
        "PNG": "image/png",
        "JPEG": "image/jpeg",
        "GIF": "image/gif",
        "BMP": "image/bmp",
        "WEBP": "image/webp"
    }
    return format_map.get(pil_img.format, "image/png")


def caption_image_bytes(image_bytes: bytes, detailed: bool = True) -> Optional[str]:
    """
    Use Google Gemini Vision to produce a detailed textual description of the image.
    
    Args:
        image_bytes: Raw image bytes
        detailed: If True, requests detailed description including charts, text, etc.
    
    Returns:
        Caption string or None if error
    """
    if not client:
        logger.error("Google API client is not initialized. Cannot caption image.")
        return None
    
    try:
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        mime_type = get_image_mime_type(image_bytes)
        
        prompt = (
            "Please describe this image in detail, including any text, charts, graphs, "
            "diagrams, tables, or visual elements. Include axis labels, data points, "
            "and any other relevant information that would be useful for understanding the content."
            if detailed
            else "Please provide a brief description of this image."
        )
        
        # Use Part with inlineData (Blob) for image
        image_part = types.Part(
            inline_data=types.Blob(
                mime_type=mime_type,
                data=b64
            )
        )
        text_part = types.Part(text=prompt)
        
        response = client.models.generate_content(
            model=VISION_MODEL,
            contents=[image_part, text_part],
            config={
                "temperature": 0.4,
                "max_output_tokens": 1024
            }
        )
        
        # Handle different response formats from Google API
        try:
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
            elif hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    text_parts = [part.text for part in candidate.content.parts if hasattr(part, 'text')]
                    if text_parts:
                        return ' '.join(text_parts).strip()
            elif isinstance(response, str):
                return response.strip()
        except Exception as e:
            print(f"Error parsing vision response: {e}")
        return None
    except Exception as e:
        print(f"Error captioning image: {e}")
        return None


def ocr_image_bytes(image_bytes: bytes) -> Optional[str]:
    """
    Extract text from image using Gemini Vision (OCR capability).
    
    Args:
        image_bytes: Raw image bytes
    
    Returns:
        Extracted text or None if error
    """
    if not client:
        logger.error("Google API client is not initialized. Cannot perform OCR.")
        return None
    
    try:
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        mime_type = get_image_mime_type(image_bytes)
        
        # Use Part with inlineData (Blob) for image
        image_part = types.Part(
            inline_data=types.Blob(
                mime_type=mime_type,
                data=b64
            )
        )
        text_part = types.Part(
            text="Extract all text from this image. Preserve formatting and structure. "
                 "If there are tables, present them in a structured format."
        )
        
        response = client.models.generate_content(
            model=VISION_MODEL,
            contents=[image_part, text_part],
            config={
                "temperature": 0.1,
                "max_output_tokens": 2048
            }
        )
        
        # Handle different response formats from Google API
        try:
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
            elif hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    text_parts = [part.text for part in candidate.content.parts if hasattr(part, 'text')]
                    if text_parts:
                        return ' '.join(text_parts).strip()
            elif isinstance(response, str):
                return response.strip()
        except Exception as e:
            print(f"Error parsing OCR response: {e}")
        return None
    except Exception as e:
        print(f"Error performing OCR: {e}")
        return None

