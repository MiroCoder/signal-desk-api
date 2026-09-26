from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_tickets_requires_auth():
    response = client.get("/tickets")
    assert response.status_code == 401

def test_tickets_rejects_invalid_token():
    response = client.get(
        "/tickets",
        headers={"Authorization": "Bearer abc123"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}