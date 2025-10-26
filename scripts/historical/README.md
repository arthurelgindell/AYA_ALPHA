# Historical Scripts - One-Time Use
**Archived**: 2025-10-26  
**Status**: Completed/Obsolete

These scripts were used during initial setup and are preserved for historical reference.

## PostgreSQL Replica Setup (Obsolete)
- setup_beta_replica.sh
- setup_beta_replica_complete.sh
- setup_beta_replica_v2.sh

**Status**: Obsolete - PostgreSQL HA now managed by Patroni  
**Replaced by**: Patroni automatic configuration

## Cleanup Scripts
- cleanup_legacy_docs.sh

**Status**: Superseded by current cleanup plan  
**Alternative**: Manual consolidation with database upload

## GLADIATOR Pipeline Scripts
- launch_week2_3_pipeline.sh

**Status**: One-time use for specific week execution  
**Current**: Use GitHub Actions workflows

## Testing Scripts
- test_mcp_servers.sh

**Status**: MCP servers deployed and operational  
**Verification**: MCP_DEPLOYMENT_REPORT.md

## Current Equivalents

Instead of these scripts, use:
- PostgreSQL HA: Managed by Patroni (automatic)
- GLADIATOR execution: GitHub Actions workflows
- MCP testing: Integrated in Cursor
- Cleanup: Database-driven consolidation

**Preserved for**: Historical reference, troubleshooting patterns

