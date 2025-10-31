# Embedding Service - Quick Start

**Status**: ✅ Configured | ⏳ Load Model in LM Studio

## One-Time Setup

1. **Load Model in LM Studio**:
   - Open LM Studio → Select `text-embedding-nomic-embed-text-v1.5` → Click "Load"

2. **Verify Service**:
   ```bash
   curl http://127.0.0.1:8765/health
   ```

3. **Test Embedding**:
   ```bash
   curl -X POST http://127.0.0.1:8765/embed \
     -H "Content-Type: application/json" \
     -d '{"text": "test"}'
   ```

## Service URLs

- **Local**: `http://127.0.0.1:8765`
- **Tailscale**: `https://alpha.tail5f2bae.ts.net/embedding` (after Tailscale serve config)

## Auto-Start

```bash
launchctl load ~/Library/LaunchAgents/com.aya.embedding-service.plist
```

## Tailscale Access

```bash
sudo /Applications/Tailscale.app/Contents/MacOS/Tailscale serve \
  --bg --set-path=/embedding --http=8765
```

✅ **Service is ready - just load the model in LM Studio!**
