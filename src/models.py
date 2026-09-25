from typing import Optional, List
from pydantic import BaseModel

class RawListing(BaseModel):
    id: str
    source: str
    raw_title: str
    raw_area_text: str
    raw_price_text: str
    locality: str
    image_phash: Optional[str] = None
    source_url: str
    property_type: Optional[str] = None
    bhk: Optional[int] = None
    bathrooms: Optional[int] = None
    status: Optional[str] = None
    rera_id: Optional[str] = None
    builder: Optional[str] = None
    possession_date: Optional[str] = None
    last_checked_at: Optional[str] = None

class NormalizedListing(BaseModel):
    id: str
    source: str
    title: str
    area_sqft: float
    price_inr: float
    price_per_sqft: float
    locality: str
    image_phash: Optional[str] = None
    source_url: str
    property_type: Optional[str] = None
    bhk: Optional[int] = None
    bathrooms: Optional[int] = None
    status: Optional[str] = None
    rera_id: Optional[str] = None
    builder: Optional[str] = None
    possession_date: Optional[str] = None
    last_checked_at: Optional[str] = None

class PropertyCluster(BaseModel):
    canonical_id: str
    locality: str
    median_price_inr: float
    average_area_sqft: float
    sources_count: int
    property_type: Optional[str] = None
    bhk: Optional[int] = None
    bathrooms: Optional[int] = None
    status: Optional[str] = None
    rera_id: Optional[str] = None
    builder: Optional[str] = None
    possession_date: Optional[str] = None
    last_checked_at: Optional[str] = None
    listings: List[NormalizedListing]
