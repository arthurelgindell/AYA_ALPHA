#!/usr/bin/env python3
"""
GLADIATOR Training Data Preparation
Converts combat training data to model fine-tuning format
"""

import json
import csv
from pathlib import Path
from datetime import datetime
import random

# Input directories
COMBAT_TRAINING_DIR = Path("/Users/arthurdell/GLADIATOR/datasets/combat_training")
PERSONA_TRAINING_DIR = Path("/Users/arthurdell/GLADIATOR/datasets/persona_combat_training")

# Output directories
FINE_TUNING_DIR = Path("/Users/arthurdell/GLADIATOR/datasets/fine_tuning")
FINE_TUNING_DIR.mkdir(exist_ok=True)


def load_all_training_pairs():
    """Load all training pairs from combat sessions"""
    all_pairs = []
    
    # Load regular combat training
    for session_file in COMBAT_TRAINING_DIR.glob("combat_session_*.json"):
        try:
            with open(session_file) as f:
                data = json.load(f)
                for pair in data.get('training_pairs', []):
                    pair['source'] = 'regular_combat'
                    pair['session_file'] = session_file.name
                    all_pairs.append(pair)
        except Exception as e:
            print(f"⚠️  Failed to load {session_file}: {e}")
    
    # Load persona combat training
    for session_file in PERSONA_TRAINING_DIR.glob("persona_combat_session_*.json"):
        try:
            with open(session_file) as f:
                data = json.load(f)
                for pair in data.get('training_pairs', []):
                    pair['source'] = 'persona_combat'
                    pair['session_file'] = session_file.name
                    all_pairs.append(pair)
        except Exception as e:
            print(f"⚠️  Failed to load {session_file}: {e}")
    
    return all_pairs


def create_training_formats(all_pairs):
    """Create different training data formats"""
    
    # Filter high-quality pairs
    high_quality_pairs = [p for p in all_pairs if p['labels']['training_value'] in ['high', 'medium']]
    
    print(f"Total pairs: {len(all_pairs)}")
    print(f"High-quality pairs: {len(high_quality_pairs)}")
    
    # 1. JSONL format for general fine-tuning
    jsonl_file = FINE_TUNING_DIR / "gladiator_training.jsonl"
    with open(jsonl_file, 'w') as f:
        for pair in high_quality_pairs:
            training_example = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are GLADIATOR Blue Team - a defensive AI that analyzes cyber attacks and generates defense strategies."
                    },
                    {
                        "role": "user", 
                        "content": f"Analyze this attack and provide defense strategy:\n\n{pair['attack']}"
                    },
                    {
                        "role": "assistant",
                        "content": pair['defense']
                    }
                ],
                "metadata": {
                    "pair_id": pair['pair_id'],
                    "source": pair['source'],
                    "attack_type": pair['labels'].get('attack_type', 'unknown'),
                    "sophistication": pair['labels'].get('sophistication', 'unknown'),
                    "blue_success": pair['labels']['blue_success'],
                    "training_value": pair['labels']['training_value']
                }
            }
            f.write(json.dumps(training_example) + '\n')
    
    print(f"✅ JSONL format: {jsonl_file} ({len(high_quality_pairs)} examples)")
    
    # 2. CSV format for analysis
    csv_file = FINE_TUNING_DIR / "gladiator_training.csv"
    df_data = []
    for pair in all_pairs:
        df_data.append({
            'pair_id': pair['pair_id'],
            'source': pair['source'],
            'attack': pair['attack'][:500] + '...' if len(pair['attack']) > 500 else pair['attack'],
            'defense': pair['defense'][:500] + '...' if len(pair['defense']) > 500 else pair['defense'],
            'attack_type': pair['labels'].get('attack_type', 'unknown'),
            'persona_name': pair['labels'].get('persona_name', 'unknown'),
            'sophistication': pair['labels'].get('sophistication', 'unknown'),
            'threat_level': pair['labels'].get('threat_level', 'unknown'),
            'blue_success': pair['labels']['blue_success'],
            'training_value': pair['labels']['training_value'],
            'detection_score': pair['outcome'].get('detection_score', 0),
            'attack_length': len(pair['attack']),
            'defense_length': len(pair['defense'])
        })
    
    # Write CSV manually without pandas
    with open(csv_file, 'w', newline='') as f:
        if df_data:
            writer = csv.DictWriter(f, fieldnames=df_data[0].keys())
            writer.writeheader()
            writer.writerows(df_data)
    print(f"✅ CSV format: {csv_file} ({len(df_data)} examples)")
    
    # 3. Persona-specific datasets
    persona_datasets = {}
    for pair in high_quality_pairs:
        persona = pair['labels'].get('attack_type', 'unknown')
        if persona not in persona_datasets:
            persona_datasets[persona] = []
        persona_datasets[persona].append(pair)
    
    for persona, pairs in persona_datasets.items():
        if len(pairs) >= 3:  # Only create datasets with sufficient examples
            persona_file = FINE_TUNING_DIR / f"gladiator_{persona}_training.jsonl"
            with open(persona_file, 'w') as f:
                for pair in pairs:
                    training_example = {
                        "messages": [
                            {
                                "role": "system",
                                "content": f"You are GLADIATOR Blue Team defending against {pair['labels'].get('persona_name', persona)} attacks. This attacker has {pair['labels'].get('sophistication', 'unknown')} sophistication level."
                            },
                            {
                                "role": "user",
                                "content": f"Analyze this {persona} attack and provide defense strategy:\n\n{pair['attack']}"
                            },
                            {
                                "role": "assistant", 
                                "content": pair['defense']
                            }
                        ],
                        "metadata": {
                            "pair_id": pair['pair_id'],
                            "persona": persona,
                            "sophistication": pair['labels'].get('sophistication', 'unknown'),
                            "blue_success": pair['labels']['blue_success']
                        }
                    }
                    f.write(json.dumps(training_example) + '\n')
            
            print(f"✅ {persona} dataset: {persona_file} ({len(pairs)} examples)")
    
    # 4. Balanced dataset (equal representation)
    balanced_pairs = []
    min_pairs_per_persona = min(len(pairs) for pairs in persona_datasets.values()) if persona_datasets else 0
    
    if min_pairs_per_persona > 0:
        for persona, pairs in persona_datasets.items():
            # Randomly sample to balance
            sampled = random.sample(pairs, min(min_pairs_per_persona, len(pairs)))
            balanced_pairs.extend(sampled)
        
        balanced_file = FINE_TUNING_DIR / "gladiator_balanced_training.jsonl"
        with open(balanced_file, 'w') as f:
            for pair in balanced_pairs:
                training_example = {
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are GLADIATOR Blue Team - a defensive AI that analyzes cyber attacks and generates defense strategies."
                        },
                        {
                            "role": "user",
                            "content": f"Analyze this attack and provide defense strategy:\n\n{pair['attack']}"
                        },
                        {
                            "role": "assistant",
                            "content": pair['defense']
                        }
                    ],
                    "metadata": {
                        "pair_id": pair['pair_id'],
                        "persona": pair['labels'].get('attack_type', 'unknown'),
                        "sophistication": pair['labels'].get('sophistication', 'unknown')
                    }
                }
                f.write(json.dumps(training_example) + '\n')
        
        print(f"✅ Balanced dataset: {balanced_file} ({len(balanced_pairs)} examples)")
    
    return {
        'total_pairs': len(all_pairs),
        'high_quality_pairs': len(high_quality_pairs),
        'persona_datasets': len(persona_datasets),
        'balanced_pairs': len(balanced_pairs) if min_pairs_per_persona > 0 else 0
    }


def generate_training_summary(stats):
    """Generate training data summary"""
    summary_file = FINE_TUNING_DIR / "training_summary.md"
    
    with open(summary_file, 'w') as f:
        f.write(f"""# GLADIATOR Training Data Summary
Generated: {datetime.now().isoformat()}

## Dataset Statistics
- **Total Training Pairs**: {stats['total_pairs']}
- **High-Quality Pairs**: {stats['high_quality_pairs']}
- **Persona-Specific Datasets**: {stats['persona_datasets']}
- **Balanced Dataset Pairs**: {stats['balanced_pairs']}

## Available Formats
1. **gladiator_training.jsonl** - Complete high-quality dataset
2. **gladiator_training.csv** - Analysis and exploration format
3. **gladiator_*_training.jsonl** - Persona-specific datasets
4. **gladiator_balanced_training.jsonl** - Balanced representation

## Usage for Fine-Tuning
```bash
# General fine-tuning
python -m transformers.trainer --train_file gladiator_training.jsonl

# Persona-specific fine-tuning  
python -m transformers.trainer --train_file gladiator_script_kiddie_training.jsonl

# Balanced fine-tuning
python -m transformers.trainer --train_file gladiator_balanced_training.jsonl
```

## Data Quality
- All examples include attack-defense pairs
- Metadata includes persona, sophistication, and success metrics
- High-quality examples filtered by training_value
- Balanced datasets ensure equal representation

## Next Steps
1. Validate training data quality
2. Split into train/validation sets
3. Begin model fine-tuning
4. Evaluate performance on test set
""")
    
    print(f"✅ Training summary: {summary_file}")


def main():
    """Main training data preparation"""
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║              GLADIATOR TRAINING DATA PREPARATION                 ║
╚══════════════════════════════════════════════════════════════════╝

Preparing training data for model fine-tuning...
""")
    
    # Load all training pairs
    all_pairs = load_all_training_pairs()
    
    if not all_pairs:
        print("❌ No training pairs found")
        return
    
    # Create training formats
    stats = create_training_formats(all_pairs)
    
    # Generate summary
    generate_training_summary(stats)
    
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║                    PREPARATION COMPLETE                          ║
╚══════════════════════════════════════════════════════════════════╝

Training data prepared in: {FINE_TUNING_DIR}
Ready for model fine-tuning!

""")


if __name__ == "__main__":
    main()
