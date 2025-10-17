#!/usr/bin/env python3
"""
MCP Server for AGENT_TURBO
Provides external tool connectivity via MCP protocol
"""

import json
import sys
import os
from pathlib import Path

# Add Agent Turbo to path
sys.path.insert(0, '/Volumes/DATA/Agent_Turbo')

from core.agent_turbo import AgentTurbo

class AgentTurboMCPServer:
    """MCP Server for Agent Turbo integration."""
    
    def __init__(self):
        self.agent_turbo = AgentTurbo()
        self.tools = {
            "agent_turbo_query": self.query_agent_turbo,
            "agent_turbo_stats": self.get_agent_turbo_stats,
            "agent_turbo_verify": self.verify_agent_turbo,
            "gpu_status": self.get_gpu_status,
            "cache_status": self.get_cache_status
        }
    
    def query_agent_turbo(self, query: str) -> dict:
        """Query Agent Turbo system."""
        try:
            result = self.agent_turbo.query(query)
            return {
                "status": "success",
                "result": result,
                "tokens_saved": self.agent_turbo.stats().get("total_tokens_saved", 0)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def get_agent_turbo_stats(self) -> dict:
        """Get Agent Turbo statistics."""
        try:
            stats = self.agent_turbo.stats()
            return {"status": "success", "stats": stats}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def verify_agent_turbo(self) -> dict:
        """Verify Agent Turbo system."""
        try:
            # Run verification
            result = subprocess.run([
                "python3", "/Volumes/DATA/Agent_Turbo/core/agent_turbo.py", "verify"
            ], capture_output=True, text=True, timeout=30)
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "output": result.stdout,
                "error": result.stderr
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def get_gpu_status(self) -> dict:
        """Get GPU status."""
        try:
            import mlx.core as mx
            gpu_info = {
                "available": mx.metal.is_available(),
                "device": str(mx.default_device()),
                "memory": mx.metal.device_info()
            }
            return {"status": "success", "gpu": gpu_info}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def get_cache_status(self) -> dict:
        """Get cache status."""
        try:
            cache_dir = Path("/Volumes/DATA/Agent_RAM/cache")
            if cache_dir.exists():
                cache_files = list(cache_dir.glob("*"))
                return {
                    "status": "success",
                    "cache_dir": str(cache_dir),
                    "files": len(cache_files),
                    "size_mb": sum(f.stat().st_size for f in cache_files) / (1024 * 1024)
                }
            else:
                return {"status": "success", "cache_dir": "not_found"}
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
    server = AgentTurboMCPServer()
    server.run()
