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
