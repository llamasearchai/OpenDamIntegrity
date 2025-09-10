from fastapi.testclient import TestClient

from open_dam_integry.api import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_stability_endpoint():
    r = client.post(
        "/stability",
        json={
            "c_kpa": 8.0,
            "phi_deg": 30.0,
            "beta_deg": 18.0,
            "height_m": 15.0,
            "gamma_kN_m3": 18.5,
            "ru": 0.15,
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert "factor_of_safety" in data and "risk_level" in data
    assert data["factor_of_safety"] > 1.0


def test_agent_fallback_without_key(monkeypatch):
    # Ensure no API key in environment so service uses deterministic fallback
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    r = client.post("/agent/respond", json={"prompt": "Hello"})
    assert r.status_code == 200
    data = r.json()
    assert data["meta"]["backend"] == "deterministic"
    assert "Agents not available" in data["text"]


def test_api_key_gate_denies_without_header(monkeypatch):
    # Enable API key gate
    monkeypatch.setenv("ODI_API_KEY", "secret")
    r = client.get("/health")
    assert r.status_code == 401


def test_api_key_gate_allows_with_header(monkeypatch):
    monkeypatch.setenv("ODI_API_KEY", "secret")
    r = client.get("/health", headers={"X-API-Key": "secret"})
    assert r.status_code == 200
