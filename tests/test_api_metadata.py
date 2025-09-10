from fastapi.testclient import TestClient

from open_dam_integry.api import app


def test_metadata_endpoint_returns_version_and_agent():
    client = TestClient(app)
    r = client.get("/metadata")
    assert r.status_code == 200
    data = r.json()
    assert "version" in data and "agent" in data
    assert isinstance(data["agent"].get("client_initialized"), bool)


def test_healthz_alias():
    client = TestClient(app)
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
