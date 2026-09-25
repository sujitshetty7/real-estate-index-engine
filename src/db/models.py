from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
import uuid

class DBRawListing(SQLModel, table=True):
    id: str = Field(primary_key=True)
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

class DBNormalizedListing(SQLModel, table=True):
    id: str = Field(primary_key=True)
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
    cluster_id: Optional[str] = Field(default=None, foreign_key="dbpropertycluster.canonical_id")

    cluster: Optional["DBPropertyCluster"] = Relationship(back_populates="listings")

class DBPropertyCluster(SQLModel, table=True):
    canonical_id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
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

    listings: List[DBNormalizedListing] = Relationship(back_populates="cluster")
