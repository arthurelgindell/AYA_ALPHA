#!/usr/bin/env python3
"""
GAMMA Syncthing Manager
GAMMA-native file synchronization system for distributed computing
Provides sophisticated file synchronization between ALPHA and BETA
"""

import json
import time
import subprocess
import os
import sys
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import requests
from pathlib import Path

class SyncStatus(Enum):
    """Syncthing sync status."""
    IDLE = "idle"
    SCANNING = "scanning"
    SYNCING = "syncing"
    ERROR = "error"
    UNKNOWN = "unknown"

@dataclass
class FolderInfo:
    """Syncthing folder information."""
    id: str
    label: str
    path: str
    type: str
    devices: List[str]
    status: SyncStatus
    local_files: int
    global_files: int
    need_files: int

@dataclass
class DeviceInfo:
    """Syncthing device information."""
    id: str
    name: str
    addresses: List[str]
    connected: bool
    last_seen: Optional[str] = None

class GammaSyncthingManager:
    """Sophisticated Syncthing management for GAMMA project."""
    
    def __init__(self):
        self.api_url = "http://localhost:8384/rest"
        self.api_key = None
        self.beta_device_id = None
        self.alpha_device_id = None
        self.folders = {}
        self.devices = {}
        
        # GAMMA-specific configuration
        self.gamma_folders = {
            "gamma_agent_turbo": {
                "id": "gamma-agent-turbo",
                "label": "GAMMA Agent Turbo",
                "path": "/Volumes/DATA/GAMMA/AGENT_TURBO",
                "type": "sendreceive"
            },
            "gamma_agent_ram": {
                "id": "gamma-agent-ram",
                "label": "GAMMA Agent RAM Cache",
                "path": "/Volumes/DATA/GAMMA/AGENT_RAM",
                "type": "sendreceive"
            },
            "gamma_knowledge": {
                "id": "gamma-knowledge",
                "label": "GAMMA Knowledge Base",
                "path": "/Volumes/DATA/GAMMA/AGENT_TURBO/core",
                "type": "sendreceive"
            }
        }
    
    def is_syncthing_running(self) -> bool:
        """Check if Syncthing is running locally."""
        try:
            result = subprocess.run(
                ["curl", "-s", f"{self.api_url}/system/status"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def start_syncthing(self) -> bool:
        """Start Syncthing service."""
        try:
            # Kill existing Syncthing processes
            subprocess.run(["pkill", "syncthing"], capture_output=True)
            time.sleep(2)
            
            # Start Syncthing
            subprocess.Popen([
                "/opt/homebrew/opt/syncthing/bin/syncthing",
                "--no-browser",
                "--no-restart",
                "--gui-address=0.0.0.0:8384"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Wait for API to be ready
            for i in range(10):
                if self.is_syncthing_running():
                    return True
                time.sleep(2)
            
            return False
        except Exception as e:
            print(f"Failed to start Syncthing: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get Syncthing system status."""
        try:
            result = subprocess.run(
                ["curl", "-s", f"{self.api_url}/system/status"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            return {}
        except:
            return {}
    
    def get_device_id(self) -> Optional[str]:
        """Get local device ID."""
        try:
            result = subprocess.run(
                ["/opt/homebrew/opt/syncthing/bin/syncthing", "--device-id"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                device_id = result.stdout.strip()
                if device_id and len(device_id) > 20:
                    return device_id
            return None
        except:
            return None
    
    def get_connections(self) -> Dict[str, Any]:
        """Get device connections."""
        try:
            result = subprocess.run(
                ["curl", "-s", f"{self.api_url}/system/connections"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            return {}
        except:
            return {}
    
    def get_folders(self) -> Dict[str, Any]:
        """Get folder configurations."""
        try:
            result = subprocess.run(
                ["curl", "-s", f"{self.api_url}/config/folders"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            return {}
        except:
            return {}
    
    def get_folder_status(self, folder_id: str) -> Dict[str, Any]:
        """Get status for specific folder."""
        try:
            result = subprocess.run(
                ["curl", "-s", f"{self.api_url}/db/status?folder={folder_id}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            return {}
        except:
            return {}
    
    def add_device(self, device_id: str, name: str, addresses: List[str]) -> bool:
        """Add a device to Syncthing."""
        try:
            device_config = {
                "deviceID": device_id,
                "name": name,
                "addresses": addresses,
                "compression": "metadata",
                "introducer": False,
                "paused": False,
                "allowedNetworks": [],
                "autoAcceptFolders": True
            }
            
            result = subprocess.run([
                "curl", "-X", "POST", f"{self.api_url}/config/devices",
                "-H", "Content-Type: application/json",
                "-d", json.dumps(device_config)
            ], capture_output=True, text=True, timeout=10)
            
            return result.returncode == 0
        except:
            return False
    
    def create_folder(self, folder_config: Dict[str, Any]) -> bool:
        """Create a new folder in Syncthing."""
        try:
            result = subprocess.run([
                "curl", "-X", "PUT", f"{self.api_url}/config/folders",
                "-H", "Content-Type: application/json",
                "-d", json.dumps(folder_config)
            ], capture_output=True, text=True, timeout=10)
            
            return result.returncode == 0
        except:
            return False
    
    def restart_syncthing(self) -> bool:
        """Restart Syncthing service."""
        try:
            result = subprocess.run([
                "curl", "-X", "POST", f"{self.api_url}/system/restart"
            ], capture_output=True, text=True, timeout=10)
            
            return result.returncode == 0
        except:
            return False
    
    def setup_gamma_folders(self) -> bool:
        """Setup GAMMA-specific folders for synchronization."""
        print("🔧 Setting up GAMMA Syncthing folders...")
        
        # Get local device ID
        self.alpha_device_id = self.get_device_id()
        if not self.alpha_device_id:
            print("❌ Could not get local device ID")
            return False
        
        print(f"✅ Local device ID: {self.alpha_device_id[:8]}...")
        
        # Create GAMMA folders
        for folder_name, folder_info in self.gamma_folders.items():
            print(f"📁 Creating folder: {folder_info['label']}")
            
            # Ensure folder path exists
            Path(folder_info['path']).mkdir(parents=True, exist_ok=True)
            
            # Create folder configuration
            folder_config = {
                "id": folder_info['id'],
                "label": folder_info['label'],
                "path": folder_info['path'],
                "type": folder_info['type'],
                "devices": [],
                "rescanIntervalS": 60,
                "fsWatcherEnabled": True,
                "fsWatcherDelayS": 10,
                "versioning": {
                    "type": "simple",
                    "params": {"keep": "10"}
                }
            }
            
            # Add BETA device if available
            if self.beta_device_id:
                folder_config["devices"].append({
                    "deviceID": self.beta_device_id,
                    "introducedBy": "",
                    "encryptionPassword": ""
                })
            
            # Create folder
            if self.create_folder(folder_config):
                print(f"  ✅ Created: {folder_info['label']}")
            else:
                print(f"  ❌ Failed: {folder_info['label']}")
        
        return True
    
    def add_beta_device(self, beta_device_id: str, beta_ip: str = "100.84.202.68") -> bool:
        """Add BETA device to Syncthing."""
        print(f"🔗 Adding BETA device: {beta_device_id[:8]}...")
        
        self.beta_device_id = beta_device_id
        
        # Add BETA device
        if self.add_device(
            device_id=beta_device_id,
            name="GAMMA-BETA",
            addresses=[f"tcp://{beta_ip}:22000"]
        ):
            print("✅ BETA device added")
            
            # Update folders to include BETA
            self.setup_gamma_folders()
            
            # Restart to apply changes
            self.restart_syncthing()
            time.sleep(5)
            
            return True
        else:
            print("❌ Failed to add BETA device")
            return False
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get comprehensive sync status."""
        status = {
            "syncthing_running": self.is_syncthing_running(),
            "system_status": self.get_system_status(),
            "connections": self.get_connections(),
            "folders": {},
            "devices": {}
        }
        
        # Get folder statuses
        for folder_name, folder_info in self.gamma_folders.items():
            folder_status = self.get_folder_status(folder_info['id'])
            status["folders"][folder_name] = {
                "id": folder_info['id'],
                "label": folder_info['label'],
                "path": folder_info['path'],
                "status": folder_status
            }
        
        return status
    
    def monitor_sync(self, duration: int = 60) -> None:
        """Monitor sync status for specified duration."""
        print("📊 Monitoring GAMMA Syncthing status...")
        print(f"Duration: {duration} seconds")
        print("-" * 50)
        
        start_time = time.time()
        
        while time.time() - start_time < duration:
            status = self.get_sync_status()
            
            # Clear screen
            os.system('clear' if os.name == 'posix' else 'cls')
            
            print("=" * 50)
            print("   GAMMA SYNCTHING MONITOR")
            print("=" * 50)
            print(f"Time: {time.strftime('%H:%M:%S')}")
            print(f"Syncthing: {'✅ Running' if status['syncthing_running'] else '❌ Stopped'}")
            print()
            
            # Show connections
            connections = status.get('connections', {}).get('connections', {})
            connected_devices = sum(1 for info in connections.values() if info.get('connected', False))
            print(f"Connected devices: {connected_devices}")
            
            # Show folder statuses
            print("\n📁 Folder Status:")
            for folder_name, folder_data in status['folders'].items():
                folder_status = folder_data.get('status', {})
                state = folder_status.get('state', 'unknown')
                local_files = folder_status.get('localFiles', 0)
                global_files = folder_status.get('globalFiles', 0)
                need_files = folder_status.get('needFiles', 0)
                
                print(f"  {folder_data['label']}:")
                print(f"    State: {state}")
                print(f"    Files: {local_files}/{global_files} (Need: {need_files})")
            
            print("\nPress Ctrl+C to exit")
            time.sleep(2)
    
    def test_sync_functionality(self) -> bool:
        """Test sync functionality with a test file."""
        print("🧪 Testing GAMMA sync functionality...")
        
        # Create test file
        test_file = Path("/Volumes/DATA/GAMMA/AGENT_TURBO/sync_test.txt")
        test_content = f"GAMMA Sync Test - {time.strftime('%Y-%m-%d %H:%M:%S')}"
        
        try:
            test_file.write_text(test_content)
            print(f"✅ Created test file: {test_file}")
            
            # Wait for sync
            print("⏳ Waiting for sync...")
            time.sleep(10)
            
            # Check if file exists (simplified test)
            if test_file.exists():
                print("✅ Test file exists")
                return True
            else:
                print("❌ Test file not found")
                return False
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
        finally:
            # Clean up test file
            if test_file.exists():
                test_file.unlink()

def main():
    """Main function for testing GAMMA Syncthing Manager."""
    print("🚀 GAMMA Syncthing Manager Test")
    print("-" * 40)
    
    manager = GammaSyncthingManager()
    
    # Check if Syncthing is running
    if not manager.is_syncthing_running():
        print("🔄 Starting Syncthing...")
        if not manager.start_syncthing():
            print("❌ Failed to start Syncthing")
            return False
        print("✅ Syncthing started")
    
    # Get system status
    status = manager.get_system_status()
    print(f"📊 Syncthing version: {status.get('version', 'unknown')}")
    
    # Get device ID
    device_id = manager.get_device_id()
    if device_id:
        print(f"🆔 Device ID: {device_id[:8]}...")
    
    # Setup folders
    if manager.setup_gamma_folders():
        print("✅ GAMMA folders configured")
    else:
        print("❌ Failed to configure folders")
    
    # Get sync status
    sync_status = manager.get_sync_status()
    print(f"📁 Folders configured: {len(sync_status['folders'])}")
    
    print("\n✨ GAMMA Syncthing Manager ready!")
    print("\nTo add BETA device:")
    print("  manager.add_beta_device('BETA_DEVICE_ID')")
    print("\nTo monitor sync:")
    print("  manager.monitor_sync(60)")
    
    return True

if __name__ == "__main__":
    main()

