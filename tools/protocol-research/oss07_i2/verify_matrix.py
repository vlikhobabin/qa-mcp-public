#!/usr/bin/env python3
"""Fail-closed outer oracle for the OSS-07-I2 public-safety matrix."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Callable
SCHEMA = "qa-mcp.oss-07-i2.verification.v1"
MATRIX_SCHEMA = "qa-mcp.oss-07-i2.public-safety-matrix.v1"
FREEZE_SCHEMA = "qa-mcp.oss-07-i2.public-safety-freeze.v1"
CONTEXT_SCHEMA = "qa-mcp.oss-07-i2.helper-context.v1"
OUTPUT_SCHEMA = "qa-mcp.oss-07-i2.helper-output.v1"
EXPECTED_FREEZE_SHA256 = "fbfba8abdc249f152a9e5270d78933e463d53cae351efdf88502bf974979c884"
ROWS: tuple[tuple[str, str, int | str], ...] = (("P46", "P", 46), ("S14", "S", 14), ("D12", "P", 5), ("G18", "S", "D14"))
RED = (46, 14, 5, "D14")
EMAIL = b"eligible@example.invalid"
EMAIL_HEX = "656c696769626c65406578616d706c652e696e76616c6964"
EMAIL_SHA = "4aa460464f7b5a72e497da3759deaa0aa0e962be8d587663d65f056c4292da15"
BASE = "docs/protocol-research/evidence/oss-07-i2-fail-closed-public-safety-matrix-2026-09-02"
MATRIX_REL, FREEZE_REL = f"{BASE}/matrix.json", f"{BASE}/freeze.json"
HELPER_REL = "tools/protocol-research/oss07_i2/audit_design.py"
class Failure(ValueError):
    def __init__(self, failure_class: str, detail: str) -> None:
        super().__init__(detail)
        self.failure_class, self.detail = failure_class, detail
def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise Failure("json_duplicate_key", f"duplicate JSON key: {key}")
        result[key] = value
    return result
def load(data: bytes, source: str) -> Any:
    try:
        return json.loads(data, object_pairs_hook=strict_object)
    except Failure:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Failure("json_parse", f"{source} is not canonical JSON: {exc}") from exc
def keys(value: Any, expected: set[str], failure_class: str, subject: str) -> None:
    if type(value) is not dict or set(value) != expected:
        raise Failure(failure_class, f"{subject} keys differ from the frozen schema")
def validate_matrix(matrix: Any) -> None:
    keys(matrix, {"schema", "license_spdx", "semantic_labels", "eligible_email", "red_result", "non_email_rule_ids", "rows"}, "matrix_schema", "matrix")
    if matrix["schema"] != MATRIX_SCHEMA:
        raise Failure("matrix_schema", "matrix schema differs")
    if matrix["license_spdx"] != "Apache-2.0":
        raise Failure("license_policy", "license is not exactly Apache-2.0")
    if matrix["semantic_labels"] != {"P": "predicate", "S": "safeguard"}:
        raise Failure("semantic_rows", "P/S semantic meanings differ")
    rows = matrix["rows"]
    ids = [row.get("id") if type(row) is dict else None for row in rows] if type(rows) is list else []
    if ids != [row[0] for row in ROWS] or len(ids) != len(set(ids)):
        raise Failure("row_topology", "row identities, order, or uniqueness differ")
    for actual, expected in zip(rows, ROWS, strict=True):
        keys(actual, {"id", "semantic_label", "expected_result"}, "semantic_rows", f"row {expected[0]}")
        if actual["semantic_label"] != expected[1]:
            raise Failure("semantic_rows", f"row {expected[0]} semantic label differs")
        if type(actual["expected_result"]) is not type(expected[2]) or actual["expected_result"] != expected[2]:
            raise Failure("expected_red", f"row {expected[0]} expected result differs")
    if matrix["red_result"] != list(RED):
        raise Failure("expected_red", "literal RED result is not 46/14/5/D14")
    if matrix["non_email_rule_ids"] != [row[0] for row in ROWS]:
        raise Failure("g18_original_bytes", "non-email rule identities or order differ")
    eligible = matrix["eligible_email"]
    keys(eligible, {"utf8_hex", "byte_length", "sha256"}, "g18_original_bytes", "eligible-email fixture")
    if eligible != {"utf8_hex": EMAIL_HEX, "byte_length": len(EMAIL), "sha256": EMAIL_SHA}:
        raise Failure("g18_original_bytes", "eligible-email byte identity differs")
def build_context(matrix: bytes, helper: bytes, nonce: str | None = None) -> dict[str, str]:
    return {"schema": CONTEXT_SCHEMA, "run_nonce": nonce or secrets.token_hex(16), "matrix_sha256": digest(matrix), "helper_sha256": digest(helper), "eligible_email_sha256": EMAIL_SHA}
def run_helper(helper: Path, matrix: Path, raw: str, fault: str) -> tuple[int, Any]:
    command = [sys.executable, str(helper), "--matrix", str(matrix), "--context-json", raw, "--fault", fault]
    try:
        completed = subprocess.run(command, check=False, capture_output=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Failure("helper_execution", f"helper did not complete: {exc}") from exc
    try:
        return completed.returncode, load(completed.stdout, "helper output")
    except Failure as exc:
        raise Failure("helper_execution", exc.detail) from exc
def validate_output(output: Any, ctx: dict[str, str]) -> None:
    keys(output, {"schema", "ok", "red_result", "row_results", "d12_execution_receipts", "g18_original_byte_receipts"}, "helper_output", "helper output")
    if output["schema"] != OUTPUT_SCHEMA or output["ok"] is not True:
        raise Failure("helper_output", "helper did not emit successful typed output")
    expected_rows = [{"row_id": row_id, "actual_result": result} for row_id, _label, result in ROWS]
    if output["red_result"] != list(RED) or output["row_results"] != expected_rows:
        raise Failure("expected_red", "observed aggregate or per-row RED result differs")
    d12 = [{"row_id": "D12", "run_nonce": ctx["run_nonce"], "input_sha256": EMAIL_SHA, "control_flow": "row_callback"}]
    if output["d12_execution_receipts"] != d12:
        raise Failure("d12_execution", "D12 callback receipt is absent or differs")
    receipts = [{"rule_id": row[0], "run_nonce": ctx["run_nonce"], "byte_length": len(EMAIL), "input_sha256": EMAIL_SHA, "control_flow": "before_rule_evaluation"} for row in ROWS]
    if output["g18_original_byte_receipts"] != receipts:
        raise Failure("g18_original_bytes", "original bytes did not reach every exact rule before evaluation")
def verify(matrix_path: Path, freeze_path: Path, helper_path: Path, raw: str | None, fault: str) -> dict[str, Any]:
    try:
        matrix_bytes, freeze_bytes, helper_bytes = matrix_path.read_bytes(), freeze_path.read_bytes(), helper_path.read_bytes()
        matrix, freeze = load(matrix_bytes, "matrix"), load(freeze_bytes, "freeze record")
        validate_matrix(matrix)
        if digest(freeze_bytes) != EXPECTED_FREEZE_SHA256:
            raise Failure("freeze_binding", "freeze-record bytes differ")
        keys(freeze, {"schema", "license_spdx", "artifacts"}, "freeze_binding", "freeze record")
        if freeze["schema"] != FREEZE_SCHEMA or freeze["license_spdx"] != "Apache-2.0" or type(freeze["artifacts"]) is not list or len(freeze["artifacts"]) != 2:
            raise Failure("freeze_binding", "freeze schema, license, or artifact count differs")
        artifacts = freeze["artifacts"]
        if [item.get("path") if type(item) is dict else None for item in artifacts] != [MATRIX_REL, HELPER_REL]:
            raise Failure("freeze_binding", "freeze artifact paths or order differ")
        for item, data, failure_class in zip(artifacts, (matrix_bytes, helper_bytes), ("matrix_sha256", "helper_sha256"), strict=True):
            keys(item, {"path", "byte_size", "sha256"}, "freeze_binding", "freeze artifact")
            if type(item["byte_size"]) is not int or type(item["sha256"]) is not str or item["byte_size"] != len(data) or item["sha256"] != digest(data):
                raise Failure(failure_class, f"{failure_class.removesuffix('_sha256')} bytes differ from freeze record")
        generated = build_context(matrix_bytes, helper_bytes)
        context_raw = raw if raw is not None else json.dumps(generated, sort_keys=True)
        code, output = run_helper(helper_path, matrix_path, context_raw, fault)
        if code != 0 or type(output) is not dict or output.get("ok") is not True:
            if type(output) is dict and output.get("failure_class") == "context":
                raise Failure("context", "helper rejected structured context before execution")
            raise Failure("helper_execution", "helper returned a non-zero or negative result")
        try:
            ctx = json.loads(context_raw, object_pairs_hook=strict_object)
        except (Failure, json.JSONDecodeError) as exc:
            raise Failure("context", "structured context was not uniquely parseable") from exc
        validate_output(output, ctx)
        return {"schema": SCHEMA, "ok": True, "failure_class": None, "red_result": list(RED), "row_count": len(ROWS), "non_email_rule_count": len(ROWS), "matrix_sha256": digest(matrix_bytes), "helper_sha256": digest(helper_bytes), "freeze_sha256": digest(freeze_bytes)}
    except OSError as exc:
        return {"schema": SCHEMA, "ok": False, "failure_class": "io", "detail": str(exc)}
    except Failure as exc:
        return {"schema": SCHEMA, "ok": False, "failure_class": exc.failure_class, "detail": exc.detail}
def invoke(matrix: Path, freeze: Path, helper: Path, raw: str | None = None, fault: str = "none") -> tuple[int, dict[str, Any]]:
    command = [sys.executable, str(Path(__file__).resolve()), "--matrix", str(matrix), "--freeze", str(freeze), "--helper", str(helper), "--helper-fault", fault]
    if raw is not None:
        command.extend(("--context-json", raw))
    completed = subprocess.run(command, check=False, capture_output=True, text=True, timeout=15)
    return completed.returncode, json.loads(completed.stdout)
def receipt(case_id: str, expected: str, code: int, output: dict[str, Any]) -> dict[str, Any]:
    passed = code != 0 and output.get("ok") is False and output.get("failure_class") == expected
    return {"id": case_id, "expected_failure_class": expected, "observed_failure_class": output.get("failure_class"), "verification_exit_code": code, "outcome": "fail-closed" if passed else "unexpected"}
def case(case_id: str, expected: str, sources: tuple[Path, Path, Path], mutate: Callable[[dict[str, Any]], None] | None = None, fault: str = "none", context_change: Callable[[dict[str, Any]], str] | None = None, edit_helper: bool = False) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="oss07-i2-") as temp_name:
        matrix, freeze, helper = (Path(temp_name) / name for name in ("matrix.json", "freeze.json", "audit_design.py"))
        for source, target in zip(sources, (matrix, freeze, helper), strict=True):
            shutil.copyfile(source, target)
        if mutate:
            value = copy.deepcopy(json.loads(matrix.read_bytes()))
            mutate(value)
            matrix.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")
        if edit_helper:
            helper.write_bytes(helper.read_bytes() + b"#")
        ctx = build_context(matrix.read_bytes(), helper.read_bytes(), "0123456789abcdef0123456789abcdef")
        raw = context_change(ctx) if context_change else None
        code, output = invoke(matrix, freeze, helper, raw, fault)
    return receipt(case_id, expected, code, output)
def run_mutations(matrix: Path, freeze: Path, helper: Path) -> tuple[int, dict[str, Any]]:
    sources = (matrix, freeze, helper)
    mutations = [case("semantic-label-P46", "semantic_rows", sources, lambda value: value["rows"][0].__setitem__("semantic_label", "S"))]
    for case_id, fault in (("red-46", "red-46"), ("red-14", "red-14"), ("red-5", "red-5"), ("red-D14", "red-d14")):
        mutations.append(case(case_id, "expected_red", sources, fault=fault))
    for case_id, failure_class, fault in (("d12-bypass-marker-retained", "d12_execution", "d12-bypass"), ("g18-changed-before-P46", "g18_original_bytes", "g18-change-P46"), ("g18-omit-before-S14", "g18_original_bytes", "g18-omit-S14")):
        mutations.append(case(case_id, failure_class, sources, fault=fault))
    mutations.append(case("helper-one-byte", "helper_sha256", sources, edit_helper=True))
    topology = (("row-add", lambda value: value["rows"].append({"id": "X99", "semantic_label": "P", "expected_result": 0})), ("row-remove", lambda value: value["rows"].pop()), ("row-duplicate", lambda value: value["rows"].append(copy.deepcopy(value["rows"][0]))), ("row-reorder", lambda value: value["rows"].__setitem__(slice(0, 2), list(reversed(value["rows"][:2])))))
    mutations.extend(case(case_id, "row_topology", sources, mutate) for case_id, mutate in topology)
    def changed_context(key: str, value: Any) -> Callable[[dict[str, Any]], str]:
        return lambda ctx: json.dumps(dict(ctx, **{key: value}), sort_keys=True)
    contexts: tuple[tuple[str, Callable[[dict[str, Any]], str]], ...] = (
        ("context-missing", lambda ctx: json.dumps({key: value for key, value in ctx.items() if key != "helper_sha256"}, sort_keys=True)),
        ("context-extra-unknown", changed_context("unknown", "rejected")),
        ("context-duplicate", lambda ctx: json.dumps(ctx, sort_keys=True).replace('"schema":', f'"schema": {json.dumps(ctx["schema"])}, "schema":', 1)),
        ("context-untyped", changed_context("matrix_sha256", 7)),
        ("context-prose-derived", changed_context("run_nonce", "derived from operator prose")),
        ("context-path", changed_context("path", "/tmp/rejected")),
        ("context-command", changed_context("command", "echo rejected")),
        ("context-credential", changed_context("credential", "synthetic-rejected-value")),
        ("context-user-data", changed_context("user_data", "synthetic-rejected-value")),
        ("context-expected-override", changed_context("expected_result", list(RED))),
    )
    mutations.extend(case(case_id, "context", sources, context_change=change) for case_id, change in contexts)
    control_code, control = invoke(matrix, freeze, helper)
    control_passed = control_code == 0 and control.get("ok") is True and control.get("red_result") == list(RED)
    ok = control_passed and len(mutations) == 23 and all(item["outcome"] == "fail-closed" for item in mutations)
    summary = {"schema": SCHEMA, "ok": ok, "control": {"verification_exit_code": control_code, "outcome": "pass" if control_passed else "unexpected", "red_result": control.get("red_result")}, "mutations": mutations, "mutation_count": len(mutations), "fail_closed_count": sum(item["outcome"] == "fail-closed" for item in mutations)}
    return (0 if ok else 1), summary
def main() -> int:
    root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", type=Path, default=root / MATRIX_REL)
    parser.add_argument("--freeze", type=Path, default=root / FREEZE_REL)
    parser.add_argument("--helper", type=Path, default=root / HELPER_REL)
    parser.add_argument("--context-json")
    parser.add_argument("--helper-fault", default="none")
    parser.add_argument("--run-mutations", action="store_true")
    args = parser.parse_args()
    if args.run_mutations:
        code, output = run_mutations(args.matrix, args.freeze, args.helper)
    else:
        output = verify(args.matrix, args.freeze, args.helper, args.context_json, args.helper_fault)
        code = 0 if output["ok"] else 1
    print(json.dumps(output, indent=2, sort_keys=True))
    return code
if __name__ == "__main__":
    sys.exit(main())
