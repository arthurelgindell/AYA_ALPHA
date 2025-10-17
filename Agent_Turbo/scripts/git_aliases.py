#!/usr/bin/env python3
"""
Git Aliases for AGENT_TURBO
Provides intelligent Git aliases and automation
"""

import subprocess
import sys
from pathlib import Path

class GitAliases:
    """Git aliases system."""
    
    def __init__(self):
        self.aliases = {
            # Basic aliases
            "st": "status",
            "co": "checkout",
            "br": "branch",
            "ci": "commit",
            "df": "diff",
            "lg": "log --oneline --graph --decorate --all",
            "unstage": "reset HEAD --",
            "last": "log -1 HEAD",
            "visual": "!cursor",
            
            # Agent Turbo specific aliases
            "turbo-status": "status --porcelain",
            "turbo-add": "add .",
            "turbo-commit": "commit -m",
            "turbo-push": "push origin",
            "turbo-pull": "pull origin",
            
            # Advanced aliases
            "amend": "commit --amend --no-edit",
            "undo": "reset HEAD~1",
            "redo": "reset HEAD@{1}",
            "stash-all": "stash push -u",
            "stash-pop": "stash pop",
            "stash-list": "stash list",
            
            # Branch management
            "new-branch": "checkout -b",
            "delete-branch": "branch -d",
            "merge-branch": "merge --no-ff",
            "rebase-branch": "rebase",
            
            # Remote management
            "remote-add": "remote add",
            "remote-remove": "remote remove",
            "remote-list": "remote -v",
            
            # History management
            "history": "log --oneline --graph --decorate --all",
            "history-file": "log --follow --",
            "history-grep": "log --grep",
            "history-author": "log --author",
            
            # File management
            "add-all": "add .",
            "reset-all": "reset HEAD .",
            "clean-all": "clean -fd",
            "rm-cached": "rm --cached",
            
            # Tag management
            "tag-list": "tag -l",
            "tag-create": "tag -a",
            "tag-delete": "tag -d",
            "tag-push": "push origin --tags"
        }
    
    def get_alias(self, alias_name: str) -> str:
        """Get alias command."""
        return self.aliases.get(alias_name, "")
    
    def list_aliases(self):
        """List all available aliases."""
        print("Available Git Aliases:")
        print()
        
        categories = {
            "Basic": ["st", "co", "br", "ci", "df", "lg", "unstage", "last", "visual"],
            "Agent Turbo": ["turbo-status", "turbo-add", "turbo-commit", "turbo-push", "turbo-pull"],
            "Advanced": ["amend", "undo", "redo", "stash-all", "stash-pop", "stash-list"],
            "Branch Management": ["new-branch", "delete-branch", "merge-branch", "rebase-branch"],
            "Remote Management": ["remote-add", "remote-remove", "remote-list"],
            "History Management": ["history", "history-file", "history-grep", "history-author"],
            "File Management": ["add-all", "reset-all", "clean-all", "rm-cached"],
            "Tag Management": ["tag-list", "tag-create", "tag-delete", "tag-push"]
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
            
            # Handle special cases
            if command.startswith("!"):
                # Shell command
                command = command[1:]
                if args:
                    command += " " + " ".join(args)
                result = subprocess.run(command, shell=True)
                return result.returncode == 0
            else:
                # Git command
                git_command = ["git"] + command.split()
                if args:
                    git_command.extend(args)
                
                print(f"🚀 Executing: {' '.join(git_command)}")
                result = subprocess.run(git_command)
                return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Alias execution failed: {e}")
            return False

def main():
    """Main execution."""
    aliases = GitAliases()
    
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
