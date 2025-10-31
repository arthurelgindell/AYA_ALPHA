"""
Agent Turbo Remote Configuration
For accessing ALPHA's PostgreSQL from AIR or other remote nodes

Author: Claude for Arthur
Date: October 29, 2025
"""

import socket

def get_database_config():
    """
    Auto-detect node and return appropriate database configuration.
    
    Returns:
        dict: Database configuration optimized for current node
    """
    hostname = socket.gethostname().lower()
    
    if 'alpha' in hostname:
        # On ALPHA - use localhost (fastest)
        return {
            'host': 'localhost',
            'port': 5432,
            'database': 'aya_rag',
            'user': 'postgres',
            'password': 'Power$$336633$$',
            'note': 'Local ALPHA connection (~1ms)'
        }
    
    elif 'beta' in hostname:
        # On BETA - prefer 10GbE, fallback to Tailscale
        return {
            'host': '192.168.0.80',  # ALPHA's 10GbE IP
            'port': 5432,
            'database': 'aya_rag',
            'user': 'postgres',
            'password': 'Power$$336633$$',
            'fallback_host': 'alpha.tail5f2bae.ts.net',
            'note': 'BETA to ALPHA via 10GbE (~2ms)'
        }
    
    elif 'gamma' in hostname:
        # On Gamma - use Tailscale
        return {
            'host': 'alpha.tail5f2bae.ts.net',
            'port': 5432,
            'database': 'aya_rag',
            'user': 'postgres',
            'password': 'Power$$336633$$',
            'note': 'Gamma to ALPHA via Tailscale (~5-10ms expected)'
        }
    
    else:
        # On AIR or unknown - use Tailscale
        return {
            'host': 'alpha.tail5f2bae.ts.net',
            'port': 5432,
            'database': 'aya_rag',
            'user': 'postgres',
            'password': 'Power$$336633$$',
            'note': 'Remote to ALPHA via Tailscale (~78ms measured from AIR)'
        }

if __name__ == "__main__":
    config = get_database_config()
    print("Database configuration for this node:")
    for key, value in config.items():
        print(f"  {key}: {value}")

