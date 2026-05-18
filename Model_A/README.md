# Module A Video Defense Runtime

Refactored runtime with a src-layout package, FastAPI Web UI, decoupled preview/detection buses, YOLO backend abstraction, PPE postprocessing, Module A A1-A4 detection, A3b/static-media logic, evidence events, diagnostics, and low-power profiles.

## Start

Windows/Pixi:

```powershell
cd D:\security_project_d
pixi run monitor
```

Plain Python from package root:

```powershell
cd D:\security_project_d\Model_A
$env:PYTHONPATH = "src"
python -m defense.web.server --auto-port
```

## Tests

```powershell
$env:PYTHONPATH = "src"
python -m compileall -q src tools tests
python -m pytest -q
python -m pytest -q -m requires_gpu
```

`requires_gpu` tests prefer CUDA but must run through the CPU fallback when CUDA is unavailable.
