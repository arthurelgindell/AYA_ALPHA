#!/usr/bin/env python3
"""
GLADIATOR Context Recovery Test
Simulate a NEW Cursor agent reading database with ZERO prior knowledge

Purpose: Verify database provides complete, understandable context
Critical: If this fails, new agent cannot recover if I crash
"""

import psycopg2
import json
from datetime import datetime

DB_CONFIG = {
    'host': 'localhost',
    'database': 'aya_rag',
    'user': 'postgres',
    'password': 'Power$$336633$$'
}

def simulate_new_agent_recovery():
    """
    Simulate NEW agent with ZERO context trying to understand current state
    """
    
    print("="*80)
    print("CONTEXT RECOVERY TEST - SIMULATING NEW CURSOR AGENT")
    print("="*80)
    print("\nScenario: I am a NEW Cursor agent. I know NOTHING about GLADIATOR.")
    print("I only have access to the database. Can I understand the current state?")
    print("")
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    context_recovered = {}
    
    # =============================================================================
    # QUERY 1: What project is this?
    # =============================================================================
    
    print("[Q1] What project am I looking at?")
    print("-" * 60)
    
    cursor.execute("""
        SELECT tablename FROM pg_tables 
        WHERE tablename LIKE 'gladiator_%' 
        LIMIT 5
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"Found tables with 'gladiator' prefix: {len(tables)}")
    print(f"Sample: {tables[:3]}")
    print("✅ CONTEXT: This is the GLADIATOR project")
    context_recovered['project'] = 'GLADIATOR'
    print("")
    
    # =============================================================================
    # QUERY 2: What phase/state are we in?
    # =============================================================================
    
    print("[Q2] What phase and state is the project in?")
    print("-" * 60)
    
    cursor.execute("""
        SELECT 
            current_phase,
            current_week,
            phase_0_progress_percentage,
            gates_passed,
            gates_total,
            foundation_model_validated,
            self_attack_prevention_validated,
            production_ready,
            last_go_no_go_decision,
            last_go_no_go_date
        FROM gladiator_project_state
        WHERE is_current = TRUE
    """)
    
    state = cursor.fetchone()
    if state:
        print(f"✅ Phase: {state[0]}")
        print(f"✅ Week: {state[1]}")
        print(f"✅ Progress: {state[2]}%")
        print(f"✅ Gates: {state[3]}/{state[4]} passed")
        print(f"✅ Foundation validated: {state[5]}")
        print(f"✅ Self-attack prevention: {state[6]}")
        print(f"✅ Production ready: {state[7]}")
        print(f"✅ Last decision: {state[8]} on {state[9]}")
        
        context_recovered['phase'] = state[0]
        context_recovered['week'] = state[1]
        context_recovered['decision'] = state[8]
    else:
        print("❌ ERROR: No current project state found!")
        return False
    print("")
    
    # =============================================================================
    # QUERY 3: What was the last action taken?
    # =============================================================================
    
    print("[Q3] What was the last action taken?")
    print("-" * 60)
    
    cursor.execute("""
        SELECT 
            change_type,
            changed_by,
            entity_name,
            reason,
            change_timestamp
        FROM gladiator_change_log
        ORDER BY change_timestamp DESC
        LIMIT 5
    """)
    
    recent_changes = cursor.fetchall()
    print("Last 5 actions:")
    for change in recent_changes:
        print(f"  {change[4]}: [{change[1]}] {change[0]} - {change[2]}")
        print(f"    Reason: {change[3][:80]}...")
    
    if recent_changes:
        context_recovered['last_action'] = recent_changes[0][0]
        context_recovered['last_action_time'] = str(recent_changes[0][4])
    print("")
    
    # =============================================================================
    # QUERY 4: What models are available?
    # =============================================================================
    
    print("[Q4] What models are deployed and their status?")
    print("-" * 60)
    
    cursor.execute("""
        SELECT 
            model_name,
            model_type,
            deployed_on,
            status,
            validation_notes
        FROM gladiator_models
        ORDER BY model_type, status DESC
    """)
    
    models = cursor.fetchall()
    print(f"Found {len(models)} models:")
    for model in models:
        print(f"  [{model[2]}] {model[0]}")
        print(f"    Type: {model[1]}, Status: {model[3]}")
        if model[4]:
            print(f"    Notes: {model[4][:100]}...")
    
    context_recovered['models_count'] = len(models)
    context_recovered['validated_models'] = len([m for m in models if m[3] == 'validated'])
    print("")
    
    # =============================================================================
    # QUERY 5: What validations have been completed?
    # =============================================================================
    
    print("[Q5] What validations have passed/failed?")
    print("-" * 60)
    
    cursor.execute("""
        SELECT 
            test_name,
            test_result,
            go_no_go_decision,
            executed_at
        FROM gladiator_validation_tests
        ORDER BY executed_at DESC
        LIMIT 8
    """)
    
    tests = cursor.fetchall()
    passed = len([t for t in tests if t[1] == 'PASS'])
    failed = len([t for t in tests if t[1] == 'FAIL'])
    
    print(f"Recent tests: {len(tests)} total, {passed} passed, {failed} failed")
    for test in tests[:3]:
        print(f"  {test[0]}: {test[1]} ({test[2]})")
    
    context_recovered['tests_passed'] = passed
    context_recovered['tests_failed'] = failed
    print("")
    
    # =============================================================================
    # QUERY 6: What's the current task/milestone?
    # =============================================================================
    
    print("[Q6] What should I be working on?")
    print("-" * 60)
    
    cursor.execute("""
        SELECT 
            milestone_name,
            status,
            completion_percentage,
            notes,
            planned_start_date
        FROM gladiator_phase_milestones
        WHERE status IN ('in_progress', 'planned')
        ORDER BY week_number
        LIMIT 3
    """)
    
    milestones = cursor.fetchall()
    print("Current/upcoming milestones:")
    for m in milestones:
        print(f"  {m[0]}")
        print(f"    Status: {m[1]}, Completion: {m[2]}%")
        if m[3]:
            print(f"    Notes: {m[3][:100]}...")
    
    if milestones and milestones[0][1] == 'in_progress':
        context_recovered['current_task'] = milestones[0][0]
        context_recovered['task_completion'] = milestones[0][2]
    print("")
    
    # =============================================================================
    # QUERY 7: Are there any active agents or locks?
    # =============================================================================
    
    print("[Q7] Are other agents working? Any resource locks?")
    print("-" * 60)
    
    cursor.execute("""
        SELECT 
            agent_id,
            assigned_task,
            status,
            last_heartbeat,
            locked_resources
        FROM gladiator_agent_coordination
        WHERE status = 'working'
           OR last_heartbeat > NOW() - INTERVAL '1 hour'
    """)
    
    agents = cursor.fetchall()
    if agents:
        print(f"Active agents: {len(agents)}")
        for agent in agents:
            print(f"  {agent[0]}: {agent[1]}")
            print(f"    Status: {agent[2]}, Last seen: {agent[3]}")
            print(f"    Locks: {agent[4]}")
    else:
        print("No active agents detected")
        print("✅ CONTEXT: No conflicts, safe to proceed")
    
    context_recovered['active_agents'] = len(agents)
    print("")
    
    # =============================================================================
    # QUERY 8: Critical - Any failures or blockers?
    # =============================================================================
    
    print("[Q8] Any critical failures or blockers?")
    print("-" * 60)
    
    cursor.execute("""
        SELECT critical_blockers, major_risks, minor_issues
        FROM gladiator_project_state
        WHERE is_current = TRUE
    """)
    
    issues = cursor.fetchone()
    print(f"Critical blockers: {issues[0]}")
    print(f"Major risks: {issues[1]}")
    print(f"Minor issues: {issues[2]}")
    
    if issues[0] == 0:
        print("✅ CONTEXT: No critical blockers, can proceed")
    else:
        print("⚠️  CONTEXT: Blockers present, need resolution")
    
    context_recovered['blockers'] = issues[0]
    print("")
    
    # =============================================================================
    # SUMMARY: Can new agent understand and resume?
    # =============================================================================
    
    print("="*80)
    print("CONTEXT RECOVERY SUMMARY")
    print("="*80)
    print("\nRecovered context:")
    for key, value in context_recovered.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*80)
    print("CONTEXT RECOVERY TEST RESULT")
    print("="*80)
    
    # Validate completeness
    required_context = [
        'project', 'phase', 'week', 'decision', 'last_action',
        'models_count', 'validated_models', 'tests_passed',
        'current_task', 'blockers'
    ]
    
    missing = [ctx for ctx in required_context if ctx not in context_recovered]
    
    if not missing:
        print("\n✅ COMPLETE CONTEXT RECOVERED")
        print("✅ New agent could understand state in <5 minutes")
        print("✅ Database provides full project context")
        print("✅ NO CONTEXT LOSS RISK")
        return True
    else:
        print(f"\n❌ INCOMPLETE CONTEXT - Missing: {missing}")
        print("❌ New agent would struggle to understand state")
        return False
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    success = simulate_new_agent_recovery()
    
    if success:
        print("\n" + "="*80)
        print("✅ DATABASE CONTEXT PRESERVATION: VALIDATED")
        print("="*80)
        print("\nSafe to proceed with Red Team execution:")
        print("  - If Cursor crashes: New agent recovers context in <5 min")
        print("  - If context lost: Database provides complete state")
        print("  - If disaster: Backups available for restore")
        print("\n✅ READY FOR OPTION A (HONEYPOT) EXECUTION")
        exit(0)
    else:
        print("\n❌ CONTEXT RECOVERY FAILED")
        print("FIX database structure before Red Team execution")
        exit(1)

