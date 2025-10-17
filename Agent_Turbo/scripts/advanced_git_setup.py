#!/usr/bin/env python3
"""
Advanced Git Setup for AGENT_TURBO
Implements advanced Git features for automated commit messages and branch management
GAMMA Project - Prime Directives Compliance
"""

import subprocess
import json
import time
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

class AdvancedGitSetup:
    """Advanced Git setup for Cursor."""
    
    def __init__(self):
        self.git_config_dir = Path("/Volumes/DATA/Agent_Turbo/git_config")
        self.git_hooks_dir = Path("/Volumes/DATA/Agent_Turbo/git_hooks")
        self.status = {
            "git_available": False,
            "hooks_configured": False,
            "automation_enabled": False,
            "branch_management_enabled": False
        }
        
    def verify_git_availability(self) -> bool:
        """Verify Git is available."""
        try:
            result = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ Git Available: {result.stdout.strip()}")
                self.status["git_available"] = True
                return True
            else:
                print("❌ Git not available")
                return False
        except Exception as e:
            print(f"❌ Git verification failed: {e}")
            return False
    
    def create_git_directories(self) -> bool:
        """Create Git configuration directories."""
        try:
            directories = [
                self.git_config_dir,
                self.git_hooks_dir,
                self.git_config_dir / "templates",
                self.git_config_dir / "aliases",
                self.git_hooks_dir / "pre-commit",
                self.git_hooks_dir / "post-commit",
                self.git_hooks_dir / "pre-push"
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created directory: {directory}")
            
            return True
            
        except Exception as e:
            print(f"❌ Git directory creation failed: {e}")
            return False
    
    def create_git_config(self) -> bool:
        """Create advanced Git configuration."""
        try:
            config_content = {
                "git": {
                    "user": {
                        "name": "Arthur Dell",
                        "email": "arthur.dell@protonmail.com"
                    },
                    "core": {
                        "editor": "cursor",
                        "autocrlf": "input",
                        "safecrlf": "warn"
                    },
                    "pull": {
                        "rebase": "false"
                    },
                    "push": {
                        "default": "simple"
                    },
                    "branch": {
                        "autosetupmerge": "true",
                        "autosetuprebase": "always"
                    }
                },
                "aliases": {
                    "st": "status",
                    "co": "checkout",
                    "br": "branch",
                    "ci": "commit",
                    "df": "diff",
                    "lg": "log --oneline --graph --decorate --all",
                    "unstage": "reset HEAD --",
                    "last": "log -1 HEAD",
                    "visual": "!cursor"
                },
                "hooks": {
                    "pre_commit": True,
                    "post_commit": True,
                    "pre_push": True
                }
            }
            
            config_path = self.git_config_dir / "git_config.json"
            config_path.write_text(json.dumps(config_content, indent=2))
            
            print("✅ Git configuration created")
            return True
            
        except Exception as e:
            print(f"❌ Git config creation failed: {e}")
            return False
    
    def create_git_aliases(self) -> bool:
        """Create Git aliases."""
        try:
            aliases_content = '''#!/usr/bin/env python3
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
'''
            
            aliases_path = Path("/Volumes/DATA/Agent_Turbo/scripts/git_aliases.py")
            aliases_path.write_text(aliases_content)
            aliases_path.chmod(0o755)
            
            print("✅ Git aliases created")
            return True
            
        except Exception as e:
            print(f"❌ Git aliases creation failed: {e}")
            return False
    
    def create_git_hooks(self) -> bool:
        """Create Git hooks for automation."""
        try:
            # Pre-commit hook
            pre_commit_hook = '''#!/bin/bash
# Pre-commit hook for AGENT_TURBO
# Runs before each commit

echo "🚀 Running pre-commit checks..."

# Check if we're in the Agent Turbo workspace
if [[ "$PWD" == *"Agent_Turbo"* ]]; then
    echo "✅ Agent Turbo workspace detected"
    
    # Run Agent Turbo verification
    if command -v python3 &> /dev/null; then
        echo "🔍 Running Agent Turbo verification..."
        python3 /Volumes/DATA/Agent_Turbo/core/agent_turbo.py verify
        if [ $? -eq 0 ]; then
            echo "✅ Agent Turbo verification passed"
        else
            echo "❌ Agent Turbo verification failed"
            exit 1
        fi
    fi
    
    # Check for large files
    echo "🔍 Checking for large files..."
    large_files=$(find . -type f -size +10M -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./.venv/*")
    if [ -n "$large_files" ]; then
        echo "⚠️  Large files detected:"
        echo "$large_files"
        echo "Consider using Git LFS for large files"
    fi
    
    # Check for sensitive files
    echo "🔍 Checking for sensitive files..."
    sensitive_files=$(find . -type f \( -name "*.key" -o -name "*.pem" -o -name "*.p12" -o -name ".env" \) -not -path "./.git/*")
    if [ -n "$sensitive_files" ]; then
        echo "❌ Sensitive files detected:"
        echo "$sensitive_files"
        echo "Please remove sensitive files before committing"
        exit 1
    fi
fi

echo "✅ Pre-commit checks passed"
exit 0
'''
            
            pre_commit_path = self.git_hooks_dir / "pre-commit" / "pre-commit.sh"
            pre_commit_path.write_text(pre_commit_hook)
            pre_commit_path.chmod(0o755)
            
            # Post-commit hook
            post_commit_hook = '''#!/bin/bash
# Post-commit hook for AGENT_TURBO
# Runs after each commit

echo "🚀 Running post-commit actions..."

# Check if we're in the Agent Turbo workspace
if [[ "$PWD" == *"Agent_Turbo"* ]]; then
    echo "✅ Agent Turbo workspace detected"
    
    # Update Agent Turbo stats
    if command -v python3 &> /dev/null; then
        echo "📊 Updating Agent Turbo stats..."
        python3 /Volumes/DATA/Agent_Turbo/core/agent_turbo.py stats > /dev/null 2>&1
    fi
    
    # Log commit information
    commit_hash=$(git rev-parse HEAD)
    commit_message=$(git log -1 --pretty=%B)
    commit_author=$(git log -1 --pretty=%an)
    commit_date=$(git log -1 --pretty=%ad)
    
    echo "📝 Commit logged:"
    echo "  Hash: $commit_hash"
    echo "  Message: $commit_message"
    echo "  Author: $commit_author"
    echo "  Date: $commit_date"
    
    # Save commit log
    log_file="/Volumes/DATA/Agent_Turbo/git_config/commit_log.json"
    if [ -f "$log_file" ]; then
        # Append to existing log
        echo "{\"hash\":\"$commit_hash\",\"message\":\"$commit_message\",\"author\":\"$commit_author\",\"date\":\"$commit_date\"}," >> "$log_file"
    else
        # Create new log
        echo "[{\"hash\":\"$commit_hash\",\"message\":\"$commit_message\",\"author\":\"$commit_author\",\"date\":\"$commit_date\"}]" > "$log_file"
    fi
fi

echo "✅ Post-commit actions completed"
exit 0
'''
            
            post_commit_path = self.git_hooks_dir / "post-commit" / "post-commit.sh"
            post_commit_path.write_text(post_commit_hook)
            post_commit_path.chmod(0o755)
            
            # Pre-push hook
            pre_push_hook = '''#!/bin/bash
# Pre-push hook for AGENT_TURBO
# Runs before each push

echo "🚀 Running pre-push checks..."

# Check if we're in the Agent Turbo workspace
if [[ "$PWD" == *"Agent_Turbo"* ]]; then
    echo "✅ Agent Turbo workspace detected"
    
    # Run final verification
    if command -v python3 &> /dev/null; then
        echo "🔍 Running final Agent Turbo verification..."
        python3 /Volumes/DATA/Agent_Turbo/core/agent_turbo.py verify
        if [ $? -eq 0 ]; then
            echo "✅ Final verification passed"
        else
            echo "❌ Final verification failed"
            exit 1
        fi
    fi
    
    # Check for uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        echo "⚠️  Uncommitted changes detected"
        echo "Please commit all changes before pushing"
        exit 1
    fi
    
    # Check for unpushed commits
    unpushed_commits=$(git log origin/$(git branch --show-current)..HEAD --oneline | wc -l)
    if [ "$unpushed_commits" -gt 0 ]; then
        echo "📤 Pushing $unpushed_commits commits"
    fi
fi

echo "✅ Pre-push checks passed"
exit 0
'''
            
            pre_push_path = self.git_hooks_dir / "pre-push" / "pre-push.sh"
            pre_push_path.write_text(pre_push_hook)
            pre_push_path.chmod(0o755)
            
            print("✅ Git hooks created")
            return True
            
        except Exception as e:
            print(f"❌ Git hooks creation failed: {e}")
            return False
    
    def create_commit_message_generator(self) -> bool:
        """Create AI-powered commit message generator."""
        try:
            generator_content = '''#!/usr/bin/env python3
"""
AI Commit Message Generator for AGENT_TURBO
Generates intelligent commit messages based on changes
"""

import subprocess
import json
import sys
from pathlib import Path
from typing import Dict, List, Any

class CommitMessageGenerator:
    """AI-powered commit message generator."""
    
    def __init__(self):
        self.config_path = Path("/Volumes/DATA/Agent_Turbo/git_config/git_config.json")
        
        # Load configuration
        if self.config_path.exists():
            self.config = json.loads(self.config_path.read_text())
        else:
            self.config = {}
    
    def get_changes(self) -> Dict[str, List[str]]:
        """Get current changes."""
        try:
            # Get staged changes
            result = subprocess.run(["git", "diff", "--cached", "--name-status"], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return {"added": [], "modified": [], "deleted": []}
            
            changes = {"added": [], "modified": [], "deleted": []}
            
            for line in result.stdout.strip().split('\\n'):
                if not line:
                    continue
                
                status, file_path = line.split('\\t', 1)
                
                if status == 'A':
                    changes["added"].append(file_path)
                elif status == 'M':
                    changes["modified"].append(file_path)
                elif status == 'D':
                    changes["deleted"].append(file_path)
            
            return changes
            
        except Exception as e:
            print(f"❌ Failed to get changes: {e}")
            return {"added": [], "modified": [], "deleted": []}
    
    def generate_commit_message(self, changes: Dict[str, List[str]]) -> str:
        """Generate commit message based on changes."""
        try:
            message_parts = []
            
            # Analyze changes
            added_files = changes.get("added", [])
            modified_files = changes.get("modified", [])
            deleted_files = changes.get("deleted", [])
            
            # Determine change type
            if added_files and not modified_files and not deleted_files:
                change_type = "Add"
            elif modified_files and not added_files and not deleted_files:
                change_type = "Update"
            elif deleted_files and not added_files and not modified_files:
                change_type = "Remove"
            else:
                change_type = "Modify"
            
            # Analyze file types
            file_types = set()
            for file_list in [added_files, modified_files, deleted_files]:
                for file_path in file_list:
                    if file_path.endswith('.py'):
                        file_types.add('Python')
                    elif file_path.endswith('.js') or file_path.endswith('.ts'):
                        file_types.add('JavaScript/TypeScript')
                    elif file_path.endswith('.md'):
                        file_types.add('Documentation')
                    elif file_path.endswith('.json'):
                        file_types.add('Configuration')
                    elif file_path.endswith('.sh'):
                        file_types.add('Shell')
                    else:
                        file_types.add('Other')
            
            # Generate message
            if len(file_types) == 1:
                file_type = list(file_types)[0]
                message_parts.append(f"{change_type} {file_type} files")
            else:
                message_parts.append(f"{change_type} files")
            
            # Add specific details
            if "Agent_Turbo" in str(Path.cwd()):
                if any("core" in f for f in added_files + modified_files):
                    message_parts.append("core system updates")
                elif any("scripts" in f for f in added_files + modified_files):
                    message_parts.append("script improvements")
                elif any("config" in f for f in added_files + modified_files):
                    message_parts.append("configuration updates")
            
            # Add file count
            total_files = len(added_files) + len(modified_files) + len(deleted_files)
            if total_files > 1:
                message_parts.append(f"({total_files} files)")
            
            return " ".join(message_parts)
            
        except Exception as e:
            print(f"❌ Failed to generate commit message: {e}")
            return "Update files"
    
    def generate_commit(self, message: str = None) -> bool:
        """Generate and create commit."""
        try:
            if not message:
                changes = self.get_changes()
                message = self.generate_commit_message(changes)
            
            print(f"🚀 Creating commit: {message}")
            
            result = subprocess.run(["git", "commit", "-m", message])
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Commit creation failed: {e}")
            return False
    
    def list_commit_templates(self):
        """List commit message templates."""
        templates = [
            "feat: Add new feature",
            "fix: Fix bug",
            "docs: Update documentation",
            "style: Code style changes",
            "refactor: Code refactoring",
            "test: Add or update tests",
            "chore: Maintenance tasks",
            "perf: Performance improvements",
            "ci: CI/CD changes",
            "build: Build system changes"
        ]
        
        print("Commit Message Templates:")
        for template in templates:
            print(f"  {template}")

def main():
    """Main execution."""
    generator = CommitMessageGenerator()
    
    if len(sys.argv) < 2:
        generator.list_commit_templates()
        return 0
    
    command = sys.argv[1]
    
    if command == "generate":
        changes = generator.get_changes()
        message = generator.generate_commit_message(changes)
        print(f"Generated message: {message}")
        return 0
    elif command == "commit":
        message = sys.argv[2] if len(sys.argv) > 2 else None
        success = generator.generate_commit(message)
        return 0 if success else 1
    elif command == "templates":
        generator.list_commit_templates()
        return 0
    else:
        print("Usage:")
        print("  python3 commit_message_generator.py generate")
        print("  python3 commit_message_generator.py commit [message]")
        print("  python3 commit_message_generator.py templates")
        return 1

if __name__ == "__main__":
    exit(main())
'''
            
            generator_path = Path("/Volumes/DATA/Agent_Turbo/scripts/commit_message_generator.py")
            generator_path.write_text(generator_content)
            generator_path.chmod(0o755)
            
            print("✅ Commit message generator created")
            return True
            
        except Exception as e:
            print(f"❌ Commit message generator creation failed: {e}")
            return False
    
    def test_git_setup(self) -> bool:
        """Test Git setup functionality."""
        try:
            # Test Git aliases
            result = subprocess.run([
                "python3", "/Volumes/DATA/Agent_Turbo/scripts/git_aliases.py", "list"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ Git aliases test successful")
            else:
                print(f"❌ Git aliases test failed: {result.stderr}")
                return False
            
            # Test commit message generator
            result = subprocess.run([
                "python3", "/Volumes/DATA/Agent_Turbo/scripts/commit_message_generator.py", "templates"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ Commit message generator test successful")
                return True
            else:
                print(f"❌ Commit message generator test failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Git setup test failed: {e}")
            return False
    
    def setup_advanced_git(self) -> bool:
        """Complete advanced Git setup."""
        print("🚀 Setting up Advanced Git...")
        
        # Verify Git availability
        if not self.verify_git_availability():
            print("❌ TASK FAILED: Git not available")
            return False
        
        # Create Git directories
        if not self.create_git_directories():
            print("❌ TASK FAILED: Git directory creation failed")
            return False
        
        # Create Git config
        if not self.create_git_config():
            print("❌ TASK FAILED: Git config creation failed")
            return False
        
        # Create Git aliases
        if not self.create_git_aliases():
            print("❌ TASK FAILED: Git aliases creation failed")
            return False
        
        # Create Git hooks
        if not self.create_git_hooks():
            print("❌ TASK FAILED: Git hooks creation failed")
            return False
        
        # Create commit message generator
        if not self.create_commit_message_generator():
            print("❌ TASK FAILED: Commit message generator creation failed")
            return False
        
        # Test Git setup
        if not self.test_git_setup():
            print("❌ TASK FAILED: Git setup test failed")
            return False
        
        print("✅ Advanced Git setup complete")
        return True

def main():
    """Main execution."""
    setup = AdvancedGitSetup()
    success = setup.setup_advanced_git()
    
    if success:
        print("✅ Advanced Git implementation successful")
        return 0
    else:
        print("❌ TASK FAILED: Advanced Git setup failed")
        return 1

if __name__ == "__main__":
    exit(main())
