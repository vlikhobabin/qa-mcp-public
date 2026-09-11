#!/usr/bin/env python3
"""Minimal MCP (Streamable HTTP) client for the genuine Vanessa manager backend.

On Linux the vanessa-mcp lazy wrapper is in `deferred` mode (it does not start a
live backend), so live driving goes straight to the EPF's runMcp server on
http://127.0.0.1:9874/mcp. This is that direct driver: initialize -> notify ->
tools/call, parsing the SSE `data:` frame.

Usage:
    vanessa_mcp_call.py <tool> [json-args]
    vanessa_mcp_call.py --list
Env:
    VANESSA_MCP_URL  (default http://127.0.0.1:9874/mcp)
"""
import json
import os
import sys
import urllib.request

URL = os.environ.get("VANESSA_MCP_URL", "http://127.0.0.1:9874/mcp")
TIMEOUT = int(os.environ.get("VANESSA_MCP_TIMEOUT", "60"))
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}


def _post(payload, session_id=None, want_headers=False):
    headers = dict(HEADERS)
    if session_id:
        headers["mcp-session-id"] = session_id
    req = urllib.request.Request(
        URL, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST"
    )
    resp = urllib.request.urlopen(req, timeout=TIMEOUT)
    body = resp.read().decode("utf-8", "replace")
    sid = resp.headers.get("mcp-session-id")
    # Streamable HTTP returns SSE: pull the first JSON `data:` line.
    data = None
    for line in body.splitlines():
        if line.startswith("data:"):
            data = json.loads(line[5:].strip())
            break
    if data is None and body.strip():
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = {"raw": body}
    return (data, sid) if want_headers else data


def session():
    data, sid = _post(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "qa-mcp-driver", "version": "0"},
            },
        },
        want_headers=True,
    )
    _post({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}, sid)
    return sid


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    sid = session()
    if argv[0] == "--list":
        data = _post({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}, sid)
        for t in data.get("result", {}).get("tools", []):
            print(t["name"])
        return 0
    tool = argv[0]
    if len(argv) > 1:
        spec = argv[1]
        if spec.startswith("@"):
            with open(spec[1:], encoding="utf-8") as fh:
                args = json.load(fh)
        else:
            args = json.loads(spec)
    else:
        args = {}
    data = _post(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": tool, "arguments": args},
        },
        sid,
    )
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
