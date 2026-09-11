"""Card 110 (E-XV) — headless «Замер производительности» over the 1C debug protocol → code COVERAGE (107) + PERF (108).

Beyond Vanessa: drive the `/e1crdbg/` debugger side from Python, run a scenario under a performance measurement, and
emit per-line {execution count → coverage, time → perf}. The protocol was decoded from 1C:EDT's `.xcore` model; the
full handshake + result schema are in `evidence/card110-*`.

Two layers, kept separate so the analysis is unit-testable with NO lab:
- PURE: ``extract_measures`` / ``build_report`` / ``render_report`` / ``resolve_module`` — parse a captured
  ``pingDebugUIParams`` response (a `DBGUIExtCmdInfoMeasure` → `PerformanceInfoMain`) into a named coverage+perf
  report. ``build_report`` takes an injectable ``resolver`` so module-name resolution is testable offline.
- LIVE: ``DebuggerSession`` (the rdbg HTTP client) + ``measure_scenario`` (boot a debug TestClient, замер a
  ``run_scenario``, collect + parse). Verified live on real ``vanessa_client``.
"""
from __future__ import annotations

import json
import subprocess
import threading
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any, Callable

# --- protocol constants (decoded from EDT com._1c.g5.v8.dt.debug.model .xcore + debug.core) ---
NIL_UUID = "00000000-0000-0000-0000-000000000000"
MEASURE_RESULT_CMD = 6  # DBGUIExtCmds.measureResultProcessing
_NS = ('xmlns="http://v8.1c.ru/8.3/debugger/debugBaseData" '
       'xmlns:dr="http://v8.1c.ru/8.3/debugger/debugRDBGRequestResponse" '
       'xmlns:aa="http://v8.1c.ru/8.3/debugger/debugAutoAttach" '
       'xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:xs="http://www.w3.org/2001/XMLSchema" '
       'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"')
# target types to declare for auto-attach (DebugTargetType literals)
AUTO_ATTACH_TYPES = ("ManagedClient", "Server", "ServerEmulation", "COMConnector", "WEBClient",
                     "HTTPService", "WEBService", "OData", "JOB")
# config-source dir name -> 1C metadata kind (for module-name resolution)
_MDO_KIND = {"Documents": "Документ", "Catalogs": "Справочник", "DataProcessors": "Обработка",
             "Reports": "Отчёт", "InformationRegisters": "РегистрСведений",
             "AccumulationRegisters": "РегистрНакопления", "CommonModules": "ОбщийМодуль",
             "ChartsOfCharacteristicTypes": "ПланВидовХарактеристик"}

Module = dict[str, Any]


# ====================================================================================================
# PURE: parse + report
# ====================================================================================================
def extract_measures(ping_response: str | bytes | dict) -> list[dict]:
    """From a ``pingDebugUIParams`` response (JSON text or already-parsed dict), return the list of
    ``PerformanceInfoMain`` payloads carried by ``DBGUIExtCmdInfoMeasure`` events."""
    data = json.loads(ping_response) if isinstance(ping_response, (str, bytes)) else (ping_response or {})
    result = ((data or {}).get("response") or {}).get("result") or []
    out: list[dict] = []
    for cmd in result:
        if not isinstance(cmd, dict):
            continue
        meas = cmd.get("measure")
        if meas and (cmd.get("cmdIDNum") == MEASURE_RESULT_CMD or "moduleData" in meas):
            out.append(meas)
    return out


def _ticks_to_us(ticks: float, freq: float) -> float:
    """Convert a durability value (in performance-counter ticks) to microseconds (freq = ticks/sec)."""
    if not freq:
        return float(ticks)
    return round(ticks * 1_000_000 / freq, 1)


def build_report(measures: list[dict], resolver: Callable[[str], Module] | None = None) -> dict[str, Any]:
    """Aggregate ``PerformanceInfoMain`` payloads into a coverage(107)+perf(108) report.

    ``resolver(object_id) -> {object, module}`` names the module (injectable; default leaves names unresolved).
    Returns ``{modules: [...], totals: {...}, measures: [...]}``: per module the COVERED lines (with per-line
    frequency = exec count and durability/pure µs = perf), aggregated across all measure events by
    (objectID, propertyID).
    """
    resolve = resolver or (lambda oid: {"object": None, "module": oid or None})
    mods: dict[tuple[str, str], dict] = {}
    measure_summ: list[dict] = []
    for meas in measures:
        freq = meas.get("performanceFrequency") or 1_000_000
        measure_summ.append({
            "session_id": meas.get("sessionID"),
            "total_us": _ticks_to_us(meas.get("totalDurability") or 0, freq),
            "modules": len(meas.get("moduleData") or []),
        })
        for mod in meas.get("moduleData") or []:
            mid = mod.get("moduleID") or {}
            oid, pid = mid.get("objectID") or "", mid.get("propertyID") or ""
            key = (oid, pid)
            info = resolve(oid)
            entry = mods.setdefault(key, {"object": info.get("object"), "module": info.get("module"),
                                          "object_id": oid, "property_id": pid, "lines": {}})
            for ln in mod.get("lineInfo") or []:
                no = ln.get("lineNo")
                cur = entry["lines"].setdefault(no, {"frequency": 0, "us": 0.0, "pure_us": 0.0})
                cur["frequency"] += ln.get("frequency") or 0
                cur["us"] = round(cur["us"] + _ticks_to_us(ln.get("durability") or 0, freq), 1)
                cur["pure_us"] = round(cur["pure_us"] + _ticks_to_us(ln.get("pureDurability") or 0, freq), 1)

    modules = []
    for (oid, pid), e in mods.items():
        lines = [{"line": no, **vals} for no, vals in sorted(e["lines"].items(), key=lambda kv: kv[0] or 0)]
        modules.append({"object": e["object"], "module": e["module"], "object_id": oid, "property_id": pid,
                        "covered_lines": len(lines), "us": round(sum(l["us"] for l in lines), 1), "lines": lines})
    modules.sort(key=lambda m: (str(m["object"]), str(m["module"])))
    totals = {
        "measure_events": len(measures),
        "modules": len(modules),
        "covered_lines": sum(m["covered_lines"] for m in modules),
        "total_us": round(sum(m["us"] for m in modules), 1),
    }
    return {"modules": modules, "totals": totals, "measures": measure_summ}


def render_report(report: dict[str, Any]) -> str:
    """Human-readable coverage(107)+perf(108) text from :func:`build_report`."""
    t = report["totals"]
    out = [f"# «Замер производительности» — coverage(107) + perf(108) — {t['measure_events']} measure event(s)",
           f"# {t['modules']} module(s), {t['covered_lines']} covered line(s), {round(t['total_us']/1000, 3)} ms total\n"]
    for m in report["modules"]:
        name = f"{m['object']} :: {m['module']}" if m["object"] else f"<{m['module']}>"
        out.append(f"• {name}  — COVERED {m['covered_lines']} line(s), {round(m['us']/1000, 3)} ms")
        for ln in m["lines"]:
            out.append(f"    line {str(ln['line']).rjust(4)}: freq={ln['frequency']}  {ln['us']}µs (pure {ln['pure_us']}µs)")
    return "\n".join(out)


def make_mdo_resolver(src_root: str | Path) -> Callable[[str], Module]:
    """Build a ``resolver(object_id) -> {object, module}`` that maps a ``BSLModuleIdInternal.objectID`` UUID to a
    named module by scanning the EDT config source tree (``<root>/<Documents|Catalogs|…>/<Name>/<Name>.mdo``).
    The UUID is either a ``<forms uuid=…>`` node (a form module) or the root ``<mdclass:… uuid=…>`` (the object
    module). Results are cached. No external tools — pure file scan.
    """
    root = Path(src_root)
    cache: dict[str, Module] = {}

    def resolver(object_id: str) -> Module:
        if not object_id:
            return {"object": None, "module": None}
        if object_id in cache:
            return cache[object_id]
        res: Module = {"object": None, "module": object_id}
        for mdo in root.rglob("*.mdo"):
            try:
                text = mdo.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if object_id not in text:
                continue
            parts = mdo.relative_to(root).parts  # e.g. ('Documents','Заказ','Заказ.mdo')
            obj = f"{_MDO_KIND.get(parts[0], parts[0])}.{parts[1]}" if len(parts) >= 2 else mdo.stem
            label = "Модуль"
            for i, line in enumerate(text.splitlines()):
                if object_id in line:
                    if "<forms uuid=" in line:
                        # the next <name> is the form name
                        rest = "\n".join(text.splitlines()[i:i + 4])
                        nm = rest.split("<name>")[1].split("</name>")[0] if "<name>" in rest else "?"
                        label = f"Форма.{nm}"
                    elif "mdclass:" in line:
                        label = "МодульОбъекта"
                    break
            res = {"object": obj, "module": label}
            break
        cache[object_id] = res
        return res

    return resolver


# ====================================================================================================
# LIVE: rdbg HTTP client + scenario driver
# ====================================================================================================
class DebuggerSession:
    """The DEBUGGER side of `/e1crdbg/rdbg` (UTF-8 XML/HTTP). One ``idOfDebuggerUI`` per session.

    Sequence (all decoded from EDT): ``attach_ui`` (registers the UI; returns HTTP 400 but DOES register) →
    ``init_settings`` → ``set_auto_attach`` → ``get_targets`` → ``attach_targets`` → ``set_measure_mode`` →
    ``poll_events`` (the real poll is ``pingDebugUIParams`` with the ui in the ``dbgui`` query param, no body).
    """

    def __init__(self, dbg_url: str = "http://127.0.0.1:1550", alias: str = "DefAlias", ui: str | None = None):
        self.dbg_url = dbg_url.rstrip("/")
        self.alias = alias
        self.ui = ui or str(uuid.uuid4())

    def _base(self) -> str:
        return f"<dr:infoBaseAlias>{self.alias}</dr:infoBaseAlias><dr:idOfDebuggerUI>{self.ui}</dr:idOfDebuggerUI>"

    def _post(self, cmd: str, inner: str = "", query: str = "", body: bytes | None = None, timeout: float = 12) -> dict:
        if body is None:
            body = (f'<?xml version="1.0" encoding="UTF-8"?><request {_NS}>{inner}</request>').encode("utf-8")
        url = f"{self.dbg_url}/e1crdbg/rdbg?cmd={cmd}{query}"
        req = urllib.request.Request(url, data=body, method="POST",
                                     headers={"Content-Type": "application/xml; charset=utf-8",
                                              "Accept-Charset": "utf-8", "Accept": "application/xml"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 — lab-local debug server
                return {"status": r.status, "body": r.read().decode("utf-8-sig", "replace")}
        except urllib.error.HTTPError as e:
            return {"status": e.code, "body": e.read().decode("utf-8-sig", "replace")}
        except Exception as exc:  # noqa: BLE001
            return {"status": None, "body": repr(exc)}

    def attach_ui(self) -> dict:  # returns 400 (response-serialization quirk) but registers the ui server-side
        return self._post("attachDebugUI", self._base()
                          + "<dr:options><dr:foregroundAbility>false</dr:foregroundAbility></dr:options>")

    def init_settings(self) -> dict:
        return self._post("initSettings", self._base() + "<dr:data><dr:breakOnNextLine>false</dr:breakOnNextLine></dr:data>")

    def set_auto_attach(self, types: tuple[str, ...] = AUTO_ATTACH_TYPES) -> dict:
        aa = "".join(f"<aa:targetType>{t}</aa:targetType>" for t in types)
        return self._post("setAutoAttachSettings", self._base() + f"<dr:autoAttachSettings>{aa}</dr:autoAttachSettings>")

    def get_targets(self) -> list[dict]:
        r = self._post("getDbgTargets", self._base())
        try:
            return json.loads(r["body"] or "{}").get("response", {}).get("id", []) or []
        except Exception:  # noqa: BLE001
            return []

    def attach_targets(self, ids: list[str]) -> dict:
        light = "".join(f"<dr:id><id>{i}</id></dr:id>" for i in ids if i)
        return self._post("attachDetachDbgTargets", self._base() + "<dr:attach>true</dr:attach>" + light)

    def set_measure_mode(self, seance: str) -> dict:  # fresh UUID = start, NIL_UUID = stop
        return self._post("setMeasureMode", self._base() + f"<dr:measureModeSeanceID>{seance}</dr:measureModeSeanceID>")

    def poll_events(self) -> dict:
        return self._post("pingDebugUIParams", query=f"&dbgui={self.ui}", body=b"")

    def handshake(self) -> list[dict]:
        """attach_ui + init_settings + set_auto_attach, then retry get_targets until the targets register."""
        self.attach_ui()
        time.sleep(3)
        self.init_settings()
        self.set_auto_attach()
        for _ in range(10):
            targets = self.get_targets()
            if targets:
                return targets
            time.sleep(2)
        return []


def measure_scenario(
    feature_text: str,
    *,
    host: str = "127.0.0.1",
    port: int = 15381,
    env_file: str = ".ai1c/vanessa-qa-mcp.env",
    src_root: str | None = None,
    dbg_port: int = 1550,
    poll_interval: float = 0.4,
    drain_sec: float = 8.0,
    result_wait_sec: float = 22.0,
    max_ms: float | None = None,
) -> dict[str, Any]:
    """LIVE: boot a debug-attached TestClient, run ``feature_text`` under a «Замер производительности», and return a
    coverage(107)+perf(108) report. Self-contained: starts ``dbgs``, launches the client with
    ``/DEBUG -http /DEBUGGERURL``, drives the full rdbg handshake, toggles measure around a ``run_scenario``, polls
    the result, parses it, and tears everything down (restarts Apache). ``src_root`` (the EDT config ``src``)
    enables module-name resolution. ``max_ms`` sets a perf assertion on the total measured time. Returns
    ``{ok, report, scenario_ok, perf_ok, raw_event_count}``.
    """
    import os

    from ..protocol.lifecycle import TestClientTarget, launch_test_client, load_env_file

    env = load_env_file(env_file)
    target = TestClientTarget.from_env(env, host=host, port=port, manage_apache=True, clear_lock=True,
                                       extra_args=["/DEBUG", "-http", "/DEBUGGERURL", f"http://{host}:{dbg_port}"])
    dbgs_bin = str(Path(target.platform_root) / "dbgs")
    dbgs = subprocess.Popen([dbgs_bin, f"--addr={host}", f"--port={dbg_port}", f"--ownerPID={os.getpid()}"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    time.sleep(3)

    sess = DebuggerSession(dbg_url=f"http://{host}:{dbg_port}")
    events: list[dict] = []
    stop = threading.Event()
    handle = None
    scenario_ok: Any = None

    def pump():
        while not stop.is_set():
            r = sess.poll_events()
            if r.get("status") == 200 and r.get("body"):
                events.append(r["body"])
            time.sleep(poll_interval)

    try:
        handle = launch_test_client(target, wait_sec=120, settle_sec=8)
        time.sleep(2)
        targets = sess.handshake()
        target_ids = [t.get("id") for t in targets if t.get("id")]
        sess.attach_targets(target_ids)
        seance = str(uuid.uuid4())
        sess.set_measure_mode(seance)        # START
        time.sleep(1)
        threading.Thread(target=pump, daemon=True).start()
        from .. import mcp_server
        res = mcp_server.run_scenario(feature_text=feature_text, host=host, port=port)
        scenario_ok = isinstance(res, dict) and res.get("status") == "passed"
        time.sleep(drain_sec)
        sess.set_measure_mode(NIL_UUID)      # STOP -> flushes the measure result
        deadline = time.monotonic() + result_wait_sec
        while time.monotonic() < deadline:
            if any("moduleData" in e or "InfoMeasure" in e for e in events):
                break
            time.sleep(0.5)
    finally:
        stop.set()
        time.sleep(0.6)
        try:
            if handle is not None:
                handle.stop()
        except Exception:  # noqa: BLE001
            pass
        try:
            dbgs.terminate()
        except Exception:  # noqa: BLE001
            pass
        subprocess.run(["sudo", "-n", "systemctl", "start", "apache2"], check=False)

    measures: list[dict] = []
    for body in events:
        measures.extend(extract_measures(body))
    resolver = make_mdo_resolver(src_root) if src_root else None
    report = build_report(measures, resolver=resolver)
    perf_ok = None if max_ms is None else (report["totals"]["total_us"] <= max_ms * 1000)
    return {
        "ok": bool(measures),
        "scenario_ok": scenario_ok,
        "raw_event_count": len(events),
        "perf_ok": perf_ok,
        "max_ms": max_ms,
        "report": report,
        "report_text": render_report(report),
    }
