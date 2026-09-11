#!/usr/bin/env python3
"""TCP proxy for capturing 1C TestManager/TestClient protocol bytes."""

from __future__ import annotations

import argparse
import asyncio
import base64
import hashlib
import json
import signal
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DIRECTION_MANAGER_TO_CLIENT = "manager_to_client"
DIRECTION_CLIENT_TO_MANAGER = "client_to_manager"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def json_default(value: Any) -> str:
    return str(value)


class CaptureLogger:
    def __init__(self, capture_dir: Path, inline_payload_limit: int) -> None:
        self.capture_dir = capture_dir
        self.connections_dir = capture_dir / "connections"
        self.inline_payload_limit = inline_payload_limit
        self.capture_dir.mkdir(parents=True, exist_ok=True)
        self.connections_dir.mkdir(parents=True, exist_ok=True)

        self.events_path = capture_dir / "traffic.jsonl"
        self.aggregate_paths = {
            DIRECTION_MANAGER_TO_CLIENT: capture_dir / f"{DIRECTION_MANAGER_TO_CLIENT}.bin",
            DIRECTION_CLIENT_TO_MANAGER: capture_dir / f"{DIRECTION_CLIENT_TO_MANAGER}.bin",
        }
        self.aggregate_offsets = {
            DIRECTION_MANAGER_TO_CLIENT: 0,
            DIRECTION_CLIENT_TO_MANAGER: 0,
        }
        self._lock = asyncio.Lock()
        self._events = self.events_path.open("a", encoding="utf-8")
        self._aggregate_files = {
            direction: path.open("ab") for direction, path in self.aggregate_paths.items()
        }

    async def close(self) -> None:
        async with self._lock:
            self._events.flush()
            self._events.close()
            for file_obj in self._aggregate_files.values():
                file_obj.flush()
                file_obj.close()

    async def event(self, event_type: str, **fields: Any) -> None:
        record = {"ts": utc_now(), "event": event_type}
        record.update(fields)
        async with self._lock:
            self._events.write(json.dumps(record, ensure_ascii=False, default=json_default) + "\n")
            self._events.flush()

    async def chunk(
        self,
        connection_id: int,
        direction: str,
        chunk_no: int,
        payload: bytes,
    ) -> None:
        digest = hashlib.sha256(payload).hexdigest()
        per_connection_path = (
            self.connections_dir / f"connection_{connection_id:04d}_{direction}.bin"
        )

        async with self._lock:
            aggregate_offset = self.aggregate_offsets[direction]
            self.aggregate_offsets[direction] += len(payload)

            aggregate_file = self._aggregate_files[direction]
            aggregate_file.write(payload)
            aggregate_file.flush()

            with per_connection_path.open("ab") as per_connection_file:
                per_connection_file.write(payload)

            record = {
                "ts": utc_now(),
                "event": "chunk",
                "connection_id": connection_id,
                "direction": direction,
                "chunk_no": chunk_no,
                "byte_count": len(payload),
                "sha256": digest,
                "aggregate_offset": aggregate_offset,
                "aggregate_path": str(self.aggregate_paths[direction]),
                "connection_path": str(per_connection_path),
                "preview_hex": payload[:64].hex(),
            }
            if len(payload) <= self.inline_payload_limit:
                record["payload_b64"] = base64.b64encode(payload).decode("ascii")
            else:
                record["payload_b64"] = None
                record["payload_omitted_reason"] = "payload exceeds inline payload limit"

            self._events.write(json.dumps(record, ensure_ascii=False) + "\n")
            self._events.flush()


class ProxyServer:
    def __init__(
        self,
        listen_host: str,
        listen_port: int,
        target_host: str,
        target_port: int,
        logger: CaptureLogger,
        connect_timeout_sec: float,
        buffer_size: int,
    ) -> None:
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.target_host = target_host
        self.target_port = target_port
        self.logger = logger
        self.connect_timeout_sec = connect_timeout_sec
        self.buffer_size = buffer_size
        self._next_connection_id = 0

    async def handle_client(
        self,
        manager_reader: asyncio.StreamReader,
        manager_writer: asyncio.StreamWriter,
    ) -> None:
        self._next_connection_id += 1
        connection_id = self._next_connection_id
        manager_peer = manager_writer.get_extra_info("peername")
        await self.logger.event(
            "connection_open",
            connection_id=connection_id,
            manager_peer=manager_peer,
            target=f"{self.target_host}:{self.target_port}",
        )

        try:
            client_reader, client_writer = await asyncio.wait_for(
                asyncio.open_connection(self.target_host, self.target_port),
                timeout=self.connect_timeout_sec,
            )
        except Exception as exc:  # noqa: BLE001 - logged and returned to TCP peer.
            await self.logger.event(
                "target_connect_failed",
                connection_id=connection_id,
                error=repr(exc),
            )
            manager_writer.close()
            await manager_writer.wait_closed()
            return

        chunk_counters = {
            DIRECTION_MANAGER_TO_CLIENT: 0,
            DIRECTION_CLIENT_TO_MANAGER: 0,
        }

        async def pipe(
            reader: asyncio.StreamReader,
            writer: asyncio.StreamWriter,
            direction: str,
        ) -> None:
            try:
                while True:
                    payload = await reader.read(self.buffer_size)
                    if not payload:
                        await self.logger.event(
                            "direction_eof",
                            connection_id=connection_id,
                            direction=direction,
                        )
                        break
                    chunk_counters[direction] += 1
                    writer.write(payload)
                    await writer.drain()
                    await self.logger.chunk(
                        connection_id,
                        direction,
                        chunk_counters[direction],
                        payload,
                    )
            except Exception as exc:  # noqa: BLE001 - proxy must preserve evidence.
                await self.logger.event(
                    "direction_error",
                    connection_id=connection_id,
                    direction=direction,
                    error=repr(exc),
                )
            finally:
                writer.close()
                try:
                    await writer.wait_closed()
                except Exception:
                    pass

        await asyncio.gather(
            pipe(manager_reader, client_writer, DIRECTION_MANAGER_TO_CLIENT),
            pipe(client_reader, manager_writer, DIRECTION_CLIENT_TO_MANAGER),
        )
        await self.logger.event("connection_closed", connection_id=connection_id)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--listen-host", default="127.0.0.1")
    parser.add_argument("--listen-port", type=int, required=True)
    parser.add_argument("--target-host", default="127.0.0.1")
    parser.add_argument("--target-port", type=int, required=True)
    parser.add_argument("--capture-dir", type=Path, required=True)
    parser.add_argument("--ready-file", type=Path)
    parser.add_argument("--connect-timeout-sec", type=float, default=30.0)
    parser.add_argument("--buffer-size", type=int, default=65536)
    parser.add_argument("--inline-payload-limit", type=int, default=65536)
    return parser.parse_args()


async def async_main() -> None:
    args = parse_args()
    logger = CaptureLogger(args.capture_dir, args.inline_payload_limit)
    proxy = ProxyServer(
        listen_host=args.listen_host,
        listen_port=args.listen_port,
        target_host=args.target_host,
        target_port=args.target_port,
        logger=logger,
        connect_timeout_sec=args.connect_timeout_sec,
        buffer_size=args.buffer_size,
    )

    manifest = {
        "schema": "protocol-proxy.manifest.v1",
        "started_at": utc_now(),
        "listen_host": args.listen_host,
        "listen_port": args.listen_port,
        "target_host": args.target_host,
        "target_port": args.target_port,
        "capture_dir": str(args.capture_dir),
        "buffer_size": args.buffer_size,
        "inline_payload_limit": args.inline_payload_limit,
    }
    (args.capture_dir / "proxy_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    server = await asyncio.start_server(
        proxy.handle_client,
        args.listen_host,
        args.listen_port,
    )
    sockets = ", ".join(str(sock.getsockname()) for sock in (server.sockets or []))
    await logger.event("proxy_listening", sockets=sockets)
    print(f"proxy-listening {sockets}", flush=True)

    if args.ready_file:
        args.ready_file.parent.mkdir(parents=True, exist_ok=True)
        args.ready_file.write_text(
            json.dumps({"ready": True, "ts": utc_now(), "sockets": sockets}, indent=2),
            encoding="utf-8",
        )

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for signame in ("SIGINT", "SIGTERM"):
        signum = getattr(signal, signame, None)
        if signum is not None:
            try:
                loop.add_signal_handler(signum, stop_event.set)
            except NotImplementedError:
                pass

    async with server:
        await stop_event.wait()
        server.close()
        await server.wait_closed()
        await logger.event("proxy_stopped")
        await logger.close()


def main() -> int:
    try:
        asyncio.run(async_main())
        return 0
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
