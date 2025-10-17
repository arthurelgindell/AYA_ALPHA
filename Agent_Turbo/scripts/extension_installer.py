#!/usr/bin/env python3
"""
Extension Installer for AGENT_TURBO
Installs specialized extensions from marketplace for enhanced functionality
GAMMA Project - Prime Directives Compliance
"""

import subprocess
import json
import time
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

class ExtensionInstaller:
    """Extension installer for Cursor."""
    
    def __init__(self):
        self.extensions_dir = Path("/Volumes/DATA/Agent_Turbo/extensions")
        self.installed_extensions = []
        self.status = {
            "extensions_available": 0,
            "extensions_installed": 0,
            "installation_successful": False
        }
        
    def get_available_extensions(self) -> List[Dict[str, str]]:
        """Get list of available extensions."""
        try:
            # Get built-in extensions
            extensions_path = Path("/Applications/Cursor.app/Contents/Resources/app/extensions")
            extensions = []
            
            for ext_dir in extensions_path.iterdir():
                if ext_dir.is_dir():
                    package_json = ext_dir / "package.json"
                    if package_json.exists():
                        try:
                            with open(package_json, 'r') as f:
                                package_data = json.load(f)
                            
                            extensions.append({
                                "name": package_data.get("name", ext_dir.name),
                                "displayName": package_data.get("displayName", ext_dir.name),
                                "description": package_data.get("description", ""),
                                "version": package_data.get("version", "1.0.0"),
                                "publisher": package_data.get("publisher", "unknown"),
                                "path": str(ext_dir)
                            })
                        except Exception as e:
                            print(f"⚠️  Failed to read {package_json}: {e}")
            
            self.status["extensions_available"] = len(extensions)
            return extensions
            
        except Exception as e:
            print(f"❌ Failed to get available extensions: {e}")
            return []
    
    def create_extension_config(self) -> bool:
        """Create extension configuration."""
        try:
            config_content = {
                "extensions": {
                    "enabled": True,
                    "auto_update": True,
                    "marketplace_access": True
                },
                "recommended_extensions": [
                    {
                        "name": "python",
                        "publisher": "ms-python",
                        "description": "Python language support",
                        "category": "language"
                    },
                    {
                        "name": "javascript",
                        "publisher": "ms-vscode",
                        "description": "JavaScript language support",
                        "category": "language"
                    },
                    {
                        "name": "typescript",
                        "publisher": "ms-vscode",
                        "description": "TypeScript language support",
                        "category": "language"
                    },
                    {
                        "name": "rust",
                        "publisher": "rust-lang",
                        "description": "Rust language support",
                        "category": "language"
                    },
                    {
                        "name": "go",
                        "publisher": "golang",
                        "description": "Go language support",
                        "category": "language"
                    },
                    {
                        "name": "java",
                        "publisher": "redhat",
                        "description": "Java language support",
                        "category": "language"
                    },
                    {
                        "name": "docker",
                        "publisher": "ms-azuretools",
                        "description": "Docker container support",
                        "category": "development"
                    },
                    {
                        "name": "gitlens",
                        "publisher": "eamodio",
                        "description": "Git supercharged",
                        "category": "git"
                    },
                    {
                        "name": "prettier",
                        "publisher": "esbenp",
                        "description": "Code formatter",
                        "category": "formatting"
                    },
                    {
                        "name": "eslint",
                        "publisher": "dbaeumer",
                        "description": "JavaScript linter",
                        "category": "linting"
                    }
                ],
                "categories": {
                    "language": "Programming language support",
                    "development": "Development tools",
                    "git": "Git integration",
                    "formatting": "Code formatting",
                    "linting": "Code linting",
                    "debugging": "Debugging tools",
                    "testing": "Testing frameworks",
                    "productivity": "Productivity tools"
                }
            }
            
            config_path = self.extensions_dir / "extension_config.json"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(json.dumps(config_content, indent=2))
            
            print("✅ Extension configuration created")
            return True
            
        except Exception as e:
            print(f"❌ Extension config creation failed: {e}")
            return False
    
    def install_extension(self, extension_name: str, publisher: str = None) -> bool:
        """Install extension from marketplace."""
        try:
            if publisher:
                full_name = f"{publisher}.{extension_name}"
            else:
                full_name = extension_name
            
            print(f"🚀 Installing extension: {full_name}")
            
            # Install extension using Cursor CLI
            result = subprocess.run([
                "cursor",
                "--install-extension",
                full_name
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"✅ Extension installed: {full_name}")
                self.installed_extensions.append(full_name)
                return True
            else:
                print(f"❌ Extension installation failed: {full_name}")
                print(f"Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Extension installation failed: {e}")
            return False
    
    def install_recommended_extensions(self) -> bool:
        """Install recommended extensions."""
        try:
            config_path = self.extensions_dir / "extension_config.json"
            if not config_path.exists():
                print("❌ Extension config not found")
                return False
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            recommended = config.get("recommended_extensions", [])
            installed_count = 0
            
            for ext in recommended:
                name = ext.get("name")
                publisher = ext.get("publisher")
                description = ext.get("description", "")
                
                if self.install_extension(name, publisher):
                    installed_count += 1
                    print(f"✅ Installed: {name} - {description}")
                else:
                    print(f"❌ Failed to install: {name}")
            
            self.status["extensions_installed"] = installed_count
            print(f"✅ Installed {installed_count}/{len(recommended)} recommended extensions")
            return installed_count > 0
            
        except Exception as e:
            print(f"❌ Recommended extensions installation failed: {e}")
            return False
    
    def create_extension_manager(self) -> bool:
        """Create extension management script."""
        try:
            manager_content = '''#!/usr/bin/env python3
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
            for line in result.stdout.strip().split('\\n'):
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
'''
            
            manager_path = Path("/Volumes/DATA/Agent_Turbo/scripts/extension_manager.py")
            manager_path.write_text(manager_content)
            manager_path.chmod(0o755)
            
            print("✅ Extension manager created")
            return True
            
        except Exception as e:
            print(f"❌ Extension manager creation failed: {e}")
            return False
    
    def test_extension_system(self) -> bool:
        """Test extension system functionality."""
        try:
            # Test extension manager
            result = subprocess.run([
                "python3", "/Volumes/DATA/Agent_Turbo/scripts/extension_manager.py", "list"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Extension manager test successful")
                return True
            else:
                print(f"❌ Extension manager test failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Extension system test failed: {e}")
            return False
    
    def setup_extensions(self) -> bool:
        """Complete extension setup."""
        print("🚀 Setting up Extensions...")
        
        # Get available extensions
        available_extensions = self.get_available_extensions()
        print(f"✅ Found {len(available_extensions)} available extensions")
        
        # Create extension config
        if not self.create_extension_config():
            print("❌ TASK FAILED: Extension config creation failed")
            return False
        
        # Create extension manager
        if not self.create_extension_manager():
            print("❌ TASK FAILED: Extension manager creation failed")
            return False
        
        # Install recommended extensions
        if not self.install_recommended_extensions():
            print("❌ TASK FAILED: Recommended extensions installation failed")
            return False
        
        # Test extension system
        if not self.test_extension_system():
            print("❌ TASK FAILED: Extension system test failed")
            return False
        
        print("✅ Extension setup complete")
        return True

def main():
    """Main execution."""
    installer = ExtensionInstaller()
    success = installer.setup_extensions()
    
    if success:
        print("✅ Extension implementation successful")
        return 0
    else:
        print("❌ TASK FAILED: Extension setup failed")
        return 1

if __name__ == "__main__":
    exit(main())
