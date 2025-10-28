# YugabyteDB Configuration for Agent Turbo
# Created: October 28, 2025
# Purpose: Enable Agent Turbo to use YugabyteDB distributed database

# YugabyteDB Connection Configuration
YUGABYTE_CONFIG = {
    'host': '127.0.0.1',  # YugabyteDB node 1
    'port': 5433,         # YugabyteDB YSQL port
    'database': 'aya_rag_prod',  # Production database
    'user': 'yugabyte',
    'password': 'yugabyte'
}

# Alternative YugabyteDB nodes for load balancing
YUGABYTE_NODES = [
    {'host': '127.0.0.1', 'port': 5433},  # Node 1 (Master)
    {'host': '127.0.0.2', 'port': 5434},  # Node 2
    {'host': '127.0.0.3', 'port': 5435},  # Node 3
]

# YugabyteDB Specific Settings
YUGABYTE_SETTINGS = {
    'topology_keys': ['cloud1.datacenter1.rack1'],
    'load_balance': True,
    'yb_read_from_followers': True,  # Enable read from followers
    'statement_timeout': 60000,  # 60 seconds
    'idle_in_transaction_session_timeout': 60000,  # 60 seconds
}

# Feature Flags
USE_YUGABYTE = True  # Set to True to use YugabyteDB, False for PostgreSQL
ENABLE_FAILOVER = True  # Enable automatic failover between nodes
ENABLE_LOAD_BALANCING = True  # Distribute reads across nodes

# Connection Pool Settings (optimized for distributed DB)
POOL_SETTINGS = {
    'minconn': 5,     # Increased for distributed system
    'maxconn': 20,    # More connections for parallel operations
    'keepalives': 1,
    'keepalives_idle': 30,
    'keepalives_interval': 10,
    'keepalives_count': 5
}

# Performance Settings
DISTRIBUTED_SETTINGS = {
    'enable_parallel_queries': True,
    'max_parallel_workers': 8,
    'effective_cache_size': '128GB',
    'work_mem': '512MB'
}
