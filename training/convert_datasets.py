#!/usr/bin/env python3
"""
Convert GLADIATOR reality check datasets to MLX-LM format.
Converts template/attack_code pairs to chat format for fine-tuning.
"""

import json
from pathlib import Path

def convert_to_chat_format(input_file, output_file):
    """Convert GLADIATOR dataset to MLX-LM chat format."""
    converted = 0

    with open(input_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', encoding='utf-8') as f_out:
        for line_num, line in enumerate(f_in, 1):
            try:
                line = line.strip()
                if not line:
                    continue

                data = json.loads(line)

                # Handle different field name formats
                # Format 1: template/attack_code (newer format)
                # Format 2: type/code (older format)
                if "template" in data and "attack_code" in data:
                    user_content = data["template"]
                    assistant_content = data["attack_code"]
                elif "type" in data and "code" in data:
                    user_content = data["type"]
                    assistant_content = data["code"]
                else:
                    print(f"Warning: Line {line_num} missing required fields: {list(data.keys())}")
                    continue

                # Convert to chat format with user/assistant messages
                chat_entry = {
                    "messages": [
                        {
                            "role": "user",
                            "content": user_content
                        },
                        {
                            "role": "assistant",
                            "content": assistant_content
                        }
                    ]
                }

                f_out.write(json.dumps(chat_entry) + '\n')
                converted += 1

            except json.JSONDecodeError as e:
                print(f"Warning: Line {line_num} has invalid JSON: {e}")
                continue
            except Exception as e:
                print(f"Warning: Line {line_num} error: {e}")
                continue

    return converted

if __name__ == "__main__":
    # Define paths
    train_input = Path("/Users/arthurdell/GLADIATOR/datasets/reality_check_train_900.jsonl")
    val_input = Path("/Users/arthurdell/GLADIATOR/datasets/reality_check_val_100.jsonl")

    output_dir = Path("/Users/arthurdell/GLADIATOR/training/reality_check_data")
    train_output = output_dir / "train.jsonl"
    val_output = output_dir / "valid.jsonl"

    # Convert datasets
    print("Converting training dataset...")
    train_count = convert_to_chat_format(train_input, train_output)
    print(f"Converted {train_count} training samples to {train_output}")

    print("\nConverting validation dataset...")
    val_count = convert_to_chat_format(val_input, val_output)
    print(f"Converted {val_count} validation samples to {val_output}")

    print("\nDataset conversion complete!")
    print(f"Training data: {train_output}")
    print(f"Validation data: {val_output}")
