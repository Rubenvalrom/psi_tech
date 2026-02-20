import requests
import json
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")

class OllamaService:
    """Handles interaction with local LLM via Ollama."""

    def __init__(self, host: str = OLLAMA_HOST, model: str = OLLAMA_MODEL):
        self.host = host
        self.model = model

    def analyze_document_text(self, text: str) -> Dict[str, Any]:
        """
        Sends document text to Ollama to extract structured metadata.
        """
        prompt = f"""
        Analiza el siguiente texto de un documento administrativo y extrae la información en formato JSON.
        Busca los siguientes campos:
        - tipo_documento (ej: Factura, Informe, Solicitud, Resolución)
        - fecha (en formato YYYY-MM-DD si es posible)
        - emisor (persona o entidad que envía)
        - receptor (persona o entidad que recibe)
        - monto (si es una factura o documento económico, solo el número)
        - resumen (un resumen de 1 frase del contenido)

        Texto del documento:
        ---
        {text[:2000]} 
        ---
        Responde EXCLUSIVAMENTE con el objeto JSON válido.
        """

        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=60
            )
            
            if response.status_code != 200:
                logger.error(f"Ollama error: {response.status_code} - {response.text}")
                return {}

            result = response.json()
            response_text = result.get("response", "{}")
            
            # Parse the JSON string from LLM response
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse Ollama JSON response: {response_text}")
                return {"raw_response": response_text}

        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            return {"error": str(e)}

    def check_health(self) -> bool:
        """Verifies if Ollama is reachable."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def generate_embedding(self, text: str) -> Optional[list]:
        """
        Generates a vector embedding for the given text.
        """
        try:
            response = requests.post(
                f"{self.host}/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text
                },
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Ollama embedding error: {response.status_code} - {response.text}")
                return None

            result = response.json()
            return result.get("embedding")

        except Exception as e:
            logger.error(f"Error calling Ollama embeddings: {e}")
            return None
