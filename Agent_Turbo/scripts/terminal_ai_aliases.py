#!/usr/bin/env python3
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
