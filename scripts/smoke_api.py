#!/usr/bin/env python3
"""Probe API endpoints either in-process or via a live server.

Default mode uses FastAPI's TestClient (no network binding). Use --mode=server
to launch uvicorn and hit real HTTP endpoints (may be restricted in sandboxes).

Prints a concise JSON summary and exits non-zero on failure.

Usage:
  PYTHONPATH=src python scripts/smoke_api.py [--mode inproc|server] [--host 127.0.0.1] [--port 8765]
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request


def curl_json(
    method: str, url: str, data: dict | None = None, timeout: float = 2.5
) -> tuple[int, str]:
    body = None
    headers = {}
    if data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["inproc", "server"], default="inproc")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    # Ensure src/ is on PYTHONPATH for local runs
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(filter(None, ["src", env.get("PYTHONPATH", "")]))

    if args.mode == "inproc":
        try:
            from fastapi.testclient import TestClient

            from open_dam_integry.api import app  # type: ignore
        except Exception as e:  # pragma: no cover
            print(json.dumps({"ok": False, "error": f"failed to import app: {e}"}))
            return 1

        with TestClient(app) as client:
            summary: dict[str, object] = {"ok": False}
            # Health
            r = client.get("/health")
            summary["health"] = {"status": r.status_code, "body": r.text}
            if r.status_code != 200:
                print(json.dumps(summary))
                return 2
            # Stability
            r = client.post(
                "/stability",
                json={
                    "c_kpa": 5.0,
                    "phi_deg": 28.0,
                    "beta_deg": 20.0,
                    "height_m": 20.0,
                    "gamma_kN_m3": 18.0,
                    "ru": 0.2,
                },
            )
            summary["stability"] = {"status": r.status_code, "body": r.text}
            # Agent
            r = client.post("/agent/respond", json={"prompt": "Quick status"})
            summary["agent"] = {"status": r.status_code, "body_preview": r.text[:180]}
            summary["ok"] = True
            print(json.dumps(summary))
            return 0

    # Verify uvicorn availability early for server mode
    try:
        import uvicorn  # noqa: F401
    except Exception as e:  # pragma: no cover
        print(json.dumps({"ok": False, "error": f"uvicorn not available: {e}"}))
        return 1

    # Start uvicorn in a subprocess
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "open_dam_integry.api:app",
        "--host",
        args.host,
        "--port",
        str(args.port),
    ]
    log_file = tempfile.NamedTemporaryFile(prefix="odi_api_", suffix=".log", delete=False)
    try:
        proc = subprocess.Popen(cmd, env=env, stdout=log_file, stderr=log_file)
    except FileNotFoundError as e:
        print(json.dumps({"ok": False, "error": f"failed to start uvicorn: {e}"}))
        return 1

    base = f"http://{args.host}:{args.port}"
    health_ok = False
    summary: dict[str, object] = {"ok": False}

    try:
        # Wait for server to be ready
        time.sleep(0.5)
        for _ in range(50):
            # Bail out if the server crashed
            if proc.poll() is not None:
                # Read last lines from log for debugging
                try:
                    log_file.flush()
                except Exception:
                    pass
                try:
                    with open(log_file.name, "rb") as fh:
                        tail = fh.read()[-2000:].decode(errors="ignore")
                except Exception:
                    tail = ""
                summary["error"] = "server exited early"
                summary["log_tail"] = tail
                print(json.dumps(summary))
                return 2
            try:
                status, body = curl_json("GET", base + "/health")
                if status == 200:
                    summary["health"] = {"status": status, "body": body}
                    health_ok = True
                    break
            except Exception:
                time.sleep(0.2)

        if not health_ok:
            summary["error"] = "health check failed"
            print(json.dumps(summary))
            return 2

        # Stability endpoint
        status, body = curl_json(
            "POST",
            base + "/stability",
            {
                "c_kpa": 5.0,
                "phi_deg": 28.0,
                "beta_deg": 20.0,
                "height_m": 20.0,
                "gamma_kN_m3": 18.0,
                "ru": 0.2,
            },
        )
        summary["stability"] = {"status": status, "body": body}

        # Agent endpoint (will fall back to deterministic if not configured)
        status, body = curl_json(
            "POST",
            base + "/agent/respond",
            {"prompt": "Quick status"},
        )
        summary["agent"] = {"status": status, "body_preview": body[:180]}

        summary["ok"] = True
        print(json.dumps(summary))
        return 0
    except (urllib.error.URLError, Exception) as e:
        summary["error"] = str(e)
        print(json.dumps(summary))
        return 3
    finally:
        try:
            if proc and proc.poll() is None:
                if os.name == "nt":
                    proc.terminate()
                else:
                    os.kill(proc.pid, signal.SIGTERM)
                proc.wait(timeout=2)
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
