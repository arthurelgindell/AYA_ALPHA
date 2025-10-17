#!/usr/bin/env python3
"""
GAMMA Ray Cluster Manager
GAMMA-native Ray cluster management for distributed computing
Provides sophisticated distributed computing across ALPHA and BETA
"""

import ray
import time
import subprocess
import os
import sys
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio

class ClusterRole(Enum):
    """Cluster node roles."""
    HEAD = "head"
    WORKER = "worker"

@dataclass
class NodeInfo:
    """Ray cluster node information."""
    node_id: str
    ip_address: str
    role: ClusterRole
    cpu_cores: int
    memory_gb: float
    gpu_cores: int
    status: str

class GammaRayCluster:
    """Sophisticated Ray cluster management for GAMMA project."""
    
    def __init__(self):
        # Use current GAMMA system IPs
        self.alpha_ip = "100.106.170.128"  # Current ALPHA IP from Tailscale
        self.beta_ip = "100.84.202.68"     # Current BETA IP from Tailscale
        self.ray_port = 6380
        self.cluster_address = f"{self.alpha_ip}:{self.ray_port}"
        self.is_head = False
        self.is_worker = False
        self.nodes = {}
        
        # GAMMA-specific configuration
        self.gamma_config = {
            "alpha": {
                "ip": self.alpha_ip,
                "ram_gb": 512,
                "gpu_cores": 80,
                "cpu_cores": 32
            },
            "beta": {
                "ip": self.beta_ip,
                "ram_gb": 256,
                "gpu_cores": 80,
                "cpu_cores": 32
            }
        }
    
    def start_head_node(self) -> bool:
        """Start Ray head node on ALPHA."""
        print("🚀 Starting GAMMA Ray head node...")
        
        try:
            # Stop any existing Ray processes
            subprocess.run(["ray", "stop", "--force"], capture_output=True)
            time.sleep(2)
            
            # Start Ray head
            result = subprocess.run([
                "ray", "start",
                "--head",
                f"--port={self.ray_port}",
                f"--node-ip-address={self.alpha_ip}",
                f"--num-cpus={self.gamma_config['alpha']['cpu_cores']}",
                f"--memory={int(self.gamma_config['alpha']['ram_gb'] * 0.8 * 1024**3)}",
                "--disable-usage-stats"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Ray head node started")
                self.is_head = True
                return True
            else:
                print(f"❌ Failed to start head node: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting head node: {e}")
            return False
    
    def start_worker_node(self) -> bool:
        """Start Ray worker node on BETA."""
        print("🚀 Starting GAMMA Ray worker node on BETA...")
        
        try:
            # Create worker start script
            worker_script = f"""#!/bin/bash
ray start \\
    --address="{self.cluster_address}" \\
    --node-ip-address="{self.beta_ip}" \\
    --num-cpus={self.gamma_config['beta']['cpu_cores']} \\
    --memory={int(self.gamma_config['beta']['ram_gb'] * 0.8 * 1024**3)} \\
    --disable-usage-stats
"""
            
            # Execute on BETA via SSH
            result = subprocess.run([
                "ssh", "-o", "ConnectTimeout=10", "-o", "StrictHostKeyChecking=no",
                f"arthurdell@{self.beta_ip}", worker_script
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ Ray worker node started on BETA")
                self.is_worker = True
                return True
            else:
                print(f"❌ Failed to start worker node: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting worker node: {e}")
            return False
    
    def connect_to_cluster(self) -> bool:
        """Connect to existing Ray cluster."""
        try:
            ray.init(address=self.cluster_address, ignore_reinit_error=True)
            print("✅ Connected to GAMMA Ray cluster")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to cluster: {e}")
            return False
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """Get comprehensive cluster status."""
        try:
            if not ray.is_initialized():
                if not self.connect_to_cluster():
                    return {"error": "Cannot connect to cluster"}
            
            # Get cluster resources
            resources = ray.cluster_resources()
            available = ray.available_resources()
            
            # Get nodes
            nodes = ray.nodes()
            
            # Get cluster info
            cluster_info = {
                "connected": ray.is_initialized(),
                "resources": {
                    "total_cpus": int(resources.get('CPU', 0)),
                    "available_cpus": int(available.get('CPU', 0)),
                    "total_memory_gb": resources.get('memory', 0) / (1024**3),
                    "available_memory_gb": available.get('memory', 0) / (1024**3),
                    "total_gpus": int(resources.get('GPU', 0)),
                    "available_gpus": int(available.get('GPU', 0))
                },
                "nodes": [],
                "node_count": len([n for n in nodes if n['Alive']])
            }
            
            # Process node information
            for i, node in enumerate(nodes):
                if node['Alive']:
                    node_info = {
                        "node_id": node['NodeID'],
                        "ip_address": node['NodeManagerAddress'],
                        "role": "head" if i == 0 else "worker",
                        "cpu_cores": int(node['Resources'].get('CPU', 0)),
                        "memory_gb": node['Resources'].get('memory', 0) / (1024**3),
                        "gpu_cores": int(node['Resources'].get('GPU', 0)),
                        "status": "active"
                    }
                    cluster_info["nodes"].append(node_info)
            
            return cluster_info
            
        except Exception as e:
            return {"error": str(e)}
    
    def test_gpu_distribution(self) -> bool:
        """Test GPU task distribution across cluster."""
        print("🧪 Testing GPU task distribution...")
        
        try:
            if not ray.is_initialized():
                if not self.connect_to_cluster():
                    return False
            
            # Get BETA node
            nodes = ray.nodes()
            beta_nodes = [n for n in nodes if n['Alive'] and self.beta_ip in n.get('NodeManagerAddress', '')]
            
            if not beta_nodes:
                print("❌ BETA node not found in cluster")
                return False
            
            beta_node_id = beta_nodes[0]['NodeID']
            print(f"✅ Found BETA node: {beta_node_id[:8]}...")
            
            # Force task on BETA using node affinity
            @ray.remote(
                num_cpus=1,
                scheduling_strategy=ray.util.scheduling_strategies.NodeAffinitySchedulingStrategy(
                    node_id=beta_node_id,
                    soft=False
                )
            )
            def gpu_task_on_beta():
                import socket
                hostname = socket.gethostname()
                
                # Test MLX
                try:
                    import mlx.core as mx
                    
                    # Small GPU test
                    A = mx.random.normal(shape=(1024, 1024))
                    B = mx.random.normal(shape=(1024, 1024))
                    start = time.time()
                    C = A @ B
                    mx.eval(C)
                    elapsed = time.time() - start
                    
                    return {
                        'hostname': hostname,
                        'mlx_working': True,
                        'time': elapsed,
                        'gflops': (2 * 1024**3 / elapsed) / 1e9
                    }
                except Exception as e:
                    return {
                        'hostname': hostname,
                        'mlx_working': False,
                        'error': str(e)
                    }
            
            print("🚀 Forcing GPU task on BETA node...")
            result = ray.get(gpu_task_on_beta.remote())
            
            print(f"📍 Task executed on: {result['hostname']}")
            
            if 'BETA' in result['hostname'] or self.beta_ip in result['hostname']:
                if result['mlx_working']:
                    print(f"✅ SUCCESS! GPU working on BETA")
                    print(f"   Performance: {result['gflops']:.1f} GFLOPS")
                    return True
                else:
                    print(f"❌ Task reached BETA but MLX failed")
                    print(f"   Error: {result.get('error', 'Unknown')}")
                    return False
            else:
                print(f"❌ Task did NOT run on BETA (ran on {result['hostname']})")
                return False
                
        except Exception as e:
            print(f"❌ GPU distribution test failed: {e}")
            return False
    
    def distribute_mlx_tasks(self, tasks: List[Dict[str, Any]]) -> List[Any]:
        """Distribute MLX GPU tasks across cluster."""
        try:
            if not ray.is_initialized():
                if not self.connect_to_cluster():
                    return []
            
            @ray.remote(num_gpus=1)
            def mlx_task(task_data):
                import mlx.core as mx
                import time
                
                # Simple MLX processing
                A = mx.random.normal(shape=(1024, 1024))
                B = mx.random.normal(shape=(1024, 1024))
                start = time.time()
                C = A @ B
                mx.eval(C)
                elapsed = time.time() - start
                
                return {
                    "task_id": task_data.get("id"),
                    "result": f"Processed: {task_data.get('data', '')[:50]}",
                    "gflops": (2 * 1024**3 / elapsed) / 1e9,
                    "time": elapsed
                }
            
            # Submit tasks
            futures = [mlx_task.remote(task) for task in tasks]
            results = ray.get(futures)
            
            return results
            
        except Exception as e:
            print(f"❌ MLX task distribution failed: {e}")
            return []
    
    def benchmark_cluster_performance(self) -> Dict[str, Any]:
        """Benchmark cluster performance."""
        print("📊 Benchmarking GAMMA Ray cluster performance...")
        
        try:
            if not ray.is_initialized():
                if not self.connect_to_cluster():
                    return {}
            
            # Test tasks
            test_tasks = [
                {"id": f"task_{i}", "data": f"Test data {i}" * 100}
                for i in range(10)
            ]
            
            # Benchmark MLX tasks
            start_time = time.time()
            results = self.distribute_mlx_tasks(test_tasks)
            elapsed = time.time() - start_time
            
            if results:
                avg_gflops = sum(r.get('gflops', 0) for r in results) / len(results)
                avg_time = sum(r.get('time', 0) for r in results) / len(results)
                
                benchmark = {
                    "total_tasks": len(test_tasks),
                    "completed_tasks": len(results),
                    "total_time": elapsed,
                    "average_gflops": avg_gflops,
                    "average_task_time": avg_time,
                    "throughput": len(results) / elapsed
                }
                
                print(f"✅ Benchmark completed:")
                print(f"   Tasks: {benchmark['completed_tasks']}/{benchmark['total_tasks']}")
                print(f"   Time: {benchmark['total_time']:.2f}s")
                print(f"   Average GFLOPS: {benchmark['average_gflops']:.1f}")
                print(f"   Throughput: {benchmark['throughput']:.2f} tasks/s")
                
                return benchmark
            else:
                print("❌ Benchmark failed - no results")
                return {}
                
        except Exception as e:
            print(f"❌ Benchmark failed: {e}")
            return {}
    
    def monitor_cluster(self, duration: int = 60) -> None:
        """Monitor cluster status for specified duration."""
        print("📊 Monitoring GAMMA Ray cluster...")
        print(f"Duration: {duration} seconds")
        print("-" * 50)
        
        start_time = time.time()
        
        while time.time() - start_time < duration:
            status = self.get_cluster_status()
            
            # Clear screen
            os.system('clear' if os.name == 'posix' else 'cls')
            
            print("=" * 50)
            print("   GAMMA RAY CLUSTER MONITOR")
            print("=" * 50)
            print(f"Time: {time.strftime('%H:%M:%S')}")
            print(f"Connected: {'✅' if status.get('connected') else '❌'}")
            print(f"Nodes: {status.get('node_count', 0)}")
            print()
            
            # Show resources
            resources = status.get('resources', {})
            print("📊 Resources:")
            print(f"  CPUs: {resources.get('available_cpus', 0)}/{resources.get('total_cpus', 0)}")
            print(f"  Memory: {resources.get('available_memory_gb', 0):.1f}/{resources.get('total_memory_gb', 0):.1f} GB")
            print(f"  GPUs: {resources.get('available_gpus', 0)}/{resources.get('total_gpus', 0)}")
            print()
            
            # Show nodes
            print("📍 Nodes:")
            for node in status.get('nodes', []):
                print(f"  {node['role']}: {node['ip_address']} ({node['cpu_cores']} CPUs, {node['memory_gb']:.1f} GB)")
            
            print("\nPress Ctrl+C to exit")
            time.sleep(2)
    
    def shutdown_cluster(self) -> bool:
        """Shutdown Ray cluster."""
        try:
            if ray.is_initialized():
                ray.shutdown()
                print("✅ Ray cluster shutdown")
            
            # Stop Ray processes
            subprocess.run(["ray", "stop", "--force"], capture_output=True)
            print("✅ Ray processes stopped")
            
            return True
        except Exception as e:
            print(f"❌ Error shutting down cluster: {e}")
            return False

def main():
    """Main function for testing GAMMA Ray Cluster."""
    print("🚀 GAMMA Ray Cluster Test")
    print("-" * 40)
    
    cluster = GammaRayCluster()
    
    # Start head node
    if cluster.start_head_node():
        print("✅ Head node started")
        
        # Start worker node
        if cluster.start_worker_node():
            print("✅ Worker node started")
            
            # Connect to cluster
            if cluster.connect_to_cluster():
                print("✅ Connected to cluster")
                
                # Get cluster status
                status = cluster.get_cluster_status()
                print(f"📊 Cluster nodes: {status.get('node_count', 0)}")
                
                # Test GPU distribution
                if cluster.test_gpu_distribution():
                    print("✅ GPU distribution working")
                    
                    # Benchmark performance
                    benchmark = cluster.benchmark_cluster_performance()
                    if benchmark:
                        print("✅ Performance benchmark completed")
                
                print("\n✨ GAMMA Ray Cluster ready!")
                print("\nTo monitor cluster:")
                print("  cluster.monitor_cluster(60)")
                print("\nTo shutdown:")
                print("  cluster.shutdown_cluster()")
                
            else:
                print("❌ Failed to connect to cluster")
        else:
            print("❌ Failed to start worker node")
    else:
        print("❌ Failed to start head node")
    
    return True

if __name__ == "__main__":
    main()

