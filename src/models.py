from typing import Optional, List
from pydantic import BaseModel

class RawListing(BaseModel):
    id: str
    source: str
    raw_title: str
    raw_area_text: str
    raw_price_text: str
    locality: str
    image_phash: Optional[str]
    source_url: str

class NormalizedListing(BaseModel):
    id: str
    source: str
    title: str
    area_sqft: float
    price_inr: float
    price_per_sqft: float
    locality: str
    image_phash: Optional[str]
    source_url: str

class PropertyCluster(BaseModel):
    canonical_id: str
    locality: str
    median_price_inr: float
    average_area_sqft: float
    sources_count: int
    listings: List[NormalizedListing]
