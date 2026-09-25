from src.sample_data import sample_listings
from src.models import NormalizedListing
from src.normalizers import normalize_area, normalize_price
from src.deduplicator import cluster_listings

def process_listings(raw_listings):
    normalized = []

    for raw in raw_listings:
        try:
            area = normalize_area(raw.raw_area_text)
            price = normalize_price(raw.raw_price_text)

            normalized.append(
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
            print(f"Failed to normalize listing {raw.id}: {e}")

    return normalized

def main():
    print("--- Starting Pipeline ---")
    print(f"Loaded {len(sample_listings)} raw listings.")

    normalized_listings = process_listings(sample_listings)
    print(f"Successfully normalized {len(normalized_listings)} listings.")

    clusters = cluster_listings(normalized_listings, threshold=0.70)
    print(f"\n--- Discovered {len(clusters)} Property Clusters ---")

    for idx, cluster in enumerate(clusters, 1):
        print(f"\nCluster {idx}: {cluster.locality}")
        print(f"  Canonical ID: {cluster.canonical_id}")
        print(f"  Listings Count: {len(cluster.listings)} from {cluster.sources_count} sources")
        print(f"  Median Price: ₹{cluster.median_price_inr:,.2f}")
        print(f"  Average Area: {cluster.average_area_sqft:,.2f} sqft")

        print("  Included Listings:")
        for l in cluster.listings:
            print(f"    - [{l.source}] {l.title} (₹{l.price_inr:,.2f} / {l.area_sqft:,.2f} sqft)")

if __name__ == "__main__":
    main()
