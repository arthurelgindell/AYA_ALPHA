#!/usr/bin/env python3
"""
ARM RED TEAM WITH CURRENT THREAT INTELLIGENCE
Process CISA KEV exploits with persona framework
Generate sophisticated, current attacks for Blue Team training
"""

import json
import requests
import time
from datetime import datetime

# Load current threat intelligence
CISA_KEV = '/Users/arthurdell/GLADIATOR/datasets/current_threats/cisa_kev_oct2025.json'
OUTPUT_DIR = '/Users/arthurdell/GLADIATOR/datasets/armed_red_team'

# LM Studio on BETA
BETA_API = "http://beta.local:1234/v1/chat/completions"
LLAMA_70B = "llama-3.3-70b-instruct"
TINYLLAMA = "tinyllama-1.1b-chat-v1.0-mlx"

# Persona definitions (from document pattern)
PERSONAS = {
    'script_kiddie': {
        'sophistication': 'low',
        'resources': 'minimal',
        'model': TINYLLAMA,
        'description': 'Uses public tools, basic techniques, no evasion'
    },
    'ransomware': {
        'sophistication': 'medium',
        'resources': 'moderate',
        'model': LLAMA_70B,
        'description': 'Opportunistic, tool-based, some evasion, economic motivation'
    },
    'apt_group': {
        'sophistication': 'high',
        'resources': 'significant',
        'model': LLAMA_70B,
        'description': 'Patient, sophisticated, advanced evasion, strategic objectives'
    },
    'nation_state': {
        'sophistication': 'extreme',
        'resources': 'unlimited',
        'model': LLAMA_70B,
        'description': 'Zero-day capable, maximum OPSEC, long-term persistence'
    }
}

print("="*80)
print("ARMING RED TEAM WITH CURRENT THREAT INTELLIGENCE")
print("="*80)
print(f"Started: {datetime.now()}")
print(f"Source: CISA KEV (October 2025 actively exploited vulnerabilities)")
print(f"Personas: {len(PERSONAS)}")
print(f"Output: {OUTPUT_DIR}")
print("="*80)
print()

# Load CISA data
with open(CISA_KEV) as f:
    cisa_data = json.load(f)

vulns = cisa_data.get('vulnerabilities', [])
print(f"Loaded: {len(vulns)} actively exploited vulnerabilities")
print()

# Process first 10 for demonstration (then scale to all 1,436)
DEMO_COUNT = 10  # Start with 10, then scale to 1,436

import os
os.makedirs(OUTPUT_DIR, exist_ok=True)

generated = 0
start_time = time.time()

for i, vuln in enumerate(vulns[:DEMO_COUNT]):
    cve_id = vuln.get('cveID', 'unknown')
    vuln_name = vuln.get('vulnerabilityName', 'unknown')
    description = vuln.get('shortDescription', 'No description')
    
    print(f"[{i+1}/{DEMO_COUNT}] Processing {cve_id}...")
    
    # Generate exploit for EACH persona
    for persona_name, persona in PERSONAS.items():
        prompt = f"""CURRENT THREAT INTELLIGENCE (October 2025):

CVE: {cve_id}
Vulnerability: {vuln_name}
Description: {description}
Status: ACTIVELY EXPLOITED IN THE WILD (CISA confirmed)

You are a {persona['description']}.

Generate a working exploit for this vulnerability at {persona['sophistication']} sophistication level:

1. Exploit approach (specific to this CVE)
2. Evasion techniques (appropriate for your sophistication)
3. Attack execution (step-by-step)
4. Expected detection challenges

Be realistic for October 2025 threat landscape.
Output functional exploit code/procedure.
"""
        
        try:
            response = requests.post(
                BETA_API,
                json={
                    "model": persona['model'],
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.8,
                    "max_tokens": 600
                },
                timeout=120
            )
            
            if response.status_code == 200:
                exploit = response.json()['choices'][0]['message']['content']
                
                # Save armed exploit
                output_file = f"{OUTPUT_DIR}/{cve_id}_{persona_name}.json"
                with open(output_file, 'w') as f:
                    json.dump({
                        'cve': cve_id,
                        'vulnerability': vuln_name,
                        'description': description,
                        'persona': persona_name,
                        'sophistication': persona['sophistication'],
                        'exploit': exploit,
                        'current': True,
                        'actively_exploited': True,
                        'generated_date': datetime.now().isoformat()
                    }, f, indent=2)
                
                generated += 1
                print(f"  ✅ {persona_name}: {len(exploit)} chars")
        
        except Exception as e:
            print(f"  ❌ {persona_name}: {e}")
    
    print()

elapsed = time.time() - start_time

print("="*80)
print("ARMING COMPLETE (DEMONSTRATION)")
print("="*80)
print(f"CVEs processed: {DEMO_COUNT}")
print(f"Exploits generated: {generated} ({generated/DEMO_COUNT:.1f} per CVE)")
print(f"Time: {elapsed:.1f}s ({elapsed/generated:.1f}s per exploit)")
print(f"Output: {OUTPUT_DIR}")
print()
print("NEXT: Scale to ALL 1,436 CVEs")
print(f"Estimated: {(elapsed/DEMO_COUNT)*1436/60:.0f} minutes for full dataset")
print("="*80)
