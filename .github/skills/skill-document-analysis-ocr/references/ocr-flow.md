# OCR Processing Flow

```python
import asyncio
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import pdf2image

async def extract_text_from_pdf(pdf_path: str, lang: str = 'spa') -> str:
    """Extract text from PDF using OCR."""
    
    # Convert PDF pages to images
    images = convert_from_path(pdf_path)
    
    all_text = []
    for page_num, image in enumerate(images):
        # OCR with Spanish language
        text = pytesseract.image_to_string(image, lang=lang)
        all_text.append(f"--- Página {page_num + 1} ---\n{text}")
    
    return "\n".join(all_text)

async def extract_text_from_image(image_path: str) -> str:
    """Extract text from image file."""
    return pytesseract.image_to_string(Image.open(image_path), lang='spa')

async def extract_metadata_from_ocr(
    ocr_text: str,
    document_type: str,
    ollama_client
) -> dict:
    """Use Ollama to extract structured metadata."""
    
    prompt = f"""
    Analiza este documento OCR y extrae en JSON:
    - solicitante
    - monto (si aplica)
    - fecha
    - tipo_tramite
    - articulos_clave
    
    Documento:
    {ocr_text[:2000]}
    """
    
    response = await ollama_client.generate_json(prompt)
    return response or {}

async def validate_ocr_quality(text: str) -> dict:
    """Assess OCR quality."""
    
    metrics = {
        "length": len(text),
        "has_numbers": any(c.isdigit() for c in text),
        "has_spanish": any(c in "ñáéíóú" for c in text),
        "confidence": min(1.0, len(text) / 500),  # Rough estimate
    }
    
    return metrics
```
