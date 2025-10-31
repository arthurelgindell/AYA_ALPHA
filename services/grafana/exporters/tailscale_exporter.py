#!/usr/bin/env python3
"""
Tailscale Metrics Exporter
Monitors Tailscale mesh network health
"""
import subprocess
import json
from prometheus_client import start_http_server, Gauge
import time
import sys

tailscale_peer_online = Gauge('tailscale_peer_online', 'Peer online status (1=online, 0=offline)', ['peer', 'peer_ip'])
tailscale_peer_latency_ms = Gauge('tailscale_peer_latency_ms', 'Peer latency in milliseconds', ['peer', 'peer_ip'])
tailscale_peer_tx_bytes = Gauge('tailscale_peer_tx_bytes', 'Bytes transmitted to peer', ['peer'])
tailscale_peer_rx_bytes = Gauge('tailscale_peer_rx_bytes', 'Bytes received from peer', ['peer'])
tailscale_peer_last_seen = Gauge('tailscale_peer_last_seen_seconds', 'Seconds since peer was last seen', ['peer'])
tailscale_relay = Gauge('tailscale_relay_active', 'Peer using relay (1=yes, 0=direct)', ['peer'])
tailscale_self_ip = Gauge('tailscale_self_info', 'Self node information', ['hostname', 'tailscale_ip'])

def collect_tailscale_metrics():
    """Collect Tailscale mesh network metrics"""
    try:
        # Use full path to tailscale binary on macOS
        tailscale_cmd = '/Applications/Tailscale.app/Contents/MacOS/Tailscale'
        result = subprocess.run([tailscale_cmd, 'status', '--json'], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print(f"Tailscale status command failed: {result.stderr}", file=sys.stderr)
            return
            
        data = json.loads(result.stdout)
        
        # Self node information
        if 'Self' in data:
            self_data = data['Self']
            hostname = self_data.get('HostName', 'unknown')
            tailscale_ip = self_data.get('TailscaleIPs', ['unknown'])[0] if 'TailscaleIPs' in self_data else 'unknown'
            tailscale_self_ip.labels(hostname=hostname, tailscale_ip=tailscale_ip).set(1)
        
        # Peer information
        for peer_key, peer_data in data.get('Peer', {}).items():
            peer_name = peer_data.get('HostName', peer_key[:8])
            peer_ip = peer_data.get('TailscaleIPs', ['unknown'])[0] if 'TailscaleIPs' in peer_data else 'unknown'
            
            # Online status
            online = 1 if peer_data.get('Online', False) else 0
            tailscale_peer_online.labels(peer=peer_name, peer_ip=peer_ip).set(online)
            
            # Last seen (calculate from LastSeen timestamp if available)
            if 'LastSeen' in peer_data and peer_data['LastSeen']:
                try:
                    from datetime import datetime
                    last_seen = datetime.fromisoformat(peer_data['LastSeen'].replace('Z', '+00:00'))
                    seconds_ago = (datetime.now().astimezone() - last_seen).total_seconds()
                    tailscale_peer_last_seen.labels(peer=peer_name).set(seconds_ago)
                except:
                    pass
            
            # Relay status
            relay = 1 if peer_data.get('Relay', '') else 0
            tailscale_relay.labels(peer=peer_name).set(relay)
            
            # Try to measure latency via ping
            if online and peer_ip != 'unknown':
                try:
                    ping_result = subprocess.run(
                        ['ping', '-c', '1', '-W', '1', peer_ip],
                        capture_output=True, text=True, timeout=2
                    )
                    if 'time=' in ping_result.stdout:
                        latency_str = ping_result.stdout.split('time=')[1].split(' ')[0]
                        latency = float(latency_str)
                        tailscale_peer_latency_ms.labels(peer=peer_name, peer_ip=peer_ip).set(latency)
                except:
                    pass
                    
            # TX/RX bytes (if available)
            if 'TxBytes' in peer_data:
                tailscale_peer_tx_bytes.labels(peer=peer_name).set(peer_data['TxBytes'])
            if 'RxBytes' in peer_data:
                tailscale_peer_rx_bytes.labels(peer=peer_name).set(peer_data['RxBytes'])
                
    except subprocess.TimeoutExpired:
        print("Tailscale status command timed out", file=sys.stderr)
    except json.JSONDecodeError as e:
        print(f"Failed to parse Tailscale JSON: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Error collecting Tailscale metrics: {e}", file=sys.stderr)

if __name__ == '__main__':
    print("Starting Tailscale Metrics Exporter on port 9201...")
    start_http_server(9201)
    print("Tailscale Metrics Exporter running. Metrics available at http://localhost:9201/metrics")
    
    while True:
        try:
            collect_tailscale_metrics()
        except Exception as e:
            print(f"Error in collection loop: {e}", file=sys.stderr)
        time.sleep(30)  # Collect every 30 seconds

