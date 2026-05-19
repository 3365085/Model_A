from __future__ import annotations

from types import SimpleNamespace

from defense.module_a.postprocess import PPEDisplayTracker
from defense.runtime.ppe_business import evaluate_ppe_business
from defense.runtime.ppe_state import SafetyHelmetState


def make_detections(boxes, classes, confidences, names):
    return SimpleNamespace(boxes=boxes, classes=classes, confidences=confidences, names=names)


def test_evaluate_ppe_business_applies_summary_and_temporal_state() -> None:
    state = SafetyHelmetState()
    tracker = PPEDisplayTracker()
    detections = make_detections(
        boxes=[(100, 100, 180, 190), (80, 80, 220, 330)],
        classes=[0, 2],
        confidences=[0.86, 0.92],
        names={0: "head", 2: "person"},
    )

    outputs = [
        evaluate_ppe_business(
            detections,
            frame_shape=(640, 640),
            ppe_state=state,
            ppe_tracker=tracker,
            tracking_enabled=True,
        )
        for _ in range(3)
    ]

    assert outputs[-1].ppe["candidate"] is True
    assert outputs[-1].ppe["confirmed"] is True
    assert outputs[-1].ppe["warning"] is True
    assert outputs[-1].ppe["person_count"] == 1
    assert outputs[-1].ppe["head_count"] == 1
    assert outputs[-1].tracks


def test_evaluate_ppe_business_can_skip_display_tracking() -> None:
    result = evaluate_ppe_business(
        make_detections([], [], [], {0: "head", 1: "helmet", 2: "person"}),
        frame_shape=(640, 640),
        ppe_state=SafetyHelmetState(),
        ppe_tracker=PPEDisplayTracker(),
        tracking_enabled=False,
    )

    assert result.ppe["candidate"] is False
    assert result.tracks == []
