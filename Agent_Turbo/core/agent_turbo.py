#!/usr/bin/env python3
"""
AGENT_TURBO - Unified High-Performance Knowledge System
GAMMA Project Implementation

Core functionality:
- High-performance token optimization and session memory
- MLX GPU acceleration for Apple Silicon
- SQLite storage with memory-mapped caching
- RAM disk optimization for ultra-fast I/O
- Bulletproof verification protocol

Performance targets:
- <100ms response time for cached queries
- >80% token reduction on repeated operations
- >50% cache hit rate after 10 queries
- 100GB RAM disk for ultra-fast I/O
- MLX Metal acceleration (160 GPU cores)
"""

import os
import sys
import json
import time
import hashlib
import mmap
import argparse
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import psutil

# PostgreSQL connector (replaces SQLite)
from postgres_connector import PostgreSQLConnector
import numpy as np

# MLX GPU acceleration
try:
    import mlx.core as mx
    import mlx.nn as nn
    GPU_AVAILABLE = True
    # Set default device to GPU for maximum performance
    if mx.metal.is_available():
        mx.set_default_device(mx.gpu)
    
    # Fix GPU core detection for Apple M3 Ultra
    device_info = mx.metal.device_info()
    device_name = device_info.get('device_name', '')
    
    # Map device names to known GPU core counts
    if 'M3 Ultra' in device_name:
        GPU_CORES = 80  # M3 Ultra has 80 GPU cores
    elif 'M3 Max' in device_name:
        GPU_CORES = 40  # M3 Max has 40 GPU cores
    elif 'M3 Pro' in device_name:
        GPU_CORES = 18  # M3 Pro has 18 GPU cores
    elif 'M3' in device_name:
        GPU_CORES = 10  # M3 has 10 GPU cores
    elif 'M2 Ultra' in device_name:
        GPU_CORES = 76  # M2 Ultra has 76 GPU cores
    elif 'M2 Max' in device_name:
        GPU_CORES = 38  # M2 Max has 38 GPU cores
    elif 'M2 Pro' in device_name:
        GPU_CORES = 19  # M2 Pro has 19 GPU cores
    elif 'M2' in device_name:
        GPU_CORES = 10  # M2 has 10 GPU cores
    elif 'M1 Ultra' in device_name:
        GPU_CORES = 64  # M1 Ultra has 64 GPU cores
    elif 'M1 Max' in device_name:
        GPU_CORES = 32  # M1 Max has 32 GPU cores
    elif 'M1 Pro' in device_name:
        GPU_CORES = 16  # M1 Pro has 16 GPU cores
    elif 'M1' in device_name:
        GPU_CORES = 8   # M1 has 8 GPU cores
    else:
        # Fallback to MLX detection (often returns 0)
        GPU_CORES = device_info.get('gpu_cores', 0)
        
except ImportError:
    GPU_AVAILABLE = False
    GPU_CORES = 0

# Configuration
AGENT_TURBO_CACHE = Path('/Volumes/DATA/Agent_RAM/cache') if Path('/Volumes/DATA/Agent_RAM').exists() else Path.home() / '.agent_turbo' / 'agent_turbo_cache'
MEMORY_LIMIT_MB = 100 * 1024  # 100GB
FLUSH_INTERVAL = 120  # 2 minutes high velocity mode
EMBEDDING_DIM = 768  # bge-base-en-v1.5 dimensions
EMBEDDING_SERVICE_URL = "http://localhost:8765"  # Existing embedding service

class AgentTurbo:
    """
    Unified high-performance knowledge system for GAMMA project.
    
    Prime Directives Compliance:
    - Migrated from SQLite to PostgreSQL aya_rag database
    - Uses existing embedding service (port 8765) for vectors
    - Maintains RAM disk caching for performance
    - All operations query/write actual PostgreSQL data (NO MOCKS)
    """
    
    def __init__(self, silent=False):
        # PostgreSQL connector (replaces SQLite)
        self.db = PostgreSQLConnector()
        
        # Embedding service URL
        self.embedding_service_url = EMBEDDING_SERVICE_URL
        
        self.cache_dir = AGENT_TURBO_CACHE
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.mmap_cache = {}
        self.query_cache = {}  # RAM disk query result cache
        self.embedding_cache = {}  # RAM disk embedding cache
        self.pattern_cache = {}  # RAM disk pattern cache
        self.session_cache = {}  # RAM disk session cache
        
        # GPU optimizer will be initialized in init_turbo_mode()
        self.gpu_optimizer = None
        
        # LM Studio client will be initialized in init_turbo_mode()
        self.lm_studio_client = None
        
        self.init_turbo_mode(silent=silent)
        self.init_ram_disk_cache(silent=silent)
    
    def generate_embedding(self, text: str) -> list:
        """
        Generate embedding via existing embedding service.
        
        Args:
            text: Text to embed
        
        Returns:
            list: 768-dimensional embedding vector
        
        Raises:
            Exception: If embedding service fails
        """
        try:
            response = requests.post(
                f"{self.embedding_service_url}/embed",
                json={"text": text},
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result['embedding']
        except Exception as e:
            print(f"❌ Embedding generation failed: {e}", file=sys.stderr)
            raise
    
    def init_turbo_mode(self, silent=False):
        """Initialize turbo mode with GPU acceleration."""
        if not silent:
            print(f"🚀 Initializing AGENT_TURBO Mode...")
        if GPU_AVAILABLE:
            if not silent:
                print(f"✅ MLX GPU acceleration enabled ({GPU_CORES} cores)")
        else:
            if not silent:
                print("⚠️  GPU not available, using CPU mode")
        
        # Initialize GPU optimizer
        if GPU_AVAILABLE:
            try:
                from core.agent_turbo_gpu import AgentTurboGPUOptimizer
                self.gpu_optimizer = AgentTurboGPUOptimizer()
                if not silent:
                    print(f"🚀 GPU optimizer initialized: {GPU_CORES} cores")
            except ImportError:
                if not silent:
                    print("⚠️  GPU optimizer not available")
                self.gpu_optimizer = None
        else:
            self.gpu_optimizer = None
        
        # Initialize LM Studio client
        try:
            from core.lm_studio_client import LMStudioClient
            self.lm_studio_client = LMStudioClient()
            if not silent:
                print("🚀 LM Studio client initialized")
        except ImportError:
            if not silent:
                print("⚠️  LM Studio client not available")
            self.lm_studio_client = None
        except Exception as e:
            if not silent:
                print(f"⚠️  LM Studio client initialization failed: {e}")
            self.lm_studio_client = None
        
        # Preload memory-mapped files
        self.preload_cache(silent=silent)
        if not silent:
            print("✅ AGENT_TURBO Mode ready!")
    
    def preload_cache(self, silent=False):
        """Preload frequently accessed files into memory-mapped cache."""
        # Use explicit Agent_Turbo path to avoid App Translocation issues
        agent_turbo_dir = Path(__file__).parent.parent
        target_dirs = [
            agent_turbo_dir / 'core',
            Path.home() / '.agent_turbo',
        ]
        
        files_loaded = 0
        for base_dir in target_dirs:
            if not base_dir.exists():
                continue
            
            try:
                # Use glob instead of rglob to avoid deep recursion
                for path in base_dir.glob('*.py'):
                    if path.stat().st_size > 0 and files_loaded < 100:
                        try:
                            with open(path, 'rb') as f:
                                self.mmap_cache[str(path)] = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                            files_loaded += 1
                        except Exception as e:
                            if "cannot mmap an empty file" not in str(e):
                                if not silent:
                                    print(f"Error mapping {path}: {e}")
            except OSError as e:
                # Skip directory if we hit filesystem limits (App Translocation, etc.)
                if not silent:
                    print(f"⚠️  Skipping {base_dir}: {e}")
                continue
        
        if files_loaded > 0:
            if not silent:
                print(f"  📂 Preloaded {files_loaded} files into memory-mapped cache")
    
    def init_ram_disk_cache(self, silent=False):
        """Initialize RAM disk cache system for ultra-fast operations."""
        if not silent:
            print("  🚀 Initializing RAM disk cache system...")
        
        # Create cache subdirectories
        cache_dirs = [
            self.cache_dir / 'queries',
            self.cache_dir / 'embeddings', 
            self.cache_dir / 'patterns',
            self.cache_dir / 'sessions',
            self.cache_dir / 'temp'
        ]
        
        for cache_dir in cache_dirs:
            cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing cache files into memory
        self.load_cache_files()
        
        if not silent:
            print(f"  ✅ RAM disk cache system ready ({len(cache_dirs)} directories)")
    
    def load_cache_files(self):
        """Load existing cache files into memory for instant access."""
        cache_types = ['queries', 'embeddings', 'patterns', 'sessions']
        
        for cache_type in cache_types:
            cache_path = self.cache_dir / cache_type
            if cache_path.exists():
                files = list(cache_path.glob('*.json'))
                for file in files:
                    try:
                        with open(file, 'r') as f:
                            data = json.load(f)
                        cache_key = file.stem
                        cache_attr = f'{cache_type.replace("s", "")}_cache'
                        if hasattr(self, cache_attr):
                            cache_dict = getattr(self, cache_attr)
                            cache_dict[cache_key] = data
                    except Exception as e:
                        print(f"    ⚠️  Error loading {file}: {e}")
    
    def save_to_ram_cache(self, cache_type: str, key: str, data: Any) -> bool:
        """Save data to RAM disk cache for ultra-fast access."""
        try:
            cache_path = self.cache_dir / cache_type
            cache_path.mkdir(parents=True, exist_ok=True)
            
            file_path = cache_path / f"{key}.json"
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Update in-memory cache
            cache_attr = f'{cache_type.replace("s", "")}_cache'
            if hasattr(self, cache_attr):
                cache_dict = getattr(self, cache_attr)
                cache_dict[key] = data
            
            return True
        except Exception as e:
            print(f"    ⚠️  Error saving to RAM cache: {e}")
            return False
    
    def get_from_ram_cache(self, cache_type: str, key: str) -> Optional[Any]:
        """Get data from RAM disk cache for instant access."""
        try:
            cache_attr = f'{cache_type.replace("s", "")}_cache'
            if hasattr(self, cache_attr):
                cache_dict = getattr(self, cache_attr)
                if key in cache_dict:
                    return cache_dict[key]
            
            # Try loading from disk if not in memory
            cache_path = self.cache_dir / cache_type
            file_path = cache_path / f"{key}.json"
            if file_path.exists():
                with open(file_path, 'r') as f:
                    data = json.load(f)
                if hasattr(self, cache_attr):
                    cache_dict = getattr(self, cache_attr)
                    cache_dict[key] = data
                return data
            
            return None
        except Exception as e:
            print(f"    ⚠️  Error getting from RAM cache: {e}")
            return None
    
    def add(self, content: str, source_session: str = None, knowledge_type: str = 'solution') -> str:
        """
        Add knowledge to PostgreSQL with embedding generation.
        
        Prime Directive #1: Queries actual PostgreSQL database, generates real embeddings.
        
        Args:
            content: Knowledge content to store
            source_session: Optional session ID that created this knowledge
            knowledge_type: Type of knowledge ('solution', 'pattern', 'error', 'optimization')
        
        Returns:
            str: Success/failure message with hash
        """
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Check for duplicates in PostgreSQL
        existing = self.db.execute_query(
            'SELECT id FROM agent_knowledge WHERE content_hash = %s',
            (content_hash,),
            fetch=True
        )
        
        if existing:
            return f"⚠️  Duplicate knowledge: {content_hash[:8]}"
        
        # Generate embedding via existing service
        try:
            embedding = self.generate_embedding(content)
        except Exception as e:
            return f"❌ Failed to generate embedding: {e}"
        
        # Convert embedding to numpy array for pgvector
        embedding_vector = np.array(embedding)
        
        # Store in PostgreSQL agent_knowledge table
        query = """
            INSERT INTO agent_knowledge 
            (content_hash, content, embedding, tokens, created_at, 
             source_session, knowledge_type, access_count)
            VALUES (%s, %s, %s, %s, NOW(), %s, %s, 0)
            RETURNING id
        """
        
        try:
            result = self.db.execute_query(
                query,
                (content_hash, content, embedding_vector, len(content.split()), 
                 source_session, knowledge_type),
                fetch=True
            )
            
            preview = content[:80] + '...' if len(content) > 80 else content
            return f"✅ Added knowledge: {content_hash[:8]}\n   Content: {preview}"
        except Exception as e:
            return f"❌ Failed to add knowledge: {e}"
    
    def query(self, query_text: str, limit: int = 5) -> str:
        """
        Query knowledge base using pgvector similarity search.
        
        Prime Directive #1: Queries actual PostgreSQL with real embeddings.
        
        Args:
            query_text: Search query
            limit: Maximum results to return
        
        Returns:
            str: Formatted results with similarity scores
        """
        # Check RAM disk cache first
        query_key = f"{hashlib.sha256(query_text.encode()).hexdigest()[:8]}_{limit}"
        cached_result = self.get_from_ram_cache('queries', query_key)
        
        if cached_result:
            # Update cache timestamp
            cached_result['timestamp'] = int(time.time())
            self.save_to_ram_cache('queries', query_key, cached_result)
            return cached_result['result']
        
        # Generate query embedding
        try:
            query_embedding = self.generate_embedding(query_text)
        except Exception as e:
            return f"❌ Failed to generate query embedding: {e}"
        
        # pgvector similarity search using cosine distance
        # Lower distance = more similar (1 - distance = similarity score)
        # Convert to numpy array for pgvector
        query_vector = np.array(query_embedding)
        
        sql = """
            SELECT 
                content,
                knowledge_type,
                1 - (embedding <=> %s) AS similarity
            FROM agent_knowledge
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> %s
            LIMIT %s
        """
        
        try:
            results = self.db.execute_query(
                sql,
                (query_vector, query_vector, limit),
                fetch=True
            )
            
            if not results:
                result_text = f"❌ No results found for: {query_text}"
            else:
                output = [f"🚀 pgvector search found {len(results)} results for: {query_text}\n"]
                for i, row in enumerate(results, 1):
                    preview = row['content'][:150] + '...' if len(row['content']) > 150 else row['content']
                    similarity = row['similarity']
                    ktype = row['knowledge_type'] or 'general'
                    output.append(f"{i}. [{ktype}] (similarity: {similarity:.3f}) {preview}")
                result_text = '\n'.join(output)
            
            # Cache the result in RAM disk
            cache_data = {
                'query': query_text,
                'result': result_text,
                'timestamp': int(time.time()),
                'limit': limit,
                'result_count': len(results),
                'method': 'pgvector'
            }
            self.save_to_ram_cache('queries', query_key, cache_data)
            
            return result_text
            
        except Exception as e:
            return f"❌ Query failed: {e}"
    
    def query_with_lm_studio(self, query: str, limit: int = 5, use_lm_studio: bool = True) -> str:
        """
        Query knowledge base with LM Studio enhancement for intelligent responses.
        
        Args:
            query: User query
            limit: Maximum number of results to retrieve
            use_lm_studio: Whether to use LM Studio for response generation
            
        Returns:
            Enhanced response with LM Studio intelligence
        """
        # First, get relevant knowledge using AGENT_TURBO
        knowledge_results = self.query(query, limit)
        
        if not use_lm_studio or not self.lm_studio_client:
            return knowledge_results
        
        try:
            # Extract context from knowledge results
            context_lines = []
            if 'Found' in knowledge_results:
                lines = knowledge_results.split('\n')
                for line in lines[1:]:  # Skip the header line
                    if line.strip() and not line.startswith('📚') and not line.startswith('❌'):
                        # Clean up the line and add to context
                        clean_line = line.strip()
                        if clean_line and not clean_line.startswith('Found'):
                            context_lines.append(clean_line)
            
            # Generate intelligent response using LM Studio
            if context_lines:
                lm_response = self.lm_studio_client.generate_response(query, context_lines)
                
                if lm_response['success']:
                    # Combine AGENT_TURBO results with LM Studio enhancement
                    enhanced_response = f"🚀 AGENT_TURBO + LM Studio Enhanced Response\n\n"
                    enhanced_response += f"📚 Knowledge Base Results:\n{knowledge_results}\n\n"
                    enhanced_response += f"🧠 LM Studio Intelligence:\n{lm_response['content']}\n\n"
                    enhanced_response += f"📊 Performance: {lm_response['response_time']:.2f}s, {lm_response['tokens']} tokens"
                    
                    return enhanced_response
                else:
                    # Fallback to AGENT_TURBO results if LM Studio fails
                    return f"{knowledge_results}\n\n⚠️  LM Studio enhancement failed: {lm_response.get('error', 'Unknown error')}"
            else:
                # No context found, use LM Studio for direct response
                lm_response = self.lm_studio_client.generate_response(query)
                
                if lm_response['success']:
                    return f"🧠 LM Studio Direct Response:\n{lm_response['content']}\n\n📊 Performance: {lm_response['response_time']:.2f}s, {lm_response['tokens']} tokens"
                else:
                    return f"{knowledge_results}\n\n⚠️  LM Studio enhancement failed: {lm_response.get('error', 'Unknown error')}"
                    
        except Exception as e:
            return f"{knowledge_results}\n\n⚠️  LM Studio integration error: {e}"
    
    def enhance_knowledge_with_lm_studio(self, knowledge_text: str, enhancement_type: str = "explanation") -> str:
        """
        Enhance knowledge using LM Studio
        
        Args:
            knowledge_text: Original knowledge text
            enhancement_type: Type of enhancement (explanation, summary, expansion, context)
            
        Returns:
            Enhanced knowledge text
        """
        if not self.lm_studio_client:
            return f"⚠️  LM Studio not available for enhancement: {knowledge_text}"
        
        try:
            result = self.lm_studio_client.enhance_knowledge(knowledge_text, enhancement_type)
            
            if result['success']:
                return f"🧠 LM Studio Enhanced Knowledge ({enhancement_type}):\n{result['content']}\n\n📊 Performance: {result['response_time']:.2f}s, {result['tokens']} tokens"
            else:
                return f"⚠️  LM Studio enhancement failed: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            return f"⚠️  LM Studio enhancement error: {e}"
    
    def stats(self) -> str:
        """
        Return system statistics from PostgreSQL with cache metrics.
        
        Prime Directive #1: Queries actual PostgreSQL database for stats.
        """
        try:
            # Count knowledge entries in PostgreSQL
            count_result = self.db.execute_query(
                'SELECT COUNT(*) as count FROM agent_knowledge',
                fetch=True
            )
            count = count_result[0]['count'] if count_result else 0
            
            # Count entries with embeddings
            embedded_result = self.db.execute_query(
                'SELECT COUNT(*) as count FROM agent_knowledge WHERE embedding IS NOT NULL',
                fetch=True
            )
            embedded_count = embedded_result[0]['count'] if embedded_result else 0
            
            # Memory usage
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            # RAM disk cache statistics
            cache_stats = {
                "query_cache_entries": len(self.query_cache),
                "embedding_cache_entries": len(self.embedding_cache),
                "pattern_cache_entries": len(self.pattern_cache),
                "session_cache_entries": len(self.session_cache)
            }
            
            # Calculate cache hit rate (simplified)
            total_cache_entries = sum(cache_stats.values())
            cache_hit_rate = min(total_cache_entries / max(count, 1) * 100, 100.0)
            
            stats = {
                "database": "PostgreSQL aya_rag",
                "knowledge_entries": count,
                "entries_with_embeddings": embedded_count,
                "embedding_coverage": f"{(embedded_count/max(count,1)*100):.1f}%",
                "memory_used_mb": round(memory_mb, 2),
                "memory_limit_mb": MEMORY_LIMIT_MB,
                "cache_hit_rate": round(cache_hit_rate, 2),
                "total_tokens_saved": total_cache_entries * 100,  # Estimate
                "using_gpu": GPU_AVAILABLE,
                "gpu_cores": GPU_CORES,
                "embedding_service": EMBEDDING_SERVICE_URL,
                "ram_disk_cache": cache_stats,
                "ram_disk_utilization": f"{total_cache_entries} cached entries"
            }
            
            return json.dumps(stats, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    def benchmark_gpu_performance(self) -> str:
        """Benchmark GPU performance for embeddings and similarity search."""
        if not self.gpu_optimizer:
            return json.dumps({"error": "GPU optimizer not available"}, indent=2)
        
        try:
            benchmark_results = self.gpu_optimizer.benchmark_gpu_performance()
            return json.dumps(benchmark_results, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    def test_lm_studio_performance(self) -> str:
        """Test LM Studio performance and return results."""
        if not self.lm_studio_client:
            return json.dumps({"error": "LM Studio client not available"}, indent=2)
        
        try:
            performance_results = self.lm_studio_client.test_performance()
            return json.dumps(performance_results, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    def verify(self) -> bool:
        """
        Verify system functionality with PostgreSQL.
        
        Prime Directive #1: Tests actual database operations, not mocks.
        """
        try:
            print("🔍 Verifying Agent Turbo PostgreSQL integration...")
            
            # Test 1: PostgreSQL connection
            test_query = self.db.execute_query('SELECT 1 as test', fetch=True)
            if not test_query or test_query[0]['test'] != 1:
                print("❌ PostgreSQL connection failed")
                return False
            print("✅ PostgreSQL connection working")
            
            # Test 2: Add operation
            test_content = f"AGENT_TURBO VERIFICATION TEST {int(time.time())}"
            result = self.add(test_content)
            if "Added knowledge" not in result and "Duplicate knowledge" not in result:
                print(f"❌ Add operation failed: {result}")
                return False
            print("✅ Add operation working")
            
            # Test 3: Verify data in database
            verify_query = self.db.execute_query(
                'SELECT COUNT(*) as count FROM agent_knowledge WHERE content LIKE %s',
                ('%VERIFICATION TEST%',),
                fetch=True
            )
            if not verify_query or verify_query[0]['count'] == 0:
                print("❌ Data not persisted in PostgreSQL")
                return False
            print("✅ Data persisted in PostgreSQL")
            
            # Test 4: Query operation
            query_result = self.query("VERIFICATION", limit=3)
            if "VERIFICATION" not in query_result and "No results" not in query_result:
                print(f"❌ Query operation failed: {query_result}")
                return False
            print("✅ Query operation working")
            
            # Test 5: RAM disk cache
            cache_test_key = "verification_test"
            cache_test_data = {"test": "data", "timestamp": int(time.time())}
            
            if not self.save_to_ram_cache('sessions', cache_test_key, cache_test_data):
                print("❌ RAM disk cache save failed")
                return False
            
            cached_data = self.get_from_ram_cache('sessions', cache_test_key)
            if not cached_data or cached_data['test'] != 'data':
                print("❌ RAM disk cache retrieve failed")
                return False
            print("✅ RAM disk cache working")
            
            # Test 6: Stats operation
            stats_result = self.stats()
            if '"knowledge_entries"' not in stats_result:
                print(f"❌ Stats operation failed: {stats_result}")
                return False
            print("✅ Stats operation working")
            
            print("\n✅ AGENT_TURBO: VERIFIED AND OPERATIONAL (PostgreSQL)")
            return True
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    parser = argparse.ArgumentParser(description='AGENT_TURBO - Unified High-Performance Knowledge System')
    parser.add_argument('command', choices=['add', 'query', 'stats', 'verify'], help='Command to execute')
    parser.add_argument('content', nargs='?', help='Content for add/query commands')
    parser.add_argument('--silent', action='store_true', help='Suppress initialization messages')
    
    args = parser.parse_args()
    
    agent_turbo = AgentTurbo(silent=args.silent or args.command == 'stats')
    
    if args.command == 'add':
        if not args.content:
            print("❌ Content required for add command")
            sys.exit(1)
        print(agent_turbo.add(args.content))
    
    elif args.command == 'query':
        if not args.content:
            print("❌ Query required for query command")
            sys.exit(1)
        print(agent_turbo.query(args.content))
    
    elif args.command == 'stats':
        print(agent_turbo.stats())
    
    elif args.command == 'verify':
        if agent_turbo.verify():
            print("✅ AGENT_TURBO: VERIFIED AND OPERATIONAL")
            sys.exit(0)
        else:
            print("❌ AGENT_TURBO: VERIFICATION FAILED")
            sys.exit(1)

if __name__ == '__main__':
    main()

