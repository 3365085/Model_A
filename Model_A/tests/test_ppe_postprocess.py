from __future__ import annotations

from types import SimpleNamespace

from defense.module_a.ppe_postprocess import bbox_iou, summarize_ppe_from_detections


def make_detections(boxes, classes, confidences, names):
    return SimpleNamespace(boxes=boxes, classes=classes, confidences=confidences, names=names)


def test_head_overlap_suppresses_weak_helmet_false_positive():
    detections = make_detections(
        boxes=[(100, 100, 180, 190), (102, 102, 178, 188), (80, 80, 220, 330)],
        classes=[0, 1, 2],
        confidences=[0.82, 0.47, 0.91],
        names={0: "head", 1: "helmet", 2: "person"},
    )

    summary = summarize_ppe_from_detections(detections, frame_shape=(640, 640))

    assert summary["raw_helmet_count"] == 1
    assert summary["helmet_count"] == 0
    assert summary["head_count"] == 1
    assert summary["candidate"] is True
    assert summary["helmet_fp_suppression"]["suppressed_helmet_indices"] == [1]


def test_strong_helmet_survives_head_overlap():
    detections = make_detections(
        boxes=[(100, 100, 180, 190), (102, 102, 178, 188), (80, 80, 220, 330)],
        classes=[0, 1, 2],
        confidences=[0.50, 0.90, 0.91],
        names={0: "head", 1: "helmet", 2: "person"},
    )

    summary = summarize_ppe_from_detections(detections, frame_shape=(640, 640))

    assert summary["raw_helmet_count"] == 1
    assert summary["helmet_count"] == 1
    assert summary["helmet_fp_suppression"]["suppressed_helmet_indices"] == []


def test_no_helmet_label_does_not_count_as_helmet():
    detections = make_detections(
        boxes=[(100, 100, 180, 190), (80, 80, 220, 330)],
        classes=[0, 1],
        confidences=[0.86, 0.92],
        names={0: "no_helmet", 1: "person"},
    )

    summary = summarize_ppe_from_detections(detections, frame_shape=(640, 640))

    assert summary["raw_helmet_count"] == 0
    assert summary["head_count"] == 1
    assert summary["candidate"] is True


def test_isolated_small_edge_head_does_not_trigger_ppe_warning():
    detections = make_detections(
        boxes=[(575, 260, 600, 294)],
        classes=[0],
        confidences=[0.72],
        names={0: "head"},
    )

    summary = summarize_ppe_from_detections(detections, frame_shape=(640, 640))

    assert summary["raw_head_count"] == 1
    assert summary["head_count"] == 0
    assert summary["candidate"] is False
    assert summary["helmet_fp_suppression"]["suppressed_head_indices"] == [0]


def test_legacy_counting_still_flags_person_without_helmet():
    detections = make_detections(boxes=[], classes=[2], confidences=[0.88], names={2: "person"})

    summary = summarize_ppe_from_detections(detections)

    assert summary["person_count"] == 1
    assert summary["helmet_count"] == 0
    assert summary["missing_helmet_count"] == 1
    assert summary["candidate"] is True


def test_bbox_iou_returns_expected_overlap():
    value = bbox_iou((0, 0, 100, 100), (50, 50, 150, 150))

    assert 0.14 < value < 0.15
