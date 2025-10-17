#!/usr/bin/env python3
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
