#!/usr/bin/env python3
"""
GLADIATOR Combat Monitor - Real-time throughput tracking
Monitors combat_training directory and reports progress
"""

import os
import json
import time
import glob
from datetime import datetime
from pathlib import Path

TRAINING_DIR = Path("/Users/arthurdell/GLADIATOR/datasets/combat_training")
TARGET_PAIRS = 10000

def count_training_pairs():
    """Count total training pairs generated"""
    total_pairs = 0
    valid_files = 0

    for f in glob.glob(str(TRAINING_DIR / "combat_session_*.json")):
        if os.path.getsize(f) > 1000:  # Skip placeholder files
            try:
                with open(f, 'r') as file:
                    data = json.load(file)
                    pairs = 0

                    if isinstance(data, dict):
                        if 'rounds' in data:
                            pairs = len(data['rounds'])
                        elif 'training_pairs' in data:
                            pairs = len(data['training_pairs'])
                        elif 'attacks' in data:
                            pairs = len(data['attacks'])

                    if pairs > 0:
                        total_pairs += pairs
                        valid_files += 1
            except:
                pass

    return total_pairs, valid_files

def main():
    """Monitor combat progress in real-time"""
    print("=" * 80)
    print("GLADIATOR COMBAT MONITOR - TURBO MODE")
    print("=" * 80)
    print(f"Target: {TARGET_PAIRS} training pairs")
    print(f"Monitor interval: 30 seconds\n")

    start_time = time.time()
    last_pairs = 0
    last_check_time = start_time

    try:
        while True:
            current_pairs, valid_files = count_training_pairs()
            current_time = time.time()
            elapsed_minutes = (current_time - start_time) / 60

            # Calculate throughput
            pairs_since_last = current_pairs - last_pairs
            time_since_last = (current_time - last_check_time) / 60

            if time_since_last > 0:
                current_throughput = pairs_since_last / time_since_last
            else:
                current_throughput = 0

            # Calculate ETA
            remaining_pairs = TARGET_PAIRS - current_pairs
            if current_throughput > 0:
                eta_minutes = remaining_pairs / current_throughput
                eta_hours = eta_minutes / 60
            else:
                eta_minutes = 0
                eta_hours = 0

            # Progress bar
            progress_pct = (current_pairs / TARGET_PAIRS) * 100
            bar_length = 50
            filled_length = int(bar_length * current_pairs // TARGET_PAIRS)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)

            # Display
            print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
                  f"[{bar}] {progress_pct:.1f}% | "
                  f"{current_pairs:,}/{TARGET_PAIRS:,} pairs | "
                  f"{current_throughput:.1f} pairs/min | "
                  f"ETA: {eta_hours:.1f}h | "
                  f"Files: {valid_files}",
                  end='', flush=True)

            # Update tracking
            last_pairs = current_pairs
            last_check_time = current_time

            # Check if complete
            if current_pairs >= TARGET_PAIRS:
                print("\n")
                print("=" * 80)
                print("TARGET ACHIEVED!")
                print(f"Total pairs: {current_pairs:,}")
                print(f"Total time: {elapsed_minutes:.1f} minutes ({elapsed_minutes/60:.1f} hours)")
                print(f"Average throughput: {current_pairs/elapsed_minutes:.1f} pairs/minute")
                print("=" * 80)
                break

            time.sleep(30)  # Check every 30 seconds

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
        print(f"Final count: {current_pairs:,} pairs in {elapsed_minutes:.1f} minutes")

if __name__ == "__main__":
    main()
