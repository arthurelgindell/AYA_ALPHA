#!/usr/bin/env python3
"""
Agent Turbo integration for n8n workflows
Enables n8n to create agent sessions, delegate tasks, and track execution

Usage:
    from agent_turbo_integration import N8NAgentTurboIntegration
    integration = N8NAgentTurboIntegration()
    session_id = integration.create_workflow_session('workflow_name', 'workflow_id')
"""

import sys
import os

# Add Agent Turbo to path
sys.path.insert(0, '/Users/arthurdell/AYA/Agent_Turbo/core')

import psycopg2
from datetime import datetime
import json


class N8NAgentTurboIntegration:
    """Integrate n8n workflows with Agent Turbo orchestration system"""
    
    def __init__(self, db_host='localhost', db_password='Power$$336633$$'):
        """
        Initialize integration with database connection
        
        Args:
            db_host: PostgreSQL host (default: localhost for ALPHA)
            db_password: Database password
        """
        self.db_config = {
            'host': db_host,
            'database': 'aya_rag',
            'user': 'postgres',
            'password': db_password,
            'port': 5432
        }
    
    def _get_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)
    
    def create_workflow_session(self, workflow_name, workflow_id):
        """
        Create agent session for n8n workflow
        
        Args:
            workflow_name: Human-readable workflow name
            workflow_id: Unique workflow identifier
            
        Returns:
            str: Created session ID
        """
        conn = self._get_connection()
        cur = conn.cursor()
        
        session_id = f"n8n_workflow_{workflow_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            cur.execute("""
                INSERT INTO agent_sessions (session_id, agent_platform, agent_role, status, landing_context)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING session_id
            """, (
                session_id, 
                'n8n', 
                'workflow_executor', 
                'active', 
                json.dumps({
                    'workflow_name': workflow_name, 
                    'workflow_id': workflow_id,
                    'created_at': datetime.now().isoformat()
                })
            ))
            
            conn.commit()
            result = cur.fetchone()[0]
            
            return result
        finally:
            cur.close()
            conn.close()
    
    def log_workflow_execution(self, workflow_id, execution_id, status, metadata=None):
        """
        Log workflow execution to database
        
        Args:
            workflow_id: Workflow identifier
            execution_id: Unique execution identifier
            status: Execution status (running, success, failed)
            metadata: Additional execution data (dict)
        """
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT INTO n8n_executions 
                (execution_id, workflow_id, status, started_at, metadata)
                VALUES (%s, %s, %s, NOW(), %s)
                ON CONFLICT (execution_id) DO UPDATE
                SET status = EXCLUDED.status,
                    metadata = EXCLUDED.metadata
            """, (
                execution_id, 
                workflow_id, 
                status, 
                json.dumps(metadata or {})
            ))
            
            conn.commit()
        finally:
            cur.close()
            conn.close()
    
    def update_execution_complete(self, execution_id, success, error_message=None, execution_time_ms=None):
        """
        Update execution as complete
        
        Args:
            execution_id: Execution identifier
            success: Boolean indicating success/failure
            error_message: Error message if failed
            execution_time_ms: Total execution time in milliseconds
        """
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                UPDATE n8n_executions
                SET finished_at = NOW(),
                    success = %s,
                    error_message = %s,
                    execution_time_ms = %s,
                    status = CASE WHEN %s THEN 'completed' ELSE 'failed' END
                WHERE execution_id = %s
            """, (success, error_message, execution_time_ms, success, execution_id))
            
            conn.commit()
        finally:
            cur.close()
            conn.close()
    
    def query_lm_studio(self, prompt, model='foundation-sec-8b-instruct-int8', max_tokens=500):
        """
        Query LM Studio for AI inference
        
        Args:
            prompt: Prompt text
            model: Model identifier
            max_tokens: Maximum tokens to generate
            
        Returns:
            dict: LM Studio response
        """
        import requests
        
        try:
            response = requests.post(
                'http://localhost:1234/v1/completions',
                json={
                    'model': model,
                    'prompt': prompt,
                    'max_tokens': max_tokens,
                    'temperature': 0.7
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def register_worker(self, worker_id, worker_type='n8n_worker', system_node='ALPHA'):
        """
        Register worker in coordination table
        
        Args:
            worker_id: Unique worker identifier
            worker_type: Worker type
            system_node: System where worker runs (ALPHA/BETA)
        """
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT INTO n8n_workers (worker_id, worker_type, status, system_node, last_heartbeat)
                VALUES (%s, %s, 'active', %s, NOW())
                ON CONFLICT (worker_id) DO UPDATE
                SET last_heartbeat = NOW(),
                    status = 'active'
            """, (worker_id, worker_type, system_node))
            
            conn.commit()
        finally:
            cur.close()
            conn.close()
    
    def worker_heartbeat(self, worker_id):
        """
        Update worker heartbeat
        
        Args:
            worker_id: Worker identifier
        """
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                UPDATE n8n_workers
                SET last_heartbeat = NOW()
                WHERE worker_id = %s
            """, (worker_id,))
            
            conn.commit()
        finally:
            cur.close()
            conn.close()


def test_integration():
    """Test the integration"""
    print("="*60)
    print("N8N AGENT TURBO INTEGRATION TEST")
    print("="*60)
    
    integration = N8NAgentTurboIntegration()
    
    # Test 1: Create workflow session
    print("\n1. Testing workflow session creation...")
    try:
        session_id = integration.create_workflow_session('test_workflow', 'test_001')
        print(f"   ✅ Created session: {session_id}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return
    
    # Test 1b: Register workflow in n8n_workflows table
    print("\n2. Registering workflow...")
    try:
        conn = integration._get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO n8n_workflows (workflow_id, workflow_name, agent_session_id, status)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (workflow_id) DO NOTHING
        """, ('test_001', 'test_workflow', session_id, 'active'))
        conn.commit()
        cur.close()
        conn.close()
        print(f"   ✅ Workflow registered")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return
    
    # Test 2: Log execution
    print("\n3. Testing execution logging...")
    try:
        integration.log_workflow_execution('test_001', 'exec_001', 'running', 
                                          {'test': 'data'})
        print(f"   ✅ Logged execution: exec_001")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return
    
    # Test 3: Update execution complete
    print("\n4. Testing execution completion...")
    try:
        integration.update_execution_complete('exec_001', True, None, 1500)
        print(f"   ✅ Updated execution as complete")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return
    
    # Test 4: Register worker
    print("\n5. Testing worker registration...")
    try:
        integration.register_worker('test_worker_001', 'test', 'ALPHA')
        print(f"   ✅ Registered worker: test_worker_001")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return
    
    # Test 5: LM Studio query (may fail if LM Studio not running)
    print("\n6. Testing LM Studio connection...")
    try:
        result = integration.query_lm_studio("Test prompt", max_tokens=10)
        if 'error' in result:
            print(f"   ⚠️  LM Studio not available: {result['error']}")
        else:
            print(f"   ✅ LM Studio responding")
    except Exception as e:
        print(f"   ⚠️  LM Studio test skipped: {e}")
    
    print("\n" + "="*60)
    print("INTEGRATION TEST COMPLETE")
    print("="*60)


if __name__ == '__main__':
    test_integration()

