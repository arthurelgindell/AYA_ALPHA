#!/usr/bin/env python3
"""
GLADIATOR Automated Combat Scheduler
Continuous combat operations for maximum training data generation
"""

import subprocess
import time
import json
from datetime import datetime
from pathlib import Path
import threading
import queue

# Configuration
COMBAT_SCRIPT = "/Users/arthurdell/GLADIATOR/scripts/combat_orchestrator.py"
TARGET_PAIRS = 10000
CURRENT_PAIRS = 492  # Updated from verification
BATCH_SIZE = 200  # pairs per batch
SESSIONS_PER_BATCH = 10
ROUNDS_PER_SESSION = 20

class CombatScheduler:
    def __init__(self):
        self.target_pairs = TARGET_PAIRS
        self.current_pairs = CURRENT_PAIRS
        self.batch_size = BATCH_SIZE
        self.sessions_per_batch = SESSIONS_PER_BATCH
        self.rounds_per_session = ROUNDS_PER_SESSION
        self.running = False
        self.results_queue = queue.Queue()
        
    def execute_combat_batch(self, batch_id):
        """Execute a single combat batch"""
        print(f"\n🚀 Starting Combat Batch {batch_id}")
        print(f"   Sessions: {self.sessions_per_batch}")
        print(f"   Rounds per session: {self.rounds_per_session}")
        print(f"   Expected pairs: {self.batch_size}")
        
        try:
            # Execute combat orchestrator
            result = subprocess.run([
                "python3", COMBAT_SCRIPT,
                str(self.sessions_per_batch),
                str(self.rounds_per_session)
            ], capture_output=True, text=True, timeout=3600)  # 1 hour timeout
            
            if result.returncode == 0:
                print(f"✅ Batch {batch_id} completed successfully")
                self.results_queue.put({
                    'batch_id': batch_id,
                    'status': 'success',
                    'pairs_generated': self.batch_size,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                print(f"❌ Batch {batch_id} failed: {result.stderr}")
                self.results_queue.put({
                    'batch_id': batch_id,
                    'status': 'failed',
                    'error': result.stderr,
                    'timestamp': datetime.now().isoformat()
                })
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Batch {batch_id} timed out")
            self.results_queue.put({
                'batch_id': batch_id,
                'status': 'timeout',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            print(f"💥 Batch {batch_id} error: {e}")
            self.results_queue.put({
                'batch_id': batch_id,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    def monitor_progress(self):
        """Monitor training data generation progress"""
        while self.running:
            try:
                # Count current training pairs
                training_dir = Path("/Users/arthurdell/GLADIATOR/datasets/combat_training")
                session_files = list(training_dir.glob("combat_session_*.json"))
                
                total_pairs = 0
                for session_file in session_files:
                    try:
                        with open(session_file) as f:
                            data = json.load(f)
                            total_pairs += len(data.get('training_pairs', []))
                    except:
                        continue
                
                progress = (total_pairs / self.target_pairs) * 100
                
                print(f"\n📊 Progress Update:")
                print(f"   Current pairs: {total_pairs}")
                print(f"   Target pairs: {self.target_pairs}")
                print(f"   Progress: {progress:.2f}%")
                print(f"   Remaining: {self.target_pairs - total_pairs}")
                
                if total_pairs >= self.target_pairs:
                    print(f"\n🎯 TARGET ACHIEVED: {total_pairs} training pairs!")
                    self.running = False
                    break
                    
                time.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                print(f"⚠️  Progress monitoring error: {e}")
                time.sleep(60)
    
    def run_continuous_combat(self):
        """Run continuous combat operations"""
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║              GLADIATOR AUTOMATED COMBAT SCHEDULER               ║
╚══════════════════════════════════════════════════════════════════╝

Target: {self.target_pairs} training pairs
Current: {self.current_pairs} training pairs
Batch size: {self.batch_size} pairs
Sessions per batch: {self.sessions_per_batch}
Rounds per session: {self.rounds_per_session}

Starting continuous combat operations...
""")
        
        self.running = True
        batch_id = 1
        
        # Start progress monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_progress)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        while self.running:
            print(f"\n{'='*80}")
            print(f"🔥 EXECUTING COMBAT BATCH {batch_id}")
            print(f"{'='*80}")
            
            # Execute combat batch
            self.execute_combat_batch(batch_id)
            
            # Check results
            try:
                result = self.results_queue.get(timeout=10)
                if result['status'] == 'success':
                    print(f"✅ Batch {batch_id} completed: {result['pairs_generated']} pairs")
                else:
                    print(f"❌ Batch {batch_id} failed: {result.get('error', 'Unknown error')}")
            except queue.Empty:
                print(f"⚠️  No result received for batch {batch_id}")
            
            # Pause between batches
            if self.running:
                print(f"\n⏸️  Pausing 30 seconds before next batch...")
                time.sleep(30)
            
            batch_id += 1
            
            # Safety limit
            if batch_id > 50:  # Maximum 50 batches
                print(f"\n🛑 Safety limit reached (50 batches)")
                break
        
        print(f"\n🏁 Continuous combat operations completed")
        monitor_thread.join(timeout=10)

def main():
    """Main scheduler"""
    scheduler = CombatScheduler()
    
    try:
        scheduler.run_continuous_combat()
    except KeyboardInterrupt:
        print(f"\n🛑 Scheduler interrupted by user")
        scheduler.running = False
    except Exception as e:
        print(f"\n💥 Scheduler error: {e}")
        scheduler.running = False

if __name__ == "__main__":
    main()
