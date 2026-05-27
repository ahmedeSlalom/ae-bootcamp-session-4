from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from app import DEFAULT_CAPABILITIES, app


client = TestClient(app)


def test_capability_filter_implementation():
    response = client.get("/capabilities", params={"practice_area": "Technology"})

    assert response.status_code == 200

    payload = response.json()

    assert payload
    assert set(payload).issubset(set(DEFAULT_CAPABILITIES))
    assert all(details["practice_area"] == "Technology" for details in payload.values())
    assert "Digital Strategy" not in payload


def test_get_capabilities_endpoint_returns_seeded_capabilities():
    response = client.get("/capabilities")

    assert response.status_code == 200

    payload = response.json()

    assert set(payload) == set(DEFAULT_CAPABILITIES)
    assert payload["Cloud Architecture"]["practice_area"] == "Technology"
    assert "consultants" in payload["Cloud Architecture"]