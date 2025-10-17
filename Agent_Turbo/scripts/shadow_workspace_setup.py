#!/usr/bin/env python3
"""
Shadow Workspace Setup for AGENT_TURBO
Implements cursor-shadow-workspace for parallel development and isolation
GAMMA Project - Prime Directives Compliance
"""

import subprocess
import json
import time
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

class ShadowWorkspaceSetup:
    """Shadow workspace setup for parallel development."""
    
    def __init__(self):
        self.cursor_extensions_path = Path("/Applications/Cursor.app/Contents/Resources/app/extensions")
        self.shadow_workspace_path = self.cursor_extensions_path / "cursor-shadow-workspace"
        self.base_workspace = Path("/Volumes/DATA/Agent_Turbo")
        self.shadow_workspaces = {
            "development": Path("/Volumes/DATA/Agent_Turbo_Dev"),
            "testing": Path("/Volumes/DATA/Agent_Turbo_Test"),
            "experimental": Path("/Volumes/DATA/Agent_Turbo_Exp"),
            "backup": Path("/Volumes/DATA/Agent_Turbo_Backup")
        }
        self.status = {
            "shadow_workspace_available": False,
            "workspaces_created": [],
            "active_workspace": None
        }
        
    def verify_shadow_workspace_extension(self) -> bool:
        """Verify shadow workspace extension is available."""
        try:
            shadow_exists = self.shadow_workspace_path.exists()
            print(f"✅ Shadow Workspace Extension: {'Available' if shadow_exists else 'Missing'}")
            
            if shadow_exists:
                self.status["shadow_workspace_available"] = True
                
            return shadow_exists
        except Exception as e:
            print(f"❌ Shadow workspace verification failed: {e}")
            return False
    
    def create_shadow_workspaces(self) -> bool:
        """Create shadow workspaces for parallel development."""
        try:
            created_workspaces = []
            
            for name, path in self.shadow_workspaces.items():
                if not path.exists():
                    print(f"🚀 Creating shadow workspace: {name} at {path}")
                    
                    # Create directory structure
                    path.mkdir(parents=True, exist_ok=True)
                    
                    # Copy essential files and directories
                    essential_items = [
                        "core",
                        "scripts", 
                        "config",
                        "data",
                        ".cursorrules",
                        "README.md"
                    ]
                    
                    for item in essential_items:
                        src = self.base_workspace / item
                        dst = path / item
                        
                        if src.exists():
                            if src.is_dir():
                                shutil.copytree(src, dst, dirs_exist_ok=True)
                            else:
                                shutil.copy2(src, dst)
                    
                    # Create workspace-specific configuration
                    self.create_workspace_config(path, name)
                    
                    created_workspaces.append(name)
                    print(f"✅ Shadow workspace '{name}' created")
                else:
                    print(f"✅ Shadow workspace '{name}' already exists")
                    created_workspaces.append(name)
            
            self.status["workspaces_created"] = created_workspaces
            return True
            
        except Exception as e:
            print(f"❌ Shadow workspace creation failed: {e}")
            return False
    
    def create_workspace_config(self, workspace_path: Path, workspace_name: str) -> bool:
        """Create workspace-specific configuration."""
        try:
            config_content = {
                "workspace_name": workspace_name,
                "base_workspace": str(self.base_workspace),
                "created_at": time.time(),
                "purpose": self.get_workspace_purpose(workspace_name),
                "settings": {
                    "agent_turbo_mode": "turbo",
                    "gpu_acceleration": True,
                    "ram_disk_cache": True,
                    "lm_studio_integration": True
                }
            }
            
            config_path = workspace_path / ".workspace_config.json"
            config_path.write_text(json.dumps(config_content, indent=2))
            
            # Create workspace-specific .cursorrules
            cursorrules_content = f"""# SHADOW WORKSPACE: {workspace_name.upper()}

## WORKSPACE PURPOSE
{self.get_workspace_purpose(workspace_name)}

## BASE WORKSPACE
{self.base_workspace}

## WORKSPACE-SPECIFIC DIRECTIVES
- This is a shadow workspace for {workspace_name}
- Changes here are isolated from the main workspace
- Sync with base workspace as needed
- Follow all Prime Directives

## AGENT TURBO INTEGRATION
- Agent Turbo core: {workspace_path}/core/agent_turbo.py
- GPU acceleration: Enabled
- RAM disk cache: Enabled
- LM Studio integration: Enabled

## WORKSPACE ISOLATION
- Independent development environment
- Parallel testing capabilities
- Experimental feature development
- Backup and recovery operations
"""
            
            cursorrules_path = workspace_path / ".cursorrules"
            cursorrules_path.write_text(cursorrules_content)
            
            return True
            
        except Exception as e:
            print(f"❌ Workspace config creation failed: {e}")
            return False
    
    def get_workspace_purpose(self, workspace_name: str) -> str:
        """Get workspace purpose description."""
        purposes = {
            "development": "Active development and feature implementation",
            "testing": "Testing and validation of new features",
            "experimental": "Experimental features and proof-of-concept work",
            "backup": "Backup and recovery operations"
        }
        return purposes.get(workspace_name, "General purpose workspace")
    
    def create_workspace_launcher(self) -> bool:
        """Create workspace launcher script."""
        try:
            launcher_content = '''#!/usr/bin/env python3
"""
Shadow Workspace Launcher for AGENT_TURBO
Launches Cursor with specific shadow workspace
"""

import subprocess
import sys
import json
from pathlib import Path

def launch_workspace(workspace_name: str):
    """Launch Cursor with specific shadow workspace."""
    workspaces = {
        "development": "/Volumes/DATA/Agent_Turbo_Dev",
        "testing": "/Volumes/DATA/Agent_Turbo_Test", 
        "experimental": "/Volumes/DATA/Agent_Turbo_Exp",
        "backup": "/Volumes/DATA/Agent_Turbo_Backup"
    }
    
    if workspace_name not in workspaces:
        print(f"❌ Unknown workspace: {workspace_name}")
        print(f"Available workspaces: {list(workspaces.keys())}")
        return False
    
    workspace_path = workspaces[workspace_name]
    
    if not Path(workspace_path).exists():
        print(f"❌ Workspace not found: {workspace_path}")
        return False
    
    try:
        # Launch Cursor with workspace
        cmd = ["cursor", workspace_path]
        subprocess.Popen(cmd)
        print(f"✅ Launched Cursor with {workspace_name} workspace")
        return True
    except Exception as e:
        print(f"❌ Failed to launch workspace: {e}")
        return False

def list_workspaces():
    """List available shadow workspaces."""
    workspaces = {
        "development": "/Volumes/DATA/Agent_Turbo_Dev",
        "testing": "/Volumes/DATA/Agent_Turbo_Test",
        "experimental": "/Volumes/DATA/Agent_Turbo_Exp", 
        "backup": "/Volumes/DATA/Agent_Turbo_Backup"
    }
    
    print("Available shadow workspaces:")
    for name, path in workspaces.items():
        exists = "✅" if Path(path).exists() else "❌"
        print(f"  {exists} {name}: {path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        list_workspaces()
        sys.exit(0)
    
    workspace_name = sys.argv[1]
    success = launch_workspace(workspace_name)
    sys.exit(0 if success else 1)
'''
            
            launcher_path = Path("/Volumes/DATA/Agent_Turbo/scripts/launch_shadow_workspace.py")
            launcher_path.write_text(launcher_content)
            launcher_path.chmod(0o755)
            
            print("✅ Shadow workspace launcher created")
            return True
            
        except Exception as e:
            print(f"❌ Launcher creation failed: {e}")
            return False
    
    def create_workspace_sync_script(self) -> bool:
        """Create workspace synchronization script."""
        try:
            sync_content = '''#!/usr/bin/env python3
"""
Shadow Workspace Sync for AGENT_TURBO
Synchronizes shadow workspaces with base workspace
"""

import shutil
import json
import time
from pathlib import Path
from typing import Dict, List

class WorkspaceSync:
    """Shadow workspace synchronization."""
    
    def __init__(self):
        self.base_workspace = Path("/Volumes/DATA/Agent_Turbo")
        self.shadow_workspaces = {
            "development": Path("/Volumes/DATA/Agent_Turbo_Dev"),
            "testing": Path("/Volumes/DATA/Agent_Turbo_Test"),
            "experimental": Path("/Volumes/DATA/Agent_Turbo_Exp"),
            "backup": Path("/Volumes/DATA/Agent_Turbo_Backup")
        }
        
        # Items to sync from base to shadow
        self.sync_items = [
            "core",
            "scripts",
            "config", 
            "data",
            ".cursorrules",
            "README.md"
        ]
        
        # Items to sync from shadow to base
        self.reverse_sync_items = [
            "core",
            "scripts",
            "config"
        ]
    
    def sync_to_shadow(self, workspace_name: str) -> bool:
        """Sync from base to shadow workspace."""
        try:
            if workspace_name not in self.shadow_workspaces:
                print(f"❌ Unknown workspace: {workspace_name}")
                return False
            
            shadow_path = self.shadow_workspaces[workspace_name]
            
            if not shadow_path.exists():
                print(f"❌ Shadow workspace not found: {shadow_path}")
                return False
            
            print(f"🚀 Syncing base to {workspace_name} workspace...")
            
            for item in self.sync_items:
                src = self.base_workspace / item
                dst = shadow_path / item
                
                if src.exists():
                    if src.is_dir():
                        if dst.exists():
                            shutil.rmtree(dst)
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)
                    print(f"✅ Synced: {item}")
            
            # Update workspace config
            config_path = shadow_path / ".workspace_config.json"
            if config_path.exists():
                config = json.loads(config_path.read_text())
                config["last_sync"] = time.time()
                config["sync_direction"] = "base_to_shadow"
                config_path.write_text(json.dumps(config, indent=2))
            
            print(f"✅ Sync to {workspace_name} complete")
            return True
            
        except Exception as e:
            print(f"❌ Sync failed: {e}")
            return False
    
    def sync_to_base(self, workspace_name: str) -> bool:
        """Sync from shadow to base workspace."""
        try:
            if workspace_name not in self.shadow_workspaces:
                print(f"❌ Unknown workspace: {workspace_name}")
                return False
            
            shadow_path = self.shadow_workspaces[workspace_name]
            
            if not shadow_path.exists():
                print(f"❌ Shadow workspace not found: {shadow_path}")
                return False
            
            print(f"🚀 Syncing {workspace_name} to base workspace...")
            
            for item in self.reverse_sync_items:
                src = shadow_path / item
                dst = self.base_workspace / item
                
                if src.exists():
                    if src.is_dir():
                        if dst.exists():
                            shutil.rmtree(dst)
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)
                    print(f"✅ Synced: {item}")
            
            print(f"✅ Sync from {workspace_name} complete")
            return True
            
        except Exception as e:
            print(f"❌ Sync failed: {e}")
            return False
    
    def list_workspaces(self):
        """List all shadow workspaces and their status."""
        print("Shadow Workspaces Status:")
        for name, path in self.shadow_workspaces.items():
            exists = "✅" if path.exists() else "❌"
            print(f"  {exists} {name}: {path}")

def main():
    """Main execution."""
    import sys
    
    sync = WorkspaceSync()
    
    if len(sys.argv) < 2:
        sync.list_workspaces()
        return 0
    
    command = sys.argv[1]
    
    if command == "list":
        sync.list_workspaces()
        return 0
    elif command == "to-shadow" and len(sys.argv) >= 3:
        workspace_name = sys.argv[2]
        success = sync.sync_to_shadow(workspace_name)
        return 0 if success else 1
    elif command == "to-base" and len(sys.argv) >= 3:
        workspace_name = sys.argv[2]
        success = sync.sync_to_base(workspace_name)
        return 0 if success else 1
    else:
        print("Usage:")
        print("  python3 sync_shadow_workspaces.py list")
        print("  python3 sync_shadow_workspaces.py to-shadow <workspace_name>")
        print("  python3 sync_shadow_workspaces.py to-base <workspace_name>")
        return 1

if __name__ == "__main__":
    exit(main())
'''
            
            sync_path = Path("/Volumes/DATA/Agent_Turbo/scripts/sync_shadow_workspaces.py")
            sync_path.write_text(sync_content)
            sync_path.chmod(0o755)
            
            print("✅ Shadow workspace sync script created")
            return True
            
        except Exception as e:
            print(f"❌ Sync script creation failed: {e}")
            return False
    
    def test_shadow_workspaces(self) -> bool:
        """Test shadow workspace functionality."""
        try:
            # Test workspace launcher
            result = subprocess.run([
                "python3", "/Volumes/DATA/Agent_Turbo/scripts/launch_shadow_workspace.py"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ Shadow workspace launcher test successful")
            else:
                print(f"❌ Launcher test failed: {result.stderr}")
                return False
            
            # Test workspace sync
            result = subprocess.run([
                "python3", "/Volumes/DATA/Agent_Turbo/scripts/sync_shadow_workspaces.py", "list"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ Shadow workspace sync test successful")
                return True
            else:
                print(f"❌ Sync test failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Shadow workspace test failed: {e}")
            return False
    
    def setup_shadow_workspaces(self) -> bool:
        """Complete shadow workspace setup."""
        print("🚀 Setting up Shadow Workspaces...")
        
        # Verify shadow workspace extension
        if not self.verify_shadow_workspace_extension():
            print("❌ TASK FAILED: Shadow workspace extension not available")
            return False
        
        # Create shadow workspaces
        if not self.create_shadow_workspaces():
            print("❌ TASK FAILED: Shadow workspace creation failed")
            return False
        
        # Create launcher
        if not self.create_workspace_launcher():
            print("❌ TASK FAILED: Launcher creation failed")
            return False
        
        # Create sync script
        if not self.create_workspace_sync_script():
            print("❌ TASK FAILED: Sync script creation failed")
            return False
        
        # Test functionality
        if not self.test_shadow_workspaces():
            print("❌ TASK FAILED: Shadow workspace test failed")
            return False
        
        print("✅ Shadow workspace setup complete")
        return True

def main():
    """Main execution."""
    setup = ShadowWorkspaceSetup()
    success = setup.setup_shadow_workspaces()
    
    if success:
        print("✅ Shadow workspace implementation successful")
        return 0
    else:
        print("❌ TASK FAILED: Shadow workspace setup failed")
        return 1

if __name__ == "__main__":
    exit(main())
