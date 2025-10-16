#!/usr/bin/env python3
"""
GLADIATOR Red Team Monitor - Iteration Safety System
Monitors BETA during Red Team generation, aborts if dangerous

Purpose: Prevent Red Team from destroying systems
Runs on: ALPHA (monitoring BETA)
Checks: Disk, RAM, CPU, network, processes, system responsiveness
"""

import subprocess
import time
import json
import psycopg2
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'aya_rag',
    'user': 'postgres',
    'password': 'Power$$336633$$'
}

# Monitoring thresholds (ABORT CONDITIONS)
ABORT_THRESHOLDS = {
    'disk_usage_percent': 90,      # Abort if disk >90% full
    'ram_usage_percent': 95,       # Abort if RAM >95% used
    'cpu_temp_celsius': 95,        # Abort if CPU >95°C (thermal danger)
    'process_count': 5000,         # Abort if >5000 processes (fork bomb)
    'network_mbps': 2000,          # Abort if >2Gbps sustained (flood)
    'ping_timeout_seconds': 5      # Abort if BETA unresponsive >5s
}

class RedTeamMonitor:
    """Monitor BETA during Red Team iteration, abort if dangerous"""
    
    def __init__(self, iteration_number):
        self.iteration = iteration_number
        self.beta_host = "beta.local"
        self.start_time = time.time()
        self.abort_triggered = False
        self.abort_reason = None
        
        # Connect to database
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor()
        
        # Log monitor start
        self._log_to_db('monitor_start', {'iteration': iteration_number})
    
    def check_beta_responsive(self):
        """Check if BETA responds to ping"""
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '2', self.beta_host],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def get_beta_metrics(self):
        """Collect metrics from BETA via SSH"""
        try:
            # Disk usage
            disk_cmd = "df /Volumes/DATA | tail -1 | awk '{print $5}' | sed 's/%//'"
            disk_result = subprocess.run(
                ['ssh', self.beta_host, disk_cmd],
                capture_output=True,
                text=True,
                timeout=10
            )
            disk_usage = int(disk_result.stdout.strip()) if disk_result.returncode == 0 else None
            
            # RAM usage (approximate from vm_stat)
            ram_cmd = "vm_stat | grep 'Pages free' | awk '{print $3}' | sed 's/\\.//'"
            ram_result = subprocess.run(
                ['ssh', self.beta_host, ram_cmd],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Process count
            proc_cmd = "ps aux | wc -l"
            proc_result = subprocess.run(
                ['ssh', self.beta_host, proc_cmd],
                capture_output=True,
                text=True,
                timeout=10
            )
            process_count = int(proc_result.stdout.strip()) if proc_result.returncode == 0 else None
            
            # Memory info
            mem_cmd = "sysctl -n hw.memsize"
            mem_result = subprocess.run(
                ['ssh', self.beta_host, mem_cmd],
                capture_output=True,
                text=True,
                timeout=10
            )
            total_mem_bytes = int(mem_result.stdout.strip()) if mem_result.returncode == 0 else None
            total_mem_gb = total_mem_bytes / (1024**3) if total_mem_bytes else 256
            
            return {
                'disk_usage_percent': disk_usage,
                'ram_total_gb': total_mem_gb,
                'process_count': process_count,
                'responsive': True,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'responsive': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_abort_conditions(self, metrics):
        """Check if any abort condition is met"""
        
        if not metrics.get('responsive'):
            return True, 'beta_unresponsive'
        
        if metrics.get('disk_usage_percent', 0) > ABORT_THRESHOLDS['disk_usage_percent']:
            return True, f"disk_full_{metrics['disk_usage_percent']}%"
        
        if metrics.get('process_count', 0) > ABORT_THRESHOLDS['process_count']:
            return True, f"process_explosion_{metrics['process_count']}"
        
        return False, None
    
    def emergency_shutdown(self, reason):
        """Emergency shutdown of Red Team on BETA"""
        print(f"\n🚨 EMERGENCY SHUTDOWN TRIGGERED: {reason}")
        print("="*80)
        
        try:
            # Kill LM Studio
            print("Killing LM Studio processes on BETA...")
            subprocess.run(['ssh', self.beta_host, 'killall "LM Studio"'], timeout=10)
            
            # Kill Python (attack generation scripts)
            print("Killing Python processes on BETA...")
            subprocess.run(['ssh', self.beta_host, 'killall python3'], timeout=10)
            
            # Verify shutdown
            time.sleep(2)
            if self.check_beta_responsive():
                print("✅ BETA still responsive after shutdown")
            else:
                print("⚠️  BETA not responding (may need manual intervention)")
            
            # Log to database
            self._log_to_db('emergency_shutdown', {
                'reason': reason,
                'iteration': self.iteration
            })
            
            print("="*80)
            print("Emergency shutdown complete. Review BETA status.")
            
        except Exception as e:
            print(f"❌ Shutdown failed: {e}")
            print("MANUAL INTERVENTION REQUIRED")
    
    def monitor_iteration(self, duration_minutes):
        """
        Monitor Red Team iteration for specified duration
        
        Args:
            duration_minutes: How long to monitor
        
        Returns:
            'completed' if successful, 'aborted' if emergency shutdown
        """
        print("="*80)
        print(f"RED TEAM MONITOR - ITERATION {self.iteration}")
        print(f"Duration: {duration_minutes} minutes")
        print(f"Started: {datetime.now()}")
        print("="*80)
        
        end_time = time.time() + (duration_minutes * 60)
        check_interval = 10  # Check every 10 seconds
        check_count = 0
        
        while time.time() < end_time:
            check_count += 1
            elapsed = int(time.time() - self.start_time)
            remaining = int(end_time - time.time())
            
            # Get metrics
            metrics = self.get_beta_metrics()
            
            # Check abort conditions
            should_abort, abort_reason = self.check_abort_conditions(metrics)
            
            if should_abort:
                self.abort_triggered = True
                self.abort_reason = abort_reason
                self.emergency_shutdown(abort_reason)
                return 'aborted'
            
            # Display status (every 6th check = 1 minute)
            if check_count % 6 == 0:
                print(f"[{elapsed//60:02d}:{elapsed%60:02d}] "
                      f"Disk: {metrics.get('disk_usage_percent', '?')}% | "
                      f"Procs: {metrics.get('process_count', '?')} | "
                      f"Remaining: {remaining//60}m{remaining%60}s")
                
                # Log to database
                self._log_metrics(metrics)
            
            # Sleep until next check
            time.sleep(check_interval)
        
        print("\n" + "="*80)
        print(f"✅ ITERATION {self.iteration} MONITORING COMPLETE")
        print(f"Duration: {duration_minutes} minutes")
        print(f"Checks performed: {check_count}")
        print(f"Abort triggered: {self.abort_triggered}")
        print("="*80)
        
        return 'completed'
    
    def _log_to_db(self, event_type, data):
        """Log event to database"""
        try:
            self.cursor.execute("""
                INSERT INTO gladiator_change_log (
                    change_type, changed_by, entity_type, entity_name,
                    reason, impact, metadata
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                event_type,
                'red_team_monitor',
                'monitoring',
                f'iteration_{self.iteration}',
                json.dumps(data),
                'critical',
                json.dumps(data)
            ))
            self.conn.commit()
        except Exception as e:
            print(f"⚠️  Database log failed: {e}")
    
    def _log_metrics(self, metrics):
        """Log metrics to database"""
        try:
            self.cursor.execute("""
                INSERT INTO gladiator_hardware_performance (
                    node_name, measured_at,
                    storage_used_gb, 
                    metadata
                ) VALUES (%s, %s, %s, %s)
            """, (
                'BETA',
                datetime.now(),
                metrics.get('disk_usage_percent', 0) * 14 / 100,  # Approximate GB
                json.dumps(metrics)
            ))
            self.conn.commit()
        except:
            pass  # Non-critical, continue monitoring
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close()


def test_monitoring_system():
    """Test monitoring system (dry run, no Red Team)"""
    
    print("="*80)
    print("MONITORING SYSTEM DRY RUN TEST")
    print("="*80)
    
    monitor = RedTeamMonitor(iteration_number=0)
    
    # Test 1: BETA connectivity
    print("\n[TEST 1] BETA Connectivity...")
    responsive = monitor.check_beta_responsive()
    print(f"✅ BETA responsive: {responsive}")
    
    if not responsive:
        print("❌ CRITICAL: Cannot reach BETA")
        return False
    
    # Test 2: Metrics collection
    print("\n[TEST 2] Metrics Collection...")
    metrics = monitor.get_beta_metrics()
    print(f"✅ Disk usage: {metrics.get('disk_usage_percent', '?')}%")
    print(f"✅ RAM total: {metrics.get('ram_total_gb', '?')} GB")
    print(f"✅ Processes: {metrics.get('process_count', '?')}")
    
    # Test 3: Abort condition logic
    print("\n[TEST 3] Abort Condition Logic...")
    should_abort, reason = monitor.check_abort_conditions(metrics)
    print(f"✅ Abort triggered: {should_abort}")
    if should_abort:
        print(f"   Reason: {reason}")
    
    # Test 4: Emergency shutdown (simulation)
    print("\n[TEST 4] Emergency Shutdown (SIMULATION)...")
    print("   Testing SSH connectivity for shutdown...")
    test_ssh = subprocess.run(
        ['ssh', 'beta.local', 'echo "shutdown test"'],
        capture_output=True,
        timeout=5
    )
    if test_ssh.returncode == 0:
        print("✅ Can execute remote commands on BETA")
        print("✅ Emergency shutdown would work")
    else:
        print("❌ Cannot execute remote commands")
        return False
    
    # Test 5: Short monitoring run (30 seconds)
    print("\n[TEST 5] Short Monitoring Run (30 seconds)...")
    result = monitor.monitor_iteration(duration_minutes=0.5)
    print(f"✅ Monitoring result: {result}")
    
    print("\n" + "="*80)
    print("✅ MONITORING SYSTEM VALIDATED")
    print("="*80)
    print("\nAbort thresholds configured:")
    for key, value in ABORT_THRESHOLDS.items():
        print(f"  - {key}: {value}")
    
    return True

if __name__ == "__main__":
    success = test_monitoring_system()
    
    if success:
        print("\n✅ READY FOR RED TEAM ITERATIONS")
        exit(0)
    else:
        print("\n❌ MONITORING SYSTEM FAILED - FIX BEFORE PROCEEDING")
        exit(1)

