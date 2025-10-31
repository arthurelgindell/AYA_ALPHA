"""
JITM Pydantic Models
Request/Response schemas for API
"""

from pydantic import BaseModel, Field, UUID4
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# System Info
class SystemInfo(BaseModel):
    system_name: str
    system_id: int
    cluster_mode: bool
    peer_systems: List[str]
    postgres_host: str
    redis_host: str
    agent_turbo_url: str
    n8n_webhook_url: str
    api_version: str
    timestamp: str

# Enums
class ProjectStatus(str, Enum):
    draft = "draft"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"

class RFQStatus(str, Enum):
    draft = "draft"
    sent = "sent"
    responded = "responded"
    accepted = "accepted"
    rejected = "rejected"

# Manufacturer Models
class ManufacturerBase(BaseModel):
    company_name: str
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    country: str = "China"
    capabilities: Dict[str, Any] = {}
    certifications: Dict[str, Any] = {}

class ManufacturerCreate(ManufacturerBase):
    pass

class ManufacturerResponse(ManufacturerBase):
    id: UUID4
    rating: float
    review_count: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ManufacturerSearch(BaseModel):
    query: str = Field(..., description="Search query for manufacturer matching")
    limit: int = Field(10, ge=1, le=100)
    min_rating: Optional[float] = Field(None, ge=0, le=10)
    country: Optional[str] = None

# Project Models
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    project_type: str = "campaign"
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    currency: str = "USD"
    target_completion_date: Optional[datetime] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: UUID4
    status: str
    priority: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# RFQ Models
class RFQBase(BaseModel):
    product_id: UUID4
    manufacturer_id: UUID4
    quantity: int
    target_price: Optional[float] = None
    required_delivery_date: Optional[datetime] = None

class RFQCreate(RFQBase):
    pass

class RFQResponse(RFQBase):
    id: UUID4
    rfq_number: str
    status: str
    sent_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Quote Models
class QuoteBase(BaseModel):
    rfq_id: UUID4
    manufacturer_id: UUID4
    quantity: int
    unit_price: float
    total_price: float
    currency: str = "USD"
    lead_time_days: Optional[int] = None

class QuoteCreate(QuoteBase):
    pass

class QuoteResponse(QuoteBase):
    id: UUID4
    status: str
    quote_valid_until: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Health Check
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    system: str
    database: str

