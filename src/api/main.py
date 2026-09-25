from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, SQLModel
from src.db.database import get_session, create_db_and_tables, engine
import os
from src.db.crud import get_clusters, get_cluster_by_id
from src.scrapers.seed_runner import process_and_store_listings, run_live_scrapers
from src.sample_data import sample_listings
from typing import List, Optional
import asyncio

app = FastAPI(title="Real Estate Indexer API")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Mount static files if needed for other assets, but we'll serve index.html directly on /
# app.mount("/static", StaticFiles(directory="src/static"), name="static")

@app.get("/", response_class=HTMLResponse)
def read_root():
    # Provide absolute path to static/index.html to be safe when running from different locations
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    index_path = os.path.join(base_dir, "static", "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/properties")
def search_properties(
    locality: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_area_sqft: Optional[float] = None,
    max_area_sqft: Optional[float] = None,
    max_price_per_sqft: Optional[float] = None,
    sort_by: Optional[str] = Query(None, pattern="^(price_asc|price_desc|area_desc)$"),
    session: Session = Depends(get_session)
):
    # Ensure tables are created first for tests
    SQLModel.metadata.create_all(session.bind)
    clusters = get_clusters(
        session,
        locality=locality,
        min_price=min_price,
        max_price=max_price,
        min_area=min_area_sqft,
        max_area=max_area_sqft,
        max_price_per_sqft=max_price_per_sqft,
        sort_by=sort_by
    )

    # Let's return them with minimal listing info
    clusters_data = []
    for c in clusters:
        clusters_data.append({
            "canonical_id": c.canonical_id,
            "locality": c.locality,
            "median_price_inr": c.median_price_inr,
            "average_area_sqft": c.average_area_sqft,
            "sources_count": c.sources_count,
            "listings": [
                {
                    "title": l.title,
                    "price_inr": l.price_inr,
                    "source": l.source,
                    "area_sqft": l.area_sqft
                } for l in c.listings
            ]
        })

    return {"clusters": clusters_data}

@app.get("/api/properties/{canonical_id}")
def get_property_cluster(canonical_id: str, session: Session = Depends(get_session)):
    # Ensure tables are created first for tests
    SQLModel.metadata.create_all(session.bind)
    cluster = get_cluster_by_id(session, canonical_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Property cluster not found")

    return {
        "canonical_id": cluster.canonical_id,
        "locality": cluster.locality,
        "median_price_inr": cluster.median_price_inr,
        "average_area_sqft": cluster.average_area_sqft,
        "sources_count": cluster.sources_count,
        "listings": [
            {
                "id": l.id,
                "source": l.source,
                "title": l.title,
                "area_sqft": l.area_sqft,
                "price_inr": l.price_inr,
                "price_per_sqft": l.price_per_sqft,
                "source_url": l.source_url
            } for l in cluster.listings
        ]
    }

@app.post("/api/ingest/sample")
def ingest_sample_data(session: Session = Depends(get_session)):
    # Since dependencies override engine, we can pass engine bound to the session for tests
    # Ensure tables are created first
    SQLModel.metadata.create_all(session.bind)
    process_and_store_listings(sample_listings, engine_override=session.bind)
    return {"message": "Successfully ingested sample data and updated clusters"}

@app.post("/api/ingest/live")
async def ingest_live_data(session: Session = Depends(get_session)):
    SQLModel.metadata.create_all(session.bind)
    scraped_listings = await run_live_scrapers()
    if scraped_listings:
        process_and_store_listings(scraped_listings, engine_override=session.bind, append=False)
        return {"message": f"Successfully scraped and stored {len(scraped_listings)} live listings."}
    return {"message": "No live listings found."}
