#!/usr/bin/env python3
"""
GLADIATOR Dataset Expansion - Privilege Escalation Batch
Generate 800 privilege escalation attack samples
Priority: CRITICAL (only 62.5% accuracy in Week 0 Track 2)
"""

import json
import requests
import random
import time
from datetime import datetime
from pathlib import Path

# LM Studio API endpoint (on BETA)
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"

# Privilege escalation techniques (8 focus areas × 100 samples each)
PRIVILEGE_ESCALATION_TEMPLATES = {
    'suid_binary_exploitation': [
        "Generate SUID binary exploitation using {binary} for privilege escalation",
        "Create privilege escalation attack exploiting SUID bit on {binary}",
        "Develop {binary} SUID exploitation technique for root access",
        "Exploit SUID {binary} vulnerability for privilege gain",
        "Generate attack code using misconfigured SUID {binary} for escalation"
    ],
    'kernel_privilege_escalation': [
        "Generate kernel exploit for {cve} privilege escalation vulnerability",
        "Create {os} kernel privilege escalation using {technique}",
        "Develop exploit for kernel vulnerability {cve} targeting {os}",
        "Generate privilege escalation using kernel {component} vulnerability",
        "Create {os} kernel exploit for local privilege escalation"
    ],
    'container_escape': [
        "Generate Docker container escape technique using {method}",
        "Create Kubernetes pod escape for privilege escalation to host",
        "Develop container breakout exploit using {vulnerability}",
        "Generate {runtime} container escape for host access",
        "Create privilege escalation via container misconfiguration {type}"
    ],
    'uac_bypass': [
        "Generate Windows UAC bypass using {technique}",
        "Create UAC elevation exploit using {method} for admin access",
        "Develop Windows {version} UAC bypass technique",
        "Generate privilege escalation bypassing Windows UAC with {tool}",
        "Create UAC bypass using COM elevation moniker {method}"
    ],
    'linux_capability_abuse': [
        "Generate Linux capability abuse for privilege escalation using {capability}",
        "Create exploit using CAP_{cap} capability for root access",
        "Develop privilege escalation abusing {capability} on {process}",
        "Generate attack exploiting Linux capabilities misconfiguration",
        "Create {capability} capability abuse for container escape"
    ],
    'sudo_misconfiguration': [
        "Generate sudo misconfiguration exploit for privilege escalation",
        "Create privilege escalation using sudo NOPASSWD misconfiguration",
        "Develop attack exploiting sudo wildcard in {command}",
        "Generate sudo -l abuse for privilege escalation to root",
        "Create privilege escalation using sudo environment variable {var}"
    ],
    'setuid_vulnerabilities': [
        "Generate setuid vulnerability exploit in {application}",
        "Create privilege escalation using setuid race condition",
        "Develop attack exploiting setuid binary {binary} vulnerability",
        "Generate setuid file handling exploit for privilege gain",
        "Create privilege escalation via setuid wrapper abuse in {program}"
    ],
    'process_injection': [
        "Generate process injection attack for privilege escalation to {process}",
        "Create DLL injection technique for Windows privilege escalation",
        "Develop ptrace injection for Linux privilege escalation",
        "Generate process hollowing attack for privilege gain",
        "Create shared object injection for privilege escalation on {os}"
    ]
}

# Variable pools for template substitution
SUBSTITUTIONS = {
    'binary': ['find', 'nmap', 'vim', 'screen', 'tmux', 'docker', 'mount', 'pkexec', 'passwd', 'chsh'],
    'cve': ['CVE-2024-1086', 'CVE-2023-32233', 'CVE-2022-0847', 'CVE-2021-4034', 'CVE-2023-2640'],
    'os': ['Linux', 'Ubuntu 22.04', 'RHEL 9', 'Debian 12', 'CentOS 8', 'Fedora 38'],
    'technique': ['use-after-free', 'race condition', 'stack overflow', 'heap spray', 'return-to-user'],
    'component': ['netfilter', 'nf_tables', 'eBPF', 'io_uring', 'perf_event'],
    'method': ['namespace confusion', 'cgroup escape', 'mount manipulation', 'procfs abuse', 'device access'],
    'vulnerability': ['runc vulnerability', 'overlay filesystem bug', 'seccomp bypass', 'AppArmor bypass'],
    'runtime': ['Docker', 'containerd', 'CRI-O', 'Podman'],
    'type': ['volume mount', 'privileged flag', 'host network', 'pid namespace'],
    'tool': ['fodhelper', 'eventvwr', 'sdclt', 'computerdefaults', 'slui'],
    'version': ['Windows 10', 'Windows 11', 'Windows Server 2022'],
    'capability': ['CAP_SYS_ADMIN', 'CAP_DAC_OVERRIDE', 'CAP_SETUID', 'CAP_NET_RAW', 'CAP_SYS_PTRACE'],
    'cap': ['SYS_ADMIN', 'DAC_OVERRIDE', 'SETUID', 'NET_RAW', 'SYS_PTRACE'],
    'process': ['systemd', 'dbus-daemon', 'polkitd', 'sshd', 'cron'],
    'command': ['/usr/bin/find', '/bin/cp', '/usr/bin/vim', '/usr/bin/less'],
    'var': ['LD_PRELOAD', 'LD_LIBRARY_PATH', 'PATH', 'PYTHONPATH'],
    'application': ['screen', 'tmux', 'sudo', 'pkexec', 'polkit'],
    'program': ['sudo-wrapper', 'pkexec-helper', 'dbus-launch']
}


def generate_prompt(template, category):
    """Generate attack code using template"""
    # Substitute all variables in template at once
    substitution_dict = {}
    for key, values in SUBSTITUTIONS.items():
        if '{' + key + '}' in template:
            substitution_dict[key] = random.choice(values)
    
    filled_template = template.format(**substitution_dict)
    
    return filled_template


def generate_attack_code_lm_studio(prompt, model="qwen3-14b-mlx"):
    """Generate attack code using LM Studio API"""
    try:
        response = requests.post(
            LM_STUDIO_URL,
            json={
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.8,
                "max_tokens": 800,
                "stream": False
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return None
            
    except Exception as e:
        print(f"Error generating with LM Studio: {e}")
        return None


def generate_privilege_escalation_batch():
    """Generate 800 privilege escalation samples"""
    
    print("="*70)
    print("GLADIATOR Privilege Escalation Sample Generation")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: 800 samples (8 categories × 100 samples)")
    print(f"LM Studio: {LM_STUDIO_URL}")
    print("="*70)
    
    all_samples = []
    sample_id_counter = 1
    
    # Generate 100 samples per category
    for category, templates in PRIVILEGE_ESCALATION_TEMPLATES.items():
        print(f"\nGenerating {category.upper()}... (target: 100 samples)")
        category_samples = []
        
        for i in range(100):
            # Select random template
            template = random.choice(templates)
            
            # Generate prompt
            prompt = generate_prompt(template, category)
            
            # Generate attack code
            attack_code = generate_attack_code_lm_studio(prompt)
            
            if attack_code:
                sample = {
                    "id": f"priv_esc_{sample_id_counter:04d}",
                    "category": "privilege_escalation",
                    "subcategory": category,
                    "template": prompt,
                    "attack_code": attack_code,
                    "model": "qwen3-14b-mlx",
                    "generated_at": datetime.now().isoformat(),
                    "generation_batch": "track3_privilege_escalation",
                    "quality_reviewed": False
                }
                
                category_samples.append(sample)
                all_samples.append(sample)
                sample_id_counter += 1
                
                # Progress update
                if (i + 1) % 10 == 0:
                    print(f"  Progress: {i + 1}/100 samples")
                    time.sleep(0.1)  # Rate limiting
            else:
                print(f"  Failed to generate sample {i + 1}, retrying...")
                continue
        
        print(f"  ✅ {category}: {len(category_samples)} samples generated")
    
    print(f"\n{'='*70}")
    print(f"Total Samples Generated: {len(all_samples)}/800")
    print(f"Generation Complete: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Save samples
    output_dir = Path("/Volumes/DATA/GLADIATOR/datasets/expansion")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "privilege_escalation_batch1.jsonl"
    with open(output_file, 'w') as f:
        for sample in all_samples:
            f.write(json.dumps(sample) + '\n')
    
    print(f"\n💾 Saved to: {output_file}")
    print(f"File size: {output_file.stat().st_size / 1024 / 1024:.2f} MB")
    
    # Generate summary report
    summary = {
        "batch_name": "privilege_escalation_batch1",
        "generated_at": datetime.now().isoformat(),
        "total_samples": len(all_samples),
        "target_samples": 800,
        "completion_percentage": (len(all_samples) / 800 * 100),
        "categories": {cat: sum(1 for s in all_samples if s['subcategory'] == cat) 
                      for cat in PRIVILEGE_ESCALATION_TEMPLATES.keys()},
        "model_used": "qwen3-14b-mlx",
        "lm_studio_url": LM_STUDIO_URL,
        "quality_review_pending": True,
        "output_file": str(output_file)
    }
    
    summary_file = output_dir / "privilege_escalation_batch1_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"📋 Summary: {summary_file}")
    print("="*70)
    
    return all_samples, summary


if __name__ == "__main__":
    # Note: This script should be run on BETA system
    import sys
    
    # Check if running on BETA
    import socket
    hostname = socket.gethostname()
    
    if 'beta' not in hostname.lower():
        print("⚠️  WARNING: This script should run on BETA system")
        print(f"Current hostname: {hostname}")
        response = input("Continue anyway? (yes/no): ")
        if response.lower() != 'yes':
            print("Execution cancelled")
            sys.exit(0)
    
    samples, summary = generate_privilege_escalation_batch()
    
    print(f"\n✅ Privilege Escalation Batch 1 Generation Complete")
    print(f"Samples: {summary['total_samples']}/800")
    print(f"Next: Manual quality review of {int(summary['total_samples'] * 0.1)} samples (10%)")

