#!/usr/bin/env python3
"""Generate 10M training samples NOW - No theory, just execution"""

import json
import os
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime

OUT = "/Users/arthurdell/GLADIATOR/datasets/training_10m"
os.makedirs(OUT, exist_ok=True)

# Generate 10M attack variants FAST (CPU-bound)
print("GENERATING 10 MILLION TRAINING SAMPLES")
print("Started:", datetime.now())

start = time.time()
generated = 0

# Simple but effective: SQL injection variants
base_sqli = [
    "' OR 1=1--", "' OR '1'='1", "admin'--", "' OR 'a'='a",
    "1' UNION SELECT", "'; DROP TABLE", "' AND 1=1--"
]

# 10M samples = write files
print("Generating samples...")
for batch in range(1000):  # 1000 batches of 10K each
    batch_data = []
    
    for i in range(10000):
        attack_id = batch * 10000 + i
        pattern = base_sqli[attack_id % len(base_sqli)]
        
        batch_data.append({
            'id': attack_id,
            'type': 'sql_injection',
            'payload': pattern + str(attack_id % 100),
            'variant': attack_id
        })
        generated += 1
    
    # Save batch
    with open(f"{OUT}/batch_{batch:04d}.json", 'w') as f:
        json.dump(batch_data, f)
    
    if batch % 100 == 0 and batch > 0:
        elapsed = time.time() - start
        rate = generated / elapsed
        print(f"[{generated:,}] {rate:,.0f}/sec")

elapsed = time.time() - start
print(f"\nCOMPLETE: {generated:,} samples in {elapsed:.1f}s")
print(f"Rate: {generated/elapsed:,.0f}/second")
print(f"Output: {OUT}")
