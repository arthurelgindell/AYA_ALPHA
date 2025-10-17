#!/usr/bin/env python3
"""
GAMMA Monitoring System
GAMMA-native monitoring system for distributed computing
Provides comprehensive monitoring of all GAMMA subsystems
"""

import time
import subprocess
import os
import sys
import json
import psutil
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import asyncio
from pathlib import Path

class SystemStatus(Enum):
    """System status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"

@dataclass
class MonitorResult:
    """Monitoring result."""
    component: str
    status: SystemStatus
    message: str
    metrics: Dict[str, Any]
    timestamp: datetime

class GammaMonitoringSystem:
    """Comprehensive monitoring system for GAMMA project."""
    
    def __init__(self):
        self.monitoring_interval = 5  # seconds
        self.results = []
        # Use current GAMMA system IPs
        self.beta_ip = "100.84.202.68"     # Current BETA IP from Tailscale
        self.alpha_ip = "100.106.170.128"  # Current ALPHA IP from Tailscale
        
        # GAMMA-specific components to monitor
        self.components = {
            "agent_turbo": {
                "name": "AGENT_TURBO",
                "type": "knowledge_system",
                "critical": True
            },
            "gpu_acceleration": {
                "name": "GPU Acceleration",
                "type": "mlx_system",
                "critical": True
            },
            "lm_studio": {
                "name": "LM Studio",
                "type": "external_service",
                "critical": False
            },
            "ram_disk": {
                "name": "RAM Disk Cache",
                "type": "storage_system",
                "critical": True
            },
            "beta_connectivity": {
                "name": "BETA Connectivity",
                "type": "network_system",
                "critical": False
            },
            "syncthing": {
                "name": "Syncthing",
                "type": "sync_system",
                "critical": False
            },
            "ray_cluster": {
                "name": "Ray Cluster",
                "type": "compute_system",
                "critical": False
            }
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-level metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024**3),
                "network_sent_mb": network.bytes_sent / (1024**2),
                "network_recv_mb": network.bytes_recv / (1024**2)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def monitor_agent_turbo(self) -> MonitorResult:
        """Monitor AGENT_TURBO system."""
        try:
            # Import AGENT_TURBO
            sys.path.insert(0, '/Volumes/DATA/GAMMA/AGENT_TURBO/core')
            from agent_turbo import AgentTurbo
            
            agent = AgentTurbo()
            stats = agent.stats()
            stats_dict = json.loads(stats)
            
            # Check key metrics
            entries = stats_dict.get('entries', 0)
            memory_used = stats_dict.get('memory_used_mb', 0)
            gpu_available = stats_dict.get('using_gpu', False)
            
            if entries > 0 and memory_used > 0:
                status = SystemStatus.HEALTHY
                message = f"AGENT_TURBO operational with {entries} entries"
            else:
                status = SystemStatus.WARNING
                message = "AGENT_TURBO has low activity"
            
            metrics = {
                "entries": entries,
                "memory_used_mb": memory_used,
                "gpu_available": gpu_available
            }
            
            return MonitorResult(
                component="agent_turbo",
                status=status,
                message=message,
                metrics=metrics,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return MonitorResult(
                component="agent_turbo",
                status=SystemStatus.CRITICAL,
                message=f"AGENT_TURBO error: {e}",
                metrics={},
                timestamp=datetime.now()
            )
    
    def monitor_gpu_acceleration(self) -> MonitorResult:
        """Monitor GPU acceleration system."""
        try:
            import mlx.core as mx
            
            # Test GPU availability
            gpu_available = mx.metal.is_available()
            
            if gpu_available:
                # Test GPU performance
                A = mx.random.normal(shape=(1024, 1024))
                B = mx.random.normal(shape=(1024, 1024))
                start = time.time()
                C = A @ B
                mx.eval(C)
                elapsed = time.time() - start
                
                gflops = (2 * 1024**3 / elapsed) / 1e9
                
                if gflops > 10:  # Reasonable threshold
                    status = SystemStatus.HEALTHY
                    message = f"GPU acceleration working ({gflops:.1f} GFLOPS)"
                else:
                    status = SystemStatus.WARNING
                    message = f"GPU performance low ({gflops:.1f} GFLOPS)"
                
                metrics = {
                    "gpu_available": True,
                    "gflops": gflops,
                    "test_time": elapsed
                }
            else:
                status = SystemStatus.CRITICAL
                message = "GPU acceleration not available"
                metrics = {"gpu_available": False}
            
            return MonitorResult(
                component="gpu_acceleration",
                status=status,
                message=message,
                metrics=metrics,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return MonitorResult(
                component="gpu_acceleration",
                status=SystemStatus.CRITICAL,
                message=f"GPU acceleration error: {e}",
                metrics={},
                timestamp=datetime.now()
            )
    
    def monitor_lm_studio(self) -> MonitorResult:
        """Monitor LM Studio service."""
        try:
            import requests
            
            response = requests.get("http://localhost:1234/v1/models", timeout=5)
            
            if response.status_code == 200:
                models = response.json()
                model_count = len(models.get('data', []))
                
                status = SystemStatus.HEALTHY
                message = f"LM Studio operational with {model_count} models"
                metrics = {"model_count": model_count, "status_code": response.status_code}
            else:
                status = SystemStatus.WARNING
                message = f"LM Studio responding with status {response.status_code}"
                metrics = {"status_code": response.status_code}
            
            return MonitorResult(
                component="lm_studio",
                status=status,
                message=message,
                metrics=metrics,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return MonitorResult(
                component="lm_studio",
                status=SystemStatus.OFFLINE,
                message=f"LM Studio offline: {e}",
                metrics={},
                timestamp=datetime.now()
            )
    
    def monitor_ram_disk(self) -> MonitorResult:
        """Monitor RAM disk cache system."""
        try:
            ram_disk_path = Path("/Volumes/DATA/GAMMA/AGENT_RAM")
            
            if ram_disk_path.exists():
                # Check disk usage
                disk_usage = psutil.disk_usage(str(ram_disk_path))
                used_percent = (disk_usage.used / disk_usage.total) * 100
                free_gb = disk_usage.free / (1024**3)
                
                # Check cache directories
                cache_dirs = ["queries", "embeddings", "patterns", "sessions", "temp"]
                existing_dirs = sum(1 for d in cache_dirs if (ram_disk_path / d).exists())
                
                if used_percent < 80 and free_gb > 1:
                    status = SystemStatus.HEALTHY
                    message = f"RAM disk healthy ({used_percent:.1f}% used, {free_gb:.1f} GB free)"
                else:
                    status = SystemStatus.WARNING
                    message = f"RAM disk usage high ({used_percent:.1f}% used)"
                
                metrics = {
                    "used_percent": used_percent,
                    "free_gb": free_gb,
                    "cache_dirs": existing_dirs,
                    "total_dirs": len(cache_dirs)
                }
            else:
                status = SystemStatus.CRITICAL
                message = "RAM disk not mounted"
                metrics = {}
            
            return MonitorResult(
                component="ram_disk",
                status=status,
                message=message,
                metrics=metrics,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return MonitorResult(
                component="ram_disk",
                status=SystemStatus.CRITICAL,
                message=f"RAM disk error: {e}",
                metrics={},
                timestamp=datetime.now()
            )
    
    def monitor_beta_connectivity(self) -> MonitorResult:
        """Monitor BETA system connectivity."""
        try:
            # Test ping
            result = subprocess.run(
                ["ping", "-c", "3", "-q", self.beta_ip],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse latency
                latency = None
                for line in result.stdout.split('\n'):
                    if 'avg' in line:
                        parts = line.split('/')
                        if len(parts) > 4:
                            latency = float(parts[4])
                            break
                
                if latency and latency < 10:
                    status = SystemStatus.HEALTHY
                    message = f"BETA connectivity good ({latency:.2f}ms)"
                else:
                    status = SystemStatus.WARNING
                    message = f"BETA connectivity slow ({latency:.2f}ms)"
                
                metrics = {"latency_ms": latency, "ping_success": True}
            else:
                status = SystemStatus.OFFLINE
                message = "BETA system unreachable"
                metrics = {"ping_success": False}
            
            return MonitorResult(
                component="beta_connectivity",
                status=status,
                message=message,
                metrics=metrics,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return MonitorResult(
                component="beta_connectivity",
                status=SystemStatus.OFFLINE,
                message=f"BETA connectivity error: {e}",
                metrics={},
                timestamp=datetime.now()
            )
    
    def monitor_syncthing(self) -> MonitorResult:
        """Monitor Syncthing service."""
        try:
            result = subprocess.run(
                ["curl", "-s", "http://localhost:8384/rest/system/status"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                status_data = json.loads(result.stdout)
                version = status_data.get('version', 'unknown')
                
                status = SystemStatus.HEALTHY
                message = f"Syncthing running (v{version})"
                metrics = {"version": version, "api_responding": True}
            else:
                status = SystemStatus.OFFLINE
                message = "Syncthing not responding"
                metrics = {"api_responding": False}
            
            return MonitorResult(
                component="syncthing",
                status=status,
                message=message,
                metrics=metrics,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return MonitorResult(
                component="syncthing",
                status=SystemStatus.OFFLINE,
                message=f"Syncthing error: {e}",
                metrics={},
                timestamp=datetime.now()
            )
    
    def monitor_ray_cluster(self) -> MonitorResult:
        """Monitor Ray cluster."""
        try:
            import ray
            
            if ray.is_initialized():
                # Get cluster info
                nodes = ray.nodes()
                alive_nodes = [n for n in nodes if n['Alive']]
                
                if len(alive_nodes) >= 2:
                    status = SystemStatus.HEALTHY
                    message = f"Ray cluster healthy ({len(alive_nodes)} nodes)"
                else:
                    status = SystemStatus.WARNING
                    message = f"Ray cluster degraded ({len(alive_nodes)} nodes)"
                
                metrics = {
                    "total_nodes": len(nodes),
                    "alive_nodes": len(alive_nodes),
                    "ray_initialized": True
                }
            else:
                status = SystemStatus.OFFLINE
                message = "Ray cluster not initialized"
                metrics = {"ray_initialized": False}
            
            return MonitorResult(
                component="ray_cluster",
                status=status,
                message=message,
                metrics=metrics,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return MonitorResult(
                component="ray_cluster",
                status=SystemStatus.OFFLINE,
                message=f"Ray cluster error: {e}",
                metrics={},
                timestamp=datetime.now()
            )
    
    def run_monitoring_cycle(self) -> List[MonitorResult]:
        """Run a complete monitoring cycle."""
        results = []
        
        # Monitor each component
        for component_id, component_info in self.components.items():
            try:
                if component_id == "agent_turbo":
                    result = self.monitor_agent_turbo()
                elif component_id == "gpu_acceleration":
                    result = self.monitor_gpu_acceleration()
                elif component_id == "lm_studio":
                    result = self.monitor_lm_studio()
                elif component_id == "ram_disk":
                    result = self.monitor_ram_disk()
                elif component_id == "beta_connectivity":
                    result = self.monitor_beta_connectivity()
                elif component_id == "syncthing":
                    result = self.monitor_syncthing()
                elif component_id == "ray_cluster":
                    result = self.monitor_ray_cluster()
                else:
                    continue
                
                results.append(result)
                
            except Exception as e:
                results.append(MonitorResult(
                    component=component_id,
                    status=SystemStatus.CRITICAL,
                    message=f"Monitoring error: {e}",
                    metrics={},
                    timestamp=datetime.now()
                ))
        
        # Store results
        self.results.extend(results)
        
        # Keep only last 100 results
        if len(self.results) > 100:
            self.results = self.results[-100:]
        
        return results
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get overall system status summary."""
        if not self.results:
            return {"status": "unknown", "message": "No monitoring data"}
        
        # Get latest results
        latest_results = {}
        for result in self.results:
            if result.component not in latest_results:
                latest_results[result.component] = result
        
        # Count statuses
        status_counts = {
            SystemStatus.HEALTHY: 0,
            SystemStatus.WARNING: 0,
            SystemStatus.CRITICAL: 0,
            SystemStatus.OFFLINE: 0
        }
        
        for result in latest_results.values():
            status_counts[result.status] += 1
        
        # Determine overall status
        if status_counts[SystemStatus.CRITICAL] > 0:
            overall_status = SystemStatus.CRITICAL
            message = f"{status_counts[SystemStatus.CRITICAL]} critical issues"
        elif status_counts[SystemStatus.WARNING] > 0:
            overall_status = SystemStatus.WARNING
            message = f"{status_counts[SystemStatus.WARNING]} warnings"
        elif status_counts[SystemStatus.OFFLINE] > 0:
            overall_status = SystemStatus.WARNING
            message = f"{status_counts[SystemStatus.OFFLINE]} offline components"
        else:
            overall_status = SystemStatus.HEALTHY
            message = "All systems operational"
        
        return {
            "overall_status": overall_status.value,
            "message": message,
            "status_counts": {k.value: v for k, v in status_counts.items()},
            "components": {
                comp: {
                    "status": result.status.value,
                    "message": result.message,
                    "timestamp": result.timestamp.isoformat()
                }
                for comp, result in latest_results.items()
            },
            "system_metrics": self.get_system_metrics()
        }
    
    def monitor_continuously(self, duration: int = 300) -> None:
        """Monitor system continuously for specified duration."""
        print("📊 Starting GAMMA system monitoring...")
        print(f"Duration: {duration} seconds")
        print("-" * 50)
        
        start_time = time.time()
        
        try:
            while time.time() - start_time < duration:
                # Run monitoring cycle
                results = self.run_monitoring_cycle()
                
                # Clear screen
                os.system('clear' if os.name == 'posix' else 'cls')
                
                print("=" * 50)
                print("   GAMMA SYSTEM MONITOR")
                print("=" * 50)
                print(f"Time: {time.strftime('%H:%M:%S')}")
                print()
                
                # Show overall status
                summary = self.get_status_summary()
                print(f"Overall Status: {summary['overall_status'].upper()}")
                print(f"Message: {summary['message']}")
                print()
                
                # Show component statuses
                print("Component Status:")
                for comp, info in summary['components'].items():
                    status_icon = {
                        'healthy': '✅',
                        'warning': '⚠️',
                        'critical': '❌',
                        'offline': '🔴'
                    }.get(info['status'], '❓')
                    
                    print(f"  {status_icon} {comp}: {info['message']}")
                
                print()
                print("Press Ctrl+C to exit")
                
                # Wait for next cycle
                time.sleep(self.monitoring_interval)
                
        except KeyboardInterrupt:
            print("\n\n✅ Monitoring stopped")
        except Exception as e:
            print(f"\n❌ Monitoring error: {e}")

def main():
    """Main function for testing GAMMA Monitoring System."""
    print("🚀 GAMMA Monitoring System Test")
    print("-" * 40)
    
    monitor = GammaMonitoringSystem()
    
    # Run single monitoring cycle
    print("🔍 Running monitoring cycle...")
    results = monitor.run_monitoring_cycle()
    
    # Show results
    for result in results:
        status_icon = {
            SystemStatus.HEALTHY: '✅',
            SystemStatus.WARNING: '⚠️',
            SystemStatus.CRITICAL: '❌',
            SystemStatus.OFFLINE: '🔴'
        }.get(result.status, '❓')
        
        print(f"{status_icon} {result.component}: {result.message}")
    
    # Show summary
    summary = monitor.get_status_summary()
    print(f"\n📊 Overall Status: {summary['overall_status'].upper()}")
    print(f"Message: {summary['message']}")
    
    print("\n✨ GAMMA Monitoring System ready!")
    print("\nTo monitor continuously:")
    print("  monitor.monitor_continuously(300)")
    
    return True

if __name__ == "__main__":
    main()

