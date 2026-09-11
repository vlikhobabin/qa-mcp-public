#!/usr/bin/env python3
"""Convert a tcpdump pcap of the manager↔client link into the proxy capture format.

The native capture pipeline (protocol_proxy.py) writes `traffic.jsonl` with per-recv
`chunk` events that `replay_probe.read_capture_chunks` consumes. tcpdump yields pcap
instead. The proxy chunks at socket-recv granularity ≈ TCP segments, so emitting one
chunk per payload-bearing TCP segment is equivalent for the analyzers.

This is a dependency-free pcap reader (linktype 1 / EN10MB, the loopback default) that
splits by direction using the known client TestClient port:
  - dst_port == client_port -> manager_to_client
  - src_port == client_port -> client_to_manager

Usage:
  python3 pcap_to_traffic.py <pcap> <client_port> <out_capture_dir>
"""
import base64
import hashlib
import json
import struct
import sys
from pathlib import Path

MANAGER_TO_CLIENT = "manager_to_client"
CLIENT_TO_MANAGER = "client_to_manager"


def iter_packets(pcap: Path):
    data = pcap.read_bytes()
    magic = struct.unpack("<I", data[:4])[0]
    if magic == 0xA1B2C3D4:
        endian, usec = "<", True
    elif magic == 0xD4C3B2A1:
        endian, usec = ">", True
    elif magic == 0xA1B23C4D:
        endian, usec = "<", False
    else:
        raise ValueError(f"unknown pcap magic {magic:#x}")
    linktype = struct.unpack(endian + "I", data[20:24])[0]
    if linktype != 1:
        raise ValueError(f"only linktype 1 (EN10MB) supported, got {linktype}")
    off = 24
    while off + 16 <= len(data):
        ts_sec, ts_frac, incl, orig = struct.unpack(endian + "IIII", data[off : off + 16])
        off += 16
        pkt = data[off : off + incl]
        off += incl
        yield ts_sec, ts_frac, pkt


def parse_tcp(pkt: bytes):
    if len(pkt) < 14:
        return None
    eth_type = struct.unpack(">H", pkt[12:14])[0]
    if eth_type != 0x0800:  # IPv4
        return None
    ip = pkt[14:]
    if len(ip) < 20:
        return None
    ihl = (ip[0] & 0x0F) * 4
    if ip[9] != 6:  # TCP
        return None
    total_len = struct.unpack(">H", ip[2:4])[0]
    tcp = ip[ihl:]
    if len(tcp) < 20:
        return None
    src_port, dst_port = struct.unpack(">HH", tcp[0:4])
    data_off = (tcp[12] >> 4) * 4
    payload_len = total_len - ihl - data_off
    if payload_len <= 0:
        return None
    payload = tcp[data_off : data_off + payload_len]
    return src_port, dst_port, payload


def main(argv):
    if len(argv) not in (3, 4):
        print(__doc__)
        return 2
    pcap = Path(argv[0])
    client_port = int(argv[1])
    out = Path(argv[2])
    # optional: restrict to ONE manager<->client connection (the manager's source port). tcpdump on the
    # client listen port captures EVERY connection (incl. aborted reconnects) → mixing them corrupts the
    # frame order. Pass the dominant manager port to isolate the real session.
    manager_port = int(argv[3]) if len(argv) == 4 else None
    (out).mkdir(parents=True, exist_ok=True)
    traffic = (out / "traffic.jsonl").open("w", encoding="utf-8")
    counters = {MANAGER_TO_CLIENT: 0, CLIENT_TO_MANAGER: 0}
    totals = {MANAGER_TO_CLIENT: 0, CLIENT_TO_MANAGER: 0}
    for ts_sec, ts_frac, pkt in iter_packets(pcap):
        parsed = parse_tcp(pkt)
        if not parsed:
            continue
        src_port, dst_port, payload = parsed
        if dst_port == client_port:
            direction = MANAGER_TO_CLIENT
            other = src_port
        elif src_port == client_port:
            direction = CLIENT_TO_MANAGER
            other = dst_port
        else:
            continue
        if manager_port is not None and other != manager_port:
            continue
        chunk_no = counters[direction]
        counters[direction] += 1
        totals[direction] += len(payload)
        rec = {
            "ts": f"{ts_sec}.{ts_frac}",
            "event": "chunk",
            "connection_id": 0,
            "direction": direction,
            "chunk_no": chunk_no,
            "byte_count": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "preview_hex": payload[:64].hex(),
            "payload_b64": base64.b64encode(payload).decode("ascii"),
        }
        traffic.write(json.dumps(rec, ensure_ascii=False) + "\n")
    traffic.close()
    print(json.dumps({
        "out": str(out),
        "manager_to_client_chunks": counters[MANAGER_TO_CLIENT],
        "client_to_manager_chunks": counters[CLIENT_TO_MANAGER],
        "manager_to_client_bytes": totals[MANAGER_TO_CLIENT],
        "client_to_manager_bytes": totals[CLIENT_TO_MANAGER],
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
