#!/usr/bin/env python3
"""
GLADIATOR Training Data Analyzer
Evaluates quality and extracts insights from combat training data
"""

import json
from pathlib import Path
from collections import Counter
from datetime import datetime


TRAINING_DIR = Path("/Users/arthurdell/GLADIATOR/datasets/combat_training")


def analyze_session(session_file):
    """Analyze single combat session"""
    with open(session_file) as f:
        data = json.load(f)
    
    stats = {
        'session_id': data['session_id'],
        'timestamp': data['timestamp'],
        'total_rounds': len(data['training_pairs']),
        'blue_successes': sum(1 for p in data['training_pairs'] if p['labels']['blue_success']),
        'blue_failures': sum(1 for p in data['training_pairs'] if not p['labels']['blue_success']),
        'high_value_pairs': sum(1 for p in data['training_pairs'] if p['labels']['training_value'] == 'high'),
        'attack_types': Counter(p['labels']['attack_type'] for p in data['training_pairs']),
        'avg_attack_length': sum(len(p['attack']) for p in data['training_pairs']) / len(data['training_pairs']) if data['training_pairs'] else 0,
        'avg_defense_length': sum(len(p['defense']) for p in data['training_pairs']) / len(data['training_pairs']) if data['training_pairs'] else 0
    }
    
    return stats


def aggregate_stats(all_stats):
    """Aggregate statistics across all sessions"""
    if not all_stats:
        return {}
    
    total_rounds = sum(s['total_rounds'] for s in all_stats)
    total_successes = sum(s['blue_successes'] for s in all_stats)
    
    attack_types = Counter()
    for s in all_stats:
        attack_types.update(s['attack_types'])
    
    return {
        'total_sessions': len(all_stats),
        'total_training_pairs': total_rounds,
        'blue_detection_rate': (total_successes / total_rounds * 100) if total_rounds > 0 else 0,
        'total_high_value': sum(s['high_value_pairs'] for s in all_stats),
        'attack_type_distribution': dict(attack_types),
        'avg_attack_length': sum(s['avg_attack_length'] for s in all_stats) / len(all_stats),
        'avg_defense_length': sum(s['avg_defense_length'] for s in all_stats) / len(all_stats)
    }


def main():
    """Main analysis"""
    session_files = sorted(TRAINING_DIR.glob("combat_session_*.json"))
    
    if not session_files:
        print("❌ No training data found")
        return
    
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║              GLADIATOR TRAINING DATA ANALYSIS                    ║
╚══════════════════════════════════════════════════════════════════╝

Analyzing {len(session_files)} session(s)...
""")
    
    all_stats = []
    for session_file in session_files:
        print(f"\n📊 {session_file.name}")
        stats = analyze_session(session_file)
        all_stats.append(stats)
        
        print(f"   Rounds: {stats['total_rounds']}")
        print(f"   Blue Detections: {stats['blue_successes']}/{stats['total_rounds']} ({stats['blue_successes']/stats['total_rounds']*100:.1f}%)")
        print(f"   High-value pairs: {stats['high_value_pairs']}")
        print(f"   Attack types: {dict(stats['attack_types'])}")
    
    # Aggregate
    agg = aggregate_stats(all_stats)
    
    print(f"""
{'='*70}
AGGREGATE STATISTICS
{'='*70}

Total Sessions:        {agg['total_sessions']}
Total Training Pairs:  {agg['total_training_pairs']}
Blue Detection Rate:   {agg['blue_detection_rate']:.1f}%
High-Value Pairs:      {agg['total_high_value']} ({agg['total_high_value']/agg['total_training_pairs']*100:.1f}%)

Average Attack Length:  {agg['avg_attack_length']:.0f} chars
Average Defense Length: {agg['avg_defense_length']:.0f} chars

Attack Type Distribution:
""")
    
    for attack_type, count in sorted(agg['attack_type_distribution'].items(), key=lambda x: x[1], reverse=True):
        pct = count / agg['total_training_pairs'] * 100
        print(f"  {attack_type:20s}: {count:3d} ({pct:5.1f}%)")
    
    print(f"""
{'='*70}

✅ Analysis complete. Training data ready for model fine-tuning.

NEXT STEPS:
1. Convert JSON pairs to model-specific format (JSONL, Parquet, etc.)
2. Balance attack type distribution if needed
3. Filter by training_value (high/medium)
4. Begin model fine-tuning with combat data

""")


if __name__ == "__main__":
    main()

