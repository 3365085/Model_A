# AGENTS.md

Scope: entire repository.

## Core rules

- Keep `src/defense` as the only production package root.
- Keep `tools/` as CLI wrappers only; reusable logic belongs in `src/defense`.
- Keep `tests/` separate from production code.
- Keep docs in `docs/` with ASCII file names.
- FastAPI is the only Web API implementation.
- Do not add legacy HTTP handlers.
- Preview and detection must remain decoupled.
- Detection uses latest-only backpressure.
- Do not change model weights, class semantics, thresholds, PPE semantics, or A3b/Module A strategy without explicit behavior-tuning work.
- GPU-preferred tests must attempt CPU fallback when CUDA is unavailable.

## Ownership boundaries

- Runtime lifecycle, threads, status snapshots, and evidence writing belong in `src/defense/runtime`.
- Web protocols, request validation, static assets, and security policy belong in `src/defense/web`.
- Module A detection, fusion, feature extraction, and postprocessing belong in `src/defense/module_a`.
- Video source adapters and frame envelopes belong in `src/defense/pipelines`.
- Shared diagnostics that are reusable by production code belong in `src/defense/diagnostics`; `tools/` should only parse CLI arguments and call into package code.
- Tests may define local fakes and fixtures, but production code must not import from `tests/`.

## Change discipline

- Prefer small, categorized commits that can be reverted independently.
- Do not move files or functions unless the ownership boundary is clearly wrong.
- Do not introduce a new framework, package root, web stack, or build system without explicit architecture work.
- Keep compatibility for public Web API paths and existing detection/status field names.
- When fixing runtime bugs, address the root cause and add a focused regression test when practical.

## Generated files

- Do not commit `__pycache__`, `.pytest_cache`, runtime evidence, local logs, model build caches, or other generated artifacts.
- Runtime evidence must be written outside source package directories by default.
- Keep large local material, model, and environment directories outside Git unless explicitly requested.

## Performance and safety

- Optimizations must not add extra GPU inference to the main detection path.
- Keep preview rendering and detection processing independently backpressured.
- Avoid tight polling when the monitor is idle.
- Surface backend, model, and runtime initialization failures clearly in status or logs; do not silently convert them into empty detection results.
