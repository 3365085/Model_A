from __future__ import annotations

from pathlib import Path


HTML = Path("src/defense/web/static/index.html")


def test_frontend_does_not_call_browser_frame_detection() -> None:
    html = HTML.read_text(encoding="utf-8")
    assert "/api/detect-frame" not in html
    assert "detectCurrentVideoFrame" not in html
    assert "captureVideoJpeg(video)" not in html


def test_mp4_uses_backend_preview_stream_not_native_video_pipeline() -> None:
    html = HTML.read_text(encoding="utf-8")
    assert 'startMjpegPreview(status);' in html
    assert '/api/runs/${runId}/preview.mjpg' in html
    assert 'function updateStartButtonState(status)' in html
    assert 'id="playPauseBtn"' in html
    assert 'id="seekSlider"' in html
    assert 'id="speedSelect"' in html
    assert 'function controlRun(action' in html
    assert '/api/runs/${runId}/control' in html
    assert "nativeVideo" not in html
    assert "analysisVideo" not in html
    assert "/api/begin-preview" not in html


def test_backend_source_pipeline_debug_state_is_reported() -> None:
    html = HTML.read_text(encoding="utf-8")
    assert "controlRun(" in html
    assert "backend_latest_only" in html or "pipelineText" in html


def test_stop_still_clears_preview_and_overlay_polling() -> None:
    html = HTML.read_text(encoding="utf-8")
    assert "function stopOverlayPolling()" in html
    assert "stopOverlayPolling();" in html
    assert 'await api("/api/stop", {})' in html
    assert "activePreviewRunId = 0;" in html
    assert 'removeAttribute("data-run-id")' in html


def test_frontend_does_not_reference_removed_realtime_control() -> None:
    html = HTML.read_text(encoding="utf-8")
    assert '$("realtime")' not in html


def test_progress_controls_are_only_shown_for_local_mp4_runs() -> None:
    html = HTML.read_text(encoding="utf-8")
    assert "const showProgressControls = isFile && duration > 0 && running;" in html
    assert '$("runControls").style.display = showProgressControls ? "grid" : "none";' in html
    assert '$("seekSlider").disabled = !running || !!status?.source_ended;' in html


def test_camera_source_uses_camera_selector_value() -> None:
    html = HTML.read_text(encoding="utf-8")
    assert 'return $("cameraSelect").value || "0";' in html
    assert 'return $("cameraSelect").value || $("sourceValue").value || "0";' not in html


def test_status_refresh_uses_adaptive_timeout() -> None:
    html = HTML.read_text(encoding="utf-8")
    assert "setInterval(refresh, 200)" not in html
    assert "refreshIntervals" in html
    assert "scheduleRefresh(nextRefreshMs)" in html


def test_status_panel_can_use_latest_overlay_record_as_live_fallback() -> None:
    html = HTML.read_text(encoding="utf-8")
    assert "function mergeOverlayStatusForPanel(status)" in html
    assert "status = mergeOverlayStatusForPanel(status);" in html
    assert "latestOverlayStatusRecord()" in html
    assert "ppe_head_count: Number(status.ppe_head_count || 0)" in html
