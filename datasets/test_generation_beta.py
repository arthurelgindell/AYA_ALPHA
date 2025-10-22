#!/usr/bin/env python3
"""
Test BETA generation with 10 samples
Verify LM Studio connectivity and sample quality before full batch
"""

import json
import requests
from datetime import datetime

LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"

def test_generation():
    """Test generation of 10 privilege escalation samples"""
    
    print("="*70)
    print("BETA Generation Test - 10 Samples")
    print("="*70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"LM Studio: {LM_STUDIO_URL}")
    print()
    
    test_prompts = [
        "Generate SUID binary exploitation using find for privilege escalation",
        "Create Docker container escape technique using namespace confusion",
        "Develop Windows 11 UAC bypass using fodhelper",
        "Generate Linux capability abuse for privilege escalation using CAP_SYS_ADMIN",
        "Create sudo misconfiguration exploit for privilege escalation",
        "Generate kernel exploit for CVE-2024-1086 privilege escalation",
        "Create setuid vulnerability exploit in screen application",
        "Generate process injection attack for privilege escalation to systemd",
        "Develop privilege escalation using sudo wildcard in /usr/bin/find",
        "Create container breakout exploit using seccomp bypass"
    ]
    
    successful = 0
    failed = 0
    samples = []
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"Sample {i}/10: {prompt[:60]}...")
        
        try:
            response = requests.post(
                LM_STUDIO_URL,
                json={
                    "model": "qwen3-14b-mlx",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.8,
                    "max_tokens": 500,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                attack_code = data['choices'][0]['message']['content']
                
                sample = {
                    "id": f"test_{i:02d}",
                    "template": prompt,
                    "attack_code": attack_code,
                    "model": "qwen3-14b-mlx",
                    "generated_at": datetime.now().isoformat()
                }
                
                samples.append(sample)
                successful += 1
                print(f"  ✅ Generated ({len(attack_code)} chars)")
            else:
                failed += 1
                print(f"  ❌ Failed (HTTP {response.status_code})")
                
        except Exception as e:
            failed += 1
            print(f"  ❌ Error: {e}")
    
    print()
    print("="*70)
    print("TEST RESULTS")
    print("="*70)
    print(f"Successful: {successful}/10")
    print(f"Failed: {failed}/10")
    print(f"Success Rate: {successful/10*100:.1f}%")
    
    if successful >= 9:
        print("\n✅ TEST PASSED - Ready for full batch generation")
        decision = "GO"
    elif successful >= 7:
        print("\n⚠️  TEST MARGINAL - Review errors before full batch")
        decision = "REVIEW"
    else:
        print("\n❌ TEST FAILED - Fix issues before full batch")
        decision = "NO-GO"
    
    # Save test samples
    if samples:
        output_file = "/Volumes/DATA/GLADIATOR/datasets/test_generation_samples.jsonl"
        with open(output_file, 'w') as f:
            for sample in samples:
                f.write(json.dumps(sample) + '\n')
        print(f"\n💾 Test samples saved: {output_file}")
        
        # Show first sample
        print("\nSample Output (first):")
        print("-"*70)
        print(f"Prompt: {samples[0]['template']}")
        print(f"Response length: {len(samples[0]['attack_code'])} chars")
        print(f"Response preview: {samples[0]['attack_code'][:200]}...")
        print("-"*70)
    
    print(f"\nDecision: {decision}")
    print("="*70)
    
    return decision, successful, failed


if __name__ == "__main__":
    test_generation()

