from __future__ import annotations

from defense.web.overlay_timeline import OverlayTimeline


def _record(seq: int, t: float, x: int = 10) -> dict:
    return {
        "overlay_seq": seq,
        "video_time_s": t,
        "ppe_tracks": [
            {
                "track_id": 1,
                "label": "helmet",
                "box": [x, 20, x + 20, 50],
                "confidence": 0.9,
                "misses": 0,
                "source": "detected",
            }
        ],
    }


def test_overlay_timeline_selects_by_video_time_when_records_arrive_out_of_order() -> None:
    timeline = OverlayTimeline()
    timeline.push(_record(2, 10.10, x=30))
    timeline.push(_record(1, 9.92, x=10))

    selected = timeline.select(9.95, match_window_s=0.18)

    assert selected is not None
    assert selected["overlay_seq"] == 1


def test_overlay_timeline_rejects_records_outside_match_window() -> None:
    timeline = OverlayTimeline()
    timeline.push(_record(1, 9.0))
    timeline.push(_record(2, 11.0))

    selected = timeline.select(10.0, match_window_s=0.18, interpolate_s=0.4, hold_s=0.55)

    assert selected is None


def test_overlay_timeline_holds_recent_record_by_video_time() -> None:
    timeline = OverlayTimeline()
    timeline.push(_record(1, 9.90))
    assert timeline.select(9.90, match_window_s=0.18) is not None

    selected = timeline.select(10.00, match_window_s=0.02, interpolate_s=0.0, hold_s=0.55)

    assert selected is not None
    assert selected["held"] is True
    assert selected["ppe_tracks"][0]["source"] == "held"


def test_overlay_timeline_clear_resets_held_overlay_after_seek() -> None:
    timeline = OverlayTimeline()
    timeline.push(_record(1, 9.90))
    assert timeline.select(9.90, match_window_s=0.18) is not None

    timeline.clear()

    assert timeline.select(10.00, match_window_s=0.18, hold_s=0.55) is None


def test_overlay_timeline_prefers_interpolation_between_records() -> None:
    timeline = OverlayTimeline()
    timeline.push(_record(1, 10.00, x=10))
    timeline.push(_record(2, 10.20, x=50))

    selected = timeline.select(10.10, match_window_s=0.18, interpolate_s=0.4, hold_s=0.55)

    assert selected is not None
    assert selected.get("interpolated") is True
    assert selected["ppe_tracks"][0]["box"][0] == 30
