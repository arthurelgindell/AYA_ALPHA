#!/usr/bin/env python3
"""
GLADIATOR Binary Classification Dataset Preparation
Combine attack and benign samples into binary classification format
"""

import json
import random
from pathlib import Path

def load_jsonl(filepath):
    """Load JSONL file"""
    samples = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.strip():
                samples.append(json.loads(line.strip()))
    return samples


def prepare_binary_dataset(attack_samples, benign_samples, output_path, dataset_type="train"):
    """
    Prepare binary classification dataset in chat format
    
    Format: {"messages": [
        {"role": "user", "content": "Analyze this code and determine if it's an attack or benign: [code]"},
        {"role": "assistant", "content": "attack"} or {"role": "assistant", "content": "benign"}
    ]}
    """
    
    combined_samples = []
    
    # Process attack samples
    for sample in attack_samples:
        code = sample.get('attack_code', sample.get('template', ''))
        if not code:
            continue
            
        combined_samples.append({
            "messages": [
                {
                    "role": "user",
                    "content": f"Analyze this code and determine if it's a cyber attack or benign activity:\n\n{code}\n\nIs this an attack or benign?"
                },
                {
                    "role": "assistant",
                    "content": "attack"
                }
            ],
            "label": "attack",
            "original_id": sample.get('id', 'unknown'),
            "category": sample.get('category', 'attack')
        })
    
    # Process benign samples
    for sample in benign_samples:
        code = sample.get('attack_code', sample.get('template', ''))
        if not code:
            continue
            
        combined_samples.append({
            "messages": [
                {
                    "role": "user",
                    "content": f"Analyze this code and determine if it's a cyber attack or benign activity:\n\n{code}\n\nIs this an attack or benign?"
                },
                {
                    "role": "assistant",
                    "content": "benign"
                }
            ],
            "label": "benign",
            "original_id": sample.get('id', 'unknown'),
            "category": sample.get('category', 'benign')
        })
    
    # Shuffle for better training
    random.shuffle(combined_samples)
    
    # Save to JSONL
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        for sample in combined_samples:
            f.write(json.dumps(sample) + '\n')
    
    # Calculate statistics
    attack_count = sum(1 for s in combined_samples if s['label'] == 'attack')
    benign_count = sum(1 for s in combined_samples if s['label'] == 'benign')
    
    print(f"\n{dataset_type.upper()} Dataset:")
    print(f"  Total samples: {len(combined_samples)}")
    print(f"  Attack samples: {attack_count}")
    print(f"  Benign samples: {benign_count}")
    print(f"  Balance: {attack_count/len(combined_samples)*100:.1f}% attack, {benign_count/len(combined_samples)*100:.1f}% benign")
    print(f"  Saved to: {output_path}")
    
    return combined_samples


def main():
    print("="*70)
    print("GLADIATOR Binary Classification Dataset Preparation")
    print("="*70)
    
    # Paths
    base_dir = Path("/Users/arthurdell/GLADIATOR")
    datasets_dir = base_dir / "datasets"
    training_dir = base_dir / "training" / "reality_check_data"
    
    # Load attack samples
    print("\nLoading attack samples...")
    attack_train = load_jsonl(datasets_dir / "reality_check_train_900.jsonl")
    attack_val = load_jsonl(datasets_dir / "reality_check_val_100.jsonl")
    print(f"  Attack training: {len(attack_train)} samples")
    print(f"  Attack validation: {len(attack_val)} samples")
    
    # Load benign samples
    print("\nLoading benign samples...")
    benign_train = load_jsonl(datasets_dir / "benign_train_900.jsonl")
    benign_val = load_jsonl(datasets_dir / "benign_val_100.jsonl")
    print(f"  Benign training: {len(benign_train)} samples")
    print(f"  Benign validation: {len(benign_val)} samples")
    
    # Prepare training dataset
    print("\nPreparing binary classification datasets...")
    train_data = prepare_binary_dataset(
        attack_train,
        benign_train,
        training_dir / "binary_train_1800.jsonl",
        "train"
    )
    
    # Prepare validation dataset
    val_data = prepare_binary_dataset(
        attack_val,
        benign_val,
        training_dir / "binary_val_200.jsonl",
        "validation"
    )
    
    # Sample verification
    print("\n" + "="*70)
    print("Sample Verification:")
    print("="*70)
    print("\nSample Training Example:")
    print(json.dumps(train_data[0], indent=2))
    
    print("\n✅ Binary classification dataset preparation complete!")
    print("="*70)


if __name__ == "__main__":
    main()

