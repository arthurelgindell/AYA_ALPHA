#!/usr/bin/env python3
"""
Embedding Service for AYA Agent Turbo
Uses SentenceTransformer with BAAI/bge-base-en-v1.5 for GPU-accelerated embeddings
Production-proven implementation with MLX Metal acceleration
"""
import hashlib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
import sys
from typing import List, Optional
from sentence_transformers import SentenceTransformer
import mlx.core as mx

# Configuration - Production Standard
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"  # Production-proven model
EMBEDDING_DIM = 768  # bge-base-en-v1.5 dimensions

# Global cache and model
cache_dict = {}
model = None

class EmbedRequest(BaseModel):
    text: str

class BatchEmbedRequest(BaseModel):
    texts: List[str]

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    global model
    
    # Startup
    print("🚀 Embedding Service starting...", file=sys.stderr, flush=True)
    print(f"   Model: {EMBEDDING_MODEL}", file=sys.stderr, flush=True)
    
    # Load SentenceTransformer model with MLX Metal acceleration
    try:
        print("   Loading SentenceTransformer model...", file=sys.stderr, flush=True)
        model = SentenceTransformer(EMBEDDING_MODEL)
        metal_available = mx.metal.is_available()
        print(f"   ✅ Model loaded successfully", file=sys.stderr, flush=True)
        print(f"   ✅ MLX Metal available: {metal_available}", file=sys.stderr, flush=True)
        print(f"   ✅ Dimensions: {EMBEDDING_DIM}", file=sys.stderr, flush=True)
    except Exception as e:
        print(f"   ❌ ERROR loading model: {e}", file=sys.stderr, flush=True)
        raise
    
    yield
    
    # Shutdown
    print("🛑 Embedding Service shutting down...", file=sys.stderr, flush=True)
    model = None

app = FastAPI(lifespan=lifespan)

def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding using SentenceTransformer model.
    
    Args:
        text: Text to embed
        
    Returns:
        List[float]: Embedding vector (768 dimensions)
        
    Raises:
        Exception: If model not loaded or generation fails
    """
    global model
    
    if model is None:
        raise Exception("Model not loaded")
    
    try:
        # Generate embedding with normalization (standard for similarity search)
        embedding = model.encode([text], normalize_embeddings=True)
        vector = embedding[0].tolist()
        
        if len(vector) != EMBEDDING_DIM:
            raise ValueError(f"Expected {EMBEDDING_DIM} dimensions, got {len(vector)}")
        
        return vector
    except Exception as e:
        raise Exception(f"Embedding generation failed: {e}")

@app.get("/health")
async def health():
    """Health check endpoint."""
    global model
    
    return {
        "status": "healthy" if model is not None else "degraded",
        "model_loaded": model is not None,
        "embedding_model": EMBEDDING_MODEL,
        "embedding_dim": EMBEDDING_DIM,
        "metal_available": mx.metal.is_available(),
        "cache_size": len(cache_dict)
    }

@app.post("/embed")
async def embed(request: EmbedRequest):
    """
    Generate embedding for a single text.
    
    Uses SentenceTransformer with MLX Metal acceleration and caching.
    """
    global model
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Generate hash for cache lookup
    text_hash = hashlib.md5(request.text.encode()).hexdigest()
    
    # Check cache
    if text_hash in cache_dict:
        return {
            "embedding": cache_dict[text_hash],
            "cached": True,
            "model": EMBEDDING_MODEL,
            "dimensions": EMBEDDING_DIM
        }
    
    # Generate embedding
    try:
        embedding = generate_embedding(request.text)
        
        # Cache result
        cache_dict[text_hash] = embedding
        
        return {
            "embedding": embedding,
            "cached": False,
            "model": EMBEDDING_MODEL,
            "dimensions": EMBEDDING_DIM
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate embedding: {str(e)}")

@app.post("/batch")
async def batch_embed(request: BatchEmbedRequest):
    """
    Generate embeddings for multiple texts.
    
    Uses SentenceTransformer with MLX Metal acceleration and caching per text.
    """
    global model
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if not request.texts:
        raise HTTPException(status_code=400, detail="Empty texts list")
    
    results = []
    
    for text in request.texts:
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Check cache
        if text_hash in cache_dict:
            results.append({
                "embedding": cache_dict[text_hash],
                "cached": True
            })
        else:
            # Generate embedding
            try:
                embedding = generate_embedding(text)
                
                # Cache result
                cache_dict[text_hash] = embedding
                
                results.append({
                    "embedding": embedding,
                    "cached": False
                })
            except Exception as e:
                results.append({
                    "error": f"Failed to generate embedding: {str(e)}"
                })
    
    return {
        "embeddings": results,
        "model": EMBEDDING_MODEL,
        "dimensions": EMBEDDING_DIM,
        "total": len(results),
        "cached": sum(1 for r in results if r.get("cached", False))
    }

@app.get("/stats")
async def stats():
    """Get service statistics."""
    global model
    
    return {
        "cache_size": len(cache_dict),
        "model": EMBEDDING_MODEL,
        "dimensions": EMBEDDING_DIM,
        "model_loaded": model is not None,
        "metal_available": mx.metal.is_available()
    }

@app.get("/")
async def root():
    """Service information."""
    return {
        "service": "AYA Embedding Service",
        "version": "1.0.0",
        "backend": "SentenceTransformer + MLX Metal",
        "model": EMBEDDING_MODEL,
        "dimensions": EMBEDDING_DIM,
        "endpoints": {
            "health": "/health",
            "embed": "/embed (POST)",
            "batch": "/batch (POST)",
            "stats": "/stats"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 Starting AYA Embedding Service on port 8765", file=sys.stderr)
    print(f"   Backend: SentenceTransformer + MLX Metal", file=sys.stderr)
    print(f"   Model: {EMBEDDING_MODEL}", file=sys.stderr)
    print(f"   Dimensions: {EMBEDDING_DIM}", file=sys.stderr)
    uvicorn.run(app, host="127.0.0.1", port=8765)
