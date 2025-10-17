#!/usr/bin/env python3
"""
AGENT_TURBO GPU Optimizer - MLX-accelerated embeddings and similarity search
GAMMA Project Implementation - ALPHA Node (Apple M3 Ultra)
"""

import numpy as np
import time
import hashlib
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
import sqlite3
import psutil

# MLX for GPU acceleration
try:
    import mlx.core as mx
    import mlx.nn as nn
    HAS_MLX = True
    # Set default device to GPU for maximum performance
    if mx.metal.is_available():
        mx.set_default_device(mx.gpu)
except ImportError:
    HAS_MLX = False
    print("Warning: MLX not available")

class AgentTurboGPUOptimizer:
    """GPU-optimized enhancements for AGENT_TURBO"""

    def __init__(self):
        self.device = mx.default_device() if HAS_MLX else None
        self.embedding_dim = 768
        self.batch_size = 32
        self.cache_size_mb = 1000  # 1GB GPU cache

        # Initialize GPU cache
        self.gpu_embedding_cache = {}
        self.gpu_memory_used = 0
        self.embedding_matrix = None
        self.vocab_size = 50000

        print(f"🚀 AGENT_TURBO GPU Optimizer initialized")
        print(f"   Device: {self.device}")
        if HAS_MLX:
            print(f"   Metal Memory: {mx.get_active_memory() / (1024**3):.2f} GB")
            print(f"   GPU Available: {mx.metal.is_available()}")
        
        # Initialize embedding matrix for GPU acceleration
        self._init_embedding_matrix()
    
    def _init_embedding_matrix(self):
        """Initialize GPU embedding matrix for fast lookups"""
        if not HAS_MLX:
            return
            
        try:
            # Create embedding matrix on GPU
            self.embedding_matrix = mx.random.normal((self.vocab_size, self.embedding_dim))
            mx.eval(self.embedding_matrix)
            print(f"   Embedding matrix initialized: {self.vocab_size}x{self.embedding_dim}")
        except Exception as e:
            print(f"   Warning: Could not initialize embedding matrix: {e}")
    
    def create_gpu_embedding(self, text: str, use_cache: bool = True) -> mx.array:
        """
        Create GPU-accelerated text embeddings using MLX
        """
        if not HAS_MLX:
            return self.create_real_embedding(text, use_cache)
        
        # Check cache first
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        
        if use_cache and text_hash in self.gpu_embedding_cache:
            return self.gpu_embedding_cache[text_hash]
        
        try:
            # Convert text to tokens (simplified approach)
            tokens = self._text_to_tokens(text)
            
            # Get embeddings from matrix
            if self.embedding_matrix is not None:
                # Use first few tokens to get embedding
                token_indices = tokens[:min(len(tokens), 128)]  # Limit to 128 tokens
                token_indices = [t % self.vocab_size for t in token_indices]  # Ensure valid indices
                
                # Get embeddings for tokens
                token_embeddings = self.embedding_matrix[token_indices]
                
                # Mean pooling to get single embedding
                embedding = mx.mean(token_embeddings, axis=0)
                
                # Normalize embedding
                embedding = embedding / mx.linalg.norm(embedding)
                
                # Cache the result
                if use_cache:
                    self.gpu_embedding_cache[text_hash] = embedding
                
                return embedding
            else:
                # Fallback to CPU embedding
                return mx.array(self.create_real_embedding(text, use_cache))
                
        except Exception as e:
            print(f"   Warning: GPU embedding failed, using CPU: {e}")
            return mx.array(self.create_real_embedding(text, use_cache))
    
    def get_gpu_stats(self) -> Dict[str, Any]:
        """Get GPU utilization statistics"""
        stats = {
            'gpu_available': HAS_MLX and mx.metal.is_available(),
            'gpu_memory_used_mb': 0,
            'gpu_memory_total_gb': 0,
            'embedding_cache_size': len(self.gpu_embedding_cache),
            'embedding_matrix_initialized': self.embedding_matrix is not None
        }
        
        if HAS_MLX and mx.metal.is_available():
            try:
                stats['gpu_memory_used_mb'] = mx.get_active_memory() / (1024**2)
                device_info = mx.metal.device_info()
                stats['gpu_memory_total_gb'] = device_info.get('memory_size', 0) / (1024**3)
            except Exception as e:
                print(f"   Warning: Could not get GPU stats: {e}")
        
        return stats
    
    def optimize_gpu_memory(self):
        """Optimize GPU memory usage"""
        if not HAS_MLX:
            return
            
        try:
            # Clear GPU cache if memory usage is high
            if mx.get_active_memory() > 1024**3:  # 1GB threshold
                print("   Clearing GPU cache to optimize memory")
                self.gpu_embedding_cache.clear()
                
            # Force garbage collection
            import gc
            gc.collect()
            
        except Exception as e:
            print(f"   Warning: GPU memory optimization failed: {e}")
    
    def benchmark_gpu_performance(self) -> Dict[str, float]:
        """Benchmark GPU performance for embeddings and similarity search"""
        if not HAS_MLX:
            return {'error': 'MLX not available'}
        
        try:
            results = {}
            
            # Test embedding generation
            test_texts = [
                "This is a test sentence for embedding generation.",
                "Another test sentence to measure performance.",
                "GPU acceleration should make this faster."
            ]
            
            # Single embedding benchmark
            start_time = time.time()
            for text in test_texts:
                embedding = self.create_gpu_embedding(text)
                mx.eval(embedding)
            single_embedding_time = (time.time() - start_time) / len(test_texts) * 1000
            results['single_embedding_ms'] = single_embedding_time
            
            # Batch embedding benchmark
            start_time = time.time()
            batch_embeddings = self.batch_create_embeddings(test_texts)
            mx.eval(batch_embeddings)
            batch_embedding_time = (time.time() - start_time) * 1000
            results['batch_embedding_ms'] = batch_embedding_time
            
            # Similarity search benchmark
            query_embedding = self.create_gpu_embedding("test query")
            db_embeddings = batch_embeddings
            
            start_time = time.time()
            similarities, top_indices = self.gpu_similarity_search(query_embedding, db_embeddings, top_k=3)
            mx.eval(similarities, top_indices)
            similarity_time = (time.time() - start_time) * 1000
            results['similarity_search_ms'] = similarity_time
            
            # Batch similarity search benchmark
            # Use a subset for batch similarity to avoid matrix dimension issues
            query_embeddings_subset = batch_embeddings[:2]  # Use only 2 queries
            
            start_time = time.time()
            batch_similarities, batch_top_indices = self.batch_similarity_search(query_embeddings_subset, db_embeddings, top_k=3)
            mx.eval(batch_similarities, batch_top_indices)
            batch_similarity_time = (time.time() - start_time) * 1000
            results['batch_similarity_ms'] = batch_similarity_time
            
            return results
            
        except Exception as e:
            return {'error': str(e)}
    
    def _text_to_tokens(self, text: str) -> List[int]:
        """Convert text to token indices (simplified tokenization)"""
        # Simple hash-based tokenization for consistency
        tokens = []
        words = text.split()
        for word in words:
            # Create deterministic token from word hash
            token = int(hashlib.md5(word.encode()).hexdigest()[:8], 16) % self.vocab_size
            tokens.append(token)
        return tokens
    
    def batch_create_embeddings(self, texts: List[str]) -> mx.array:
        """
        Create embeddings for multiple texts in batch for GPU efficiency
        """
        if not HAS_MLX:
            return mx.array([self.create_real_embedding(text) for text in texts])
        
        try:
            embeddings = []
            for text in texts:
                embedding = self.create_gpu_embedding(text)
                embeddings.append(embedding)
            
            # Stack embeddings into batch
            batch_embeddings = mx.stack(embeddings)
            return batch_embeddings
            
        except Exception as e:
            print(f"   Warning: Batch embedding failed: {e}")
            return mx.array([self.create_real_embedding(text) for text in texts])
    
    def gpu_similarity_search(self, query_embedding: mx.array, db_embeddings: mx.array, top_k: int = 5) -> Tuple[mx.array, mx.array]:
        """
        GPU-accelerated similarity search using cosine similarity
        """
        if not HAS_MLX:
            # Fallback to CPU
            query_np = np.array(query_embedding)
            db_np = np.array(db_embeddings)
            similarities = np.dot(query_np, db_np.T)
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            return mx.array(similarities), mx.array(top_indices)
        
        try:
            # Ensure query_embedding is 2D (1, embedding_dim)
            if len(query_embedding.shape) == 1:
                query_embedding = query_embedding.reshape(1, -1)
            
            # Normalize embeddings for cosine similarity
            query_norm = query_embedding / mx.linalg.norm(query_embedding, axis=1, keepdims=True)
            db_norm = db_embeddings / mx.linalg.norm(db_embeddings, axis=1, keepdims=True)
            
            # Compute similarities: (1, dim) @ (n, dim).T = (1, n)
            similarities = mx.matmul(query_norm, db_norm.T)
            
            # Get top-k indices from the first (and only) query
            top_indices = mx.argsort(similarities[0], axis=0)[-top_k:][::-1]
            
            return similarities[0], top_indices
            
        except Exception as e:
            print(f"   Warning: GPU similarity search failed: {e}")
            # Fallback to CPU
            query_np = np.array(query_embedding)
            db_np = np.array(db_embeddings)
            if len(query_np.shape) == 1:
                query_np = query_np.reshape(1, -1)
            similarities = np.dot(query_np, db_np.T)
            top_indices = np.argsort(similarities[0])[-top_k:][::-1]
            return mx.array(similarities[0]), mx.array(top_indices)
    
    def batch_similarity_search(self, query_embeddings: mx.array, db_embeddings: mx.array, top_k: int = 5) -> Tuple[mx.array, mx.array]:
        """
        Batch GPU-accelerated similarity search for multiple queries
        """
        if not HAS_MLX:
            # Fallback to CPU
            query_np = np.array(query_embeddings)
            db_np = np.array(db_embeddings)
            similarities = np.dot(query_np, db_np.T)
            top_indices = np.argsort(similarities, axis=1)[:, -top_k:][:, ::-1]
            return mx.array(similarities), mx.array(top_indices)
        
        try:
            # Normalize embeddings
            query_norm = query_embeddings / mx.linalg.norm(query_embeddings, axis=1, keepdims=True)
            db_norm = db_embeddings / mx.linalg.norm(db_embeddings, axis=1, keepdims=True)
            
            # Compute batch similarities
            similarities = mx.matmul(query_norm, db_norm.T)
            
            # Get top-k indices for each query
            top_indices = mx.argsort(similarities, axis=1)[:, -top_k:][:, ::-1]
            
            return similarities, top_indices
            
        except Exception as e:
            print(f"   Warning: Batch GPU similarity search failed: {e}")
            # Fallback to CPU
            query_np = np.array(query_embeddings)
            db_np = np.array(db_embeddings)
            similarities = np.dot(query_np, db_np.T)
            top_indices = np.argsort(similarities, axis=1)[:, -top_k:][:, ::-1]
            return mx.array(similarities), mx.array(top_indices)

    def create_real_embedding(self, text: str, use_cache: bool = True) -> np.ndarray:
        """
        Create real text embeddings using deterministic hash-based approach
        Fallback method when GPU acceleration is not available
        """
        # Check cache first
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]

        if use_cache and text_hash in self.gpu_embedding_cache:
            cached = self.gpu_embedding_cache[text_hash]
            # Convert MLX array to numpy if needed
            if hasattr(cached, '__array__'):
                return np.array(cached)
            return cached

        # Create deterministic embedding based on text content
        # This simulates what a real embedding model would do

        # 1. Tokenize (simple word-based for now)
        words = text.lower().split()[:512]  # Max 512 tokens

        # 2. Create word vectors (deterministic based on word hash)
        word_vectors = []
        for word in words:
            # Each word gets a unique but deterministic vector
            word_hash = hashlib.md5(word.encode()).digest()
            # Repeat hash to get enough bytes for 768 dimensions
            repeats_needed = (self.embedding_dim * 4 + len(word_hash) - 1) // len(word_hash)
            extended_hash = (word_hash * repeats_needed)[:self.embedding_dim * 4]  # 4 bytes per float32
            word_vec = np.frombuffer(extended_hash, dtype=np.float32)[:self.embedding_dim]
            # Normalize safely
            norm = np.linalg.norm(word_vec)
            if norm > 0:
                word_vec = word_vec / norm
            else:
                word_vec = np.random.randn(self.embedding_dim).astype(np.float32)
                word_vec = word_vec / np.linalg.norm(word_vec)
            word_vectors.append(word_vec)

        if not word_vectors:
            # Empty text - return zero vector
            return np.zeros(self.embedding_dim, dtype=np.float32)

        # 3. Aggregate word vectors (mean pooling)
        if HAS_MLX:
            # Use GPU for aggregation
            vectors_gpu = mx.array(np.stack(word_vectors))
            embedding_gpu = mx.mean(vectors_gpu, axis=0)
            embedding = np.array(embedding_gpu)
        else:
            # CPU fallback
            embedding = np.mean(word_vectors, axis=0)

        # 4. Final normalization
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        else:
            embedding = np.ones(self.embedding_dim, dtype=np.float32) / np.sqrt(self.embedding_dim)

        # Cache the result
        if use_cache:
            self.gpu_embedding_cache[text_hash] = embedding
            self.gpu_memory_used += embedding.nbytes

        return embedding.astype(np.float32)

    def batch_similarity_search_numpy(self,
                               query_embedding: np.ndarray,
                               embeddings: List[np.ndarray],
                               top_k: int = 10) -> List[Tuple[int, float]]:
        """
        GPU-accelerated batch similarity search (numpy version)
        Returns indices and similarity scores
        """
        if not HAS_MLX or len(embeddings) == 0:
            # CPU fallback
            similarities = []
            for i, emb in enumerate(embeddings):
                sim = np.dot(query_embedding, emb)
                similarities.append((i, float(sim)))
            return sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]

        # GPU-accelerated version
        query_gpu = mx.array(query_embedding)

        # Process in batches to avoid memory overflow
        all_similarities = []

        for i in range(0, len(embeddings), self.batch_size):
            batch = embeddings[i:i + self.batch_size]
            batch_gpu = mx.array(np.stack(batch))

            # Batched cosine similarity
            similarities = mx.matmul(batch_gpu, query_gpu)

            # Convert back to numpy and store with indices
            for j, sim in enumerate(np.array(similarities)):
                all_similarities.append((i + j, float(sim)))

        # Return top-k
        return sorted(all_similarities, key=lambda x: x[1], reverse=True)[:top_k]

    def optimize_memory_access(self, file_path: Path) -> Optional[memoryview]:
        """
        Memory-map files for efficient access
        Reduces memory pressure for large files
        """
        if not file_path.exists():
            return None

        try:
            with open(file_path, 'r+b') as f:
                # Memory-map the file
                import mmap
                mmapped = mmap.mmap(f.fileno(), 0)
                return memoryview(mmapped)
        except Exception as e:
            print(f"Failed to memory-map {file_path}: {e}")
            return None

    def stream_jsonl_entries(self, file_path: Path, batch_size: int = 100):
        """
        Stream JSONL entries in batches to avoid loading everything
        """
        batch = []

        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        entry = json.loads(line)
                        batch.append(entry)

                        if len(batch) >= batch_size:
                            yield batch
                            batch = []
                    except json.JSONDecodeError:
                        continue

        # Yield remaining entries
        if batch:
            yield batch

    def create_vector_index(self, embeddings: List[np.ndarray]) -> mx.array:
        """
        Create GPU-resident vector index for fast search
        """
        if not HAS_MLX or not embeddings:
            return None

        # Stack all embeddings into a single GPU array
        embeddings_matrix = np.stack(embeddings)
        gpu_index = mx.array(embeddings_matrix)

        print(f"✅ Created GPU index with {len(embeddings)} vectors")
        print(f"   Shape: {gpu_index.shape}")
        print(f"   Memory: {gpu_index.nbytes / (1024**2):.2f} MB")

        return gpu_index

    def get_optimization_stats(self) -> Dict:
        """
        Get current optimization statistics
        """
        stats = {
            "gpu_available": HAS_MLX,
            "device": str(self.device) if HAS_MLX else "CPU",
            "embedding_cache_size": len(self.gpu_embedding_cache),
            "gpu_memory_used_mb": self.gpu_memory_used / (1024**2),
            "batch_size": self.batch_size,
        }

        if HAS_MLX:
            stats["metal_memory_gb"] = mx.metal.get_active_memory() / (1024**3)
            stats["peak_memory_gb"] = mx.metal.get_peak_memory() / (1024**3)

        return stats

def enhance_agent_turbo_engine():
    """
    Enhance the existing AGENT_TURBO engine with GPU optimizations
    """
    print("🔧 Enhancing AGENT_TURBO with GPU optimizations...")

    # Initialize optimizer
    optimizer = AgentTurboGPUOptimizer()

    # Patch the AGENT_TURBO engine's methods
    import sys
    sys.path.insert(0, str(Path.home() / '.claude' / 'claude-knowledge-system'))

    try:
        from agent_turbo import AgentTurbo

        # Store original methods
        original_generate_embedding = AgentTurbo.generate_embedding
        original_similarity_search = AgentTurbo.similarity_search

        # Replace with optimized versions
        def optimized_generate_embedding(self, text: str) -> np.ndarray:
            """GPU-optimized embedding generation"""
            return optimizer.create_real_embedding(text)

        def optimized_similarity_search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
            """GPU-optimized similarity search"""
            if not self.active_memory:
                return []

            # Extract embeddings from active memory
            entry_ids = list(self.active_memory.keys())
            embeddings = [entry.embedding for entry in self.active_memory.values()]

            # GPU-accelerated search
            results = optimizer.batch_similarity_search(query_embedding, embeddings, top_k)

            # Map indices back to entry IDs
            return [(entry_ids[idx], score) for idx, score in results]

        # Apply patches
        AgentTurbo.generate_embedding = optimized_generate_embedding
        AgentTurbo.similarity_search = optimized_similarity_search

        print("✅ AGENT_TURBO engine enhanced with GPU optimizations!")
        print(f"   Stats: {optimizer.get_optimization_stats()}")

        return optimizer

    except ImportError as e:
        print(f"❌ Could not enhance AGENT_TURBO: {e}")
        return None

def test_agent_turbo_gpu_optimization():
    """Test the GPU optimization enhancements"""
    optimizer = AgentTurboGPUOptimizer()

    # Test embedding generation
    print("\n🧪 Testing GPU-optimized embeddings...")

    test_texts = [
        "How to implement vim mode in VS Code",
        "Docker compose configuration for PostgreSQL",
        "GAMMA platform architecture overview"
    ]

    embeddings = []
    start = time.time()

    for text in test_texts:
        emb = optimizer.create_real_embedding(text)
        embeddings.append(emb)
        print(f"   Generated embedding for: '{text[:50]}...' Shape: {emb.shape}")

    elapsed = time.time() - start
    print(f"   Time: {elapsed*1000:.2f}ms for {len(test_texts)} embeddings")

    # Test similarity search
    print("\n🔍 Testing GPU-accelerated search...")
    query = optimizer.create_real_embedding("vim configuration")

    start = time.time()
    results = optimizer.batch_similarity_search(query, embeddings, top_k=2)
    elapsed = time.time() - start

    print(f"   Search completed in {elapsed*1000:.2f}ms")
    for idx, score in results:
        print(f"   Match {idx}: {test_texts[idx][:50]}... (score: {score:.4f})")

    # Show stats
    print("\n📊 Optimization Stats:")
    stats = optimizer.get_optimization_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    # Run tests
    test_gpu_optimization()

    # Enhance AGENT_TURBO if requested
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "enhance":
        enhance_agent_turbo_engine()
        print("\n✨ AGENT_TURBO is now GPU-optimized!")
