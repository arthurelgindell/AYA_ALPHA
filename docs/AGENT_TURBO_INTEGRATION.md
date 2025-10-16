# GitHub Actions + Agent Turbo Integration
## Automated Workflows with Database Orchestration

**Date**: October 16, 2025  
**Status**: Production Ready  
**Integration**: GitHub Actions (ALPHA/BETA) ↔ Agent Turbo (aya_rag)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     GitHub Repository                            │
│  .github/workflows/*.yml                                         │
└────────────┬────────────────────────────────────────────────────┘
             │
             │ Workflow Trigger (push, PR, schedule, manual)
             │
     ┌───────▼────────┐              ┌───────────────┐
     │ GitHub Actions │              │ Claude Code   │
     │  Dispatcher    │◄────────────►│  (Planner)    │
     └───────┬────────┘              └───────┬───────┘
             │                               │
             │                               │ Planning
             │ Job Assignment                │ & Audit
             │                               │
     ┌───────▼────────┐              ┌───────▼───────┐
     │ ALPHA Runner   │              │  aya_rag DB   │
     │ [self-hosted,  │◄────────────►│  (Postgres)   │
     │  alpha, studio]│              │               │
     └────────────────┘              │ - Sessions    │
                                     │ - Tasks       │
     ┌────────────────┐              │ - Actions     │
     │ BETA Runner    │              │ - Audit Trail │
     │ [self-hosted,  │◄────────────►│ - Results     │
     │  beta, studio] │              └───────────────┘
     └────────────────┘

Flow:
1. Workflow triggered → GitHub Actions dispatcher
2. Job routed to ALPHA/BETA runner based on labels
3. Runner executes steps, logs to aya_rag database
4. Claude Code audits results via database queries
5. Next tasks delegated based on success/failure
```

---

## Core Concepts

### 1. Agent Turbo Orchestration

**Database Tables** (aya_rag):
- `agent_sessions`: Track workflow runs as sessions
- `agent_tasks`: Individual jobs/tasks
- `agent_actions`: Step-by-step actions within tasks
- `agent_artifacts`: Output files, logs, models
- `agent_audit_log`: Complete audit trail

**Key Principles**:
- Every GitHub Actions run = Agent Turbo session
- Every job = Agent Turbo task
- Every step = Agent Turbo action
- Claude Code = Planner & Auditor
- Specialized agents (ALPHA/BETA) = Executors

### 2. GitHub Actions Self-Hosted Runners

**ALPHA** (Blue Team Training):
- Labels: `[self-hosted, macOS, arm64, alpha, studio]`
- Purpose: Model fine-tuning, validation, distillation
- Resources: 192GB RAM, 4TB SSD, M3 Ultra
- Database role: Executor (Blue Team tasks)

**BETA** (Red Team Generation):
- Labels: `[self-hosted, macOS, arm64, beta, studio]`
- Purpose: Attack pattern generation, LLM inference
- Resources: 192GB RAM, 4TB + 16TB SSD, M3 Ultra
- Database role: Executor (Red Team tasks)

### 3. Integration Pattern

```python
# Workflow Step → Database Logging
name: "Fine-tune Model"
run: |
  # 1. Log task start to aya_rag
  python3 log_task.py --action start --task "blue_team_finetune"
  
  # 2. Execute training
  python3 train.py --config config.yml
  
  # 3. Log completion + artifacts
  python3 log_task.py --action complete \
    --task "blue_team_finetune" \
    --artifacts "model.pth,metrics.json" \
    --result "success"
```

---

## Workflow Examples

### Example 1: GLADIATOR Reality Check (Automated)

**File**: `.github/workflows/gladiator-reality-check.yml`

```yaml
name: GLADIATOR Reality Check

on:
  workflow_dispatch:
    inputs:
      sample_size:
        description: 'Number of patterns to sample'
        required: true
        default: '1000'
  schedule:
    # Run daily at 2 AM
    - cron: '0 2 * * *'

permissions:
  contents: read

env:
  POSTGRES_HOST: localhost
  POSTGRES_DB: aya_rag
  POSTGRES_USER: arthur

jobs:
  # ============================================================================
  # PLANNING PHASE (Claude Code)
  # ============================================================================
  plan:
    name: Planning Session
    runs-on: ubuntu-latest
    outputs:
      session_id: ${{ steps.init.outputs.session_id }}
      task_ids: ${{ steps.init.outputs.task_ids }}
    
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
      
      - name: Initialize Agent Turbo Session
        id: init
        run: |
          # Create planning session in aya_rag
          python3 << 'EOF'
          import sys
          sys.path.insert(0, 'Agent_Turbo/core')
          from claude_planner import ClaudePlanner
          
          planner = ClaudePlanner()
          session_id = planner.start_planning_session(
              task_type="gladiator_reality_check",
              context={
                  "sample_size": ${{ github.event.inputs.sample_size }},
                  "trigger": "${{ github.event_name }}",
                  "run_id": "${{ github.run_id }}"
              }
          )
          
          # Create delegated tasks
          tasks = {
              "generate_dataset": planner.create_delegated_task(
                  session_id=session_id,
                  task_name="Generate Reality Check Dataset",
                  assigned_agent="BETA",
                  priority="critical"
              ),
              "transfer_dataset": planner.create_delegated_task(
                  session_id=session_id,
                  task_name="Transfer Dataset to ALPHA",
                  assigned_agent="BETA→ALPHA",
                  priority="critical"
              ),
              "finetune": planner.create_delegated_task(
                  session_id=session_id,
                  task_name="Fine-tune Foundation Model",
                  assigned_agent="ALPHA",
                  priority="critical"
              ),
              "validate": planner.create_delegated_task(
                  session_id=session_id,
                  task_name="Validate Model Performance",
                  assigned_agent="ALPHA",
                  priority="critical"
              )
          }
          
          print(f"session_id={session_id}")
          print(f"task_ids={','.join(map(str, tasks.values()))}")
          EOF

  # ============================================================================
  # EXECUTION PHASE - BETA (Red Team)
  # ============================================================================
  generate-dataset:
    name: Generate Dataset (BETA)
    runs-on: [self-hosted, macOS, arm64, beta, studio]
    needs: plan
    timeout-minutes: 180
    
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11
      
      - name: Log Task Start
        run: |
          python3 Agent_Turbo/core/task_logger.py \
            --session ${{ needs.plan.outputs.session_id }} \
            --task generate_dataset \
            --status started
      
      - name: Generate Reality Check Dataset
        id: generate
        run: |
          cd /Volumes/DATA/GLADIATOR
          
          # Run generation script (from BETA container)
          docker exec red_combat python3 << 'PYEOF'
          import json
          import random
          from pathlib import Path
          
          # Load existing patterns
          pattern_dir = Path("/gladiator/data/attack_patterns/iteration_001")
          patterns = []
          for f in sorted(pattern_dir.glob("attack_*.json"))[:3134]:
              with open(f) as fp:
                  patterns.append(json.load(fp))
          
          # Stratified sampling
          sample = random.sample(patterns, ${{ github.event.inputs.sample_size }})
          
          # Save dataset
          output = {
              "metadata": {
                  "sample_size": len(sample),
                  "source": "iteration_001",
                  "generated_by": "github-actions"
              },
              "patterns": sample
          }
          
          with open("/gladiator/data/reality_check_${{ github.event.inputs.sample_size }}.json", "w") as f:
              json.dump(output, f, indent=2)
          
          print(f"Generated {len(sample)} patterns")
          PYEOF
          
          echo "dataset_path=/Volumes/DATA/GLADIATOR/reality_check_${{ github.event.inputs.sample_size }}.json" >> $GITHUB_OUTPUT
      
      - name: Verify Dataset
        run: |
          FILE="${{ steps.generate.outputs.dataset_path }}"
          if [[ -f "$FILE" ]]; then
            SIZE=$(stat -f%z "$FILE")
            PATTERNS=$(jq '.patterns | length' "$FILE")
            echo "✅ Dataset created: $FILE"
            echo "   Size: $SIZE bytes"
            echo "   Patterns: $PATTERNS"
          else
            echo "❌ Dataset generation failed!"
            exit 1
          fi
      
      - name: Log Task Complete
        if: always()
        run: |
          python3 Agent_Turbo/core/task_logger.py \
            --session ${{ needs.plan.outputs.session_id }} \
            --task generate_dataset \
            --status ${{ job.status }} \
            --artifact "${{ steps.generate.outputs.dataset_path }}"

  # ============================================================================
  # DATA TRANSFER - BETA → ALPHA
  # ============================================================================
  transfer-dataset:
    name: Transfer to ALPHA
    runs-on: [self-hosted, macOS, arm64, beta, studio]
    needs: [plan, generate-dataset]
    timeout-minutes: 30
    
    steps:
      - name: Log Task Start
        run: |
          python3 Agent_Turbo/core/task_logger.py \
            --session ${{ needs.plan.outputs.session_id }} \
            --task transfer_dataset \
            --status started
      
      - name: Transfer via rsync
        run: |
          DATASET="/Volumes/DATA/GLADIATOR/reality_check_${{ github.event.inputs.sample_size }}.json"
          
          rsync -avz --progress \
            "$DATASET" \
            alpha.local:/Users/arthurdell/GLADIATOR/datasets/
          
          # Verify transfer
          ssh alpha.local "ls -lh /Users/arthurdell/GLADIATOR/datasets/reality_check_*.json"
      
      - name: Log Task Complete
        if: always()
        run: |
          python3 Agent_Turbo/core/task_logger.py \
            --session ${{ needs.plan.outputs.session_id }} \
            --task transfer_dataset \
            --status ${{ job.status }}

  # ============================================================================
  # EXECUTION PHASE - ALPHA (Blue Team)
  # ============================================================================
  finetune-model:
    name: Fine-tune Model (ALPHA)
    runs-on: [self-hosted, macOS, arm64, alpha, studio]
    needs: [plan, transfer-dataset]
    timeout-minutes: 1440  # 24 hours
    
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11
      
      - name: Log Task Start
        run: |
          python3 Agent_Turbo/core/task_logger.py \
            --session ${{ needs.plan.outputs.session_id }} \
            --task finetune \
            --status started
      
      - name: Prepare Training Data
        run: |
          cd /Users/arthurdell/GLADIATOR
          
          docker exec blue_combat python3 << 'PYEOF'
          import json
          from pathlib import Path
          
          # Load reality check dataset
          with open("/gladiator/datasets/reality_check_${{ github.event.inputs.sample_size }}.json") as f:
              data = json.load(f)
          
          patterns = data["patterns"]
          
          # Split 90/10
          train_size = int(len(patterns) * 0.9)
          train_set = patterns[:train_size]
          val_set = patterns[train_size:]
          
          # Save as JSONL
          with open("/gladiator/datasets/reality_check_train.jsonl", "w") as f:
              for p in train_set:
                  json.dump(p, f)
                  f.write("\n")
          
          with open("/gladiator/datasets/reality_check_val.jsonl", "w") as f:
              for p in val_set:
                  json.dump(p, f)
                  f.write("\n")
          
          print(f"Train: {len(train_set)}, Val: {len(val_set)}")
          PYEOF
      
      - name: Fine-tune Foundation Model
        id: train
        run: |
          docker exec blue_combat python3 /gladiator/scripts/finetune_foundation.py \
            --train /gladiator/datasets/reality_check_train.jsonl \
            --val /gladiator/datasets/reality_check_val.jsonl \
            --steps 100 \
            --checkpoint-every 50 \
            --output /gladiator/models/reality_check_model
      
      - name: Upload Model Artifact
        uses: actions/upload-artifact@v4
        with:
          name: reality-check-model
          path: /Users/arthurdell/GLADIATOR/models/reality_check_model/
          retention-days: 7
      
      - name: Log Task Complete
        if: always()
        run: |
          python3 Agent_Turbo/core/task_logger.py \
            --session ${{ needs.plan.outputs.session_id }} \
            --task finetune \
            --status ${{ job.status }} \
            --artifact "reality_check_model"

  # ============================================================================
  # VALIDATION PHASE - ALPHA
  # ============================================================================
  validate-model:
    name: Validate Model (ALPHA)
    runs-on: [self-hosted, macOS, arm64, alpha, studio]
    needs: [plan, finetune-model]
    timeout-minutes: 60
    
    outputs:
      accuracy: ${{ steps.test.outputs.accuracy }}
      go_decision: ${{ steps.decide.outputs.decision }}
    
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11
      
      - name: Log Task Start
        run: |
          python3 Agent_Turbo/core/task_logger.py \
            --session ${{ needs.plan.outputs.session_id }} \
            --task validate \
            --status started
      
      - name: Run Validation Test
        id: test
        run: |
          docker exec blue_combat python3 /gladiator/scripts/validate_model.py \
            --model /gladiator/models/reality_check_model \
            --test /gladiator/datasets/reality_check_val.jsonl \
            --output /gladiator/results/validation_results.json
          
          # Extract accuracy
          ACCURACY=$(docker exec blue_combat jq '.accuracy' /gladiator/results/validation_results.json)
          echo "accuracy=$ACCURACY" >> $GITHUB_OUTPUT
          echo "Validation Accuracy: $ACCURACY%"
      
      - name: GO/NO-GO Decision
        id: decide
        run: |
          ACCURACY=${{ steps.test.outputs.accuracy }}
          THRESHOLD=90.0
          
          if (( $(echo "$ACCURACY >= $THRESHOLD" | bc -l) )); then
            echo "decision=GO" >> $GITHUB_OUTPUT
            echo "✅ GO: Accuracy ${ACCURACY}% >= ${THRESHOLD}%"
          else
            echo "decision=NO-GO" >> $GITHUB_OUTPUT
            echo "❌ NO-GO: Accuracy ${ACCURACY}% < ${THRESHOLD}%"
            exit 1
          fi
      
      - name: Upload Results
        uses: actions/upload-artifact@v4
        with:
          name: validation-results
          path: /Users/arthurdell/GLADIATOR/results/validation_results.json
      
      - name: Log Task Complete
        if: always()
        run: |
          python3 Agent_Turbo/core/task_logger.py \
            --session ${{ needs.plan.outputs.session_id }} \
            --task validate \
            --status ${{ job.status }} \
            --result "accuracy=${{ steps.test.outputs.accuracy }},decision=${{ steps.decide.outputs.decision }}"

  # ============================================================================
  # AUDIT PHASE (Claude Code)
  # ============================================================================
  audit:
    name: Audit Results
    runs-on: ubuntu-latest
    needs: [plan, validate-model]
    if: always()
    
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11
      
      - name: Audit Task Results
        run: |
          python3 << 'EOF'
          import sys
          sys.path.insert(0, 'Agent_Turbo/core')
          from claude_planner import ClaudePlanner
          
          planner = ClaudePlanner()
          
          # Audit all tasks in session
          session_id = "${{ needs.plan.outputs.session_id }}"
          
          audit_results = planner.audit_task_results(
              session_id=session_id,
              expected_outcomes={
                  "generate_dataset": "Dataset created with ${{ github.event.inputs.sample_size }} patterns",
                  "transfer_dataset": "Dataset transferred to ALPHA",
                  "finetune": "Model fine-tuned successfully",
                  "validate": "Validation accuracy >= 90%"
              }
          )
          
          # Generate summary
          summary = planner.get_planning_session_summary(session_id)
          
          print("=" * 80)
          print("AUDIT RESULTS")
          print("=" * 80)
          print(f"Session: {session_id}")
          print(f"Status: {summary['status']}")
          print(f"Tasks Completed: {summary['completed_tasks']}/{summary['total_tasks']}")
          print(f"Accuracy: ${{ needs.validate-model.outputs.accuracy }}%")
          print(f"Decision: ${{ needs.validate-model.outputs.go_decision }}")
          print("=" * 80)
          
          # Log to database
          planner.log_audit_result(
              session_id=session_id,
              audit_status="completed",
              findings=audit_results,
              recommendations=["Proceed to full Blue Team training" if "${{ needs.validate-model.outputs.go_decision }}" == "GO" else "Debug and retest"]
          )
          EOF
      
      - name: Post Summary to PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const summary = `
            ## GLADIATOR Reality Check Results
            
            **Session**: \`${{ needs.plan.outputs.session_id }}\`
            **Accuracy**: ${{ needs.validate-model.outputs.accuracy }}%
            **Decision**: **${{ needs.validate-model.outputs.go_decision }}**
            
            ### Tasks
            - ✅ Generate Dataset (BETA)
            - ✅ Transfer Dataset (BETA → ALPHA)
            - ✅ Fine-tune Model (ALPHA)
            - ✅ Validate Model (ALPHA)
            
            ### Next Steps
            ${{ needs.validate-model.outputs.go_decision == 'GO' && '✅ Proceed to full Blue Team training' || '❌ Debug and retest Reality Check' }}
            `;
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: summary
            });
```

---

### Example 2: Automated Attack Pattern Generation

**File**: `.github/workflows/gladiator-pattern-generation.yml`

```yaml
name: GLADIATOR Pattern Generation

on:
  workflow_dispatch:
    inputs:
      category:
        description: 'Attack category'
        required: true
        type: choice
        options:
          - supply_chain
          - api_exploitation
          - container_escape
          - apt_campaign
          - zero_trust_bypass
      count:
        description: 'Number of patterns'
        required: true
        default: '1000'

permissions:
  contents: write

jobs:
  generate:
    name: Generate Patterns (BETA)
    runs-on: [self-hosted, macOS, arm64, beta, studio]
    timeout-minutes: 360
    
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11
      
      - name: Log to Agent Turbo
        run: |
          python3 << 'EOF'
          import sys
          sys.path.insert(0, 'Agent_Turbo/core')
          from agent_orchestrator import AgentOrchestrator
          
          orchestrator = AgentOrchestrator()
          session_id = orchestrator.initialize_agent_session(
              agent_name="BETA",
              agent_type="pattern_generator",
              task_description=f"Generate ${{ github.event.inputs.count }} ${{ github.event.inputs.category }} patterns"
          )
          
          print(f"SESSION_ID={session_id}")
          EOF
      
      - name: Generate Attack Patterns
        run: |
          docker exec red_combat python3 /gladiator/data/scripts/generate_patterns.py \
            --category ${{ github.event.inputs.category }} \
            --count ${{ github.event.inputs.count }} \
            --output /gladiator/data/attack_patterns/${{ github.event.inputs.category }}
      
      - name: Commit New Patterns
        run: |
          cd /Volumes/DATA/GLADIATOR
          git add attack_patterns/${{ github.event.inputs.category }}
          git commit -m "Add ${{ github.event.inputs.count }} ${{ github.event.inputs.category }} patterns"
          git push origin main
```

---

### Example 3: Daily Health Check

**File**: `.github/workflows/gladiator-health-check.yml`

```yaml
name: GLADIATOR Health Check

on:
  schedule:
    - cron: '0 8 * * *'  # Daily at 8 AM
  workflow_dispatch:

jobs:
  health-alpha:
    name: Health Check (ALPHA)
    runs-on: [self-hosted, macOS, arm64, alpha, studio]
    
    steps:
      - name: System Resources
        run: |
          echo "CPU Usage:"
          top -l 1 -s 0 | grep "CPU usage"
          echo ""
          echo "Memory Usage:"
          vm_stat | perl -ne '/page size of (\d+)/ and $size=$1; /Pages\s+([^:]+)[^\d]+(\d+)/ and printf("%-16s % 16.2f Mi\n", "$1:", $2 * $size / 1048576);'
          echo ""
          echo "Disk Space:"
          df -h /
      
      - name: Docker Status
        run: |
          docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Size}}'
          echo ""
          docker exec blue_combat df -h /gladiator
      
      - name: Database Connectivity
        run: |
          python3 -c "
          import sys
          sys.path.insert(0, '/Users/arthurdell/AYA/Agent_Turbo/core')
          from postgres_connector import PostgreSQLConnector
          db = PostgreSQLConnector()
          result = db.execute_query('SELECT COUNT(*) FROM agent_sessions', fetch=True)
          print(f'✅ Database connected: {result[0][\"count\"]} sessions')
          db.close_all_connections()
          "

  health-beta:
    name: Health Check (BETA)
    runs-on: [self-hosted, macOS, arm64, beta, studio]
    
    steps:
      - name: System Resources
        run: |
          echo "CPU Usage:"
          top -l 1 -s 0 | grep "CPU usage"
          echo ""
          echo "Memory Usage:"
          vm_stat | perl -ne '/page size of (\d+)/ and $size=$1; /Pages\s+([^:]+)[^\d]+(\d+)/ and printf("%-16s % 16.2f Mi\n", "$1:", $2 * $size / 1048576);'
          echo ""
          echo "Disk Space:"
          df -h /Volumes/DATA
      
      - name: Docker Status
        run: |
          docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Size}}'
          echo ""
          docker exec red_combat df -h /gladiator/data
      
      - name: LM Studio Status
        run: |
          curl -s http://localhost:1234/v1/models | jq '.data[] | {id, object}'
      
      - name: Pattern Count
        run: |
          PATTERN_COUNT=$(docker exec red_combat find /gladiator/data/attack_patterns -name "*.json" -type f | wc -l)
          echo "Total attack patterns: $PATTERN_COUNT"
```

---

## Database Schema Integration

### Agent Turbo Tables Used

```sql
-- Sessions (GitHub workflow runs)
CREATE TABLE agent_sessions (
    session_id UUID PRIMARY KEY,
    session_type VARCHAR(50),  -- 'github_actions', 'manual', 'scheduled'
    agent_name VARCHAR(100),   -- 'ALPHA', 'BETA', 'Claude Code'
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status VARCHAR(20),
    context JSONB,             -- GitHub run metadata
    github_run_id VARCHAR(50),
    github_workflow VARCHAR(100)
);

-- Tasks (GitHub jobs)
CREATE TABLE agent_tasks (
    task_id UUID PRIMARY KEY,
    session_id UUID REFERENCES agent_sessions(session_id),
    task_name VARCHAR(200),
    assigned_agent VARCHAR(100),
    priority VARCHAR(20),
    status VARCHAR(20),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    result JSONB,
    github_job_name VARCHAR(100)
);

-- Actions (GitHub steps)
CREATE TABLE agent_actions (
    action_id UUID PRIMARY KEY,
    task_id UUID REFERENCES agent_tasks(task_id),
    action_type VARCHAR(100),
    action_description TEXT,
    status VARCHAR(20),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    output TEXT,
    github_step_name VARCHAR(100)
);

-- Artifacts (Models, datasets, logs)
CREATE TABLE agent_artifacts (
    artifact_id UUID PRIMARY KEY,
    session_id UUID REFERENCES agent_sessions(session_id),
    task_id UUID REFERENCES agent_tasks(task_id),
    artifact_type VARCHAR(50),  -- 'model', 'dataset', 'log', 'report'
    artifact_name VARCHAR(200),
    file_path TEXT,
    file_size_bytes BIGINT,
    checksum VARCHAR(64),
    created_at TIMESTAMP,
    metadata JSONB
);
```

### Query Examples

```sql
-- Get all GLADIATOR Reality Check runs
SELECT 
    s.session_id,
    s.github_run_id,
    s.status,
    s.start_time,
    COUNT(t.task_id) as total_tasks,
    SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) as completed_tasks
FROM agent_sessions s
LEFT JOIN agent_tasks t ON s.session_id = t.session_id
WHERE s.context->>'workflow' = 'GLADIATOR Reality Check'
GROUP BY s.session_id
ORDER BY s.start_time DESC;

-- Get average Reality Check accuracy
SELECT 
    AVG((t.result->>'accuracy')::numeric) as avg_accuracy,
    COUNT(*) as total_runs
FROM agent_tasks t
JOIN agent_sessions s ON t.session_id = s.session_id
WHERE t.task_name = 'Validate Model Performance'
  AND t.status = 'completed';

-- Find failed tasks for debugging
SELECT 
    s.github_run_id,
    t.task_name,
    t.assigned_agent,
    a.action_description,
    a.output
FROM agent_sessions s
JOIN agent_tasks t ON s.session_id = t.session_id
JOIN agent_actions a ON t.task_id = a.task_id
WHERE t.status = 'failed'
ORDER BY s.start_time DESC
LIMIT 10;
```

---

## Deployment Guide

### 1. Install GitHub Runners

```bash
# On ALPHA
sudo ./install-runner.sh alpha "$GITHUB_TOKEN" "$ORG_NAME"

# On BETA
sudo ./install-runner.sh beta "$GITHUB_TOKEN" "$ORG_NAME"
```

### 2. Deploy Agent Turbo Logger Script

**File**: `Agent_Turbo/core/task_logger.py`

```python
#!/usr/bin/env python3
"""
GitHub Actions → Agent Turbo Database Logger
"""
import argparse
import sys
from pathlib import Path
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent))
from agent_orchestrator import AgentOrchestrator

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--session', required=True, help='Session ID')
    parser.add_argument('--task', required=True, help='Task name')
    parser.add_argument('--status', required=True, choices=['started', 'completed', 'failed'])
    parser.add_argument('--artifact', help='Artifact path')
    parser.add_argument('--result', help='Result data (JSON or key=value)')
    args = parser.parse_args()
    
    orchestrator = AgentOrchestrator()
    
    if args.status == 'started':
        task_id = orchestrator.create_task(
            session_id=args.session,
            task_name=args.task,
            assigned_agent=get_current_runner()
        )
        print(f"Task started: {task_id}")
    
    elif args.status in ['completed', 'failed']:
        orchestrator.update_task_status(
            session_id=args.session,
            task_name=args.task,
            status=args.status,
            result=parse_result(args.result) if args.result else None
        )
        
        if args.artifact:
            orchestrator.log_artifact(
                session_id=args.session,
                artifact_path=args.artifact
            )
        
        print(f"Task {args.status}: {args.task}")

def get_current_runner():
    """Detect current runner from environment"""
    import os
    runner_name = os.environ.get('RUNNER_NAME', 'unknown')
    if 'alpha' in runner_name.lower():
        return 'ALPHA'
    elif 'beta' in runner_name.lower():
        return 'BETA'
    return runner_name

def parse_result(result_str):
    """Parse result string as JSON or key=value pairs"""
    try:
        return json.loads(result_str)
    except:
        result = {}
        for pair in result_str.split(','):
            if '=' in pair:
                k, v = pair.split('=', 1)
                result[k.strip()] = v.strip()
        return result

if __name__ == '__main__':
    main()
```

### 3. Configure Workflow Files

```bash
# Copy workflows to repository
mkdir -p .github/workflows
cp github-runners/workflows/*.yml .github/workflows/

# Commit and push
git add .github/workflows/
git commit -m "Add GitHub Actions + Agent Turbo workflows"
git push
```

### 4. Configure Secrets

**GitHub Repository → Settings → Secrets**:
- `POSTGRES_PASSWORD`: Database password for aya_rag
- `RUNNER_TOKEN`: GitHub runner registration token (if needed)

---

## Benefits

### 1. Complete Audit Trail
- Every workflow run logged to database
- Full traceability from trigger → execution → result
- Historical performance metrics
- Debugging capabilities

### 2. Claude Code Oversight
- Automated planning and task delegation
- Post-execution auditing
- Anomaly detection
- Performance optimization recommendations

### 3. Multi-Agent Orchestration
- ALPHA and BETA work in coordinated workflows
- Automatic load balancing based on labels
- Parallel execution where possible
- Sequential dependencies enforced

### 4. GLADIATOR-Specific Integration
- Automated Reality Checks
- Pattern generation pipelines
- Model training/validation
- Continuous monitoring

### 5. Developer Experience
- Self-service workflows (workflow_dispatch)
- Automated schedules (cron)
- PR-triggered validation
- Real-time status in GitHub UI + database

---

## Monitoring

### GitHub Actions UI
- **Real-time**: Actions tab shows live workflow progress
- **Artifacts**: Download models, datasets, logs
- **Re-run**: Retry failed workflows with one click

### Agent Turbo Database
- **Historical**: Query past sessions, tasks, actions
- **Analytics**: Performance trends, success rates
- **Debugging**: Full logs and context for failures

### Example Dashboard Query

```sql
-- GLADIATOR Workflow Dashboard
WITH recent_runs AS (
    SELECT 
        s.session_id,
        s.github_run_id,
        s.status,
        s.start_time,
        s.end_time,
        EXTRACT(EPOCH FROM (s.end_time - s.start_time)) as duration_seconds,
        (SELECT COUNT(*) FROM agent_tasks WHERE session_id = s.session_id AND status = 'completed') as completed_tasks,
        (SELECT COUNT(*) FROM agent_tasks WHERE session_id = s.session_id) as total_tasks
    FROM agent_sessions s
    WHERE s.context->>'workflow' LIKE 'GLADIATOR%'
      AND s.start_time > NOW() - INTERVAL '7 days'
)
SELECT 
    status,
    COUNT(*) as runs,
    AVG(duration_seconds) as avg_duration_sec,
    SUM(completed_tasks) as total_tasks_completed,
    ROUND(100.0 * SUM(completed_tasks) / NULLIF(SUM(total_tasks), 0), 2) as success_rate_pct
FROM recent_runs
GROUP BY status;
```

---

## Troubleshooting

### Workflow Not Triggering

**Check**:
1. Runner online in GitHub UI
2. Labels match workflow `runs-on`
3. Service running: `sudo launchctl list | grep github.actions.runner`

### Database Connection Failures

**Check**:
1. Postgres running: `pg_isready -h localhost`
2. Network connectivity: `ping alpha.local` / `ping beta.local`
3. Environment variables set in workflow

### Task Not Logging

**Check**:
1. `task_logger.py` permissions: `chmod +x Agent_Turbo/core/task_logger.py`
2. Python path correct in workflow
3. Session ID passed correctly from planning phase

---

## Future Enhancements

- [ ] Slack/Discord notifications via webhooks
- [ ] Grafana dashboard for real-time metrics
- [ ] Automatic rollback on failed validations
- [ ] Multi-repository orchestration
- [ ] Cost tracking (compute hours per workflow)
- [ ] ML model performance tracking over time

---

**Version**: 1.0  
**Last Updated**: October 16, 2025  
**Status**: Production Ready

