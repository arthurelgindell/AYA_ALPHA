#!/usr/bin/env python3
"""
Queue All Technologies - Batch Queue Script
Queues Tier 1, Tier 2, and Tier 3 technologies for intelligence gathering
"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from scout_orchestrator import ScoutOrchestrator

# Technology definitions by tier
TIER_1 = [
    {
        'url': 'https://pytorch.org/docs/',
        'technology': 'pytorch',
        'priority': 10,
        'max_pages': 2000
    },
    {
        'url': 'https://docs.nvidia.com/deeplearning/cudnn/',
        'technology': 'cudnn',
        'priority': 10,
        'max_pages': 500
    },
    {
        'url': 'https://www.deepspeed.ai/',
        'technology': 'deepspeed',
        'priority': 10,
        'max_pages': 1000
    },
    {
        'url': 'https://github.com/NVIDIA/Megatron-LM',
        'technology': 'megatron_lm',
        'priority': 10,
        'max_pages': 500
    },
    {
        'url': 'https://docs.nvidia.com/nemo/',
        'technology': 'nemo',
        'priority': 10,
        'max_pages': 1000
    }
]

TIER_2 = [
    {
        'url': 'https://docs.github.com/en/actions',
        'technology': 'github_actions',
        'priority': 8,
        'max_pages': 1500
    },
    {
        'url': 'https://patroni.readthedocs.io/',
        'technology': 'patroni',
        'priority': 8,
        'max_pages': 500
    },
    {
        'url': 'https://prometheus.io/docs/',
        'technology': 'prometheus',
        'priority': 7,
        'max_pages': 1000
    },
    {
        'url': 'https://kubernetes.io/docs/',
        'technology': 'kubernetes',
        'priority': 8,
        'max_pages': 3000
    },
    {
        'url': 'https://fastapi.tiangolo.com/',
        'technology': 'fastapi',
        'priority': 7,
        'max_pages': 800
    }
]

TIER_3 = [
    {
        'url': 'https://huggingface.co/docs/transformers/',
        'technology': 'transformers',
        'priority': 6,
        'max_pages': 2000
    },
    {
        'url': 'https://docs.anthropic.com/',
        'technology': 'anthropic_claude',
        'priority': 6,
        'max_pages': 500
    },
    {
        'url': 'https://github.com/pgvector/pgvector',
        'technology': 'pgvector',
        'priority': 5,
        'max_pages': 200
    }
]

def queue_tier(orchestrator: ScoutOrchestrator, technologies: list, tier_name: str):
    """Queue a tier of technologies"""
    print(f"\n{'='*60}")
    print(f"📋 Queueing {tier_name}")
    print(f"{'='*60}\n")
    
    queue_ids = []
    for tech in technologies:
        try:
            queue_id = orchestrator.queue_new_crawl(
                url=tech['url'],
                technology_name=tech['technology'],
                priority=tech['priority'],
                max_pages=tech['max_pages']
            )
            queue_ids.append(queue_id)
            print(f"  ✅ {tech['technology']:25s} | ID: {queue_id:3d} | Priority: {tech['priority']:2d} | Pages: {tech['max_pages']:4d}")
        except Exception as e:
            print(f"  ❌ {tech['technology']:25s} | ERROR: {e}")
    
    print(f"\n✅ {tier_name}: Queued {len(queue_ids)} technologies")
    return queue_ids

def main():
    """Main execution"""
    orchestrator = ScoutOrchestrator()
    
    print("\n🚀 Intelligence Scout - Batch Queue Script")
    print("=" * 60)
    
    # Queue Tier 1
    tier1_ids = queue_tier(orchestrator, TIER_1, "Tier 1: GAMMA Critical (Priority 10)")
    
    # Queue Tier 2
    tier2_ids = queue_tier(orchestrator, TIER_2, "Tier 2: Core AYA Infrastructure (Priority 7-8)")
    
    # Queue Tier 3
    tier3_ids = queue_tier(orchestrator, TIER_3, "Tier 3: Supporting Technologies (Priority 5-6)")
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 QUEUE SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Tier 1: {len(tier1_ids)} technologies queued")
    print(f"✅ Tier 2: {len(tier2_ids)} technologies queued")
    print(f"✅ Tier 3: {len(tier3_ids)} technologies queued")
    print(f"📋 Total: {len(tier1_ids) + len(tier2_ids) + len(tier3_ids)} technologies queued")
    print(f"\n💡 Next step: Run tier processing with validation checkpoints")
    print(f"   python3 process_tiers_with_checkpoints.py")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()

