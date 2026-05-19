from __future__ import annotations

from fastapi.testclient import TestClient

from defense.web.fastapi_app import create_app


class DummyEngine:
    def get_status(self) -> dict:
        return {"run_id": 0, "running": False, "display_options": {}}


def test_index_disables_browser_cache() -> None:
    client = TestClient(create_app(engine=DummyEngine()))

    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store, no-cache, must-revalidate, max-age=0"
    assert response.headers["Pragma"] == "no-cache"


def test_static_assets_disable_browser_cache() -> None:
    client = TestClient(create_app(engine=DummyEngine()))

    response = client.get("/static/overlay_timeline.js")

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store, no-cache, must-revalidate, max-age=0"
