# GLADIATOR Cyber Defense Platform
## Weapon-as-a-Service with Adversarial Training

**Status**: Phase 0 - Reality Check  
**Strategy**: Option A (Quality Over Quantity)  
**Timeline**: 8 weeks to production  
**Target Date**: December 11, 2025

---

## Overview

GLADIATOR is a production-grade cyber defense platform featuring:
- **10K-50K diverse attack patterns** (modern threat focus)
- **Red/Blue adversarial training** (evolutionary defense)
- **Fractional gate control** (graduated response)
- **Air-gap deployment** (zero external dependencies)
- **Self-attack prevention** (cryptographic safeguards)

### Current Progress

**Completed**:
- ✅ Strategic pivot to Option A (quality-first)
- ✅ 3,134 high-quality attack patterns (20+ categories)
- ✅ Infrastructure validated (ALPHA/BETA Mac Studio M3 Ultra)
- ✅ Qwen3-14B model validated @ 42.5 tok/s
- ✅ Docker containers operational (blue_combat, red_combat)
- ✅ Database synchronized (aya_rag)
- ✅ GitHub Actions CI/CD ready

**In Progress**:
- ⏳ Reality Check (1,000-sample validation)
- ⏳ Pattern expansion (42K new patterns)
- ⏳ Blue Team training

---

## Quick Start

### Prerequisites
- macOS Sequoia 15.0+ (ARM64)
- Xcode Command Line Tools
- Docker Desktop
- PostgreSQL 18+
- GitHub Actions self-hosted runners (ALPHA, BETA)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/YOUR_ORG/GLADIATOR.git
cd GLADIATOR

# 2. Install runners on ALPHA and BETA
cd runners
sudo ./install-runner.sh alpha "$GITHUB_TOKEN" "$ORG_NAME" "GLADIATOR"
# On BETA:
sudo ./install-runner.sh beta "$GITHUB_TOKEN" "$ORG_NAME" "GLADIATOR"

# 3. Test runners
# GitHub UI → Actions → Runner Smoke Test → Run workflow

# 4. Execute Reality Check
# GitHub UI → Actions → GLADIATOR Reality Check → Run workflow
```

---

## Architecture

```
┌────────────────────────────────────────────────────────┐
│              GitHub Repository (GLADIATOR)              │
│                .github/workflows/*.yml                  │
└──────────────────┬─────────────────────────────────────┘
                   │
       ┌───────────▼──────────┐      ┌─────────────────┐
       │  GitHub Actions      │      │  Claude Code    │
       │  (Orchestrator)      │◄────►│  (Planner)      │
       └───────────┬──────────┘      └────────┬────────┘
                   │                           │
         ┌─────────┴─────────┐                 │
         │                   │                 │
    ┌────▼────┐         ┌────▼────┐            │
    │ ALPHA   │         │  BETA   │            │
    │ Runner  │         │ Runner  │            │
    │ (Blue)  │         │ (Red)   │            │
    └────┬────┘         └────┬────┘            │
         │                   │                 │
         └─────────┬─────────┘                 │
                   │                           │
            ┌──────▼────────┐                  │
            │   aya_rag     │◄─────────────────┘
            │   Database    │
            │  (Postgres)   │
            └───────────────┘
```

### Hardware

**ALPHA** (Blue Team):
- Mac Studio M3 Ultra
- 512GB RAM (verified)
- 4TB NVMe SSD
- Docker: blue_combat
- Purpose: Model training, validation

**BETA** (Red Team):
- Mac Studio M3 Ultra
- 512GB RAM (verified)
- 4TB + 16TB Thunderbolt SSD
- Docker: red_combat
- LM Studio: Qwen3-14B @ 42.5 tok/s
- Purpose: Attack pattern generation

---

## Workflows

### Reality Check
**Trigger**: Manual (workflow_dispatch) or scheduled (daily)  
**Duration**: 12-24 hours  
**Purpose**: Validate fine-tuning approach on 1,000-sample test

**Steps**:
1. Generate 1,000-pattern dataset (BETA)
2. Transfer to ALPHA
3. Fine-tune Foundation-Sec-8B (100 steps)
4. Validate accuracy (≥90% target)
5. GO/NO-GO decision

### Pattern Generation
**Trigger**: Manual with parameters (category, count)  
**Duration**: 1-6 hours  
**Purpose**: Generate attack patterns for specific threat categories

**Categories**:
- Supply chain attacks
- API exploitation
- Container/cloud escape
- APT campaigns
- Zero-trust bypass
- AI/ML attacks
- Traditional web (XSS, CSRF)

### Health Check
**Trigger**: Scheduled (daily at 8 AM)  
**Duration**: 5 minutes  
**Purpose**: Monitor system resources, Docker status, database connectivity

---

## Documentation

- **Master Architecture**: [`docs/GLADIATOR_MASTER_ARCHITECTURE_v2.4.md`](docs/GLADIATOR_MASTER_ARCHITECTURE_v2.4.md)
- **Execution Plan**: [`docs/GLADIATOR_EXECUTION_PLAN_v2.3.md`](docs/GLADIATOR_EXECUTION_PLAN_v2.3.md)
- **Test Plan**: [`docs/GLADIATOR_INFRASTRUCTURE_TEST_PLAN_v2.3.md`](docs/GLADIATOR_INFRASTRUCTURE_TEST_PLAN_v2.3.md)
- **Mission Briefing**: [`docs/GLADIATOR_MISSION_BRIEFING.md`](docs/GLADIATOR_MISSION_BRIEFING.md)
- **Workflow Summary**: [`docs/WORKFLOW_SUMMARY.md`](docs/WORKFLOW_SUMMARY.md)
- **Agent Turbo Integration**: [`docs/AGENT_TURBO_INTEGRATION.md`](docs/AGENT_TURBO_INTEGRATION.md)

---

## Project Structure

```
GLADIATOR/
├── .github/
│   └── workflows/           # GitHub Actions workflows
├── docs/                    # Documentation
├── scripts/                 # Training and generation scripts
├── config/                  # Configuration files
│   ├── alpha/              # ALPHA-specific configs
│   └── beta/               # BETA-specific configs
├── docker/                  # Docker container definitions
│   ├── blue_combat/        # Blue Team container
│   └── red_combat/         # Red Team container
├── runners/                 # Self-hosted runner setup
│   ├── install-runner.sh   # Runner installer
│   └── launchd/            # macOS service configs
├── agent-turbo/            # Agent Turbo integration
│   └── integration/        # Integration scripts
├── .gitignore
├── README.md
└── LICENSE
```

---

## Strategic Pivot: Option A

**Decision Date**: October 16, 2025  
**Decision Maker**: Arthur (Executive CTO)

### Old Strategy (v2.3)
- 10M SQL injection variants
- 6-month timeline
- Quantity-focused

### New Strategy (v2.4 - Option A)
- 10K-50K diverse patterns
- 8-week timeline
- Quality-focused
- Modern threat alignment

### Rationale
1. **Modern Threats**: SQL injection <5% of breaches, supply chain attacks 45%
2. **ML Best Practice**: Quality > quantity after 10K-50K diverse samples
3. **Timeline**: 5-6 months faster to production
4. **Evidence**: 3,134 existing patterns show 21% phishing, 21% XSS, 21% buffer overflow, only 1.8% SQL

**Result**: ✅ Approved, database updated, documentation synchronized

---

## Timeline

**Week 0** (October 16-22): Reality Check
- Generate 1,000-sample dataset
- Fine-tune Foundation-Sec-8B
- Validate ≥90% accuracy
- GO/NO-GO decision

**Week 1-4**: Pattern Expansion + Blue Team Training
- Generate 42K new patterns (modern threats)
- Fine-tune on 45K total patterns
- Target: ≥98% accuracy

**Week 5-7**: Knowledge Distillation
- Distill 8B → 1.5B model
- Quantize to 4-bit MLX
- Target: <500MB, ≥93% accuracy

**Week 8** (December 9-11): Production Validation
- Gauntlet test (100K samples)
- Final GO/NO-GO
- **Production Ready**: December 11, 2025 ✅

---

## Security

### Hardening Applied
- ✅ Repository restrictions (GLADIATOR repo only)
- ✅ Fork PR protection (no untrusted code)
- ✅ Action pinning (SHA-locked dependencies)
- ✅ Read-only tokens (escalate per-job)
- ✅ Work directory cleanup (periodic purge)
- ✅ Non-admin runner user
- ✅ Cryptographic self-attack prevention

### Compliance
- Air-gap capable deployment
- No external API dependencies for inference
- Complete audit trail (aya_rag database)
- Encrypted model packaging

---

## Monitoring

### Real-Time (GitHub Actions UI)
- Workflow runs: Actions tab
- Live logs: Step-by-step execution
- Artifacts: Download models, datasets, results

### Historical (aya_rag Database)
```sql
-- Get last 10 Reality Check runs
SELECT 
    github_run_id,
    status,
    start_time,
    end_time
FROM agent_sessions
WHERE context->>'workflow' = 'GLADIATOR Reality Check'
ORDER BY start_time DESC
LIMIT 10;
```

### Metrics
- Training accuracy trends
- Pattern generation rate
- Model performance over time
- System resource utilization

---

## Contributing

**Internal project** - Not open for external contributions.

For team members:
1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and commit
3. Push and create PR: `git push origin feature/your-feature`
4. Request review from Arthur
5. Merge after approval

---

## Support

**Documentation**: See `docs/` directory  
**Issues**: GitHub Issues tab  
**Contact**: Arthur (Executive CTO)

**Troubleshooting**:
1. Check runner logs: `/Users/runner/actions-runner/runner.*.log`
2. Check database: `psql aya_rag -c "SELECT * FROM agent_sessions ORDER BY start_time DESC LIMIT 5"`
3. Check GitHub Actions status: https://www.githubstatus.com/

---

## License

**Internal Use Only**  
Not for redistribution.

All rights reserved. © 2025

---

## Acknowledgments

- **Agent Turbo**: Multi-agent orchestration framework
- **LM Studio**: Local LLM runtime
- **MLX**: Apple Silicon optimization framework
- **PostgreSQL**: Database backend

---

**Version**: 2.4  
**Last Updated**: October 16, 2025  
**Status**: Production Ready - Phase 0 Execution
