from __future__ import annotations

import json
import math
import os
from dataclasses import FrozenInstanceError
from pathlib import Path
from types import MappingProxyType
from urllib.parse import quote

import pytest

from tests.support.boundary_inputs import encoded as _encoded, nested_arrays as _nested_arrays
from tests.support.runtime_targets import TargetProfileInputs

from qa_mcp.config import Settings
from qa_mcp.core import (
    ApplicationContext,
    ArtifactReference,
    EvidenceLedger,
    EvidenceScope,
    OperationBoundaryError,
    OperationError,
    OperationKind,
    OperationRequest,
    OperationResult,
    OperationVerdict,
    admit_operation_provenance,
    normalize_operation_result,
    resolve_runtime_target,
)
import qa_mcp.core.boundary as _boundary


REQUEST = OperationRequest(OperationKind.READ, "read_active_window")
FINGERPRINT = "sha256:" + "a" * 64


class Executor:
    name = "boundary-test"

    def execute(self, request, *, target, session):
        del target, session
        return OperationResult.success(request)


def _settings() -> Settings:
    return Settings(manager_templates="manager.json", value_read_templates="value.json")


def _context() -> ApplicationContext:
    return ApplicationContext(settings=_settings(), executor=Executor())


def _full_local_context(tmp_path: Path) -> tuple[ApplicationContext, Path]:
    root = tmp_path / "evidence"
    root.mkdir(parents=True)
    (tmp_path / "target.env").write_text("INFOBASE_PATH=/private/test\n", encoding="utf-8")
    inputs = TargetProfileInputs(
        tmp_path, fingerprint="target-observed", evidence_policy="full_local",
        non_production_approved=True,
    )
    inputs.write_profile()
    resolution = resolve_runtime_target(inputs.handoff_env())
    assert resolution is not None
    return ApplicationContext(settings=_settings(), executor=Executor(), runtime_target=resolution), root


def _provenance(**changes: object):
    values = {
        "operation": "read_active_window",
        "target": "client.target",
        "session": "session-1",
        "binding": "binding.main",
        "fingerprint": FINGERPRINT,
        "generation": 7,
        "evidence_policy": "sanitized",
    }
    values.update(changes)
    return admit_operation_provenance(**values)


def _raw(
    *,
    value: object = None,
    verdict: OperationVerdict = OperationVerdict.SUCCESS,
    details: object = None,
    artifacts: tuple[ArtifactReference, ...] = (),
) -> OperationResult:
    error = None
    if verdict is not OperationVerdict.SUCCESS:
        error = OperationError("EXECUTOR-SECRET", "executor secret", True, details or {})
    return OperationResult(
        request=OperationRequest(OperationKind.WRITE, "executor_forgery"),
        verdict=verdict,
        value=value,
        error=error,
        artifacts=artifacts,
    )


def _normalize(
    value: object = None,
    *,
    context: ApplicationContext | None = None,
    verdict: OperationVerdict = OperationVerdict.SUCCESS,
    details: object = None,
    artifacts: tuple[ArtifactReference, ...] = (),
    provenance=None,
    **kwargs,
) -> OperationResult:
    # Generic finite-class matrices are explicit test fixtures.  The
    # production read_active_window schema intentionally admits only the
    # bounded window observation; temporarily selecting a fixture catalog
    # keeps these legacy class/URL controls while leaving production authority
    # unchanged.  Contexts supplied by authority/provenance tests retain the
    # real catalog and are never switched.
    if context is not None:
        return normalize_operation_result(
            context, REQUEST,
            _raw(value=value, verdict=verdict, details=details, artifacts=artifacts),
            provenance or _provenance(), **kwargs,
        )
    original = _boundary._SOURCE_SCHEMAS
    fixture_read = ("read_active_window", _boundary._COMMON, _boundary._COMMON, True)
    _boundary._SOURCE_SCHEMAS = _boundary.MappingProxyType({
        "read_active_window": fixture_read,
        "get_window_list": original["get_window_list"],
        "capture_screenshot": original["capture_screenshot"],
    })
    try:
        return normalize_operation_result(
            _context(), REQUEST,
            _raw(value=value, verdict=verdict, details=details, artifacts=artifacts),
            provenance or _provenance(), **kwargs,
        )
    finally:
        _boundary._SOURCE_SCHEMAS = original


def _assert_fixed_invalid(
    result: OperationResult,
    *fragments: str,
    code: str = "invalid-executor-result",
) -> None:
    payload = result.to_dict()
    assert result.verdict is OperationVerdict.FAILURE
    assert result.value is None and result.artifacts == ()
    assert result.error and result.error.code == code
    rendered = json.dumps(payload, ensure_ascii=False, default=str)
    for fragment in fragments:
        assert fragment not in rendered


def test_context_catalog_is_constructor_proof_deeply_immutable_and_sealed() -> None:
    with pytest.raises(TypeError):
        ApplicationContext(  # type: ignore[call-arg]
            settings=_settings(), executor=Executor(), operation_schemas={}
        )
    context = _context()
    assert isinstance(context.operation_schemas, MappingProxyType)
    schema = context.operation_schemas["read_active_window"]
    with pytest.raises((TypeError, AttributeError)):
        object.__setattr__(schema, "value", ())
    with pytest.raises(TypeError):
        context.operation_schemas["other"] = schema  # type: ignore[index]
    with pytest.raises(FrozenInstanceError):
        context.operation_schemas = {}  # type: ignore[assignment]
    with pytest.raises(FrozenInstanceError):
        del context.operation_schemas
    object.__setattr__(context, "operation_schemas", {"read_active_window": schema})
    _assert_fixed_invalid(_normalize({"referenceLabel": "Reference label 7"}, context=context))
    context, replacement = _context(), _context()
    object.__setattr__(context, "operation_schemas", replacement.operation_schemas)
    _assert_fixed_invalid(_normalize({"referenceLabel": "Reference label 7"}, context=context))


def test_application_contexts_own_distinct_frozen_ledgers() -> None:
    first, second = _context(), _context()
    assert first.evidence_ledger is not second.evidence_ledger
    with pytest.raises(FrozenInstanceError):
        first.evidence_ledger = second.evidence_ledger  # type: ignore[assignment]
    with pytest.raises(FrozenInstanceError):
        del first.evidence_ledger
    object.__setattr__(first, "evidence_ledger", second.evidence_ledger)
    _assert_fixed_invalid(_normalize(context=first))


class ExplodingValue:
    def __getattribute__(self, name: str):
        raise RuntimeError("UNDECLARED-SENTINEL")


def test_undeclared_value_is_omitted_without_access() -> None:
    output = _normalize(
        {"unknown": ExplodingValue(), "referenceLabel": "Reference label 7"}
    ).to_dict()
    assert output["value"] == {"referenceLabel": "Reference label 7"}
    assert "UNDECLARED-SENTINEL" not in json.dumps(output)


@pytest.mark.parametrize(
    ("field", "values"),
    [
        ("active", [False, True]),
        ("sequence", [-(2**63), 0, 2**63 - 1]),
        ("duration", [-(2**63), 2**63 - 1, -0.0, 0.0, 1.5]),
        ("referenceCount", [0, 2_147_483_647]),
        ("referenceLabel", ["Reference label 7"]),
        (
            "documentationURL",
            [
                "HTTPS://DOCS.EXAMPLE.COM:443/guide",
                "http://192.0.2.10:80/guide",
                "https://8.8.8.8/guide",
                "https://[2001:0db8:0:0::1]/guide",
                "https://BÜCHER.EXAMPLE/guide",
            ],
        ),
    ],
)
def test_six_class_exact_valid_cells_preserve(field: str, values: list[object]) -> None:
    for value in values:
        output = _normalize({field: value}).to_dict()["value"]
        assert field in output
        if field == "documentationURL":
            assert output[field].startswith(("http://", "https://"))
        else:
            assert output[field] == value


class IntSubclass(int):
    pass


class FloatSubclass(float):
    pass


class StringSubclass(str):
    pass


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("active", [0, 1, "true", None]),
        ("sequence", ["7", 7.0, True, None, IntSubclass(7), -(2**63) - 1, 2**63]),
        (
            "duration",
            ["1.5", True, None, IntSubclass(1), FloatSubclass(1.5), 2**63, math.nan, math.inf, -math.inf],
        ),
        (
            "referenceCount",
            ["1", 1.0, True, None, IntSubclass(1), -1, 2_147_483_648],
        ),
        (
            "referenceLabel",
            [7, {"x": 1}, None, StringSubclass("Reference label 7"), "another label"],
        ),
        (
            "documentationURL",
            [7, {"x": 1}, None, StringSubclass("https://docs.example.com/guide")],
        ),
    ],
)
def test_six_class_invalid_cells_have_one_complete_outcome(field: str, invalid: list[object]) -> None:
    for candidate in invalid:
        _assert_fixed_invalid(_normalize({field: candidate}))


@pytest.mark.parametrize(
    ("candidate", "canonical"),
    [
        ("https://[2001:0db8:0:0::1]:443/guide", "https://[2001:db8::1]/guide"),
        ("HTTPS://BÜCHER.EXAMPLE:443/guide", "https://xn--bcher-kva.example/guide"),
    ],
)
def test_documentation_url_host_canonicalization_is_exact(candidate: str, canonical: str) -> None:
    assert _normalize({"documentationURL": candidate}).to_dict()["value"]["documentationURL"] == canonical


@pytest.mark.parametrize(
    "candidate",
    [
        "C:relative-secret",
        "C:\\private\\secret",
        "\\\\server\\share\\secret",
        "\\\\?\\C:\\private\\secret",
        "/tmp/private",
        "token=VALUE-SENTINEL",
        "connectionString=VALUE-SENTINEL",
        "User Id=VALUE-SENTINEL",
        "Data Source=VALUE-SENTINEL",
        "accessKey=VALUE-SENTINEL",
        "hostname=127.0.0.1",
        "127.0.0.1:8080",
        "[::1]:15381",
        "another label",
    ],
)
@pytest.mark.parametrize("location", ["value", "error"])
def test_same_path_literal_hostiles_fail_at_value_and_error(location: str, candidate: str) -> None:
    if location == "value":
        result = _normalize({"referenceLabel": candidate})
    else:
        result = _normalize(
            verdict=OperationVerdict.FAILURE,
            details={"referenceLabel": candidate},
        )
    _assert_fixed_invalid(result, candidate, "VALUE-SENTINEL")


@pytest.mark.parametrize("location", ["value", "error"])
def test_same_path_exact_literal_preserves_at_value_and_error(location: str) -> None:
    if location == "value":
        output = _normalize({"referenceLabel": "Reference label 7"}).to_dict()
        assert output["value"]["referenceLabel"] == "Reference label 7"
    else:
        output = _normalize(
            verdict=OperationVerdict.FAILURE,
            details={"referenceLabel": "Reference label 7"},
        ).to_dict()
        assert output["error"]["code"] == "executor-failure"
        assert output["error"]["details"]["referenceLabel"] == "Reference label 7"
        assert "EXECUTOR-SECRET" not in json.dumps(output)


@pytest.mark.parametrize(
    ("verdict", "code"),
    [
        (OperationVerdict.BLOCKED, "executor-blocked"),
        (OperationVerdict.AMBIGUOUS, "executor-ambiguous"),
        (OperationVerdict.FAILURE, "executor-failure"),
    ],
)
def test_non_success_verdicts_use_only_fixed_error_envelopes(
    verdict: OperationVerdict,
    code: str,
) -> None:
    output = _normalize(
        verdict=verdict,
        details={"referenceLabel": "Reference label 7", "secret": ExplodingValue()},
    ).to_dict()
    assert output["verdict"] == verdict.value
    assert output["error"] == {
        "code": code,
        "message": {
            OperationVerdict.BLOCKED: "executor reported a blocked operation",
            OperationVerdict.AMBIGUOUS: "executor reported an ambiguous operation",
            OperationVerdict.FAILURE: "executor reported an operation failure",
        }[verdict],
        "retryable": True,
        "details": {"referenceLabel": "Reference label 7"},
    }
    assert "EXECUTOR-SECRET" not in json.dumps(output)


@pytest.mark.parametrize("depth", range(1, 6))
@pytest.mark.parametrize("case", ["credential", "user", "userpass", "control"])
def test_documentation_url_depth_matrix(depth: int, case: str) -> None:
    if case == "credential":
        url = "https://docs.example.com/" + _encoded("token=URL-SECRET", depth)
    elif case in {"user", "userpass"}:
        authority = "user@docs.example.com" if case == "user" else "user:pass@docs.example.com"
        url = "https://" + _encoded(authority, depth) + "/guide"
    else:
        url = "https://docs.example.com/" + _encoded("safe guide", depth)
    result = _normalize({"documentationURL": url})
    if case == "control" and depth <= 4:
        assert result.to_dict()["value"]["documentationURL"] == "https://docs.example.com/safe%20guide"
    else:
        _assert_fixed_invalid(result, url, "URL-SECRET", "user:pass")


@pytest.mark.parametrize("depth", range(1, 5))
@pytest.mark.parametrize("control", [*(chr(value) for value in range(32)), "\x7f"])
def test_documentation_url_rejects_controls_after_every_decode(depth: int, control: str) -> None:
    candidate = "safe" + control + "tail"
    url = "https://docs.example.com/" + _encoded(candidate, depth)
    _assert_fixed_invalid(_normalize({"documentationURL": url}), url, candidate)


@pytest.mark.parametrize("location", ["leading", "path"])
@pytest.mark.parametrize("control", [*(chr(value) for value in range(32)), "\x7f"])
def test_documentation_url_rejects_raw_parser_stripping_controls(
    location: str, control: str
) -> None:
    url = (
        control + "https://docs.example.com/guide"
        if location == "leading"
        else "https://docs.example.com/guide" + control + "part"
    )
    _assert_fixed_invalid(_normalize({"documentationURL": url}), url)


@pytest.mark.parametrize("depth", range(1, 5))
@pytest.mark.parametrize("delimiter", ["?secret", "#secret", "/shadow", "\\shadow"])
def test_documentation_url_rejects_decoded_authority_structure_changes(
    depth: int, delimiter: str
) -> None:
    authority = _encoded("docs.example.com" + delimiter, depth)
    url = "https://" + authority + "/guide"
    _assert_fixed_invalid(_normalize({"documentationURL": url}), url, delimiter)


@pytest.mark.parametrize("depth", range(1, 5))
def test_documentation_url_preserves_valid_encoded_default_port(depth: int) -> None:
    port = ":443"
    for _ in range(depth):
        port = quote(port, safe="")
    url = "https://docs.example.com" + port + "/guide"
    assert _normalize({"documentationURL": url}).to_dict()["value"]["documentationURL"] == "https://docs.example.com/guide"


@pytest.mark.parametrize(
    "url",
    [
        "http://127.1/private",
        "http://169.254.169.254/latest",
        "http://10.0.0.1/x",
        "http://0x7f000001/x",
        "http://0177.0.0.1/x",
        "http://localhost/x",
        "http://host.internal/x",
        "http://[::1]/x",
        "http://[fe80::1%25eth0]/x",
        "http://[64:ff9b::127.0.0.1]/x",
        "http://[2002:7f00:1::]/x",
        "http://0.0.0.0/x",
        "http://224.0.0.1/x",
        "http://240.0.0.1/x",
        "http://[::]/x",
        "http://[ff02::1]/x",
        "https://user@8.8.8.8/x",
        "https://user:pass@docs.example.com/x",
        "https://docs.example.com/x?q=secret",
        "https://docs.example.com/x#secret",
        "https://docs.example.com/guide%20token%3DURL-SECRET",
        "https://docs.example.com/%ZZ",
        "https://docs.example.com/%00private",
        "https://docs.example.com:99999/x",
    ],
)
def test_documentation_url_nonpublic_and_malformed_values_reject(url: str) -> None:
    _assert_fixed_invalid(_normalize({"documentationURL": url}), url, "URL-SECRET")


def test_documentation_url_scalar_boundary() -> None:
    prefix = "https://docs.example.com/"
    for size, accepted in ((2047, True), (2048, True), (2049, False)):
        candidate = prefix + "x" * (size - len(prefix))
        result = _normalize({"documentationURL": candidate})
        assert (result.error is None) is accepted
        if not accepted:
            _assert_fixed_invalid(result, candidate)


@pytest.mark.parametrize(
    ("artifact", "accepted"),
    [
        (ArtifactReference("a" * 127), True),
        (ArtifactReference("a" * 128), True),
        (ArtifactReference("a" * 129), False),
        (ArtifactReference("proof", "a" * 63 + "/" + "b" * 62), True),
        (ArtifactReference("proof", "a" * 63 + "/" + "b" * 63), True),
        (ArtifactReference("proof", "a" * 63 + "/" + "b" * 64), False),
        (ArtifactReference("proof", sha256=""), True),
        (ArtifactReference("proof", sha256="sha256:" + "a" * 64), True),
        (ArtifactReference("proof", sha256="sha256:" + "a" * 63), False),
        (ArtifactReference("proof", sha256="sha256:" + "A" * 64), False),
        (ArtifactReference("proof", sensitivity="public"), True),
        (ArtifactReference("proof", sensitivity="private"), False),
        (ArtifactReference("proof", sensitivity=StringSubclass("internal")), False),
    ],
)
def test_artifact_field_boundaries_are_exact(artifact: ArtifactReference, accepted: bool) -> None:
    result = _normalize(artifacts=(artifact,))
    assert (result.error is None) is accepted
    if accepted:
        assert "path" not in result.to_dict()["artifacts"][0]
    else:
        _assert_fixed_invalid(result)


@pytest.mark.parametrize(
    "artifact",
    [
        ArtifactReference(StringSubclass("proof")),
        ArtifactReference("proof", StringSubclass("image/png")),
        ArtifactReference("proof", sha256=StringSubclass("sha256:" + "a" * 64)),
    ],
)
def test_every_artifact_text_field_rejects_subclasses(artifact: ArtifactReference) -> None:
    _assert_fixed_invalid(_normalize(artifacts=(artifact,)))


def test_malformed_artifact_shape_and_tuple_are_fixed() -> None:
    artifact = ArtifactReference("proof")
    object.__delattr__(artifact, "artifact_id")
    _assert_fixed_invalid(_normalize(artifacts=(artifact,)))

    class ArtifactSubclass(ArtifactReference):
        pass

    _assert_fixed_invalid(_normalize(artifacts=(ArtifactSubclass("proof"),)))

    class TupleSubclass(tuple):
        pass

    raw = _raw()
    object.__setattr__(raw, "artifacts", TupleSubclass((ArtifactReference("proof"),)))
    _assert_fixed_invalid(normalize_operation_result(_context(), REQUEST, raw, _provenance()))


def test_artifact_collection_limit_and_duplicate_identity_are_exact() -> None:
    exact = _normalize(artifacts=tuple(ArtifactReference(f"a{index}") for index in range(64)))
    above = _normalize(artifacts=tuple(ArtifactReference(f"a{index}") for index in range(65)))
    duplicate = _normalize(artifacts=(ArtifactReference("proof"), ArtifactReference("proof")))
    assert exact.error is None and len(exact.artifacts) == 64
    assert above.error and above.error.code == "result-too-large"
    _assert_fixed_invalid(duplicate)


def test_sanitized_executor_path_never_emits(tmp_path: Path) -> None:
    result = _normalize(
        artifacts=(ArtifactReference("proof", "image/png", path=str(tmp_path / "private")),)
    ).to_dict()
    assert "path" not in result["artifacts"][0]
    assert str(tmp_path) not in json.dumps(result)


def test_full_local_uses_only_current_exact_scope_receipt(tmp_path: Path) -> None:
    context, root = _full_local_context(tmp_path)
    first = root / "first.png"
    second = root / "second.png"
    first.write_bytes(b"first")
    second.write_bytes(b"second")
    ledger = context.evidence_ledger
    with ledger.operation() as first_scope, ledger.operation() as second_scope:
        first_receipt = first_scope.record("proof", first)
        second_receipt = second_scope.record("proof", second)
        raw = _raw(artifacts=(ArtifactReference("proof", "image/png", path="C:\\forged"),))
        valid = normalize_operation_result(
            context,
            REQUEST,
            raw,
            _provenance(evidence_policy="full_local"),
            scope=first_scope,
            receipts=(first_receipt,),
        )
        assert valid.to_dict()["artifacts"][0]["path"] == str(first.resolve())
        foreign = normalize_operation_result(
            context,
            REQUEST,
            raw,
            _provenance(evidence_policy="full_local"),
            scope=first_scope,
            receipts=(second_receipt,),
        )
        _assert_fixed_invalid(
            foreign,
            str(second),
            "C:\\forged",
            code="invalid-evidence-receipt",
        )
        extra = normalize_operation_result(
            context,
            REQUEST,
            raw,
            _provenance(evidence_policy="full_local"),
            scope=first_scope,
            receipts=(first_receipt, first_scope.record("extra", first)),
        )
        _assert_fixed_invalid(extra, code="invalid-evidence-receipt")
        object.__setattr__(first_receipt, "path", second)
        mutated = normalize_operation_result(
            context,
            REQUEST,
            raw,
            _provenance(evidence_policy="full_local"),
            scope=first_scope,
            receipts=(first_receipt,),
        )
        _assert_fixed_invalid(
            mutated,
            str(second),
            code="invalid-evidence-receipt",
        )
    stale = normalize_operation_result(
        context,
        REQUEST,
        raw,
        _provenance(evidence_policy="full_local"),
        scope=first_scope,
        receipts=(first_receipt,),
    )
    _assert_fixed_invalid(
        stale,
        str(first),
        code="invalid-evidence-receipt",
    )


def test_overlapping_contexts_and_exception_cleanup_are_isolated(tmp_path: Path) -> None:
    first_context, first_root = _full_local_context(tmp_path / "first")
    second_context, second_root = _full_local_context(tmp_path / "second")
    first_path, second_path = first_root / "proof", second_root / "proof"
    first_path.write_text("first")
    second_path.write_text("second")
    first_scope = None
    with pytest.raises(RuntimeError):
        with first_context.evidence_ledger.operation() as first_scope:
            first_scope.record("proof", first_path)
            with second_context.evidence_ledger.operation() as second_scope:
                receipt = second_scope.record("proof", second_path)
                valid = normalize_operation_result(
                    second_context,
                    REQUEST,
                    _raw(artifacts=(ArtifactReference("proof"),)),
                    _provenance(evidence_policy="full_local"),
                    scope=second_scope,
                    receipts=(receipt,),
                )
                assert valid.to_dict()["artifacts"][0]["path"] == str(second_path.resolve())
            raise RuntimeError("scope failure")
    assert first_scope is not None
    with pytest.raises(OperationBoundaryError):
        first_scope.record("late", first_path)


def test_ledger_rejects_wrong_path_class_symlink_outside_and_mutation(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    inside = root / "inside"
    inside.write_text("inside")
    outside = tmp_path / "outside"
    outside.write_text("outside")
    link = root / "link"
    link.symlink_to(outside)
    ledger = EvidenceLedger(root, "full_local")

    class PathSubclass(type(root)):
        pass

    with ledger.operation() as scope:
        scope.record("inside", inside)
        forged = EvidenceScope(ledger, scope._token)
        with pytest.raises(OperationBoundaryError):
            forged.record("forged", inside)
        for candidate in (outside, link, PathSubclass(str(inside))):
            with pytest.raises(OperationBoundaryError) as caught:
                scope.record("other", candidate)
            assert caught.value.code == "invalid-evidence-receipt"
    with pytest.raises((AttributeError, FrozenInstanceError)):
        ledger.policy = "sanitized"  # type: ignore[misc]
    with pytest.raises((AttributeError, FrozenInstanceError)):
        ledger.root = tmp_path  # type: ignore[misc]


def test_context_rejects_coherent_private_ledger_authority_mutation(tmp_path: Path) -> None:
    context, root = _full_local_context(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    proof = outside / "proof"
    proof.write_text("outside")
    ledger = context.evidence_ledger
    object.__setattr__(ledger, "_authority", (outside.resolve(), "full_local"))
    object.__setattr__(ledger, "_guard", (outside.resolve(), "full_local", ledger._seal))
    with ledger.operation() as scope:
        receipt = scope.record("proof", proof)
        result = normalize_operation_result(
            context,
            REQUEST,
            _raw(artifacts=(ArtifactReference("proof"),)),
            _provenance(evidence_policy="full_local"),
            scope=scope,
            receipts=(receipt,),
        )
    _assert_fixed_invalid(result, str(outside))


def _path_of_exact_length(root: Path, size: int) -> Path:
    current = root
    while len(str(current)) + 202 < size:
        current = current / ("d" * 200)
        current.mkdir(exist_ok=True)
    tail = size - len(str(current)) - 1
    assert 0 < tail <= 200
    result = current / ("f" * tail)
    result.write_text("proof")
    assert len(str(result.resolve())) == size
    return result


@pytest.mark.skipif(os.name == "nt", reason="Windows path limits are covered by offline scalar probes")
def test_receipt_path_scalar_boundary_is_exact(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    ledger = EvidenceLedger(root, "full_local")
    for size, accepted in ((2047, True), (2048, True), (2049, False)):
        candidate = _path_of_exact_length(root, size)
        with ledger.operation() as scope:
            if accepted:
                assert scope.record(f"proof-{size}", candidate).path == candidate.resolve()
            else:
                with pytest.raises(OperationBoundaryError) as caught:
                    scope.record(f"proof-{size}", candidate)
                assert caught.value.code == "invalid-evidence-receipt"


def _node_matrix(total_nodes: int) -> dict[str, object]:
    # value object + outer array + eight inner arrays + 448 full-row scalars = 458
    tail = total_nodes - 458
    assert 0 <= tail <= 64
    return {"matrix": [[0] * 64 for _ in range(7)] + [[0] * tail]}


@pytest.mark.parametrize("nodes,accepted", [(511, True), (512, True), (513, False)])
def test_shared_node_boundary_is_exact(nodes: int, accepted: bool) -> None:
    result = _normalize(_node_matrix(nodes))
    assert (result.error is None) is accepted
    if not accepted:
        assert result.error and result.error.code == "result-too-large"


def test_artifact_five_nodes_share_the_content_counter() -> None:
    accepted = _normalize(_node_matrix(507), artifacts=(ArtifactReference("proof"),))
    rejected = _normalize(_node_matrix(508), artifacts=(ArtifactReference("proof"),))
    assert accepted.error is None
    assert rejected.error and rejected.error.code == "result-too-large"


def test_rejected_artifact_charges_zero_and_field_validation_precedes_receipt(
    tmp_path: Path,
) -> None:
    context, _ = _full_local_context(tmp_path)
    with context.evidence_ledger.operation() as scope:
        invalid = normalize_operation_result(
            context,
            REQUEST,
            _raw(value=_node_matrix(508), artifacts=(ArtifactReference("A-invalid"),)),
            _provenance(evidence_policy="full_local"),
            scope=scope,
        )
        assert invalid.error and invalid.error.code == "invalid-executor-result"
        missing_receipt = normalize_operation_result(
            context,
            REQUEST,
            _raw(artifacts=(ArtifactReference("proof"),)),
            _provenance(evidence_policy="full_local"),
            scope=scope,
        )
        assert missing_receipt.error and missing_receipt.error.code == "invalid-evidence-receipt"


@pytest.mark.parametrize(
    "artifact",
    [
        ArtifactReference("A-invalid"),
        ArtifactReference("proof", "INVALID"),
        ArtifactReference("proof", sha256="sha256:invalid"),
        ArtifactReference("proof", sensitivity="private"),
    ],
)
@pytest.mark.parametrize("receipt_case", ["missing-scope", "malformed", "foreign"])
def test_artifact_local_failure_precedes_every_receipt_failure(
    tmp_path: Path, artifact: ArtifactReference, receipt_case: str
) -> None:
    context, root = _full_local_context(tmp_path)
    proof = root / "proof"
    proof.write_text("proof")
    with context.evidence_ledger.operation() as scope:
        receipt = scope.record("proof", proof)
        selected_scope = None if receipt_case == "missing-scope" else scope
        receipts = (object(),) if receipt_case == "malformed" else (receipt,)
        if receipt_case == "foreign":
            with context.evidence_ledger.operation() as foreign_scope:
                selected_scope = foreign_scope
                result = normalize_operation_result(
                    context, REQUEST, _raw(artifacts=(artifact,)),
                    _provenance(evidence_policy="full_local"),
                    scope=selected_scope, receipts=receipts,
                )
        else:
            result = normalize_operation_result(
                context, REQUEST, _raw(artifacts=(artifact,)),
                _provenance(evidence_policy="full_local"),
                scope=selected_scope, receipts=receipts,
            )
    _assert_fixed_invalid(result, code="invalid-executor-result")


@pytest.mark.parametrize("field", ["artifact_id", "path", "_ledger", "_scope"])
def test_malformed_exact_receipt_stays_invalid_evidence(
    tmp_path: Path, field: str
) -> None:
    context, root = _full_local_context(tmp_path)
    proof = root / "proof"
    proof.write_text("proof")
    with context.evidence_ledger.operation() as scope:
        receipt = scope.record("proof", proof)
        object.__delattr__(receipt, field)
        result = normalize_operation_result(
            context, REQUEST, _raw(artifacts=(ArtifactReference("proof"),)),
            _provenance(evidence_policy="full_local"), scope=scope, receipts=(receipt,),
        )
    _assert_fixed_invalid(result, code="invalid-evidence-receipt")


@pytest.mark.parametrize("value", [[], {}])
def test_unhashable_receipt_identity_stays_invalid_evidence(
    tmp_path: Path, value: object
) -> None:
    context, root = _full_local_context(tmp_path)
    proof = root / "proof"
    proof.write_text("proof")
    with context.evidence_ledger.operation() as scope:
        receipt = scope.record("proof", proof)
        object.__setattr__(receipt, "artifact_id", value)
        result = normalize_operation_result(
            context, REQUEST, _raw(artifacts=(ArtifactReference("proof"),)),
            _provenance(evidence_policy="full_local"), scope=scope, receipts=(receipt,),
        )
    _assert_fixed_invalid(result, code="invalid-evidence-receipt")


@pytest.mark.parametrize("field", ["_ledger", "_token"])
def test_malformed_exact_scope_stays_invalid_evidence(tmp_path: Path, field: str) -> None:
    context, root = _full_local_context(tmp_path)
    proof = root / "proof"
    proof.write_text("proof")
    with context.evidence_ledger.operation() as scope:
        receipt = scope.record("proof", proof)
        object.__delattr__(scope, field)
        result = normalize_operation_result(
            context, REQUEST, _raw(artifacts=(ArtifactReference("proof"),)),
            _provenance(evidence_policy="full_local"), scope=scope, receipts=(receipt,),
        )
    _assert_fixed_invalid(result, code="invalid-evidence-receipt")


@pytest.mark.parametrize("arrays,accepted", [(5, True), (6, True), (7, False)])
def test_depth_boundary_is_exact(arrays: int, accepted: bool) -> None:
    result = _normalize({"nested": _nested_arrays(arrays)})
    assert (result.error is None) is accepted
    if not accepted:
        assert result.error and result.error.code == "result-too-large"


@pytest.mark.parametrize("items,accepted", [(63, True), (64, True), (65, False)])
def test_item_boundary_counts_unknown_keys_without_reading_values(items: int, accepted: bool) -> None:
    value = {f"unknown{index}": ExplodingValue() for index in range(items - 1)}
    value["referenceLabel"] = "Reference label 7"
    result = _normalize(value)
    assert (result.error is None) is accepted
    if accepted:
        assert result.to_dict()["value"] == {"referenceLabel": "Reference label 7"}
    else:
        assert result.error and result.error.code == "result-too-large"


def _byte_result(tail_length: int) -> OperationResult:
    prefix = "https://docs.example.com/"
    links = [prefix + "x" * (2048 - len(prefix)) for _ in range(31)]
    links.append(prefix + "y" * tail_length)
    return _normalize({"links": links})


def test_complete_canonical_utf8_byte_boundary_is_exact() -> None:
    seed = _byte_result(1)
    seed_size = len(json.dumps(seed.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())
    tail_65535 = 1 + 65535 - seed_size
    assert 1 <= tail_65535 <= 2000
    below = _byte_result(tail_65535)
    exact = _byte_result(tail_65535 + 1)
    above = _byte_result(tail_65535 + 2)
    assert len(json.dumps(below.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()) == 65535
    assert len(json.dumps(exact.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()) == 65536
    assert above.error and above.error.code == "result-too-large"


class DictSubclass(dict):
    def items(self):
        raise RuntimeError("MAPPING-SENTINEL")


@pytest.mark.parametrize(
    "value",
    [
        DictSubclass(referenceLabel="Reference label 7"),
        {"sequence": 10**5000},
        {"duration": math.inf},
        {"duration": math.nan},
    ],
)
def test_malformed_values_return_total_secret_safe_failure(value: object) -> None:
    result = _normalize(value)
    _assert_fixed_invalid(result, "MAPPING-SENTINEL")
    json.dumps(result.to_dict(), allow_nan=False)


def test_deleted_dto_fields_and_forged_provenance_are_total() -> None:
    raw = _raw(value={"referenceLabel": "Reference label 7"})
    object.__delattr__(raw, "verdict")
    result = normalize_operation_result(_context(), REQUEST, raw, _provenance())
    _assert_fixed_invalid(result)
    admitted = _provenance()
    object.__setattr__(admitted, "operation", "C:PROVENANCE-SENTINEL")
    forged = normalize_operation_result(_context(), REQUEST, _raw(), admitted)
    _assert_fixed_invalid(forged, "PROVENANCE-SENTINEL")


def test_dynamic_context_and_provenance_objects_are_not_inspected() -> None:
    class ExplodingObject:
        def __getattribute__(self, name: str):
            raise RuntimeError("DYNAMIC-AUTHORITY-SENTINEL")

    _assert_fixed_invalid(
        normalize_operation_result(ExplodingObject(), REQUEST, _raw(), _provenance()),
        "DYNAMIC-AUTHORITY-SENTINEL",
    )
    _assert_fixed_invalid(
        normalize_operation_result(_context(), REQUEST, _raw(), ExplodingObject()),
        "DYNAMIC-AUTHORITY-SENTINEL",
    )


@pytest.mark.parametrize("field", ["operation", "target", "session", "binding", "fingerprint"])
@pytest.mark.parametrize(
    "candidate",
    ["C:relative", "C:\\private", "/tmp/private", "x=y", "https://example.com"],
)
def test_provenance_rejects_physical_forms_without_echo(field: str, candidate: str) -> None:
    with pytest.raises(OperationBoundaryError) as caught:
        _provenance(**{field: candidate})
    assert caught.value.code == "invalid-operation-provenance"
    assert candidate not in str(caught.value)


@pytest.mark.parametrize("generation", [True, 0, -1, 1.0, "7", 2**63, pytest.param(10**5000, id="huge")])
def test_provenance_generation_is_exact_positive_int64(generation: object) -> None:
    with pytest.raises(OperationBoundaryError):
        _provenance(generation=generation)


def test_valid_provenance_is_immutable_and_serialized() -> None:
    admitted = _provenance()
    with pytest.raises(FrozenInstanceError):
        admitted.operation = "changed"  # type: ignore[misc]
    output = _normalize({"active": True}, provenance=admitted).to_dict()
    assert output["provenance"] == {
        "operation": "read_active_window",
        "target": "client.target",
        "session": "session-1",
        "binding": "binding.main",
        "fingerprint": FINGERPRINT,
        "generation": 7,
        "evidence_policy": "sanitized",
    }
