from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import app


def test_api_health_ok():
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_api_scenarios_shape():
    client = TestClient(app)
    response = client.get("/api/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3

    scenario = data[0]
    assert "id" in scenario
    assert "name" in scenario
    assert "description" in scenario
    assert "defaultConfig" in scenario
    assert "tags" in scenario
    assert isinstance(scenario["tags"], list)


def test_api_run_returns_frames():
    client = TestClient(app)
    response = client.post(
        "/api/run",
        json={
            "scenario_id": "coast",
            "t_end_s": 10.0,
            "dt_s": 1.0,
        },
    )
    assert response.status_code == 200
    frames = response.json()
    assert isinstance(frames, list)
    assert len(frames) == 11

    frame0 = frames[0]
    assert "t_s" in frame0
    assert "bodies" in frame0
    assert "craft" in frame0
    assert "events" in frame0

    assert isinstance(frame0["bodies"], list)
    assert isinstance(frame0["craft"], list)
    assert isinstance(frame0["events"], list)

    craft_ids = {c["id"] for c in frame0["craft"]}
    assert any(cid.endswith(".true") for cid in craft_ids)
    assert any(cid.endswith(".est") for cid in craft_ids)

