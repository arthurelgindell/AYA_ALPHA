#!/usr/bin/env python3
"""
GLADIATOR Persona Training Data Analyzer
Analyzes persona-based combat training data with sophistication metrics
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime


TRAINING_DIR = Path("/Users/arthurdell/GLADIATOR/datasets/persona_combat_training")


def analyze_persona_session(session_file):
    """Analyze single persona combat session"""
    with open(session_file) as f:
        data = json.load(f)
    
    stats = {
        'session_id': data['session_id'],
        'timestamp': data['timestamp'],
        'total_rounds': len(data['training_pairs']),
        'blue_successes': sum(1 for p in data['training_pairs'] if p['labels']['blue_success']),
        'blue_failures': sum(1 for p in data['training_pairs'] if not p['labels']['blue_success']),
        'high_value_pairs': sum(1 for p in data['training_pairs'] if p['labels']['training_value'] == 'high'),
        'persona_distribution': Counter(p['labels']['attack_type'] for p in data['training_pairs']),
        'sophistication_distribution': Counter(p['labels']['sophistication'] for p in data['training_pairs']),
        'threat_level_distribution': Counter(p['labels']['threat_level'] for p in data['training_pairs']),
        'avg_attack_length': sum(len(p['attack']) for p in data['training_pairs']) / len(data['training_pairs']) if data['training_pairs'] else 0,
        'avg_defense_length': sum(len(p['defense']) for p in data['training_pairs']) / len(data['training_pairs']) if data['training_pairs'] else 0,
        'detection_scores': [p['outcome']['detection_score'] for p in data['training_pairs']]
    }
    
    return stats


def aggregate_persona_stats(all_stats):
    """Aggregate statistics across all persona sessions"""
    if not all_stats:
        return {}
    
    total_rounds = sum(s['total_rounds'] for s in all_stats)
    total_successes = sum(s['blue_successes'] for s in all_stats)
    
    # Aggregate distributions
    persona_dist = Counter()
    sophistication_dist = Counter()
    threat_level_dist = Counter()
    
    for s in all_stats:
        persona_dist.update(s['persona_distribution'])
        sophistication_dist.update(s['sophistication_distribution'])
        threat_level_dist.update(s['threat_level_distribution'])
    
    # Calculate detection rates by persona
    persona_detection_rates = defaultdict(lambda: {'successes': 0, 'total': 0})
    sophistication_detection_rates = defaultdict(lambda: {'successes': 0, 'total': 0})
    
    for s in all_stats:
        for pair in s.get('training_pairs', []):
            persona = pair['labels']['attack_type']
            sophistication = pair['labels']['sophistication']
            
            persona_detection_rates[persona]['total'] += 1
            sophistication_detection_rates[sophistication]['total'] += 1
            
            if pair['labels']['blue_success']:
                persona_detection_rates[persona]['successes'] += 1
                sophistication_detection_rates[sophistication]['successes'] += 1
    
    return {
        'total_sessions': len(all_stats),
        'total_training_pairs': total_rounds,
        'overall_detection_rate': (total_successes / total_rounds * 100) if total_rounds > 0 else 0,
        'total_high_value': sum(s['high_value_pairs'] for s in all_stats),
        'persona_distribution': dict(persona_dist),
        'sophistication_distribution': dict(sophistication_dist),
        'threat_level_distribution': dict(threat_level_dist),
        'persona_detection_rates': {k: (v['successes']/v['total']*100) if v['total'] > 0 else 0 
                                   for k, v in persona_detection_rates.items()},
        'sophistication_detection_rates': {k: (v['successes']/v['total']*100) if v['total'] > 0 else 0 
                                          for k, v in sophistication_detection_rates.items()},
        'avg_attack_length': sum(s['avg_attack_length'] for s in all_stats) / len(all_stats),
        'avg_defense_length': sum(s['avg_defense_length'] for s in all_stats) / len(all_stats),
        'all_detection_scores': [score for s in all_stats for score in s['detection_scores']]
    }


def main():
    """Main persona analysis"""
    session_files = sorted(TRAINING_DIR.glob("persona_combat_session_*.json"))
    
    if not session_files:
        print("❌ No persona training data found")
        return
    
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║           GLADIATOR PERSONA TRAINING DATA ANALYSIS              ║
╚══════════════════════════════════════════════════════════════════╝

Analyzing {len(session_files)} persona session(s)...
""")
    
    all_stats = []
    for session_file in session_files:
        print(f"\n📊 {session_file.name}")
        stats = analyze_persona_session(session_file)
        all_stats.append(stats)
        
        print(f"   Rounds: {stats['total_rounds']}")
        if stats['total_rounds'] > 0:
            print(f"   Blue Detections: {stats['blue_successes']}/{stats['total_rounds']} ({stats['blue_successes']/stats['total_rounds']*100:.1f}%)")
        else:
            print(f"   Blue Detections: 0/0 (0.0%) - No training pairs")
        print(f"   High-value pairs: {stats['high_value_pairs']}")
        print(f"   Personas: {dict(stats['persona_distribution'])}")
        print(f"   Sophistication: {dict(stats['sophistication_distribution'])}")
    
    # Aggregate
    agg = aggregate_persona_stats(all_stats)
    
    print(f"""
{'='*70}
PERSONA AGGREGATE STATISTICS
{'='*70}

Total Sessions:        {agg['total_sessions']}
Total Training Pairs:  {agg['total_training_pairs']}
Overall Detection Rate: {agg['overall_detection_rate']:.1f}%
High-Value Pairs:      {agg['total_high_value']} ({agg['total_high_value']/agg['total_training_pairs']*100:.1f}%)

Average Attack Length:  {agg['avg_attack_length']:.0f} chars
Average Defense Length: {agg['avg_defense_length']:.0f} chars

Persona Distribution:
""")
    
    for persona, count in sorted(agg['persona_distribution'].items(), key=lambda x: x[1], reverse=True):
        pct = count / agg['total_training_pairs'] * 100
        detection_rate = agg['persona_detection_rates'].get(persona, 0)
        print(f"  {persona:20s}: {count:3d} ({pct:5.1f}%) - Detection: {detection_rate:.1f}%")
    
    print(f"""
Sophistication Distribution:
""")
    
    for sophistication, count in sorted(agg['sophistication_distribution'].items(), key=lambda x: x[1], reverse=True):
        pct = count / agg['total_training_pairs'] * 100
        detection_rate = agg['sophistication_detection_rates'].get(sophistication, 0)
        print(f"  {sophistication:20s}: {count:3d} ({pct:5.1f}%) - Detection: {detection_rate:.1f}%")
    
    if agg['all_detection_scores']:
        avg_score = sum(agg['all_detection_scores']) / len(agg['all_detection_scores'])
        max_score = max(agg['all_detection_scores'])
        min_score = min(agg['all_detection_scores'])
        
        print(f"""
Detection Score Statistics:
  Average Score: {avg_score:.1f}/10
  Maximum Score: {max_score:.1f}/10
  Minimum Score: {min_score:.1f}/10
""")
    
    print(f"""
{'='*70}

✅ Persona analysis complete. Training data ready for model fine-tuning.

NEXT STEPS:
1. Convert persona JSON pairs to model-specific format
2. Balance persona distribution if needed
3. Filter by training_value and sophistication level
4. Begin model fine-tuning with persona-aware data

""")


if __name__ == "__main__":
    main()
