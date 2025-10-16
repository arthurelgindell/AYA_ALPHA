#!/bin/bash
# Configure Docker Desktop for 200GB on both systems
# NOTE: This requires manual GUI action - providing instructions

cat << 'EOF'
======================================================================
DOCKER RESOURCE CONFIGURATION - MANUAL STEPS REQUIRED
======================================================================

ALPHA (Current system):
1. Open Docker Desktop application
2. Settings (gear icon) → Resources
3. Change Memory: 200GB (from current 7.65GB)
4. Change CPUs: 12 (if not already set)
5. Change Disk: 100GB
6. Click "Apply & Restart"
7. Wait ~2 minutes for Docker to restart

BETA (via remote):
1. Access BETA system
2. Open Docker Desktop application  
3. Settings → Resources
4. Change Memory: 200GB
5. Change CPUs: 12
6. Change Disk: 100GB
7. Apply & Restart

After configuration:
- Run: docker info | grep "Total Memory"
- Should show: ~200GB

Then: Ready to build combat containers
======================================================================

These settings enable 200GB RAM per container (symmetric allocation).
Required for combat-ready Red vs Blue testing with full models.

Manual configuration needed (Docker Desktop GUI-based).
EOF
