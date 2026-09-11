"""MCP stdio integration — a real stdio roundtrip to the native server.

Launches `python -m qa_mcp.mcp_server` as a subprocess, connects an MCP client over stdio, and
calls the pure `transpile` tool (no live TestClient needed) — validating the MCP surface end-to-end
over the real protocol, not just the in-process tool functions.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

REPO_ROOT = Path(__file__).resolve().parents[2]

FEATURE = "# language: ru\nСценарий: s\n  Дано я читаю активное окно\n  И я нажимаю на кнопку с именем 'PF_RESET_STATE'\n"


def _server_params() -> StdioServerParameters:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    return StdioServerParameters(command=sys.executable, args=["-m", "qa_mcp.mcp_server"], env=env)


async def _roundtrip() -> tuple[set[str], dict]:
    async with stdio_client(_server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            result = await session.call_tool("transpile", {"feature_text": FEATURE})
    names = {t.name for t in tools.tools}
    payload = result.structuredContent
    if payload is None:
        payload = json.loads(result.content[0].text)
    return names, payload


def test_mcp_stdio_transpile_roundtrip() -> None:
    names, payload = asyncio.run(_roundtrip())
    assert {"transpile", "run_scenario", "run_step"}.issubset(names)
    # FastMCP may wrap a dict return as {"result": ...}
    data = payload.get("result", payload) if isinstance(payload, dict) else payload
    kinds = [s["kind"] for s in data["steps"]]
    assert kinds == ["read_active_window", "click_button"]
    assert data["unmapped"] == []
