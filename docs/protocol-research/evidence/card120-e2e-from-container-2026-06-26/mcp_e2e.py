#!/usr/bin/env python3
"""card 120 e2e — drive the thin container's MCP tools: protocol read (host.docker.internal:15381) +
host-agent display route (get_window_list / capture_screenshot via :8001)."""
import asyncio, json
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

URL = "http://127.0.0.1:8000/mcp/"

def show(label, res):
    out = {}
    sc = getattr(res, "structuredContent", None)
    if sc:
        out = sc
    else:
        parts = []
        for c in (res.content or []):
            parts.append(getattr(c, "text", str(c)))
        txt = "".join(parts)
        try:
            out = json.loads(txt)
        except Exception:
            out = {"_text": txt[:600]}
    print("=== %s ===" % label)
    print(json.dumps(out, ensure_ascii=False)[:1400])
    return out

async def main():
    async with streamablehttp_client(URL) as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = await s.list_tools()
            print("TOOLS_COUNT", len(tools.tools))

            # 1) PROTOCOL path (TCP -> host.docker.internal:15381)
            r1 = await s.call_tool("read_form_descriptor", {})
            d1 = show("read_form_descriptor (protocol)", r1)

            # 2) HOST-AGENT display route: window list (EnumWindows on session 1)
            r2 = await s.call_tool("get_window_list", {"display": "win"})
            d2 = show("get_window_list (host-agent)", r2)

            # 3) HOST-AGENT display route: screenshot (PrintWindow on session 1)
            r3 = await s.call_tool("capture_screenshot", {"display": "win"})
            d3 = show("capture_screenshot (host-agent)", r3)

            # compact verdict line for easy grep
            fc = d1.get("field_count") or len(d1.get("fields") or {})
            print("VERDICT", json.dumps({
                "protocol_fields": fc,
                "windows": d2.get("count"),
                "screenshot_path": d3.get("path"),
                "screenshot_backend": d3.get("tool") or d3.get("backend"),
            }, ensure_ascii=False))

asyncio.run(main())
