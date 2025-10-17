#!/usr/bin/env python3
import hashlib
from fastapi import FastAPI
from pydantic import BaseModel
import mlx.core as mx
from sentence_transformers import SentenceTransformer
import sys

app = FastAPI()

# Global cache and model
cache_dict = {}
model = None

class EmbedRequest(BaseModel):
    text: str

@app.on_event("startup")
async def load_model():
    global model
    try:
        # Load model with MLX Metal acceleration
        model = SentenceTransformer('BAAI/bge-base-en-v1.5')
        metal_available = mx.metal.is_available()
        print(f"Model loaded. MLX Metal available: {metal_available}", file=sys.stderr, flush=True)
    except Exception as e:
        print(f"ERROR loading model: {e}", file=sys.stderr, flush=True)
        raise

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "metal_available": mx.metal.is_available(),
        "model_loaded": model is not None
    }

@app.post("/embed")
async def embed(request: EmbedRequest):
    if model is None:
        return {"error": "Model not loaded"}, 500

    # Generate hash for cache lookup
    text_hash = hashlib.md5(request.text.encode()).hexdigest()

    # Check cache
    if text_hash in cache_dict:
        return {"embedding": cache_dict[text_hash], "cached": True}

    # Generate embedding
    embedding = model.encode([request.text], normalize_embeddings=True)
    vector = embedding[0].tolist()

    # Cache result
    cache_dict[text_hash] = vector

    return {"embedding": vector, "cached": False}

@app.get("/stats")
async def stats():
    return {
        "cache_size": len(cache_dict),
        "metal_available": mx.metal.is_available()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)
