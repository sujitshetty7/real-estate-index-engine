import asyncio
from sqlmodel import Session
from src.db.crud import save_raw_listings, save_clusters, clear_db
from src.db.models import DBRawListing, DBNormalizedListing, DBPropertyCluster
from src.normalizers import normalize_area, normalize_price
from src.deduplicator import cluster_listings
from src.models import NormalizedListing, RawListing
from typing import List

def process_and_store_listings(raw_listings: List[RawListing], engine_override=None, append=False):
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

            # Skip invalid normalized data
            if area <= 0 or price <= 0:
                continue

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
        if not append:
            clear_db(session)
        save_raw_listings(session, db_raw_listings)
        save_clusters(session, db_clusters)

    print(f"Successfully processed and stored {len(normalized_objs)} valid listings and {len(clusters)} clusters.")

async def run_live_scrapers():
    from src.scrapers.nobroker import NoBrokerScraper
    from src.scrapers.squareyards import SquareYardsScraper

    print("Running live scrapers for Mumbai...")
    all_listings = []

    try:
        nb_scraper = NoBrokerScraper(locality="Mumbai")
        nb_url = 'https://www.nobroker.in/flats-for-sale-in-mumbai_mumbai'
        nb_html = await nb_scraper.fetch_page(nb_url)
        nb_listings = nb_scraper.parse(nb_html, nb_url)
        print(f"NoBroker returned {len(nb_listings)} raw listings")
        all_listings.extend(nb_listings)
    except Exception as e:
        print(f"Failed to scrape NoBroker: {e}")

    try:
        sy_scraper = SquareYardsScraper(locality="Mumbai")
        sy_url = 'https://www.squareyards.com/sale/property-for-sale-in-mumbai'
        sy_html = await sy_scraper.fetch_page(sy_url)
        sy_listings = sy_scraper.parse(sy_html, sy_url)
        print(f"SquareYards returned {len(sy_listings)} raw listings")
        all_listings.extend(sy_listings)
    except Exception as e:
        print(f"Failed to scrape SquareYards: {e}")

    return all_listings

async def run_seed():
    from src.db.database import create_db_and_tables

    create_db_and_tables()

    # Get live listings
    scraped_listings = await run_live_scrapers()

    print(f"Total live raw listings to process: {len(scraped_listings)}")

    # Process and overwrite db with live listings
    process_and_store_listings(scraped_listings, append=False)

if __name__ == "__main__":
    asyncio.run(run_seed())
