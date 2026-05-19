from __future__ import annotations

from fastapi.testclient import TestClient

from defense.web.fastapi_app import create_app


class ReadyDetectionEngine:
    def __init__(self) -> None:
        self.run_id = 41
        self.started_with: dict | None = None

    def start(self, **payload) -> int:
        self.started_with = payload
        return self.run_id

    def wait_ready_for_preview(self, run_id: int, timeout: float = 45.0) -> dict:
        assert run_id == self.run_id
        return self.get_status()

    def get_status(self) -> dict:
        return {
            "run_id": self.run_id,
            "running": True,
            "ready_for_preview": True,
            "detector_ready": True,
            "backend": "test",
            "artifact": "test://artifact",
            "overlay_seq": 3,
            "raw_boxes_count": 2,
            "frame_idx": 12,
            "p_adv": 0.42,
            "display_options": {},
            "recent_events": [],
            "recent_ppe_events": [],
            "recent_source_auth_events": [],
        }

    def get_overlay(self, since_seq: int = 0) -> dict:
        return {
            "run_id": self.run_id,
            "seq": 3,
            "latest_seq": 3,
            "records": [
                {
                    "overlay_seq": 3,
                    "video_time_s": 0.4,
                    "a3b_score": 0.2,
                    "a3b_triggered": False,
                    "raw_boxes_count": 2,
                }
            ],
        }


def test_web_start_returns_detection_readiness_fields() -> None:
    engine = ReadyDetectionEngine()
    client = TestClient(create_app(engine=engine))

    response = client.post(
        "/api/start",
        json={"source_type": "file", "source": "sample.mp4", "profile": "desktop_rtx", "ready_timeout_s": 0.1},
    )

    assert response.status_code == 200
    data = response.json()
    status = data["status"]
    assert data["ok"] is True
    assert data["run_id"] == 41
    assert status["ready_for_preview"] is True
    assert status["detector_ready"] is True
    assert status["backend"] == "test"
    assert status["overlay_seq"] == 3
    assert status["raw_boxes_count"] == 2
    assert engine.started_with["profile"] == "desktop_rtx"


def test_web_overlay_returns_detection_records() -> None:
    client = TestClient(create_app(engine=ReadyDetectionEngine()))

    response = client.get("/api/overlay?since_seq=0")

    assert response.status_code == 200
    overlay = response.json()["overlay"]
    assert overlay["latest_seq"] == 3
    assert overlay["records"][0]["raw_boxes_count"] == 2
    assert "a3b_score" in overlay["records"][0]
