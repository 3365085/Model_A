from __future__ import annotations

import argparse
import os
import socket
import threading
import webbrowser
from pathlib import Path

from defense.runtime.config import DEFAULT_CONFIG_PATH


def open_browser_later(url: str) -> None:
    def _open() -> None:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    threading.Timer(0.8, _open).start()


def warn_if_public_host(host: str) -> None:
    if str(host).strip() in {"0.0.0.0", "::"} and not os.environ.get("MODULE_A_WEB_TOKEN"):
        print("WARNING: binding to a public host without MODULE_A_WEB_TOKEN exposes control APIs.")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Module A web monitor")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7860)
    parser.add_argument("--auto-port", action="store_true")
    parser.add_argument("--open-browser", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    return parser.parse_args(argv)


def select_port(host: str, port: int, auto_port: bool) -> int:
    if not auto_port:
        return int(port)
    for candidate in range(int(port), int(port) + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((str(host), int(candidate)))
            except OSError:
                continue
            return int(candidate)
    return int(port)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
    from .fastapi_app import create_app
    import uvicorn

    port = select_port(str(args.host), int(args.port), bool(args.auto_port))
    warn_if_public_host(str(args.host))
    app = create_app(config_path=Path(args.config), bind_host=str(args.host))
    url = f"http://{args.host}:{port}/"
    print(f"Module A monitor running at {url}")
    if args.open_browser:
        open_browser_later(url)
    server = uvicorn.Server(
        uvicorn.Config(app, host=str(args.host), port=port, log_level="warning" if args.quiet else "info")
    )
    try:
        server.run()
    except KeyboardInterrupt:
        pass
    finally:
        app.state.engine.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
