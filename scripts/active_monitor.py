#!/usr/bin/env python3
"""
Active Combat Monitor - Reports progress every 2 minutes
"""
import json
import time
from pathlib import Path
from datetime import datetime

def count_pairs():
    """Count all training pairs"""
    training_dir = Path("/Users/arthurdell/GLADIATOR/datasets/combat_training")
    total = 0
    for f in training_dir.glob("combat_session_*.json"):
        try:
            with open(f) as fp:
                total += len(json.load(fp).get('training_pairs', []))
        except:
            pass
    return total

def main():
    print("="*70)
    print("GLADIATOR ACTIVE COMBAT MONITOR")
    print("Reporting every 2 minutes | Press Ctrl+C to stop")
    print("="*70)

    last_count = count_pairs()
    start_time = time.time()

    while True:
        time.sleep(120)  # 2 minutes

        current_count = count_pairs()
        elapsed = (time.time() - start_time) / 60  # minutes
        gained = current_count - last_count
        rate = gained / 2 if gained > 0 else 0  # pairs per minute

        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Progress Report:")
        print(f"  Total Pairs: {current_count} ({(current_count/10000)*100:.2f}%)")
        print(f"  Gained: +{gained} pairs in last 2 minutes")
        print(f"  Rate: {rate:.1f} pairs/min ({rate*60:.0f} pairs/hour)")
        print(f"  Milestone 1 (1,000): {(current_count/1000)*100:.1f}%")
        print(f"  Remaining: {10000 - current_count}")

        if rate > 0:
            eta_minutes = (10000 - current_count) / rate
            eta_hours = eta_minutes / 60
            print(f"  ETA to 10,000: {eta_hours:.1f} hours")

        last_count = current_count

        if current_count >= 10000:
            print(f"\n🎯 TARGET REACHED: {current_count} pairs!")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nMonitor stopped by user")
