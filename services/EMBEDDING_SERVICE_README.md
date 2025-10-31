# Embedding Service for AYA Agent Turbo

## Status: ✅ OPERATIONAL
- **Service**: Running on port 8765
- **GPU Acceleration**: Metal enabled (80 cores)
- **Model**: BAAI/bge-base-en-v1.5 (768 dimensions)
- **Auto-start**: Configured via launchd
- **Database**: PostgreSQL 18 on port 5432 (aya_rag)

## Service Details

### Location
- **Code**: `/Users/arthurdell/AYA/services/embedding_service.py`
- **LaunchD**: `~/Library/LaunchAgents/com.aya.embedding-service.plist`
- **Logs**: `~/Library/Logs/AgentTurbo/embedding.log`

### Endpoints
- `GET /health` - Health check with Metal status
- `POST /embed` - Generate embeddings (with caching)
- `GET /stats` - Cache statistics

### Architecture
- FastAPI service with uvicorn
- MLX Metal GPU acceleration
- MD5-based caching system
- Sentence Transformers with BAAI/bge-base-en-v1.5
- 768-dimensional normalized embeddings

## What Was Fixed

1. **Port Conflict**: Task API was occupying port 8765
   - Stopped task_api launchd service
   - Freed port for embedding service

2. **Database Configuration**: Using PostgreSQL 18
   - Database: aya_rag (production)
   - Port: 5432
   - User: postgres
   - Password: Power$$336633$$

3. **Service Configuration**: Created native macOS service
   - No Docker needed (MLX is macOS-specific)
   - LaunchD for auto-start on boot
   - Proper Python path configuration

## Management Commands

### Start/Stop/Restart
```bash
# Stop service
launchctl unload ~/Library/LaunchAgents/com.aya.embedding-service.plist

# Start service
launchctl load ~/Library/LaunchAgents/com.aya.embedding-service.plist

# Restart service
launchctl unload ~/Library/LaunchAgents/com.aya.embedding-service.plist && \
launchctl load ~/Library/LaunchAgents/com.aya.embedding-service.plist

# Check status
launchctl list | grep embedding
lsof -i :8765
```

### Testing
```bash
# Health check
curl http://localhost:8765/health

# Generate embedding
curl -X POST http://localhost:8765/embed \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text here"}'

# Check statistics
curl http://localhost:8765/stats
```

### Monitoring
```bash
# View logs
tail -f ~/Library/Logs/AgentTurbo/embedding.log

# Check process
ps aux | grep embedding_service

# Monitor performance
curl http://localhost:8765/stats
```

## Integration with Agent Turbo

Agent Turbo automatically uses this service when adding knowledge:
```python
from agent_turbo import AgentTurbo
turbo = AgentTurbo()
turbo.add("Your knowledge text here")
```

The service generates embeddings via HTTP POST to localhost:8765/embed.

## PostgreSQL 18 Connection

- **Database**: aya_rag
- **Table**: agent_knowledge
- **Embedding Column**: vector type (pgvector extension)
- **Current Entries**: 122 (verified working)

## Performance Characteristics

- **Embedding Generation**: ~50-100ms first time
- **Cached Response**: <5ms
- **GPU Acceleration**: 80 Metal cores utilized
- **Vector Dimensions**: 768
- **Memory Usage**: ~500MB with model loaded
- **Cache**: MD5 hash-based, in-memory

## Troubleshooting

### Service won't start
```bash
# Check logs
tail -100 ~/Library/Logs/AgentTurbo/embedding_error.log

# Verify Python packages
python3 -c "import fastapi, sentence_transformers, mlx.core"

# Check port availability
lsof -i :8765
```

### Embeddings not generating
```bash
# Test directly
python3 /Users/arthurdell/AYA/services/embedding_service.py

# Check model download
ls -la ~/.cache/torch/sentence_transformers/
```

### PostgreSQL connection issues
```bash
# Test connection
PGPASSWORD='Power$$336633$$' psql -h localhost -p 5432 -U postgres -d aya_rag -c "SELECT 1"

# Check vector extension
PGPASSWORD='Power$$336633$$' psql -h localhost -p 5432 -U postgres -d aya_rag -c "SELECT * FROM pg_extension WHERE extname='vector'"
```

## Known Limitations

1. **macOS Only**: MLX Metal acceleration requires Apple Silicon
2. **Single Model**: Currently using BAAI/bge-base-en-v1.5 only
3. **Cache Persistence**: In-memory cache resets on restart
4. **No Batch Processing**: Single embedding per request

## Future Improvements

- Add batch embedding endpoint
- Implement persistent cache (Redis/disk)
- Support multiple embedding models
- Add request rate limiting
- Implement authentication
- Create Docker alternative for Linux deployment

---

**Last Updated**: October 28, 2025
**Verified Working**: ✅ All systems operational