#!/usr/bin/env python3
"""
Monitored Execution - Runs commands with timeout and logging
Prevents infinite hangs by terminating after timeout
"""

import subprocess
import sys
import signal
import time
from datetime import datetime
import json

def run_with_timeout(command, timeout_seconds=60, log_file=None):
    """Run command with timeout, return success/failure/timeout"""
    
    start_time = datetime.now()
    log_data = {
        'command': command,
        'start_time': start_time.isoformat(),
        'timeout_seconds': timeout_seconds,
        'status': 'unknown',
        'output': '',
        'error': '',
        'duration_seconds': 0
    }
    
    try:
        # Start process
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=os.setsid if hasattr(os, 'setsid') else None
        )
        
        # Wait with timeout
        try:
            stdout, stderr = process.communicate(timeout=timeout_seconds)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            log_data.update({
                'status': 'success' if process.returncode == 0 else 'failed',
                'exit_code': process.returncode,
                'output': stdout,
                'error': stderr,
                'duration_seconds': duration
            })
            
            return log_data
            
        except subprocess.TimeoutExpired:
            # Timeout - kill process tree
            import os
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            except:
                process.kill()
            
            duration = (datetime.now() - start_time).total_seconds()
            
            log_data.update({
                'status': 'timeout',
                'duration_seconds': duration,
                'error': f'Command exceeded {timeout_seconds}s timeout'
            })
            
            return log_data
    
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        log_data.update({
            'status': 'error',
            'error': str(e),
            'duration_seconds': duration
        })
        
        return log_data
    
    finally:
        # Always log results
        if log_file:
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_data, indent=2) + '\n\n')

if __name__ == "__main__":
    import os
    
    if len(sys.argv) < 2:
        print("Usage: monitored_exec.py <command> [timeout_seconds] [log_file]")
        sys.exit(1)
    
    command = sys.argv[1]
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    log_file = sys.argv[3] if len(sys.argv) > 3 else '/Users/arthurdell/GLADIATOR/logs/monitored_exec.log'
    
    result = run_with_timeout(command, timeout, log_file)
    
    print(f"Status: {result['status']}")
    print(f"Duration: {result['duration_seconds']:.1f}s")
    
    if result['output']:
        print(f"Output:\n{result['output'][:500]}")
    
    if result['error']:
        print(f"Error:\n{result['error'][:500]}")
    
    sys.exit(0 if result['status'] == 'success' else 1)

