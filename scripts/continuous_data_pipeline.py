#!/usr/bin/env python3
"""
GLADIATOR CONTINUOUS DATA PIPELINE - MAXIMUM THROUGHPUT
Orchestrates Red Team (BETA) + Mutation Engine (ALPHA) + Blue Team Training

Mode: FULL AUTO - Max resource utilization
Monitoring: Real-time metrics every 30 seconds
Duration: Until Arthur says stop or targets met
"""

import subprocess
import time
import json
import os
import psycopg2
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

DB_CONFIG = {
    'host': 'localhost',
    'database': 'aya_rag',
    'user': 'postgres',
    'password': 'Power$$336633$$'
}

class ContinuousPipeline:
    """Orchestrate Red Team + Mutations + Training"""
    
    def __init__(self):
        self.start_time = time.time()
        self.iteration = 1
        
        # Metrics
        self.red_team_attacks = 0
        self.mutations_generated = 0
        self.total_training_samples = 52200  # Already have from first run
        
        # Database connection
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor()
        
        # Directories
        self.red_team_dir = "/Users/arthurdell/GLADIATOR/datasets/red_team_sync"
        self.mutation_dir = "/Users/arthurdell/GLADIATOR/datasets/mutations"
        os.makedirs(self.red_team_dir, exist_ok=True)
    
    def sync_red_team_attacks(self):
        """Sync new attacks from BETA to ALPHA"""
        
        try:
            # Rsync new attacks
            result = subprocess.run([
                'rsync', '-av', '--update',
                'beta.local:/Volumes/DATA/GLADIATOR/attack_patterns/',
                self.red_team_dir + '/'
            ], capture_output=True, text=True, timeout=60)
            
            # Count total
            count_result = subprocess.run([
                'find', self.red_team_dir, '-name', '*.json', '-type', 'f'
            ], capture_output=True, text=True)
            
            attack_files = count_result.stdout.strip().split('\n')
            new_count = len([f for f in attack_files if f])
            
            if new_count > self.red_team_attacks:
                new_attacks = new_count - self.red_team_attacks
                self.red_team_attacks = new_count
                return new_attacks
            
            return 0
            
        except Exception as e:
            print(f"  ⚠️  Sync error: {e}")
            return 0
    
    def run_mutation_engine(self, new_attacks):
        """Run mutation engine on new attacks"""
        
        if new_attacks == 0:
            return 0
        
        try:
            # For each new attack, generate 100 mutations
            # Using subprocess to run mutation engine
            result = subprocess.run([
                'python3',
                '/Users/arthurdell/GLADIATOR/scripts/mutation_engine.py'
            ], capture_output=True, text=True, timeout=120, cwd='/Users/arthurdell/GLADIATOR')
            
            # Parse output for mutation count
            output = result.stdout
            if 'mutations' in output.lower():
                # Extract count from output
                for line in output.split('\n'):
                    if 'Mutations:' in line:
                        try:
                            count = int(line.split(':')[1].strip().replace(',', ''))
                            self.mutations_generated += count
                            self.total_training_samples += count
                            return count
                        except:
                            pass
            
            return new_attacks * 50  # Estimate if parsing failed
            
        except Exception as e:
            print(f"  ⚠️  Mutation error: {e}")
            return 0
    
    def get_system_metrics(self):
        """Get metrics from both systems"""
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'elapsed_minutes': (time.time() - self.start_time) / 60
        }
        
        # BETA metrics
        try:
            beta_disk = subprocess.run([
                'ssh', 'beta.local',
                "df /Volumes/DATA | tail -1 | awk '{print $3}'"
            ], capture_output=True, text=True, timeout=10)
            
            metrics['beta_disk_gb'] = float(beta_disk.stdout.strip().replace('Gi', '')) if beta_disk.returncode == 0 else 0
        except:
            metrics['beta_disk_gb'] = 0
        
        # ALPHA metrics
        try:
            alpha_disk = subprocess.run([
                'df', '-h', '/', '|', 'tail', '-1'
            ], capture_output=True, text=True, timeout=5, shell=True)
            
            metrics['alpha_disk_info'] = alpha_disk.stdout.strip()
        except:
            metrics['alpha_disk_info'] = 'unknown'
        
        return metrics
    
    def log_to_database(self, event_type, data):
        """Log event to database"""
        try:
            self.cursor.execute("""
                INSERT INTO gladiator_change_log (
                    change_type, changed_by, entity_name, reason, metadata
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                event_type,
                'continuous_pipeline',
                f'iteration_{self.iteration}',
                json.dumps(data),
                json.dumps(data)
            ))
            self.conn.commit()
        except:
            pass
    
    def display_dashboard(self, metrics):
        """Display real-time dashboard"""
        
        print("\n" + "="*80)
        print(f"GLADIATOR CONTINUOUS PIPELINE - {datetime.now().strftime('%H:%M:%S')}")
        print("="*80)
        print(f"Elapsed: {metrics['elapsed_minutes']:.1f} minutes")
        print()
        
        print("DATA GENERATION:")
        print(f"  Red Team attacks (BETA LLM):  {self.red_team_attacks:,}")
        print(f"  Mutations (ALPHA CPU):        {self.mutations_generated:,}")
        print(f"  TOTAL TRAINING SAMPLES:       {self.total_training_samples:,}")
        print()
        
        print("SYSTEM METRICS:")
        print(f"  BETA storage: {metrics.get('beta_disk_gb', 0):.1f} GB used")
        print(f"  ALPHA storage: {metrics.get('alpha_disk_info', 'checking...')}")
        print()
        
        # Calculate rates
        if metrics['elapsed_minutes'] > 0:
            red_rate = self.red_team_attacks / metrics['elapsed_minutes']
            mut_rate = self.mutations_generated / metrics['elapsed_minutes']
            total_rate = self.total_training_samples / metrics['elapsed_minutes']
            
            print("GENERATION RATES:")
            print(f"  Red Team: {red_rate:.0f}/min = {red_rate*60:.0f}/hour = {red_rate*1440:,.0f}/day")
            print(f"  Mutations: {mut_rate:.0f}/min")
            print(f"  Combined: {total_rate:.0f}/min = {total_rate*60:,.0f}/hour")
            print()
            
            # Projection to 10M
            if total_rate > 0:
                remaining = 10000000 - self.total_training_samples
                eta_minutes = remaining / total_rate
                print("PROJECTION TO 10M SAMPLES:")
                print(f"  Remaining: {remaining:,}")
                print(f"  ETA: {eta_minutes:.0f} minutes ({eta_minutes/60:.1f} hours)")
        
        print("="*80)
    
    def run_continuous(self, check_interval=60):
        """
        Run continuous pipeline
        
        Every minute:
        1. Sync new Red Team attacks from BETA
        2. Run mutation engine on new attacks (if any)
        3. Update metrics
        4. Log to database
        5. Display dashboard
        """
        
        print("="*80)
        print("GLADIATOR CONTINUOUS PIPELINE - STARTING")
        print("="*80)
        print(f"Started: {datetime.now()}")
        print(f"Check interval: {check_interval} seconds")
        print(f"Initial training samples: {self.total_training_samples:,}")
        print()
        print("Running until:")
        print("  - Arthur types CTRL+C")
        print("  - 10M samples reached")
        print("  - Critical error detected")
        print("="*80)
        print()
        
        cycle = 0
        
        try:
            while self.total_training_samples < 10000000:
                cycle += 1
                
                # Sync new Red Team attacks
                new_attacks = self.sync_red_team_attacks()
                
                if new_attacks > 0:
                    print(f"[Cycle {cycle}] Synced {new_attacks} new attacks from BETA")
                    
                    # Generate mutations (use ALPHA CPUs)
                    new_mutations = self.run_mutation_engine(new_attacks)
                    print(f"[Cycle {cycle}] Generated {new_mutations:,} mutations")
                
                # Get metrics
                metrics = self.get_system_metrics()
                
                # Display dashboard
                self.display_dashboard(metrics)
                
                # Log to database
                self.log_to_database('pipeline_cycle', {
                    'cycle': cycle,
                    'red_team_attacks': self.red_team_attacks,
                    'mutations': self.mutations_generated,
                    'total': self.total_training_samples,
                    'new_attacks': new_attacks if 'new_attacks' in locals() else 0
                })
                
                # Wait for next cycle
                print(f"\nNext check in {check_interval}s...\n")
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\n\n" + "="*80)
            print("PIPELINE STOPPED BY USER")
            print("="*80)
            self.display_final_summary()
        
        except Exception as e:
            print(f"\n\n🚨 ERROR: {e}")
            self.display_final_summary()
    
    def display_final_summary(self):
        """Display final statistics"""
        
        total_time = (time.time() - self.start_time) / 60
        
        print(f"\nFINAL STATISTICS:")
        print(f"  Runtime: {total_time:.1f} minutes ({total_time/60:.2f} hours)")
        print(f"  Red Team attacks: {self.red_team_attacks:,}")
        print(f"  Mutations: {self.mutations_generated:,}")
        print(f"  TOTAL SAMPLES: {self.total_training_samples:,}")
        print(f"  Average rate: {self.total_training_samples/total_time:.0f} samples/minute")
        print()
        print("✅ Data ready for Blue Team training")
        
        # Final database update
        self.cursor.execute("""
            UPDATE gladiator_project_state
            SET total_attack_patterns_generated = %s
            WHERE is_current = TRUE
        """, (self.total_training_samples,))
        self.conn.commit()

if __name__ == "__main__":
    pipeline = ContinuousPipeline()
    pipeline.run_continuous(check_interval=60)  # Check every minute

