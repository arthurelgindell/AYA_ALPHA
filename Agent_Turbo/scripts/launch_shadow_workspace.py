#!/usr/bin/env python3
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
