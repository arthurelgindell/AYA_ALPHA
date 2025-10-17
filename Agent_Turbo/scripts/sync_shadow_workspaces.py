#!/usr/bin/env python3
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
