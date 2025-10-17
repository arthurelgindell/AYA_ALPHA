#!/usr/bin/env python3
"""
Deep Linking Setup for AGENT_TURBO
Implements cursor-deeplink for direct navigation to specific code locations
GAMMA Project - Prime Directives Compliance
"""

import subprocess
import json
import time
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

class DeepLinkingSetup:
    """Deep linking setup for Cursor."""
    
    def __init__(self):
        self.deeplink_dir = Path("/Volumes/DATA/Agent_Turbo/deep_links")
        self.links_config = {}
        self.status = {
            "deeplink_available": False,
            "links_configured": False,
            "navigation_ready": False
        }
        
    def verify_deeplink_extension(self) -> bool:
        """Verify deeplink extension is available."""
        try:
            deeplink_path = Path("/Applications/Cursor.app/Contents/Resources/app/extensions/cursor-deeplink")
            deeplink_exists = deeplink_path.exists()
            print(f"✅ Deep Link Extension: {'Available' if deeplink_exists else 'Missing'}")
            
            if deeplink_exists:
                self.status["deeplink_available"] = True
                
            return deeplink_exists
        except Exception as e:
            print(f"❌ Deep link verification failed: {e}")
            return False
    
    def create_deeplink_directories(self) -> bool:
        """Create deep linking directories."""
        try:
            directories = [
                self.deeplink_dir,
                self.deeplink_dir / "bookmarks",
                self.deeplink_dir / "shortcuts",
                self.deeplink_dir / "navigation",
                self.deeplink_dir / "templates"
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created directory: {directory}")
            
            return True
            
        except Exception as e:
            print(f"❌ Deep link directory creation failed: {e}")
            return False
    
    def create_deeplink_config(self) -> bool:
        """Create deep linking configuration."""
        try:
            config_content = {
                "deeplinks": {
                    "enabled": True,
                    "auto_generate": True,
                    "bookmark_support": True,
                    "shortcut_support": True
                },
                "navigation": {
                    "quick_access": True,
                    "context_aware": True,
                    "history_tracking": True
                },
                "bookmarks": {
                    "max_bookmarks": 100,
                    "auto_save": True,
                    "categories": ["core", "scripts", "config", "docs"]
                },
                "shortcuts": {
                    "max_shortcuts": 50,
                    "keyboard_support": True,
                    "command_palette": True
                }
            }
            
            config_path = self.deeplink_dir / "deeplink_config.json"
            config_path.write_text(json.dumps(config_content, indent=2))
            
            print("✅ Deep link configuration created")
            return True
            
        except Exception as e:
            print(f"❌ Deep link config creation failed: {e}")
            return False
    
    def create_bookmark_manager(self) -> bool:
        """Create bookmark manager for deep linking."""
        try:
            manager_content = '''#!/usr/bin/env python3
"""
Bookmark Manager for AGENT_TURBO
Manages bookmarks and deep links for quick navigation
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any

class BookmarkManager:
    """Bookmark management system."""
    
    def __init__(self):
        self.deeplink_dir = Path("/Volumes/DATA/Agent_Turbo/deep_links")
        self.bookmarks_file = self.deeplink_dir / "bookmarks" / "bookmarks.json"
        self.config_file = self.deeplink_dir / "deeplink_config.json"
        
        # Load configuration
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {}
        
        # Load bookmarks
        if self.bookmarks_file.exists():
            with open(self.bookmarks_file, 'r') as f:
                self.bookmarks = json.load(f)
        else:
            self.bookmarks = {"bookmarks": [], "categories": {}}
    
    def add_bookmark(self, name: str, path: str, line: int = 1, category: str = "general") -> bool:
        """Add a new bookmark."""
        try:
            bookmark = {
                "name": name,
                "path": path,
                "line": line,
                "category": category,
                "created_at": time.time(),
                "deeplink": f"cursor://file/{path}:{line}"
            }
            
            self.bookmarks["bookmarks"].append(bookmark)
            
            # Update categories
            if category not in self.bookmarks["categories"]:
                self.bookmarks["categories"][category] = []
            self.bookmarks["categories"][category].append(name)
            
            # Save bookmarks
            self.bookmarks_file.write_text(json.dumps(self.bookmarks, indent=2))
            
            print(f"✅ Bookmark added: {name} -> {path}:{line}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to add bookmark: {e}")
            return False
    
    def remove_bookmark(self, name: str) -> bool:
        """Remove a bookmark."""
        try:
            # Find and remove bookmark
            for i, bookmark in enumerate(self.bookmarks["bookmarks"]):
                if bookmark["name"] == name:
                    category = bookmark["category"]
                    
                    # Remove from bookmarks list
                    del self.bookmarks["bookmarks"][i]
                    
                    # Remove from category
                    if category in self.bookmarks["categories"]:
                        if name in self.bookmarks["categories"][category]:
                            self.bookmarks["categories"][category].remove(name)
                    
                    # Save bookmarks
                    self.bookmarks_file.write_text(json.dumps(self.bookmarks, indent=2))
                    
                    print(f"✅ Bookmark removed: {name}")
                    return True
            
            print(f"❌ Bookmark not found: {name}")
            return False
            
        except Exception as e:
            print(f"❌ Failed to remove bookmark: {e}")
            return False
    
    def list_bookmarks(self, category: str = None):
        """List bookmarks."""
        try:
            if category:
                bookmarks = [b for b in self.bookmarks["bookmarks"] if b["category"] == category]
                print(f"Bookmarks in category '{category}':")
            else:
                bookmarks = self.bookmarks["bookmarks"]
                print("All bookmarks:")
            
            if not bookmarks:
                print("  No bookmarks found")
                return
            
            for bookmark in bookmarks:
                print(f"  {bookmark['name']}")
                print(f"    Path: {bookmark['path']}")
                print(f"    Line: {bookmark['line']}")
                print(f"    Category: {bookmark['category']}")
                print(f"    Deeplink: {bookmark['deeplink']}")
                print()
                
        except Exception as e:
            print(f"❌ Failed to list bookmarks: {e}")
    
    def get_bookmark(self, name: str) -> Dict[str, Any]:
        """Get bookmark by name."""
        try:
            for bookmark in self.bookmarks["bookmarks"]:
                if bookmark["name"] == name:
                    return bookmark
            return {}
        except Exception as e:
            print(f"❌ Failed to get bookmark: {e}")
            return {}
    
    def generate_deeplink(self, path: str, line: int = 1) -> str:
        """Generate deeplink for path and line."""
        try:
            # Convert to absolute path
            abs_path = Path(path).resolve()
            deeplink = f"cursor://file/{abs_path}:{line}"
            return deeplink
        except Exception as e:
            print(f"❌ Failed to generate deeplink: {e}")
            return ""
    
    def open_bookmark(self, name: str) -> bool:
        """Open bookmark in Cursor."""
        try:
            bookmark = self.get_bookmark(name)
            if not bookmark:
                print(f"❌ Bookmark not found: {name}")
                return False
            
            deeplink = bookmark["deeplink"]
            print(f"🚀 Opening bookmark: {name}")
            print(f"   Deeplink: {deeplink}")
            
            # Open in Cursor
            import subprocess
            result = subprocess.run(["cursor", deeplink], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ Bookmark opened successfully")
                return True
            else:
                print(f"❌ Failed to open bookmark: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to open bookmark: {e}")
            return False
    
    def create_agent_turbo_bookmarks(self) -> bool:
        """Create default Agent Turbo bookmarks."""
        try:
            default_bookmarks = [
                {
                    "name": "Agent Turbo Core",
                    "path": "/Volumes/DATA/Agent_Turbo/core/agent_turbo.py",
                    "line": 1,
                    "category": "core"
                },
                {
                    "name": "Agent Turbo GPU",
                    "path": "/Volumes/DATA/Agent_Turbo/core/agent_turbo_gpu.py",
                    "line": 1,
                    "category": "core"
                },
                {
                    "name": "LM Studio Client",
                    "path": "/Volumes/DATA/Agent_Turbo/core/lm_studio_client.py",
                    "line": 1,
                    "category": "core"
                },
                {
                    "name": "Cursor Integration",
                    "path": "/Volumes/DATA/Agent_Turbo/scripts/verify_cursor_integration.py",
                    "line": 1,
                    "category": "scripts"
                },
                {
                    "name": "Prime Directives",
                    "path": "/Volumes/DATA/Agent_Turbo/scripts/verify_prime_directives.py",
                    "line": 1,
                    "category": "scripts"
                },
                {
                    "name": "Performance Benchmark",
                    "path": "/Volumes/DATA/Agent_Turbo/scripts/performance_benchmark.py",
                    "line": 1,
                    "category": "scripts"
                },
                {
                    "name": "Cursor Rules",
                    "path": "/Volumes/DATA/Agent_Turbo/.cursorrules",
                    "line": 1,
                    "category": "config"
                },
                {
                    "name": "Integration Status",
                    "path": "/Volumes/DATA/Agent_Turbo/documents/CURSOR_INTEGRATION_STATUS.md",
                    "line": 1,
                    "category": "docs"
                }
            ]
            
            for bookmark in default_bookmarks:
                self.add_bookmark(
                    bookmark["name"],
                    bookmark["path"],
                    bookmark["line"],
                    bookmark["category"]
                )
            
            print("✅ Default Agent Turbo bookmarks created")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create default bookmarks: {e}")
            return False

def main():
    """Main execution."""
    manager = BookmarkManager()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 bookmark_manager.py add <name> <path> [line] [category]")
        print("  python3 bookmark_manager.py remove <name>")
        print("  python3 bookmark_manager.py list [category]")
        print("  python3 bookmark_manager.py open <name>")
        print("  python3 bookmark_manager.py deeplink <path> [line]")
        print("  python3 bookmark_manager.py init")
        return 1
    
    command = sys.argv[1]
    
    if command == "add" and len(sys.argv) >= 4:
        name = sys.argv[2]
        path = sys.argv[3]
        line = int(sys.argv[4]) if len(sys.argv) > 4 else 1
        category = sys.argv[5] if len(sys.argv) > 5 else "general"
        success = manager.add_bookmark(name, path, line, category)
        return 0 if success else 1
    elif command == "remove" and len(sys.argv) >= 3:
        name = sys.argv[2]
        success = manager.remove_bookmark(name)
        return 0 if success else 1
    elif command == "list":
        category = sys.argv[2] if len(sys.argv) > 2 else None
        manager.list_bookmarks(category)
        return 0
    elif command == "open" and len(sys.argv) >= 3:
        name = sys.argv[2]
        success = manager.open_bookmark(name)
        return 0 if success else 1
    elif command == "deeplink" and len(sys.argv) >= 3:
        path = sys.argv[2]
        line = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        deeplink = manager.generate_deeplink(path, line)
        print(deeplink)
        return 0
    elif command == "init":
        success = manager.create_agent_turbo_bookmarks()
        return 0 if success else 1
    else:
        print("Invalid command")
        return 1

if __name__ == "__main__":
    exit(main())
'''
            
            manager_path = Path("/Volumes/DATA/Agent_Turbo/scripts/bookmark_manager.py")
            manager_path.write_text(manager_content)
            manager_path.chmod(0o755)
            
            print("✅ Bookmark manager created")
            return True
            
        except Exception as e:
            print(f"❌ Bookmark manager creation failed: {e}")
            return False
    
    def create_shortcut_manager(self) -> bool:
        """Create shortcut manager for deep linking."""
        try:
            shortcut_content = '''#!/usr/bin/env python3
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
                            "text": f"{shortcut['command']}\\r"
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
'''
            
            shortcut_path = Path("/Volumes/DATA/Agent_Turbo/scripts/shortcut_manager.py")
            shortcut_path.write_text(shortcut_content)
            shortcut_path.chmod(0o755)
            
            print("✅ Shortcut manager created")
            return True
            
        except Exception as e:
            print(f"❌ Shortcut manager creation failed: {e}")
            return False
    
    def test_deep_linking(self) -> bool:
        """Test deep linking functionality."""
        try:
            # Test bookmark manager
            result = subprocess.run([
                "python3", "/Volumes/DATA/Agent_Turbo/scripts/bookmark_manager.py", "init"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Bookmark manager test successful")
            else:
                print(f"❌ Bookmark manager test failed: {result.stderr}")
                return False
            
            # Test shortcut manager
            result = subprocess.run([
                "python3", "/Volumes/DATA/Agent_Turbo/scripts/shortcut_manager.py", "init"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Shortcut manager test successful")
                return True
            else:
                print(f"❌ Shortcut manager test failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Deep linking test failed: {e}")
            return False
    
    def setup_deep_linking(self) -> bool:
        """Complete deep linking setup."""
        print("🚀 Setting up Deep Linking...")
        
        # Verify deeplink extension
        if not self.verify_deeplink_extension():
            print("❌ TASK FAILED: Deep link extension not available")
            return False
        
        # Create deeplink directories
        if not self.create_deeplink_directories():
            print("❌ TASK FAILED: Deep link directory creation failed")
            return False
        
        # Create deeplink config
        if not self.create_deeplink_config():
            print("❌ TASK FAILED: Deep link config creation failed")
            return False
        
        # Create bookmark manager
        if not self.create_bookmark_manager():
            print("❌ TASK FAILED: Bookmark manager creation failed")
            return False
        
        # Create shortcut manager
        if not self.create_shortcut_manager():
            print("❌ TASK FAILED: Shortcut manager creation failed")
            return False
        
        # Test deep linking
        if not self.test_deep_linking():
            print("❌ TASK FAILED: Deep linking test failed")
            return False
        
        self.status["links_configured"] = True
        self.status["navigation_ready"] = True
        
        print("✅ Deep linking setup complete")
        return True

def main():
    """Main execution."""
    setup = DeepLinkingSetup()
    success = setup.setup_deep_linking()
    
    if success:
        print("✅ Deep linking implementation successful")
        return 0
    else:
        print("❌ TASK FAILED: Deep linking setup failed")
        return 1

if __name__ == "__main__":
    exit(main())
