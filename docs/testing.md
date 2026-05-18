# Testing

From the repository root, the Pixi smoke task compiles the package and runs pytest:

```powershell
cd D:\security_project_d\Model_A
pixi run smoke
```

Plain Python equivalent:

```powershell
$env:PYTHONPATH = "src"
python -m compileall -q src tools tests
python -m pytest -q
python -m pytest -q -m requires_gpu
```

The `cuda_device` fixture returns `cuda:0` when CUDA is available and `cpu` otherwise. This keeps GPU-preferred tests executing on CPU-only machines.

For video diagnostics:

```powershell
$env:PYTHONPATH = "src"
python tools/video_diagnostic.py --profile low_power --max-frames 30 --no-cuda-check
```
