"""Shared pytest fixtures for Module A tests.

Responsibilities:
  * Insert the package root on ``sys.path`` so ``from defense.module_a ...``
    resolves without installing the package.
  * Skip CUDA-dependent tests cleanly on CPU-only machines.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
for _path in (SRC_ROOT, PROJECT_ROOT):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))
PKG_ROOT = PROJECT_ROOT


@pytest.fixture(scope="session")
def cuda_device() -> str:
    """Return CUDA when available, otherwise CPU so GPU-preferred tests still run."""
    import torch

    return "cuda:0" if torch.cuda.is_available() else "cpu"


@pytest.fixture(scope="session")
def pkg_root() -> Path:
    return PKG_ROOT


@pytest.fixture(scope="session")
def samples_dir(pkg_root: Path) -> Path:
    return pkg_root / "samples"


@pytest.fixture(scope="session")
def baseline_config_path(pkg_root: Path) -> Path:
    return pkg_root / "experiments" / "configs" / "module_a_baseline.yaml"
