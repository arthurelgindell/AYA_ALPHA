#!/usr/bin/env python3
"""
Claude Code Planner Interface
Specialized interface for Claude Code to act as planner/auditor in multi-agent orchestration

Prime Directives Compliance:
- Directive #1: FUNCTIONAL REALITY - All operations use actual orchestrator and database
- Directive #11: NO THEATRICAL WRAPPERS - Real planning, real delegation, real auditing
"""

from typing import Dict, List, Optional
from agent_orchestrator import AgentOrchestrator


class ClaudePlanner:
    """
    Claude Code planner interface for multi-agent orchestration.
    
    Features:
    - Planning session initialization with full landing context
    - Human-readable landing context formatting
    - Task delegation to other agents
    - Audit trail for completed tasks
    - Session management
    """
    
    def __init__(self):
        """Initialize Claude planner with orchestrator."""
        self.orchestrator = AgentOrchestrator()
        self.current_session_id = None
    
    def start_planning_session(self) -> Dict:
        """
        Start a new planning session for Claude Code.
        
        Returns:
            dict: Session info with formatted landing context prompt
        """
        # Initialize session as planner
        session = self.orchestrator.initialize_agent_session(
            agent_platform='claude_code',
            agent_role='planner'
        )
        
        self.current_session_id = session['session_id']
        
        # Format landing context into human-readable prompt
        landing_context_prompt = self.format_landing_context(session['landing_context'])
        
        return {
            'session_id': session['session_id'],
            'landing_context': session['landing_context'],
            'landing_context_prompt': landing_context_prompt,
            'created_at': session['created_at']
        }
    
    def format_landing_context(self, context: Dict) -> str:
        """
        Format landing context into human-readable prompt for Claude Code.
        
        Args:
            context: Raw landing context from orchestrator
        
        Returns:
            str: Formatted prompt text
        """
        lines = []
        lines.append("=" * 80)
        lines.append("AYA SYSTEM STATE - LANDING CONTEXT")
        lines.append("=" * 80)
        lines.append("")
        
        # 1. System Nodes
        if context.get('system_nodes'):
            lines.append("## INFRASTRUCTURE")
            lines.append("")
            for node in context['system_nodes']:
                lines.append(f"Node: {node.get('node_name', 'Unknown')}")
                lines.append(f"  Role: {node.get('node_role', 'Unknown')}")
                lines.append(f"  Model: {node.get('model_name', 'Unknown')}")
                lines.append(f"  CPU: {node.get('cpu_model', 'Unknown')} ({node.get('cpu_cores', 0)} cores)")
                if node.get('gpu_model'):
                    lines.append(f"  GPU: {node.get('gpu_model')}")
                lines.append(f"  RAM: {node.get('ram_gb', 0)} GB")
                lines.append(f"  Storage: {node.get('storage_internal_tb', 0)} TB")
                lines.append("")
        
        # 2. Active Services
        if context.get('active_services'):
            lines.append("## ACTIVE SERVICES")
            lines.append("")
            for svc in context['active_services']:
                port_info = f":{svc.get('port')}" if svc.get('port') else ""
                node_info = f" on {svc.get('node_name')}" if svc.get('node_name') else ""
                lines.append(f"  - {svc.get('service_name')}{port_info} ({svc.get('service_type', 'unknown')}){node_info}")
            lines.append("")
        
        # 3. Documentation Sources
        if context.get('documentation_sources'):
            lines.append("## KNOWLEDGE BASE")
            lines.append("")
            for doc in context['documentation_sources'][:10]:  # Top 10
                project = doc.get('source_project', 'unknown')
                table = doc.get('source_table', 'unknown')
                count = doc.get('chunk_count', 0)
                lines.append(f"  - {project}/{table}: {count:,} chunks")
            lines.append("")
        
        # 4. Database Stats
        if context.get('database_stats'):
            stats = context['database_stats']
            lines.append("## DATABASE METRICS")
            lines.append("")
            lines.append(f"  Total Size: {stats.get('total_size_mb', 0):.1f} MB")
            lines.append(f"  Documents: {stats.get('total_documents', 0):,}")
            lines.append(f"  Chunks: {stats.get('total_chunks', 0):,}")
            lines.append(f"  Knowledge Entries: {stats.get('knowledge_entries', 0):,}")
            lines.append(f"  Agent Sessions: {stats.get('total_sessions', 0)}")
            lines.append(f"  Agent Tasks: {stats.get('total_tasks', 0)}")
            lines.append("")
        
        # 5. Recent Tasks
        if context.get('recent_tasks'):
            lines.append("## RECENT AGENT TASKS")
            lines.append("")
            for task in context['recent_tasks'][:5]:  # Last 5
                lines.append(f"  [{task.get('status', 'unknown')}] {task.get('task_type')}: {task.get('task_description', '')[:60]}...")
            lines.append("")
        
        # 6. Timestamp
        lines.append(f"Generated: {context.get('generated_at', 'Unknown')}")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def create_delegated_task(
        self,
        task_description: str,
        task_type: str,
        assigned_to_role: str,
        priority: int = 5,
        depends_on_tasks: Optional[List[str]] = None,
        required_context: Optional[Dict] = None
    ) -> str:
        """
        Delegate a task to another agent.
        
        Args:
            task_description: Human-readable task description
            task_type: Type of task ('code_review', 'implementation', 'testing', etc.)
            assigned_to_role: Target agent role ('executor', 'validator', etc.)
            priority: Priority 1-10 (10 = highest)
            depends_on_tasks: List of task_ids this depends on
            required_context: Additional context for the task
        
        Returns:
            str: task_id
        """
        if not self.current_session_id:
            raise Exception("No active planning session. Call start_planning_session() first.")
        
        # Create task via orchestrator
        task_id = self.orchestrator.create_task(
            session_id=self.current_session_id,
            task_type=task_type,
            task_description=task_description,
            assigned_to_role=assigned_to_role,
            priority=priority,
            depends_on_tasks=depends_on_tasks,
            required_context=required_context
        )
        
        # Log the delegation action
        self.orchestrator.log_agent_action(
            session_id=self.current_session_id,
            task_id=task_id,
            action_type='task_delegation',
            action_description=f"Delegated task to {assigned_to_role}: {task_description}",
            input_data={
                'task_type': task_type,
                'assigned_to_role': assigned_to_role,
                'priority': priority
            },
            success=True
        )
        
        return task_id
    
    def audit_task_results(
        self,
        task_id: str,
        audit_status: str,
        audit_notes: str,
        approved: bool
    ) -> bool:
        """
        Audit completed task results as planner.
        
        Args:
            task_id: Task to audit
            audit_status: Audit outcome ('approved', 'rejected', 'needs_revision')
            audit_notes: Detailed audit notes
            approved: Whether task is approved
        
        Returns:
            bool: Success
        """
        if not self.current_session_id:
            raise Exception("No active planning session. Call start_planning_session() first.")
        
        # Update task status based on audit
        new_status = 'completed' if approved else 'blocked'
        success = self.orchestrator.update_task_status(
            task_id=task_id,
            status=new_status,
            output_data={
                'audit_status': audit_status,
                'audit_notes': audit_notes,
                'approved': approved,
                'audited_by': self.current_session_id
            }
        )
        
        # Log audit action
        self.orchestrator.log_agent_action(
            session_id=self.current_session_id,
            task_id=task_id,
            action_type='task_audit',
            action_description=f"Audited task: {audit_status}",
            input_data={
                'task_id': task_id,
                'audit_status': audit_status,
                'approved': approved
            },
            output_data={
                'audit_notes': audit_notes
            },
            success=True
        )
        
        return success
    
    def get_planning_session_summary(self) -> Dict:
        """
        Get summary of current planning session.
        
        Returns:
            dict: Session summary with tasks and actions
        """
        if not self.current_session_id:
            return {'error': 'No active planning session'}
        
        history = self.orchestrator.get_session_history(self.current_session_id)
        
        # Summarize tasks by status
        task_summary = {
            'total': len(history['tasks']),
            'by_status': {},
            'by_role': {}
        }
        
        for task in history['tasks']:
            status = task.get('status', 'unknown')
            role = task.get('assigned_to_role', 'unknown')
            task_summary['by_status'][status] = task_summary['by_status'].get(status, 0) + 1
            task_summary['by_role'][role] = task_summary['by_role'].get(role, 0) + 1
        
        return {
            'session_id': self.current_session_id,
            'task_summary': task_summary,
            'total_actions': len(history['actions']),
            'recent_tasks': history['tasks'][:5],
            'recent_actions': history['actions'][:5]
        }


# Verification function
def verify_claude_planner():
    """
    Verify Claude planner functionality with end-to-end workflow.
    
    Prime Directive #1: Tests actual database operations.
    """
    print("🔍 Verifying Claude Planner...")
    
    try:
        planner = ClaudePlanner()
        
        # Test 1: Start planning session
        print("\n✅ Test 1: Start planning session")
        session = planner.start_planning_session()
        print(f"   Session ID: {session['session_id']}")
        print(f"   Landing context length: {len(session['landing_context_prompt'])} chars")
        print("\n   Landing Context Preview (first 500 chars):")
        print(session['landing_context_prompt'][:500])
        print("   ...")
        
        # Test 2: Delegate task
        print("\n✅ Test 2: Delegate task to executor")
        task_id = planner.create_delegated_task(
            task_description="Implement feature X according to specifications",
            task_type="implementation",
            assigned_to_role="executor",
            priority=8,
            required_context={'spec_version': '2.0'}
        )
        print(f"   Task ID: {task_id}")
        
        # Test 3: Delegate another task
        print("\n✅ Test 3: Delegate task to validator")
        task_id_2 = planner.create_delegated_task(
            task_description="Validate implementation of feature X",
            task_type="validation",
            assigned_to_role="validator",
            priority=7,
            depends_on_tasks=[task_id]
        )
        print(f"   Task ID: {task_id_2}")
        
        # Test 4: Audit task
        print("\n✅ Test 4: Audit task results")
        audit_success = planner.audit_task_results(
            task_id=task_id,
            audit_status="approved",
            audit_notes="Implementation meets all requirements. Code quality is excellent.",
            approved=True
        )
        print(f"   Audit success: {audit_success}")
        
        # Test 5: Get session summary
        print("\n✅ Test 5: Get planning session summary")
        summary = planner.get_planning_session_summary()
        print(f"   Total tasks: {summary['task_summary']['total']}")
        print(f"   Total actions: {summary['total_actions']}")
        print(f"   Tasks by status: {summary['task_summary']['by_status']}")
        print(f"   Tasks by role: {summary['task_summary']['by_role']}")
        
        # Test 6: Verify in database
        print("\n✅ Test 6: Verify data in database")
        from postgres_connector import PostgreSQLConnector
        db = PostgreSQLConnector()
        
        # Verify session exists
        session_check = db.execute_query("""
            SELECT session_id, agent_platform, agent_role, status
            FROM agent_sessions
            WHERE session_id = %s
        """, (session['session_id'],), fetch=True)
        print(f"   Session in DB: {session_check[0] if session_check else 'NOT FOUND'}")
        
        # Verify tasks exist
        tasks_check = db.execute_query("""
            SELECT task_id, task_type, status
            FROM agent_tasks
            WHERE session_id = %s
            ORDER BY created_at
        """, (session['session_id'],), fetch=True)
        print(f"   Tasks in DB: {len(tasks_check)}")
        for t in tasks_check:
            print(f"     - {t['task_id'][:15]}... ({t['task_type']}) [{t['status']}]")
        
        # Verify actions exist
        actions_check = db.execute_query("""
            SELECT action_type, success
            FROM agent_actions
            WHERE session_id = %s
        """, (session['session_id'],), fetch=True)
        print(f"   Actions in DB: {len(actions_check)}")
        
        db.close_all_connections()
        
        print("\n✅ CLAUDE PLANNER: VERIFIED AND OPERATIONAL")
        return True
        
    except Exception as e:
        print(f"\n❌ VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    import sys
    success = verify_claude_planner()
    sys.exit(0 if success else 1)

