#!/usr/bin/env python3
"""
GLADIATOR Variant Generator - Option 3 Hybrid Approach
Uses TinyLlama to generate 7,000 variants per exploit
Target: 1,436 exploits × 7,000 variants = 10,052,000 sophisticated attacks
"""

import json
import os
import sys
import requests
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
EXPLOIT_DB_DIR = "/Users/arthurdell/GLADIATOR/datasets/exploit_database/"
OUTPUT_DIR = "/Volumes/DATA/GLADIATOR/variant_database/"
LOG_FILE = "/Volumes/DATA/GLADIATOR/logs/variant_generation.log"
LM_STUDIO_URL = "http://localhost:1234/v1/completions"
VARIANTS_PER_EXPLOIT = 7000
MAX_WORKERS = 15  # TinyLlama instances
BATCH_SIZE = 1000  # Variants per batch file

def log(message):
    """Log to file and stdout"""
    timestamp = datetime.now().isoformat()
    log_msg = f"[{timestamp}] {message}"
    print(log_msg, flush=True)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(log_msg + '\n')

def generate_variant(exploit_data, variant_num):
    """Generate one variant using TinyLlama"""
    cve = exploit_data.get('cve')
    vuln_name = exploit_data.get('vulnerability_name', '')
    
    prompt = f"""Generate a sophisticated attack variant for {cve} ({vuln_name}).
Create evasion technique #{variant_num}.
Make it polymorphic, obfuscated, and behaviorally different.
Output ONLY the attack code, no explanations.

Variant #{variant_num}:"""

    try:
        response = requests.post(
            LM_STUDIO_URL,
            json={
                "prompt": prompt,
                "max_tokens": 500,
                "temperature": 0.9,  # High creativity
                "top_p": 0.95,
                "stop": ["\n\n\n"]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            code = result.get('choices', [{}])[0].get('text', '').strip()
            
            return {
                'variant_id': f"{cve}_variant_{variant_num:06d}",
                'base_cve': cve,
                'variant_number': variant_num,
                'attack_code': code,
                'generated_at': datetime.now().isoformat(),
                'sophistication': 'high',
                'evasive': True
            }
    except Exception as e:
        log(f"    Error variant {variant_num}: {e}")
        return None

def generate_variants_for_exploit(exploit_file):
    """Generate all variants for one exploit"""
    cve = exploit_file.stem
    
    # Check if already completed
    output_dir = Path(OUTPUT_DIR) / cve
    if output_dir.exists():
        existing = len(list(output_dir.glob("batch_*.json")))
        expected_batches = (VARIANTS_PER_EXPLOIT + BATCH_SIZE - 1) // BATCH_SIZE
        if existing >= expected_batches:
            log(f"  {cve}: Already complete ({existing} batches), skipping")
            return VARIANTS_PER_EXPLOIT
    
    # Load exploit
    with open(exploit_file) as f:
        exploit_data = json.load(f)
    
    if not exploit_data.get('ready_for_variants'):
        log(f"  {cve}: No base exploit found, skipping")
        return 0
    
    log(f"  {cve}: Generating {VARIANTS_PER_EXPLOIT} variants...")
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate variants in parallel
    generated = 0
    batch_num = 0
    current_batch = []
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(generate_variant, exploit_data, i): i 
            for i in range(1, VARIANTS_PER_EXPLOIT + 1)
        }
        
        for future in as_completed(futures):
            variant = future.result()
            if variant:
                current_batch.append(variant)
                generated += 1
                
                # Save batch when full
                if len(current_batch) >= BATCH_SIZE:
                    batch_file = output_dir / f"batch_{batch_num:04d}.json"
                    with open(batch_file, 'w') as f:
                        json.dump(current_batch, f, indent=2)
                    log(f"    {cve}: Saved batch {batch_num} ({len(current_batch)} variants)")
                    current_batch = []
                    batch_num += 1
                
                # Progress update
                if generated % 100 == 0:
                    pct = generated * 100 // VARIANTS_PER_EXPLOIT
                    log(f"    {cve}: {generated}/{VARIANTS_PER_EXPLOIT} ({pct}%)")
    
    # Save final batch
    if current_batch:
        batch_file = output_dir / f"batch_{batch_num:04d}.json"
        with open(batch_file, 'w') as f:
            json.dump(current_batch, f, indent=2)
        log(f"    {cve}: Saved final batch {batch_num} ({len(current_batch)} variants)")
    
    log(f"  {cve}: ✓ Complete - {generated} variants generated")
    return generated

def main():
    """Main execution"""
    log("="*80)
    log("GLADIATOR VARIANT GENERATOR - OPTION 3 HYBRID")
    log(f"TinyLlama Instances: {MAX_WORKERS}")
    log(f"Variants per exploit: {VARIANTS_PER_EXPLOIT}")
    log("="*80)
    
    # Find exploit files
    exploit_files = list(Path(EXPLOIT_DB_DIR).glob("CVE-*.json"))
    total_exploits = len(exploit_files)
    
    log(f"\nFound {total_exploits} exploits")
    log(f"Target: {total_exploits} × {VARIANTS_PER_EXPLOIT} = {total_exploits * VARIANTS_PER_EXPLOIT:,} variants")
    log(f"Output: {OUTPUT_DIR}\n")
    
    if total_exploits == 0:
        log("ERROR: No exploits found. Run download_exploits.py first.")
        return 0
    
    log("Starting variant generation...\n")
    
    # Generate variants
    total_variants = 0
    for i, exploit_file in enumerate(exploit_files, 1):
        cve = exploit_file.stem
        log(f"[{i}/{total_exploits}] {cve}")
        
        variants = generate_variants_for_exploit(exploit_file)
        total_variants += variants
        
        # Progress summary
        if i % 10 == 0:
            avg_per_exploit = total_variants / i
            estimated_total = int(avg_per_exploit * total_exploits)
            pct = i * 100 // total_exploits
            log(f"  Progress: {i}/{total_exploits} exploits ({pct}%)")
            log(f"  Generated: {total_variants:,} variants")
            log(f"  Estimated total: {estimated_total:,}\n")
    
    log("\n" + "="*80)
    log(f"VARIANT GENERATION COMPLETE")
    log(f"Exploits processed: {total_exploits}")
    log(f"Total variants: {total_variants:,}")
    log(f"Target achieved: {total_variants*100//10000000}%")
    log("="*80)
    
    return total_variants

if __name__ == "__main__":
    try:
        count = main()
        sys.exit(0 if count > 0 else 1)
    except KeyboardInterrupt:
        log("\n\nGeneration interrupted by user")
        sys.exit(130)
    except Exception as e:
        log(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

