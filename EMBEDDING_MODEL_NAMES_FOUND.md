# Embedding Model Names - Available in LM Studio

**Date**: October 30, 2025  
**Status**: ✅ Models Found via API

---

## ✅ Available Embedding Models

LM Studio API reports these embedding models are available:

1. **text-embedding-nomic-embed-text-v1.5**
   - Status: Available but needs to be loaded
   - This is the model name currently in the service code

2. **nomicai-modernbert-embed-base@4bit**
   - Status: Quantized 4-bit version
   - May have different dimensions

3. **nomicai-modernbert-embed-base@8bit**
   - Status: Quantized 8-bit version
   - May have different dimensions

---

## 🔍 Finding the Model in LM Studio UI

The **UI name may differ** from the API name. Here's what to look for:

### In LM Studio UI:

1. **Open LM Studio** on ALPHA

2. **Go to "Chat" or "Local Server" tab**

3. **Look for models with these keywords**:
   - `nomic`
   - `embed` or `embedding`
   - `modernbert`

4. **Common UI display names**:
   - `nomic-embed-text` (without version)
   - `nomic-embed-text-v1.5`
   - `Nomic Embed Text v1.5`
   - `modernbert-embed-base`
   - `nomicai-modernbert-embed-base`

5. **The model might show as**:
   - With or without version number
   - With or without "text-embedding-" prefix
   - With quantization suffix (@4bit, @8bit) or without

---

## ⚠️ Important: Model Must Be Loaded

**Even if you find the model, you must LOAD it in LM Studio UI** before the API can use it.

**Steps**:
1. Find the embedding model in the list
2. **Select it** (click on it)
3. **Click "Load"** button
4. Wait for "Loaded" status
5. Then the API will work

---

## 🔧 If You Still Can't Find It

### Option 1: Use Quantized Versions

The service can use:
- `nomicai-modernbert-embed-base@4bit`
- `nomicai-modernbert-embed-base@8bit`

These may work without needing to find the exact name in UI.

### Option 2: Check LM Studio Server Status

In LM Studio:
1. Go to **"Local Server"** tab
2. Check if **server is running**
3. Verify port **1234** is active
4. Make sure a model is **loaded** (any model)

### Option 3: Use Original BAAI Model

Revert to production-proven `BAAI/bge-base-en-v1.5` via SentenceTransformer (original standard).

---

## 🎯 What to Do Next

**Please check LM Studio UI and tell me**:

1. **Do you see any models with "nomic" or "embed" in the name?** (Yes/No)
2. **What is the exact name displayed?** (exact text)
3. **Can you load it?** (Yes/No)
4. **If not found, should we**:
   - Try the quantized versions?
   - Revert to original BAAI/bge-base-en-v1.5?

---

## 📋 Quick Test

Once you load a model in LM Studio UI, test:

```bash
curl -X POST http://localhost:1234/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model":"text-embedding-nomic-embed-text-v1.5","input":"test"}'
```

If this works after loading, the service will work too.

---

**Available API Names**: 
- `text-embedding-nomic-embed-text-v1.5`
- `nomicai-modernbert-embed-base@4bit`
- `nomicai-modernbert-embed-base@8bit`

**Action**: Load one of these in LM Studio UI, then the service will work.

