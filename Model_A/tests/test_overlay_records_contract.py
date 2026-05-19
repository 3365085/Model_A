from __future__ import annotations

from defense.runtime.overlay_records import build_overlay_record


def test_overlay_record_carries_status_panel_fields() -> None:
    record = build_overlay_record(
        status={
            "running": True,
            "frame_idx": 42,
            "video_time_s": 1.4,
            "p_adv": 0.25,
            "p_adv_display": 0.25,
            "reason": "temporal_texture_change",
            "reason_codes": ["temporal_texture_change"],
            "timing_ms": 12.5,
            "processing_ms": 19.0,
            "detector_inference_ms": 8.0,
            "module_a_timing_ms": 4.0,
            "ppe_warning": True,
            "ppe_person_count": 1,
            "ppe_helmet_count": 0,
            "ppe_head_count": 1,
            "ppe_missing_helmet_count": 1,
            "ppe_reason": "missing helmet",
            "branch_cards": [{"branch": "p_adv", "score_display": "0.250"}],
        },
        ppe_tracks=[{"track_id": 1, "label": "head", "box": [1, 2, 3, 4]}],
        run_id=7,
        display_options={"show_boxes": True},
    )

    assert record["run_id"] == 7
    assert record["running"] is True
    assert record["frame_idx"] == 42
    assert record["p_adv"] == 0.25
    assert record["reason_codes"] == ["temporal_texture_change"]
    assert record["ppe_reason"] == "missing helmet"
    assert record["ppe_head_count"] == 1
    assert record["branch_cards"] == [{"branch": "p_adv", "score_display": "0.250"}]
    assert record["detector_inference_ms"] == 8.0
    assert record["module_a_timing_ms"] == 4.0
