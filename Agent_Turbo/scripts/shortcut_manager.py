#!/usr/bin/env python3
"""
Shortcut Manager for AGENT_TURBO
Manages keyboard shortcuts and command palette entries for deep linking
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any

class ShortcutManager:
    """Shortcut management system."""
    
    def __init__(self):
        self.deeplink_dir = Path("/Volumes/DATA/Agent_Turbo/deep_links")
        self.shortcuts_file = self.deeplink_dir / "shortcuts" / "shortcuts.json"
        self.config_file = self.deeplink_dir / "deeplink_config.json"
        
        # Load configuration
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {}
        
        # Load shortcuts
        if self.shortcuts_file.exists():
            with open(self.shortcuts_file, 'r') as f:
                self.shortcuts = json.load(f)
        else:
            self.shortcuts = {"shortcuts": [], "keybindings": []}
    
    def add_shortcut(self, name: str, command: str, keybinding: str = None, category: str = "general") -> bool:
        """Add a new shortcut."""
        try:
            shortcut = {
                "name": name,
                "command": command,
                "keybinding": keybinding,
                "category": category,
                "created_at": time.time()
            }
            
            self.shortcuts["shortcuts"].append(shortcut)
            
            # Add keybinding if provided
            if keybinding:
                keybinding_config = {
                    "key": keybinding,
                    "command": command,
                    "when": "editorTextFocus"
                }
                self.shortcuts["keybindings"].append(keybinding_config)
            
            # Save shortcuts
            self.shortcuts_file.write_text(json.dumps(self.shortcuts, indent=2))
            
            print(f"✅ Shortcut added: {name} -> {command}")
            if keybinding:
                print(f"   Keybinding: {keybinding}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to add shortcut: {e}")
            return False
    
    def remove_shortcut(self, name: str) -> bool:
        """Remove a shortcut."""
        try:
            # Find and remove shortcut
            for i, shortcut in enumerate(self.shortcuts["shortcuts"]):
                if shortcut["name"] == name:
                    # Remove from shortcuts list
                    del self.shortcuts["shortcuts"][i]
                    
                    # Remove associated keybinding
                    if shortcut["keybinding"]:
                        for j, keybinding in enumerate(self.shortcuts["keybindings"]):
                            if keybinding["key"] == shortcut["keybinding"]:
                                del self.shortcuts["keybindings"][j]
                                break
                    
                    # Save shortcuts
                    self.shortcuts_file.write_text(json.dumps(self.shortcuts, indent=2))
                    
                    print(f"✅ Shortcut removed: {name}")
                    return True
            
            print(f"❌ Shortcut not found: {name}")
            return False
            
        except Exception as e:
            print(f"❌ Failed to remove shortcut: {e}")
            return False
    
    def list_shortcuts(self, category: str = None):
        """List shortcuts."""
        try:
            if category:
                shortcuts = [s for s in self.shortcuts["shortcuts"] if s["category"] == category]
                print(f"Shortcuts in category '{category}':")
            else:
                shortcuts = self.shortcuts["shortcuts"]
                print("All shortcuts:")
            
            if not shortcuts:
                print("  No shortcuts found")
                return
            
            for shortcut in shortcuts:
                print(f"  {shortcut['name']}")
                print(f"    Command: {shortcut['command']}")
                if shortcut['keybinding']:
                    print(f"    Keybinding: {shortcut['keybinding']}")
                print(f"    Category: {shortcut['category']}")
                print()
                
        except Exception as e:
            print(f"❌ Failed to list shortcuts: {e}")
    
    def create_agent_turbo_shortcuts(self) -> bool:
        """Create default Agent Turbo shortcuts."""
        try:
            default_shortcuts = [
                {
                    "name": "Open Agent Turbo Core",
                    "command": "cursor /Volumes/DATA/Agent_Turbo/core/agent_turbo.py",
                    "keybinding": "ctrl+shift+t",
                    "category": "core"
                },
                {
                    "name": "Open Agent Turbo GPU",
                    "command": "cursor /Volumes/DATA/Agent_Turbo/core/agent_turbo_gpu.py",
                    "keybinding": "ctrl+shift+g",
                    "category": "core"
                },
                {
                    "name": "Run Agent Turbo Verification",
                    "command": "python3 /Volumes/DATA/Agent_Turbo/core/agent_turbo.py verify",
                    "keybinding": "ctrl+shift+v",
                    "category": "scripts"
                },
                {
                    "name": "Run Agent Turbo Stats",
                    "command": "python3 /Volumes/DATA/Agent_Turbo/core/agent_turbo.py stats",
                    "keybinding": "ctrl+shift+s",
                    "category": "scripts"
                },
                {
                    "name": "Open Cursor Rules",
                    "command": "cursor /Volumes/DATA/Agent_Turbo/.cursorrules",
                    "keybinding": "ctrl+shift+r",
                    "category": "config"
                },
                {
                    "name": "Open Integration Status",
                    "command": "cursor /Volumes/DATA/Agent_Turbo/documents/CURSOR_INTEGRATION_STATUS.md",
                    "keybinding": "ctrl+shift+i",
                    "category": "docs"
                }
            ]
            
            for shortcut in default_shortcuts:
                self.add_shortcut(
                    shortcut["name"],
                    shortcut["command"],
                    shortcut["keybinding"],
                    shortcut["category"]
                )
            
            print("✅ Default Agent Turbo shortcuts created")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create default shortcuts: {e}")
            return False
    
    def generate_keybindings_json(self) -> bool:
        """Generate keybindings.json for Cursor."""
        try:
            keybindings = []
            
            for shortcut in self.shortcuts["shortcuts"]:
                if shortcut["keybinding"]:
                    keybinding = {
                        "key": shortcut["keybinding"],
                        "command": "workbench.action.terminal.sendSequence",
                        "args": {
                            "text": f"{shortcut['command']}\r"
                        },
                        "when": "terminalFocus"
                    }
                    keybindings.append(keybinding)
            
            # Save keybindings
            keybindings_path = Path("/Volumes/DATA/Agent_Turbo/.vscode/keybindings.json")
            keybindings_path.parent.mkdir(exist_ok=True)
            keybindings_path.write_text(json.dumps(keybindings, indent=2))
            
            print("✅ Keybindings.json generated")
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate keybindings: {e}")
            return False

def main():
    """Main execution."""
    manager = ShortcutManager()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 shortcut_manager.py add <name> <command> [keybinding] [category]")
        print("  python3 shortcut_manager.py remove <name>")
        print("  python3 shortcut_manager.py list [category]")
        print("  python3 shortcut_manager.py init")
        print("  python3 shortcut_manager.py generate")
        return 1
    
    command = sys.argv[1]
    
    if command == "add" and len(sys.argv) >= 4:
        name = sys.argv[2]
        command = sys.argv[3]
        keybinding = sys.argv[4] if len(sys.argv) > 4 else None
        category = sys.argv[5] if len(sys.argv) > 5 else "general"
        success = manager.add_shortcut(name, command, keybinding, category)
        return 0 if success else 1
    elif command == "remove" and len(sys.argv) >= 3:
        name = sys.argv[2]
        success = manager.remove_shortcut(name)
        return 0 if success else 1
    elif command == "list":
        category = sys.argv[2] if len(sys.argv) > 2 else None
        manager.list_shortcuts(category)
        return 0
    elif command == "init":
        success = manager.create_agent_turbo_shortcuts()
        return 0 if success else 1
    elif command == "generate":
        success = manager.generate_keybindings_json()
        return 0 if success else 1
    else:
        print("Invalid command")
        return 1

if __name__ == "__main__":
    exit(main())
