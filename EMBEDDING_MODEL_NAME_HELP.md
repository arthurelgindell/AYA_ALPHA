# Finding the Correct Embedding Model Name

## Issue
The model name `text-embedding-nomic-embed-text-v1.5` doesn't appear in LM Studio UI.

## How to Find the Model

### Step 1: Open LM Studio
- Open LM Studio application on ALPHA
- Look at the **Models** tab or **Chat** tab

### Step 2: Search for Embedding Models
Look for models with these keywords:
- `nomic`
- `embed`
- `embedding`
- `nomic-embed`
- `modernbert`

### Step 3: Check the Display Name
The UI may show:
- `nomic-embed-text-v1.5`
- `Nomic Embed Text v1.5`
- `nomic-embed-text`
- `nomicai-modernbert-embed-base`
- Or a similar variation

### Step 4: Load the Model
1. Select the embedding model
2. Click **"Load"**
3. Wait for it to load into memory

### Step 5: Verify API Name
Once loaded, the API name (used in code) may differ from UI name.

---

## Alternative: Check What You Have Installed

In LM Studio UI:
1. Go to **Settings** or **Models** section
2. Check **Downloaded/Installed** models
3. Look for any embedding models

---

## What to Share

Please share:
1. **Exact name** you see in LM Studio UI
2. **Whether you can load it**
3. **Any error messages** when trying to load

---

## Quick Options

**Option 1**: Use what you have
- Share the model name you see
- I'll update the code to use it

**Option 2**: Use original standard
- Revert to `BAAI/bge-base-en-v1.5` (SentenceTransformer)
- This was the original production standard

**Option 3**: Install new model
- Download an embedding model in LM Studio
- Then configure the service to use it
