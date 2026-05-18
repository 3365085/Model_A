from __future__ import annotations

from pathlib import Path

from defense.module_a.backends.detector_backend import DetectionFrameResult
from defense.runtime import pipeline_factory


class WarmupFailingPipeline:
    warmup_frames = 1

    def __init__(self, backend, *, config):
        self.backend = backend
        self.config = config
        self.reset_count = 0

    def warmup(self, frames: int) -> None:
        raise RuntimeError("warmup exploded")

    def reset(self) -> None:
        self.reset_count += 1


class DummyBackend:
    backend = "dummy"
    artifact_path = "dummy://artifact"
    names = {}

    def predict(self, image):
        return DetectionFrameResult(
            image=image,
            boxes=[],
            classes=[],
            confidences=[],
            names=self.names,
            backend=self.backend,
            artifact_path=self.artifact_path,
            inference_ms=0.0,
            raw_result=None,
        )


def test_pipeline_cache_exposes_warmup_failure(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(pipeline_factory, "VideoDefensePipeline", WarmupFailingPipeline)
    monkeypatch.setattr(pipeline_factory, "create_detector_backend", lambda config, root: DummyBackend())
    monkeypatch.setattr(
        pipeline_factory,
        "load_runtime_config",
        lambda **kwargs: {"runtime": {}, "inference": {"backend": "dummy"}},
    )

    bundle = pipeline_factory.PipelineCache(root=tmp_path).get(profile="default")

    assert bundle.backend == "dummy"
    assert bundle.warmup_error == "RuntimeError: warmup exploded"
    assert bundle.pipeline.reset_count == 1
