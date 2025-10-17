#!/usr/bin/env python3
"""
Terminal AI Setup for AGENT_TURBO
Implements terminal AI features for assistance in terminal operations
GAMMA Project - Prime Directives Compliance
"""

import subprocess
import json
import time
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

class TerminalAISetup:
    """Terminal AI setup for Cursor."""
    
    def __init__(self):
        self.terminal_ai_dir = Path("/Volumes/DATA/Agent_Turbo/terminal_ai")
        self.ai_commands_dir = Path("/Volumes/DATA/Agent_Turbo/ai_commands")
        self.status = {
            "terminal_ai_available": False,
            "ai_commands_configured": False,
            "suggestions_enabled": False,
            "auto_completion_enabled": False
        }
        
    def create_terminal_ai_directories(self) -> bool:
        """Create terminal AI directories."""
        try:
            directories = [
                self.terminal_ai_dir,
                self.ai_commands_dir,
                self.terminal_ai_dir / "suggestions",
                self.terminal_ai_dir / "completions",
                self.terminal_ai_dir / "history",
                self.ai_commands_dir / "custom",
                self.ai_commands_dir / "aliases"
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created directory: {directory}")
            
            return True
            
        except Exception as e:
            print(f"❌ Terminal AI directory creation failed: {e}")
            return False
    
    def create_terminal_ai_config(self) -> bool:
        """Create terminal AI configuration."""
        try:
            config_content = {
                "terminal_ai": {
                    "enabled": True,
                    "suggestions_enabled": True,
                    "auto_completion_enabled": True,
                    "command_history_enabled": True
                },
                "suggestions": {
                    "max_suggestions": 5,
                    "context_aware": True,
                    "learn_from_history": True,
                    "suggestion_timeout": 2
                },
                "completions": {
                    "file_completion": True,
                    "command_completion": True,
                    "argument_completion": True,
                    "smart_completion": True
                },
                "history": {
                    "max_history_size": 1000,
                    "persistent_history": True,
                    "history_analysis": True
                }
            }
            
            config_path = self.terminal_ai_dir / "terminal_ai_config.json"
            config_path.write_text(json.dumps(config_content, indent=2))
            
            print("✅ Terminal AI configuration created")
            return True
            
        except Exception as e:
            print(f"❌ Terminal AI config creation failed: {e}")
            return False
    
    def create_ai_command_suggestions(self) -> bool:
        """Create AI command suggestions system."""
        try:
            suggestions_content = '''#!/usr/bin/env python3
"""
AI Command Suggestions for AGENT_TURBO
Provides intelligent command suggestions based on context
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any

class AICommandSuggestions:
    """AI-powered command suggestions."""
    
    def __init__(self):
        self.config_path = Path("/Volumes/DATA/Agent_Turbo/terminal_ai/terminal_ai_config.json")
        self.history_path = Path("/Volumes/DATA/Agent_Turbo/terminal_ai/history/command_history.json")
        self.suggestions_path = Path("/Volumes/DATA/Agent_Turbo/terminal_ai/suggestions/suggestions.json")
        
        # Load configuration
        if self.config_path.exists():
            self.config = json.loads(self.config_path.read_text())
        else:
            self.config = {}
        
        # Load command history
        if self.history_path.exists():
            self.history = json.loads(self.history_path.read_text())
        else:
            self.history = {"commands": [], "contexts": []}
    
    def get_suggestions(self, current_input: str, context: str = "") -> List[str]:
        """Get AI-powered command suggestions."""
        try:
            suggestions = []
            
            # Context-based suggestions
            if "python" in current_input.lower():
                suggestions.extend([
                    "python3 /Volumes/DATA/Agent_Turbo/core/agent_turbo.py verify",
                    "python3 /Volumes/DATA/Agent_Turbo/core/agent_turbo.py stats",
                    "python3 /Volumes/DATA/Agent_Turbo/scripts/verify_cursor_integration.py"
                ])
            
            if "git" in current_input.lower():
                suggestions.extend([
                    "git status",
                    "git add .",
                    "git commit -m 'Update'",
                    "git push"
                ])
            
            if "cursor" in current_input.lower():
                suggestions.extend([
                    "cursor .",
                    "cursor --version",
                    "cursor --help"
                ])
            
            # Agent Turbo specific suggestions
            if "agent" in current_input.lower() or "turbo" in current_input.lower():
                suggestions.extend([
                    "python3 /Volumes/DATA/Agent_Turbo/core/agent_turbo.py verify",
                    "python3 /Volumes/DATA/Agent_Turbo/core/agent_turbo.py stats",
                    "python3 /Volumes/DATA/Agent_Turbo/scripts/verify_cursor_integration.py",
                    "python3 /Volumes/DATA/Agent_Turbo/scripts/verify_prime_directives.py"
                ])
            
            # File operation suggestions
            if any(op in current_input for op in ["ls", "cd", "mkdir", "rm"]):
                suggestions.extend([
                    "ls -la",
                    "cd /Volumes/DATA/Agent_Turbo",
                    "mkdir -p new_directory",
                    "rm -rf old_directory"
                ])
            
            # Limit suggestions
            max_suggestions = self.config.get("suggestions", {}).get("max_suggestions", 5)
            return suggestions[:max_suggestions]
            
        except Exception as e:
            print(f"❌ Suggestions generation failed: {e}")
            return []
    
    def save_command_history(self, command: str, context: str = ""):
        """Save command to history."""
        try:
            history_entry = {
                "command": command,
                "context": context,
                "timestamp": time.time()
            }
            
            self.history["commands"].append(history_entry)
            
            # Limit history size
            max_history = self.config.get("history", {}).get("max_history_size", 1000)
            if len(self.history["commands"]) > max_history:
                self.history["commands"] = self.history["commands"][-max_history:]
            
            # Save history
            self.history_path.write_text(json.dumps(self.history, indent=2))
            
        except Exception as e:
            print(f"❌ History save failed: {e}")
    
    def get_context_suggestions(self, current_directory: str) -> List[str]:
        """Get context-aware suggestions based on current directory."""
        try:
            suggestions = []
            current_path = Path(current_directory)
            
            # Agent Turbo workspace suggestions
            if "Agent_Turbo" in str(current_path):
                suggestions.extend([
                    "python3 core/agent_turbo.py verify",
                    "python3 core/agent_turbo.py stats",
                    "python3 scripts/verify_cursor_integration.py"
                ])
            
            # Scripts directory suggestions
            if current_path.name == "scripts":
                suggestions.extend([
                    "python3 browser_automation_setup.py",
                    "python3 mcp_integration_setup.py",
                    "python3 shadow_workspace_setup.py"
                ])
            
            # Core directory suggestions
            if current_path.name == "core":
                suggestions.extend([
                    "python3 agent_turbo.py verify",
                    "python3 agent_turbo.py stats",
                    "python3 agent_turbo_gpu.py"
                ])
            
            return suggestions
            
        except Exception as e:
            print(f"❌ Context suggestions failed: {e}")
            return []

def main():
    """Main execution."""
    import time
    
    suggestions = AICommandSuggestions()
    
    if len(sys.argv) < 2:
        print("Usage: python3 ai_command_suggestions.py <current_input> [context]")
        return 1
    
    current_input = sys.argv[1]
    context = sys.argv[2] if len(sys.argv) > 2 else ""
    
    # Get suggestions
    suggestions_list = suggestions.get_suggestions(current_input, context)
    
    # Print suggestions
    for i, suggestion in enumerate(suggestions_list, 1):
        print(f"{i}. {suggestion}")
    
    return 0

if __name__ == "__main__":
    exit(main())
'''
            
            suggestions_path = Path("/Volumes/DATA/Agent_Turbo/scripts/ai_command_suggestions.py")
            suggestions_path.write_text(suggestions_content)
            suggestions_path.chmod(0o755)
            
            print("✅ AI command suggestions created")
            return True
            
        except Exception as e:
            print(f"❌ AI command suggestions creation failed: {e}")
            return False
    
    def create_terminal_ai_aliases(self) -> bool:
        """Create terminal AI aliases."""
        try:
            aliases_content = '''#!/usr/bin/env python3
"""
Terminal AI Aliases for AGENT_TURBO
Provides intelligent aliases for common operations
"""

import subprocess
import sys
from pathlib import Path

class TerminalAIAliases:
    """Terminal AI aliases system."""
    
    def __init__(self):
        self.aliases = {
            # Agent Turbo aliases
            "turbo": "python3 /Volumes/DATA/Agent_Turbo/core/agent_turbo.py",
            "turbo-verify": "python3 /Volumes/DATA/Agent_Turbo/core/agent_turbo.py verify",
            "turbo-stats": "python3 /Volumes/DATA/Agent_Turbo/core/agent_turbo.py stats",
            "turbo-integration": "python3 /Volumes/DATA/Agent_Turbo/scripts/verify_cursor_integration.py",
            "turbo-directives": "python3 /Volumes/DATA/Agent_Turbo/scripts/verify_prime_directives.py",
            
            # Development aliases
            "dev-setup": "python3 /Volumes/DATA/Agent_Turbo/scripts/browser_automation_setup.py",
            "mcp-setup": "python3 /Volumes/DATA/Agent_Turbo/scripts/mcp_integration_setup.py",
            "shadow-setup": "python3 /Volumes/DATA/Agent_Turbo/scripts/shadow_workspace_setup.py",
            "local-exp": "python3 /Volumes/DATA/Agent_Turbo/scripts/local_experimentation_setup.py",
            "retrieval-opt": "python3 /Volumes/DATA/Agent_Turbo/scripts/retrieval_optimization_setup.py",
            
            # Workspace aliases
            "workspace": "cd /Volumes/DATA/Agent_Turbo",
            "workspace-dev": "cd /Volumes/DATA/Agent_Turbo_Dev",
            "workspace-test": "cd /Volumes/DATA/Agent_Turbo_Test",
            "workspace-exp": "cd /Volumes/DATA/Agent_Turbo_Exp",
            "workspace-backup": "cd /Volumes/DATA/Agent_Turbo_Backup",
            
            # Cursor aliases
            "cursor-workspace": "cursor /Volumes/DATA/Agent_Turbo",
            "cursor-dev": "cursor /Volumes/DATA/Agent_Turbo_Dev",
            "cursor-test": "cursor /Volumes/DATA/Agent_Turbo_Test",
            
            # Git aliases
            "git-status": "git status",
            "git-add": "git add .",
            "git-commit": "git commit -m",
            "git-push": "git push",
            "git-pull": "git pull",
            
            # System aliases
            "ll": "ls -la",
            "la": "ls -la",
            "l": "ls -la",
            "..": "cd ..",
            "...": "cd ../..",
            "....": "cd ../../.."
        }
    
    def get_alias(self, alias_name: str) -> str:
        """Get alias command."""
        return self.aliases.get(alias_name, "")
    
    def list_aliases(self):
        """List all available aliases."""
        print("Available Terminal AI Aliases:")
        print()
        
        categories = {
            "Agent Turbo": ["turbo", "turbo-verify", "turbo-stats", "turbo-integration", "turbo-directives"],
            "Development": ["dev-setup", "mcp-setup", "shadow-setup", "local-exp", "retrieval-opt"],
            "Workspace": ["workspace", "workspace-dev", "workspace-test", "workspace-exp", "workspace-backup"],
            "Cursor": ["cursor-workspace", "cursor-dev", "cursor-test"],
            "Git": ["git-status", "git-add", "git-commit", "git-push", "git-pull"],
            "System": ["ll", "la", "l", "..", "...", "...."]
        }
        
        for category, alias_list in categories.items():
            print(f"{category}:")
            for alias in alias_list:
                command = self.aliases.get(alias, "")
                print(f"  {alias:<20} -> {command}")
            print()
    
    def execute_alias(self, alias_name: str, *args) -> bool:
        """Execute alias command."""
        try:
            command = self.get_alias(alias_name)
            if not command:
                print(f"❌ Unknown alias: {alias_name}")
                return False
            
            # Add arguments if provided
            if args:
                command += " " + " ".join(args)
            
            print(f"🚀 Executing: {command}")
            result = subprocess.run(command, shell=True)
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Alias execution failed: {e}")
            return False

def main():
    """Main execution."""
    aliases = TerminalAIAliases()
    
    if len(sys.argv) < 2:
        aliases.list_aliases()
        return 0
    
    alias_name = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    if alias_name == "list":
        aliases.list_aliases()
        return 0
    
    success = aliases.execute_alias(alias_name, *args)
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
'''
            
            aliases_path = Path("/Volumes/DATA/Agent_Turbo/scripts/terminal_ai_aliases.py")
            aliases_path.write_text(aliases_content)
            aliases_path.chmod(0o755)
            
            print("✅ Terminal AI aliases created")
            return True
            
        except Exception as e:
            print(f"❌ Terminal AI aliases creation failed: {e}")
            return False
    
    def create_shell_integration(self) -> bool:
        """Create shell integration for terminal AI."""
        try:
            # Create bash integration
            bash_integration = '''# AGENT_TURBO Terminal AI Integration
# Add to ~/.bashrc or ~/.bash_profile

# Agent Turbo aliases
alias turbo="python3 /Volumes/DATA/Agent_Turbo/core/agent_turbo.py"
alias turbo-verify="python3 /Volumes/DATA/Agent_Turbo/core/agent_turbo.py verify"
alias turbo-stats="python3 /Volumes/DATA/Agent_Turbo/core/agent_turbo.py stats"
alias turbo-integration="python3 /Volumes/DATA/Agent_Turbo/scripts/verify_cursor_integration.py"
alias turbo-directives="python3 /Volumes/DATA/Agent_Turbo/scripts/verify_prime_directives.py"

# Development aliases
alias dev-setup="python3 /Volumes/DATA/Agent_Turbo/scripts/browser_automation_setup.py"
alias mcp-setup="python3 /Volumes/DATA/Agent_Turbo/scripts/mcp_integration_setup.py"
alias shadow-setup="python3 /Volumes/DATA/Agent_Turbo/scripts/shadow_workspace_setup.py"
alias local-exp="python3 /Volumes/DATA/Agent_Turbo/scripts/local_experimentation_setup.py"
alias retrieval-opt="python3 /Volumes/DATA/Agent_Turbo/scripts/retrieval_optimization_setup.py"

# Workspace aliases
alias workspace="cd /Volumes/DATA/Agent_Turbo"
alias workspace-dev="cd /Volumes/DATA/Agent_Turbo_Dev"
alias workspace-test="cd /Volumes/DATA/Agent_Turbo_Test"
alias workspace-exp="cd /Volumes/DATA/Agent_Turbo_Exp"
alias workspace-backup="cd /Volumes/DATA/Agent_Turbo_Backup"

# Cursor aliases
alias cursor-workspace="cursor /Volumes/DATA/Agent_Turbo"
alias cursor-dev="cursor /Volumes/DATA/Agent_Turbo_Dev"
alias cursor-test="cursor /Volumes/DATA/Agent_Turbo_Test"

# System aliases
alias ll="ls -la"
alias la="ls -la"
alias l="ls -la"
alias ..="cd .."
alias ...="cd ../.."
alias ....="cd ../../.."

# Terminal AI function
turbo-ai() {
    python3 /Volumes/DATA/Agent_Turbo/scripts/ai_command_suggestions.py "$@"
}

# Terminal AI aliases function
turbo-aliases() {
    python3 /Volumes/DATA/Agent_Turbo/scripts/terminal_ai_aliases.py "$@"
}
'''
            
            bash_path = Path("/Volumes/DATA/Agent_Turbo/terminal_ai/bash_integration.sh")
            bash_path.write_text(bash_integration)
            bash_path.chmod(0o755)
            
            # Create zsh integration
            zsh_integration = '''# AGENT_TURBO Terminal AI Integration
# Add to ~/.zshrc

# Agent Turbo aliases
alias turbo="python3 /Volumes/DATA/Agent_Turbo/core/agent_turbo.py"
alias turbo-verify="python3 /Volumes/DATA/Agent_Turbo/core/agent_turbo.py verify"
alias turbo-stats="python3 /Volumes/DATA/Agent_Turbo/core/agent_turbo.py stats"
alias turbo-integration="python3 /Volumes/DATA/Agent_Turbo/scripts/verify_cursor_integration.py"
alias turbo-directives="python3 /Volumes/DATA/Agent_Turbo/scripts/verify_prime_directives.py"

# Development aliases
alias dev-setup="python3 /Volumes/DATA/Agent_Turbo/scripts/browser_automation_setup.py"
alias mcp-setup="python3 /Volumes/DATA/Agent_Turbo/scripts/mcp_integration_setup.py"
alias shadow-setup="python3 /Volumes/DATA/Agent_Turbo/scripts/shadow_workspace_setup.py"
alias local-exp="python3 /Volumes/DATA/Agent_Turbo/scripts/local_experimentation_setup.py"
alias retrieval-opt="python3 /Volumes/DATA/Agent_Turbo/scripts/retrieval_optimization_setup.py"

# Workspace aliases
alias workspace="cd /Volumes/DATA/Agent_Turbo"
alias workspace-dev="cd /Volumes/DATA/Agent_Turbo_Dev"
alias workspace-test="cd /Volumes/DATA/Agent_Turbo_Test"
alias workspace-exp="cd /Volumes/DATA/Agent_Turbo_Exp"
alias workspace-backup="cd /Volumes/DATA/Agent_Turbo_Backup"

# Cursor aliases
alias cursor-workspace="cursor /Volumes/DATA/Agent_Turbo"
alias cursor-dev="cursor /Volumes/DATA/Agent_Turbo_Dev"
alias cursor-test="cursor /Volumes/DATA/Agent_Turbo_Test"

# System aliases
alias ll="ls -la"
alias la="ls -la"
alias l="ls -la"
alias ..="cd .."
alias ...="cd ../.."
alias ....="cd ../../.."

# Terminal AI function
turbo-ai() {
    python3 /Volumes/DATA/Agent_Turbo/scripts/ai_command_suggestions.py "$@"
}

# Terminal AI aliases function
turbo-aliases() {
    python3 /Volumes/DATA/Agent_Turbo/scripts/terminal_ai_aliases.py "$@"
}
'''
            
            zsh_path = Path("/Volumes/DATA/Agent_Turbo/terminal_ai/zsh_integration.sh")
            zsh_path.write_text(zsh_integration)
            zsh_path.chmod(0o755)
            
            print("✅ Shell integration created")
            return True
            
        except Exception as e:
            print(f"❌ Shell integration creation failed: {e}")
            return False
    
    def test_terminal_ai(self) -> bool:
        """Test terminal AI functionality."""
        try:
            # Test AI command suggestions
            result = subprocess.run([
                "python3", "/Volumes/DATA/Agent_Turbo/scripts/ai_command_suggestions.py", "python"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ Terminal AI suggestions test successful")
            else:
                print(f"❌ Terminal AI suggestions test failed: {result.stderr}")
                return False
            
            # Test terminal AI aliases
            result = subprocess.run([
                "python3", "/Volumes/DATA/Agent_Turbo/scripts/terminal_ai_aliases.py", "list"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ Terminal AI aliases test successful")
                return True
            else:
                print(f"❌ Terminal AI aliases test failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Terminal AI test failed: {e}")
            return False
    
    def setup_terminal_ai(self) -> bool:
        """Complete terminal AI setup."""
        print("🚀 Setting up Terminal AI...")
        
        # Create terminal AI directories
        if not self.create_terminal_ai_directories():
            print("❌ TASK FAILED: Terminal AI directory creation failed")
            return False
        
        # Create terminal AI config
        if not self.create_terminal_ai_config():
            print("❌ TASK FAILED: Terminal AI config creation failed")
            return False
        
        # Create AI command suggestions
        if not self.create_ai_command_suggestions():
            print("❌ TASK FAILED: AI command suggestions creation failed")
            return False
        
        # Create terminal AI aliases
        if not self.create_terminal_ai_aliases():
            print("❌ TASK FAILED: Terminal AI aliases creation failed")
            return False
        
        # Create shell integration
        if not self.create_shell_integration():
            print("❌ TASK FAILED: Shell integration creation failed")
            return False
        
        # Test terminal AI
        if not self.test_terminal_ai():
            print("❌ TASK FAILED: Terminal AI test failed")
            return False
        
        print("✅ Terminal AI setup complete")
        return True

def main():
    """Main execution."""
    setup = TerminalAISetup()
    success = setup.setup_terminal_ai()
    
    if success:
        print("✅ Terminal AI implementation successful")
        return 0
    else:
        print("❌ TASK FAILED: Terminal AI setup failed")
        return 1

if __name__ == "__main__":
    exit(main())
