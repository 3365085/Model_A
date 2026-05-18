from __future__ import annotations

import numpy as np

from defense.module_a.backends.detector_backend import DetectionFrameResult
from defense.module_a.postprocess import PPEDisplayTracker, merge_roi_detections


def _detections(
    boxes: list[list[int]],
    classes: list[int],
    confidences: list[float],
    names: dict[int, str] | None = None,
) -> DetectionFrameResult:
    return DetectionFrameResult(
        image=np.zeros((640, 640, 3), dtype=np.uint8),
        boxes=boxes,
        classes=classes,
        confidences=confidences,
        names=names or {0: "helmet", 1: "head", 2: "person"},
        backend="fake",
        artifact_path="fake.pt",
        inference_ms=1.0,
        raw_result=None,
    )


def test_small_head_track_is_held_through_short_dropouts() -> None:
    tracker = PPEDisplayTracker(redetect_interval=1)
    ppe = {"helmet_fp_suppression": {}}

    tracks = tracker.update(
        _detections([[120, 80, 136, 99]], [1], [0.72]),
        ppe,
        (640, 640),
    )
    assert len(tracks) == 1
    assert tracks[0]["label"] == "head"
    assert tracks[0]["is_small"] is True

    tracks = []
    for _ in range(5):
        tracks = tracker.update(_detections([], [], []), ppe, (640, 640))

    assert len(tracks) == 1
    assert tracks[0]["source"] == "held"
    assert tracks[0]["misses"] == 5


def test_helmet_track_holds_then_recovers_after_short_dropout() -> None:
    tracker = PPEDisplayTracker(
        hold_frames=10,
        small_hold_frames=10,
        iou_match_threshold=0.30,
        smooth_alpha=0.65,
        show_held_boxes=True,
    )
    ppe = {"helmet_fp_suppression": {}}

    tracks = tracker.update(_detections([[100, 100, 140, 145]], [0], [0.88]), ppe, (640, 640))
    assert len(tracks) == 1
    assert tracks[0]["source"] == "detected"

    tracks = tracker.update(_detections([], [], []), ppe, (640, 640))
    assert len(tracks) == 1
    assert tracks[0]["source"] == "held"
    assert tracks[0]["misses"] == 1

    tracks = tracker.update(_detections([], [], []), ppe, (640, 640))
    assert len(tracks) == 1
    assert tracks[0]["source"] == "held"
    assert tracks[0]["misses"] == 2

    tracks = tracker.update(_detections([[104, 102, 144, 147]], [0], [0.91]), ppe, (640, 640))
    assert len(tracks) == 1
    assert tracks[0]["source"] == "detected"
    assert tracks[0]["misses"] == 0


def test_adjacent_heads_do_not_merge_into_one_big_display_box() -> None:
    tracker = PPEDisplayTracker()
    ppe = {"helmet_fp_suppression": {}}

    tracks = tracker.update(
        _detections(
            [[80, 80, 108, 112], [122, 82, 150, 114]],
            [1, 1],
            [0.81, 0.78],
        ),
        ppe,
        (640, 640),
    )

    head_tracks = [track for track in tracks if track["label"] == "head"]
    assert len(head_tracks) == 2
    assert all((track["box"][2] - track["box"][0]) < 40 for track in head_tracks)


def test_head_and_helmet_same_target_keeps_single_primary_box() -> None:
    tracker = PPEDisplayTracker()
    ppe = {"helmet_fp_suppression": {}}

    tracks = tracker.update(
        _detections(
            [[200, 150, 236, 190], [202, 148, 238, 188]],
            [1, 0],
            [0.52, 0.63],
        ),
        ppe,
        (640, 640),
    )

    assert len(tracks) == 1
    assert tracks[0]["label"] == "helmet"


def test_roi_detections_are_mapped_back_and_deduplicated() -> None:
    base = _detections([[100, 100, 122, 128]], [1], [0.35])
    roi_result = _detections([[12, 10, 36, 40]], [1], [0.82])

    merged = merge_roi_detections(
        base,
        [([90, 92, 186, 188], roi_result)],
        (640, 640),
    )

    assert merged.inference_ms == 2.0
    assert [102, 102, 126, 132] in merged.boxes
    assert max(merged.confidences) == 0.82
