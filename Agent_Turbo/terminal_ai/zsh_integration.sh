# AGENT_TURBO Terminal AI Integration
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
