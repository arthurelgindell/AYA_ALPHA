#!/usr/bin/env python3
"""
Process Tiers with Checkpoints - Batch Processing with Validation
Processes technologies tier by tier with validation checkpoints after each tier
"""

import sys
import subprocess
import time
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'Agent_Turbo' / 'core'))

from scout_orchestrator import ScoutOrchestrator
from postgres_connector import PostgreSQLConnector

def validate_tier(tier_name: str, expected_technologies: list):
    """Validate a tier's completion"""
    print(f"\n{'='*60}")
    print(f"🔍 VALIDATION CHECKPOINT: {tier_name}")
    print(f"{'='*60}\n")
    
    db = PostgreSQLConnector()
    
    # Check queue status
    print("📊 Queue Status:")
    queue_stats = db.execute_query(
        """SELECT technology_name, status, pages_crawled, max_pages, completed_at
           FROM intelligence_scout_queue
           WHERE technology_name = ANY(%s)
           ORDER BY technology_name""",
        (expected_technologies,),
        fetch='all'
    )
    
    completed = 0
    pending = 0
    failed = 0
    total_pages = 0
    
    for item in queue_stats:
        tech_name = item['technology_name']
        status = item['status']
        pages = item['pages_crawled'] or 0
        max_pages = item['max_pages']
        
        status_icon = "✅" if status == 'completed' else "⏳" if status == 'pending' else "❌"
        print(f"  {status_icon} {tech_name:25s} | {status:12s} | {pages:4d}/{max_pages:4d} pages")
        
        if status == 'completed':
            completed += 1
            total_pages += pages
        elif status == 'pending':
            pending += 1
        else:
            failed += 1
    
    print(f"\n  Summary: {completed} completed, {pending} pending, {failed} failed")
    
    # Check knowledge entries
    print(f"\n📚 Knowledge Entries:")
    knowledge_stats = db.execute_query(
        """SELECT source_technology, COUNT(*) as entries,
                  COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) as with_embeddings
           FROM agent_knowledge
           WHERE source_technology = ANY(%s)
           GROUP BY source_technology
           ORDER BY entries DESC""",
        (expected_technologies,),
        fetch='all'
    )
    
    total_entries = 0
    total_embeddings = 0
    
    for stat in knowledge_stats:
        tech = stat['source_technology']
        entries = stat['entries']
        embeddings = stat['with_embeddings']
        coverage = (embeddings / entries * 100) if entries > 0 else 0
        total_entries += entries
        total_embeddings += embeddings
        print(f"  {tech:25s} | {entries:6d} entries | {embeddings:6d} embeddings ({coverage:.1f}%)")
    
    print(f"\n  Total: {total_entries:,} entries, {total_embeddings:,} embeddings")
    
    # Check documentation tables
    print(f"\n📄 Documentation Tables:")
    for tech in expected_technologies:
        table_name = f"{tech}_documentation"
        table_exists = db.execute_query(
            """SELECT EXISTS (
                   SELECT FROM information_schema.tables 
                   WHERE table_schema = 'public' 
                   AND table_name = %s
               )""",
            (table_name,),
            fetch='one'
        )
        
        if table_exists and table_exists.get('exists'):
            doc_count = db.execute_query(
                f"SELECT COUNT(*) as count FROM {table_name}",
                fetch='one'
            )
            count = doc_count['count'] if doc_count else 0
            print(f"  ✅ {table_name:35s} | {count:5d} documents")
        else:
            print(f"  ❌ {table_name:35s} | Not created")
    
    # Embedding service health check
    print(f"\n🔧 Embedding Service:")
    try:
        import requests
        response = requests.get('http://localhost:8765/health', timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"  ✅ Status: {health.get('status', 'unknown')}")
            print(f"  ✅ Model Loaded: {health.get('model_loaded', False)}")
            print(f"  ✅ Metal GPU: {health.get('metal_available', False)}")
        else:
            print(f"  ⚠️  Service returned status {response.status_code}")
    except Exception as e:
        print(f"  ❌ Service check failed: {e}")
    
    print(f"\n{'='*60}\n")
    
    return {
        'completed': completed,
        'pending': pending,
        'failed': failed,
        'total_entries': total_entries,
        'total_embeddings': total_embeddings,
        'total_pages': total_pages
    }

def process_queue_until_complete(orchestrator: ScoutOrchestrator, max_items: int = None):
    """Process queue items until completion or max_items reached"""
    items_processed = 0
    
    while True:
        # Get next pending item
        queue_item = orchestrator.crawler.get_queue_item()
        
        if not queue_item:
            print("\n✅ No more pending items in queue")
            break
        
        if max_items and items_processed >= max_items:
            print(f"\n⏸️  Reached max items limit ({max_items})")
            break
        
        queue_id = queue_item['id']
        technology = queue_item['technology_name']
        
        print(f"\n🔄 Processing: {technology} (Queue ID: {queue_id})")
        print(f"{'='*60}\n")
        
        try:
            result = orchestrator.process_queue_item(queue_id)
            
            if 'error' in result:
                print(f"❌ Error processing {technology}: {result['error']}")
            else:
                print(f"✅ Successfully processed {technology}")
                items_processed += 1
        
        except KeyboardInterrupt:
            print(f"\n⚠️  Interrupted. Processed {items_processed} items.")
            break
        except Exception as e:
            print(f"❌ Exception processing {technology}: {e}")
            import traceback
            traceback.print_exc()
            continue
        
        # Small delay between items
        time.sleep(2)
    
    return items_processed

def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process Intelligence Scout tiers with checkpoints')
    parser.add_argument('--tier', choices=['1', '2', '3', 'all'], default='all',
                       help='Which tier to process')
    parser.add_argument('--max-items', type=int, help='Maximum items to process per tier')
    parser.add_argument('--skip-validation', action='store_true',
                       help='Skip validation checkpoints')
    
    args = parser.parse_args()
    
    orchestrator = ScoutOrchestrator()
    
    # Technology lists by tier
    TIER_1_TECHS = ['pytorch', 'cudnn', 'deepspeed', 'megatron_lm', 'nemo']
    TIER_2_TECHS = ['github_actions', 'patroni', 'prometheus', 'kubernetes', 'fastapi']
    TIER_3_TECHS = ['transformers', 'anthropic_claude', 'pgvector']
    
    print("\n🚀 Intelligence Scout - Tier Processing with Checkpoints")
    print("=" * 60)
    
    if args.tier in ['1', 'all']:
        print("\n📋 TIER 1: GAMMA Critical Technologies")
        print("=" * 60)
        
        items = process_queue_until_complete(orchestrator, args.max_items)
        print(f"\n✅ Tier 1: Processed {items} items")
        
        if not args.skip_validation:
            validate_tier("Tier 1: GAMMA Critical", TIER_1_TECHS)
        
        if args.tier != 'all':
            return
        
        # Checkpoint pause
        if not args.skip_validation:
            input("\n⏸️  Press Enter to continue to Tier 2...")
    
    if args.tier in ['2', 'all']:
        print("\n📋 TIER 2: Core AYA Infrastructure")
        print("=" * 60)
        
        items = process_queue_until_complete(orchestrator, args.max_items)
        print(f"\n✅ Tier 2: Processed {items} items")
        
        if not args.skip_validation:
            validate_tier("Tier 2: Core AYA Infrastructure", TIER_2_TECHS)
        
        if args.tier != 'all':
            return
        
        # Checkpoint pause
        if not args.skip_validation:
            input("\n⏸️  Press Enter to continue to Tier 3...")
    
    if args.tier in ['3', 'all']:
        print("\n📋 TIER 3: Supporting Technologies")
        print("=" * 60)
        
        items = process_queue_until_complete(orchestrator, args.max_items)
        print(f"\n✅ Tier 3: Processed {items} items")
        
        if not args.skip_validation:
            validate_tier("Tier 3: Supporting Technologies", TIER_3_TECHS)
    
    # Final summary
    print(f"\n{'='*60}")
    print("🎉 ALL TIERS COMPLETE")
    print(f"{'='*60}\n")
    
    # Overall validation
    all_techs = TIER_1_TECHS + TIER_2_TECHS + TIER_3_TECHS
    validate_tier("Final Summary - All Technologies", all_techs)

if __name__ == '__main__':
    main()

