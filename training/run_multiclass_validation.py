#!/usr/bin/env python3
"""
GLADIATOR Multi-Class Attack Detection Validation
Test fine-tuned model on validation set - Target: ≥75% accuracy
"""

import json
import time
from pathlib import Path
from collections import Counter
from mlx_lm import load, generate

def load_validation_data(filepath):
    """Load validation data from JSONL"""
    samples = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.strip():
                samples.append(json.loads(line.strip()))
    return samples


def run_multiclass_validation(model, tokenizer, samples):
    """
    Run multi-class attack detection validation
    Returns accuracy per category and overall
    """
    results = []
    correct = 0
    total = len(samples)
    
    # Track per-category accuracy
    category_stats = {}
    
    print(f"\nValidating {total} samples...")
    print("="*70)
    
    start_time = time.time()
    
    for i, sample in enumerate(samples, 1):
        # Get ground truth label
        ground_truth = sample.get('label', 'unknown')
        
        # Get user message for prediction
        messages = sample['messages']
        user_content = messages[0]['content']
        
        # Use chat template
        prompt = tokenizer.apply_chat_template(
            [{"role": "user", "content": user_content}],
            tokenize=False,
            add_generation_prompt=True
        )
        
        # Generate prediction
        try:
            response = generate(
                model,
                tokenizer,
                prompt=prompt,
                max_tokens=20,  # Attack type should be short
                verbose=False
            )
            
            # Parse response (look for attack type keywords)
            response_lower = response.lower().replace('-', '_').replace(' ', '_')
            
            predicted = 'unknown'
            # Check for each attack type
            attack_types = [
                'sql_injection', 'xss', 'phishing', 'command_injection',
                'privilege_escalation', 'buffer_overflow', 'dos', 'mitm',
                'path_traversal', 'malware'
            ]
            
            for attack_type in attack_types:
                if attack_type in response_lower:
                    predicted = attack_type
                    break
            
            # Check if correct
            is_correct = (predicted == ground_truth)
            if is_correct:
                correct += 1
            
            # Update category stats
            if ground_truth not in category_stats:
                category_stats[ground_truth] = {'total': 0, 'correct': 0}
            category_stats[ground_truth]['total'] += 1
            if is_correct:
                category_stats[ground_truth]['correct'] += 1
            
            # Store result
            results.append({
                'sample_id': i,
                'ground_truth': ground_truth,
                'predicted': predicted,
                'correct': is_correct,
                'response': response[:200]  # First 200 chars
            })
            
            # Progress update
            if i % 10 == 0:
                current_accuracy = (correct / i) * 100
                elapsed = time.time() - start_time
                print(f"Progress: {i}/{total} | Accuracy: {current_accuracy:.1f}% | Time: {elapsed:.1f}s")
                
        except Exception as e:
            print(f"ERROR on sample {i}: {e}")
            results.append({
                'sample_id': i,
                'ground_truth': ground_truth,
                'predicted': 'error',
                'correct': False,
                'error': str(e)
            })
    
    # Calculate metrics
    accuracy = (correct / total) * 100
    total_time = time.time() - start_time
    
    # Print results
    print("="*70)
    print("\n✅ VALIDATION COMPLETE")
    print("="*70)
    print(f"Total Samples: {total}")
    print(f"Correct Predictions: {correct}")
    print(f"Incorrect Predictions: {total - correct}")
    print(f"\nOVERALL ACCURACY: {accuracy:.2f}%")
    
    print(f"\nPer-Category Performance:")
    for category in sorted(category_stats.keys()):
        stats = category_stats[category]
        cat_accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"  {category}: {stats['correct']}/{stats['total']} = {cat_accuracy:.1f}%")
    
    print(f"\nTotal Time: {total_time:.1f}s")
    print(f"Avg Time per Sample: {total_time/total:.2f}s")
    print("="*70)
    
    return {
        'accuracy': accuracy,
        'total_samples': total,
        'correct': correct,
        'incorrect': total - correct,
        'category_stats': category_stats,
        'total_time': total_time,
        'results': results
    }


def main():
    print("="*70)
    print("GLADIATOR Multi-Class Attack Detection Validation")
    print("="*70)
    print("\nTarget: ≥75% accuracy for GO decision\n")
    
    # Paths
    model_path = "/Users/arthurdell/GLADIATOR/models/DavidBianco/Foundation-Sec-8B-Instruct-int8"
    adapter_path = "/Users/arthurdell/GLADIATOR/checkpoints/multiclass_detection"
    val_file = "/Users/arthurdell/GLADIATOR/training/reality_check_data/multiclass_val_100.jsonl"
    results_dir = Path("/Users/arthurdell/GLADIATOR/results")
    results_file = results_dir / "multiclass_detection_results.json"
    
    # Load model
    print("Loading fine-tuned model...")
    model_start = time.time()
    model, tokenizer = load(model_path, adapter_path=adapter_path)
    model_load_time = time.time() - model_start
    print(f"✅ Model loaded in {model_load_time:.2f}s\n")
    
    # Load validation data
    print("Loading validation dataset...")
    samples = load_validation_data(val_file)
    print(f"✅ Loaded {len(samples)} validation samples\n")
    
    # Run validation
    metrics = run_multiclass_validation(model, tokenizer, samples)
    
    # Assessment
    print("\n" + "="*70)
    print("MULTI-CLASS DETECTION ASSESSMENT")
    print("="*70)
    print(f"\nAccuracy Target: ≥75.0%")
    print(f"Achieved Accuracy: {metrics['accuracy']:.2f}%")
    
    if metrics['accuracy'] >= 75.0:
        decision = "GO"
        print(f"\n🟢 DECISION: {decision}")
        print("✅ Target met - Multi-class detection validated")
    else:
        decision = "CONDITIONAL"
        print(f"\n🟡 DECISION: {decision}")
        print(f"⚠️  Below target - Gap: {75.0 - metrics['accuracy']:.2f} percentage points")
        print("Note: Proceed with caution, note limitations for dataset expansion")
    
    # Save results
    results_dir.mkdir(exist_ok=True)
    
    # Convert category_stats for JSON serialization
    category_performance = {}
    for category, stats in metrics['category_stats'].items():
        category_performance[category] = {
            'total': stats['total'],
            'correct': stats['correct'],
            'accuracy': (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        }
    
    output = {
        'task': 'Multi-Class Attack Detection Validation (Track 2)',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'decision': decision,
        'target': 75.0,
        'metrics': {
            'overall_accuracy': metrics['accuracy'],
            'category_performance': category_performance
        },
        'counts': {
            'total_samples': metrics['total_samples'],
            'correct': metrics['correct'],
            'incorrect': metrics['incorrect']
        },
        'timing': {
            'total_time': metrics['total_time'],
            'avg_per_sample': metrics['total_time'] / metrics['total_samples'],
            'model_load_time': model_load_time
        },
        'results': metrics['results']
    }
    
    with open(results_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    print("="*70)
    
    return decision, metrics


if __name__ == "__main__":
    main()

