# Embedding Model Name Clarification

**Date**: October 30, 2025  
**Question**: Model name `text-embedding-nomic-embed-text-v1.5` not found in LM Studio

---

## 🔍 The Issue

The embedding service was updated to use LM Studio, but the model name may be:
1. **Different in UI vs API** - UI shows one name, API uses another
2. **Not installed** - Model needs to be downloaded first
3. **Different name format** - LM Studio uses different naming

---

## 📋 Original Embedding Standard

According to `EMBEDDING_STANDARD.md`, the original production standard was:
- **Model**: `BAAI/bge-base-en-v1.5`
- **Framework**: SentenceTransformer (not LM Studio)
- **Dimensions**: 768
- **Status**: Production validated

This was the **original working implementation** before we tried to migrate to LM Studio.

---

## 🎯 Options

### Option 1: Find the Correct LM Studio Model Name

**In LM Studio UI, look for**:
- Models with "nomic" in the name
- Models with "embed" or "embedding" in the name
- Models labeled as "embedding models"

**Common variations**:
- `nomic-embed-text-v1.5`
- `nomic-embed-text`
- `nomicai-modernbert-embed-base`
- `text-embedding-nomic-embed-text` (without version)
- `nomic-embed-text-v1`

**Once you find it**:
1. Load the model in LM Studio UI
2. Share the exact name you see
3. I'll update the service code to use the correct API name

### Option 2: Revert to Original BAAI Model

If you prefer the original production-proven approach:

**Revert to**: `BAAI/bge-base-en-v1.5` via SentenceTransformer
- ✅ Already proven in production
- ✅ 768 dimensions (matches database)
- ✅ No LM Studio dependency
- ✅ Direct MLX acceleration

**To revert**:
I can update the embedding service to use SentenceTransformer directly (original implementation).

### Option 3: Install Embedding Model in LM Studio

If you want to use LM Studio but the model isn't installed:

1. **Open LM Studio**
2. **Go to "Models" tab**
3. **Search for**: "nomic embed" or "embedding"
4. **Download** an embedding model
5. **Load it**, then share the exact name

---

## 🔧 Quick Check: What Models Do You See?

Please check LM Studio and tell me:

1. **Do you see ANY embedding models?** (Yes/No)
2. **What are their exact names?** (as displayed in UI)
3. **Can you load any of them?** (Yes/No)

---

## 💡 Recommendation

Given that:
- The original `BAAI/bge-base-en-v1.5` was production-proven
- LM Studio embedding models may need special setup
- The model name discrepancy suggests a configuration issue

**Suggestion**: Either:
1. **Use what you have** - Share the embedding model name you see in LM Studio
2. **Revert to original** - Use `BAAI/bge-base-en-v1.5` via SentenceTransformer (proven to work)

Both approaches provide 768-dimensional embeddings compatible with your database.

---

**Next Step**: Please share:
- The exact embedding model name(s) you see in LM Studio UI
- OR confirm if you'd like to revert to the original BAAI/bge-base-en-v1.5 implementation

