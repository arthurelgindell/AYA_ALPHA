#!/usr/bin/env python3
"""
GLADIATOR Multi-Class Attack Detection Dataset Preparation
Prepare dataset for attack type classification
"""

import json
import random
from pathlib import Path
from collections import Counter

# Attack type patterns for classification
ATTACK_TYPE_PATTERNS = {
    'sql_injection': ['sql', 'injection', 'query', 'select', 'union', 'drop', 'insert', 'database'],
    'xss': ['xss', 'cross-site', 'script', 'javascript', 'alert', 'onerror', 'onclick'],
    'phishing': ['phishing', 'phish', 'credential', 'fake', 'impersonat', 'social engineering'],
    'command_injection': ['command', 'injection', 'exec', 'shell', 'system', 'os'],
    'privilege_escalation': ['privilege', 'escalat', 'elevat', 'admin', 'root', 'suid'],
    'buffer_overflow': ['buffer', 'overflow', 'memory', 'segmentation', 'stack', 'heap'],
    'dos': ['denial', 'service', 'dos', 'ddos', 'flood', 'amplification'],
    'mitm': ['man-in-the-middle', 'mitm', 'intercept', 'eavesdrop', 'sniff'],
    'path_traversal': ['path', 'traversal', 'directory', '../', '..\\', 'file inclusion'],
    'malware': ['malware', 'virus', 'trojan', 'backdoor', 'ransomware']
}


def detect_attack_type_from_template(template):
    """Detect attack type from template text"""
    if not template:
        return 'unknown'
    
    template_lower = template.lower()
    
    # Count matches for each attack type
    scores = {}
    for attack_type, keywords in ATTACK_TYPE_PATTERNS.items():
        score = sum(1 for keyword in keywords if keyword in template_lower)
        if score > 0:
            scores[attack_type] = score
    
    # Return attack type with highest score
    if scores:
        return max(scores, key=scores.get)
    return 'unknown'


def load_jsonl(filepath):
    """Load JSONL file"""
    samples = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.strip():
                samples.append(json.loads(line.strip()))
    return samples


def prepare_multiclass_dataset(samples, output_path, dataset_type="train"):
    """
    Prepare multi-class detection dataset in chat format
    
    Format: {"messages": [
        {"role": "user", "content": "Analyze this attack and identify the type: [code]"},
        {"role": "assistant", "content": "[attack_type]"}
    ]}
    """
    
    formatted_samples = []
    
    for sample in samples:
        # Get attack code/template
        code = sample.get('attack_code', sample.get('template', ''))
        template = sample.get('template', '')
        
        if not code:
            continue
        
        # Detect attack type from template
        attack_type = detect_attack_type_from_template(template)
        
        formatted_samples.append({
            "messages": [
                {
                    "role": "user",
                    "content": f"Analyze this cyber attack code and identify the specific attack type:\n\n{code}\n\nWhat type of attack is this? (sql_injection, xss, phishing, command_injection, privilege_escalation, buffer_overflow, dos, mitm, path_traversal, malware, or unknown)"
                },
                {
                    "role": "assistant",
                    "content": attack_type
                }
            ],
            "label": attack_type,
            "original_id": sample.get('id', 'unknown'),
            "original_template": template[:100]
        })
    
    # Shuffle
    random.shuffle(formatted_samples)
    
    # Save to JSONL
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        for sample in formatted_samples:
            f.write(json.dumps(sample) + '\n')
    
    # Calculate statistics
    attack_types = [s['label'] for s in formatted_samples]
    type_counts = Counter(attack_types)
    
    print(f"\n{dataset_type.upper()} Dataset:")
    print(f"  Total samples: {len(formatted_samples)}")
    print(f"\n  Attack type distribution:")
    for attack_type, count in type_counts.most_common():
        pct = count / len(formatted_samples) * 100
        print(f"    {attack_type}: {count} ({pct:.1f}%)")
    print(f"  Saved to: {output_path}")
    
    return formatted_samples


def main():
    print("="*70)
    print("GLADIATOR Multi-Class Attack Detection Dataset Preparation")
    print("="*70)
    
    # Paths
    base_dir = Path("/Users/arthurdell/GLADIATOR")
    datasets_dir = base_dir / "datasets"
    training_dir = base_dir / "training" / "reality_check_data"
    
    # Load attack samples (only attack samples, not benign)
    print("\nLoading attack samples...")
    attack_train = load_jsonl(datasets_dir / "reality_check_train_900.jsonl")
    attack_val = load_jsonl(datasets_dir / "reality_check_val_100.jsonl")
    print(f"  Attack training: {len(attack_train)} samples")
    print(f"  Attack validation: {len(attack_val)} samples")
    
    # Prepare training dataset
    print("\nPreparing multi-class detection datasets...")
    train_data = prepare_multiclass_dataset(
        attack_train,
        training_dir / "multiclass_train_900.jsonl",
        "train"
    )
    
    # Prepare validation dataset
    val_data = prepare_multiclass_dataset(
        attack_val,
        training_dir / "multiclass_val_100.jsonl",
        "validation"
    )
    
    # Sample verification
    print("\n" + "="*70)
    print("Sample Verification:")
    print("="*70)
    print("\nSample Training Example:")
    print(json.dumps(train_data[0], indent=2))
    
    print("\n✅ Multi-class detection dataset preparation complete!")
    print("="*70)


if __name__ == "__main__":
    main()

