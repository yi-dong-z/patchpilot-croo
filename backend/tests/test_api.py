from fastapi.testclient import TestClient

from patchpilot.api import app
from patchpilot.evidence import store


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_demo_contract():
    response = client.get("/api/demo")
    assert response.status_code == 200
    body = response.json()
    assert body["result"]["status"] == "resolved"
    assert len(body["result"]["downstream_orders"]) == 2
    assert body["result"]["mode"] == "mock"


def test_invalid_mission_returns_inline_error_contract():
    response = client.post("/api/missions", json={"repo_url": "https://example.com"})
    assert response.status_code == 422
    assert "repo_url" in response.json()["detail"]


def test_live_evidence_requires_secret(monkeypatch):
    monkeypatch.setenv("EVIDENCE_INGEST_TOKEN", "test-secret")
    denied = client.post("/api/live-evidence", json={"result": {"mode": "live"}})
    assert denied.status_code == 401
    accepted = client.post(
        "/api/live-evidence",
        headers={"Authorization": "Bearer test-secret"},
        json={"request": {"repo_url": "https://github.com/a/b"}, "result": {"mode": "live"}},
    )
    assert accepted.status_code == 202
    store(None)
