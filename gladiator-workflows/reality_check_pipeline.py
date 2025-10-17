#!/usr/bin/env python3
"""
GLADIATOR Reality Check Pipeline
Complete workflow orchestration with Agent Turbo integration
"""
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
import time

sys.path.insert(0, '/Users/arthurdell/AYA/Agent_Turbo/core')
from claude_planner import ClaudePlanner
from agent_orchestrator import AgentOrchestrator

class RealityCheckPipeline:
    def __init__(self, sample_size=1000):
        self.sample_size = sample_size
        self.planner = ClaudePlanner()
        self.orchestrator = AgentOrchestrator()
        self.session_id = None
        self.tasks = {}
        
    def initialize_session(self):
        """Initialize Agent Turbo planning session"""
        print("="*80)
        print("GLADIATOR REALITY CHECK PIPELINE")
        print("="*80)
        print(f"Sample Size: {self.sample_size}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print()
        
        self.session_id = self.planner.start_planning_session(
            task_type="gladiator_reality_check",
            context={
                "sample_size": self.sample_size,
                "trigger": "manual",
                "option_a_strategy": True,
                "modern_threat_focus": True
            }
        )
        
        print(f"✅ Session initialized: {self.session_id}")
        
        # Create delegated tasks
        print("\nCreating tasks...")
        self.tasks = {
            "generate": self.planner.create_delegated_task(
                session_id=self.session_id,
                task_name="Generate Reality Check Dataset",
                assigned_agent="BETA",
                priority="critical"
            ),
            "transfer": self.planner.create_delegated_task(
                session_id=self.session_id,
                task_name="Transfer Dataset BETA→ALPHA",
                assigned_agent="BETA",
                priority="critical"
            ),
            "split": self.planner.create_delegated_task(
                session_id=self.session_id,
                task_name="Split Dataset (900/100)",
                assigned_agent="ALPHA",
                priority="critical"
            ),
            "baseline": self.planner.create_delegated_task(
                session_id=self.session_id,
                task_name="Foundation Model Baseline",
                assigned_agent="ALPHA",
                priority="high"
            ),
            "finetune": self.planner.create_delegated_task(
                session_id=self.session_id,
                task_name="Fine-tune Foundation-Sec-8B",
                assigned_agent="ALPHA",
                priority="critical"
            ),
            "validate": self.planner.create_delegated_task(
                session_id=self.session_id,
                task_name="Validate Model Performance",
                assigned_agent="ALPHA",
                priority="critical"
            )
        }
        
        for name, task_id in self.tasks.items():
            print(f"  ✅ Task '{name}': {task_id}")
        
        print()
        return self.session_id
    
    def task_1_generate_dataset(self):
        """Task 1: Generate Reality Check dataset on BETA"""
        print("="*80)
        print("TASK 1: Generate Reality Check Dataset (BETA)")
        print("="*80)
        
        task_id = self.tasks["generate"]
        self.orchestrator.update_task_status(
            session_id=self.session_id,
            task_name="Generate Reality Check Dataset",
            status="in_progress"
        )
        
        # Create generation script
        generation_script = f"""
import json
import random
from pathlib import Path
from datetime import datetime

# Configuration
ATTACK_DIR = Path("/gladiator/data/attack_patterns/iteration_001")
OUTPUT_FILE = Path("/gladiator/data/reality_check_{self.sample_size}.json")
SAMPLE_SIZE = {self.sample_size}
RANDOM_SEED = 42

print("Loading attack patterns...")
patterns = []
for json_file in sorted(ATTACK_DIR.glob("attack_*.json")):
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
            patterns.append(data)
    except Exception as e:
        print(f"Warning: Failed to load {{json_file}}: {{e}}")
        continue

print(f"Loaded {{len(patterns)}} attack patterns")

# Stratified sampling by attack type
from collections import defaultdict
by_type = defaultdict(list)
for p in patterns:
    attack_type = p.get('type', p.get('template', 'unknown'))
    key = ' '.join(str(attack_type).split()[:3])
    by_type[key].append(p)

print(f"Found {{len(by_type)}} attack categories")

# Sample proportionally
random.seed(RANDOM_SEED)
sampled = []
total = len(patterns)

for attack_type, type_patterns in by_type.items():
    proportion = len(type_patterns) / total
    type_sample_size = max(1, int(SAMPLE_SIZE * proportion))
    
    if len(type_patterns) <= type_sample_size:
        sampled.extend(type_patterns)
    else:
        sampled.extend(random.sample(type_patterns, type_sample_size))

# Adjust to exact size
if len(sampled) < SAMPLE_SIZE:
    remaining = [p for p in patterns if p not in sampled]
    needed = SAMPLE_SIZE - len(sampled)
    sampled.extend(random.sample(remaining, min(needed, len(remaining))))
elif len(sampled) > SAMPLE_SIZE:
    sampled = random.sample(sampled, SAMPLE_SIZE)

print(f"\\nSampled {{len(sampled)}} patterns")

# Create output
output = {{
    "metadata": {{
        "generated_at": datetime.now().isoformat(),
        "source": "iteration_001",
        "total_available": len(patterns),
        "sample_size": len(sampled),
        "random_seed": RANDOM_SEED,
        "option_a_strategy": True
    }},
    "patterns": sampled
}}

# Write output
OUTPUT_FILE.write_text(json.dumps(output, indent=2))
print(f"\\n✅ Dataset created: {{OUTPUT_FILE}}")
print(f"   Size: {{OUTPUT_FILE.stat().st_size / 1024 / 1024:.2f}} MB")
print(f"   Patterns: {{len(sampled)}}")
"""
        
        print("Deploying generation script to BETA...")
        # Write script to temp file
        script_path = Path("/tmp/generate_reality_check.py")
        script_path.write_text(generation_script)
        
        # Copy to BETA
        subprocess.run([
            "scp", str(script_path),
            "arthurdell@beta.local:/tmp/generate_reality_check.py"
        ], check=True)
        
        print("✅ Script deployed to BETA")
        print("\nExecuting dataset generation on BETA...")
        
        # Execute on BETA via red_combat container
        result = subprocess.run([
            "ssh", "arthurdell@beta.local",
            "docker exec red_combat python3 /tmp/generate_reality_check.py"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        
        if result.returncode != 0:
            print(f"❌ Generation failed: {result.stderr}")
            self.orchestrator.update_task_status(
                session_id=self.session_id,
                task_name="Generate Reality Check Dataset",
                status="failed",
                result={"error": result.stderr}
            )
            return False
        
        # Verify output
        verify_result = subprocess.run([
            "ssh", "arthurdell@beta.local",
            f"docker exec red_combat test -f /gladiator/data/reality_check_{self.sample_size}.json && echo 'EXISTS' || echo 'MISSING'"
        ], capture_output=True, text=True)
        
        if "EXISTS" in verify_result.stdout:
            print(f"\\n✅ Task 1 COMPLETE: Dataset generated on BETA")
            
            # Get file size
            size_result = subprocess.run([
                "ssh", "arthurdell@beta.local",
                f"docker exec red_combat stat -f%z /gladiator/data/reality_check_{self.sample_size}.json"
            ], capture_output=True, text=True)
            
            file_size = int(size_result.stdout.strip())
            
            self.orchestrator.update_task_status(
                session_id=self.session_id,
                task_name="Generate Reality Check Dataset",
                status="completed",
                result={
                    "sample_size": self.sample_size,
                    "file_size_bytes": file_size,
                    "file_size_mb": round(file_size / 1024 / 1024, 2),
                    "location": f"/gladiator/data/reality_check_{self.sample_size}.json"
                }
            )
            return True
        else:
            print(f"❌ Dataset file not found after generation")
            self.orchestrator.update_task_status(
                session_id=self.session_id,
                task_name="Generate Reality Check Dataset",
                status="failed",
                result={"error": "File not created"}
            )
            return False
    
    def task_2_transfer_dataset(self):
        """Task 2: Transfer dataset from BETA to ALPHA"""
        print("\\n" + "="*80)
        print("TASK 2: Transfer Dataset BETA→ALPHA")
        print("="*80)
        
        self.orchestrator.update_task_status(
            session_id=self.session_id,
            task_name="Transfer Dataset BETA→ALPHA",
            status="in_progress"
        )
        
        # Create transfer directory on ALPHA
        alpha_dir = Path("/Users/arthurdell/GLADIATOR/datasets")
        alpha_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Transferring dataset to {alpha_dir}...")
        
        # Transfer via rsync
        result = subprocess.run([
            "rsync", "-avz", "--progress",
            f"arthurdell@beta.local:/Volumes/DATA/GLADIATOR/reality_check_{self.sample_size}.json",
            str(alpha_dir / f"reality_check_{self.sample_size}.json")
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Verify file exists on ALPHA
            alpha_file = alpha_dir / f"reality_check_{self.sample_size}.json"
            if alpha_file.exists():
                file_size = alpha_file.stat().st_size
                print(f"\\n✅ Task 2 COMPLETE: Dataset transferred to ALPHA")
                print(f"   Location: {alpha_file}")
                print(f"   Size: {file_size / 1024 / 1024:.2f} MB")
                
                self.orchestrator.update_task_status(
                    session_id=self.session_id,
                    task_name="Transfer Dataset BETA→ALPHA",
                    status="completed",
                    result={
                        "source": f"beta:/gladiator/data/reality_check_{self.sample_size}.json",
                        "destination": str(alpha_file),
                        "file_size_bytes": file_size
                    }
                )
                return True
        
        print(f"❌ Transfer failed: {result.stderr}")
        self.orchestrator.update_task_status(
            session_id=self.session_id,
            task_name="Transfer Dataset BETA→ALPHA",
            status="failed",
            result={"error": result.stderr}
        )
        return False
    
    def finalize_session(self, success=True):
        """Finalize and audit session"""
        print("\\n" + "="*80)
        print("AUDIT & FINALIZATION")
        print("="*80)
        
        # Get session summary
        summary = self.planner.get_planning_session_summary(self.session_id)
        
        print(f"\\nSession Summary:")
        print(f"  Session ID: {self.session_id}")
        print(f"  Status: {summary.get('status', 'unknown')}")
        print(f"  Tasks Completed: {summary.get('completed_tasks', 0)}/{summary.get('total_tasks', 0)}")
        
        # Audit results
        audit_results = self.planner.audit_task_results(
            session_id=self.session_id,
            expected_outcomes={
                "Generate Reality Check Dataset": f"Dataset with {self.sample_size} patterns created",
                "Transfer Dataset BETA→ALPHA": "Dataset transferred successfully"
            }
        )
        
        print(f"\\nAudit Results: {audit_results.get('status', 'unknown')}")
        
        print("\\n" + "="*80)
        if success:
            print("✅ REALITY CHECK TASKS 1-2 COMPLETE")
        else:
            print("❌ REALITY CHECK FAILED - CHECK LOGS")
        print("="*80)
        print("\\nNext Steps:")
        print("  - Task 3: Split dataset (900 train / 100 validation)")
        print("  - Task 4: Baseline test (Foundation-Sec-8B)")
        print("  - Task 5: Configure fine-tuning")
        print("  - Task 6: Launch training (12-24 hours)")
        print()

def main():
    pipeline = RealityCheckPipeline(sample_size=1000)
    
    try:
        # Initialize
        pipeline.initialize_session()
        
        # Task 1: Generate dataset
        if not pipeline.task_1_generate_dataset():
            pipeline.finalize_session(success=False)
            return 1
        
        # Task 2: Transfer dataset
        if not pipeline.task_2_transfer_dataset():
            pipeline.finalize_session(success=False)
            return 1
        
        # Finalize
        pipeline.finalize_session(success=True)
        return 0
        
    except Exception as e:
        print(f"\\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

