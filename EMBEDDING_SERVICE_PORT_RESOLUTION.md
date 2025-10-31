# Embedding Service - Port 8765 Resolution

**Date**: October 30, 2025  
**Status**: Code updated ✅ | Port conflict ⚠️

---

## ✅ Code Update Complete

The embedding service has been successfully updated:
- ✅ Reverted to SentenceTransformer + BAAI/bge-base-en-v1.5
- ✅ MLX Metal acceleration enabled
- ✅ Model loads successfully (confirmed in logs)

### Logs Show Success:
```
✅ Model loaded successfully
✅ MLX Metal available: True
✅ Dimensions: 768
```

---

## ⚠️ Port Conflict Issue

**Problem**: Port 8765 is already in use by another process

**Symptoms**:
- Model loads successfully
- Service fails to bind: `[Errno 48] Address already in use`

---

## 🔧 Resolution Steps

### Step 1: Identify What's Using Port 8765

```bash
lsof -i :8765
```

This will show the process ID (PID) using the port.

### Step 2: Kill the Process

```bash
# Find the PID
PID=$(lsof -ti :8765)

# Kill it
kill -9 $PID
```

Or if LaunchAgent is managing it:
```bash
launchctl unload ~/Library/LaunchAgents/com.aya.embedding-service.plist
```

### Step 3: Verify Port is Free

```bash
lsof -i :8765 || echo "✅ Port is free"
```

### Step 4: Start the Service

```bash
cd /Users/arthurdell/AYA/services
python3 embedding_service.py > ~/Library/Logs/AgentTurbo/embedding.log 2>&1 &
```

### Step 5: Verify Service is Running

```bash
curl http://localhost:8765/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "embedding_model": "BAAI/bge-base-en-v1.5",
  "embedding_dim": 768,
  "metal_available": true
}
```

---

## 🎯 Alternative: Use LaunchAgent

Once the port is free, you can configure LaunchAgent for auto-start:

```bash
# Load LaunchAgent
launchctl load ~/Library/LaunchAgents/com.aya.embedding-service.plist

# Check status
launchctl list | grep embedding
```

---

## ✅ Verification

After resolving the port conflict:

1. **Health Check**: `curl http://localhost:8765/health`
2. **Test Embedding**: 
   ```bash
   curl -X POST http://localhost:8765/embed \
     -H "Content-Type: application/json" \
     -d '{"text": "test"}'
   ```

---

**Status**: Code is ready, just need to resolve the port conflict manually.

