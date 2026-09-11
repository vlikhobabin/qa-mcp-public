#!/usr/bin/env python3
"""card 120 e2e WRITE — full stack: container MCP -> protocol open (host.docker.internal:15381) ->
host-agent /type SendInput into the 1C Наименование field -> window-targeted PrintWindow proof."""
import asyncio, json
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

URL = "http://127.0.0.1:8000/mcp/"
WIN = "Демонстрационное приложение"

def parse(res):
    sc = getattr(res, "structuredContent", None)
    if sc:
        return sc
    txt = "".join(getattr(c, "text", "") for c in (res.content or []))
    try:
        return json.loads(txt)
    except Exception:
        return {"_text": txt[:800]}

async def main():
    async with streamablehttp_client(URL) as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            rw = await s.call_tool("write_form_value_xtest",
                                   {"value": "E2E120Контейнер", "field": "Наименование", "save": False})
            dw = parse(rw)
            print("WRITE", json.dumps(dw, ensure_ascii=False)[:800])
            rs = await s.call_tool("capture_screenshot", {"display": "win", "window": WIN})
            ds = parse(rs)
            print("SHOT", json.dumps(ds, ensure_ascii=False)[:400])

asyncio.run(main())
