#!/usr/bin/env python3
"""
GLADIATOR Reality Check Validation - Task 10 (FINAL - CORRECTED)
Tests fine-tuned model on 100 held-out validation samples
GO/NO-GO GATE: Must achieve ≥90% detection accuracy

CORRECTED: Uses apply_chat_template() for proper model inference
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
RESULTS_FILE = RESULTS_DIR / "reality_check_results_FINAL.json"

# Attack type patterns for detection
ATTACK_PATTERNS = {
    'sql_injection': ['sql', 'injection', 'query', 'database', 'union', 'select', 'drop', 'insert'],
    'xss': ['xss', 'cross-site', 'script', 'javascript', 'payload', 'alert'],
    'phishing': ['phish', 'credential', 'fake', 'social engineering', 'impersonat'],
    'command_injection': ['command', 'injection', 'exec', 'shell', 'system'],
    'path_traversal': ['path', 'traversal', 'directory', 'file'],
    'buffer_overflow': ['buffer', 'overflow', 'memory', 'exploit'],
    'privilege_escalation': ['privilege', 'escalat', 'elevat', 'admin', 'root'],
    'dos': ['denial', 'service', 'dos', 'ddos', 'flood'],
    'mitm': ['man-in-the-middle', 'mitm', 'intercept', 'eavesdrop'],
    'malware': ['malware', 'virus', 'trojan', 'backdoor', 'ransomware']
}


def detect_attack_from_template(template: str) -> str:
    """Detect attack type from template text using pattern matching."""
    template_lower = template.lower()

    scores = {}
    for attack_type, keywords in ATTACK_PATTERNS.items():
        score = sum(1 for keyword in keywords if keyword in template_lower)
        if score > 0:
            scores[attack_type] = score

    if scores:
        return max(scores, key=scores.get)
    return 'unknown'


def detect_attack_from_response(response: str) -> str:
    """Detect attack type from model response using pattern matching."""
    response_lower = response.lower()

    scores = {}
    for attack_type, keywords in ATTACK_PATTERNS.items():
        score = sum(1 for keyword in keywords if keyword in response_lower)
        if score > 0:
            scores[attack_type] = score

    if scores:
        return max(scores, key=scores.get)
    return 'unknown'


def load_validation_data(file_path: str) -> List[Dict]:
    """Load validation dataset from JSONL file."""
    samples = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip():
                samples.append(json.loads(line.strip()))
    return samples


def run_validation(model, tokenizer, samples: List[Dict]) -> Tuple[List[Dict], float]:
    """Run validation on all samples and calculate accuracy."""
    results = []
    correct = 0
    total = len(samples)

    print(f"\nStarting validation on {total} samples...")
    print("Using chat template for proper model inference")
    print("=" * 80)

    start_time = time.time()

    for i, sample in enumerate(samples, 1):
        # Extract ground truth from template
        template = sample.get('template', '')
        attack_code = sample.get('attack_code', '')
        ground_truth_type = detect_attack_from_template(template)

        # Create chat message (CORRECTED: Use chat template format)
        messages = [{
            "role": "user",
            "content": f"You are a cybersecurity analyst. Analyze this attack code and identify the attack type:\n\n{attack_code[:500]}\n\nWhat type of cyber attack is this? Provide a brief analysis."
        }]

        # Generate model prediction using chat template (CRITICAL FIX)
        try:
            # Apply chat template to format prompt correctly
            prompt = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )

            response = generate(
                model,
                tokenizer,
                prompt=prompt,
                max_tokens=150,
                verbose=False
            )

            # Detect attack type from response
            predicted_type = detect_attack_from_response(response)

            # Check if correct
            is_correct = (ground_truth_type == predicted_type)
            if is_correct:
                correct += 1

            # Store result
            result = {
                'sample_id': i,
                'template': template[:100] + '...' if len(template) > 100 else template,
                'ground_truth': ground_truth_type,
                'predicted': predicted_type,
                'correct': is_correct,
                'response': response[:300] + '...' if len(response) > 300 else response,
                'response_length': len(response)
            }
            results.append(result)

            # Progress update every 10 samples
            if i % 10 == 0:
                current_accuracy = (correct / i) * 100
                elapsed = time.time() - start_time
                print(f"Progress: {i}/{total} | Correct: {correct}/{i} | Accuracy: {current_accuracy:.2f}% | Time: {elapsed:.1f}s")

        except Exception as e:
            print(f"ERROR on sample {i}: {e}")
            results.append({
                'sample_id': i,
                'template': template[:100] + '...' if len(template) > 100 else template,
                'ground_truth': ground_truth_type,
                'predicted': 'error',
                'correct': False,
                'error': str(e),
                'response_length': 0
            })

    # Calculate final accuracy
    accuracy = (correct / total) * 100
    total_time = time.time() - start_time

    print("=" * 80)
    print(f"\n✅ VALIDATION COMPLETE")
    print(f"Samples Tested: {total}")
    print(f"Correct Predictions: {correct}")
    print(f"Incorrect Predictions: {total - correct}")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"Total Time: {total_time:.1f}s")
    print(f"Avg Time per Sample: {total_time/total:.2f}s")

    return results, accuracy


def analyze_failures(results: List[Dict]):
    """Analyze failure patterns."""
    failures = [r for r in results if not r['correct']]

    if not failures:
        print("\n✅ NO FAILURES - Perfect accuracy!")
        return

    print(f"\n❌ FAILURE ANALYSIS ({len(failures)} failures)")
    print("=" * 80)

    # Count empty responses
    empty_responses = [f for f in failures if f.get('response_length', 0) == 0]
    print(f"Empty responses: {len(empty_responses)}")

    # Group failures by ground truth type
    failure_by_type = {}
    for failure in failures:
        gt_type = failure['ground_truth']
        if gt_type not in failure_by_type:
            failure_by_type[gt_type] = []
        failure_by_type[gt_type].append(failure)

    for attack_type, type_failures in failure_by_type.items():
        print(f"\n{attack_type.upper()}: {len(type_failures)} failures")
        for failure in type_failures[:2]:  # Show first 2 examples
            pred = failure.get('predicted', 'error')
            resp_len = failure.get('response_length', 0)
            print(f"  Sample {failure['sample_id']}: Predicted as '{pred}' (response: {resp_len} chars)")


def save_results(results: List[Dict], accuracy: float, go_decision: str):
    """Save validation results to JSON file."""
    RESULTS_DIR.mkdir(exist_ok=True)

    correct_count = sum(1 for r in results if r['correct'])

    output = {
        'task': 'Task 10: Reality Check Validation (FINAL - Chat Template Corrected)',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_samples': len(results),
        'correct_predictions': correct_count,
        'incorrect_predictions': len(results) - correct_count,
        'accuracy_percent': round(accuracy, 2),
        'go_no_go_decision': go_decision,
        'threshold': 90.0,
        'validation_method': 'Chat template with apply_chat_template()',
        'results': results
    }

    with open(RESULTS_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n📄 Results saved to: {RESULTS_FILE}")
    return output


def main():
    """Main validation routine."""
    print("=" * 80)
    print("GLADIATOR REALITY CHECK VALIDATION - TASK 10 (FINAL)")
    print("=" * 80)
    print("\nCRITICAL GO/NO-GO GATE: Must achieve ≥90% accuracy")
    print("CORRECTED: Using apply_chat_template() for proper inference\n")

    # Load model
    print("Loading fine-tuned model with adapters...")
    model_start = time.time()
    model, tokenizer = load(MODEL_PATH, adapter_path=ADAPTER_PATH)
    model_load_time = time.time() - model_start
    print(f"✅ Model loaded in {model_load_time:.3f}s")

    # Verify tokenizer has chat template
    if not hasattr(tokenizer, 'apply_chat_template'):
        print("⚠️  WARNING: Tokenizer does not have apply_chat_template method")
    else:
        print("✅ Chat template available\n")

    # Load validation data
    print("Loading validation dataset...")
    samples = load_validation_data(VAL_FILE)
    print(f"✅ Loaded {len(samples)} validation samples\n")

    # Run validation
    results, accuracy = run_validation(model, tokenizer, samples)

    # Analyze failures
    analyze_failures(results)

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
        print("❌ Threshold NOT met - STOP Phase 0, investigate further")

    # Save results
    output = save_results(results, accuracy, go_decision)

    print("\n" + "=" * 80)
    print("VALIDATION COMPLETE - PRIME DIRECTIVE COMPLIANT")
    print("=" * 80)

    return output


if __name__ == "__main__":
    main()
