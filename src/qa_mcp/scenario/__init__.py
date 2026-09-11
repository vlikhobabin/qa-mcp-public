"""Native scenario runner — execute test scenarios through the in-repo Python TestManager.

Card 74. Orchestrates an ordered list of steps against a `TestClientSession` (synthesized,
capture-free bootstrap) with NO Vanessa Automation manager in the loop. Phase 1 covers
read-only steps + assertions; later phases add single-session multi-op, action steps, a Gherkin
bridge, and a native MCP surface.
"""

from __future__ import annotations

from .actions import ACTION_REGISTRY, render_action
from .gherkin import (
    TranspileResult, filter_by_tags, parse_feature, search_steps, step_library, transpile_feature,
    transpile_scenario,
)
from .model import Scenario, ScenarioResult, Step, StepResult
from .reporting import junit_xml, write_allure_results
from .runner import ScenarioRunner, normalize_form_date, run_write_scenario
from .smoke import (
    generate_smoke_feature, generate_smoke_scenarios, open_link_for, smoke_coverage,
)
from .autofill import (
    RequiredField, build_autofill_plan, create_fill_feature, enum_values_from_mdo, reference_entity_set,
    required_fields_from_mdo, resolve_enum_value, resolve_reference_value, smoke_value_for_type,
)

__all__ = [
    "Scenario",
    "Step",
    "StepResult",
    "ScenarioResult",
    "ScenarioRunner",
    "normalize_form_date",
    "run_write_scenario",
    "ACTION_REGISTRY",
    "render_action",
    "TranspileResult",
    "parse_feature",
    "transpile_scenario",
    "transpile_feature",
    "filter_by_tags",
    "step_library",
    "search_steps",
    "junit_xml",
    "write_allure_results",
    "generate_smoke_feature",
    "generate_smoke_scenarios",
    "open_link_for",
    "smoke_coverage",
    "RequiredField",
    "required_fields_from_mdo",
    "smoke_value_for_type",
    "build_autofill_plan",
    "create_fill_feature",
    "reference_entity_set",
    "resolve_reference_value",
    "enum_values_from_mdo",
    "resolve_enum_value",
]
