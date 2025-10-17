#!/usr/bin/env python3
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
