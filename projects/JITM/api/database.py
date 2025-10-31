"""
JITM Database Module
PostgreSQL aya_rag connection and session management
"""

import os
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import logging

logger = logging.getLogger(__name__)

# Database connection from environment
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'aya_rag')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')

# Build connection string
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using
    echo=os.getenv('LOG_LEVEL', 'info').lower() == 'debug'
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database connection and verify tables"""
    try:
        with engine.connect() as conn:
            # Test connection
            result = conn.execute(text("SELECT 1"))
            logger.info(f"Database connection successful: {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
            
            # Verify JITM tables exist
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_name LIKE 'jitm_%'
            """))
            count = result.fetchone()[0]
            logger.info(f"Found {count} JITM tables in database")
            
            if count < 10:
                logger.warning("Expected 10 JITM tables, verify schema is deployed")
            
            return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

@contextmanager
def get_db_session() -> Session:
    """Get database session with automatic cleanup"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def get_db():
    """Dependency for FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

