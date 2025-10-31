#!/usr/bin/env python3
"""
Worker coordinator for n8n distributed workers
Handles worker registration, heartbeats, and status updates
"""

import os
import sys
import time
import socket
from datetime import datetime

# Add Agent Turbo integration
sys.path.insert(0, os.path.dirname(__file__))
from agent_turbo_integration import N8NAgentTurboIntegration


class WorkerCoordinator:
    """Coordinate n8n worker with database tracking"""
    
    def __init__(self):
        """Initialize coordinator"""
        self.worker_id = os.environ.get('HOSTNAME', socket.gethostname())
        self.system_node = os.environ.get('SYSTEM_NODE', 'ALPHA')
        self.integration = N8NAgentTurboIntegration()
        self.heartbeat_interval = 30  # seconds
    
    def register(self):
        """Register worker on startup"""
        print(f"[{datetime.now()}] Registering worker: {self.worker_id}")
        try:
            self.integration.register_worker(
                worker_id=self.worker_id,
                worker_type='n8n_worker',
                system_node=self.system_node
            )
            print(f"[{datetime.now()}] Worker registered successfully")
        except Exception as e:
            print(f"[{datetime.now()}] Worker registration failed: {e}")
    
    def heartbeat_loop(self):
        """Continuous heartbeat loop"""
        while True:
            try:
                self.integration.worker_heartbeat(self.worker_id)
                print(f"[{datetime.now()}] Heartbeat sent for {self.worker_id}")
            except Exception as e:
                print(f"[{datetime.now()}] Heartbeat failed: {e}")
            
            time.sleep(self.heartbeat_interval)
    
    def start(self):
        """Start coordinator (registration + heartbeat)"""
        self.register()
        self.heartbeat_loop()


if __name__ == '__main__':
    coordinator = WorkerCoordinator()
    coordinator.start()

