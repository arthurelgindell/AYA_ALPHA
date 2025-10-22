#!/usr/bin/env python3
"""
GLADIATOR Sample Quality Validation
Validate sample quality before training
"""

import json
import sys
from pathlib import Path
from collections import Counter
from datetime import datetime

def validate_format(sample, sample_id):
    """Validate sample format"""
    errors = []
    
    # Check required fields
    if 'id' not in sample:
        errors.append("Missing 'id' field")
    
    if 'messages' not in sample:
        errors.append("Missing 'messages' field")
        return errors  # Can't continue without messages
    
    if not isinstance(sample['messages'], list):
        errors.append("'messages' must be a list")
        return errors
    
    if len(sample['messages']) != 2:
        errors.append(f"'messages' must have 2 entries, got {len(sample['messages'])}")
        return errors
    
    # Validate user message
    user_msg = sample['messages'][0]
    if 'role' not in user_msg or user_msg['role'] != 'user':
        errors.append("First message must have role='user'")
    
    if 'content' not in user_msg or not user_msg['content']:
        errors.append("User message content is empty")
    
    # Validate assistant message
    assistant_msg = sample['messages'][1]
    if 'role' not in assistant_msg or assistant_msg['role'] != 'assistant':
        errors.append("Second message must have role='assistant'")
    
    if 'content' not in assistant_msg or not assistant_msg['content']:
        errors.append("Assistant message content is empty")
    
    return errors

def validate_content(sample):
    """Validate sample content quality"""
    errors = []
    warnings = []
    
    user_content = sample['messages'][0]['content']
    assistant_content = sample['messages'][1]['content']
    
    # Check lengths
    if len(user_content) < 20:
        warnings.append(f"User content very short ({len(user_content)} chars)")
    
    if len(user_content) > 5000:
        errors.append(f"User content too long ({len(user_content)} chars)")
    
    if len(assistant_content) < 10:
        errors.append(f"Assistant content too short ({len(assistant_content)} chars)")
    
    if len(assistant_content) > 3000:
        warnings.append(f"Assistant content very long ({len(assistant_content)} chars)")
    
    # Check for code/content in user message
    if 'code' not in user_content.lower() and 'analyze' not in user_content.lower():
        warnings.append("User prompt may not contain code to analyze")
    
    # Check for classification in assistant response
    assistant_lower = assistant_content.lower()
    has_classification = any(word in assistant_lower for word in [
        'benign', 'attack', 'sql', 'xss', 'phishing', 'command', 'privilege',
        'buffer', 'dos', 'mitm', 'injection', 'escalation', 'overflow'
    ])
    
    if not has_classification:
        errors.append("Assistant response doesn't contain attack classification")
    
    return errors, warnings

def extract_category(sample):
    """Extract category from sample"""
    response = sample['messages'][1]['content'].lower()
    
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

def validate_distribution(samples):
    """Check category distribution balance"""
    categories = Counter([extract_category(s) for s in samples])
    
    total = len(samples)
    issues = []
    
    # Check for extreme imbalance
    for category, count in categories.items():
        percentage = (count / total) * 100
        
        if percentage > 20:
            issues.append(f"Category '{category}' over-represented: {percentage:.1f}% (max 20%)")
        
        if percentage < 5 and category != 'unknown':
            issues.append(f"Category '{category}' under-represented: {percentage:.1f}% (min 5%)")
    
    # Check attack vs benign ratio
    benign_count = categories.get('benign', 0)
    attack_count = total - benign_count
    
    benign_pct = (benign_count / total) * 100 if total > 0 else 0
    attack_pct = (attack_count / total) * 100 if total > 0 else 0
    
    if abs(benign_pct - 50) > 10:
        issues.append(f"Attack/Benign imbalance: {attack_pct:.1f}% attack, {benign_pct:.1f}% benign (target: 50/50)")
    
    return categories, issues

def quality_check(input_files, output_file=None):
    """
    Run quality check on dataset files
    """
    print("=" * 80)
    print("GLADIATOR Sample Quality Validation")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load samples
    all_samples = []
    for filepath in input_files:
        path = Path(filepath)
        if not path.exists():
            print(f"⚠️  File not found: {filepath}")
            continue
        
        print(f"Loading: {path.name}")
        with open(path, 'r') as f:
            samples = []
            for i, line in enumerate(f):
                if line.strip():
                    try:
                        sample = json.loads(line.strip())
                        samples.append(sample)
                    except json.JSONDecodeError as e:
                        print(f"  ❌ JSON error on line {i+1}: {e}")
            
            print(f"  Loaded {len(samples)} samples")
            all_samples.extend(samples)
    
    if not all_samples:
        print("❌ No samples loaded")
        return False
    
    print(f"\nTotal samples: {len(all_samples)}")
    print()
    
    # Format validation
    print("Running format validation...")
    format_errors = []
    format_warnings = []
    
    for i, sample in enumerate(all_samples):
        errors = validate_format(sample, i)
        if errors:
            format_errors.append((i, errors))
            if len(format_errors) <= 10:  # Only print first 10
                print(f"  Sample {i}: {', '.join(errors)}")
    
    if format_errors:
        print(f"\n❌ Format validation failed: {len(format_errors)} samples with errors")
    else:
        print(f"✅ Format validation passed: {len(all_samples)} samples")
    
    print()
    
    # Content validation
    print("Running content validation...")
    content_errors = []
    content_warnings = []
    
    for i, sample in enumerate(all_samples):
        errors, warnings = validate_content(sample)
        if errors:
            content_errors.append((i, errors))
            if len(content_errors) <= 10:
                print(f"  Sample {i} errors: {', '.join(errors)}")
        if warnings:
            content_warnings.append((i, warnings))
    
    if content_errors:
        print(f"\n⚠️  Content validation: {len(content_errors)} samples with errors")
    else:
        print(f"✅ Content validation passed: {len(all_samples)} samples")
    
    if content_warnings:
        print(f"ℹ️  Content warnings: {len(content_warnings)} samples with warnings")
    
    print()
    
    # Distribution validation
    print("Analyzing distribution...")
    categories, distribution_issues = validate_distribution(all_samples)
    
    print("\nCategory Distribution:")
    for category, count in categories.most_common():
        percentage = (count / len(all_samples)) * 100
        print(f"  {category:25s}: {count:5d} ({percentage:5.2f}%)")
    
    print()
    
    if distribution_issues:
        print("Distribution Issues:")
        for issue in distribution_issues:
            print(f"  ⚠️  {issue}")
    else:
        print("✅ Distribution balanced")
    
    print()
    
    # Duplicate check
    print("Checking for duplicates...")
    ids = [s.get('id') for s in all_samples if 'id' in s]
    duplicate_ids = [id for id, count in Counter(ids).items() if count > 1]
    
    if duplicate_ids:
        print(f"⚠️  Found {len(duplicate_ids)} duplicate IDs")
        if len(duplicate_ids) <= 10:
            print(f"  Duplicates: {duplicate_ids}")
    else:
        print(f"✅ No duplicate IDs found")
    
    print()
    
    # Summary
    print("=" * 80)
    print("QUALITY CHECK SUMMARY")
    print("=" * 80)
    
    total_errors = len(format_errors) + len(content_errors)
    total_warnings = len(content_warnings) + len(distribution_issues)
    
    print(f"Total samples checked: {len(all_samples)}")
    print(f"Format errors: {len(format_errors)}")
    print(f"Content errors: {len(content_errors)}")
    print(f"Warnings: {total_warnings}")
    print(f"Duplicate IDs: {len(duplicate_ids)}")
    print()
    
    # Overall decision
    if total_errors == 0 and len(duplicate_ids) == 0:
        decision = "PASS"
        print("✅ DECISION: PASS - Dataset ready for training")
    elif total_errors < len(all_samples) * 0.05:  # Less than 5% error rate
        decision = "PASS_WITH_WARNINGS"
        print(f"⚠️  DECISION: PASS WITH WARNINGS - {total_errors} errors (<5%)")
        print("   Review and consider fixing errors before training")
    else:
        decision = "FAIL"
        print(f"❌ DECISION: FAIL - {total_errors} errors (≥5%)")
        print("   Fix errors before training")
    
    print()
    
    # Save report
    if output_file:
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_samples": len(all_samples),
            "format_errors": len(format_errors),
            "content_errors": len(content_errors),
            "warnings": total_warnings,
            "duplicate_ids": len(duplicate_ids),
            "decision": decision,
            "category_distribution": dict(categories),
            "distribution_issues": distribution_issues,
            "error_details": {
                "format": [(i, e) for i, e in format_errors[:100]],  # First 100
                "content": [(i, e) for i, e in content_errors[:100]]
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Report saved to: {output_file}")
        print()
    
    return decision in ["PASS", "PASS_WITH_WARNINGS"]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: quality_check.py <input_file1> [input_file2] ...")
        print("Example: quality_check.py datasets/expansion/*.jsonl")
        sys.exit(1)
    
    input_files = sys.argv[1:]
    output_file = "quality_check_report.json"
    
    success = quality_check(input_files, output_file)
    
    sys.exit(0 if success else 1)

