#!/usr/bin/env python3
"""Smoke a built standalone image without exposing its generated credential."""

from __future__ import annotations

import argparse
import json
import secrets
import subprocess
import time
import urllib.error
import urllib.request


def docker(*args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["docker", *args], check=False, text=True, capture_output=True
    )
    if check and result.returncode:
        raise RuntimeError((result.stderr or result.stdout).strip())
    return result.stdout.strip()


def request(url: str, *, token: str = "", body: bytes | None = None) -> tuple[int, bytes]:
    headers = {"Accept": "application/json, text/event-stream"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if body is not None:
        headers["Content-Type"] = "application/json; charset=utf-8"
    req = urllib.request.Request(url, data=body, headers=headers, method="POST" if body else "GET")
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status, response.read(65536)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(65536)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("image")
    parser.add_argument("--name", default="qa-mcp-standalone-smoke")
    parser.add_argument("--expected-source-commit", default="")
    args = parser.parse_args()

    if docker("ps", "-aq", "--filter", f"name=^/{args.name}$"):
        raise SystemExit(f"refusing to replace existing container: {args.name}")
    token = secrets.token_hex(32)
    created = False
    try:
        docker(
            "run", "-d", "--name", args.name,
            "--label", "qa-mcp.owned=standalone-smoke",
            "-p", "127.0.0.1::8080",
            "-e", f"QA_MCP_BEARER_TOKEN={token}", args.image,
        )
        created = True
        port = ""
        for _ in range(30):
            binding = docker("port", args.name, "8080/tcp", check=False)
            if binding:
                port = binding.rsplit(":", 1)[-1]
                try:
                    status, health = request(f"http://127.0.0.1:{port}/health")
                    if status == 200 and json.loads(health) == {"status": "ok"}:
                        break
                except (OSError, ValueError):
                    pass
            if docker("inspect", "-f", "{{.State.Status}}", args.name, check=False) == "exited":
                raise RuntimeError("container exited before health passed")
            time.sleep(1)
        else:
            raise RuntimeError("bounded health did not become ready")

        unauthorized, _ = request(f"http://127.0.0.1:{port}/mcp")
        initialize = json.dumps({
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18", "capabilities": {},
                "clientInfo": {"name": "qa-mcp-release-smoke", "version": "1"},
            },
        }).encode("utf-8")
        authorized, response = request(
            f"http://127.0.0.1:{port}/mcp", token=token, body=initialize
        )
        user = docker("image", "inspect", args.image, "-f", "{{.Config.User}}")
        revision = docker(
            "image", "inspect", args.image,
            "-f", '{{index .Config.Labels "org.opencontainers.image.revision"}}',
        )
        checks = {
            "health": status == 200,
            "unauthorized": unauthorized == 401,
            "authorized_initialize": authorized == 200 and b'"serverInfo"' in response,
            "non_root": bool(user and user not in {"0", "root"}),
            "source_revision": not args.expected_source_commit or revision == args.expected_source_commit,
        }
        print(json.dumps({
            "schema": "qa-mcp.standalone-image-smoke.v1",
            "image": args.image,
            "container_user": user,
            "source_revision": revision,
            "checks": checks,
            "ok": all(checks.values()),
        }, sort_keys=True))
        return 0 if all(checks.values()) else 1
    except Exception as exc:  # noqa: BLE001 - release gate emits bounded diagnostics.
        logs = docker("logs", "--tail", "40", args.name, check=False) if created else ""
        print(json.dumps({"ok": False, "error": str(exc), "logs": logs[-2000:]}, sort_keys=True))
        return 1
    finally:
        if created:
            docker("rm", "-f", args.name, check=False)


if __name__ == "__main__":
    raise SystemExit(main())
