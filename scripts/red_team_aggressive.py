#!/usr/bin/env python3
"""
RED TEAM AGGRESSIVE MODE - PUSH BETA TO MAXIMUM
Simplified, no complex parallelism, just FAST generation
"""

import requests
import json
import time
from datetime import datetime
import os

API = "http://localhost:1234/v1/chat/completions"
LLAMA = "llama-3.3-70b-instruct"
TINY = "tinyllama-1.1b-chat-v1.0-mlx"

OUT = "/Volumes/DATA/GLADIATOR/attack_patterns/iteration_001"
os.makedirs(OUT, exist_ok=True)

TEMPLATES = [
    "SQL injection attack for login bypass",
    "XSS payload for cookie theft",
    "Port scan pattern",
    "Phishing email template",
    "Buffer overflow exploit"
]

print("RED TEAM AGGRESSIVE - STARTING")
print(f"Output: {OUT}")
print(f"Started: {datetime.now()}")

count = 0
start = time.time()

# SIMPLE LOOP - JUST GENERATE FAST
for i in range(10000):
    template = TEMPLATES[i % len(TEMPLATES)]
    model = LLAMA if i % 5 == 0 else TINY  # 20% Llama, 80% TinyLlama (faster)
    
    try:
        resp = requests.post(API, json={
            "model": model,
            "messages": [{"role": "user", "content": f"Generate {template}"}],
            "temperature": 0.8,
            "max_tokens": 200  # Shorter = faster
        }, timeout=60)
        
        if resp.status_code == 200:
            code = resp.json()['choices'][0]['message']['content']
            
            with open(f"{OUT}/attack_{i:06d}.json", 'w') as f:
                json.dump({
                    'id': i,
                    'type': template,
                    'code': code,
                    'model': model,
                    'time': datetime.now().isoformat()
                }, f)
            
            count += 1
            
            if count % 50 == 0:
                elapsed = time.time() - start
                rate = count / elapsed
                eta = (10000 - count) / rate if rate > 0 else 0
                print(f"[{count:05d}/10000] {rate:.2f}/sec ETA: {eta/3600:.1f}hrs")
    
    except Exception as e:
        if count % 100 == 0:
            print(f"Error at {count}: {e}")
        time.sleep(0.1)

total = time.time() - start
print(f"\nCOMPLETE: {count} attacks in {total/3600:.2f} hours")
print(f"Rate: {count/total:.2f}/second")

