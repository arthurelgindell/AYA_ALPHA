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
    
    
    def validate_agent_platform(self, agent_platform: str, agent_role: str) -> tuple:
        """
        Validate agent platform and role combination.
        
        Architecture (Oct 2025 - Clean Slate Reconfiguration):
        - PRIMARY: cursor, claude (main workflow agents)
        - AUDIT: gemini, codex (supplementary verification only)
        - SYSTEM: n8n (workflow automation)
        
        Args:
            agent_platform: Platform ID
            agent_role: Role
            
        Returns:
            tuple: (is_valid, error_message)
        """
        ALLOWED_PLATFORMS = {
            'cursor': {'roles': ['planner', 'executor', 'developer'], 'type': 'primary'},
            'claude': {'roles': ['planner', 'orchestrator', 'architect'], 'type': 'primary'},
            'gemini': {'roles': ['auditor', 'validator'], 'type': 'audit'},
            'codex': {'roles': ['auditor', 'validator'], 'type': 'audit'},
            'n8n': {'roles': ['workflow_executor'], 'type': 'system'},
        }
        
        if agent_platform not in ALLOWED_PLATFORMS:
            return False, f"Platform '{agent_platform}' not allowed. Use: {', '.join(ALLOWED_PLATFORMS.keys())}"
        
        platform_config = ALLOWED_PLATFORMS[agent_platform]
        if agent_role not in platform_config['roles']:
            return False, f"Role '{agent_role}' not valid for {agent_platform}. Allowed: {', '.join(platform_config['roles'])}"
        
        if platform_config['type'] == 'audit':
            print(f"⚠️  {agent_platform} is audit-only (supplementary use)", flush=True)
        
        return True, ""

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
                    storage_external_tb,
                    storage_external_device,
                    model_name,
                    gpu_model,
                    gpu_cores,
                    metadata->>'working_path' as working_path,
                    status
                FROM system_nodes
                WHERE status = 'active'
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
        
        Architecture enforced: cursor/claude (primary), gemini/codex (audit only)
        
        Args:
            agent_platform: Platform ID ('cursor', 'claude', 'gemini', 'codex', 'n8n')
            agent_role: Role (varies by platform)
            parent_session_id: Optional parent session for delegation chains
        
        Returns:
            dict: Session info with session_id and landing_context
        """
        # Validate platform and role
        is_valid, error_msg = self.validate_agent_platform(agent_platform, agent_role)
        if not is_valid:
            raise ValueError(f"Agent platform validation failed: {error_msg}")

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

