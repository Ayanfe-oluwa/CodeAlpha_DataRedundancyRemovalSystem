import os
from fastapi.testclient import TestClient

# Use a separate local test database so tests do not touch a developer's normal DB.
os.environ["DATABASE_URL"] = "sqlite:///./test_redundancy.db"

from app.main import app
from app.database import Base, engine

def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_unique_record_is_inserted():
    response = client.post("/records", json={
        "name": "Mary James",
        "email": "mary@example.com",
        "description": "First record"
    })
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "unique"
    assert body["inserted"] is True

def test_exact_duplicate_is_not_inserted():
    payload = {"name": "John Smith", "email": "john@example.com", "description": "Customer"}
    first = client.post("/records", json=payload)
    second = client.post("/records", json=payload)
    assert first.json()["status"] == "unique"
    assert second.json()["status"] == "duplicate"
    assert second.json()["inserted"] is False
    assert len(client.get("/records").json()) == 1

def test_same_email_different_details_is_flagged():
    client.post("/records", json={
        "name": "John Smith", "email": "john@example.com", "description": "Customer"
    })
    response = client.post("/records", json={
        "name": "John Adams", "email": "JOHN@example.com", "description": "Different details"
    })
    assert response.json()["status"] == "potential_conflict"
    assert response.json()["inserted"] is False
    assert len(client.get("/records").json()) == 1

def test_invalid_email_is_rejected():
    response = client.post("/records", json={"name": "Alex", "email": "not-an-email"})
    assert response.status_code == 422

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
