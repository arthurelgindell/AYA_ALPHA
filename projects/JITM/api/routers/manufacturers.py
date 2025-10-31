"""
JITM Manufacturers Router
AI-powered manufacturer search and management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import requests
import logging
import os

from api.database import get_db
from api.models import ManufacturerResponse, ManufacturerCreate, ManufacturerSearch

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[ManufacturerResponse])
async def list_manufacturers(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    status: str = Query("active"),
    db: Session = Depends(get_db)
):
    """List manufacturers with pagination"""
    try:
        result = db.execute(text("""
            SELECT id, company_name, contact_name, email, phone, website,
                   country, capabilities, certifications, rating, review_count,
                   status, created_at
            FROM jitm_manufacturers
            WHERE status = :status
            ORDER BY rating DESC, company_name
            LIMIT :limit OFFSET :offset
        """), {"status": status, "limit": limit, "offset": offset})
        
        return [dict(row._mapping) for row in result]
    except Exception as e:
        logger.error(f"Error listing manufacturers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=List[ManufacturerResponse])
async def search_manufacturers(
    search: ManufacturerSearch,
    db: Session = Depends(get_db)
):
    """
    AI-powered manufacturer search using Agent Turbo embeddings
    
    Generates embedding for search query and finds similar manufacturers
    using pgvector cosine similarity
    """
    try:
        # Generate embedding via Agent Turbo
        agent_turbo_url = os.getenv('AGENT_TURBO_URL', 'http://localhost:8765')
        
        try:
            response = requests.post(
                f"{agent_turbo_url}/embed",
                json={"text": search.query},
                timeout=5
            )
            response.raise_for_status()
            embedding = response.json()['embedding']
        except Exception as e:
            logger.warning(f"Agent Turbo embedding failed: {e}, falling back to text search")
            # Fallback to text-based search
            result = db.execute(text("""
                SELECT id, company_name, contact_name, email, phone, website,
                       country, capabilities, certifications, rating, review_count,
                       status, created_at
                FROM jitm_manufacturers
                WHERE 
                    (company_name ILIKE :query OR 
                     capabilities::text ILIKE :query OR
                     certifications::text ILIKE :query)
                    AND status = 'active'
                    AND (:min_rating IS NULL OR rating >= :min_rating)
                    AND (:country IS NULL OR country = :country)
                ORDER BY rating DESC
                LIMIT :limit
            """), {
                "query": f"%{search.query}%",
                "min_rating": search.min_rating,
                "country": search.country,
                "limit": search.limit
            })
            return [dict(row._mapping) for row in result]
        
        # Use pgvector similarity search
        result = db.execute(text("""
            SELECT 
                id, company_name, contact_name, email, phone, website,
                country, capabilities, certifications, rating, review_count,
                status, created_at,
                (embedding <=> :embedding::vector) as similarity
            FROM jitm_manufacturers
            WHERE 
                embedding IS NOT NULL
                AND status = 'active'
                AND (:min_rating IS NULL OR rating >= :min_rating)
                AND (:country IS NULL OR country = :country)
            ORDER BY embedding <=> :embedding::vector
            LIMIT :limit
        """), {
            "embedding": str(embedding),
            "min_rating": search.min_rating,
            "country": search.country,
            "limit": search.limit
        })
        
        manufacturers = [dict(row._mapping) for row in result]
        logger.info(f"Found {len(manufacturers)} manufacturers for query: {search.query}")
        return manufacturers
        
    except Exception as e:
        logger.error(f"Error searching manufacturers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{manufacturer_id}", response_model=ManufacturerResponse)
async def get_manufacturer(
    manufacturer_id: str,
    db: Session = Depends(get_db)
):
    """Get manufacturer by ID"""
    try:
        result = db.execute(text("""
            SELECT id, company_name, contact_name, email, phone, website,
                   country, capabilities, certifications, rating, review_count,
                   status, created_at
            FROM jitm_manufacturers
            WHERE id = :id
        """), {"id": manufacturer_id})
        
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Manufacturer not found")
        
        return dict(row._mapping)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching manufacturer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=ManufacturerResponse, status_code=201)
async def create_manufacturer(
    manufacturer: ManufacturerCreate,
    db: Session = Depends(get_db)
):
    """Create new manufacturer (with optional AI embedding generation)"""
    try:
        # Generate embedding for manufacturer profile
        profile_text = f"{manufacturer.company_name} {manufacturer.capabilities} {manufacturer.certifications}"
        
        embedding = None
        try:
            agent_turbo_url = os.getenv('AGENT_TURBO_URL', 'http://localhost:8765')
            response = requests.post(
                f"{agent_turbo_url}/embed",
                json={"text": profile_text},
                timeout=5
            )
            if response.ok:
                embedding = response.json()['embedding']
        except:
            logger.warning("Could not generate embedding for new manufacturer")
        
        # Insert manufacturer
        result = db.execute(text("""
            INSERT INTO jitm_manufacturers 
            (company_name, contact_name, email, phone, website, country,
             capabilities, certifications, embedding, status)
            VALUES 
            (:company_name, :contact_name, :email, :phone, :website, :country,
             :capabilities::jsonb, :certifications::jsonb, :embedding::vector, 'active')
            RETURNING id, company_name, contact_name, email, phone, website,
                      country, capabilities, certifications, rating, review_count,
                      status, created_at
        """), {
            "company_name": manufacturer.company_name,
            "contact_name": manufacturer.contact_name,
            "email": manufacturer.email,
            "phone": manufacturer.phone,
            "website": manufacturer.website,
            "country": manufacturer.country,
            "capabilities": str(manufacturer.capabilities),
            "certifications": str(manufacturer.certifications),
            "embedding": str(embedding) if embedding else None
        })
        
        db.commit()
        row = result.fetchone()
        return dict(row._mapping)
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating manufacturer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

