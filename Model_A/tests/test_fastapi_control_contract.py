from __future__ import annotations

from fastapi.testclient import TestClient

from defense.web.fastapi_app import create_app


class DummyEngine:
    def __init__(self) -> None:
        self.run_id = 7
        self.calls: list[tuple[int, str, dict]] = []

    def get_status(self) -> dict:
        return {"run_id": self.run_id, "running": True, "display_options": {}}

    def control_run(self, run_id: int, action: str, **payload) -> dict:
        self.calls.append((run_id, action, payload))
        return {"run_id": run_id, "running": True, "playback_paused": action == "pause", "display_options": {}}


def test_control_route_does_not_pass_duplicate_action() -> None:
    engine = DummyEngine()
    app = create_app(engine=engine)
    client = TestClient(app)

    response = client.post("/api/runs/7/control", json={"action": "pause", "source_time_s": 4.0})

    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert engine.calls == [(7, "pause", {"source_time_s": 4.0})]
