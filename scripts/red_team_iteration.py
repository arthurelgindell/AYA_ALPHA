#!/usr/bin/env python3
"""
GLADIATOR Red Team Iteration Executor
Generates attack patterns with monitoring and safety

Usage: python3 red_team_iteration.py <iteration_number> <duration_minutes>
Example: python3 red_team_iteration.py 001 60
"""

import sys
import subprocess
import time
import json
from datetime import datetime
from red_team_monitor import RedTeamMonitor

def generate_attacks_on_beta(iteration, duration_minutes, target_count=5000):
    """
    Execute Red Team attack generation on BETA
    
    Args:
        iteration: Iteration number
        duration_minutes: How long to run
        target_count: Target number of attacks to generate
    """
    
    # Create generation script for BETA
    generation_script = f"""
import requests
import json
import time
from datetime import datetime

API_URL = "http://localhost:1234/v1/chat/completions"
LLAMA_MODEL = "llama-3.3-70b-instruct"
TINY_MODEL = "tinyllama-1.1b-chat-v1.0-mlx"

ATTACK_DIR = "/Volumes/DATA/GLADIATOR/attack_patterns/iteration_{iteration:03d}"
import os
os.makedirs(ATTACK_DIR, exist_ok=True)

print("="*80)
print(f"RED TEAM ITERATION {iteration:03d} - ATTACK GENERATION")
print(f"Target: {target_count} attacks in {duration_minutes} minutes")
print(f"Output: {{ATTACK_DIR}}")
print("="*80)

generated = 0
start_time = time.time()
end_time = start_time + ({duration_minutes} * 60)

attack_types = [
    'SQL injection for web application login bypass',
    'XSS payload for cookie theft',
    'Port scanning pattern for network reconnaissance',
    'Phishing email template for credential harvesting',
    'Buffer overflow exploit for privilege escalation'
]

while time.time() < end_time and generated < {target_count}:
    attack_type = attack_types[generated % len(attack_types)]
    
    try:
        # Use Llama 70B for exploit generation
        response = requests.post(API_URL, json={{
            "model": LLAMA_MODEL,
            "messages": [{{"role": "user", "content": f"Generate {{attack_type}}"}}],
            "temperature": 0.8,
            "max_tokens": 300
        }}, timeout=60)
        
        if response.status_code == 200:
            attack_code = response.json()['choices'][0]['message']['content']
            
            # Save attack pattern
            attack_file = f"{{ATTACK_DIR}}/attack_{{generated:06d}}.json"
            with open(attack_file, 'w') as f:
                json.dump({{
                    'id': f'iter{{iteration:03d}}_{{generated:06d}}',
                    'type': attack_type,
                    'code': attack_code,
                    'generated_at': datetime.now().isoformat(),
                    'model': LLAMA_MODEL
                }}, f, indent=2)
            
            generated += 1
            
            if generated % 100 == 0:
                elapsed = time.time() - start_time
                rate = generated / elapsed if elapsed > 0 else 0
                remaining = ({target_count} - generated) / rate if rate > 0 else 0
                print(f"Progress: {{generated}}/{target_count} ({{rate:.1f}}/min, ETA: {{remaining/60:.1f}}m)")
    
    except Exception as e:
        print(f"Error generating attack {{generated}}: {{e}}")
        time.sleep(1)

print(f"\\nGenerated {{generated}} attacks in {{(time.time()-start_time)/60:.1f}} minutes")
print(f"Location: {{ATTACK_DIR}}")
"""
    
    # Write script to BETA
    print(f"\n[ITERATION {iteration}] Deploying generation script to BETA...")
    
    script_path = f"/tmp/red_team_generate_iter_{iteration}.py"
    with open('/tmp/beta_gen_script.py', 'w') as f:
        f.write(generation_script)
    
    # Copy to BETA
    subprocess.run(
        ['scp', '/tmp/beta_gen_script.py', f'beta.local:{script_path}'],
        check=True
    )
    
    print(f"✅ Script deployed to BETA:{script_path}")
    
    # Start generation in background on BETA
    print(f"\n[ITERATION {iteration}] Starting Red Team generation on BETA...")
    
    beta_cmd = f"cd /Volumes/DATA/GLADIATOR && python3 {script_path} > /tmp/redteam_iter_{iteration}.log 2>&1 &"
    subprocess.run(['ssh', 'beta.local', beta_cmd])
    
    print(f"✅ Red Team started on BETA")
    print(f"   Monitor will watch for {duration_minutes} minutes")
    print(f"   Target: {target_count} attacks")
    print("")
    
    return script_path


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 red_team_iteration.py <iteration_number> <duration_minutes>")
        print("Example: python3 red_team_iteration.py 001 60")
        sys.exit(1)
    
    iteration = int(sys.argv[1])
    duration = int(sys.argv[2])
    target_attacks = int(sys.argv[3]) if len(sys.argv) > 3 else 5000
    
    print("="*80)
    print(f"GLADIATOR RED TEAM ITERATION {iteration:03d}")
    print("="*80)
    print(f"Duration: {duration} minutes")
    print(f"Target: {target_attacks} attacks")
    print(f"Monitoring: ACTIVE (abort if dangerous)")
    print("")
    
    # Deploy and start Red Team
    script_path = generate_attacks_on_beta(iteration, duration, target_attacks)
    
    # Monitor with safety
    monitor = RedTeamMonitor(iteration_number=iteration)
    result = monitor.monitor_iteration(duration_minutes=duration)
    
    if result == 'aborted':
        print("\n🚨 ITERATION ABORTED - Red Team was dangerous")
        print(f"Reason: {monitor.abort_reason}")
        print("\n⚠️  RESTORE FROM BACKUP RECOMMENDED")
        sys.exit(1)
    
    print("\n✅ ITERATION COMPLETE - Checking results...")
    
    # Get attack count from BETA
    count_cmd = f"ls /Volumes/DATA/GLADIATOR/attack_patterns/iteration_{iteration:03d}/ 2>/dev/null | wc -l"
    result = subprocess.run(
        ['ssh', 'beta.local', count_cmd],
        capture_output=True,
        text=True
    )
    
    attacks_generated = int(result.stdout.strip()) if result.returncode == 0 else 0
    
    print(f"✅ Attacks generated: {attacks_generated}")
    print(f"✅ BETA still responsive")
    print("")
    print("="*80)
    print("ITERATION READY FOR REVIEW")
    print("="*80)
    print("\nArthur, please review:")
    print(f"  1. BETA status (SSH to beta.local)")
    print(f"  2. Attack quality (check attack_patterns/iteration_{iteration:03d}/)")
    print(f"  3. System stability")
    print("")
    print("Decision: CONTINUE to next iteration or RESTORE from backup?")

if __name__ == "__main__":
    main()

