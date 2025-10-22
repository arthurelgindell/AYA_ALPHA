#!/usr/bin/env python3
"""
GLADIATOR Binary Classification Validation
Test fine-tuned model on validation set - GO/NO-GO gate (≥90% required)
"""

import json
import time
from pathlib import Path
from mlx_lm import load, generate

def load_validation_data(filepath):
    """Load validation data from JSONL"""
    samples = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.strip():
                samples.append(json.loads(line.strip()))
    return samples


def run_binary_validation(model, tokenizer, samples):
    """
    Run binary classification validation
    Returns accuracy, precision, recall, F1
    """
    results = []
    correct = 0
    total = len(samples)
    
    # Track for precision/recall
    true_positives = 0
    false_positives = 0
    true_negatives = 0
    false_negatives = 0
    
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
                max_tokens=10,  # Binary response should be short
                verbose=False
            )
            
            # Parse response (look for "attack" or "benign")
            response_lower = response.lower()
            if 'attack' in response_lower and 'benign' not in response_lower:
                predicted = 'attack'
            elif 'benign' in response_lower and 'attack' not in response_lower:
                predicted = 'benign'
            else:
                # Default to most common token
                predicted = 'unknown'
            
            # Check if correct
            is_correct = (predicted == ground_truth)
            if is_correct:
                correct += 1
            
            # Update confusion matrix
            if ground_truth == 'attack' and predicted == 'attack':
                true_positives += 1
            elif ground_truth == 'benign' and predicted == 'attack':
                false_positives += 1
            elif ground_truth == 'benign' and predicted == 'benign':
                true_negatives += 1
            elif ground_truth == 'attack' and predicted == 'benign':
                false_negatives += 1
            
            # Store result
            results.append({
                'sample_id': i,
                'ground_truth': ground_truth,
                'predicted': predicted,
                'correct': is_correct,
                'response': response[:200]  # First 200 chars
            })
            
            # Progress update
            if i % 20 == 0:
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
    
    # Precision: TP / (TP + FP)
    precision = (true_positives / (true_positives + false_positives) * 100) if (true_positives + false_positives) > 0 else 0
    
    # Recall: TP / (TP + FN)
    recall = (true_positives / (true_positives + false_negatives) * 100) if (true_positives + false_negatives) > 0 else 0
    
    # F1: 2 * (Precision * Recall) / (Precision + Recall)
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0
    
    total_time = time.time() - start_time
    
    # Print results
    print("="*70)
    print("\n✅ VALIDATION COMPLETE")
    print("="*70)
    print(f"Total Samples: {total}")
    print(f"Correct Predictions: {correct}")
    print(f"Incorrect Predictions: {total - correct}")
    print(f"\nACCURACY: {accuracy:.2f}%")
    print(f"Precision: {precision:.2f}%")
    print(f"Recall: {recall:.2f}%")
    print(f"F1 Score: {f1:.2f}%")
    print(f"\nConfusion Matrix:")
    print(f"  True Positives (attack→attack): {true_positives}")
    print(f"  False Positives (benign→attack): {false_positives}")
    print(f"  True Negatives (benign→benign): {true_negatives}")
    print(f"  False Negatives (attack→benign): {false_negatives}")
    print(f"\nTotal Time: {total_time:.1f}s")
    print(f"Avg Time per Sample: {total_time/total:.2f}s")
    print("="*70)
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'total_samples': total,
        'correct': correct,
        'incorrect': total - correct,
        'true_positives': true_positives,
        'false_positives': false_positives,
        'true_negatives': true_negatives,
        'false_negatives': false_negatives,
        'total_time': total_time,
        'results': results
    }


def main():
    print("="*70)
    print("GLADIATOR Binary Classification Validation")
    print("="*70)
    print("\nCRITICAL GO/NO-GO GATE: Must achieve ≥90% accuracy\n")
    
    # Paths
    model_path = "/Users/arthurdell/GLADIATOR/models/DavidBianco/Foundation-Sec-8B-Instruct-int8"
    adapter_path = "/Users/arthurdell/GLADIATOR/checkpoints/binary_classification"
    val_file = "/Users/arthurdell/GLADIATOR/training/reality_check_data/binary_val_200.jsonl"
    results_dir = Path("/Users/arthurdell/GLADIATOR/results")
    results_file = results_dir / "binary_classification_results.json"
    
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
    metrics = run_binary_validation(model, tokenizer, samples)
    
    # GO/NO-GO Decision
    print("\n" + "="*70)
    print("GO/NO-GO DECISION")
    print("="*70)
    print(f"\nAccuracy Threshold: ≥90.0%")
    print(f"Achieved Accuracy: {metrics['accuracy']:.2f}%")
    
    if metrics['accuracy'] >= 90.0:
        decision = "GO"
        print(f"\n🟢 DECISION: {decision}")
        print("✅ Threshold met - Proceed to Track 2 (multi-class detection)")
    else:
        decision = "NO-GO"
        print(f"\n🔴 DECISION: {decision}")
        print(f"❌ Threshold NOT met - Gap: {90.0 - metrics['accuracy']:.2f} percentage points")
        print("Action: Investigate and adjust before proceeding")
    
    # Save results
    results_dir.mkdir(exist_ok=True)
    output = {
        'task': 'Binary Classification Validation (Track 1)',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'decision': decision,
        'threshold': 90.0,
        'metrics': {
            'accuracy': metrics['accuracy'],
            'precision': metrics['precision'],
            'recall': metrics['recall'],
            'f1': metrics['f1']
        },
        'counts': {
            'total_samples': metrics['total_samples'],
            'correct': metrics['correct'],
            'incorrect': metrics['incorrect'],
            'true_positives': metrics['true_positives'],
            'false_positives': metrics['false_positives'],
            'true_negatives': metrics['true_negatives'],
            'false_negatives': metrics['false_negatives']
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

