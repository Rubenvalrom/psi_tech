#!/usr/bin/env python3
"""
ocr_service.py - OCR document processing and metadata extraction service
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import tempfile

import pytesseract
from pdf2image import convert_from_path
import aiofiles
from PIL import Image
import ollama

logger = logging.getLogger(__name__)


class OCRService:
    """OCR and document processing service"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.client = ollama.Client(host=ollama_url)
    
    async def extract_text_from_pdf(
        self,
        pdf_path: str,
        start_page: int = 1,
        end_page: Optional[int] = None
    ) -> Dict[int, str]:
        """Extract text from PDF pages"""
        
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        try:
            logger.info(f"Converting PDF to images: {pdf_file.name}")
            
            # Convert PDF to images
            images = convert_from_path(
                pdf_path,
                first_page=start_page,
                last_page=end_page
            )
            
            # Extract text from each image
            text_by_page = {}
            for page_num, image in enumerate(images, start=start_page):
                logger.info(f"Extracting text from page {page_num}")
                
                text = pytesseract.image_to_string(
                    image,
                    lang='spa+eng'  # Spanish + English
                )
                text_by_page[page_num] = text.strip()
            
            logger.info(f"Extracted text from {len(images)} pages")
            return text_by_page
        
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    async def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from image using OCR"""
        
        image_file = Path(image_path)
        if not image_file.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        try:
            logger.info(f"Extracting text from image: {image_file.name}")
            
            # Load image
            image = Image.open(image_file)
            
            # Extract text
            text = pytesseract.image_to_string(
                image,
                lang='spa+eng'
            )
            
            return text.strip()
        
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            raise
    
    async def extract_metadata_from_ocr(
        self,
        text: str,
        document_type: str = "general"
    ) -> Dict[str, Any]:
        """Extract structured metadata from OCR text using Ollama"""
        
        prompts = {
            "general": """Extract the following metadata from the text:
- Document type
- Document number/ID
- Date
- Sender
- Recipient
- Subject
- Key amounts (if any)

Text: {text}

Provide response as JSON.""",
            
            "invoice": """Extract invoice data from text:
- Invoice number
- Date
- Supplier name
- Supplier NIF
- Total amount
- Concept
- Payment terms

Text: {text}

Provide response as JSON.""",
            
            "contract": """Extract contract details:
- Contract number
- Parties involved
- Contract date
- Amounts
- Duration
- Main clauses

Text: {text}

Provide response as JSON.""",
        }
        
        prompt = prompts.get(document_type, prompts["general"])
        prompt = prompt.format(text=text[:2000])  # Limit text length
        
        try:
            logger.info(f"Extracting metadata (type: {document_type})")
            
            response = self.client.generate(
                model='mistral',
                prompt=prompt,
                stream=False,
                options={
                    'temperature': 0.3,
                    'top_p': 0.9,
                }
            )
            
            # Parse response (simplified - in production, parse JSON)
            metadata = {
                "extracted_text": text[:500],
                "document_type": document_type,
                "ollama_response": response.get('response', ''),
            }
            
            return metadata
        
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return {"error": str(e), "text": text[:500]}
    
    async def process_document(
        self,
        file_path: str,
        document_type: str = "general"
    ) -> Dict[str, Any]:
        """Process document: convert to text and extract metadata"""
        
        file_path = Path(file_path)
        
        try:
            # Step 1: Extract text
            if file_path.suffix.lower() == '.pdf':
                text_by_page = await self.extract_text_from_pdf(str(file_path))
                full_text = "\n".join(text_by_page.values())
            else:
                full_text = await self.extract_text_from_image(str(file_path))
            
            # Step 2: Extract metadata
            metadata = await self.extract_metadata_from_ocr(
                full_text,
                document_type
            )
            
            # Step 3: Quality assessment
            quality = self._assess_ocr_quality(full_text)
            
            result = {
                "file_name": file_path.name,
                "file_size": file_path.stat().st_size,
                "document_type": document_type,
                "extracted_text": full_text[:1000],
                "text_length": len(full_text),
                "metadata": metadata,
                "quality": quality,
                "processed_at": str(asyncio.get_event_loop().time())
            }
            
            logger.info(f"Document processed: {file_path.name} (quality: {quality['score']}%)")
            return result
        
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            raise
    
    @staticmethod
    def _assess_ocr_quality(text: str) -> Dict[str, Any]:
        """Assess OCR quality"""
        
        if not text:
            return {"score": 0, "assessment": "No text extracted"}
        
        # Simple heuristics
        words = text.split()
        if not words:
            return {"score": 0, "assessment": "No words detected"}
        
        # Check for common OCR errors (special characters)
        error_chars = sum(1 for c in text if ord(c) < 32 and c not in '\n\t\r')
        error_ratio = error_chars / len(text)
        
        if error_ratio > 0.1:
            score = 40
            assessment = "Poor - High error ratio"
        elif error_ratio > 0.05:
            score = 60
            assessment = "Fair - Some errors detected"
        else:
            score = 90
            assessment = "Good - Low error ratio"
        
        return {
            "score": score,
            "assessment": assessment,
            "word_count": len(words),
            "character_count": len(text),
            "error_ratio": f"{error_ratio*100:.2f}%"
        }
    
    async def batch_process_documents(
        self,
        directory: str,
        file_pattern: str = "*.pdf",
        document_type: str = "general"
    ) -> List[Dict[str, Any]]:
        """Process multiple documents in a directory"""
        
        doc_dir = Path(directory)
        if not doc_dir.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        files = list(doc_dir.glob(file_pattern))
        logger.info(f"Found {len(files)} files to process")
        
        results = []
        for file_path in files:
            try:
                result = await self.process_document(str(file_path), document_type)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                results.append({
                    "file_name": file_path.name,
                    "error": str(e)
                })
        
        return results


# Example usage
async def main():
    service = OCRService()
    
    # Process single document
    result = await service.process_document(
        "./sample.pdf",
        document_type="invoice"
    )
    
    print(f"Document: {result['file_name']}")
    print(f"Quality: {result['quality']['score']}%")
    print(f"Extracted: {result['extracted_text'][:200]}...")


if __name__ == "__main__":
    asyncio.run(main())
