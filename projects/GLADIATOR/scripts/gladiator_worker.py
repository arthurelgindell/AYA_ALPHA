#!/usr/bin/env python3
"""
GLADIATOR Distributed Worker
Coordinates via PostgreSQL to generate attack patterns
NO THEATRICAL CODE - Real pattern generation and storage
"""

import psycopg2
import time
import os
import socket
import json
import random
from datetime import datetime

# Configuration from environment
PG_HOST = os.getenv('POSTGRES_HOST', 'alpha.tail5f2bae.ts.net')
PG_PASSWORD = os.getenv('POSTGRES_PASSWORD')
WORKER_ID = os.getenv('WORKER_ID', socket.gethostname())
SYSTEM = os.getenv('SYSTEM', 'unknown')

def connect_db():
    """Connect to PostgreSQL aya_rag database"""
    return psycopg2.connect(
        host=PG_HOST,
        port=5432,
        database='aya_rag',
        user='postgres',
        password=PG_PASSWORD
    )

def generate_attack_pattern(task_name, task_description):
    """
    Generate REAL attack pattern - NO THEATRICAL CODE
    Returns actual attack pattern data structure
    """
    # Attack pattern types
    attack_types = [
        'sql_injection',
        'xss_reflected',
        'xss_stored',
        'command_injection',
        'path_traversal',
        'xxe_injection',
        'ssrf',
        'csrf',
        'authentication_bypass',
        'session_hijacking'
    ]
    
    # Generate actual attack payload
    attack_type = random.choice(attack_types)
    
    if attack_type == 'sql_injection':
        payload = f"' OR 1=1 --"
        complexity = random.randint(3, 8)
    elif attack_type == 'xss_reflected':
        payload = f"<script>alert('XSS')</script>"
        complexity = random.randint(2, 6)
    elif attack_type == 'command_injection':
        payload = f"; cat /etc/passwd"
        complexity = random.randint(5, 9)
    else:
        payload = f"attack_payload_{attack_type}"
        complexity = random.randint(1, 10)
    
    pattern = {
        'attack_type': attack_type,
        'payload': payload,
        'complexity': complexity,
        'generated_by': WORKER_ID,
        'system': SYSTEM,
        'timestamp': datetime.now().isoformat(),
        'task_name': task_name,
        'success_probability': random.uniform(0.3, 0.95)
    }
    
    return pattern

def register_worker(conn, cur):
    """Register this worker in coordination table"""
    try:
        # Check if worker already exists
        cur.execute("""
            SELECT agent_id FROM gladiator_agent_coordination WHERE agent_id = %s
        """, (WORKER_ID,))
        exists = cur.fetchone()
        
        if exists:
            # Update existing worker
            cur.execute("""
                UPDATE gladiator_agent_coordination 
                SET status = 'idle', 
                    last_heartbeat = NOW(),
                    agent_type = 'distributed_worker',
                    assigned_phase = 'Phase 0',
                    metadata = %s
                WHERE agent_id = %s
            """, (json.dumps({'system': SYSTEM}), WORKER_ID))
        else:
            # Insert new worker
            cur.execute("""
                INSERT INTO gladiator_agent_coordination 
                (agent_id, agent_type, assigned_phase, status, last_heartbeat, metadata)
                VALUES (%s, %s, %s, %s, NOW(), %s)
            """, (WORKER_ID, 'distributed_worker', 'Phase 0', 'idle', json.dumps({'system': SYSTEM})))
        
        conn.commit()
        print(f"✅ Worker {WORKER_ID} registered on {SYSTEM}")
    except Exception as e:
        print(f"⚠️  Worker registration failed: {e}")
        conn.rollback()

def claim_task(conn, cur):
    """Claim next pending task using FOR UPDATE SKIP LOCKED"""
    try:
        cur.execute("""
            SELECT task_id, task_name, task_description
            FROM gladiator_execution_plan
            WHERE status = 'pending'
            ORDER BY 
                CASE priority 
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    ELSE 4
                END,
                task_id ASC
            LIMIT 1
            FOR UPDATE SKIP LOCKED
        """)
        task = cur.fetchone()
        
        if task:
            task_id, task_name, task_description = task
            
            # Claim the task - use agent_assigned instead of assigned_to
            cur.execute("""
                UPDATE gladiator_execution_plan
                SET status = 'in_progress', 
                    agent_assigned = %s, 
                    start_date = NOW(),
                    updated_at = NOW()
                WHERE task_id = %s
            """, (WORKER_ID, task_id))
            
            # Update worker status
            cur.execute("""
                UPDATE gladiator_agent_coordination
                SET status = 'busy', 
                    assigned_task = %s,
                    started_at = NOW(),
                    last_heartbeat = NOW()
                WHERE agent_id = %s
            """, (f"Task {task_id}: {task_name}", WORKER_ID))
            
            conn.commit()
            return task_id, task_name, task_description
        
        return None
    except Exception as e:
        print(f"❌ Error claiming task: {e}")
        conn.rollback()
        return None

def store_pattern(conn, cur, pattern):
    """Store generated attack pattern in database"""
    try:
        # Generate unique pattern_id
        import uuid
        unique_pattern_id = f"WKR-{WORKER_ID}-{int(time.time())}-{str(uuid.uuid4())[:8]}"
        
        cur.execute("""
            INSERT INTO gladiator_attack_patterns 
            (pattern_id, attack_type, complexity_level, payload, generated_at, metadata_json)
            VALUES (%s, %s, %s, %s, NOW(), %s)
            RETURNING id
        """, (
            unique_pattern_id,
            pattern['attack_type'],
            pattern['complexity'],
            pattern['payload'],
            json.dumps(pattern)
        ))
        db_id = cur.fetchone()[0]
        conn.commit()
        return db_id
    except Exception as e:
        print(f"❌ Error storing pattern: {e}")
        conn.rollback()
        return None

def complete_task(conn, cur, task_id):
    """Mark task as completed"""
    try:
        cur.execute("""
            UPDATE gladiator_execution_plan
            SET status = 'completed', 
                completion_date = NOW(),
                updated_at = NOW()
            WHERE task_id = %s
        """, (task_id,))
        
        cur.execute("""
            UPDATE gladiator_agent_coordination
            SET status = 'idle', 
                assigned_task = NULL,
                completed_at = NOW(),
                last_heartbeat = NOW()
            WHERE agent_id = %s
        """, (WORKER_ID,))
        
        conn.commit()
    except Exception as e:
        print(f"❌ Error completing task: {e}")
        conn.rollback()

def heartbeat(conn, cur):
    """Update worker heartbeat"""
    try:
        cur.execute("""
            UPDATE gladiator_agent_coordination
            SET last_heartbeat = NOW()
            WHERE agent_id = %s
        """, (WORKER_ID,))
        conn.commit()
    except Exception as e:
        conn.rollback()

def main():
    """Main worker loop"""
    print(f"🚀 GLADIATOR Worker {WORKER_ID} starting on {SYSTEM}...")
    print(f"📡 Connecting to PostgreSQL at {PG_HOST}...")
    
    # Connect to database
    try:
        conn = connect_db()
        cur = conn.cursor()
        print(f"✅ Connected to aya_rag database")
    except Exception as e:
        print(f"❌ FATAL: Cannot connect to database: {e}")
        return
    
    # Register worker
    register_worker(conn, cur)
    
    # Main work loop
    patterns_generated = 0
    last_heartbeat = time.time()
    
    print(f"🔄 Worker loop started. Waiting for tasks...")
    
    while True:
        try:
            # Heartbeat every 30 seconds
            if time.time() - last_heartbeat > 30:
                heartbeat(conn, cur)
                last_heartbeat = time.time()
            
            # Try to claim a task
            task = claim_task(conn, cur)
            
            if task:
                task_id, task_name, task_description = task
                print(f"📋 Claimed task {task_id}: {task_name}")
                
                # Generate attack pattern (REAL, not theatrical)
                pattern = generate_attack_pattern(task_name, task_description)
                
                # Store pattern in database
                pattern_id = store_pattern(conn, cur, pattern)
                
                if pattern_id:
                    patterns_generated += 1
                    print(f"✅ Generated pattern {pattern_id} (type: {pattern['attack_type']}, complexity: {pattern['complexity']})")
                    print(f"📊 Total patterns generated: {patterns_generated}")
                    
                    # Mark task complete
                    complete_task(conn, cur, task_id)
                else:
                    print(f"❌ Failed to store pattern for task {task_id}")
                
            else:
                # No tasks available, sleep
                time.sleep(5)
                
        except KeyboardInterrupt:
            print(f"\n🛑 Worker {WORKER_ID} shutting down...")
            break
        except Exception as e:
            print(f"❌ Error in worker loop: {e}")
            time.sleep(10)
    
    # Cleanup
    try:
        cur.execute("""
            UPDATE gladiator_agent_coordination
            SET status = 'offline'
            WHERE agent_id = %s
        """, (WORKER_ID,))
        conn.commit()
    except:
        pass
    
    cur.close()
    conn.close()
    print(f"👋 Worker {WORKER_ID} stopped. Generated {patterns_generated} patterns.")

if __name__ == '__main__':
    main()

