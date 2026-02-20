---
name: skill-document-analysis-ocr
description: Implement OCR and intelligent document analysis using pytesseract, pdf2image, and Ollama. Includes text extraction from PDFs/images, metadata extraction via LLM, quality validation, and error handling. Use when building document processing pipelines that extract structured data from unstructured sources.
---

# Document Analysis & OCR

## Quick Start

```python
from app.services.ocr_service import OCRService

ocr = OCRService()

# Extract text from PDF
text = await ocr.extract_text_from_pdf("documento.pdf")

# Extract metadata via AI
metadata = await ocr.extract_metadata(text, documento_type="factura")
# Returns: {solicitante, monto, fecha, articulos, ...}

# Validate quality
quality = ocr.assess_quality(text)
if quality.confidence < 0.7:
    print("Low OCR confidence, manual review recommended")
```

## Architecture

See [references/ocr-flow.md](references/ocr-flow.md):
- PDF → Images (pdf2image)
- Images → Text (pytesseract)
- Text → Structured (Ollama + JSON parsing)

See [references/quality-checks.md](references/quality-checks.md):
- Confidence scoring
- Fallback to manual review
- Re-OCR with different settings

See [references/metadata-extraction.md](references/metadata-extraction.md):
- Prompt templates for different document types
- Pydantic validation
- Error handling (malformed JSON, empty text)
