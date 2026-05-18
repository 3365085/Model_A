from __future__ import annotations

"""Smoke test for the MP4 hidden-analyzer delayed-sync route.

This script intentionally uses the lightweight ``empty_smoke`` profile so it can
verify paths, Web/Runtime contracts and A3b status plumbing on machines without
CUDA/TensorRT. Full inference validation should still be run with desktop_rtx on
the deployment workstation.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from defense.runtime import MonitorEngine, PipelineCache, open_capture, project_root, sample_sources
from defense.runtime.config import workspace_material_root
from defense.runtime.frame_processor import prepare_frame_640


def main() -> int:
    root = project_root()
    samples = sample_sources()
    material_root = workspace_material_root()
    material_source = str(material_root / "手机随意录制的视频" / "固定镜头室外视频.mp4")
    if not any(str(item.get("source", "")).startswith(str(material_root)) for item in samples):
        raise AssertionError(f"/api/samples 未暴露素材根目录: {material_root}")

    cap = open_capture("file", material_source)
    try:
        ok, frame = cap.read()
        if not ok or frame is None:
            raise AssertionError(f"素材无法读取: {material_source}")
        frame_640 = prepare_frame_640(frame)
        shape = tuple(int(x) for x in frame.shape)
    finally:
        cap.release()

    cache = PipelineCache(root=root)
    engine = MonitorEngine(cache)
    run_id = engine.start(source_type="file", source=material_source, profile="empty_smoke", realtime=True)
    try:
        status = engine.wait_detector_ready(run_id, timeout=5.0)
        if not status.get("detector_ready"):
            raise AssertionError(f"detector 未就绪: {status}")
        if status.get("browser_frame_queue_policy") != "latest_only_mailbox":
            raise AssertionError(f"队列策略异常: {status.get('browser_frame_queue_policy')}")

        first = engine.process_browser_frame(
            run_id=run_id,
            frame=frame_640,
            video_time_s=0.0,
            client_frame_id=1,
            await_result=True,
        )
        record = first.get("overlay_record") or {}
        for key in ("video_time_s", "a3b_score", "a3b_triggered"):
            if key not in record:
                raise AssertionError(f"overlay_record 缺少 {key}: {record}")

        engine.begin_preview(run_id, 0.0)
        queued = engine.process_browser_frame(
            run_id=run_id,
            frame=frame_640,
            video_time_s=0.04,
            client_frame_id=2,
            await_result=False,
        )
        if not queued.get("accepted"):
            raise AssertionError(f"异步帧未接受: {queued}")
        overlay = engine.get_overlay(since_seq=0)
        if not overlay.get("records"):
            raise AssertionError("overlay 时间线为空")

        print(json.dumps({
            "ok": True,
            "project_root": str(root),
            "material_source": material_source,
            "material_shape": shape,
            "profile": status.get("profile"),
            "display_delay_ms": status.get("browser_frame_display_delay_ms"),
            "sample_fps": status.get("browser_frame_sample_fps"),
            "queue_policy": status.get("browser_frame_queue_policy"),
            "overlay_records": len(overlay.get("records") or []),
            "a3b_fields_present": True,
        }, ensure_ascii=False, indent=2))
    finally:
        engine.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
