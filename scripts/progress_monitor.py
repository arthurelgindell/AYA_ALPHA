#!/usr/bin/env python3
"""
GLADIATOR Progress Monitor
Real-time tracking of combat training data generation
"""

import json
import time
import os
from pathlib import Path
from datetime import datetime, timedelta
import psycopg2

# Configuration
COMBAT_TRAINING_DIR = Path("/Users/arthurdell/GLADIATOR/datasets/combat_training")
PERSONA_TRAINING_DIR = Path("/Users/arthurdell/GLADIATOR/datasets/persona_combat_training")
TARGET_PAIRS = 10000
REFRESH_INTERVAL = 10  # seconds

DB_CONFIG = {
    'host': 'localhost',
    'database': 'aya_rag',
    'user': 'postgres',
    'password': 'Power$$336633$$'
}

class ProgressMonitor:
    """Monitor training data generation progress"""

    def __init__(self):
        self.start_time = datetime.now()
        self.last_count = 0
        self.last_check_time = time.time()
        self.samples_history = []

    def count_training_pairs(self):
        """Count all training pairs from combat sessions"""
        combat_pairs = 0
        persona_pairs = 0

        # Count regular combat sessions
        combat_files = list(COMBAT_TRAINING_DIR.glob("combat_session_*.json"))
        for session_file in combat_files:
            try:
                with open(session_file) as f:
                    data = json.load(f)
                    combat_pairs += len(data.get('training_pairs', []))
            except:
                continue

        # Count persona combat sessions
        persona_files = list(PERSONA_TRAINING_DIR.glob("persona_combat_session_*.json"))
        for session_file in persona_files:
            try:
                with open(session_file) as f:
                    data = json.load(f)
                    persona_pairs += len(data.get('training_pairs', []))
            except:
                continue

        return {
            'combat_pairs': combat_pairs,
            'persona_pairs': persona_pairs,
            'total_pairs': combat_pairs + persona_pairs,
            'combat_files': len(combat_files),
            'persona_files': len(persona_files)
        }

    def calculate_rates(self, current_count):
        """Calculate generation rates"""
        current_time = time.time()
        time_delta = current_time - self.last_check_time

        if time_delta > 0 and self.last_count > 0:
            pairs_delta = current_count - self.last_count
            rate_per_second = pairs_delta / time_delta
            rate_per_minute = rate_per_second * 60
            rate_per_hour = rate_per_minute * 60
            rate_per_day = rate_per_hour * 24

            return {
                'pairs_delta': pairs_delta,
                'time_delta': time_delta,
                'per_second': rate_per_second,
                'per_minute': rate_per_minute,
                'per_hour': rate_per_hour,
                'per_day': rate_per_day
            }

        return None

    def calculate_eta(self, current_count, rate_per_hour):
        """Calculate estimated time to completion"""
        remaining = TARGET_PAIRS - current_count

        if rate_per_hour > 0:
            hours_remaining = remaining / rate_per_hour
            eta = datetime.now() + timedelta(hours=hours_remaining)
            return {
                'remaining': remaining,
                'hours_remaining': hours_remaining,
                'days_remaining': hours_remaining / 24,
                'eta': eta
            }

        return None

    def get_database_stats(self):
        """Get stats from database"""
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    current_phase,
                    total_attack_patterns_generated,
                    red_team_progress_percentage,
                    gates_passed,
                    gates_total
                FROM gladiator_project_state
                WHERE is_current = TRUE
            """)

            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result:
                return {
                    'phase': result[0],
                    'db_patterns': result[1],
                    'db_progress': result[2],
                    'gates_passed': result[3],
                    'gates_total': result[4]
                }
        except:
            pass

        return None

    def display_dashboard(self, stats, rates, eta, db_stats):
        """Display real-time dashboard"""

        # Clear screen (works on Unix/Mac)
        os.system('clear')

        print("=" * 80)
        print("GLADIATOR PROGRESS MONITOR")
        print("=" * 80)
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Current: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Uptime: {datetime.now() - self.start_time}")
        print("=" * 80)
        print()

        # Training Data Progress
        total = stats['total_pairs']
        progress_pct = (total / TARGET_PAIRS) * 100

        print("TRAINING DATA GENERATION:")
        print(f"  Combat sessions:    {stats['combat_pairs']:>6,} pairs ({stats['combat_files']} files)")
        print(f"  Persona sessions:   {stats['persona_pairs']:>6,} pairs ({stats['persona_files']} files)")
        print(f"  {'─' * 70}")
        print(f"  TOTAL:              {total:>6,} / {TARGET_PAIRS:,} pairs")
        print()

        # Progress Bar
        bar_width = 50
        filled = int(bar_width * total / TARGET_PAIRS)
        bar = '█' * filled + '░' * (bar_width - filled)
        print(f"  [{bar}] {progress_pct:.2f}%")
        print()

        # Milestones
        print("MILESTONES:")
        milestones = [
            (1000, "10% - First Milestone"),
            (2500, "25% - Quarter Complete"),
            (5000, "50% - Halfway Point"),
            (7500, "75% - Three Quarters"),
            (10000, "100% - TARGET COMPLETE")
        ]

        for target, label in milestones:
            if total >= target:
                status = "✅"
            elif total >= target * 0.9:
                status = "🟡"
            else:
                status = "⬜"
            remaining = max(0, target - total)
            print(f"  {status} {target:>5,} pairs - {label:<25} (Remaining: {remaining:>5,})")
        print()

        # Generation Rates
        if rates:
            print("GENERATION RATES:")
            print(f"  Last interval:  +{rates['pairs_delta']:>4} pairs in {rates['time_delta']:.0f}s")
            print(f"  Per minute:      {rates['per_minute']:>5.1f} pairs/min")
            print(f"  Per hour:        {rates['per_hour']:>5.0f} pairs/hour")
            print(f"  Per day:         {rates['per_day']:>5,.0f} pairs/day")
            print()

        # ETA
        if eta and rates and rates['per_hour'] > 0:
            print("ESTIMATED TIME TO COMPLETION:")
            print(f"  Remaining pairs: {eta['remaining']:>6,}")
            print(f"  Hours remaining: {eta['hours_remaining']:>6.1f} hours")
            print(f"  Days remaining:  {eta['days_remaining']:>6.1f} days")
            print(f"  ETA:             {eta['eta'].strftime('%Y-%m-%d %H:%M:%S')}")
            print()

        # Database Status
        if db_stats:
            print("DATABASE STATUS:")
            print(f"  Phase:           {db_stats['phase']}")
            print(f"  DB patterns:     {db_stats['db_patterns']:,}")
            print(f"  DB progress:     {db_stats['db_progress']}%")
            print(f"  Gates passed:    {db_stats['gates_passed']}/{db_stats['gates_total']}")

            # Check sync status
            if abs(total - db_stats['db_patterns']) > 100:
                print(f"  ⚠️  SYNC NEEDED: Database shows {db_stats['db_patterns']:,}, filesystem has {total:,}")
            else:
                print(f"  ✅ Database in sync")
            print()

        print("=" * 80)
        print(f"Next update in {REFRESH_INTERVAL} seconds... (Press Ctrl+C to stop)")
        print("=" * 80)

    def run(self):
        """Run continuous monitoring"""
        print("GLADIATOR Progress Monitor Starting...")
        print(f"Monitoring: {COMBAT_TRAINING_DIR}")
        print(f"           {PERSONA_TRAINING_DIR}")
        print(f"Target: {TARGET_PAIRS:,} training pairs")
        print(f"Refresh interval: {REFRESH_INTERVAL} seconds")
        print()
        print("Press Ctrl+C to stop monitoring")
        print()
        time.sleep(2)

        try:
            while True:
                # Count current pairs
                stats = self.count_training_pairs()
                current_count = stats['total_pairs']

                # Calculate rates
                rates = self.calculate_rates(current_count)

                # Calculate ETA
                eta = None
                if rates and rates['per_hour'] > 0:
                    eta = self.calculate_eta(current_count, rates['per_hour'])

                # Get database stats
                db_stats = self.get_database_stats()

                # Display dashboard
                self.display_dashboard(stats, rates, eta, db_stats)

                # Store for next iteration
                self.last_count = current_count
                self.last_check_time = time.time()

                # Add to history
                self.samples_history.append({
                    'timestamp': datetime.now(),
                    'count': current_count
                })

                # Keep last 100 samples
                if len(self.samples_history) > 100:
                    self.samples_history.pop(0)

                # Check if target reached
                if current_count >= TARGET_PAIRS:
                    print("\n" + "=" * 80)
                    print("🎯 TARGET REACHED!")
                    print("=" * 80)
                    print(f"Total pairs generated: {current_count:,}")
                    print(f"Target: {TARGET_PAIRS:,}")
                    print(f"Time elapsed: {datetime.now() - self.start_time}")
                    print("=" * 80)
                    break

                # Wait for next update
                time.sleep(REFRESH_INTERVAL)

        except KeyboardInterrupt:
            print("\n\n" + "=" * 80)
            print("MONITORING STOPPED")
            print("=" * 80)
            stats = self.count_training_pairs()
            print(f"Final count: {stats['total_pairs']:,} / {TARGET_PAIRS:,} pairs")
            print(f"Runtime: {datetime.now() - self.start_time}")
            print("=" * 80)

def main():
    """Main entry point"""
    monitor = ProgressMonitor()
    monitor.run()

if __name__ == "__main__":
    main()
