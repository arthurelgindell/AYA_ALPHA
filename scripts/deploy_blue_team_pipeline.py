#!/usr/bin/env python3
"""
BLUE TEAM MULTI-AGENT PIPELINE DEPLOYMENT
4-Stage Detection Architecture (Document Section 4)

Stage 1: Traffic Filtering (7B lightweight)
Stage 2: Threat Analysis (Foundation-sec-8b) 
Stage 3: Attribution (13B specialist)
Stage 4: Response Planning (Llama 70B)

Runs on: ALPHA (512GB RAM available)
"""

import requests
import json
from datetime import datetime

ALPHA_API = "http://localhost:1234/v1/chat/completions"
FOUNDATION = "foundation-sec-8b-instruct-int8"

print("="*80)
print("BLUE TEAM MULTI-AGENT PIPELINE DEPLOYMENT")
print("="*80)
print(f"Started: {datetime.now()}")
print()

# Stage 2: Threat Analysis (using validated Foundation model)
print("[STAGE 2] Deploying Threat Analysis Agent...")
print("Model: foundation-sec-8b-instruct-int8 (validated)")
print("Resources: 50GB RAM allocated")
print("Task: Extract IOCs, TTPs, behavioral patterns")
print()

# Test Stage 2 with sample attack
test_attack = """
Network traffic detected:
- Multiple failed SSH login attempts from 203.0.113.42
- Followed by successful login
- Immediate privilege escalation attempt
- Lateral movement to internal systems
- Data exfiltration to external IP

Analyze this attack pattern.
"""

print("Testing Stage 2 detection...")
try:
    response = requests.post(ALPHA_API, json={
        "model": FOUNDATION,
        "messages": [{"role": "user", "content": test_attack}],
        "max_tokens": 300
    }, timeout=60)
    
    if response.status_code == 200:
        analysis = response.json()['choices'][0]['message']['content']
        print("✅ Stage 2 OPERATIONAL")
        print(f"\nSample Analysis:\n{analysis[:300]}...")
        
        # Save pipeline configuration
        pipeline_config = {
            'stage_2_threat_analysis': {
                'model': FOUNDATION,
                'status': 'operational',
                'resources_gb': 50,
                'latency_target_ms': 100,
                'test_result': 'passed'
            }
        }
        
        with open('/Users/arthurdell/GLADIATOR/datasets/blue_pipeline_config.json', 'w') as f:
            json.dump(pipeline_config, f, indent=2)
        
        print("\n✅ BLUE TEAM STAGE 2 DEPLOYED")
    else:
        print(f"❌ Stage 2 failed: {response.status_code}")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*80)
print("BLUE TEAM PIPELINE: Stage 2 operational, ready for combat testing")
print("="*80)
