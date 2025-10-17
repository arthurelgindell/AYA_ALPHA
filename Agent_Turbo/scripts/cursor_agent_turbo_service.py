#!/usr/bin/env python3
"""
AGENT_TURBO Background Service for Cursor Integration
Runs continuously to provide Agent Turbo capabilities to Cursor AI
"""

import os
import sys
import time
import json
import signal
from pathlib import Path
from datetime import datetime

# Add project to path
sys.path.insert(0, '/Volumes/DATA/Agent_Turbo')

from core.agent_turbo import AgentTurbo

# Global service instance
turbo_service = None
running = True

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global running
    print(f"\n🛑 Received signal {signum}, shutting down Agent Turbo service...")
    running = False

def create_status_file(status: str, turbo: AgentTurbo = None):
    """Create status file for Cursor to read."""
    status_dir = Path.home() / '.cursor'
    status_dir.mkdir(parents=True, exist_ok=True)
    
    status_file = status_dir / 'agent_turbo_status.json'
    
    status_data = {
        'status': status,
        'timestamp': datetime.now().isoformat(),
        'pid': os.getpid(),
        'workspace': str(Path('/Volumes/DATA/Agent_Turbo')),
    }
    
    if turbo:
        try:
            stats = json.loads(turbo.stats())
            status_data['stats'] = stats
        except Exception as e:
            status_data['stats_error'] = str(e)
    
    with open(status_file, 'w') as f:
        json.dump(status_data, f, indent=2)
    
    return status_file

def main():
    """Main service loop."""
    global turbo_service, running
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🚀 Starting AGENT_TURBO Background Service for Cursor...")
    print(f"   PID: {os.getpid()}")
    print(f"   Workspace: /Volumes/DATA/Agent_Turbo")
    
    try:
        # Initialize Agent Turbo
        turbo_service = AgentTurbo()
        
        # Verify it's working
        if not turbo_service.verify():
            print("❌ AGENT_TURBO verification failed!")
            create_status_file('failed')
            sys.exit(1)
        
        print("✅ AGENT_TURBO initialized and verified")
        
        # Create status file
        status_file = create_status_file('active', turbo_service)
        print(f"📄 Status file: {status_file}")
        
        # Signal readiness to Cursor
        print("AGENT_TURBO_SERVICE_READY")
        sys.stdout.flush()
        
        # Service loop - keep alive and handle requests
        heartbeat_interval = 60  # Update status every 60 seconds
        last_heartbeat = time.time()
        
        while running:
            current_time = time.time()
            
            # Update status file periodically
            if current_time - last_heartbeat >= heartbeat_interval:
                create_status_file('active', turbo_service)
                last_heartbeat = current_time
            
            # Sleep briefly to avoid CPU spinning
            time.sleep(1)
        
        # Clean shutdown
        print("✅ AGENT_TURBO service stopped cleanly")
        create_status_file('stopped')
        
    except KeyboardInterrupt:
        print("\n🛑 Service interrupted by user")
        create_status_file('stopped')
    except Exception as e:
        print(f"❌ Service error: {e}")
        import traceback
        traceback.print_exc()
        create_status_file('error')
        sys.exit(1)

if __name__ == '__main__':
    main()

