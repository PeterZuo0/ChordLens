from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_ok():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["app"] == "ChordLens"


def test_cors_allows_alternate_local_vite_port():
    client = TestClient(app)

    response = client.options(
        "/api/audio/analyze",
        headers={
            "Origin": "http://127.0.0.1:5174",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5174"
