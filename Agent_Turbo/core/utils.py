#!/usr/bin/env python3
"""
AGENT_TURBO Utilities
Shared utility functions for the AGENT_TURBO system
"""

import time
import json
from pathlib import Path
from typing import Optional, Dict, Any

def now_iso() -> str:
    """Get current timestamp in ISO format."""
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())

def timestamp_suffix() -> str:
    """Get timestamp suffix for file naming."""
    return time.strftime("%Y-%m-%d_%H%M", time.localtime())

def safe_json_loads(s: str) -> Optional[dict]:
    """Safely parse JSON string."""
    try:
        return json.loads(s)
    except Exception:
        return None

def read_json_file(path: Path) -> Optional[dict]:
    """Read JSON file safely."""
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return None

def ensure_dir(p: Path) -> None:
    """Ensure directory exists."""
    p.mkdir(parents=True, exist_ok=True)

def get_memory_usage() -> Dict[str, Any]:
    """Get current memory usage statistics."""
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        return {
            "rss_mb": memory_info.rss / 1024 / 1024,
            "vms_mb": memory_info.vms / 1024 / 1024,
            "percent": process.memory_percent()
        }
    except ImportError:
        return {"error": "psutil not available"}

def get_gpu_info() -> Dict[str, Any]:
    """Get GPU information if available."""
    try:
        import mlx.core as mx
        device_info = mx.metal.device_info()
        return {
            "available": True,
            "cores": device_info.get('gpu_cores', 0),
            "memory_gb": mx.metal.get_active_memory() / (1024**3)
        }
    except ImportError:
        return {"available": False, "error": "MLX not available"}

def format_bytes(bytes_value: int) -> str:
    """Format bytes into human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"

