from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_system_health():
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "APEX AI Engine"

def test_system_config():
    response = client.get("/api/v1/system/config")
    assert response.status_code == 200
    assert "PORT" in response.json()
