from __future__ import annotations

import importlib
from types import SimpleNamespace

import numpy as np

from defense.pipelines.video_defense_pipeline import VideoDefensePipeline


class _FakeDetectorResult:
    def __init__(self) -> None:
        self.p_adv = 0.2
        self.reason_codes = ["fake_reason"]
        self.alert_confirmed = False
        self.attack_state_active = False
        self.single_frame_suspicious = False
        self.details = {"module_a_breakdown": {"a1_overexposure_ms": 0.0}}

    def to_info_dict(self) -> dict[str, object]:
        return {
            "layer_triggered": "NORMAL",
            "is_attack": False,
            "attack_detected": False,
            "attack_state_active": False,
            "attack_state_source": "none",
            "attack_state_remaining": 0,
            "attack_state_last_layer": "NORMAL",
            "alert_confirmed": False,
            "timing_ms": 0.0,
            "details": dict(self.details),
        }


class _FakeModuleA:
    def __init__(self, config=None):
        self.config = config or {}

    def reset(self) -> None:
        return None

    def process(self, item):
        return _FakeDetectorResult()


class _FakeBackend:
    names = {0: "person"}

    def predict(self, image):
        return SimpleNamespace(
            image=image,
            boxes=[[1, 1, 10, 10]],
            classes=[0],
            confidences=[0.9],
            names=self.names,
            backend="fake",
            artifact_path="fake",
            inference_ms=3.5,
            raw_result=None,
        )


def test_pipeline_emits_latency_contract(monkeypatch):
    pipeline_mod = importlib.import_module("defense.pipelines.video_defense_pipeline")
    monkeypatch.setattr(pipeline_mod, "ModuleADetector", _FakeModuleA)
    pipeline = VideoDefensePipeline(_FakeBackend(), config={"module_a": {}})
    frame = np.zeros((320, 480, 3), dtype=np.uint8)

    _, _, info = pipeline.process_frame(frame)

    latency = info["latency_breakdown"]
    assert "frame_resize_ms" in latency
    assert "detector_reuse_hit" in latency
    assert "detector_change_score" in latency
    assert "source_frame_shape" in latency
    assert "detector_frame_shape" in latency
