from __future__ import annotations

import threading
import time

from defense.runtime.runner import MonitorEngine


class DummyCache:
    pass


def test_stop_joins_worker_threads() -> None:
    engine = MonitorEngine(DummyCache())
    engine.thread_join_timeout_s = 0.5
    started = threading.Event()

    def worker() -> None:
        started.set()
        while not engine.stop_event.is_set():
            time.sleep(0.01)

    thread = threading.Thread(target=worker, name="test-worker")
    thread.start()
    assert started.wait(timeout=1.0)
    engine.capture_thread = thread
    engine.status["running"] = True

    engine.stop()

    assert not thread.is_alive()
    assert engine.capture_thread is None
    assert engine.status["running"] is False
    assert engine.status["stop_threads_pending"] == []


def test_stop_reports_threads_that_do_not_exit() -> None:
    engine = MonitorEngine(DummyCache())
    engine.thread_join_timeout_s = 0.01
    release = threading.Event()
    started = threading.Event()

    def worker() -> None:
        started.set()
        release.wait(timeout=1.0)

    thread = threading.Thread(target=worker, name="stubborn-worker")
    thread.start()
    assert started.wait(timeout=1.0)
    engine.capture_thread = thread
    engine.status["running"] = True

    engine.stop()
    release.set()
    thread.join(timeout=1.0)

    assert engine.status["stop_threads_pending"] == ["stubborn-worker"]
    assert engine.status["warning"] == "worker_threads_did_not_stop"
