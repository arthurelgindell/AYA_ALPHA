#!/usr/bin/env python3
"""
Extension Manager for AGENT_TURBO
Manages Cursor extensions and installations
"""

import subprocess
import json
import sys
from pathlib import Path
from typing import Dict, List, Any

class ExtensionManager:
    """Extension management system."""
    
    def __init__(self):
        self.extensions_dir = Path("/Volumes/DATA/Agent_Turbo/extensions")
        self.config_path = self.extensions_dir / "extension_config.json"
        
        # Load configuration
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {}
    
    def list_installed_extensions(self) -> List[Dict[str, str]]:
        """List installed extensions."""
        try:
            result = subprocess.run([
                "cursor",
                "--list-extensions"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"❌ Failed to list extensions: {result.stderr}")
                return []
            
            extensions = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('.')
                    if len(parts) >= 2:
                        publisher = parts[0]
                        name = '.'.join(parts[1:])
                        extensions.append({
                            "name": name,
                            "publisher": publisher,
                            "full_name": line
                        })
            
            return extensions
            
        except Exception as e:
            print(f"❌ Failed to list extensions: {e}")
            return []
    
    def install_extension(self, extension_name: str, publisher: str = None) -> bool:
        """Install extension."""
        try:
            if publisher:
                full_name = f"{publisher}.{extension_name}"
            else:
                full_name = extension_name
            
            print(f"🚀 Installing extension: {full_name}")
            
            result = subprocess.run([
                "cursor",
                "--install-extension",
                full_name
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"✅ Extension installed: {full_name}")
                return True
            else:
                print(f"❌ Extension installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Extension installation failed: {e}")
            return False
    
    def uninstall_extension(self, extension_name: str, publisher: str = None) -> bool:
        """Uninstall extension."""
        try:
            if publisher:
                full_name = f"{publisher}.{extension_name}"
            else:
                full_name = extension_name
            
            print(f"🚀 Uninstalling extension: {full_name}")
            
            result = subprocess.run([
                "cursor",
                "--uninstall-extension",
                full_name
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"✅ Extension uninstalled: {full_name}")
                return True
            else:
                print(f"❌ Extension uninstallation failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Extension uninstallation failed: {e}")
            return False
    
    def update_extensions(self) -> bool:
        """Update all extensions."""
        try:
            print("🚀 Updating extensions...")
            
            result = subprocess.run([
                "cursor",
                "--update-extensions"
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print("✅ Extensions updated")
                return True
            else:
                print(f"❌ Extension update failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Extension update failed: {e}")
            return False
    
    def show_extension_info(self, extension_name: str, publisher: str = None):
        """Show extension information."""
        try:
            if publisher:
                full_name = f"{publisher}.{extension_name}"
            else:
                full_name = extension_name
            
            print(f"Extension: {full_name}")
            
            # Check if installed
            installed_extensions = self.list_installed_extensions()
            is_installed = any(ext["full_name"] == full_name for ext in installed_extensions)
            
            print(f"Status: {'Installed' if is_installed else 'Not installed'}")
            
            # Show recommended extensions info
            recommended = self.config.get("recommended_extensions", [])
            for ext in recommended:
                if ext.get("name") == extension_name and ext.get("publisher") == publisher:
                    print(f"Description: {ext.get('description', 'N/A')}")
                    print(f"Category: {ext.get('category', 'N/A')}")
                    break
            
        except Exception as e:
            print(f"❌ Failed to show extension info: {e}")
    
    def list_recommended_extensions(self):
        """List recommended extensions."""
        try:
            recommended = self.config.get("recommended_extensions", [])
            installed_extensions = self.list_installed_extensions()
            installed_names = [ext["full_name"] for ext in installed_extensions]
            
            print("Recommended Extensions:")
            print()
            
            for ext in recommended:
                name = ext.get("name")
                publisher = ext.get("publisher")
                description = ext.get("description", "")
                category = ext.get("category", "")
                
                full_name = f"{publisher}.{name}"
                status = "✅ Installed" if full_name in installed_names else "❌ Not installed"
                
                print(f"{status} {full_name}")
                print(f"    Description: {description}")
                print(f"    Category: {category}")
                print()
                
        except Exception as e:
            print(f"❌ Failed to list recommended extensions: {e}")

def main():
    """Main execution."""
    manager = ExtensionManager()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 extension_manager.py list")
        print("  python3 extension_manager.py install <name> [publisher]")
        print("  python3 extension_manager.py uninstall <name> [publisher]")
        print("  python3 extension_manager.py update")
        print("  python3 extension_manager.py info <name> [publisher]")
        print("  python3 extension_manager.py recommended")
        return 1
    
    command = sys.argv[1]
    
    if command == "list":
        extensions = manager.list_installed_extensions()
        print(f"Installed Extensions ({len(extensions)}):")
        for ext in extensions:
            print(f"  {ext['full_name']}")
        return 0
    elif command == "install" and len(sys.argv) >= 3:
        name = sys.argv[2]
        publisher = sys.argv[3] if len(sys.argv) > 3 else None
        success = manager.install_extension(name, publisher)
        return 0 if success else 1
    elif command == "uninstall" and len(sys.argv) >= 3:
        name = sys.argv[2]
        publisher = sys.argv[3] if len(sys.argv) > 3 else None
        success = manager.uninstall_extension(name, publisher)
        return 0 if success else 1
    elif command == "update":
        success = manager.update_extensions()
        return 0 if success else 1
    elif command == "info" and len(sys.argv) >= 3:
        name = sys.argv[2]
        publisher = sys.argv[3] if len(sys.argv) > 3 else None
        manager.show_extension_info(name, publisher)
        return 0
    elif command == "recommended":
        manager.list_recommended_extensions()
        return 0
    else:
        print("Invalid command")
        return 1

if __name__ == "__main__":
    exit(main())
