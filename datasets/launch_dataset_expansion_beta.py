#!/usr/bin/env python3
"""
GLADIATOR Dataset Expansion - Track 3
Launch on BETA system for parallel execution during Week 1
Target: 10,000 samples (5,000 attacks + 5,000 benign)
"""

import json
import random
from pathlib import Path
from datetime import datetime

def generate_expansion_plan():
    """
    Create dataset expansion plan focusing on weak categories
    and improving diversity
    """
    
    print("="*70)
    print("GLADIATOR Dataset Expansion - Track 3")
    print("="*70)
    print(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Priority categories based on Track 2 results
    priority_categories = {
        'privilege_escalation': {
            'current_accuracy': 62.5,
            'current_samples': 8,
            'target_samples': 800,
            'priority': 'CRITICAL',
            'focus_areas': [
                'SUID binary exploitation',
                'Kernel privilege escalation',
                'Container escape techniques',
                'Windows UAC bypass',
                'Linux capability abuse',
                'Sudo misconfigurations',
                'setuid vulnerabilities',
                'Process injection for privilege gain'
            ]
        },
        'buffer_overflow': {
            'current_accuracy': 100.0,
            'current_samples': 5,
            'target_samples': 600,
            'priority': 'HIGH',
            'focus_areas': [
                'Stack-based buffer overflow',
                'Heap-based buffer overflow',
                'Integer overflow',
                'Format string vulnerabilities',
                'Return-oriented programming (ROP)',
                'Use-after-free exploits'
            ]
        },
        'path_traversal': {
            'current_accuracy': 0.0,  # Not tested in v1
            'current_samples': 0,
            'target_samples': 500,
            'priority': 'HIGH',
            'focus_areas': [
                'Directory traversal attacks',
                'File inclusion (LFI/RFI)',
                'Path normalization bypass',
                'Null byte injection',
                'ZIP file path traversal'
            ]
        },
        'malware': {
            'current_accuracy': 0.0,  # Not tested in v1
            'current_samples': 0,
            'target_samples': 700,
            'priority': 'HIGH',
            'focus_areas': [
                'Ransomware patterns',
                'Trojan implementations',
                'Backdoor techniques',
                'Rootkit methods',
                'Worm propagation',
                'Cryptominers',
                'Fileless malware'
            ]
        },
        'sql_injection': {
            'current_accuracy': 100.0,
            'current_samples': 16,
            'target_samples': 600,
            'priority': 'MEDIUM',
            'focus_areas': [
                'Time-based blind SQLi',
                'Boolean-based blind SQLi',
                'Error-based SQLi',
                'UNION-based SQLi',
                'Stacked queries',
                'Out-of-band SQLi',
                'Second-order SQLi'
            ]
        },
        'xss': {
            'current_accuracy': 100.0,
            'current_samples': 13,
            'target_samples': 600,
            'priority': 'MEDIUM',
            'focus_areas': [
                'Stored XSS',
                'Reflected XSS',
                'DOM-based XSS',
                'Mutation XSS (mXSS)',
                'CSS injection',
                'XSS via SVG',
                'Template injection'
            ]
        },
        'command_injection': {
            'current_accuracy': 100.0,
            'current_samples': 4,
            'target_samples': 500,
            'priority': 'MEDIUM',
            'focus_areas': [
                'OS command injection',
                'Shell metacharacter abuse',
                'Command chaining',
                'Argument injection',
                'Environment variable injection'
            ]
        },
        'phishing': {
            'current_accuracy': 100.0,
            'current_samples': 11,
            'target_samples': 500,
            'priority': 'MEDIUM',
            'focus_areas': [
                'Spear phishing',
                'Whaling attacks',
                'Clone phishing',
                'Voice phishing (vishing)',
                'SMS phishing (smishing)',
                'QR code phishing'
            ]
        },
        'dos': {
            'current_accuracy': 100.0,
            'current_samples': 3,
            'target_samples': 400,
            'priority': 'MEDIUM',
            'focus_areas': [
                'Application-layer DoS',
                'DDoS amplification',
                'Slowloris',
                'HTTP flood',
                'SYN flood',
                'DNS amplification'
            ]
        },
        'mitm': {
            'current_accuracy': 100.0,
            'current_samples': 3,
            'target_samples': 300,
            'priority': 'LOW',
            'focus_areas': [
                'ARP spoofing',
                'DNS spoofing',
                'SSL stripping',
                'Session hijacking',
                'BGP hijacking'
            ]
        }
    }
    
    # Calculate totals
    total_target = sum(cat['target_samples'] for cat in priority_categories.values())
    
    print(f"\nExpansion Plan Summary:")
    print(f"  Current Total: ~60 attack samples (from Track 2)")
    print(f"  Target Total: {total_target:,} attack samples")
    print(f"  Additional Needed: {total_target - 60:,} samples")
    print(f"  Plus Benign: {total_target:,} samples (1:1 ratio)")
    print(f"  Grand Total: {total_target * 2:,} samples")
    
    print(f"\nPriority Breakdown:")
    for category, details in sorted(priority_categories.items(), 
                                    key=lambda x: (0 if x[1]['priority'] == 'CRITICAL' else 
                                                  1 if x[1]['priority'] == 'HIGH' else 
                                                  2 if x[1]['priority'] == 'MEDIUM' else 3)):
        print(f"\n  {category.upper()} [{details['priority']}]")
        print(f"    Current: {details['current_samples']} samples ({details['current_accuracy']:.1f}% accuracy)")
        print(f"    Target: {details['target_samples']} samples")
        print(f"    Need: {details['target_samples'] - details['current_samples']} samples")
        print(f"    Focus areas: {len(details['focus_areas'])} specific techniques")
    
    # Save expansion plan
    output_dir = Path("/Users/arthurdell/GLADIATOR/datasets")
    plan_file = output_dir / "expansion_plan_track3.json"
    
    plan_data = {
        'plan_version': '2.0',
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'target_total_samples': total_target * 2,
        'target_attack_samples': total_target,
        'target_benign_samples': total_target,
        'categories': priority_categories,
        'execution': {
            'system': 'BETA',
            'location': '/Volumes/DATA/GLADIATOR',
            'container': 'red_combat',
            'tools': ['LM Studio', 'CVE database', 'Manual generation'],
            'timeline': '2-3 weeks',
            'quality_gate': 'Manual review + automated validation'
        }
    }
    
    with open(plan_file, 'w') as f:
        json.dump(plan_data, f, indent=2)
    
    print(f"\n💾 Expansion plan saved to: {plan_file}")
    
    # Generate execution instructions
    instructions_file = output_dir / "EXPANSION_INSTRUCTIONS.md"
    with open(instructions_file, 'w') as f:
        f.write("# GLADIATOR Dataset Expansion - Track 3 Execution Instructions\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Target**: {total_target * 2:,} total samples\n")
        f.write(f"**Timeline**: 2-3 weeks (parallel with Week 1)\n\n")
        f.write("---\n\n")
        f.write("## EXECUTION ON BETA SYSTEM\n\n")
        f.write("### Prerequisites\n")
        f.write("- BETA system accessible\n")
        f.write("- red_combat container running\n")
        f.write("- LM Studio operational (http://localhost:1234)\n")
        f.write("- CVE database accessible\n\n")
        f.write("### Phase 1: Privilege Escalation (Week 1, Days 1-2)\n")
        f.write("**Priority**: CRITICAL (only 62.5% accuracy in Track 2)\n\n")
        f.write("Generate 800 privilege escalation samples:\n")
        for i, focus_area in enumerate(priority_categories['privilege_escalation']['focus_areas'], 1):
            f.write(f"{i}. {focus_area} (100 samples)\n")
        f.write("\n### Phase 2: High-Priority Categories (Week 1, Days 3-5)\n")
        f.write("- Buffer Overflow: 600 samples\n")
        f.write("- Path Traversal: 500 samples\n")
        f.write("- Malware: 700 samples\n\n")
        f.write("### Phase 3: Medium-Priority Categories (Week 2)\n")
        f.write("- SQL Injection: 600 samples\n")
        f.write("- XSS: 600 samples\n")
        f.write("- Command Injection: 500 samples\n")
        f.write("- Phishing: 500 samples\n")
        f.write("- DoS: 400 samples\n\n")
        f.write("### Phase 4: Low-Priority & Benign (Week 3)\n")
        f.write("- MITM: 300 samples\n")
        f.write("- Benign samples: 5,500 samples (match attack total)\n\n")
        f.write("### Quality Control\n")
        f.write("- Manual review: 10% of samples per category\n")
        f.write("- Automated validation: 100% of samples\n")
        f.write("- Deduplication: Run across all samples\n")
        f.write("- Labeling review: Reduce unknown to <10%\n\n")
        f.write("### Execution Commands\n")
        f.write("```bash\n")
        f.write("# On BETA system\n")
        f.write("ssh beta.local\n")
        f.write("cd /Volumes/DATA/GLADIATOR\n\n")
        f.write("# Generate samples (to be implemented)\n")
        f.write("# docker exec red_combat python3 /gladiator/scripts/generate_expansion_dataset.py\n")
        f.write("```\n\n")
        f.write("---\n\n")
        f.write("**Status**: READY TO LAUNCH (Week 1, Day 1)\n")
    
    print(f"📋 Execution instructions saved to: {instructions_file}")
    
    print("\n" + "="*70)
    print("✅ Dataset Expansion Plan (Track 3) Ready")
    print("="*70)
    print("\nStatus: READY TO LAUNCH during Week 1")
    print("Next Action: Execute expansion on BETA in parallel with Week 1 tasks")
    print("="*70)


if __name__ == "__main__":
    generate_expansion_plan()

