import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from src.api.main import app, get_session

# Use an in-memory SQLite database for testing
connect_args = {"check_same_thread": False}
# In memory sqlite drops tables as soon as connection closes. By using StaticPool we keep the DB in memory for all threads
from sqlalchemy.pool import StaticPool
engine = create_engine(
    "sqlite:///:memory:",
    connect_args=connect_args,
    poolclass=StaticPool
)

def get_session_override():
    with Session(engine) as session:
        yield session

app.dependency_overrides[get_session] = get_session_override

client = TestClient(app)

@pytest.fixture(autouse=True)
def prepare_database():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    # Do not call process_and_store_listings in fixture body that might cause issues with thread local session
    yield
    SQLModel.metadata.drop_all(engine)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<!DOCTYPE html>" in response.text
    assert "Real Estate Indexer" in response.text

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_ingest_sample():
    response = client.post("/api/ingest/sample")
    assert response.status_code == 200
    assert "Successfully ingested" in response.json()["message"]

def test_search_properties_no_filters():
    client.post("/api/ingest/sample")
    response = client.get("/api/properties")
    assert response.status_code == 200
    clusters = response.json()["clusters"]
    assert len(clusters) > 0

def test_search_properties_locality_filter():
    client.post("/api/ingest/sample")
    response = client.get("/api/properties?locality=Shahapur")
    assert response.status_code == 200
    clusters = response.json()["clusters"]
    assert len(clusters) > 0
    for cluster in clusters:
        assert "shahapur" in cluster["locality"].lower()

def test_search_properties_price_filter():
    client.post("/api/ingest/sample")
    # Looking for cheap plots
    response = client.get("/api/properties?max_price=5000000") # 50 Lakh
    assert response.status_code == 200
    clusters = response.json()["clusters"]
    assert len(clusters) > 0
    for cluster in clusters:
        assert cluster["median_price_inr"] <= 5000000.0

def test_search_properties_area_filter():
    client.post("/api/ingest/sample")
    response = client.get("/api/properties?min_area_sqft=50000")
    assert response.status_code == 200
    clusters = response.json()["clusters"]
    assert len(clusters) > 0
    for cluster in clusters:
        assert cluster["average_area_sqft"] >= 50000.0

def test_search_properties_sorting():
    client.post("/api/ingest/sample")
    response = client.get("/api/properties?sort_by=price_asc")
    assert response.status_code == 200
    clusters = response.json()["clusters"]

    prices = [c["median_price_inr"] for c in clusters]
    assert prices == sorted(prices)

def test_get_property_cluster_details():
    client.post("/api/ingest/sample")
    # First get a list of properties
    response = client.get("/api/properties?locality=Karjat")
    clusters = response.json()["clusters"]
    assert len(clusters) > 0

    canonical_id = clusters[0]["canonical_id"]

    # Fetch details
    details_response = client.get(f"/api/properties/{canonical_id}")
    assert details_response.status_code == 200

    details = details_response.json()
    assert details["canonical_id"] == canonical_id
    assert "listings" in details
    assert len(details["listings"]) > 0
    assert "source_url" in details["listings"][0]
