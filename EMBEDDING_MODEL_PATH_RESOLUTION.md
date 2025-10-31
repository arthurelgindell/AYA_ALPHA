# Embedding Model Path Resolution

**Date**: October 30, 2025  
**Issue Resolved**: Model `text-embedding-nomic-embed-text-v1.5` not found in LM Studio UI

---

## 🔍 Root Cause

**Problem**: The model name `text-embedding-nomic-embed-text-v1.5` is:
- ✅ Reported by LM Studio API (`/v1/models`)
- ❌ **NOT a file path** - it's an API identifier
- ❌ **NOT selectable** in LM Studio UI
- ❌ **NOT actually installed** as files

---

## ✅ Actual Available Models

**Model Files Found**:
```
/Users/arthurdell/AYA/models/mlx-community/
├── nomicai-modernbert-embed-base-4bit/  ✅ (has model.safetensors)
├── nomicai-modernbert-embed-base-8bit/  ✅ (has model.safetensors)
├── nomicai-modernbert-embed-base-6bit/  ❌ (empty)
└── nomicai-modernbert-embed-base-bf16/  ❌ (empty)
```

**API Model Names**:
- `nomicai-modernbert-embed-base@4bit` (768 dimensions)
- `nomicai-modernbert-embed-base@8bit` (768 dimensions)
- `text-embedding-nomic-embed-text-v1.5` (virtual identifier - not real)

---

## 🎯 Solution

**Update embedding service** to use the **actual available models**:

### Option 1: Use `nomicai-modernbert-embed-base@4bit` (Recommended)
- ✅ Has model files
- ✅ 768 dimensions (matches database)
- ✅ Lower memory usage (4-bit quantization)

### Option 2: Use `nomicai-modernbert-embed-base@8bit`
- ✅ Has model files
- ✅ 768 dimensions (matches database)
- ⚠️ Higher memory usage (8-bit quantization)

---

## 📝 Model Path Details

**File System Path**:
```
/Users/arthurdell/AYA/models/mlx-community/nomicai-modernbert-embed-base-4bit/
├── config.json
├── model.safetensors (84MB)
├── model.safetensors.index.json
└── ... (other config files)
```

**LM Studio API Name**:
```
nomicai-modernbert-embed-base@4bit
```

**Dimensions**: 768 (confirmed from config.json)

---

## 🔧 Required Changes

1. **Update embedding service code**:
   ```python
   # Change from:
   EMBEDDING_MODEL = "text-embedding-nomic-embed-text-v1.5"
   
   # To:
   EMBEDDING_MODEL = "nomicai-modernbert-embed-base@4bit"
   ```

2. **Verify dimensions remain 768** (already confirmed ✅)

3. **Test embedding generation** after update

---

## ✅ Verification

After updating, test:
```bash
curl -X POST http://localhost:1234/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model":"nomicai-modernbert-embed-base@4bit","input":"test"}'
```

**Expected**: Returns 768-dimensional embedding vector

---

**Status**: Ready to update service code  
**Recommendation**: Use `nomicai-modernbert-embed-base@4bit`

