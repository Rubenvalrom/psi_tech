#!/usr/bin/env python3
"""
health_check.py - Validate Olympus Smart Gov deployment health
"""

import asyncio
import httpx
import sys
import json
from datetime import datetime

class DeploymentHealthCheck:
    def __init__(self, backend_url="http://localhost:8000", 
                 keycloak_url="http://localhost:8080",
                 ollama_url="http://localhost:11434",
                 postgres_url="postgresql://user:pass@localhost:5432/olympus"):
        self.backend_url = backend_url
        self.keycloak_url = keycloak_url
        self.ollama_url = ollama_url
        self.postgres_url = postgres_url
        self.results = {}
        self.start_time = datetime.utcnow()
    
    async def check_backend(self):
        """Check FastAPI backend readiness"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.backend_url}/health/ready")
                response.raise_for_status()
                self.results["backend"] = {
                    "status": "healthy",
                    "response": response.json()
                }
        except Exception as e:
            self.results["backend"] = {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def check_keycloak(self):
        """Check Keycloak availability"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                url = f"{self.keycloak_url}/auth/realms/olympus"
                response = await client.get(url)
                response.raise_for_status()
                self.results["keycloak"] = {
                    "status": "healthy",
                    "realm": response.json().get("realm-public-key") is not None
                }
        except Exception as e:
            self.results["keycloak"] = {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def check_ollama(self):
        """Check Ollama LLM service"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.ollama_url}/api/tags")
                response.raise_for_status()
                models = response.json().get("models", [])
                self.results["ollama"] = {
                    "status": "healthy",
                    "models": [m["name"] for m in models]
                }
        except Exception as e:
            self.results["ollama"] = {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def check_postgres(self):
        """Check PostgreSQL connectivity"""
        try:
            import asyncpg
            conn_params = self._parse_postgres_url(self.postgres_url)
            conn = await asyncpg.connect(
                host=conn_params["host"],
                port=conn_params["port"],
                user=conn_params["user"],
                password=conn_params["password"],
                database=conn_params["database"],
                timeout=5
            )
            version = await conn.fetchval("SELECT version()")
            await conn.close()
            
            self.results["postgres"] = {
                "status": "healthy",
                "version": version[:50] + "..." if len(version) > 50 else version
            }
        except Exception as e:
            self.results["postgres"] = {
                "status": "unhealthy",
                "error": str(e)
            }
    
    @staticmethod
    def _parse_postgres_url(url):
        """Parse PostgreSQL connection string"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return {
            "user": parsed.username or "postgres",
            "password": parsed.password or "",
            "host": parsed.hostname or "localhost",
            "port": parsed.port or 5432,
            "database": parsed.path.lstrip("/") or "postgres"
        }
    
    async def run(self):
        """Run all health checks concurrently"""
        print(f"🔍 Starting deployment health checks at {self.start_time.isoformat()}...")
        print(f"   Backend: {self.backend_url}")
        print(f"   Keycloak: {self.keycloak_url}")
        print(f"   Ollama: {self.ollama_url}")
        print()
        
        await asyncio.gather(
            self.check_backend(),
            self.check_keycloak(),
            self.check_ollama(),
            self.check_postgres()
        )
    
    def report(self):
        """Print health check report"""
        healthy_count = sum(1 for r in self.results.values() if r.get("status") == "healthy")
        total_count = len(self.results)
        
        print("=" * 60)
        print(f"HEALTH CHECK RESULTS: {healthy_count}/{total_count} healthy")
        print("=" * 60)
        
        for service, result in self.results.items():
            status_emoji = "✅" if result.get("status") == "healthy" else "❌"
            print(f"\n{status_emoji} {service.upper()}")
            for key, value in result.items():
                if key != "status":
                    print(f"   {key}: {value}")
        
        duration = (datetime.utcnow() - self.start_time).total_seconds()
        print(f"\n⏱️  Check completed in {duration:.2f}s")
        print("=" * 60)
        
        # Return exit code
        return 0 if healthy_count == total_count else 1

async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Check Olympus deployment health")
    parser.add_argument("--backend", default="http://localhost:8000")
    parser.add_argument("--keycloak", default="http://localhost:8080")
    parser.add_argument("--ollama", default="http://localhost:11434")
    parser.add_argument("--postgres", default="postgresql://postgres:postgres@localhost:5432/olympus")
    
    args = parser.parse_args()
    
    checker = DeploymentHealthCheck(
        backend_url=args.backend,
        keycloak_url=args.keycloak,
        ollama_url=args.ollama,
        postgres_url=args.postgres
    )
    
    await checker.run()
    exit_code = checker.report()
    sys.exit(exit_code)

if __name__ == "__main__":
    asyncio.run(main())
