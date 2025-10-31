# Embedding Service - Model Name Verification

**Date**: October 30, 2025  
**Issue**: Model name `text-embedding-nomic-embed-text-v1.5` not found in LM Studio UI

---

## 🔍 Model Name Clarification

### Possible Model Names in LM Studio

The embedding model name in the **LM Studio UI** may differ from the **API model name**. Here are the possibilities:

#### Option 1: LM Studio UI vs API Naming
- **UI Display Name**: May show as just "nomic-embed-text" or "Nomic Embed Text v1.5"
- **API Model Name**: `text-embedding-nomic-embed-text-v1.5`
- **Action**: Load the model in UI, then use the API name

#### Option 2: Alternative Model Name
- **Model**: `nomicai-modernbert-embed-base`
- **Dimensions**: May differ (need to verify)
- **Status**: Also listed in documentation as available

#### Option 3: Original Standard (BAAI/bge-base-en-v1.5)
- **Model**: `BAAI/bge-base-en-v1.5` via SentenceTransformer
- **Status**: This was the original embedding standard
- **Implementation**: Direct MLX, not via LM Studio

---

## 🔧 How to Find the Correct Model Name

### Step 1: Check LM Studio UI

1. **Open LM Studio** on ALPHA
2. **Go to "Models" or "Chat" tab**
3. **Look for embedding models** - they typically have names like:
   - `nomic-embed-text`
   - `nomic-embed-text-v1.5`
   - `nomic-embed-text-v1`
   - `nomic-embed`
   - `modernbert-embed`
   - Any model with "embed" or "nomic" in the name

### Step 2: Load the Model in UI

1. **Select the embedding model** from the list
2. **Click "Load"** button
3. **Verify** it shows as "Loaded"

### Step 3: Check API Model Name

Once loaded, check what the API reports:

```bash
curl -s http://localhost:1234/v1/models | python3 -m json.tool | grep -A 2 -i "embed\|nomic"
```

Look for the model's `id` field - that's the API name to use.

---

## 🔄 Update Service Code

Once you identify the correct model name, update the service:

**File**: `/Users/arthurdell/AYA/services/embedding_service.py`

**Line 16**: Change `EMBEDDING_MODEL` to the correct model name

```python
EMBEDDING_MODEL = "correct-model-name-here"  # Update this
EMBEDDING_DIM = 768  # May need to update if dimensions differ
```

---

## 📋 Alternative: Use Original BAAI Model

If LM Studio embedding models aren't available, we can revert to the original SentenceTransformer approach:

**Original Standard**:
- Model: `BAAI/bge-base-en-v1.5`
- Dimensions: 768
- Framework: SentenceTransformer + MLX
- Status: Production validated

This would require updating the embedding service to use SentenceTransformer directly instead of LM Studio API.

---

## ✅ Quick Action Steps

1. **Open LM Studio UI** on ALPHA
2. **Find embedding models** in the model list
3. **Share the exact model name** you see in the UI
4. **Or load the model** and we'll check the API name

Once you provide the model name, I'll update the service code accordingly.

---

## 🎯 Next Steps

**Option A**: If you find the model in LM Studio UI:
- Share the exact name displayed
- Load it in the UI
- I'll update the service code with the correct API name

**Option B**: If no embedding models are in LM Studio:
- We can use the original `BAAI/bge-base-en-v1.5` via SentenceTransformer
- This was the production standard before

**Option C**: Download/Install embedding model:
- Install `nomic-embed-text-v1.5` or similar in LM Studio
- Then use it via the API

---

**Current Status**: Waiting for model name clarification  
**Service**: ✅ Running and ready  
**Code**: ✅ Waiting for correct model name

