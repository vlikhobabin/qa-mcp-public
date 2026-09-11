"""Fail-closed operation routing shared by MCP and scenario public paths."""

from __future__ import annotations

from pathlib import Path
from types import MappingProxyType
from typing import Any

from .application import ApplicationContext
from .boundary import (
    EvidenceLedger, OperationBoundaryError, admit_operation_provenance,
    normalize_operation_result,
)
from .contracts import (
    OperationError,
    OperationKind,
    OperationRequest,
    OperationResult,
    OperationVerdict,
    SessionIdentity,
)
from .runtime_target import validate_runtime_target_resolution

_MISSING = object()
_WINDOW_EXPECTATION_KEY = "_expected_window"

# These names are shared operation entrypoints, not result-schema membership.
# The result boundary intentionally has a much smaller positive catalog.
NATIVE_SESSION_OPERATION_NAMES = frozenset({
    "activate_window", "add_table_row", "advanced_search", "answer_dialog",
    "assert_form_value", "capture_screenshot", "choose_from_list", "choose_from_menu",
    "click_command", "close_window", "copy_table_row", "delete_table_row",
    "get_window_list", "get_window_list_testclient", "measure_scenario", "move_table_row",
    "open_card", "open_external_processor", "open_list", "read_form_descriptor",
    "read_active_window", "read_element", "read_form_summary", "read_list_column",
    "read_list_grid", "read_list_row", "read_record",
    "read_spreadsheet_cell", "read_table_cell", "read_user_messages", "run_report",
    "run_scenario", "run_step", "run_write_scenario_tool", "search_list",
    "select_all_table_rows", "select_table_row", "send_keys", "set_choice",
    "set_list_view", "set_reference_field", "set_table_cell", "set_table_date_cell",
    "switch_page", "toggle_checkbox", "wait_for_form_value", "write_form_date",
    "write_form_fields_by_label", "write_form_value", "write_form_value_xtest",
    "write_form_values",
})

_LIFECYCLE_OPERATION_NAMES = frozenset({"launch_test_client", "attach_test_client", "test_client_status", "stop_test_client"})


def _fixed_request(kind: OperationKind = OperationKind.READ, name: str = "invalid_operation") -> OperationRequest:
    return OperationRequest(kind, name)


def _fixed_result(
    request: OperationRequest,
    provenance: Any,
    *,
    verdict: OperationVerdict,
    code: str,
    message: str,
) -> OperationResult:
    return OperationResult(
        request=request,
        verdict=verdict,
        error=OperationError(code, message),
        provenance=provenance,
    )


def _snapshot_request(request: Any) -> OperationRequest:
    if (
        type(request) is not OperationRequest
        or type(request.kind) is not OperationKind
        or type(request.name) is not str
        or type(request.arguments) is not dict
    ):
        raise ValueError("invalid request")
    return OperationRequest(request.kind, request.name, dict(request.arguments))


def _project_bound_active_window(raw: OperationResult, request: OperationRequest) -> OperationResult:
    """Project a trusted ActiveWindowContext into the finite bound-read DTO.

    This runs after route admission and after exactly one executor call.  The
    native/session handler still returns its normal context; only the bound
    operation path receives this private-to-public projection.  Invalid or
    unsuccessful native observations fail closed instead of becoming an empty
    successful value.
    """
    if type(raw) is not OperationResult or raw.verdict is not OperationVerdict.SUCCESS:
        return raw
    if raw.error is not None:
        raise OperationBoundaryError("invalid-executor-result")
    value = raw.value
    if type(value) is not dict:
        raise OperationBoundaryError("invalid-executor-result")
    if len(value) > 64:
        raise OperationBoundaryError("result-too-large")
    if any(type(key) is not str for key in value):
        raise OperationBoundaryError("invalid-executor-result")
    if type(value.get("status")) is not str:
        raise OperationBoundaryError("invalid-executor-result")
    if value["status"] != "ok":
        return OperationResult(request, OperationVerdict.FAILURE,
                               error=OperationError("executor-failure", "executor operation failed"),
                               artifacts=raw.artifacts, provenance=raw.provenance)
    ref = value.get("active_window_ref")
    markers = value.get("active_window_markers")
    if ref is not None and (type(ref) is not str or len(ref) > 2048):
        raise OperationBoundaryError("invalid-executor-result")
    if type(markers) is not list:
        raise OperationBoundaryError("invalid-executor-result")
    if len(markers) > 64:
        raise OperationBoundaryError("result-too-large")
    if any(type(item) is not str or len(item) > 2048 for item in markers):
        raise OperationBoundaryError("invalid-executor-result")
    if ref is not None and ref:
        state = "observed" if ref in markers else "ambiguous"
    elif ref is None and not markers:
        state = "missing"
    else:
        state = "ambiguous"
    observation: dict[str, Any] = {"window_state": state, "marker_count": len(markers)}
    if _WINDOW_EXPECTATION_KEY in request.arguments:
        expected = request.arguments[_WINDOW_EXPECTATION_KEY]
        if type(expected) is not str or not expected or len(expected) > 2048:
            observation["assertion_passed"] = False
        else:
            observation["assertion_passed"] = (
                state == "observed" and any(expected in marker for marker in markers)
            )
    return OperationResult(request, OperationVerdict.SUCCESS, value=observation,
                           artifacts=raw.artifacts, provenance=raw.provenance)


def _application_boundary(
    context: ApplicationContext,
) -> tuple[Any, MappingProxyType, EvidenceLedger]:
    runtime_target = context.runtime_target
    catalog = context.operation_schemas
    ledger = context.evidence_ledger
    guard = context._operation_boundary_guard
    if (
        type(catalog) is not MappingProxyType
        or type(ledger) is not EvidenceLedger
        or not ledger._valid()
        or type(guard) is not tuple
        or len(guard) != 2
        or guard[0] is not catalog
        or guard[1] is not ledger
    ):
        raise ValueError("invalid application boundary")
    return runtime_target, catalog, ledger


def _uses_positive_boundary(context: Any, operation: Any) -> bool:
    """Classify once before ScenarioRunner execution; malformed state stays closed."""

    try:
        if type(context) is not ApplicationContext or type(operation) is not str:
            return True
        runtime_target, catalog, ledger = _application_boundary(context)
        return operation in catalog and (runtime_target is not None or ledger.root is not None)
    except Exception:
        return True


def is_explicitly_unbound_context(context: Any) -> bool:
    """Recognize only an intact, deliberately unbound application context.

    A malformed formerly bound context must not be mistaken for the legacy
    unbound compatibility path merely because one of its binding fields was
    cleared.  Keep this check total: registered-tool preflight uses it before
    evaluating hidden arguments or provider callbacks.
    """

    try:
        runtime_target, _catalog, ledger = _application_boundary(context)
        return (
            runtime_target is None
            and ledger.root is None
        )
    except Exception:
        return False


def _attachment_values(attachment: Any) -> dict[str, Any]:
    if type(attachment) is dict:
        values = attachment
    else:
        values = vars(attachment)
        if type(values) is not dict:
            raise ValueError("invalid attachment")
    status = values.get("status", {})
    if type(status) is not dict:
        status = {}
    return {
        name: values.get(name, status.get(name, _MISSING))
        for name in ("target", "session", "binding_generation", "host", "port", "display")
    }


def _matches_argument(
    arguments: dict[str, Any], name: str, expected: Any, exact_type: type
) -> bool:
    if name not in arguments:
        return True
    value = arguments[name]
    return type(value) is exact_type and value == expected


def _binding_provenance(
    runtime_target: Any,
    session: Any,
    request: OperationRequest,
) -> tuple[Any, Any]:
    resolution = validate_runtime_target_resolution(runtime_target)
    binding = resolution.binding
    expected = binding.target
    admitted_session = None
    if (
        type(session) is SessionIdentity
        and session.target is expected
        and type(session.sequence) is int
        and 0 <= session.sequence < 2**63
    ):
        admitted_session = session.session_id
    values = {
        "operation": request.name,
        "target": expected.logical_id,
        "session": admitted_session,
        "binding": binding.binding_ref,
        "fingerprint": expected.fingerprint,
        "generation": binding.binding_generation,
        "evidence_policy": binding.evidence_policy.value,
    }
    try:
        provenance = admit_operation_provenance(**values)
    except Exception:
        values["session"] = None
        provenance = admit_operation_provenance(**values)
    return provenance, resolution


def _admit_bound_route(
    target: Any,
    session: Any,
    attachment_source: Any,
    arguments: dict[str, Any],
    resolution: Any,
    provenance: Any,
) -> tuple[Any, SessionIdentity]:
    binding = resolution.binding
    expected = binding.target
    if target is not expected:
        raise ValueError("target mismatch")
    if (
        type(session) is not SessionIdentity
        or session.target is not expected
        or type(session.session_id) is not str
        or type(session.sequence) is not int
        or not 0 <= session.sequence < 2**63
        or session.sequence != binding.binding_generation
        or provenance.session != session.session_id
    ):
        raise ValueError("session mismatch")
    attachment = _attachment_values(attachment_source)
    if (
        attachment["target"] is not expected
        or attachment["session"] is not session
        or type(attachment["binding_generation"]) is not int
        or attachment["binding_generation"] != binding.binding_generation
        or type(attachment["host"]) is not str
        or not attachment["host"]
        or type(attachment["port"]) is not int
        or not 0 < attachment["port"] <= 65535
    ):
        raise ValueError("attachment mismatch")
    if not _matches_argument(arguments, "host", attachment["host"], str):
        raise ValueError("host mismatch")
    if not _matches_argument(arguments, "port", attachment["port"], int):
        raise ValueError("port mismatch")
    if "display" in arguments:
        display = attachment["display"]
        if type(display) is not str or not _matches_argument(arguments, "display", display, str):
            raise ValueError("display mismatch")
    return expected, session


def blocked_bound_route(
    context: Any, request: Any,
) -> OperationResult | None:
    """Return a fixed refusal unless a bound native request has a current route.

    This narrow preflight deliberately evaluates neither hidden arguments nor
    endpoint/display helpers.  Registered-tool composition uses it before
    provider-owned callbacks; shared operation execution repeats the exact
    validation with its request arguments before calling an executor.
    """

    trusted_request, provenance = _fixed_request(), None
    try:
        if type(context) is not ApplicationContext:
            raise ValueError("invalid context")
        runtime_target, _catalog, _ledger = _application_boundary(context)
        trusted_request = _snapshot_request(request)
        if runtime_target is None:
            raise ValueError("bound runtime target missing")
        provenance, resolution = _binding_provenance(
            runtime_target, context.session, trusted_request
        )
        _admit_bound_route(
            context.target, context.session, context.attachment,
            trusted_request.arguments, resolution, provenance,
        )
    except Exception:
        return _fixed_result(
            trusted_request, provenance,
            verdict=OperationVerdict.BLOCKED,
            code="runtime-target-route-blocked",
            message="operation route was not admitted",
        )
    return None


def execute_operation(context: ApplicationContext, request: OperationRequest) -> OperationResult:
    """Execute one operation after schema-independent bound-route admission."""

    if type(context) is not ApplicationContext:
        return _fixed_result(
            _fixed_request(),
            None,
            verdict=OperationVerdict.FAILURE,
            code="invalid-executor-result",
            message="operation result was not admitted",
        )
    trusted_request, provenance = _fixed_request(), None
    try:
        runtime_target, catalog, ledger = _application_boundary(context)
        if runtime_target is None and ledger.root is None:
            return context.executor.execute(
                request, target=context.target, session=context.session
            )
        trusted_request = _snapshot_request(request)
        if runtime_target is None:
            raise ValueError("bound runtime target missing")
        if trusted_request.name in _LIFECYCLE_OPERATION_NAMES:
            return context.executor.execute(
                request, target=context.target, session=context.session
            )
        if trusted_request.name not in NATIVE_SESSION_OPERATION_NAMES:
            raise ValueError("unknown bound operation")
        target = context.target
        session = context.session
        attachment = context.attachment
        executor = context.executor
        provenance, resolution = _binding_provenance(
            runtime_target, session, trusted_request
        )
        arguments = trusted_request.arguments
        target, session = _admit_bound_route(
            target, session, attachment, arguments, resolution, provenance
        )
    except Exception:
        return _fixed_result(
            trusted_request,
            provenance,
            verdict=OperationVerdict.BLOCKED,
            code="runtime-target-route-blocked",
            message="operation route was not admitted",
        )

    try:
        with ledger.operation(trusted_request.name) as scope:
            try:
                raw = executor.execute(
                    trusted_request, target=target, session=session
                )
            except Exception:
                raw = _fixed_result(
                    trusted_request,
                    None,
                    verdict=OperationVerdict.FAILURE,
                    code="executor-failure",
                    message="executor operation failed",
                )
            if trusted_request.name == "read_active_window":
                try:
                    raw = _project_bound_active_window(raw, trusted_request)
                except OperationBoundaryError as error:
                    # Retain the boundary's complete fixed failure partition;
                    # wrapping malformed data as executor failure loses it.
                    return _fixed_result(
                        _fixed_request(trusted_request.kind, trusted_request.name),
                        provenance, verdict=OperationVerdict.FAILURE,
                        code=("result-too-large" if error.code == "result-too-large"
                              else "invalid-executor-result"),
                        message="operation result was not admitted",
                    )
            # Declared output schemas still normalize their public result.
            # Schema-missing but explicitly native operations retain the
            # executor's established contract after the same route admission.
            if trusted_request.name not in catalog:
                return raw
            # Only source-owned production has populated this scope. Collect
            # those records without inspecting untrusted artifact fields first;
            # normalization owns shape/size-before-receipt failure ordering.
            normalized = normalize_operation_result(
                context, trusted_request, raw, provenance, scope=scope,
                receipts=ledger._scope_receipts(scope),
            )
            if normalized.verdict is OperationVerdict.SUCCESS:
                scope._retain()
            return normalized
    except Exception:
        return _fixed_result(
            trusted_request,
            provenance,
            verdict=OperationVerdict.FAILURE,
            code="invalid-executor-result",
            message="operation result was not admitted",
        )


def execute_mcp_operation(context: ApplicationContext, request: OperationRequest) -> OperationResult:
    """Execute through the shared MCP boundary."""

    return execute_operation(context, request)


def execute_scenario_operation(context: ApplicationContext, request: OperationRequest) -> OperationResult:
    """Execute through the shared ScenarioRunner boundary."""

    return execute_operation(context, request)
