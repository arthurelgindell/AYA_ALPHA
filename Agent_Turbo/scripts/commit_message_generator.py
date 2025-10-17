#!/usr/bin/env python3
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
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                status, file_path = line.split('\t', 1)
                
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
