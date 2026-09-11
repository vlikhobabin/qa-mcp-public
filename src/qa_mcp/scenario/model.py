"""Scenario / Step data model for the native runner (card 74)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Phase-1 step kinds map to already-live-capable read operations on TestClientSession.
# Card 103 (E-FW) added the assertion/read family measured against the real Vanessa corpus:
# assert_form_open / assert_window_open / assert_element_present / wait_window.
READ_STEP_KINDS = frozenset(
    {
        "read_active_window", "read_form_summary", "read_element", "read_form_value",
        "assert_form_open", "assert_window_open", "assert_element_present", "wait_window",
        "assert_table_rows",  # card 103 Wave 2 — «таблица 'T' содержит строки:» + DataTable
        "assert_data",        # card 105 (E-XV) — assert a value in the DATA LAYER via OData (beyond Vanessa)
        "assert_step_perf",   # card 111 item 6 — «каждый шаг выполняется быстрее N мс» (per-step perf budget)
        "assert_data_count",  # card 111 item 7 — «в базе 'X' где "f" количество записей равно N» (count assert)
    }
)
# Phase-3 action step kinds map to the parametric command synthesizers (qa_mcp.protocol.navigation);
# their executors live in qa_mcp.scenario.actions. Action execution re-targets a captured command
# template (the write-from-capture constraint), so each carries `params` for the synthesizer.
# Card 103 (E-FW) added navigation breadth: open_main_form / close_window / close_all_windows / connect_client.
ACTION_STEP_KINDS = frozenset(
    {
        "open_list", "form_command", "select_row", "open_card", "click_button", "input_text", "switch_page",
        "open_main_form", "close_window", "close_all_windows", "connect_client",
        "open_create_form",  # card 106 change 4 — open a NEW-object create form (e1cib/data/<Type>.<Name>, no ?ref)
        "open_external_epf",  # card 109 — open an EXTERNAL .epf/.erf via native Файл→Открыть (xtest; tool-executed)
        "run_subscenario",  # card 103 Wave 2 — nested scenario call («я выполняю сценарий 'X'»)
    }
)
# Card 103 (E-FW) — steps qa-mcp RECOGNIZES but intentionally no-ops (Vanessa-runtime concepts with no
# qa-mcp equivalent). Recognized-and-skipped is honest: NOT silently dropped (it transpiles), NOT pretended
# to execute. `params["reason"]` records why.
SKIP_STEP_KINDS = frozenset({"skip_step"})
STEP_KINDS = READ_STEP_KINDS | ACTION_STEP_KINDS | SKIP_STEP_KINDS


@dataclass(frozen=True)
class Step:
    """One scenario step. `kind` selects the manager operation; `params` carries action args for
    action kinds; `expect_contains` (optional) asserts the step's result preview contains a
    substring."""

    kind: str
    name: str
    marker: str | None = None  # target element marker (read_element)
    frame_mode: str = "short"  # read_element frame coverage
    expect_contains: str | None = None
    expect_equals: str | None = None  # card 103: strict-equality assert («стал равен»)
    params: dict[str, Any] = field(default_factory=dict)  # action-step synthesizer args

    def __post_init__(self) -> None:
        if self.kind not in STEP_KINDS:
            raise ValueError(f"Unsupported step kind: {self.kind!r}")
        if self.kind == "read_element" and not self.marker:
            raise ValueError("read_element step requires a 'marker'")

    @property
    def is_action(self) -> bool:
        return self.kind in ACTION_STEP_KINDS


@dataclass(frozen=True)
class Scenario:
    """An ordered, named list of steps. `tags` carries Gherkin @tags (card 103 Wave 2) for filtering."""

    name: str
    steps: list[Step]
    tags: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Scenario":
        steps = [
            Step(
                kind=s["kind"],
                name=s.get("name", s["kind"]),
                marker=s.get("marker"),
                frame_mode=s.get("frame_mode", "short"),
                expect_contains=s.get("expect_contains"),
                expect_equals=s.get("expect_equals"),
                params=s.get("params", {}),
            )
            for s in data["steps"]
        ]
        return cls(name=data["name"], steps=steps, tags=list(data.get("tags", [])))


@dataclass
class StepResult:
    name: str
    kind: str
    status: str  # "ok" | "assert_failed" | "error"
    preview: str = ""
    assertion: bool | None = None  # None = no assertion on this step
    error: str | None = None
    duration_sec: float = 0.0  # card 104 — wall time of this step (for reports)
    attachments: list[str] = field(default_factory=list)  # card 104 — file paths (e.g. screenshots)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind,
            "status": self.status,
            "preview": self.preview[:500],
            "assertion": self.assertion,
            "error": self.error,
            "duration_sec": self.duration_sec,
            "attachments": list(self.attachments),
        }


@dataclass
class ScenarioResult:
    name: str
    status: str  # "passed" | "failed"
    steps: list[StepResult] = field(default_factory=list)
    duration_sec: float = 0.0  # card 104 — total wall time
    started_at: float = 0.0    # card 104 — epoch seconds at scenario start (0 = not timed)

    @property
    def passed(self) -> bool:
        return self.status == "passed"

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario": self.name,
            "status": self.status,
            "duration_sec": self.duration_sec,
            "started_at": self.started_at,
            "steps": [s.to_dict() for s in self.steps],
        }
