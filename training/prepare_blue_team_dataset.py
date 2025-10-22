#!/usr/bin/env python3
"""
GLADIATOR Blue Team Dataset Preparation
Prepare 11,000 balanced samples for production training
"""

import json
import random
from pathlib import Path
from collections import Counter
from datetime import datetime

def load_jsonl(filepath):
    """Load samples from JSONL file"""
    samples = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.strip():
                samples.append(json.loads(line.strip()))
    return samples

def validate_sample(sample, sample_id):
    """
    Validate sample meets quality requirements
    Returns: (is_valid, error_message)
    """
    # Check required fields
    required_fields = ['id', 'messages']
    for field in required_fields:
        if field not in sample:
            return False, f"Missing field: {field}"
    
    # Check messages structure
    if not isinstance(sample['messages'], list):
        return False, "messages field must be a list"
    
    if len(sample['messages']) != 2:
        return False, f"messages must have 2 entries (user + assistant), got {len(sample['messages'])}"
    
    # Check user message
    user_msg = sample['messages'][0]
    if user_msg.get('role') != 'user':
        return False, "First message must be user role"
    
    if not user_msg.get('content'):
        return False, "User message content is empty"
    
    # Check assistant message
    assistant_msg = sample['messages'][1]
    if assistant_msg.get('role') != 'assistant':
        return False, "Second message must be assistant role"
    
    response = assistant_msg.get('content', '')
    if not response:
        return False, "Assistant response is empty"
    
    # Check response length
    if len(response) < 10:
        return False, f"Response too short: {len(response)} chars"
    
    if len(response) > 3000:
        return False, f"Response too long: {len(response)} chars"
    
    return True, None

def analyze_distribution(samples):
    """Analyze sample distribution"""
    categories = []
    for sample in samples:
        # Extract category from response
        response = sample['messages'][1]['content'].lower()
        
        if 'benign' in response:
            categories.append('benign')
        elif 'sql' in response or 'injection' in response:
            categories.append('sql_injection')
        elif 'xss' in response or 'cross-site' in response:
            categories.append('xss')
        elif 'phish' in response:
            categories.append('phishing')
        elif 'command' in response and 'injection' in response:
            categories.append('command_injection')
        elif 'privilege' in response or 'escalat' in response:
            categories.append('privilege_escalation')
        elif 'buffer' in response or 'overflow' in response:
            categories.append('buffer_overflow')
        elif 'dos' in response or 'denial' in response:
            categories.append('dos')
        elif 'mitm' in response or 'man-in-the-middle' in response:
            categories.append('mitm')
        else:
            categories.append('unknown')
    
    return Counter(categories)

def prepare_blue_team_dataset(
    attack_sources,
    benign_sources,
    output_dir,
    total_samples=11000,
    train_split=0.8,
    valid_split=0.2
):
    """
    Prepare Blue Team dataset from multiple sources
    
    Args:
        attack_sources: List of file paths containing attack samples
        benign_sources: List of file paths containing benign samples
        output_dir: Output directory for prepared datasets
        total_samples: Target total samples (default 11,000)
        train_split: Training set ratio (default 0.8)
        valid_split: Validation set ratio (default 0.2)
    """
    
    print("="*80)
    print("GLADIATOR Blue Team Dataset Preparation")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load attack samples
    print("Loading attack samples...")
    attack_samples = []
    for source in attack_sources:
        if Path(source).exists():
            samples = load_jsonl(source)
            attack_samples.extend(samples)
            print(f"  Loaded {len(samples)} samples from {Path(source).name}")
    
    print(f"Total attack samples: {len(attack_samples)}")
    print()
    
    # Load benign samples
    print("Loading benign samples...")
    benign_samples = []
    for source in benign_sources:
        if Path(source).exists():
            samples = load_jsonl(source)
            benign_samples.extend(samples)
            print(f"  Loaded {len(samples)} samples from {Path(source).name}")
    
    print(f"Total benign samples: {len(benign_samples)}")
    print()
    
    # Target: 50/50 split
    target_attack = total_samples // 2
    target_benign = total_samples // 2
    
    # Sample or duplicate to reach target
    if len(attack_samples) > target_attack:
        attack_samples = random.sample(attack_samples, target_attack)
        print(f"Sampled {target_attack} attack samples")
    elif len(attack_samples) < target_attack:
        # Duplicate samples to reach target
        repeats = target_attack // len(attack_samples)
        remainder = target_attack % len(attack_samples)
        attack_samples = attack_samples * repeats + random.sample(attack_samples, remainder)
        print(f"Warning: Duplicated attack samples to reach {target_attack}")
    
    if len(benign_samples) > target_benign:
        benign_samples = random.sample(benign_samples, target_benign)
        print(f"Sampled {target_benign} benign samples")
    elif len(benign_samples) < target_benign:
        # Duplicate samples to reach target
        repeats = target_benign // len(benign_samples)
        remainder = target_benign % len(benign_samples)
        benign_samples = benign_samples * repeats + random.sample(benign_samples, remainder)
        print(f"Warning: Duplicated benign samples to reach {target_benign}")
    
    print()
    
    # Combine and shuffle
    all_samples = attack_samples + benign_samples
    random.shuffle(all_samples)
    
    print(f"Total combined samples: {len(all_samples)}")
    print()
    
    # Quality validation
    print("Running quality validation...")
    valid_samples = []
    invalid_count = 0
    
    for i, sample in enumerate(all_samples):
        is_valid, error = validate_sample(sample, i)
        if is_valid:
            valid_samples.append(sample)
        else:
            invalid_count += 1
            if invalid_count <= 10:  # Only print first 10 errors
                print(f"  Sample {i}: INVALID - {error}")
    
    if invalid_count > 0:
        print(f"\nWarning: {invalid_count} invalid samples removed")
        print(f"Valid samples: {len(valid_samples)}")
    else:
        print(f"✅ All {len(valid_samples)} samples passed validation")
    
    print()
    
    # Analyze distribution
    print("Analyzing distribution...")
    distribution = analyze_distribution(valid_samples)
    
    print("\nCategory Distribution:")
    for category, count in distribution.most_common():
        percentage = (count / len(valid_samples)) * 100
        print(f"  {category:25s}: {count:5d} ({percentage:5.2f}%)")
    
    print()
    
    # Check balance
    max_count = max(distribution.values())
    min_count = min(distribution.values())
    variance = ((max_count - min_count) / len(valid_samples)) * 100
    
    if variance > 15:
        print(f"⚠️  Warning: High variance in distribution ({variance:.1f}%)")
        print("   Consider rebalancing before training")
    else:
        print(f"✅ Distribution balanced (variance: {variance:.1f}%)")
    
    print()
    
    # Split into train/valid
    random.shuffle(valid_samples)
    
    split_idx = int(len(valid_samples) * train_split)
    train_samples = valid_samples[:split_idx]
    valid_samples_split = valid_samples[split_idx:]
    
    print(f"Train/Valid Split:")
    print(f"  Training:   {len(train_samples):5d} samples ({train_split*100:.0f}%)")
    print(f"  Validation: {len(valid_samples_split):5d} samples ({valid_split*100:.0f}%)")
    print()
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Write files
    print("Writing dataset files...")
    
    train_file = output_path / "train.jsonl"
    with open(train_file, 'w') as f:
        for sample in train_samples:
            f.write(json.dumps(sample) + '\n')
    print(f"  ✅ {train_file} ({len(train_samples)} samples)")
    
    valid_file = output_path / "valid.jsonl"
    with open(valid_file, 'w') as f:
        for sample in valid_samples_split:
            f.write(json.dumps(sample) + '\n')
    print(f"  ✅ {valid_file} ({len(valid_samples_split)} samples)")
    
    # Create test set (subset of validation)
    test_samples = random.sample(valid_samples_split, min(500, len(valid_samples_split) // 4))
    test_file = output_path / "test.jsonl"
    with open(test_file, 'w') as f:
        for sample in test_samples:
            f.write(json.dumps(sample) + '\n')
    print(f"  ✅ {test_file} ({len(test_samples)} samples)")
    
    print()
    
    # Generate metadata
    metadata = {
        "created": datetime.now().isoformat(),
        "total_samples": len(valid_samples),
        "train_samples": len(train_samples),
        "valid_samples": len(valid_samples_split),
        "test_samples": len(test_samples),
        "train_split": train_split,
        "valid_split": valid_split,
        "distribution": dict(distribution),
        "variance_percent": round(variance, 2),
        "invalid_samples_removed": invalid_count,
        "attack_sources": [str(Path(s).name) for s in attack_sources],
        "benign_sources": [str(Path(s).name) for s in benign_sources]
    }
    
    metadata_file = output_path / "metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"  ✅ {metadata_file}")
    
    print()
    print("="*80)
    print("Blue Team Dataset Preparation Complete")
    print("="*80)
    print(f"Output directory: {output_path}")
    print(f"Ready for training: {len(train_samples)} train, {len(valid_samples_split)} validation")
    print()
    
    return metadata

if __name__ == "__main__":
    # Example usage - will be called from launcher script
    print("Blue Team Dataset Preparation Script")
    print("Usage: Called from launcher with appropriate paths")
    print()
    print("To prepare dataset:")
    print("  1. Ensure all expansion samples are in datasets/expansion/")
    print("  2. Run launch script which calls this with correct paths")
    print("  3. Output will be in datasets/blue_team_training/")

