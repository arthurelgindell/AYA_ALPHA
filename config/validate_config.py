#!/usr/bin/env python3
"""
Configuration Validation Script
Validates reality_check_config.json for Task 5
"""

import json
import os
import sys
import hashlib
import requests
from pathlib import Path
from typing import Dict, List, Tuple


def calculate_md5(file_path: str) -> str:
    """Calculate MD5 checksum of a file."""
    md5_hash = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def validate_json(config_path: str) -> Tuple[bool, Dict, str]:
    """Validate JSON is parseable and load config."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return True, config, "JSON valid and parseable"
    except json.JSONDecodeError as e:
        return False, {}, f"JSON parse error: {e}"
    except Exception as e:
        return False, {}, f"Error reading config: {e}"


def validate_hyperparameters(config: Dict) -> Tuple[bool, List[str]]:
    """Validate all hyperparameters match specification."""
    errors = []

    # Required hyperparameters with exact values
    required_params = {
        ('training', 'learning_rate'): 0.0001,
        ('training', 'batch_size'): 32,
        ('training', 'num_steps'): 100,
        ('training', 'warmup_steps'): 10,
        ('generation', 'temperature'): 0.7,
        ('generation', 'max_tokens'): 512,
    }

    for (section, param), expected_value in required_params.items():
        actual_value = config.get(section, {}).get(param)
        if actual_value != expected_value:
            errors.append(
                f"{section}.{param}: Expected {expected_value}, got {actual_value}"
            )

    return len(errors) == 0, errors


def validate_paths(config: Dict) -> Tuple[bool, List[str]]:
    """Validate all file paths exist and are accessible."""
    errors = []

    # Data file paths
    train_file = config.get('data', {}).get('train_file')
    val_file = config.get('data', {}).get('val_file')

    if not train_file:
        errors.append("Training file path not specified")
    elif not os.path.exists(train_file):
        errors.append(f"Training file does not exist: {train_file}")
    elif not os.access(train_file, os.R_OK):
        errors.append(f"Training file not readable: {train_file}")

    if not val_file:
        errors.append("Validation file path not specified")
    elif not os.path.exists(val_file):
        errors.append(f"Validation file does not exist: {val_file}")
    elif not os.access(val_file, os.R_OK):
        errors.append(f"Validation file not readable: {val_file}")

    # Output directories
    checkpoint_dir = config.get('output', {}).get('checkpoint_dir')
    log_dir = config.get('output', {}).get('log_dir')

    if not checkpoint_dir:
        errors.append("Checkpoint directory not specified")
    elif not os.path.exists(checkpoint_dir):
        errors.append(f"Checkpoint directory does not exist: {checkpoint_dir}")

    if not log_dir:
        errors.append("Log directory not specified")
    elif not os.path.exists(log_dir):
        errors.append(f"Log directory does not exist: {log_dir}")

    return len(errors) == 0, errors


def validate_model_endpoint(config: Dict) -> Tuple[bool, str]:
    """Test if model endpoint is accessible."""
    endpoint = config.get('model', {}).get('endpoint')

    if not endpoint:
        return False, "Model endpoint not specified"

    try:
        # Test with a simple models list request
        response = requests.get(f"{endpoint}/models", timeout=5)

        if response.status_code == 200:
            return True, f"Endpoint accessible (HTTP {response.status_code})"
        else:
            return False, f"Endpoint returned HTTP {response.status_code}"

    except requests.exceptions.ConnectionError:
        return False, f"Connection refused - LM Studio may not be running"
    except requests.exceptions.Timeout:
        return False, f"Connection timeout - endpoint not responding"
    except Exception as e:
        return False, f"Error testing endpoint: {e}"


def get_file_info(file_path: str) -> Dict:
    """Get file information."""
    stat = os.stat(file_path)
    return {
        'path': file_path,
        'size': stat.st_size,
        'size_human': f"{stat.st_size / 1024:.2f} KB",
        'md5': calculate_md5(file_path)
    }


def main():
    """Main validation routine."""
    config_path = "/Users/arthurdell/GLADIATOR/config/reality_check_config.json"

    print("=" * 80)
    print("TASK 5: FINE-TUNING CONFIGURATION VALIDATION")
    print("=" * 80)
    print()

    # File info
    print("Configuration File:")
    if os.path.exists(config_path):
        file_info = get_file_info(config_path)
        print(f"  Path: {file_info['path']}")
        print(f"  Size: {file_info['size_human']} ({file_info['size']} bytes)")
        print(f"  MD5:  {file_info['md5']}")
    else:
        print(f"  ERROR: Config file not found at {config_path}")
        sys.exit(1)
    print()

    # Validate JSON
    print("JSON Validation:")
    json_valid, config, json_msg = validate_json(config_path)
    print(f"  Status: {'PASS' if json_valid else 'FAIL'}")
    print(f"  Message: {json_msg}")
    if not json_valid:
        sys.exit(1)
    print()

    # Validate hyperparameters
    print("Hyperparameter Validation:")
    params_valid, param_errors = validate_hyperparameters(config)
    print(f"  Status: {'PASS' if params_valid else 'FAIL'}")
    if params_valid:
        print(f"  Learning Rate: {config['training']['learning_rate']}")
        print(f"  Batch Size: {config['training']['batch_size']}")
        print(f"  Training Steps: {config['training']['num_steps']}")
        print(f"  Warmup Steps: {config['training']['warmup_steps']}")
        print(f"  Temperature: {config['generation']['temperature']}")
        print(f"  Max Tokens: {config['generation']['max_tokens']}")
    else:
        for error in param_errors:
            print(f"  ERROR: {error}")
    print()

    # Validate paths
    print("Data Path Validation:")
    paths_valid, path_errors = validate_paths(config)
    print(f"  Status: {'PASS' if paths_valid else 'FAIL'}")
    if paths_valid:
        train_file = config['data']['train_file']
        val_file = config['data']['val_file']
        train_stat = os.stat(train_file)
        val_stat = os.stat(val_file)

        print(f"  Train File: {train_file}")
        print(f"    Size: {train_stat.st_size / (1024*1024):.2f} MB")
        print(f"    Readable: Yes")

        print(f"  Val File: {val_file}")
        print(f"    Size: {val_stat.st_size / 1024:.2f} KB")
        print(f"    Readable: Yes")

        print(f"  Checkpoint Dir: {config['output']['checkpoint_dir']}")
        print(f"    Exists: Yes")

        print(f"  Log Dir: {config['output']['log_dir']}")
        print(f"    Exists: Yes")
    else:
        for error in path_errors:
            print(f"  ERROR: {error}")
    print()

    # Validate model endpoint
    print("Model Endpoint Validation:")
    endpoint_valid, endpoint_msg = validate_model_endpoint(config)
    print(f"  Status: {'PASS' if endpoint_valid else 'FAIL'}")
    print(f"  Endpoint: {config['model']['endpoint']}")
    print(f"  Message: {endpoint_msg}")
    print()

    # Final result
    print("=" * 80)
    all_valid = json_valid and params_valid and paths_valid

    if all_valid:
        print("VALIDATION RESULT: SUCCESS")
        print()
        print("All checks passed:")
        print("  ✓ Configuration file created")
        print("  ✓ JSON valid and parseable")
        print("  ✓ Learning rate = 0.0001 (1e-4)")
        print("  ✓ Batch size = 32")
        print("  ✓ Training steps = 100")
        print("  ✓ All data paths exist and verified")
        print("  ✓ Checkpoint/log directories created")

        if endpoint_valid:
            print("  ✓ Model endpoint accessible")
        else:
            print("  ⚠ Model endpoint not accessible (LM Studio may not be running)")
            print("    This is expected if LM Studio is not currently active")

        print()
        print("NOTE: Model endpoint check is informational only.")
        print("Configuration is valid regardless of endpoint availability.")
    else:
        print("VALIDATION RESULT: FAILED")
        print()
        print("Failed checks:")
        if not json_valid:
            print("  ✗ JSON validation failed")
        if not params_valid:
            print("  ✗ Hyperparameter validation failed")
        if not paths_valid:
            print("  ✗ Path validation failed")
        sys.exit(1)

    print("=" * 80)


if __name__ == "__main__":
    main()
