# Module A Video Defense Runtime

Refactored runtime with a src-layout package, FastAPI Web UI, decoupled preview/detection buses, YOLO backend abstraction, PPE postprocessing, Module A A1-A4 detection, A3b/static-media logic, evidence events, diagnostics, and low-power profiles.

## Start

Pixi workspace root is `D:\security_project_d`. The shared GPU environment is
`D:\security_project_d\.pixi`; do not create or use a separate
`D:\security_project_d\Model_A\.pixi` environment for normal operation.

Windows/Pixi:

```powershell
cd D:\security_project_d
pixi run monitor
```

Plain Python from package root is only a local debugging fallback. It uses the
currently active Python environment, so GPU libraries are not guaranteed unless
that environment is already configured.

```powershell
cd D:\security_project_d\Model_A
$env:PYTHONPATH = "src"
python -m defense.web.server --auto-port
```

## Tests

Preferred path:

```powershell
cd D:\security_project_d
pixi run smoke
```

Or with plain Python from the package root:

```powershell
$env:PYTHONPATH = "src"
python -m compileall -q src tools tests
python -m pytest -q
python -m pytest -q -m requires_gpu
```

`requires_gpu` tests prefer CUDA but must run through the CPU fallback when CUDA is unavailable.
