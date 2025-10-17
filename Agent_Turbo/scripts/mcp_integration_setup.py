#!/usr/bin/env python3
"""
MCP Integration Setup for AGENT_TURBO
Implements cursor-mcp for external tool connectivity
GAMMA Project - Prime Directives Compliance
"""

import subprocess
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

class MCPIntegrationSetup:
    """MCP integration setup for Cursor."""
    
    def __init__(self):
        self.cursor_extensions_path = Path("/Applications/Cursor.app/Contents/Resources/app/extensions")
        self.mcp_path = self.cursor_extensions_path / "cursor-mcp"
        self.status = {
            "mcp_available": False,
            "mcp_active": False,
            "external_tools": [],
            "connections": []
        }
        
    def verify_mcp_extension(self) -> bool:
        """Verify MCP extension is available."""
        try:
            mcp_exists = self.mcp_path.exists()
            print(f"✅ MCP Extension: {'Available' if mcp_exists else 'Missing'}")
            
            if mcp_exists:
                self.status["mcp_available"] = True
                
            return mcp_exists
        except Exception as e:
            print(f"❌ MCP verification failed: {e}")
            return False
    
    def create_mcp_config(self) -> bool:
        """Create MCP configuration file."""
        try:
            config_content = {
                "mcpServers": {
                    "agent_turbo": {
                        "command": "python3",
                        "args": ["/Volumes/DATA/Agent_Turbo/scripts/mcp_server.py"],
                        "env": {
                            "AGENT_TURBO_PATH": "/Volumes/DATA/Agent_Turbo",
                            "AGENT_TURBO_MODE": "turbo"
                        }
                    },
                    "lm_studio": {
                        "command": "python3",
                        "args": ["/Volumes/DATA/Agent_Turbo/scripts/lm_studio_mcp.py"],
                        "env": {
                            "LM_STUDIO_URL": "http://localhost:1234/v1"
                        }
                    },
                    "gpu_monitor": {
                        "command": "python3",
                        "args": ["/Volumes/DATA/Agent_Turbo/scripts/gpu_monitor_mcp.py"],
                        "env": {
                            "GPU_MONITOR_MODE": "mlx"
                        }
                    }
                }
            }
            
            config_path = Path("/Volumes/DATA/Agent_Turbo/.cursor/mcp_config.json")
            config_path.parent.mkdir(exist_ok=True)
            config_path.write_text(json.dumps(config_content, indent=2))
            
            print("✅ MCP configuration created")
            return True
            
        except Exception as e:
            print(f"❌ MCP config creation failed: {e}")
            return False
    
    def create_mcp_server(self) -> bool:
        """Create MCP server for Agent Turbo."""
        try:
            server_content = '''#!/usr/bin/env python3
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
'''
            
            server_path = Path("/Volumes/DATA/Agent_Turbo/scripts/mcp_server.py")
            server_path.write_text(server_content)
            server_path.chmod(0o755)
            
            print("✅ MCP server created")
            return True
            
        except Exception as e:
            print(f"❌ MCP server creation failed: {e}")
            return False
    
    def create_lm_studio_mcp(self) -> bool:
        """Create LM Studio MCP server."""
        try:
            lm_studio_content = '''#!/usr/bin/env python3
"""
LM Studio MCP Server
Provides LM Studio connectivity via MCP protocol
"""

import json
import sys
import requests
from pathlib import Path

# Add Agent Turbo to path
sys.path.insert(0, '/Volumes/DATA/Agent_Turbo')

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
            result = self.lm_client.generate(prompt, max_tokens=max_tokens)
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def create_embedding(self, text: str) -> dict:
        """Create embedding using LM Studio."""
        try:
            result = self.lm_client.create_embedding(text)
            return {"status": "success", "embedding": result}
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
'''
            
            lm_studio_path = Path("/Volumes/DATA/Agent_Turbo/scripts/lm_studio_mcp.py")
            lm_studio_path.write_text(lm_studio_content)
            lm_studio_path.chmod(0o755)
            
            print("✅ LM Studio MCP server created")
            return True
            
        except Exception as e:
            print(f"❌ LM Studio MCP creation failed: {e}")
            return False
    
    def test_mcp_connection(self) -> bool:
        """Test MCP connection."""
        try:
            # Test Agent Turbo MCP server by importing and testing directly
            import sys
            sys.path.insert(0, '/Volumes/DATA/Agent_Turbo/scripts')
            
            # Test the server class directly
            from mcp_server import AgentTurboMCPServer
            
            server = AgentTurboMCPServer()
            test_request = {
                "method": "agent_turbo_stats",
                "params": {}
            }
            
            response = server.handle_request(test_request)
            
            if response.get("status") == "success":
                print("✅ MCP connection test successful")
                return True
            else:
                print(f"❌ MCP connection test failed: {response.get('error', 'Unknown error')}")
                return False
            
        except Exception as e:
            print(f"❌ MCP test failed: {e}")
            return False
    
    def setup_mcp(self) -> bool:
        """Complete MCP integration setup."""
        print("🚀 Setting up MCP Integration...")
        
        # Verify MCP extension
        if not self.verify_mcp_extension():
            print("❌ TASK FAILED: MCP extension not available")
            return False
        
        # Create MCP configuration
        if not self.create_mcp_config():
            print("❌ TASK FAILED: MCP config creation failed")
            return False
        
        # Create MCP servers
        if not self.create_mcp_server():
            print("❌ TASK FAILED: MCP server creation failed")
            return False
        
        if not self.create_lm_studio_mcp():
            print("❌ TASK FAILED: LM Studio MCP creation failed")
            return False
        
        # Test connection
        if not self.test_mcp_connection():
            print("❌ TASK FAILED: MCP connection test failed")
            return False
        
        print("✅ MCP integration setup complete")
        return True

def main():
    """Main execution."""
    setup = MCPIntegrationSetup()
    success = setup.setup_mcp()
    
    if success:
        print("✅ MCP integration implementation successful")
        return 0
    else:
        print("❌ TASK FAILED: MCP integration setup failed")
        return 1

if __name__ == "__main__":
    exit(main())
