import pytest
from src.models import NormalizedListing
from src.deduplicator import compute_similarity, cluster_listings

@pytest.fixture
def mock_listings():
    return [
        NormalizedListing(
            id="1", source="a", title="5 Guntha Plot", area_sqft=5445.0,
            price_inr=9200000.0, price_per_sqft=1689.6, locality="Shahapur",
            image_phash="a1b2c3d4e5f60000", source_url="http://a.com/1"
        ),
        NormalizedListing(
            id="2", source="b", title="5445 sqft prime land", area_sqft=5445.0,
            price_inr=9000000.0, price_per_sqft=1652.89, locality="Shahapur",
            image_phash="a1b2c3d4e5f60000", source_url="http://b.com/2"
        ),
        NormalizedListing(
            id="3", source="c", title="Different locality", area_sqft=5445.0,
            price_inr=9200000.0, price_per_sqft=1689.6, locality="Karjat",
            image_phash="a1b2c3d4e5f60000", source_url="http://c.com/3"
        )
    ]

def test_compute_similarity(mock_listings):
    l1, l2, l3 = mock_listings

    # Same locality, same area, same phash, similar price
    score_1_2 = compute_similarity(l1, l2)
    assert score_1_2 > 0.70

    # Different locality should result in 0 score
    score_1_3 = compute_similarity(l1, l3)
    assert score_1_3 == 0.0

def test_cluster_listings(mock_listings):
    clusters = cluster_listings(mock_listings, threshold=0.70)
    # Expect 2 clusters: {l1, l2} and {l3}
    assert len(clusters) == 2

    # Check that l1 and l2 are in the same cluster
    cluster_1 = next(c for c in clusters if len(c.listings) == 2)
    assert cluster_1.locality == "Shahapur"
    assert cluster_1.sources_count == 2

    cluster_2 = next(c for c in clusters if len(c.listings) == 1)
    assert cluster_2.locality == "Karjat"

def test_transitive_matching():
    # A matches B, B matches C, but A doesn't strictly match C well enough to cross the threshold on its own.
    # Due to connected components, they should all end up in the same cluster.

    # Create 3 listings
    l_a = NormalizedListing(
        id="A", source="src1", title="10 Guntha land in Pune", area_sqft=10890.0,
        price_inr=10000000.0, price_per_sqft=918.27, locality="Pune",
        image_phash="1111111111111111", source_url="urlA"
    )

    # B matches A's area perfectly, and has same phash. Similar title.
    # So A matches B strongly.
    l_b = NormalizedListing(
        id="B", source="src2", title="10 Guntha plot Pune", area_sqft=10890.0,
        price_inr=10500000.0, price_per_sqft=964.18, locality="Pune",
        image_phash="1111111111111111", source_url="urlB"
    )

    # C matches B because price is identical to B, title is similar to B.
    # But C's image is completely different from A and B, and area is different from A.
    l_c = NormalizedListing(
        id="C", source="src3", title="Plot 10 Guntha Pune", area_sqft=11200.0, # closer area to bump score
        price_inr=10500000.0, price_per_sqft=913.04, locality="Pune",
        image_phash="9999999999999999", source_url="urlC"
    )

    # Let's verify our assumptions about their direct similarities
    sim_a_b = compute_similarity(l_a, l_b)
    sim_b_c = compute_similarity(l_b, l_c)
    sim_a_c = compute_similarity(l_a, l_c)

    # Set threshold such that A-B and B-C pass, but A-C fails
    # Force threshold strictly between the required boundaries
    threshold = sim_a_c + 0.01

    assert sim_a_b >= threshold
    assert sim_b_c >= threshold
    assert sim_a_c < threshold

    listings = [l_a, l_b, l_c]
    clusters = cluster_listings(listings, threshold=threshold)

    # Since A matches B and B matches C, all three should be in 1 cluster
    assert len(clusters) == 1
    assert len(clusters[0].listings) == 3
    assert {l.id for l in clusters[0].listings} == {"A", "B", "C"}
