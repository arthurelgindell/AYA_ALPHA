#!/usr/bin/env python3
"""
Custom Modes Setup for AGENT_TURBO
Creates custom modes for specialized workflows
GAMMA Project - Prime Directives Compliance
"""

import subprocess
import json
import time
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

class CustomModesSetup:
    """Custom modes setup for Cursor."""
    
    def __init__(self):
        self.modes_dir = Path("/Volumes/DATA/Agent_Turbo/custom_modes")
        self.modes_config = {}
        self.status = {
            "modes_created": 0,
            "modes_configured": False,
            "workflows_ready": False
        }
        
    def create_modes_directories(self) -> bool:
        """Create custom modes directories."""
        try:
            directories = [
                self.modes_dir,
                self.modes_dir / "development",
                self.modes_dir / "testing",
                self.modes_dir / "debugging",
                self.modes_dir / "documentation",
                self.modes_dir / "performance",
                self.modes_dir / "deployment",
                self.modes_dir / "maintenance"
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created directory: {directory}")
            
            return True
            
        except Exception as e:
            print(f"❌ Modes directory creation failed: {e}")
            return False
    
    def create_development_mode(self) -> bool:
        """Create development mode configuration."""
        try:
            mode_config = {
                "name": "Development Mode",
                "description": "Optimized for active development and coding",
                "settings": {
                    "editor.fontSize": 14,
                    "editor.tabSize": 4,
                    "editor.insertSpaces": True,
                    "editor.wordWrap": "on",
                    "editor.minimap.enabled": True,
                    "editor.bracketPairColorization.enabled": True,
                    "editor.guides.bracketPairs": True,
                    "editor.suggest.showKeywords": True,
                    "editor.suggest.showSnippets": True,
                    "editor.quickSuggestions": {
                        "other": True,
                        "comments": False,
                        "strings": True
                    },
                    "files.autoSave": "afterDelay",
                    "files.autoSaveDelay": 1000,
                    "terminal.integrated.fontSize": 12,
                    "workbench.colorTheme": "Default Dark+",
                    "workbench.iconTheme": "vs-seti"
                },
                "extensions": [
                    "ms-python.python",
                    "ms-vscode.vscode-typescript-next",
                    "eamodio.gitlens",
                    "ms-vscode.vscode-json"
                ],
                "tasks": [
                    {
                        "label": "Run Agent Turbo Verification",
                        "type": "shell",
                        "command": "python3",
                        "args": ["/Volumes/DATA/Agent_Turbo/core/agent_turbo.py", "verify"],
                        "group": "build"
                    },
                    {
                        "label": "Run Agent Turbo Stats",
                        "type": "shell",
                        "command": "python3",
                        "args": ["/Volumes/DATA/Agent_Turbo/core/agent_turbo.py", "stats"],
                        "group": "build"
                    }
                ],
                "launch": {
                    "version": "0.2.0",
                    "configurations": [
                        {
                            "name": "Debug Agent Turbo",
                            "type": "python",
                            "request": "launch",
                            "program": "/Volumes/DATA/Agent_Turbo/core/agent_turbo.py",
                            "args": ["verify"],
                            "console": "integratedTerminal"
                        }
                    ]
                }
            }
            
            config_path = self.modes_dir / "development" / "development_mode.json"
            config_path.write_text(json.dumps(mode_config, indent=2))
            
            print("✅ Development mode created")
            return True
            
        except Exception as e:
            print(f"❌ Development mode creation failed: {e}")
            return False
    
    def create_testing_mode(self) -> bool:
        """Create testing mode configuration."""
        try:
            mode_config = {
                "name": "Testing Mode",
                "description": "Optimized for testing and validation",
                "settings": {
                    "editor.fontSize": 13,
                    "editor.tabSize": 2,
                    "editor.insertSpaces": True,
                    "editor.wordWrap": "off",
                    "editor.minimap.enabled": False,
                    "editor.bracketPairColorization.enabled": True,
                    "editor.guides.bracketPairs": True,
                    "editor.suggest.showKeywords": True,
                    "editor.suggest.showSnippets": True,
                    "editor.quickSuggestions": {
                        "other": True,
                        "comments": True,
                        "strings": True
                    },
                    "files.autoSave": "afterDelay",
                    "files.autoSaveDelay": 500,
                    "terminal.integrated.fontSize": 11,
                    "workbench.colorTheme": "Default Dark+",
                    "workbench.iconTheme": "vs-seti",
                    "testing.automaticallyOpenPeekView": "failureInVisibleDocument",
                    "testing.followRunningTest": True,
                    "testing.gutterEnabled": True
                },
                "extensions": [
                    "ms-python.python",
                    "ms-python.pytest",
                    "ms-python.unittest",
                    "eamodio.gitlens"
                ],
                "tasks": [
                    {
                        "label": "Run All Tests",
                        "type": "shell",
                        "command": "python3",
                        "args": ["-m", "pytest", "/Volumes/DATA/Agent_Turbo/tests/"],
                        "group": "test"
                    },
                    {
                        "label": "Run Agent Turbo Integration Tests",
                        "type": "shell",
                        "command": "python3",
                        "args": ["/Volumes/DATA/Agent_Turbo/scripts/verify_cursor_integration.py"],
                        "group": "test"
                    },
                    {
                        "label": "Run Prime Directives Tests",
                        "type": "shell",
                        "command": "python3",
                        "args": ["/Volumes/DATA/Agent_Turbo/scripts/verify_prime_directives.py"],
                        "group": "test"
                    }
                ],
                "launch": {
                    "version": "0.2.0",
                    "configurations": [
                        {
                            "name": "Debug Tests",
                            "type": "python",
                            "request": "launch",
                            "module": "pytest",
                            "args": ["/Volumes/DATA/Agent_Turbo/tests/"],
                            "console": "integratedTerminal"
                        }
                    ]
                }
            }
            
            config_path = self.modes_dir / "testing" / "testing_mode.json"
            config_path.write_text(json.dumps(mode_config, indent=2))
            
            print("✅ Testing mode created")
            return True
            
        except Exception as e:
            print(f"❌ Testing mode creation failed: {e}")
            return False
    
    def create_debugging_mode(self) -> bool:
        """Create debugging mode configuration."""
        try:
            mode_config = {
                "name": "Debugging Mode",
                "description": "Optimized for debugging and troubleshooting",
                "settings": {
                    "editor.fontSize": 15,
                    "editor.tabSize": 4,
                    "editor.insertSpaces": True,
                    "editor.wordWrap": "on",
                    "editor.minimap.enabled": True,
                    "editor.bracketPairColorization.enabled": True,
                    "editor.guides.bracketPairs": True,
                    "editor.suggest.showKeywords": True,
                    "editor.suggest.showSnippets": True,
                    "editor.quickSuggestions": {
                        "other": True,
                        "comments": True,
                        "strings": True
                    },
                    "files.autoSave": "afterDelay",
                    "files.autoSaveDelay": 2000,
                    "terminal.integrated.fontSize": 13,
                    "workbench.colorTheme": "Default Dark+",
                    "workbench.iconTheme": "vs-seti",
                    "debug.console.fontSize": 13,
                    "debug.console.lineHeight": 1.2,
                    "debug.openDebug": "openOnDebugBreak",
                    "debug.showBreakpointsInOverviewRuler": True,
                    "debug.showInlineBreakpointCandidates": True
                },
                "extensions": [
                    "ms-python.python",
                    "ms-python.debugpy",
                    "eamodio.gitlens",
                    "ms-vscode.vscode-json"
                ],
                "tasks": [
                    {
                        "label": "Debug Agent Turbo",
                        "type": "shell",
                        "command": "python3",
                        "args": ["-m", "pdb", "/Volumes/DATA/Agent_Turbo/core/agent_turbo.py"],
                        "group": "build"
                    },
                    {
                        "label": "Run with Debug Output",
                        "type": "shell",
                        "command": "python3",
                        "args": ["-u", "/Volumes/DATA/Agent_Turbo/core/agent_turbo.py", "verify"],
                        "group": "build"
                    }
                ],
                "launch": {
                    "version": "0.2.0",
                    "configurations": [
                        {
                            "name": "Debug Agent Turbo Core",
                            "type": "python",
                            "request": "launch",
                            "program": "/Volumes/DATA/Agent_Turbo/core/agent_turbo.py",
                            "args": ["verify"],
                            "console": "integratedTerminal",
                            "justMyCode": False,
                            "stopOnEntry": False
                        },
                        {
                            "name": "Debug Agent Turbo GPU",
                            "type": "python",
                            "request": "launch",
                            "program": "/Volumes/DATA/Agent_Turbo/core/agent_turbo_gpu.py",
                            "console": "integratedTerminal",
                            "justMyCode": False
                        }
                    ]
                }
            }
            
            config_path = self.modes_dir / "debugging" / "debugging_mode.json"
            config_path.write_text(json.dumps(mode_config, indent=2))
            
            print("✅ Debugging mode created")
            return True
            
        except Exception as e:
            print(f"❌ Debugging mode creation failed: {e}")
            return False
    
    def create_performance_mode(self) -> bool:
        """Create performance mode configuration."""
        try:
            mode_config = {
                "name": "Performance Mode",
                "description": "Optimized for performance monitoring and optimization",
                "settings": {
                    "editor.fontSize": 12,
                    "editor.tabSize": 2,
                    "editor.insertSpaces": True,
                    "editor.wordWrap": "off",
                    "editor.minimap.enabled": False,
                    "editor.bracketPairColorization.enabled": False,
                    "editor.guides.bracketPairs": False,
                    "editor.suggest.showKeywords": False,
                    "editor.suggest.showSnippets": False,
                    "editor.quickSuggestions": {
                        "other": False,
                        "comments": False,
                        "strings": False
                    },
                    "files.autoSave": "off",
                    "terminal.integrated.fontSize": 10,
                    "workbench.colorTheme": "Default Dark+",
                    "workbench.iconTheme": "vs-seti",
                    "workbench.enableExperiments": False,
                    "workbench.settings.enableNaturalLanguageSearch": False
                },
                "extensions": [
                    "ms-python.python",
                    "ms-python.pylint",
                    "ms-python.flake8"
                ],
                "tasks": [
                    {
                        "label": "Run Performance Benchmark",
                        "type": "shell",
                        "command": "python3",
                        "args": ["/Volumes/DATA/Agent_Turbo/scripts/performance_benchmark.py"],
                        "group": "build"
                    },
                    {
                        "label": "Monitor System Performance",
                        "type": "shell",
                        "command": "python3",
                        "args": ["-c", "import psutil; print(f'CPU: {psutil.cpu_percent()}%, Memory: {psutil.virtual_memory().percent}%')"],
                        "group": "build"
                    },
                    {
                        "label": "Check GPU Status",
                        "type": "shell",
                        "command": "python3",
                        "args": ["-c", "import mlx.core as mx; print(f'GPU Available: {mx.metal.is_available()}')"],
                        "group": "build"
                    }
                ],
                "launch": {
                    "version": "0.2.0",
                    "configurations": [
                        {
                            "name": "Profile Agent Turbo",
                            "type": "python",
                            "request": "launch",
                            "program": "/Volumes/DATA/Agent_Turbo/core/agent_turbo.py",
                            "args": ["stats"],
                            "console": "integratedTerminal",
                            "profile": True
                        }
                    ]
                }
            }
            
            config_path = self.modes_dir / "performance" / "performance_mode.json"
            config_path.write_text(json.dumps(mode_config, indent=2))
            
            print("✅ Performance mode created")
            return True
            
        except Exception as e:
            print(f"❌ Performance mode creation failed: {e}")
            return False
    
    def create_mode_switcher(self) -> bool:
        """Create mode switcher script."""
        try:
            switcher_content = '''#!/usr/bin/env python3
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
'''
            
            switcher_path = Path("/Volumes/DATA/Agent_Turbo/scripts/mode_switcher.py")
            switcher_path.write_text(switcher_content)
            switcher_path.chmod(0o755)
            
            print("✅ Mode switcher created")
            return True
            
        except Exception as e:
            print(f"❌ Mode switcher creation failed: {e}")
            return False
    
    def test_custom_modes(self) -> bool:
        """Test custom modes functionality."""
        try:
            # Test mode switcher
            result = subprocess.run([
                "python3", "/Volumes/DATA/Agent_Turbo/scripts/mode_switcher.py", "list"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ Custom modes test successful")
                return True
            else:
                print(f"❌ Custom modes test failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Custom modes test failed: {e}")
            return False
    
    def setup_custom_modes(self) -> bool:
        """Complete custom modes setup."""
        print("🚀 Setting up Custom Modes...")
        
        # Create modes directories
        if not self.create_modes_directories():
            print("❌ TASK FAILED: Modes directory creation failed")
            return False
        
        # Create individual modes
        if not self.create_development_mode():
            print("❌ TASK FAILED: Development mode creation failed")
            return False
        
        if not self.create_testing_mode():
            print("❌ TASK FAILED: Testing mode creation failed")
            return False
        
        if not self.create_debugging_mode():
            print("❌ TASK FAILED: Debugging mode creation failed")
            return False
        
        if not self.create_performance_mode():
            print("❌ TASK FAILED: Performance mode creation failed")
            return False
        
        # Create mode switcher
        if not self.create_mode_switcher():
            print("❌ TASK FAILED: Mode switcher creation failed")
            return False
        
        # Test custom modes
        if not self.test_custom_modes():
            print("❌ TASK FAILED: Custom modes test failed")
            return False
        
        self.status["modes_created"] = 4
        self.status["modes_configured"] = True
        self.status["workflows_ready"] = True
        
        print("✅ Custom modes setup complete")
        return True

def main():
    """Main execution."""
    setup = CustomModesSetup()
    success = setup.setup_custom_modes()
    
    if success:
        print("✅ Custom modes implementation successful")
        return 0
    else:
        print("❌ TASK FAILED: Custom modes setup failed")
        return 1

if __name__ == "__main__":
    exit(main())
