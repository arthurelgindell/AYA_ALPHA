# ALPHA AGENT_TURBO Configuration
ALPHA_SYSTEM = True
ALPHA_IP = "100.106.170.128"
BETA_IP = "100.84.202.68"
RAM_DISK_PATH = "/Volumes/DATA/Agent_RAM"
AGENT_TURBO_PATH = "/Volumes/DATA/Agent_Turbo"
LM_STUDIO_URL = "http://localhost:1234/v1"

# PostgreSQL Database (Single Source of Truth)
POSTGRES_HOST = "localhost"  # ALPHA is primary
POSTGRES_DB = "aya_rag"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "Power$$336633$$"

# System Role
SYSTEM_ROLE = "PRIMARY"  # ALPHA is primary, BETA is replica

# Performance Settings
GPU_ACCELERATION = True  # Enable if Apple Silicon available
MAX_CACHE_SIZE_MB = 100 * 1024  # 100GB RAM disk
FLUSH_INTERVAL_SECONDS = 120

# LM Studio Settings
LM_STUDIO_MODEL = "qwen/qwen3-next-80b"  # Adjust based on ALPHA's model
LM_STUDIO_TIMEOUT = 30

# Agent Turbo Database (Local Cache)
# Uses ~/.agent_turbo/agent_turbo.db (portable, user home)
# This is separate from PostgreSQL - used for performance caching only

