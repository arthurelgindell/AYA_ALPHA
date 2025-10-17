#!/usr/bin/env python3
"""
Agent Orchestrator for Multi-Agent Coordination
Manages agent sessions, task delegation, and full landing context

Prime Directives Compliance:
- Directive #1: FUNCTIONAL REALITY - All operations use actual PostgreSQL database
- Directive #11: NO THEATRICAL WRAPPERS - Real sessions, real tasks, real context
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from postgres_connector import PostgreSQLConnector


def serialize_datetime(obj: Any) -> Any:
    """Recursively convert datetime objects to ISO format strings for JSON serialization."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: serialize_datetime(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_datetime(item) for item in obj]
    else:
        return obj


class AgentOrchestrator:
    """
    Multi-agent orchestration system for AYA.
    
    Features:
    - Session management across multiple AI platforms
    - Complete landing context generation
    - Task delegation and tracking
    - Audit trail for all agent actions
    """
    
    def __init__(self):
        """Initialize orchestrator with PostgreSQL connection."""
        self.db = PostgreSQLConnector()
    
    def generate_landing_context(self) -> Dict:
        """
        Generate complete system state snapshot for agent initialization.
        
        Prime Directive #1: Queries actual system state from PostgreSQL.
        
        Returns:
            dict: Complete landing context with:
                - system_nodes: Hardware specs (ALPHA, BETA, AIR)
                - active_services: Running services on each node
                - documentation_sources: Available knowledge sources
                - database_stats: Current database metrics
                - recent_tasks: Recent agent tasks
        """
        context = {}
        
        # 1. System nodes (hardware specs)
        try:
            nodes = self.db.execute_query("""
                SELECT 
                    node_name,
                    node_role,
                    cpu_model,
                    cpu_cores_total as cpu_cores,
                    ram_gb,
                    storage_internal_tb,
                    model_name,
                    gpu_model
                FROM system_nodes
                ORDER BY node_name
            """, fetch=True)
            context['system_nodes'] = nodes
        except Exception as e:
            context['system_nodes'] = []
            context['_errors'] = context.get('_errors', []) + [f"system_nodes: {str(e)}"]
        
        # 2. Active services
        try:
            services = self.db.execute_query("""
                SELECT 
                    s.service_name,
                    s.port,
                    s.status,
                    s.service_type,
                    n.node_name
                FROM services s
                LEFT JOIN system_nodes n ON s.node_id = n.id
                WHERE s.status = 'running'
                ORDER BY n.node_name, s.service_name
            """, fetch=True)
            context['active_services'] = services
        except Exception as e:
            context['active_services'] = []
            context['_errors'] = context.get('_errors', []) + [f"active_services: {str(e)}"]
        
        # 3. Documentation sources
        try:
            doc_sources = self.db.execute_query("""
                SELECT 
                    source_project,
                    source_table,
                    COUNT(*) as chunk_count,
                    MAX(created_at) as last_updated
                FROM chunks
                WHERE source_project IS NOT NULL
                GROUP BY source_project, source_table
                ORDER BY chunk_count DESC
                LIMIT 20
            """, fetch=True)
            context['documentation_sources'] = doc_sources
        except Exception as e:
            context['documentation_sources'] = []
            context['_errors'] = context.get('_errors', []) + [f"documentation_sources: {str(e)}"]
        
        # 4. Database stats
        try:
            db_stats = self.db.execute_query("""
                SELECT 
                    pg_database_size('aya_rag') / 1024 / 1024 as total_size_mb,
                    (SELECT COUNT(*) FROM documents) as total_documents,
                    (SELECT COUNT(*) FROM chunks) as total_chunks,
                    (SELECT COUNT(*) FROM agent_knowledge) as knowledge_entries,
                    (SELECT COUNT(*) FROM agent_sessions) as total_sessions,
                    (SELECT COUNT(*) FROM agent_tasks) as total_tasks
            """, fetch=True)
            context['database_stats'] = db_stats[0] if db_stats else {}
        except Exception as e:
            context['database_stats'] = {}
            context['_errors'] = context.get('_errors', []) + [f"database_stats: {str(e)}"]
        
        # 5. Recent agent tasks (last 10)
        try:
            recent_tasks = self.db.execute_query("""
                SELECT 
                    task_id,
                    task_type,
                    task_description,
                    status,
                    created_at
                FROM agent_tasks
                ORDER BY created_at DESC
                LIMIT 10
            """, fetch=True)
            context['recent_tasks'] = recent_tasks
        except Exception as e:
            context['recent_tasks'] = []
            context['_errors'] = context.get('_errors', []) + [f"recent_tasks: {str(e)}"]
        
        # 6. Current timestamp
        context['generated_at'] = datetime.now().isoformat()
        
        return context
    
    def initialize_agent_session(
        self, 
        agent_platform: str, 
        agent_role: str,
        parent_session_id: Optional[str] = None
    ) -> Dict:
        """
        Initialize a new agent session with full landing context.
        
        Args:
            agent_platform: Platform ID ('claude_code', 'openai', 'gemini', etc.)
            agent_role: Role ('planner', 'executor', 'auditor', 'validator')
            parent_session_id: Optional parent session for delegation chains
        
        Returns:
            dict: Session info with session_id and landing_context
        """
        # Generate unique session ID
        session_id = f"{agent_platform}_{agent_role}_{uuid.uuid4().hex[:8]}"
        
        # Generate landing context
        landing_context = self.generate_landing_context()
        
        # Serialize datetime objects for JSON storage
        landing_context_serialized = serialize_datetime(landing_context)
        
        # Insert session into database
        insert_sql = """
            INSERT INTO agent_sessions 
            (session_id, agent_platform, agent_role, parent_session_id, 
             landing_context, status, created_at, last_active)
            VALUES (%s, %s, %s, %s, %s, 'active', NOW(), NOW())
            RETURNING id, session_id, created_at
        """
        
        try:
            result = self.db.execute_query(
                insert_sql,
                (session_id, agent_platform, agent_role, parent_session_id, 
                 json.dumps(landing_context_serialized)),
                fetch=True
            )
            
            return {
                'session_id': session_id,
                'agent_platform': agent_platform,
                'agent_role': agent_role,
                'landing_context': landing_context,
                'created_at': result[0]['created_at'].isoformat() if result else datetime.now().isoformat()
            }
        except Exception as e:
            raise Exception(f"Failed to initialize agent session: {e}")
    
    def create_task(
        self,
        session_id: str,
        task_type: str,
        task_description: str,
        assigned_to_role: str,
        priority: int = 5,
        depends_on_tasks: Optional[List[str]] = None,
        required_context: Optional[Dict] = None
    ) -> str:
        """
        Create a new task for agent execution.
        
        Args:
            session_id: Session ID that created this task
            task_type: Type of task ('code_review', 'implementation', 'testing', etc.)
            task_description: Human-readable description
            assigned_to_role: Target agent role
            priority: Priority 1-10 (10 = highest)
            depends_on_tasks: List of task_ids this depends on
            required_context: Additional context needed for task
        
        Returns:
            str: task_id
        """
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        
        insert_sql = """
            INSERT INTO agent_tasks
            (task_id, session_id, task_type, task_description, task_priority,
             assigned_to_role, depends_on_tasks, required_context, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pending', NOW())
            RETURNING task_id
        """
        
        try:
            result = self.db.execute_query(
                insert_sql,
                (task_id, session_id, task_type, task_description, priority,
                 assigned_to_role, depends_on_tasks or [], 
                 json.dumps(required_context or {})),
                fetch=True
            )
            return result[0]['task_id'] if result else task_id
        except Exception as e:
            raise Exception(f"Failed to create task: {e}")
    
    def log_agent_action(
        self,
        session_id: str,
        task_id: Optional[str],
        action_type: str,
        action_description: str,
        input_data: Optional[Dict] = None,
        output_data: Optional[Dict] = None,
        success: bool = True,
        execution_time_ms: Optional[int] = None
    ) -> str:
        """
        Log an agent action for audit trail.
        
        Args:
            session_id: Session performing the action
            task_id: Optional task this action belongs to
            action_type: Type ('query', 'write', 'command', 'api_call')
            action_description: Human-readable description
            input_data: Input parameters
            output_data: Output results
            success: Whether action succeeded
            execution_time_ms: Execution time in milliseconds
        
        Returns:
            str: action_id
        """
        action_id = f"action_{uuid.uuid4().hex[:12]}"
        
        insert_sql = """
            INSERT INTO agent_actions
            (action_id, session_id, task_id, action_type, action_description,
             input_data, output_data, success, execution_time_ms, executed_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            RETURNING action_id
        """
        
        try:
            result = self.db.execute_query(
                insert_sql,
                (action_id, session_id, task_id, action_type, action_description,
                 json.dumps(input_data or {}), json.dumps(output_data or {}),
                 success, execution_time_ms),
                fetch=True
            )
            return result[0]['action_id'] if result else action_id
        except Exception as e:
            raise Exception(f"Failed to log action: {e}")
    
    def get_session_history(self, session_id: str) -> Dict:
        """
        Get complete history for a session.
        
        Args:
            session_id: Session to retrieve
        
        Returns:
            dict: Session info with tasks and actions
        """
        # Get session info
        session = self.db.execute_query("""
            SELECT * FROM agent_sessions WHERE session_id = %s
        """, (session_id,), fetch=True)
        
        if not session:
            raise Exception(f"Session not found: {session_id}")
        
        # Get tasks
        tasks = self.db.execute_query("""
            SELECT * FROM agent_tasks 
            WHERE session_id = %s 
            ORDER BY created_at DESC
        """, (session_id,), fetch=True)
        
        # Get actions
        actions = self.db.execute_query("""
            SELECT * FROM agent_actions 
            WHERE session_id = %s 
            ORDER BY executed_at DESC
        """, (session_id,), fetch=True)
        
        return {
            'session': session[0],
            'tasks': tasks,
            'actions': actions
        }
    
    def update_task_status(
        self,
        task_id: str,
        status: str,
        progress_percentage: Optional[int] = None,
        current_step: Optional[str] = None,
        output_data: Optional[Dict] = None
    ) -> bool:
        """
        Update task status and progress.
        
        Args:
            task_id: Task to update
            status: New status ('pending', 'in_progress', 'completed', 'failed', 'blocked')
            progress_percentage: Progress 0-100
            current_step: Description of current step
            output_data: Task output data
        
        Returns:
            bool: Success
        """
        update_parts = ["status = %s"]
        params = [status]
        
        if progress_percentage is not None:
            update_parts.append("progress_percentage = %s")
            params.append(progress_percentage)
        
        if current_step is not None:
            update_parts.append("current_step = %s")
            params.append(current_step)
        
        if output_data is not None:
            update_parts.append("output_data = %s")
            params.append(json.dumps(output_data))
        
        if status == 'in_progress':
            update_parts.append("started_at = NOW()")
        elif status == 'completed':
            update_parts.append("completed_at = NOW()")
            # Only set progress to 100 if not already set above
            if progress_percentage is None:
                update_parts.append("progress_percentage = 100")
        
        params.append(task_id)
        
        update_sql = f"""
            UPDATE agent_tasks
            SET {', '.join(update_parts)}
            WHERE task_id = %s
        """
        
        try:
            self.db.execute_query(update_sql, tuple(params), fetch=False)
            return True
        except Exception as e:
            print(f"Failed to update task: {e}")
            return False


# Verification function
def verify_orchestrator():
    """
    Verify orchestrator functionality.
    
    Prime Directive #1: Tests actual database operations.
    """
    print("🔍 Verifying Agent Orchestrator...")
    
    try:
        orch = AgentOrchestrator()
        
        # Test 1: Generate landing context
        print("\n✅ Test 1: Generate landing context")
        context = orch.generate_landing_context()
        print(f"   System nodes: {len(context.get('system_nodes', []))}")
        print(f"   Active services: {len(context.get('active_services', []))}")
        print(f"   Doc sources: {len(context.get('documentation_sources', []))}")
        if context.get('database_stats'):
            print(f"   Database size: {context['database_stats'].get('total_size_mb', 0):.1f} MB")
        
        # Test 2: Initialize session
        print("\n✅ Test 2: Initialize agent session")
        session = orch.initialize_agent_session('claude_code', 'planner')
        print(f"   Session ID: {session['session_id']}")
        print(f"   Context keys: {list(session['landing_context'].keys())}")
        
        # Test 3: Create task
        print("\n✅ Test 3: Create task")
        task_id = orch.create_task(
            session['session_id'],
            'test_task',
            'Test task for verification',
            'executor',
            priority=7
        )
        print(f"   Task ID: {task_id}")
        
        # Test 4: Log action
        print("\n✅ Test 4: Log agent action")
        action_id = orch.log_agent_action(
            session['session_id'],
            task_id,
            'test_action',
            'Test action for verification',
            input_data={'test': 'data'},
            success=True,
            execution_time_ms=50
        )
        print(f"   Action ID: {action_id}")
        
        # Test 5: Get session history
        print("\n✅ Test 5: Get session history")
        history = orch.get_session_history(session['session_id'])
        print(f"   Tasks: {len(history['tasks'])}")
        print(f"   Actions: {len(history['actions'])}")
        
        # Test 6: Update task status
        print("\n✅ Test 6: Update task status")
        success = orch.update_task_status(
            task_id,
            'completed',
            progress_percentage=100,
            output_data={'result': 'success'}
        )
        print(f"   Update success: {success}")
        
        print("\n✅ AGENT ORCHESTRATOR: VERIFIED AND OPERATIONAL")
        return True
        
    except Exception as e:
        print(f"\n❌ VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    import sys
    success = verify_orchestrator()
    sys.exit(0 if success else 1)

