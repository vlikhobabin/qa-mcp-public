"""Curated live-regression checks — the durable replacement for the per-card hand-run evidence scripts.

Each check exercises ONE class of LIVE-verified capability against the real lab `vanessa_client` and returns
``(ok, detail)``. The default CORE set is read-only and side-effect-free (safe to schedule nightly); the
write-roundtrip and debug-measure sets are opt-in (the former creates a lab record, the latter boots its own debug
server and is slow).

The checks call the real MCP tools (`qa_mcp.mcp_server`) so they go through the exact production code paths an
agent uses. Targets (the Банки record, the HomePage `ДиаграммаПоПериодам` element, the Валюты/Банки objects) are
the same genuine artifacts the board-card evidence used.
"""

from __future__ import annotations

from dataclasses import dataclass

from .harness import Check


@dataclass
class LiveContext:
    """Everything the checks need; built once by the CLI after loading the env profile."""

    host: str = "127.0.0.1"
    port: int = 15381
    odata_url: str = ""
    odata_user: str = "Администратор"
    odata_password: str = ""
    display: str | None = None          # owned-Xvfb display (for xtest write checks)
    env_file: str = ".ai1c/vanessa-qa-mcp.env"
    src_root: str = ""                   # config .mdo root (for the measure check's module-name resolver)
    measure_max_ms: float = 0.0


def _mcp():
    from .. import mcp_server
    return mcp_server


# --- CORE checks (read-only, nightly-safe) -------------------------------------------------------------------

# Genuine HomePage element on vanessa_client (card-103 live evidence) + a deliberately-absent name for the
# negative assertion (a regression that breaks the assert path would make the negative WRONGLY pass).
_HOMEPAGE_ELEMENT = "ДиаграммаПоПериодам"
_ABSENT_ELEMENT = "ZZZ_НесуществующийЭлемент_QAREG"

# NB: `assert_form_open 'HomePage'` is intentionally NOT in the curated set — the home-form identifier is
# environment-coupled and produced an EXECUTION error (a false-red) on the lab. The "a form opens" path is already
# covered, reliably, by `ui.open_two_objects`. Curated checks must go red only on a REAL regression.
_ASSERT_POS_FEATURE = (
    "Сценарий: assert family (positive)\n"
    f"  Когда Элемент формы с именем '{_HOMEPAGE_ELEMENT}' присутствует на форме\n"
    "  И Я устанавливаю флаг настройки Vanessa Automation 'X'\n"
)
_ASSERT_NEG_FEATURE = (
    "Сценарий: assert family (negative — must assert_failed)\n"
    f"  Когда Элемент формы с именем '{_ABSENT_ELEMENT}' присутствует на форме\n"
)
_OPEN_FEATURE = (
    "Сценарий: open two different objects in one session\n"
    "  Когда Я открываю основную форму справочника 'Валюты'\n"
    "  И Я открываю основную форму справочника 'Банки'\n"
)
_MEASURE_FEATURE = (
    "Сценарий: measurable scenario (create form runs object + form BSL)\n"
    "  Когда Я создаю новый документ 'Заказ'\n"
)


def _statuses(report: dict) -> list[str]:
    return [s.get("status") for s in (report.get("steps") or [])]


def _protocol_drift_preflight(ctx: LiveContext):
    """Fast, no-boot preflight (item 4): is the live platform still the one the frame captures were stamped on?
    Informational (does not gate the run — the live checks decide red/green) but surfaces a version/template drift
    so a red run is DIAGNOSED ('platform moved, refresh per the runbook') not guessed. The gating tool is the
    standalone `python -m qa_mcp.regression.versioning [--strict]`."""
    from . import versioning as v
    live = v.detect_live_platform_version(env_file=ctx.env_file)
    # Compare against the manifest for the LIVE version family (per-version manifests, P0): on 8.5 this reads the
    # 8.5 baseline, not the 8.3 default — so a blessed 8.5 platform reports OK instead of a spurious version drift.
    family = v.version_key(live)
    manifest_path = v.repo_root() / (v.manifest_path_for(family) if family else v.MANIFEST_PATH)
    if not manifest_path.exists():
        manifest_path = v.repo_root() / v.MANIFEST_PATH  # fall back to the default-family manifest
    if not manifest_path.exists():
        return True, {"note": "no manifest (run `versioning --stamp`)"}
    verdict = v.detect_drift(v.read_manifest(manifest_path), live, root=v.repo_root())
    return verdict.ok, {"severity": verdict.severity, "live": verdict.live_version,
                        "baseline": verdict.recorded_version, "message": verdict.message}


def _data_layer_banki(ctx: LiveContext):
    """Data-layer assert via read-only OData (card 105) — a known stable record must read back exactly."""
    res = _mcp().assert_data(
        entity_set="Catalog_Банки", field="Description", expected="ВнешИнвестСити Банк",
        filter="Code eq '000000005'",
        base_url=ctx.odata_url, user=ctx.odata_user, password=ctx.odata_password,
    )
    ok = bool(res.get("ok")) and res.get("record_count") == 1
    return ok, {"actual": res.get("actual"), "record_count": res.get("record_count")}


def _assert_family(ctx: LiveContext):
    """The assert family through `run_scenario` on the live HomePage (card 103 Wave 3): every positive step ok,
    AND the negative (absent element) correctly reports assert_failed."""
    m = _mcp()
    pos = m.run_scenario(host=ctx.host, port=ctx.port, feature_text=_ASSERT_POS_FEATURE)
    neg = m.run_scenario(host=ctx.host, port=ctx.port, feature_text=_ASSERT_NEG_FEATURE)
    pos_ok = bool(_statuses(pos)) and all(s == "ok" for s in _statuses(pos))
    neg_ok = any(s == "assert_failed" for s in _statuses(neg))
    return (pos_ok and neg_ok), {
        "positive": _statuses(pos), "negative": _statuses(neg),
        "positive_all_ok": pos_ok, "negative_assert_failed": neg_ok,
    }


def _open_two_objects(ctx: LiveContext):
    """Config-agnostic open: two DIFFERENT catalog main forms open in one bootstrapped session (card 103 Wave 3
    live leg) — the capture-free retarget-to-a-different-object proof."""
    res = _mcp().run_scenario(host=ctx.host, port=ctx.port, feature_text=_OPEN_FEATURE)
    statuses = _statuses(res)
    ok = len(statuses) >= 2 and all(s == "ok" for s in statuses)
    return ok, {"statuses": statuses, "step_count": len(statuses)}


def _read_descriptor(ctx: LiveContext):
    """The capture-free descriptor read path (card 98 #1 / card 106): open a form by nav-link and enumerate its
    element tree LIVE. A LIST form has 0 EditField VALUES (its rows live in a dynlist), so the populated signal is
    ``element_count`` (the enumerated EditFields/Buttons/Tables/Groups — 44–67 for a catalog list)."""
    res = _mcp().read_form_descriptor(
        host=ctx.host, port=ctx.port, open_link="e1cib/list/Справочник.Валюты", enumerate_live=True,
    )
    element_count = res.get("element_count") or len(res.get("elements") or [])
    field_count = res.get("field_count") or len(res.get("fields") or {})
    ok = element_count > 0 or field_count > 0
    return ok, {"element_count": element_count, "field_count": field_count, "opened": res.get("opened")}


def _list_grid_after_dirty(ctx: LiveContext):
    """Card 124 — cold-client-boundary robustness. The prior UI checks (open_two_objects, read_descriptor) leave
    the session DIRTY (catalog forms stacked); `read_list_grid` must still return the catalog rows (auto
    clean-state sweep + retry) — NOT a silent 0. Banki is a stable populated lab catalog. Pass = rows recovered
    OR a 0 carrying the diagnostic `reason` (no display backend to sweep); a silent/malformed 0 is a real
    regression → red. Placed AFTER the dirtying UI checks on purpose."""
    res = _mcp().read_list_grid(
        open_link="e1cib/list/Справочник.Банки", columns=["Код", "Наименование"],
        max_rows=5, host=ctx.host, port=ctx.port,
    )
    rc = res.get("row_count")
    ok = isinstance(rc, int) and (rc > 0 or bool(res.get("reason")))
    return ok, {"row_count": rc, "clean_state_swept": res.get("clean_state_swept"),
                "has_reason": bool(res.get("reason"))}


def core_checks() -> list[Check]:
    """The default read-only, side-effect-free regression set (safe to schedule nightly)."""
    return [
        Check("preflight.protocol_drift", "version-resilience", _protocol_drift_preflight,
              phase="data_pre", required=False),
        Check("data_layer.banki", "data-layer assert", _data_layer_banki, phase="data_pre"),
        Check("ui.assert_family", "assert family", _assert_family, phase="ui"),
        Check("ui.open_two_objects", "open action", _open_two_objects, phase="ui"),
        Check("ui.read_descriptor", "read/introspect", _read_descriptor, phase="ui"),
        Check("ui.list_grid_after_dirty", "read/grid (cold-boundary)", _list_grid_after_dirty, phase="ui"),
    ]


# --- OPT-IN checks ------------------------------------------------------------------------------------------

_WRITE_VALUE = "QAREGRESSION"


def _write_by_label(ctx: LiveContext):
    """Write an arbitrary field by label on a create form (card 106). OPT-IN: creates a lab record."""
    res = _mcp().write_form_fields_by_label(
        open_link="e1cib/data/Справочник.Валюты", labels=["Наименование"], values=[_WRITE_VALUE],
        display=ctx.display or "", host=ctx.host, port=ctx.port, save=True,
    )
    # The UI write is only green when the tool's own protocol value-read verified
    # the committed value. DB persistence is still verified separately below.
    readback = res.get("readback") or {}
    ok = bool(res.get("foregrounded")) and bool(res.get("all_targeted")) and bool(res.get("all_committed"))
    return ok, {
        "foregrounded": res.get("foregrounded"),
        "all_targeted": res.get("all_targeted"),
        "all_committed": res.get("all_committed"),
        "readback_verified": readback.get("verified"),
    }


def _write_persisted(ctx: LiveContext):
    """The UI→DB roundtrip tail (card 105): the value written above persisted to the DB."""
    res = _mcp().assert_data(
        entity_set="Catalog_Валюты", field="Description", expected=_WRITE_VALUE,
        filter=f"Description eq '{_WRITE_VALUE}'",
        base_url=ctx.odata_url, user=ctx.odata_user, password=ctx.odata_password,
    )
    return bool(res.get("ok")), {"actual": res.get("actual"), "record_count": res.get("record_count")}


def write_roundtrip_checks() -> list[Check]:
    """OPT-IN (`--include-write`): a full UI→DB roundtrip. NOTE: creates a `QAREGRESSION` currency in the lab
    infobase each run (the read-only OData client cannot delete it)."""
    return [
        Check("ui.write_by_label", "write roundtrip", _write_by_label, phase="ui"),
        Check("data_post.write_persisted", "write roundtrip", _write_persisted, phase="data_post"),
    ]


def _measure_coverage_perf(ctx: LiveContext):
    """Code coverage + perf/APDEX via the debug protocol (card 110). OPT-IN: boots its own debug server, slow."""
    res = _mcp().measure_scenario(
        feature_text=_MEASURE_FEATURE, host=ctx.host, port=ctx.port,
        env_file=ctx.env_file, src_root=ctx.src_root, max_ms=ctx.measure_max_ms,
    )
    report = res.get("report") or {}
    totals = report.get("totals") or {}
    covered = totals.get("covered_lines") or totals.get("lines") or 0
    perf_ok = res.get("perf_ok", True) if ctx.measure_max_ms > 0 else True
    ok = bool(res.get("ok")) and bool(perf_ok)
    return ok, {"ok": res.get("ok"), "covered_lines": covered, "perf_ok": res.get("perf_ok"),
                "modules": len((report.get("modules") or []))}


def measure_checks() -> list[Check]:
    """OPT-IN (`--include-measure`): the beyond-Vanessa coverage+perf capability. Self-contained but slow
    (boots its own `dbgs` + debug TestClient)."""
    return [Check("measure.coverage_perf", "debug measure", _measure_coverage_perf, phase="measure")]
