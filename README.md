# AYA
## AI Orchestration & Execution Platform

**Primary System**: Agent Turbo (Multi-agent orchestration)  
**Database**: PostgreSQL `aya_rag` (Centralized state & audit trail)  
**Infrastructure**: ALPHA/BETA Mac Studio M3 Ultra  
**Automation**: GitHub Actions self-hosted runners

---

## Overview

AYA is a production AI orchestration platform featuring:
- **Agent Turbo**: Multi-agent task planning, delegation, and auditing
- **PostgreSQL Backend**: Centralized state management and audit trail
- **GitHub Actions CI/CD**: Automated workflows on self-hosted runners
- **Project Management**: GLADIATOR and other AI subsystems

### Architecture

```
AYA Platform
│
├── Agent_Turbo/              ← Core orchestration system
│   ├── core/                 ├─ Claude Code (planner/auditor)
│   │   ├── claude_planner.py
│   │   ├── agent_orchestrator.py
│   │   └── postgres_connector.py
│   └── AGENT_INTEGRATION_GUIDE.md
│
├── projects/
│   └── GLADIATOR/            ← Cyber defense project
│       ├── docs/
│       ├── scripts/
│       └── docker/
│
├── .github/workflows/        ← GitHub Actions automation
│   ├── reality-check.yml
│   └── runner-smoke.yml
│
├── Databases/                ← Knowledge bases
├── models/                   ← Local LLMs
└── services/                 ← Supporting services
```

---

## Infrastructure

### Hardware
- **ALPHA**: Mac Studio M3 Ultra (512GB RAM, Blue Team training)
- **BETA**: Mac Studio M3 Ultra (256GB RAM, 16TB SSD, Red Team generation)
- **AIR**: MacBook Air M4 (Monitoring, secondary)

### Software
- PostgreSQL 18.0 (`aya_rag` database)
- Docker (blue_combat, red_combat containers)
- LM Studio (Qwen3-14B, llama-3.3-70b)
- GitHub Actions (self-hosted runners)

### Network
- Tailscale mesh network (ALPHA ↔ BETA)
- 10GbE Ethernet (upgrade pending)
- Air-gap capability for production deployment

---

## Quick Start

### Prerequisites
- macOS Sequoia 15.0+ (ARM64)
- PostgreSQL 18+
- Docker Desktop
- GitHub account with repository access

### Setup

```bash
# Clone repository
git clone git@github.com:arthurelgindell/AYA.git
cd AYA

# Initialize Agent Turbo
cd Agent_Turbo/core
python3 agent_launcher.py

# Connect to database
psql aya_rag
```

---

## Projects

### GLADIATOR (Active)
**Path**: `projects/GLADIATOR/`  
**Status**: Phase 0 - Reality Check  
**Timeline**: 8 weeks to production (December 11, 2025)

Weapon-as-a-service cyber defense platform with:
- 3,134 high-quality attack patterns (verified)
- Red/Blue adversarial training
- Option A strategy (quality over quantity)
- Self-hosted GitHub Actions automation

**Documentation**: `projects/GLADIATOR/docs/GLADIATOR_MASTER_ARCHITECTURE_v2.4.md`

---

## GitHub Actions

### Self-Hosted Runners

**ALPHA** (alpha-m3-ultra):
- Labels: `[self-hosted, macOS, arm64, alpha, studio]`
- Status: ✅ Operational (smoke test passed)
- Purpose: Blue Team training, model validation

**BETA** (beta-m3-ultra):
- Labels: `[self-hosted, macOS, arm64, beta, studio]`
- Status: ✅ Operational (smoke test passed)  
- Purpose: Red Team generation, LLM inference

### Workflows

1. **GLADIATOR Reality Check**: Validate training approach (12-24h)
2. **Runner Smoke Test**: Verify runner health (2min)

**Trigger**: https://github.com/arthurelgindell/AYA/actions

---

## Agent Turbo

### Core Components

- **Claude Code** (Planner/Auditor): High-level planning and result verification
- **Specialized Agents**: Task execution (ALPHA, BETA runners)
- **PostgreSQL Backend**: State management, audit trail

### Database Tables

```sql
agent_sessions       -- Workflow runs, planning sessions
agent_tasks          -- Individual tasks within sessions
agent_actions        -- Step-by-step action log
agent_artifacts      -- Output files, models, datasets
gladiator_*          -- Project-specific tables
```

### Integration

Workflows automatically log to `aya_rag` database for complete audit trail and coordination.

---

## Documentation

- **Agent Turbo**: `Agent_Turbo/AGENT_INTEGRATION_GUIDE.md`
- **GLADIATOR**: `projects/GLADIATOR/docs/`
- **Workflows**: `.github/workflows/`
- **Database Schema**: `aya_schema_implementation.sql`

---

## Development

### Directory Structure
```
AYA/
├── Agent_Turbo/              Production orchestration system
├── projects/
│   └── GLADIATOR/            Cyber defense project
├── .github/workflows/        GitHub Actions automation
├── Databases/                Knowledge bases & crawlers
├── models/                   Local LLM models
├── services/                 Supporting services
└── archive_legacy_docs/      Historical documentation
```

### Contributing

Internal project. For team collaboration:
1. Create feature branch
2. Make changes
3. Create PR
4. Review and merge

---

## Monitoring

### Real-Time
- **GitHub Actions**: https://github.com/arthurelgindell/AYA/actions
- **Runner Logs**: `/Users/runner/actions-runner/runner.out.log`

### Historical
```sql
-- Recent workflow runs
SELECT * FROM agent_sessions 
WHERE context->>'repository' = 'AYA' 
ORDER BY start_time DESC LIMIT 10;

-- GLADIATOR progress
SELECT * FROM gladiator_project_state WHERE is_current = true;
```

---

## Status

**AYA Platform**: Production Ready ✅  
**Agent Turbo**: Operational  
**GLADIATOR**: Phase 0 - Reality Check ready  
**GitHub Actions**: ALPHA & BETA runners operational  
**Database**: aya_rag synchronized

**Next**: Execute GLADIATOR Reality Check workflow

---

## License

Internal Use Only  
© 2025 Arthur Dell

---

## Contact

**Owner**: Arthur Dell  
**Email**: arthur@dellight.ai  
**System**: ALPHA (alpha.tail5f2bae.ts.net)

---

**Version**: 1.0  
**Last Updated**: October 17, 2025  
**Status**: Production Orchestration Platform

