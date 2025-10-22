#!/usr/bin/env python3
"""
GLADIATOR Blue Team Model Validation
Validate trained model on full validation set - GO/NO-GO gate (≥95% required)
"""

import json
import time
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
from mlx_lm import load, generate

def load_validation_data(filepath):
    """Load validation data from JSONL"""
    samples = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.strip():
                samples.append(json.loads(line.strip()))
    return samples

def extract_ground_truth(sample):
    """Extract ground truth label from sample"""
    response = sample['messages'][1]['content'].lower()
    
    # Priority order for classification
    if 'benign' in response:
        return 'benign'
    elif 'sql' in response and 'injection' in response:
        return 'sql_injection'
    elif 'xss' in response or 'cross-site' in response:
        return 'xss'
    elif 'phish' in response:
        return 'phishing'
    elif 'command' in response and 'injection' in response:
        return 'command_injection'
    elif 'privilege' in response or 'escalat' in response:
        return 'privilege_escalation'
    elif 'buffer' in response or 'overflow' in response:
        return 'buffer_overflow'
    elif 'dos' in response or 'denial' in response:
        return 'dos'
    elif 'mitm' in response or 'man-in-the-middle' in response:
        return 'mitm'
    else:
        return 'unknown'

def extract_prediction(response_text):
    """Extract prediction from model response"""
    response_lower = response_text.lower()
    
    # Priority order matching ground truth extraction
    if 'benign' in response_lower and 'not' not in response_lower[:50]:
        return 'benign'
    elif 'sql' in response_lower and 'injection' in response_lower:
        return 'sql_injection'
    elif 'xss' in response_lower or 'cross-site' in response_lower:
        return 'xss'
    elif 'phish' in response_lower:
        return 'phishing'
    elif 'command' in response_lower and 'injection' in response_lower:
        return 'command_injection'
    elif 'privilege' in response_lower or 'escalat' in response_lower:
        return 'privilege_escalation'
    elif 'buffer' in response_lower or 'overflow' in response_lower:
        return 'buffer_overflow'
    elif 'dos' in response_lower or 'denial' in response_lower:
        return 'dos'
    elif 'mitm' in response_lower or 'man-in-the-middle' in response_lower:
        return 'mitm'
    elif 'attack' in response_lower:
        return 'unknown_attack'
    else:
        return 'unknown'

def calculate_metrics(results):
    """Calculate precision, recall, F1 for each category"""
    categories = set()
    for r in results:
        categories.add(r['ground_truth'])
        categories.add(r['predicted'])
    
    metrics = {}
    
    for category in categories:
        tp = sum(1 for r in results if r['ground_truth'] == category and r['predicted'] == category)
        fp = sum(1 for r in results if r['ground_truth'] != category and r['predicted'] == category)
        fn = sum(1 for r in results if r['ground_truth'] == category and r['predicted'] != category)
        tn = sum(1 for r in results if r['ground_truth'] != category and r['predicted'] != category)
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        metrics[category] = {
            'tp': tp,
            'fp': fp,
            'fn': fn,
            'tn': tn,
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
    
    return metrics

def run_blue_team_validation(model, tokenizer, samples, output_dir):
    """
    Run Blue Team validation on full validation set
    Returns validation results and GO/NO-GO decision
    """
    results = []
    correct = 0
    total = len(samples)
    
    # Category tracking
    category_correct = defaultdict(int)
    category_total = defaultdict(int)
    
    print(f"\nValidating {total} samples...")
    print("=" * 80)
    
    start_time = time.time()
    
    for i, sample in enumerate(samples):
        # Get prompt (user message)
        prompt = sample['messages'][0]['content']
        
        # Get ground truth
        ground_truth = extract_ground_truth(sample)
        
        # Generate prediction
        try:
            response = generate(
                model,
                tokenizer,
                prompt=prompt,
                max_tokens=500,
                temp=0.7,
                verbose=False
            )
        except Exception as e:
            response = ""
            print(f"Error on sample {i}: {e}")
        
        # Extract prediction
        predicted = extract_prediction(response)
        
        # Check correctness
        is_correct = (predicted == ground_truth)
        
        if is_correct:
            correct += 1
            category_correct[ground_truth] += 1
        
        category_total[ground_truth] += 1
        
        # Store result
        results.append({
            'id': sample.get('id', i),
            'prompt': prompt[:200],  # Truncate for storage
            'response': response[:500],
            'ground_truth': ground_truth,
            'predicted': predicted,
            'correct': is_correct
        })
        
        # Progress update every 50 samples
        if (i + 1) % 50 == 0:
            current_accuracy = (correct / (i + 1)) * 100
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed
            eta = (total - (i + 1)) / rate if rate > 0 else 0
            
            print(f"Progress: {i+1}/{total} ({(i+1)/total*100:.1f}%) | "
                  f"Accuracy: {current_accuracy:.2f}% | "
                  f"Rate: {rate:.1f} samples/sec | "
                  f"ETA: {eta/60:.1f} min")
    
    elapsed_time = time.time() - start_time
    
    print("=" * 80)
    print(f"Validation complete in {elapsed_time:.1f} seconds")
    print()
    
    # Calculate overall metrics
    overall_accuracy = (correct / total) * 100
    
    print("OVERALL RESULTS:")
    print(f"  Total samples: {total}")
    print(f"  Correct: {correct}")
    print(f"  Incorrect: {total - correct}")
    print(f"  Accuracy: {overall_accuracy:.2f}%")
    print()
    
    # Per-category accuracy
    print("PER-CATEGORY ACCURACY:")
    print("-" * 80)
    
    category_results = []
    for category in sorted(category_total.keys()):
        cat_total = category_total[category]
        cat_correct = category_correct[category]
        cat_accuracy = (cat_correct / cat_total) * 100 if cat_total > 0 else 0
        
        status = "✅" if cat_accuracy >= 90 else "⚠️" if cat_accuracy >= 75 else "❌"
        
        print(f"{status} {category:25s}: {cat_correct:4d}/{cat_total:4d} ({cat_accuracy:6.2f}%)")
        
        category_results.append({
            'category': category,
            'correct': cat_correct,
            'total': cat_total,
            'accuracy': round(cat_accuracy, 2)
        })
    
    print()
    
    # Calculate precision/recall/F1
    detailed_metrics = calculate_metrics(results)
    
    print("DETAILED METRICS:")
    print("-" * 80)
    print(f"{'Category':25s} {'Precision':>10s} {'Recall':>10s} {'F1':>10s}")
    print("-" * 80)
    
    overall_precision = []
    overall_recall = []
    overall_f1 = []
    
    for category in sorted(detailed_metrics.keys()):
        metrics = detailed_metrics[category]
        print(f"{category:25s} {metrics['precision']*100:9.2f}% {metrics['recall']*100:9.2f}% {metrics['f1']*100:9.2f}%")
        
        if category != 'unknown':  # Exclude unknown from overall averages
            overall_precision.append(metrics['precision'])
            overall_recall.append(metrics['recall'])
            overall_f1.append(metrics['f1'])
    
    avg_precision = (sum(overall_precision) / len(overall_precision)) * 100 if overall_precision else 0
    avg_recall = (sum(overall_recall) / len(overall_recall)) * 100 if overall_recall else 0
    avg_f1 = (sum(overall_f1) / len(overall_f1)) * 100 if overall_f1 else 0
    
    print("-" * 80)
    print(f"{'AVERAGE':25s} {avg_precision:9.2f}% {avg_recall:9.2f}% {avg_f1:9.2f}%")
    print()
    
    # GO/NO-GO Decision
    print("=" * 80)
    print("GO/NO-GO DECISION")
    print("=" * 80)
    
    go_conditions = {
        'overall_accuracy_95': overall_accuracy >= 95.0,
        'all_categories_90': all(acc >= 90.0 for acc in [cr['accuracy'] for cr in category_results if cr['category'] != 'unknown']),
        'precision_92': avg_precision >= 92.0,
        'recall_92': avg_recall >= 92.0,
        'f1_92': avg_f1 >= 92.0
    }
    
    print("\nGO Criteria:")
    print(f"  {'✅' if go_conditions['overall_accuracy_95'] else '❌'} Overall accuracy ≥95%: {overall_accuracy:.2f}%")
    print(f"  {'✅' if go_conditions['all_categories_90'] else '❌'} All categories ≥90%: {all(go_conditions.values())}")
    print(f"  {'✅' if go_conditions['precision_92'] else '❌'} Precision ≥92%: {avg_precision:.2f}%")
    print(f"  {'✅' if go_conditions['recall_92'] else '❌'} Recall ≥92%: {avg_recall:.2f}%")
    print(f"  {'✅' if go_conditions['f1_92'] else '❌'} F1 ≥92%: {avg_f1:.2f}%")
    
    all_pass = all(go_conditions.values())
    
    print()
    if all_pass:
        decision = "GO"
        print("🟢 DECISION: GO - Model meets all criteria")
        print("   ✅ Proceed to Week 4 (Red Team Training)")
    else:
        decision = "NO-GO"
        print("🔴 DECISION: NO-GO - Model does not meet criteria")
        print("   ❌ Review failed conditions and consider:")
        print("      - Additional training iterations")
        print("      - Dataset rebalancing")
        print("      - Learning rate adjustment")
    
    print()
    
    # Save results
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    results_data = {
        "validation_date": datetime.now().isoformat(),
        "model": "GLADIATOR-SEC-8B-EXPERT-v1.0",
        "total_samples": total,
        "correct_predictions": correct,
        "incorrect_predictions": total - correct,
        "accuracy_percent": round(overall_accuracy, 2),
        "decision": decision,
        "go_criteria": go_conditions,
        "metrics": {
            "overall_accuracy": round(overall_accuracy, 2),
            "precision": round(avg_precision, 2),
            "recall": round(avg_recall, 2),
            "f1": round(avg_f1, 2)
        },
        "category_accuracy": category_results,
        "detailed_metrics": {k: {mk: round(mv, 4) if isinstance(mv, float) else mv 
                                 for mk, mv in v.items()} 
                            for k, v in detailed_metrics.items()},
        "validation_time_seconds": round(elapsed_time, 1),
        "results": results
    }
    
    results_file = output_path / "blue_team_validation_results.json"
    with open(results_file, 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"Results saved to: {results_file}")
    print()
    
    return results_data

if __name__ == "__main__":
    import sys
    
    print("=" * 80)
    print("GLADIATOR Blue Team Model Validation")
    print("=" * 80)
    print()
    
    # Paths
    model_path = "/Users/arthurdell/GLADIATOR/models/DavidBianco/Foundation-Sec-8B-Instruct-int8"
    adapter_path = "/Users/arthurdell/GLADIATOR/checkpoints/blue_team_8b"
    data_path = "/Users/arthurdell/GLADIATOR/datasets/blue_team_training/valid.jsonl"
    output_dir = "/Users/arthurdell/GLADIATOR/results"
    
    # Check if files exist
    if not Path(model_path).exists():
        print(f"❌ ERROR: Model not found at {model_path}")
        sys.exit(1)
    
    if not Path(adapter_path).exists():
        print(f"❌ ERROR: Adapter not found at {adapter_path}")
        print("   Train the model first using launch_blue_team_training.sh")
        sys.exit(1)
    
    if not Path(data_path).exists():
        print(f"❌ ERROR: Validation data not found at {data_path}")
        sys.exit(1)
    
    print("Loading model and adapter...")
    try:
        model, tokenizer = load(model_path, adapter_path=adapter_path)
        print("✅ Model loaded successfully")
        print()
    except Exception as e:
        print(f"❌ ERROR loading model: {e}")
        sys.exit(1)
    
    print("Loading validation data...")
    samples = load_validation_data(data_path)
    print(f"✅ Loaded {len(samples)} validation samples")
    print()
    
    # Run validation
    results = run_blue_team_validation(model, tokenizer, samples, output_dir)
    
    print("=" * 80)
    print("Validation Complete")
    print("=" * 80)
    print()
    print(f"Decision: {results['decision']}")
    print(f"Accuracy: {results['accuracy_percent']}%")
    print()

