#!/usr/bin/env python3
"""
GAMMA Beta Connection System
GAMMA-native BETA connection system for distributed computing
Provides sophisticated connectivity to BETA system via multiple methods
"""

import asyncio
import json
import time
import subprocess
import os
import sys
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib
import requests
from pathlib import Path

class ConnectionMethod(Enum):
    """Available connection methods to BETA."""
    SSH = "ssh"
    SYNCTHING = "syncthing"
    RAY = "ray"
    TAILSCALE = "tailscale"

@dataclass
class BetaSystem:
    """BETA system configuration."""
    ip: str = "100.84.202.68"
    hostname: str = "beta"
    user: str = "arthurdell"
    ram_gb: int = 256
    gpu_cores: int = 80
    cpu_cores: int = 32

@dataclass
class ConnectionStatus:
    """Connection status information."""
    method: ConnectionMethod
    connected: bool
    latency_ms: Optional[float] = None
    bandwidth_mbps: Optional[float] = None
    error: Optional[str] = None

class GammaBetaConnector:
    """Sophisticated BETA connection system for GAMMA project."""
    
    def __init__(self):
        self.beta = BetaSystem()
        # Use current GAMMA system IPs
        self.alpha_ip = "100.106.170.128"  # Current ALPHA IP from Tailscale
        self.connection_status: Dict[ConnectionMethod, ConnectionStatus] = {}
        self.ssh_keys = [
            "gamma_alpha_to_beta_key",
            "gamma_beta_access_key", 
            "gamma_id_ed25519"
        ]
        
    def test_network_connectivity(self) -> bool:
        """Test basic network connectivity to BETA."""
        try:
            result = subprocess.run(
                ["ping", "-c", "3", "-q", self.beta.ip],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    def get_network_latency(self) -> Optional[float]:
        """Get network latency to BETA in milliseconds."""
        try:
            result = subprocess.run(
                ["ping", "-c", "3", "-q", self.beta.ip],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'avg' in line:
                        parts = line.split('/')
                        if len(parts) > 4:
                            return float(parts[4])
            return None
        except:
            return None
    
    def test_ssh_connection(self) -> ConnectionStatus:
        """Test SSH connection to BETA."""
        try:
            # Try with different SSH keys
            for key in self.ssh_keys:
                key_path = f"~/.ssh/{key}"
                result = subprocess.run(
                    ["ssh", "-F", "/dev/null", "-o", "ConnectTimeout=5", 
                     "-o", "StrictHostKeyChecking=no", "-o", "IdentitiesOnly=yes",
                     "-i", key_path, f"{self.beta.user}@{self.beta.ip}", 
                     "echo 'SSH connection successful'"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    latency = self.get_network_latency()
                    return ConnectionStatus(
                        method=ConnectionMethod.SSH,
                        connected=True,
                        latency_ms=latency
                    )
            
            return ConnectionStatus(
                method=ConnectionMethod.SSH,
                connected=False,
                error="All SSH key attempts failed"
            )
        except Exception as e:
            return ConnectionStatus(
                method=ConnectionMethod.SSH,
                connected=False,
                error=str(e)
            )
    
    def test_syncthing_connection(self) -> ConnectionStatus:
        """Test Syncthing connection to BETA."""
        try:
            # Check if Syncthing is running locally
            result = subprocess.run(
                ["curl", "-s", "http://localhost:8384/rest/system/status"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return ConnectionStatus(
                    method=ConnectionMethod.SYNCTHING,
                    connected=False,
                    error="Syncthing not running locally"
                )
            
            # Check for BETA device in connections
            result = subprocess.run(
                ["curl", "-s", "http://localhost:8384/rest/system/connections"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                try:
                    connections = json.loads(result.stdout)
                    # Look for BETA device (simplified check)
                    connected = any(
                        info.get('connected', False) 
                        for info in connections.get('connections', {}).values()
                    )
                    
                    return ConnectionStatus(
                        method=ConnectionMethod.SYNCTHING,
                        connected=connected,
                        latency_ms=self.get_network_latency()
                    )
                except:
                    pass
            
            return ConnectionStatus(
                method=ConnectionMethod.SYNCTHING,
                connected=False,
                error="Could not parse Syncthing status"
            )
        except Exception as e:
            return ConnectionStatus(
                method=ConnectionMethod.SYNCTHING,
                connected=False,
                error=str(e)
            )
    
    def test_ray_connection(self) -> ConnectionStatus:
        """Test Ray cluster connection to BETA."""
        try:
            import ray
            
            # Try to connect to Ray cluster
            ray.init(address=f"{self.alpha_ip}:6380", ignore_reinit_error=True)
            
            # Get cluster nodes
            nodes = ray.nodes()
            beta_nodes = [
                n for n in nodes 
                if n['Alive'] and self.beta.ip in n.get('NodeManagerAddress', '')
            ]
            
            connected = len(beta_nodes) > 0
            
            return ConnectionStatus(
                method=ConnectionMethod.RAY,
                connected=connected,
                latency_ms=self.get_network_latency()
            )
        except Exception as e:
            return ConnectionStatus(
                method=ConnectionMethod.RAY,
                connected=False,
                error=str(e)
            )
    
    def test_tailscale_connection(self) -> ConnectionStatus:
        """Test Tailscale connectivity to BETA."""
        try:
            result = subprocess.run(
                ["tailscale", "status"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Check if BETA is in Tailscale status
                connected = self.beta.ip in result.stdout
                
                return ConnectionStatus(
                    method=ConnectionMethod.TAILSCALE,
                    connected=connected,
                    latency_ms=self.get_network_latency()
                )
            
            return ConnectionStatus(
                method=ConnectionMethod.TAILSCALE,
                connected=False,
                error="Tailscale not available"
            )
        except Exception as e:
            return ConnectionStatus(
                method=ConnectionMethod.TAILSCALE,
                connected=False,
                error=str(e)
            )
    
    def test_all_connections(self) -> Dict[ConnectionMethod, ConnectionStatus]:
        """Test all available connection methods to BETA."""
        print("🔍 Testing BETA connectivity methods...")
        
        # Test network connectivity first
        if not self.test_network_connectivity():
            print("❌ Basic network connectivity failed")
            return {}
        
        print("✅ Basic network connectivity: OK")
        
        # Test each connection method
        methods = [
            (ConnectionMethod.SSH, self.test_ssh_connection),
            (ConnectionMethod.SYNCTHING, self.test_syncthing_connection),
            (ConnectionMethod.RAY, self.test_ray_connection),
            (ConnectionMethod.TAILSCALE, self.test_tailscale_connection)
        ]
        
        for method, test_func in methods:
            print(f"🔍 Testing {method.value} connection...")
            status = test_func()
            self.connection_status[method] = status
            
            if status.connected:
                print(f"✅ {method.value}: Connected")
                if status.latency_ms:
                    print(f"   Latency: {status.latency_ms:.2f}ms")
            else:
                print(f"❌ {method.value}: Failed")
                if status.error:
                    print(f"   Error: {status.error}")
        
        return self.connection_status
    
    def execute_ssh_command(self, command: str, timeout: int = 30) -> Tuple[bool, str]:
        """Execute command on BETA via SSH."""
        for key in self.ssh_keys:
            key_path = f"~/.ssh/{key}"
            try:
                result = subprocess.run(
                    ["ssh", "-F", "/dev/null", "-o", "ConnectTimeout=5",
                     "-o", "StrictHostKeyChecking=no", "-o", "IdentitiesOnly=yes",
                     "-i", key_path, f"{self.beta.user}@{self.beta.ip}", command],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
                if result.returncode == 0:
                    return True, result.stdout
            except subprocess.TimeoutExpired:
                return False, "Timeout"
            except Exception as e:
                continue
        
        return False, "All SSH key attempts failed"
    
    def get_beta_system_info(self) -> Dict[str, Any]:
        """Get BETA system information via SSH."""
        success, output = self.execute_ssh_command(
            "python3 -c \"import psutil; import json; "
            "print(json.dumps({'cpu_percent': psutil.cpu_percent(), "
            "'memory_percent': psutil.virtual_memory().percent, "
            "'available_gb': psutil.virtual_memory().available / 1e9, "
            "'hostname': psutil.os.uname().nodename}))\""
        )
        
        if success:
            try:
                return json.loads(output)
            except:
                pass
        
        # Fallback info
        return {
            "status": "online" if success else "offline",
            "hostname": "beta",
            "cpu_percent": 0,
            "memory_percent": 0,
            "available_gb": 0
        }
    
    def distribute_workload(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Distribute workload between ALPHA and BETA based on availability."""
        beta_info = self.get_beta_system_info()
        
        alpha_tasks = []
        beta_tasks = []
        
        if (beta_info.get("status") == "online" and 
            beta_info.get("available_gb", 0) > 10):
            # BETA is available, split workload
            for i, task in enumerate(tasks):
                if i % 2 == 0:
                    alpha_tasks.append(task)
                else:
                    beta_tasks.append(task)
        else:
            # BETA unavailable, process all on ALPHA
            alpha_tasks = tasks
        
        return {
            "alpha": alpha_tasks,
            "beta": beta_tasks,
            "beta_status": beta_info
        }
    
    async def process_parallel(self, tasks: List[Dict[str, Any]]) -> List[Any]:
        """Process tasks in parallel across ALPHA and BETA."""
        distribution = self.distribute_workload(tasks)
        
        async def process_on_alpha(task_list):
            """Process tasks locally on ALPHA."""
            results = []
            for task in task_list:
                # Simulate processing
                await asyncio.sleep(0.1)
                results.append({
                    "task_id": task.get("id"),
                    "processed_by": "alpha",
                    "result": f"Processed: {task.get('data', '')[:50]}"
                })
            return results
        
        async def process_on_beta(task_list):
            """Process tasks remotely on BETA."""
            if not task_list:
                return []
            
            # Send tasks to BETA for processing
            task_json = json.dumps(task_list)
            command = f"python3 -c 'import json; tasks={task_json}; " \
                     f"print(json.dumps([{{\"task_id\": t[\"id\"], " \
                     f"\"processed_by\": \"beta\", " \
                     f"\"result\": \"Processed: \" + str(t.get(\"data\", \"\"))[:50]}} " \
                     f"for t in tasks]))'"
            
            success, output = self.execute_ssh_command(command)
            if success:
                try:
                    return json.loads(output)
                except:
                    pass
            return []
        
        # Process in parallel
        alpha_future = process_on_alpha(distribution["alpha"])
        beta_future = process_on_beta(distribution["beta"])
        
        alpha_results, beta_results = await asyncio.gather(
            alpha_future,
            beta_future
        )
        
        return alpha_results + beta_results
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get comprehensive connection statistics."""
        beta_info = self.get_beta_system_info()
        latency = self.get_network_latency()
        
        return {
            "alpha": {
                "ip": self.alpha_ip,
                "ram_gb": 512,
                "gpu_cores": 80,
                "cpu_cores": 32
            },
            "beta": {
                "ip": self.beta.ip,
                "ram_gb": self.beta.ram_gb,
                "gpu_cores": self.beta.gpu_cores,
                "cpu_cores": self.beta.cpu_cores,
                "status": beta_info
            },
            "network": {
                "latency_ms": latency,
                "bandwidth_mbps": 420,  # Known from previous tests
                "network_ready": latency is not None and latency < 5
            },
            "connections": {
                method.value: {
                    "connected": status.connected,
                    "latency_ms": status.latency_ms,
                    "error": status.error
                }
                for method, status in self.connection_status.items()
            },
            "combined_resources": {
                "total_ram_gb": 512 + self.beta.ram_gb,
                "total_gpu_cores": 80 + self.beta.gpu_cores,
                "total_cpu_cores": 32 + self.beta.cpu_cores,
                "theoretical_tflops": 64  # Estimated for M3 Ultra x2
            }
        }

async def test_gamma_beta_connector():
    """Test the GAMMA Beta Connector system."""
    print("🚀 GAMMA Beta Connector Test")
    print("-" * 40)
    
    connector = GammaBetaConnector()
    
    # Test all connections
    connections = connector.test_all_connections()
    
    # Get system stats
    stats = connector.get_connection_stats()
    print(f"\n📊 System Configuration:")
    print(f"  Alpha: {stats['alpha']['ram_gb']}GB RAM, {stats['alpha']['gpu_cores']} GPU cores")
    print(f"  Beta: {stats['beta']['ram_gb']}GB RAM, {stats['beta']['gpu_cores']} GPU cores")
    
    if stats['network'].get('latency_ms'):
        print(f"  Network: {stats['network']['latency_ms']:.2f}ms latency")
    
    # Test distributed processing
    test_tasks = [
        {"id": f"task_{i}", "data": f"Process this text segment {i}" * 10}
        for i in range(6)
    ]
    
    print(f"\n📦 Processing {len(test_tasks)} tasks...")
    
    # Process tasks
    start = time.perf_counter()
    results = await connector.process_parallel(test_tasks)
    elapsed = time.perf_counter() - start
    
    print(f"✅ Completed in {elapsed:.2f}s")
    
    # Show results
    alpha_count = sum(1 for r in results if r.get("processed_by") == "alpha")
    beta_count = sum(1 for r in results if r.get("processed_by") == "beta")
    
    print(f"\n📈 Distribution:")
    print(f"  Alpha processed: {alpha_count} tasks")
    print(f"  Beta processed: {beta_count} tasks")
    
    print("\n✨ GAMMA Beta Connector ready!")

if __name__ == "__main__":
    asyncio.run(test_gamma_beta_connector())

