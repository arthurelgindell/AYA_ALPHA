#!/usr/bin/env python3
"""
LM Studio MCP Server
Provides LM Studio connectivity via MCP protocol
"""

import json
import sys
import requests
from pathlib import Path

# Add Agent Turbo to path
import os
AYA_ROOT = '/Volumes/DATA/AYA' if os.path.exists('/Volumes/DATA/AYA') else '/Users/arthurdell/AYA'
sys.path.insert(0, os.path.join(AYA_ROOT, 'Agent_Turbo'))

from core.lm_studio_client import LMStudioClient

class LMStudioMCPServer:
    """MCP Server for LM Studio integration."""
    
    def __init__(self):
        self.lm_client = LMStudioClient()
        self.tools = {
            "lm_studio_status": self.get_status,
            "lm_studio_models": self.get_models,
            "lm_studio_generate": self.generate_text,
            "lm_studio_embed": self.create_embedding
        }
    
    def get_status(self) -> dict:
        """Get LM Studio status."""
        try:
            response = requests.get("http://localhost:1234/v1/models", timeout=10)
            if response.status_code == 200:
                models = response.json()
                return {
                    "status": "success",
                    "connected": True,
                    "models": len(models.get("data", [])),
                    "model_id": self.lm_client.model_id
                }
            else:
                return {"status": "error", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def get_models(self) -> dict:
        """Get available models."""
        try:
            response = requests.get("http://localhost:1234/v1/models", timeout=10)
            if response.status_code == 200:
                models = response.json()
                return {"status": "success", "models": models}
            else:
                return {"status": "error", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def generate_text(self, prompt: str, max_tokens: int = 100) -> dict:
        """Generate text using LM Studio."""
        try:
            result = self.lm_client.generate_text(prompt, max_tokens=max_tokens)
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def create_embedding(self, text: str) -> dict:
        """Create embedding using existing embedding service on port 8765."""
        try:
            import requests
            response = requests.post(
                "http://localhost:8765/embed",
                json={"text": text},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success",
                    "embedding": data['embedding']
                }
            else:
                return {"status": "error", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def handle_request(self, request: dict) -> dict:
        """Handle MCP request."""
        try:
            method = request.get("method")
            params = request.get("params", {})
            
            if method in self.tools:
                return self.tools[method](**params)
            else:
                return {"status": "error", "error": f"Unknown method: {method}"}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def run(self):
        """Run MCP server."""
        try:
            while True:
                line = sys.stdin.readline()
                if not line:
                    break
                
                try:
                    request = json.loads(line.strip())
                    response = self.handle_request(request)
                    print(json.dumps(response))
                    sys.stdout.flush()
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    error_response = {"status": "error", "error": str(e)}
                    print(json.dumps(error_response))
                    sys.stdout.flush()
                    
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    server = LMStudioMCPServer()
    server.run()
