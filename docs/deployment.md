# Deployment

## Environment

Use the existing Pixi environment when available. The repository uses Python 3.11, FastAPI, Uvicorn, OpenCV, NumPy, PyTorch, ONNX Runtime GPU, TensorRT, and Ultralytics.

Run Pixi commands from the repository root:

```powershell
cd D:\security_project_d\Model_A
pixi run monitor
```

## GPU check

```powershell
nvidia-smi
pixi run verify-ai
$env:PYTHONPATH = "src"
python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else None)"
```

## Profiles

- `high_quality`: highest load, intended for desktop RTX-class GPUs.
- `balanced`: moderate detection load.
- `low_power`: lower detector FPS and slower Module A slow-path intervals while preserving usable preview FPS.

## Security

Localhost is zero-friction by default. If binding to a non-localhost host or setting `MODULE_A_WEB_TOKEN`, control APIs and WebSocket require the token.
