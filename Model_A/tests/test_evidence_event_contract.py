from __future__ import annotations

import numpy as np

from defense.runtime.evidence import EvidenceSession, default_evidence_root


def test_default_evidence_root_is_outside_source_tree(monkeypatch) -> None:
    monkeypatch.delenv("MODULE_A_EVIDENCE_ROOT", raising=False)

    root = default_evidence_root()

    assert root.parts[-3:] == ("runtime", "evidence", "monitor")
    assert "src" not in root.parts


def test_default_evidence_root_uses_environment_override(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("MODULE_A_EVIDENCE_ROOT", str(tmp_path))

    assert default_evidence_root() == tmp_path


def test_a3b_evidence_finalize_exports_ui_compatibility_fields(tmp_path) -> None:
    session = EvidenceSession(
        source_type="file",
        source="case.mp4",
        profile="desktop_rtx",
        root=tmp_path,
        pre_frames=0,
        post_frames=1,
        sample_every=1,
    )
    frame = np.zeros((32, 32, 3), dtype=np.uint8)
    session.update(
        frame_idx=12,
        frame=frame,
        info={},
        ppe={},
        status={
            "a3b_triggered": True,
            "a3b_event_score": 0.84,
            "a3b_triggered_source": "observed_window",
        },
    )

    events = session.close()

    assert len(events) == 1
    event = events[0]
    assert event["channel"] == "a3b"
    assert event["event_id"] == 1
    assert event["trigger_frame"] == 12
    assert event["last_warning_frame"] == 12
    assert event["peak_a3b_score"] == 0.84
    assert event["peak_score"] == 0.84
    assert event["reason"] == "observed_window"
    assert event["evidence_saved"] is True
    assert event["evidence_saved_frame_count"] == 1
    assert event["evidence_frames_dir"]
    assert event["evidence_representative_path"]
