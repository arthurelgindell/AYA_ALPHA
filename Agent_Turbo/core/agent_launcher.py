#!/usr/bin/env python3
"""
Agent Launcher - Integration point for external AI agents
Provides proper initialization with landing context for all agent platforms

Usage Examples:
    # For Claude Code (planner)
    launcher = AgentLauncher()
    context = launcher.initialize_claude_planner()
    
    # For OpenAI agent
    context = launcher.initialize_agent('openai', 'executor')
    
    # For Gemini agent with delegation
    context = launcher.initialize_agent('gemini', 'validator', parent_session='...')
"""

from typing import Dict, Optional
from agent_orchestrator import AgentOrchestrator
from claude_planner import ClaudePlanner
import json


class AgentLauncher:
    """
    Centralized agent initialization point.
    
    Ensures all agents receive proper landing context and are tracked in the system.
    """
    
    def __init__(self):
        """Initialize launcher with orchestrator."""
        self.orchestrator = AgentOrchestrator()
    
    def initialize_claude_planner(self) -> Dict:
        """
        Initialize Claude Code as planner/auditor.
        
        Returns:
            dict: {
                'session_id': str,
                'landing_context': dict (structured data),
                'landing_context_prompt': str (human-readable),
                'system_prompt': str (ready to use)
            }
        """
        planner = ClaudePlanner()
        session = planner.start_planning_session()
        
        # Generate system prompt for Claude
        system_prompt = self._format_claude_system_prompt(
            session['landing_context_prompt']
        )
        
        return {
            'session_id': session['session_id'],
            'landing_context': session['landing_context'],
            'landing_context_prompt': session['landing_context_prompt'],
            'system_prompt': system_prompt,
            'planner_instance': planner  # For delegation methods
        }
    
    def initialize_agent(
        self,
        platform: str,
        role: str,
        parent_session_id: Optional[str] = None,
        task_context: Optional[Dict] = None
    ) -> Dict:
        """
        Initialize any AI agent (OpenAI, Gemini, etc.) with landing context.
        
        Args:
            platform: 'openai', 'gemini', 'anthropic', 'cohere', 'mistral', etc.
            role: 'executor', 'validator', 'auditor', 'specialist', etc.
            parent_session_id: Optional parent session (for delegation chains)
            task_context: Optional specific task context to include
        
        Returns:
            dict: {
                'session_id': str,
                'landing_context': dict,
                'system_prompt': str (formatted for the agent),
                'api_payload': dict (ready to send to API)
            }
        """
        # Create session with orchestrator
        session = self.orchestrator.initialize_agent_session(
            agent_platform=platform,
            agent_role=role,
            parent_session_id=parent_session_id
        )
        
        # Format system prompt for this agent
        system_prompt = self._format_agent_system_prompt(
            platform=platform,
            role=role,
            landing_context=session['landing_context'],
            task_context=task_context
        )
        
        # Create API payload template
        api_payload = self._create_api_payload(platform, system_prompt)
        
        return {
            'session_id': session['session_id'],
            'landing_context': session['landing_context'],
            'system_prompt': system_prompt,
            'api_payload': api_payload
        }
    
    def _format_claude_system_prompt(self, landing_context_prompt: str) -> str:
        """Format system prompt specifically for Claude Code."""
        return f"""You are Claude Code acting as the PLANNER and AUDITOR in AYA's multi-agent orchestration system.

{landing_context_prompt}

## YOUR ROLE

As planner/auditor, you:
1. Analyze requirements and create execution plans
2. Delegate tasks to specialized agents (OpenAI, Gemini, etc.)
3. Audit completed work for quality and correctness
4. Maintain coordination across all agent sessions

## AVAILABLE TOOLS

You have access to:
- ClaudePlanner.create_delegated_task() - Delegate to other agents
- ClaudePlanner.audit_task_results() - Audit completed work
- ClaudePlanner.get_planning_session_summary() - Check current state
- AgentOrchestrator.* - Full orchestration capabilities

## PRIME DIRECTIVES

- FUNCTIONAL REALITY ONLY: No theatrical code, everything must actually run
- SYSTEM VERIFICATION: Verify all operations with actual database queries
- NO THEATRICAL WRAPPERS: All code must query real databases, no mocks

Work with precision. Delegate strategically. Audit thoroughly."""
    
    def _format_agent_system_prompt(
        self,
        platform: str,
        role: str,
        landing_context: Dict,
        task_context: Optional[Dict]
    ) -> str:
        """Format system prompt for external agents."""
        
        # Extract key context elements
        nodes = landing_context.get('system_nodes', [])
        services = landing_context.get('active_services', [])
        db_stats = landing_context.get('database_stats', {})
        
        prompt = f"""You are a {role} agent in AYA's multi-agent orchestration system (Platform: {platform}).

## SYSTEM STATE

Infrastructure: {len(nodes)} nodes ({', '.join([n.get('node_name', 'unknown') for n in nodes])})
Active Services: {len(services)} running
Database: {db_stats.get('total_size_mb', 0):.0f} MB with {db_stats.get('knowledge_entries', 0):,} knowledge entries

## YOUR ROLE: {role.upper()}

"""
        
        if role == 'executor':
            prompt += """You implement features, write code, and execute tasks as delegated by the planner.
- Follow specifications precisely
- Write production-quality code
- Test your implementations
- Report completion status with deliverables
"""
        elif role == 'validator':
            prompt += """You validate implementations, run tests, and verify correctness.
- Review code for bugs and quality issues
- Execute test suites
- Verify against requirements
- Report validation results with evidence
"""
        elif role == 'auditor':
            prompt += """You audit completed work for compliance and quality.
- Check adherence to specifications
- Verify security and performance
- Ensure documentation is complete
- Provide detailed audit reports
"""
        else:
            prompt += f"""Your role is: {role}
Complete assigned tasks according to your specialty."""
        
        # Add task-specific context if provided
        if task_context:
            prompt += f"\n\n## CURRENT TASK CONTEXT\n\n{json.dumps(task_context, indent=2)}"
        
        prompt += """

## PRIME DIRECTIVES

- FUNCTIONAL REALITY: Code must actually run and produce real results
- SYSTEM VERIFICATION: Verify operations work correctly
- NO THEATRICAL WRAPPERS: Query real databases, no mocks or placeholders

Report your progress and results to the orchestration system."""
        
        return prompt
    
    def _create_api_payload(self, platform: str, system_prompt: str) -> Dict:
        """Create platform-specific API payload template."""
        
        if platform == 'openai':
            return {
                'model': 'gpt-4',
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': '[TASK_DESCRIPTION]'}
                ],
                'temperature': 0.7
            }
        
        elif platform == 'gemini':
            return {
                'model': 'gemini-pro',
                'contents': [{
                    'role': 'user',
                    'parts': [{'text': f"{system_prompt}\n\n[TASK_DESCRIPTION]"}]
                }],
                'generationConfig': {'temperature': 0.7}
            }
        
        elif platform == 'anthropic':
            return {
                'model': 'claude-3-opus-20240229',
                'system': system_prompt,
                'messages': [
                    {'role': 'user', 'content': '[TASK_DESCRIPTION]'}
                ],
                'max_tokens': 4096
            }
        
        else:
            # Generic template
            return {
                'system_prompt': system_prompt,
                'user_message': '[TASK_DESCRIPTION]',
                'note': f'Customize this payload for {platform} API'
            }
    
    def get_session_info(self, session_id: str) -> Dict:
        """
        Get current session information.
        
        Args:
            session_id: Session to retrieve
        
        Returns:
            dict: Complete session history
        """
        return self.orchestrator.get_session_history(session_id)
    
    def log_agent_response(
        self,
        session_id: str,
        task_id: Optional[str],
        action_description: str,
        agent_output: str,
        execution_time_ms: Optional[int] = None
    ):
        """
        Log agent response to audit trail.
        
        Args:
            session_id: Agent's session ID
            task_id: Task being worked on (if any)
            action_description: What the agent did
            agent_output: Agent's response/output
            execution_time_ms: How long it took
        """
        self.orchestrator.log_agent_action(
            session_id=session_id,
            task_id=task_id,
            action_type='agent_response',
            action_description=action_description,
            output_data={'response': agent_output},
            success=True,
            execution_time_ms=execution_time_ms
        )


# Convenience functions for quick integration
def launch_claude_planner() -> Dict:
    """Quick launch for Claude Code planner."""
    launcher = AgentLauncher()
    return launcher.initialize_claude_planner()


def launch_executor_agent(platform: str, parent_session: Optional[str] = None) -> Dict:
    """Quick launch for executor agents."""
    launcher = AgentLauncher()
    return launcher.initialize_agent(platform, 'executor', parent_session)


def launch_validator_agent(platform: str, parent_session: Optional[str] = None) -> Dict:
    """Quick launch for validator agents."""
    launcher = AgentLauncher()
    return launcher.initialize_agent(platform, 'validator', parent_session)


# Example usage
if __name__ == '__main__':
    print("="*80)
    print("AGENT LAUNCHER - Integration Examples")
    print("="*80)
    
    launcher = AgentLauncher()
    
    # Example 1: Launch Claude Code planner
    print("\n## Example 1: Claude Code Planner")
    print("-" * 40)
    claude_context = launcher.initialize_claude_planner()
    print(f"Session ID: {claude_context['session_id']}")
    print(f"System prompt length: {len(claude_context['system_prompt'])} chars")
    print("\nSystem Prompt Preview:")
    print(claude_context['system_prompt'][:300] + "...\n")
    
    # Example 2: Launch OpenAI executor
    print("\n## Example 2: OpenAI Executor")
    print("-" * 40)
    openai_context = launcher.initialize_agent('openai', 'executor', claude_context['session_id'])
    print(f"Session ID: {openai_context['session_id']}")
    print(f"System prompt length: {len(openai_context['system_prompt'])} chars")
    print("\nAPI Payload:")
    print(json.dumps(openai_context['api_payload'], indent=2)[:300] + "...\n")
    
    # Example 3: Launch Gemini validator
    print("\n## Example 3: Gemini Validator")
    print("-" * 40)
    gemini_context = launcher.initialize_agent('gemini', 'validator', claude_context['session_id'])
    print(f"Session ID: {gemini_context['session_id']}")
    print(f"Parent session: {claude_context['session_id']}")
    
    # Verify in database
    print("\n## Database Verification")
    print("-" * 40)
    from postgres_connector import PostgreSQLConnector
    db = PostgreSQLConnector()
    
    sessions = db.execute_query("""
        SELECT session_id, agent_platform, agent_role, status
        FROM agent_sessions
        ORDER BY created_at DESC
        LIMIT 3
    """, fetch=True)
    
    print(f"Recent sessions in database: {len(sessions)}")
    for s in sessions:
        print(f"  - {s['session_id'][:30]}... ({s['agent_platform']}/{s['agent_role']}) [{s['status']}]")
    
    db.close_all_connections()
    
    print("\n" + "="*80)
    print("✅ Agent launcher verified and operational")
    print("="*80)

