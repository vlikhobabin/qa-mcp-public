"""ScenarioRunner — execute a Scenario through the Python TestManager (card 74, Phase 1).

Phase 1 executes read-only steps. Each step opens a session via the injected `session_factory`
(so the runner is unit-testable with a fake), runs the mapped read operation with the synthesized
bootstrap (capture-free), serializes the result to a preview string, and evaluates the optional
`expect_contains` assertion. Phase 2 will bootstrap once and chain operations in a single session.

Card 103 Wave 3 wires the broadened BDD vocabulary into the executor:
- assertion family over a single cached live read (no double-advance under the linear-template
  cursor constraint): assert_form_open / assert_window_open / wait_window (active-window read),
  assert_element_present / assert_table_rows (form-summary read);
- strict-equality assert (`expect_equals`, «стал равен») on a value read;
- data-layer assert (`assert_data`) via the read-only OData client — session-independent, so it runs
  in either path without a TestClient boot;
- recognized-and-skipped steps (`skip_step`) — no-op, honestly reported;
- nested scenarios (`run_subscenario`) — the callee's steps run on the SAME bootstrapped handle.
The remaining new ACTION kinds (open_main_form / close_window / close_all_windows / connect_client)
route to the injected `action_resolver` exactly as the original action steps do; synthesizing their
live command frames + the on-lab live-verify is the LAB-gated remainder of Wave 3.
"""

from __future__ import annotations

from datetime import datetime
import json
import re
import time
from pathlib import Path
from typing import Any, Callable, Protocol

from ..core import (
    ApplicationContext,
    OperationKind,
    OperationRequest,
    OperationVerdict,
    execute_scenario_operation,
)
from ..core.operations import _uses_positive_boundary
from .model import Scenario, ScenarioResult, Step, StepResult


class SessionLike(Protocol):
    def __enter__(self) -> "SessionLike": ...
    def __exit__(self, *exc: object) -> None: ...
    def get_active_window_context(self, *, bootstrap: Any, templates: Any, output_dir: Path, synthesized: Any) -> Any: ...
    def get_form_summary(self, *, bootstrap: Any, templates: Any, output_dir: Path, synthesized: Any) -> Any: ...
    def get_form_element_details(self, *, bootstrap: Any, templates: Any, output_dir: Path, frame_mode: str) -> Any: ...


def _preview(context: Any) -> str:
    """Uniform result preview for assertion matching."""
    to_result = getattr(context, "to_result", None)
    data = to_result() if callable(to_result) else context
    return json.dumps(data, ensure_ascii=False, default=str)


# Card 103 Wave 3 — assertion kinds grouped by the single live read they evaluate against. Each group
# reads ONE context per session (cached) so several asserts on one form never re-advance the linear cursor.
_WINDOW_ASSERT_KINDS = frozenset({"assert_form_open", "assert_window_open", "wait_window"})
_FORM_ASSERT_KINDS = frozenset({"assert_element_present", "assert_table_rows"})
# Card 103 Wave 3 (live leg) — navigation/open kinds that open a form by NAV-LINK on the live session. These
# do NOT replay a single captured command frame (the action_resolver path); a live open is the multi-frame
# `splice_navigate` cold sequence against the LIVE desktop MainFrame (config-agnostic, fixture-free; proven on
# 8/8 forms via read_form_descriptor). They route to the injected `navigate_resolver` instead.
_NAVIGATE_OPEN_KINDS = frozenset({"open_main_form", "open_list", "open_create_form"})
_WRITE_COMMAND_KINDS = frozenset({"click_button", "form_command"})
_DATE_RE = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")


def normalize_form_date(value: str) -> str:
    """Validate a form-level date field value as DD.MM.YYYY."""
    text = str(value).strip()
    if not _DATE_RE.match(text):
        raise ValueError(f"date must be DD.MM.YYYY, got {value!r}")
    try:
        return datetime.strptime(text, "%d.%m.%Y").strftime("%d.%m.%Y")
    except ValueError as exc:
        raise ValueError(f"invalid date {value!r}") from exc


def date_prefix_committed(readback: Any, requested: str) -> bool:
    """Date read-backs may append a time component; accept an exact date prefix."""
    return str(readback or "").startswith(requested)


def _table_rows_present(table: Any, preview: str) -> tuple[bool, str]:
    """assert_table_rows check: every non-empty data cell of the attached DataTable must appear in the
    form-summary preview. Row 0 is the header (column names); rows 1.. are data. A table with no data rows
    (phrasing-only, table optional) asserts nothing → passes."""
    if not isinstance(table, list) or len(table) < 2:
        return (True, "no data rows to assert")
    missing: list[str] = []
    for row in table[1:]:
        for cell in row if isinstance(row, list) else []:
            value = str(cell).strip()
            if value and value not in preview:
                missing.append(value)
    return (not missing, "all row cells present" if not missing else f"missing cells: {missing}")


class ScenarioRunner:
    def __init__(
        self,
        session_factory: Callable[[], SessionLike],
        bootstrap: Any,
        templates: Any,
        output_dir: Path,
        synthesized: Any = None,
        action_resolver: Callable[[Step, Any], tuple[bytes, Any]] | None = None,
        odata_client: Any = None,
        scenario_registry: "dict[str, Scenario] | None" = None,
        navigate_resolver: "Callable[[Step, Any], dict[str, Any]] | None" = None,
        operation_context: ApplicationContext | None = None,
    ) -> None:
        self.session_factory = session_factory
        self.bootstrap = bootstrap
        self.templates = templates
        self.output_dir = Path(output_dir)
        self.synthesized = synthesized
        # Card 103 Wave 3: a read-only OData client for `assert_data` steps (None → constructed lazily from
        # env on first use) and a name→Scenario registry for `run_subscenario` nested calls (None → unknown).
        self._odata_client = odata_client
        self.scenario_registry = scenario_registry
        # Card 103 Wave 3 (live leg): open a form by nav-link on the live bootstrapped handle for
        # open_main_form / open_list steps. Called as `navigate_resolver(step, handle)` → a result dict
        # ({"opened": bool, "nav_link", "caption"/"secondary_frame"/"managed_form"}). Injected so the runner
        # stays decoupled from the splice mechanics in mcp_server. None → open steps fall through to the
        # action_resolver path (offline single-frame replay), preserving prior behavior.
        self.navigate_resolver = navigate_resolver
        self.operation_context = operation_context
        # Card 78 Phase B: resolve an action step to (captured command frame, rebinder) so the
        # single-session handle can execute it via run_action. Called as `action_resolver(step, handle)`
        # so it can read the LIVE session identifiers (handle.state.managed_form_guid / ack_guid, known
        # only after bootstrap) to build the captured->live rebinder. Injected for testability + to keep
        # the runner decoupled from the capture corpus. None → action steps unsupported (as before).
        self.action_resolver = action_resolver

    def _execute_read(self, session: SessionLike, step: Step, step_dir: Path) -> Any:
        operation_context = self.operation_context
        if operation_context is not None:
            integrated = _uses_positive_boundary(operation_context, step.kind)
            common = {
                "session": session,
                "bootstrap": self.bootstrap,
                "templates": self.templates,
                "output_dir": step_dir,
            }
            if step.kind == "read_active_window":
                common["synthesized"] = self.synthesized
                if step.expect_contains is not None:
                    # Request-local carrier consumed by the trusted bound
                    # operation seam; it is never sent to the native session
                    # and is not serialized in the public result.
                    common["_expected_window"] = step.expect_contains
            elif step.kind == "read_form_summary":
                common["synthesized"] = self.synthesized
            elif step.kind == "read_element":
                common["frame_mode"] = step.frame_mode
            else:
                raise ValueError(f"Unsupported step kind: {step.kind!r}")
            result = execute_scenario_operation(
                operation_context,
                OperationRequest(OperationKind.READ, step.kind, common),
            )
            if result.verdict is OperationVerdict.SUCCESS:
                return result.to_dict() if integrated else result.value
            message = result.error.message if result.error is not None else result.verdict.value
            if not integrated:
                raise RuntimeError(f"{result.verdict.value}: {message}")
            payload = json.dumps(result.to_dict(), ensure_ascii=False, sort_keys=True)
            raise RuntimeError(f"{result.verdict.value}: {message}; operation_result={payload}")
        if step.kind == "read_active_window":
            return session.get_active_window_context(
                bootstrap=self.bootstrap, templates=self.templates, output_dir=step_dir, synthesized=self.synthesized
            )
        if step.kind == "read_form_summary":
            return session.get_form_summary(
                bootstrap=self.bootstrap, templates=self.templates, output_dir=step_dir, synthesized=self.synthesized
            )
        if step.kind == "read_element":
            return session.get_form_element_details(
                bootstrap=self.bootstrap, templates=self.templates, output_dir=step_dir, frame_mode=step.frame_mode
            )
        raise ValueError(f"Unsupported step kind: {step.kind!r}")

    # --- Card 103 Wave 3: session-independent steps (run in either path, no TestClient needed) ---

    def _run_sessionless_step(self, step: Step) -> StepResult | None:
        """Execute a step that needs no TestClient session. Returns a StepResult for `skip_step` /
        `assert_data`, or None for any step that does need a (handle) session."""
        if step.kind == "skip_step":
            reason = step.params.get("reason") or "recognized; no qa-mcp equivalent"
            return StepResult(name=step.name, kind=step.kind, status="ok",
                              preview=f"[skipped] {reason}", assertion=None)
        if step.kind == "connect_client":
            # Card 103 Wave 3: qa-mcp OWNS the TestClient connection — the runner's session_factory already
            # connects/bootstraps. A «я подключаю … TestClient» step is a recognized lifecycle marker, not a
            # protocol command, so it is a no-op here (intercepted before the action_resolver registry lookup).
            target = step.marker or step.params.get("profile") or "runner session"
            return StepResult(name=step.name, kind=step.kind, status="ok",
                              preview=f"[connect] TestClient connection owned by the runner ({target})",
                              assertion=None)
        if step.kind == "assert_data":
            try:
                result = self._run_assert_data(step)
            except Exception as exc:  # noqa: BLE001 — config/HTTP failures are reported, not raised
                return StepResult(name=step.name, kind=step.kind, status="error",
                                  error=f"{type(exc).__name__}: {exc}")
            preview = json.dumps(result, ensure_ascii=False, default=str)
            ok = bool(result.get("ok"))
            return StepResult(name=step.name, kind=step.kind, status="ok" if ok else "assert_failed",
                              preview=preview[:500], assertion=ok)
        if step.kind == "assert_data_count":
            try:
                result = self._run_assert_data_count(step)
            except Exception as exc:  # noqa: BLE001 — config/HTTP failures are reported, not raised
                return StepResult(name=step.name, kind=step.kind, status="error",
                                  error=f"{type(exc).__name__}: {exc}")
            ok = bool(result.get("ok"))
            return StepResult(name=step.name, kind=step.kind, status="ok" if ok else "assert_failed",
                              preview=json.dumps(result, ensure_ascii=False, default=str)[:500], assertion=ok)
        return None

    def _run_assert_data(self, step: Step) -> dict[str, Any]:
        """Read a value from the data layer (read-only OData) and assert it — beyond Vanessa (UI-only).
        The OData client is injectable for offline tests; absent, it is built from env on first use."""
        from ..data import ODataClient, assert_data_value

        if self._odata_client is None:
            self._odata_client = ODataClient()
        p = step.params
        return assert_data_value(
            self._odata_client, p["entity_set"], p["field"], p["expected"],
            key=(p.get("key") or None), filter=(p.get("filter") or None),
            match=p.get("match", "equals"),
        )

    def _run_assert_data_count(self, step: Step) -> dict[str, Any]:
        """Card 111 item 7 — assert the COUNT of records matching a filter in the data layer (read-only OData)."""
        from ..data import ODataClient, assert_data_count_value

        if self._odata_client is None:
            self._odata_client = ODataClient()
        p = step.params
        return assert_data_count_value(
            self._odata_client, p["entity_set"], int(p["expected"]),
            op=p.get("op", "eq"), filter=(p.get("filter") or None),
        )

    # --- Card 103 Wave 3: single-read cached asserts + nested scenarios (single-session path) ---

    def _cached_active_window(self, handle: Any, cache: dict[str, Any]) -> Any:
        if "active_window" not in cache:
            cache["active_window"] = handle.active_window()
        return cache["active_window"]

    def _cached_form_summary(self, handle: Any, cache: dict[str, Any]) -> Any:
        if "form_summary" not in cache:
            cache["form_summary"] = handle.form_summary()
        return cache["form_summary"]

    def _assert_against(self, context: Any, step: Step) -> StepResult:
        """Evaluate a presence/table assertion against an already-read live context."""
        preview = _preview(context)
        if step.kind == "assert_table_rows":
            ok, detail = _table_rows_present(step.params.get("table"), preview)
            return StepResult(name=step.name, kind=step.kind, status="ok" if ok else "assert_failed",
                              preview=f"{detail} | {preview}"[:500], assertion=ok)
        target = step.marker or ""
        ok = bool(target) and target in preview
        return StepResult(name=step.name, kind=step.kind, status="ok" if ok else "assert_failed",
                          preview=preview, assertion=ok)

    def _run_subscenario(self, handle: Any, step: Step, *, cache: dict[str, Any],
                         call_stack: tuple[str, ...]) -> StepResult:
        """Run a nested scenario (the «я выполняю сценарий 'X'» idiom) on THIS bootstrapped handle, so the
        callee continues the same live session. Guards against recursive cycles."""
        name = step.marker or ""
        if name in call_stack:
            return StepResult(name=step.name, kind=step.kind, status="error",
                              error=f"recursive subscenario call: {name!r}")
        callee = (self.scenario_registry or {}).get(name)
        if callee is None:
            return StepResult(name=step.name, kind=step.kind, status="error",
                              error=f"unknown subscenario {name!r} (not in scenario_registry)")
        sub_stack = call_stack + (name,)
        sub_results: list[StepResult] = []
        for sub in callee.steps:
            sr = self._run_sessionless_step(sub)
            if sr is None:
                sr = self._run_step_on_handle(handle, sub, cache=cache, call_stack=sub_stack)
            sub_results.append(sr)
        ok = bool(sub_results) and all(r.status == "ok" for r in sub_results)
        failed = [r.name for r in sub_results if r.status != "ok"]
        preview = (f"subscenario {name!r}: {len(sub_results)} steps, "
                   + ("all ok" if ok else f"failed {failed}"))
        return StepResult(name=step.name, kind=step.kind, status="ok" if ok else "assert_failed",
                          preview=preview, assertion=ok)

    def _run_step(self, step: Step, index: int) -> StepResult:
        step_dir = self.output_dir / f"step_{index:02d}_{step.kind}"
        bound_window = (step.kind == "read_active_window"
                        and self.operation_context is not None
                        and _uses_positive_boundary(self.operation_context, step.kind))
        try:
            with self.session_factory() as session:
                context = self._execute_read(session, step, step_dir)
            preview = _preview(context)
        except Exception as exc:  # noqa: BLE001 — report any step failure, don't abort the scenario
            return StepResult(name=step.name, kind=step.kind, status="error", error=f"{type(exc).__name__}: {exc}")

        if step.expect_contains is not None:
            # Bound active-window reads publish only assertion_passed.  Do not
            # search the sanitized preview for the caller's private expected
            # text (which would both leak it and make true matches impossible).
            if bound_window:
                ok = (type(context) is dict and type(context.get("value")) is dict
                      and context["value"].get("assertion_passed") is True)
            else:
                ok = step.expect_contains in preview
            return StepResult(
                name=step.name,
                kind=step.kind,
                status="ok" if ok else "assert_failed",
                preview=preview,
                assertion=ok,
            )
        return StepResult(name=step.name, kind=step.kind, status="ok", preview=preview)

    def _eval_step_perf(self, step: Step, results: list[StepResult]) -> StepResult:
        """assert_step_perf (card 111 item 6): every PRIOR step in this scenario stayed within the budget
        (`params['max_ms']`). Evaluated over the already-recorded per-step durations, so place it LAST in a
        scenario. Session-independent — it reads the accumulated results, not the client."""
        from ..debug.gates import evaluate_perf_budget
        max_ms = float((step.params or {}).get("max_ms") or 0.0)
        verdict = evaluate_perf_budget(
            [{"name": r.name, "kind": r.kind, "duration_sec": r.duration_sec} for r in results], max_ms)
        if verdict["ok"]:
            preview = f"OK — {verdict['checked']} step(s) within {max_ms:.0f}ms"
        else:
            preview = "OVER BUDGET: " + "; ".join(
                f"{v['name']} {v['ms']:.0f}ms > {max_ms:.0f}ms" for v in verdict["violations"])
        return StepResult(name=step.name, kind=step.kind,
                          status="ok" if verdict["ok"] else "assert_failed",
                          preview=preview, assertion=verdict["ok"])

    def run(self, scenario: Scenario) -> ScenarioResult:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        results: list[StepResult] = []
        started_at = time.time()
        t0 = time.perf_counter()
        for index, step in enumerate(scenario.steps, start=1):
            s0 = time.perf_counter()
            if step.kind == "assert_step_perf":
                sr = self._eval_step_perf(step, results)
            else:
                sr = self._run_sessionless_step(step)
                if sr is None:
                    sr = self._run_step(step, index)
            sr.duration_sec = round(time.perf_counter() - s0, 6)
            results.append(sr)
        status = "passed" if all(r.status == "ok" for r in results) else "failed"
        return ScenarioResult(name=scenario.name, status=status, steps=results,
                              started_at=started_at, duration_sec=round(time.perf_counter() - t0, 6))

    # --- Phase 2: single-session mode (bootstrap once, run each step as an op on one socket) ---

    def _run_step_on_handle(self, handle: Any, step: Step, *, cache: dict[str, Any] | None = None,
                            call_stack: tuple[str, ...] = ()) -> StepResult:
        cache = cache if cache is not None else {}
        # Card 103 Wave 3: a nested scenario runs its callee's steps on THIS handle (own result + assertion).
        if step.kind == "run_subscenario":
            return self._run_subscenario(handle, step, cache=cache, call_stack=call_stack)
        try:
            if step.kind == "read_active_window":
                # Route through the cache so a later window assert reuses THIS read (the linear cursor
                # cannot re-advance to the active-window frame — a re-read would raise; card 103 Wave 3).
                context = self._cached_active_window(handle, cache)
            elif step.kind == "read_form_summary":
                context = self._cached_form_summary(handle, cache)
            elif step.kind == "read_form_value":
                # Card 79 (Fork 1): open the fixture form (if needed) + read the field's LIVE value
                # so an assertion can verify the EFFECT, not just acceptance.
                context = handle.read_form_value(field=step.marker or "PF_EDIT_STRING")
            # Card 103 Wave 3: assertion family — evaluate against ONE cached live read per context type so
            # several asserts on a form never re-advance the order-dependent linear cursor.
            elif step.kind in _WINDOW_ASSERT_KINDS:
                return self._assert_against(self._cached_active_window(handle, cache), step)
            elif step.kind in _FORM_ASSERT_KINDS:
                return self._assert_against(self._cached_form_summary(handle, cache), step)
            elif step.kind in _NAVIGATE_OPEN_KINDS and self.navigate_resolver is not None:
                # Card 103 Wave 3 (live leg): EXECUTE an open on the live client by nav-link (splice_navigate),
                # not a captured-frame replay. The resolver opens the target form and resolves its window
                # identifiers; the step passes when the form actually opened — an observable client-state change.
                result = self.navigate_resolver(step, handle)
                opened = bool(result.get("opened"))
                preview = json.dumps(result, ensure_ascii=False, default=str)
                if not opened:
                    return StepResult(
                        name=step.name, kind=step.kind, status="error", preview=preview[:500],
                        error=f"form did not open for nav-link {result.get('nav_link')!r}",
                    )
                if step.expect_contains is not None:
                    ok = step.expect_contains in preview
                    return StepResult(name=step.name, kind=step.kind, status="ok" if ok else "assert_failed",
                                      preview=preview[:500], assertion=ok)
                return StepResult(name=step.name, kind=step.kind, status="ok", preview=preview[:500],
                                  assertion=True)
            elif step.is_action:
                # Card 78 Phase B: execute an action step on the open synthesized session.
                if self.action_resolver is None:
                    raise ValueError(f"action step {step.kind!r} needs an action_resolver in single-session mode")
                command_payload, rebinder = self.action_resolver(step, handle)
                context = handle.run_action(command_payload, query_id=step.name, rebinder=rebinder)
                if isinstance(context, dict) and context.get("accepted") is False:
                    return StepResult(
                        name=step.name, kind=step.kind, status="error",
                        error=f"action rejected by client (no response): {context}",
                    )
            else:
                raise ValueError(f"step kind {step.kind!r} is not supported in single-session mode (Phase 2)")
            preview = _preview(context)
        except Exception as exc:  # noqa: BLE001
            return StepResult(name=step.name, kind=step.kind, status="error", error=f"{type(exc).__name__}: {exc}")

        # Card 103: strict-equality assert («стал равен») on a value read — compare the field's parsed value.
        if step.expect_equals is not None:
            actual = getattr(context, "value", None)
            actual_s = "" if actual is None else str(actual)
            ok = actual_s == step.expect_equals
            return StepResult(name=step.name, kind=step.kind, status="ok" if ok else "assert_failed",
                              preview=preview, assertion=ok)
        if step.expect_contains is not None:
            ok = step.expect_contains in preview
            return StepResult(
                name=step.name, kind=step.kind, status="ok" if ok else "assert_failed", preview=preview, assertion=ok
            )
        return StepResult(name=step.name, kind=step.kind, status="ok", preview=preview)

    def run_single_session(self, scenario: Scenario) -> ScenarioResult:
        """Bootstrap ONCE, then run every step as an operation segment on the same socket
        (no re-bootstrap). Steps must be in increasing-frame order (linear-template constraint)."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        results: list[StepResult] = []
        started_at = time.time()
        t0 = time.perf_counter()
        cache: dict[str, Any] = {}  # card 103 Wave 3 — per-session read cache (linear-cursor safe asserts)
        try:
            with self.session_factory() as session:
                handle = session.open_and_bootstrap(
                    bootstrap=self.bootstrap,
                    templates=self.templates,
                    output_dir=self.output_dir,
                    synthesized=self.synthesized,
                )
                for step in scenario.steps:
                    s0 = time.perf_counter()
                    if step.kind == "assert_step_perf":
                        sr = self._eval_step_perf(step, results)
                    else:
                        sr = self._run_sessionless_step(step)
                        if sr is None:
                            sr = self._run_step_on_handle(handle, step, cache=cache)
                    sr.duration_sec = round(time.perf_counter() - s0, 6)
                    results.append(sr)
        except Exception as exc:  # noqa: BLE001 — bootstrap/connection failure fails the scenario
            results.append(StepResult(name="bootstrap", kind="bootstrap", status="error", error=f"{type(exc).__name__}: {exc}"))
        status = "passed" if results and all(r.status == "ok" for r in results) else "failed"
        return ScenarioResult(name=scenario.name, status=status, steps=results,
                              started_at=started_at, duration_sec=round(time.perf_counter() - t0, 6))


def run_write_scenario(
    scenario: Scenario,
    *,
    host: str = "127.0.0.1",
    port: int = 15381,
    capture: str = "commit-conn",
    base_field: str = "PF_EDIT_STRING",
    captured_value: str = "QAGENUINE2026",
    default_value: str = "PF_EDIT_STRING_VALUE",
    command_executor: Callable[[Step, Any], dict[str, Any]] | None = None,
    persistence_verifier: Callable[[Scenario, list[StepResult]], dict[str, Any]] | None = None,
) -> ScenarioResult:
    """Card 83 step 2 + card 86b: execute a WRITE scenario — route each ``input_text`` step through the
    commit-capable native write path (`NativeWriteSession`), so the value actually COMMITS, verified by
    read-back. One session is opened once (fixes multi-write) on the ``base_field`` capture template; each
    step writes to its own ``step.marker`` field via capture-free element addressing (86b) — so the steps may
    target DIFFERENT fields with no per-field capture. Command steps are accepted only when an explicit
    ``command_executor`` or session command method is available; otherwise they fail closed."""
    from ..protocol.bootstrap import resolve_capture_dir
    from ..protocol.native_write import NativeWriteSession, derive_write_template

    template = derive_write_template(resolve_capture_dir(capture), base_field, captured_value, default_value)
    results: list[StepResult] = []
    with NativeWriteSession(template, host=host, port=port) as session:
        for step in scenario.steps:
            if step.kind == "switch_page":  # card 86d: navigate to a tab page on the same session
                target = step.marker or ""
                outcome = session.switch_page(target)
                ok = bool(outcome.get("accepted"))
                results.append(StepResult(
                    name=step.name, kind=step.kind, status="ok" if ok else "error",
                    preview=f"switch_page -> {target} accepted={ok}",
                    error=None if ok else "page switch not accepted"))
                continue
            if step.kind in _WRITE_COMMAND_KINDS:
                target = step.marker or step.params.get("button") or ""
                try:
                    if command_executor is not None:
                        outcome = command_executor(step, session)
                    elif hasattr(session, "click_command"):
                        outcome = session.click_command(target)
                    else:
                        raise ValueError("command steps need command_executor in write mode")
                except Exception as exc:  # noqa: BLE001
                    results.append(StepResult(
                        name=step.name, kind=step.kind, status="error",
                        error=f"{type(exc).__name__}: {exc}"))
                    continue
                ok = bool(outcome.get("accepted") or outcome.get("committed") or outcome.get("ok"))
                results.append(StepResult(
                    name=step.name,
                    kind=step.kind,
                    status="ok" if ok else "error",
                    preview=json.dumps(outcome, ensure_ascii=False, default=str)[:500],
                    assertion=ok,
                    error=None if ok else f"command {target!r} was not accepted",
                ))
                continue
            if step.kind != "input_text":
                results.append(StepResult(
                    name=step.name, kind=step.kind, status="error",
                    error=f"{step.kind!r} not supported in write mode (reads need run_single_session)"))
                continue
            value = step.params.get("new_value") or step.params.get("value") or ""
            target = step.marker or base_field
            surface = "form_field"
            if step.params.get("value_type") == "date":
                try:
                    value = normalize_form_date(value)
                except ValueError as exc:
                    results.append(StepResult(name=step.name, kind=step.kind, status="error", error=str(exc)))
                    continue
                surface = "form_field_date"
            outcome = session.write(value, field=target)
            committed = (
                date_prefix_committed(outcome.get("readback_value"), value)
                if surface == "form_field_date" else bool(outcome.get("committed"))
            )
            preview = f"{target}={outcome.get('readback_value')!r} committed={committed}"
            if surface == "form_field_date":
                preview = f"{preview} surface=form_field_date"
            if step.expect_contains is not None:
                ok = step.expect_contains in preview
                results.append(StepResult(
                    name=step.name, kind=step.kind, status="ok" if ok else "assert_failed",
                    preview=preview, assertion=ok))
            else:
                results.append(StepResult(
                    name=step.name, kind=step.kind, status="ok" if committed else "error",
                    preview=preview, error=None if committed else "value did not commit"))
        if persistence_verifier is not None:
            try:
                verification = persistence_verifier(scenario, results)
                ok = bool(verification.get("ok"))
                results.append(StepResult(
                    name="persistence verification",
                    kind="assert_data",
                    status="ok" if ok else "assert_failed",
                    preview=json.dumps(verification, ensure_ascii=False, default=str)[:500],
                    assertion=ok,
                ))
            except Exception as exc:  # noqa: BLE001
                results.append(StepResult(
                    name="persistence verification", kind="assert_data", status="error",
                    error=f"{type(exc).__name__}: {exc}"))
    status = "passed" if results and all(r.status == "ok" for r in results) else "failed"
    return ScenarioResult(name=scenario.name, status=status, steps=results)
