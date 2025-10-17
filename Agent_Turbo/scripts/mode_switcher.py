#!/usr/bin/env python3
"""
Mode Switcher for AGENT_TURBO
Switches between different custom modes
"""

import json
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Any

class ModeSwitcher:
    """Custom mode switcher."""
    
    def __init__(self):
        self.modes_dir = Path("/Volumes/DATA/Agent_Turbo/custom_modes")
        self.vscode_dir = Path("/Volumes/DATA/Agent_Turbo/.vscode")
        self.current_mode = None
        
        # Ensure .vscode directory exists
        self.vscode_dir.mkdir(exist_ok=True)
    
    def list_modes(self):
        """List available modes."""
        print("Available Custom Modes:")
        print()
        
        mode_dirs = [d for d in self.modes_dir.iterdir() if d.is_dir()]
        
        for mode_dir in mode_dirs:
            config_file = mode_dir / f"{mode_dir.name}_mode.json"
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                    
                    name = config.get("name", mode_dir.name)
                    description = config.get("description", "No description")
                    
                    print(f"  {mode_dir.name}: {name}")
                    print(f"    Description: {description}")
                    print()
                except Exception as e:
                    print(f"  {mode_dir.name}: Error reading config - {e}")
                    print()
    
    def switch_mode(self, mode_name: str) -> bool:
        """Switch to specified mode."""
        try:
            mode_dir = self.modes_dir / mode_name
            config_file = mode_dir / f"{mode_name}_mode.json"
            
            if not config_file.exists():
                print(f"❌ Mode config not found: {config_file}")
                return False
            
            # Load mode configuration
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            print(f"🚀 Switching to {config.get('name', mode_name)} mode...")
            
            # Apply settings
            settings = config.get("settings", {})
            if settings:
                settings_file = self.vscode_dir / "settings.json"
                settings_file.write_text(json.dumps(settings, indent=2))
                print("✅ Settings applied")
            
            # Apply tasks
            tasks = config.get("tasks", [])
            if tasks:
                tasks_file = self.vscode_dir / "tasks.json"
                tasks_config = {
                    "version": "2.0.0",
                    "tasks": tasks
                }
                tasks_file.write_text(json.dumps(tasks_config, indent=2))
                print("✅ Tasks applied")
            
            # Apply launch configuration
            launch = config.get("launch", {})
            if launch:
                launch_file = self.vscode_dir / "launch.json"
                launch_file.write_text(json.dumps(launch, indent=2))
                print("✅ Launch configuration applied")
            
            # Save current mode
            self.current_mode = mode_name
            mode_info_file = self.vscode_dir / "current_mode.json"
            mode_info = {
                "mode": mode_name,
                "name": config.get("name", mode_name),
                "description": config.get("description", ""),
                "switched_at": time.time()
            }
            mode_info_file.write_text(json.dumps(mode_info, indent=2))
            
            print(f"✅ Successfully switched to {config.get('name', mode_name)} mode")
            return True
            
        except Exception as e:
            print(f"❌ Mode switch failed: {e}")
            return False
    
    def get_current_mode(self) -> str:
        """Get current mode."""
        try:
            mode_info_file = self.vscode_dir / "current_mode.json"
            if mode_info_file.exists():
                with open(mode_info_file, 'r') as f:
                    mode_info = json.load(f)
                return mode_info.get("mode", "unknown")
            return "unknown"
        except Exception as e:
            print(f"❌ Failed to get current mode: {e}")
            return "unknown"
    
    def show_current_mode(self):
        """Show current mode information."""
        try:
            mode_info_file = self.vscode_dir / "current_mode.json"
            if mode_info_file.exists():
                with open(mode_info_file, 'r') as f:
                    mode_info = json.load(f)
                
                print("Current Mode:")
                print(f"  Mode: {mode_info.get('mode', 'unknown')}")
                print(f"  Name: {mode_info.get('name', 'unknown')}")
                print(f"  Description: {mode_info.get('description', 'No description')}")
                
                # Show when it was switched
                switched_at = mode_info.get('switched_at', 0)
                if switched_at > 0:
                    import time
                    time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(switched_at))
                    print(f"  Switched at: {time_str}")
            else:
                print("No mode currently active")
                
        except Exception as e:
            print(f"❌ Failed to show current mode: {e}")

def main():
    """Main execution."""
    import time
    
    switcher = ModeSwitcher()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 mode_switcher.py list")
        print("  python3 mode_switcher.py switch <mode_name>")
        print("  python3 mode_switcher.py current")
        return 1
    
    command = sys.argv[1]
    
    if command == "list":
        switcher.list_modes()
        return 0
    elif command == "switch" and len(sys.argv) >= 3:
        mode_name = sys.argv[2]
        success = switcher.switch_mode(mode_name)
        return 0 if success else 1
    elif command == "current":
        switcher.show_current_mode()
        return 0
    else:
        print("Invalid command")
        return 1

if __name__ == "__main__":
    exit(main())
