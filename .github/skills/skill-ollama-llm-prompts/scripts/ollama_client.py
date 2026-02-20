#!/usr/bin/env python3
"""
Ollama client library with reliability patterns.
Usage: python ollama_client.py --model mistral --prompt "What is AI?"
"""

import asyncio
import httpx
import logging
import random
import json
from typing import Optional, Dict
from datetime import datetime, timedelta
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "mistral"
TIMEOUT_SECONDS = 30


class ResponseFormat(Enum):
    TEXT = "text"
    JSON = "json"


class OllamaClient:
    """Client for Ollama with retry logic, timeouts, and graceful degradation."""
    
    def __init__(self, base_url: str = OLLAMA_URL, timeout: int = TIMEOUT_SECONDS):
        self.base_url = base_url
        self.timeout = timeout
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_latency": 0,
        }
    
    async def generate(
        self,
        prompt: str,
        model: str = DEFAULT_MODEL,
        temperature: float = 0.7,
        max_retries: int = 3,
    ) -> Optional[str]:
        """Generate text with automatic retry."""
        
        delay = 1.0
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return await self._call_ollama(prompt, model, temperature)
            except (httpx.TimeoutException, httpx.ConnectError) as e:
                last_exception = e
                
                if attempt < max_retries - 1:
                    jitter = random.uniform(0, 0.1 * delay)
                    wait_time = delay + jitter
                    logger.warning(
                        f"Ollama call failed (attempt {attempt + 1}/{max_retries}). "
                        f"Retrying in {wait_time:.2f}s. Error: {e}"
                    )
                    await asyncio.sleep(wait_time)
                    delay *= 2.0
                else:
                    logger.error(f"Ollama call failed after {max_retries} retries")
        
        raise last_exception
    
    async def _call_ollama(
        self,
        prompt: str,
        model: str,
        temperature: float
    ) -> str:
        """Internal method to call Ollama API."""
        
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "temperature": temperature,
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            
            self.metrics["total_requests"] += 1
            self.metrics["successful_requests"] += 1
            
            return response.json()["response"]
    
    async def generate_with_fallback(
        self,
        prompt: str,
        model: str = DEFAULT_MODEL,
        fallback_response: str = "Unable to generate response. Please try again.",
    ) -> Dict[str, str]:
        """Generate with fallback if Ollama unavailable."""
        
        try:
            response = await self.generate(prompt, model)
            return {
                "response": response,
                "source": "ollama",
                "success": True
            }
        except Exception as e:
            logger.error(f"Using fallback: {e}")
            self.metrics["failed_requests"] += 1
            return {
                "response": fallback_response,
                "source": "fallback",
                "success": False,
                "error": str(e)
            }
    
    async def generate_json(
        self,
        prompt: str,
        model: str = DEFAULT_MODEL,
        schema: Optional[Dict] = None,
    ) -> Optional[Dict]:
        """Generate JSON output with validation."""
        
        json_prompt = f"""{prompt}

Return ONLY valid JSON, no markdown, no explanation:"""
        
        response_text = await self.generate(json_prompt, model)
        
        try:
            # Try to parse as JSON
            data = json.loads(response_text)
            return data
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse extracted JSON: {match.group()}")
                    return None
            else:
                logger.error(f"No JSON found in response: {response_text}")
                return None
    
    def get_metrics(self) -> Dict:
        """Get performance metrics."""
        success_rate = (
            self.metrics["successful_requests"] / self.metrics["total_requests"] * 100
            if self.metrics["total_requests"] > 0
            else 0
        )
        avg_latency = (
            self.metrics["total_latency"] / self.metrics["successful_requests"]
            if self.metrics["successful_requests"] > 0
            else 0
        )
        
        return {
            "total_requests": self.metrics["total_requests"],
            "successful_requests": self.metrics["successful_requests"],
            "failed_requests": self.metrics["failed_requests"],
            "success_rate_percent": f"{success_rate:.1f}",
            "avg_latency_seconds": f"{avg_latency:.2f}",
        }


async def main():
    """CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ollama client CLI")
    parser.add_argument("--prompt", required=True, help="Prompt text")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model name")
    parser.add_argument("--json", action="store_true", help="Parse output as JSON")
    parser.add_argument("--show-metrics", action="store_true", help="Show metrics after")
    
    args = parser.parse_args()
    
    client = OllamaClient()
    
    try:
        if args.json:
            result = await client.generate_json(args.prompt, args.model)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            result = await client.generate(args.prompt, args.model)
            print(result)
        
        if args.show_metrics:
            print("\n=== Metrics ===")
            metrics = client.get_metrics()
            for key, value in metrics.items():
                print(f"{key}: {value}")
    
    except Exception as e:
        logger.error(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
