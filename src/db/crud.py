from sqlmodel import Session, select
from typing import List, Optional
from src.db.models import DBRawListing, DBNormalizedListing, DBPropertyCluster

def save_raw_listings(session: Session, raw_listings: List[DBRawListing]):
    for listing in raw_listings:
        session.add(listing)
    session.commit()

def save_clusters(session: Session, clusters: List[DBPropertyCluster]):
    for cluster in clusters:
        session.add(cluster)
    session.commit()

def get_clusters(session: Session, locality: Optional[str] = None,
                 min_price: Optional[float] = None, max_price: Optional[float] = None,
                 min_area: Optional[float] = None, max_area: Optional[float] = None,
                 max_price_per_sqft: Optional[float] = None,
                 property_type: Optional[str] = None,
                 bhk: Optional[str] = None,
                 status: Optional[str] = None,
                 builder: Optional[str] = None,
                 sort_by: Optional[str] = None) -> List[DBPropertyCluster]:

    query = select(DBPropertyCluster)

    if locality:
        query = query.where(DBPropertyCluster.locality.ilike(f"%{locality}%"))
    if min_price is not None:
        query = query.where(DBPropertyCluster.median_price_inr >= min_price)
    if max_price is not None:
        query = query.where(DBPropertyCluster.median_price_inr <= max_price)
    if min_area is not None:
        query = query.where(DBPropertyCluster.average_area_sqft >= min_area)
    if max_area is not None:
        query = query.where(DBPropertyCluster.average_area_sqft <= max_area)

    if property_type:
        query = query.where(DBPropertyCluster.property_type.ilike(f"%{property_type}%"))
    if builder:
        query = query.where(DBPropertyCluster.builder.ilike(f"%{builder}%"))
    if status:
        query = query.where(DBPropertyCluster.status.ilike(f"%{status}%"))
    if bhk:
        if bhk.endswith("+"):
            try:
                min_bhk = int(bhk[:-1])
                query = query.where(DBPropertyCluster.bhk >= min_bhk)
            except ValueError:
                pass
        else:
            try:
                exact_bhk = int(bhk)
                query = query.where(DBPropertyCluster.bhk == exact_bhk)
            except ValueError:
                pass

    if sort_by == "price_asc":
        query = query.order_by(DBPropertyCluster.median_price_inr.asc())
    elif sort_by == "price_desc":
        query = query.order_by(DBPropertyCluster.median_price_inr.desc())
    elif sort_by == "area_desc":
        query = query.order_by(DBPropertyCluster.average_area_sqft.desc())

    results = session.exec(query).all()

    if max_price_per_sqft is not None:
        filtered_results = []
        for cluster in results:
            if cluster.average_area_sqft > 0:
                cluster_pps = cluster.median_price_inr / cluster.average_area_sqft
                if cluster_pps <= max_price_per_sqft:
                    filtered_results.append(cluster)
        return filtered_results

    return results

def get_cluster_by_id(session: Session, canonical_id: str) -> Optional[DBPropertyCluster]:
    return session.get(DBPropertyCluster, canonical_id)

def clear_db(session: Session):
    try:
        session.exec(select(DBNormalizedListing)).all() # Check if table exists

        # Use simple deletes to avoid query API warnings
        from sqlmodel import delete
        session.exec(delete(DBNormalizedListing))
        session.exec(delete(DBPropertyCluster))
        session.exec(delete(DBRawListing))
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Warning: could not clear DB tables: {e}")
