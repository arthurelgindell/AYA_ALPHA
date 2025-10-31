"""
JITM API - Just-In-Time Manufacturing Orchestration
Production-grade FastAPI application

Clustered deployment across ALPHA + BETA
PostgreSQL aya_rag backend
Agent Turbo AI integration
n8n workflow automation
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
import sys
import logging
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import init_db, get_db_session
from api.routers import manufacturers, projects, rfqs, quotes, contracts, orders, logistics
from api.models import SystemInfo

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup resources"""
    logger.info(f"Starting JITM API on {os.getenv('SYSTEM_NAME', 'unknown')}")
    
    # Initialize database connection
    init_db()
    logger.info("Database connection initialized")
    
    yield
    
    logger.info("Shutting down JITM API")

# Create FastAPI application
app = FastAPI(
    title="JITM API",
    description="Just-In-Time Manufacturing Orchestration System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(manufacturers.router, prefix="/api/v1/manufacturers", tags=["Manufacturers"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(rfqs.router, prefix="/api/v1/rfqs", tags=["RFQs"])
app.include_router(quotes.router, prefix="/api/v1/quotes", tags=["Quotes"])
app.include_router(contracts.router, prefix="/api/v1/contracts", tags=["Contracts"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["Orders"])
app.include_router(logistics.router, prefix="/api/v1/logistics", tags=["Logistics"])

@app.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    return {
        "service": "JITM API",
        "version": "1.0.0",
        "system": os.getenv('SYSTEM_NAME', 'unknown'),
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/health", response_model=dict)
async def health_check():
    """Health check endpoint for Docker"""
    try:
        # Test database connection
        with get_db_session() as db:
            db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "system": os.getenv('SYSTEM_NAME', 'unknown'),
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

@app.get("/system/info", response_model=SystemInfo)
async def system_info():
    """System information and cluster status"""
    return {
        "system_name": os.getenv('SYSTEM_NAME', 'unknown'),
        "system_id": int(os.getenv('SYSTEM_ID', 0)),
        "cluster_mode": os.getenv('CLUSTER_MODE', 'false') == 'true',
        "peer_systems": os.getenv('PEER_SYSTEMS', '').split(',') if os.getenv('PEER_SYSTEMS') else [],
        "postgres_host": os.getenv('POSTGRES_HOST', 'unknown'),
        "redis_host": os.getenv('REDIS_HOST', 'unknown'),
        "agent_turbo_url": os.getenv('AGENT_TURBO_URL', 'unknown'),
        "n8n_webhook_url": os.getenv('N8N_WEBHOOK_URL', 'unknown'),
        "api_version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=os.getenv('LOG_LEVEL', 'info').lower()
    )

