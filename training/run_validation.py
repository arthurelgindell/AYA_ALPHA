#!/usr/bin/env python3
"""
GLADIATOR Reality Check Validation - Task 10
Tests fine-tuned model on 100 held-out validation samples
GO/NO-GO GATE: Must achieve ≥90% detection accuracy
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Tuple
from mlx_lm import load, generate

# Paths
MODEL_PATH = "/Users/arthurdell/GLADIATOR/models/DavidBianco/Foundation-Sec-8B-Instruct-int8"
ADAPTER_PATH = "/Users/arthurdell/GLADIATOR/checkpoints/reality_check"
VAL_FILE = "/Users/arthurdell/GLADIATOR/datasets/reality_check_val_100.jsonl"
RESULTS_DIR = Path("/Users/arthurdell/GLADIATOR/results")
RESULTS_FILE = RESULTS_DIR / "reality_check_results.json"

# Attack type keywords for detection
ATTACK_KEYWORDS = {
    'sql_injection': ['sql', 'injection', 'select', 'union', 'drop', 'insert', 'update', 'database'],
    'xss': ['xss', 'cross-site', 'script', 'javascript', 'alert', 'onerror', 'onclick'],
    'phishing': ['phishing', 'phish', 'credential', 'fake', 'impersonat', 'social engineering'],
    'buffer_overflow': ['buffer', 'overflow', 'memory', 'segmentation', 'stack', 'heap'],
    'port_scan': ['port', 'scan', 'nmap', 'reconnaissance', 'probe', 'enumeration'],
    'command_injection': ['command', 'injection', 'exec', 'shell', 'system', 'os'],
    'path_traversal': ['path', 'traversal', 'directory', '../', '..\\', 'file inclusion'],
    'brute_force': ['brute', 'force', 'password', 'crack', 'dictionary', 'guess'],
    'ddos': ['ddos', 'denial', 'service', 'flood', 'amplification', 'botnet']
}


def load_validation_data(file_path: str) -> List[Dict]:
    """Load validation dataset from JSONL file."""
    samples = []
    with open(file_path, 'r') as f:
        for line in f:
            samples.append(json.loads(line.strip()))
    return samples


def detect_attack_type(text: str) -> str:
    """Detect attack type from model response using keyword matching."""
    text_lower = text.lower()

    # Count keyword matches for each attack type
    matches = {}
    for attack_type, keywords in ATTACK_KEYWORDS.items():
        match_count = sum(1 for keyword in keywords if keyword in text_lower)
        if match_count > 0:
            matches[attack_type] = match_count

    # Return attack type with most keyword matches
    if matches:
        return max(matches, key=matches.get)
    return 'unknown'


def normalize_attack_type(attack_type: str) -> str:
    """Normalize attack type names for comparison."""
    return attack_type.lower().replace(' ', '_').replace('-', '_')


def run_validation(model, tokenizer, samples: List[Dict]) -> Tuple[List[Dict], float]:
    """Run validation on all samples and calculate accuracy."""
    results = []
    correct = 0
    total = len(samples)

    print(f"\nStarting validation on {total} samples...")
    print("=" * 80)

    start_time = time.time()

    for i, sample in enumerate(samples, 1):
        # Extract ground truth
        sample_data = sample.get('messages', [{}])[0].get('content', '')
        ground_truth_type = None

        # Parse ground truth from sample
        if 'Attack Type:' in sample_data:
            gt_line = [line for line in sample_data.split('\n') if 'Attack Type:' in line][0]
            ground_truth_type = gt_line.split('Attack Type:')[1].strip()

        # Generate prediction prompt
        attack_code = None
        if 'Attack Code:' in sample_data:
            code_section = sample_data.split('Attack Code:')[1].split('Task:')[0].strip()
            attack_code = code_section

        if not attack_code:
            # Extract from code field if available
            messages = sample.get('messages', [])
            if messages and 'content' in messages[0]:
                attack_code = messages[0]['content']

        prompt = f"""Analyze this security threat and identify the attack type:

{attack_code}

What type of cyber attack is this? Respond with the attack type."""

        # Generate model prediction
        try:
            response = generate(
                model,
                tokenizer,
                prompt=prompt,
                max_tokens=100,
                verbose=False
            )

            # Detect attack type from response
            predicted_type = detect_attack_type(response)

            # Normalize for comparison
            gt_normalized = normalize_attack_type(ground_truth_type) if ground_truth_type else 'unknown'
            pred_normalized = normalize_attack_type(predicted_type)

            # Check if correct
            is_correct = gt_normalized == pred_normalized
            if is_correct:
                correct += 1

            # Store result
            result = {
                'sample_id': i,
                'ground_truth': ground_truth_type,
                'predicted': predicted_type,
                'correct': is_correct,
                'response': response[:200]  # First 200 chars
            }
            results.append(result)

            # Progress update every 10 samples
            if i % 10 == 0:
                current_accuracy = (correct / i) * 100
                elapsed = time.time() - start_time
                print(f"Progress: {i}/{total} samples | Accuracy: {current_accuracy:.2f}% | Elapsed: {elapsed:.1f}s")

        except Exception as e:
            print(f"ERROR on sample {i}: {e}")
            results.append({
                'sample_id': i,
                'ground_truth': ground_truth_type,
                'predicted': 'error',
                'correct': False,
                'error': str(e)
            })

    # Calculate final accuracy
    accuracy = (correct / total) * 100
    total_time = time.time() - start_time

    print("=" * 80)
    print(f"\n✅ VALIDATION COMPLETE")
    print(f"Samples Tested: {total}")
    print(f"Correct Predictions: {correct}")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"Total Time: {total_time:.1f}s")
    print(f"Avg Time per Sample: {total_time/total:.2f}s")

    return results, accuracy


def save_results(results: List[Dict], accuracy: float, go_decision: str):
    """Save validation results to JSON file."""
    RESULTS_DIR.mkdir(exist_ok=True)

    output = {
        'task': 'Task 10: Reality Check Validation',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_samples': len(results),
        'correct_predictions': sum(1 for r in results if r['correct']),
        'accuracy_percent': round(accuracy, 2),
        'go_no_go_decision': go_decision,
        'threshold': 90.0,
        'results': results
    }

    with open(RESULTS_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n📄 Results saved to: {RESULTS_FILE}")
    return output


def main():
    """Main validation routine."""
    print("=" * 80)
    print("GLADIATOR REALITY CHECK VALIDATION - TASK 10")
    print("=" * 80)
    print("\nCRITICAL GO/NO-GO GATE: Must achieve ≥90% accuracy\n")

    # Load model
    print("Loading fine-tuned model with adapters...")
    model_start = time.time()
    model, tokenizer = load(MODEL_PATH, adapter_path=ADAPTER_PATH)
    model_load_time = time.time() - model_start
    print(f"✅ Model loaded in {model_load_time:.3f}s\n")

    # Load validation data
    print("Loading validation dataset...")
    samples = load_validation_data(VAL_FILE)
    print(f"✅ Loaded {len(samples)} validation samples\n")

    # Run validation
    results, accuracy = run_validation(model, tokenizer, samples)

    # Make GO/NO-GO decision
    print("\n" + "=" * 80)
    print("GO/NO-GO DECISION")
    print("=" * 80)
    print(f"\nAccuracy Threshold: ≥90.0%")
    print(f"Achieved Accuracy: {accuracy:.2f}%")

    if accuracy >= 90.0:
        go_decision = "GO"
        print(f"\n🟢 DECISION: {go_decision}")
        print("✅ Threshold met - Proceed to Week 1 (Data Preparation & Network)")
    else:
        go_decision = "NO-GO"
        print(f"\n🔴 DECISION: {go_decision}")
        print("❌ Threshold NOT met - STOP Phase 0, investigate, retest")

    # Save results
    output = save_results(results, accuracy, go_decision)

    print("\n" + "=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)

    return output


if __name__ == "__main__":
    main()
