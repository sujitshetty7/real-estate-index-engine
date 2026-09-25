import asyncio
from sqlmodel import Session
from src.db.crud import save_raw_listings, save_clusters, clear_db
from src.db.models import DBRawListing, DBNormalizedListing, DBPropertyCluster
from src.normalizers import normalize_area, normalize_price
from src.deduplicator import cluster_listings
from src.models import NormalizedListing, RawListing
from typing import List

def process_and_store_listings(raw_listings: List[RawListing], engine_override=None):
    from src.db.database import engine as default_engine
    target_engine = engine_override if engine_override else default_engine

    # 1. Normalize
    normalized_objs = []
    db_raw_listings = []

    for raw in raw_listings:
        # Create DB Raw Model
        db_raw_listings.append(DBRawListing(
            id=raw.id,
            source=raw.source,
            raw_title=raw.raw_title,
            raw_area_text=raw.raw_area_text,
            raw_price_text=raw.raw_price_text,
            locality=raw.locality,
            image_phash=raw.image_phash,
            source_url=raw.source_url
        ))

        try:
            area = normalize_area(raw.raw_area_text)
            price = normalize_price(raw.raw_price_text)

            normalized_objs.append(
                NormalizedListing(
                    id=raw.id,
                    source=raw.source,
                    title=raw.raw_title,
                    area_sqft=area,
                    price_inr=price,
                    price_per_sqft=price / area if area > 0 else 0,
                    locality=raw.locality,
                    image_phash=raw.image_phash,
                    source_url=raw.source_url
                )
            )
        except Exception as e:
            print(f"Failed to normalize {raw.id}: {e}")

    # 2. Cluster
    clusters = cluster_listings(normalized_objs, threshold=0.70)

    # 3. Store in DB
    db_clusters = []
    for c in clusters:
        db_cluster = DBPropertyCluster(
            canonical_id=c.canonical_id,
            locality=c.locality,
            median_price_inr=c.median_price_inr,
            average_area_sqft=c.average_area_sqft,
            sources_count=c.sources_count,
            listings=[]
        )

        for l in c.listings:
            db_cluster.listings.append(
                DBNormalizedListing(
                    id=l.id,
                    source=l.source,
                    title=l.title,
                    area_sqft=l.area_sqft,
                    price_inr=l.price_inr,
                    price_per_sqft=l.price_per_sqft,
                    locality=l.locality,
                    image_phash=l.image_phash,
                    source_url=l.source_url,
                    cluster_id=c.canonical_id
                )
            )
        db_clusters.append(db_cluster)

    with Session(target_engine) as session:
        clear_db(session)
        save_raw_listings(session, db_raw_listings)
        save_clusters(session, db_clusters)

    print(f"Successfully processed and stored {len(raw_listings)} listings and {len(clusters)} clusters.")

async def run_seed():
    from src.db.database import create_db_and_tables
    from src.sample_data import sample_listings
    from src.scrapers.generic_html import GenericHTMLScraper

    create_db_and_tables()

    # 1. First run the scrapers to simulate web ingestion
    # For demonstration, we create a mock HTML to parse since we don't have a real URL setup
    mock_html = """
    <html>
        <body>
            <div class="property-card">
                <h2 class="title">10 Guntha land near Karjat Station</h2>
                <span class="area">10 Guntha</span>
                <span class="price">1.5 Cr</span>
            </div>
            <div class="property-card">
                <h2 class="title">Farm Plot Lonavala Hill</h2>
                <span class="area">5000 sqft</span>
                <span class="price">40 Lakh</span>
            </div>
        </body>
    </html>
    """

    scraper = GenericHTMLScraper(
        source_name="mock_directory",
        selectors={
            "container": ".property-card",
            "title": ".title",
            "area": ".area",
            "price": ".price"
        },
        locality="Karjat/Lonavala"
    )

    print("Scraping properties...")
    scraped_listings = scraper.parse(mock_html, source_url="http://mock-directory.com/listings")

    # 2. Combine with sample listings
    all_listings = sample_listings + scraped_listings

    print(f"Total raw listings to process: {len(all_listings)}")
    process_and_store_listings(all_listings)

if __name__ == "__main__":
    asyncio.run(run_seed())
