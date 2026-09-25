from typing import List
from src.models import NormalizedListing, PropertyCluster
from rapidfuzz import fuzz
import imagehash
import uuid

def compute_similarity(listing_a: NormalizedListing, listing_b: NormalizedListing) -> float:
    # 1. Strict Blocking
    if listing_a.locality.lower() != listing_b.locality.lower():
        return 0.0

    score = 0.0

    # 2. Area Score (Weight 0.35)
    max_area = max(listing_a.area_sqft, listing_b.area_sqft)
    if max_area > 0:
        area_diff_pct = abs(listing_a.area_sqft - listing_b.area_sqft) / max_area
        if area_diff_pct <= 0.03:
            score += 0.35
        elif area_diff_pct <= 0.07:
            score += 0.15

    # 3. Price Score (Weight 0.25)
    max_price = max(listing_a.price_inr, listing_b.price_inr)
    if max_price > 0:
        price_diff_pct = abs(listing_a.price_inr - listing_b.price_inr) / max_price
        if price_diff_pct <= 0.10:
            score += 0.25
        elif price_diff_pct <= 0.15:
            score += 0.10

    # 4. Title/Landmark Similarity (Weight 0.20)
    title_sim = fuzz.token_ratio(listing_a.title, listing_b.title) / 100.0
    score += title_sim * 0.20

    # 5. Visual Similarity (Weight 0.20)
    if listing_a.image_phash and listing_b.image_phash:
        try:
            hash_a = imagehash.hex_to_hash(listing_a.image_phash)
            hash_b = imagehash.hex_to_hash(listing_b.image_phash)
            hamming_dist = hash_a - hash_b
            if hamming_dist <= 6:
                score += 0.20
        except ValueError:
            pass

    return score

def cluster_listings(listings: List[NormalizedListing], threshold: float = 0.70) -> List[PropertyCluster]:
    n = len(listings)
    adj = {i: [] for i in range(n)}

    # Build adjacency list based on similarity threshold
    for i in range(n):
        for j in range(i + 1, n):
            if compute_similarity(listings[i], listings[j]) >= threshold:
                adj[i].append(j)
                adj[j].append(i)

    clusters = []
    visited = set()

    # Extract connected components using BFS
    for i in range(n):
        if i not in visited:
            component_indices = []
            queue = [i]
            visited.add(i)

            while queue:
                curr = queue.pop(0)
                component_indices.append(curr)

                for neighbor in adj[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)

            current_cluster = [listings[idx] for idx in component_indices]
            clusters.append(current_cluster)

    result = []
    for cluster in clusters:
        total_price = sum(l.price_inr for l in cluster)
        total_area = sum(l.area_sqft for l in cluster)
        n = len(cluster)

        # Calculate median price properly or just use average if simpler
        # Problem requested "median_price_inr", so we calculate median
        prices = sorted([l.price_inr for l in cluster])
        mid = n // 2
        if n % 2 == 0:
            median_price = (prices[mid - 1] + prices[mid]) / 2.0
        else:
            median_price = prices[mid]

        result.append(PropertyCluster(
            canonical_id=str(uuid.uuid4()),
            locality=cluster[0].locality,
            median_price_inr=median_price,
            average_area_sqft=total_area / n,
            sources_count=len(set(l.source for l in cluster)),
            listings=cluster
        ))

    return result
