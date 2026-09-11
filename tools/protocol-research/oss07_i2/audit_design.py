#!/usr/bin/env python3
"""Emit hash-bound observations for the OSS-07-I2 offline design matrix."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any
CONTEXT_SCHEMA = "qa-mcp.oss-07-i2.helper-context.v1"
OUTPUT_SCHEMA = "qa-mcp.oss-07-i2.helper-output.v1"
CONTEXT_KEYS = ("schema", "run_nonce", "matrix_sha256", "helper_sha256", "eligible_email_sha256")
RESULTS: dict[str, int | str] = {"P46": 46, "S14": 14, "D12": 5, "G18": "D14"}
EMAIL = b"eligible@example.invalid"
FAULTS = {"none", "red-46", "red-14", "red-5", "red-d14", "d12-bypass", "g18-change-P46", "g18-omit-S14"}
class ContextError(ValueError):
    """The typed helper context was not admitted."""
def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContextError(f"duplicate context key: {key}")
        result[key] = value
    return result
def context(raw: str, matrix: bytes, helper: bytes) -> dict[str, str]:
    try:
        value = json.loads(raw, object_pairs_hook=strict_object)
    except (json.JSONDecodeError, ContextError) as exc:
        raise ContextError(str(exc)) from exc
    if type(value) is not dict or set(value) != set(CONTEXT_KEYS):
        raise ContextError("context keys differ from the typed allowlist")
    if any(type(value[key]) is not str for key in CONTEXT_KEYS):
        raise ContextError("every context field must be a string")
    if value["schema"] != CONTEXT_SCHEMA or re.fullmatch(r"[0-9a-f]{32}", value["run_nonce"]) is None:
        raise ContextError("context schema or nonce format differs")
    expected = {"matrix_sha256": digest(matrix), "helper_sha256": digest(helper), "eligible_email_sha256": digest(EMAIL)}
    if any(re.fullmatch(r"[0-9a-f]{64}", value[key]) is None or value[key] != wanted for key, wanted in expected.items()):
        raise ContextError("context digest differs from observed bytes")
    return value
def execute(matrix: dict[str, Any], ctx: dict[str, str], fault: str) -> dict[str, Any]:
    if fault not in FAULTS:
        raise ValueError(f"unsupported test fault: {fault}")
    rows, d12, g18 = [], [], []
    changed = {"red-46": ("P46", 47), "red-14": ("S14", 15), "red-5": ("D12", 6), "red-d14": ("G18", "D15")}
    for row in matrix["rows"]:
        row_id, input_bytes = row["id"], EMAIL
        if fault == "g18-change-P46" and row_id == "P46":
            input_bytes = b"changed@example.invalid"
        if not (fault == "g18-omit-S14" and row_id == "S14"):
            g18.append({"rule_id": row_id, "run_nonce": ctx["run_nonce"], "byte_length": len(input_bytes), "input_sha256": digest(input_bytes), "control_flow": "before_rule_evaluation"})
        actual = changed[fault][1] if fault in changed and changed[fault][0] == row_id else RESULTS[row_id]
        rows.append({"row_id": row_id, "actual_result": actual})
        if row_id == "D12" and fault != "d12-bypass":
            d12.append({"row_id": row_id, "run_nonce": ctx["run_nonce"], "input_sha256": digest(input_bytes), "control_flow": "row_callback"})
    return {"schema": OUTPUT_SCHEMA, "ok": True, "red_result": [row["actual_result"] for row in rows], "row_results": rows, "d12_execution_receipts": d12, "g18_original_byte_receipts": g18}
def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--context-json", required=True)
    parser.add_argument("--fault", default="none")
    args = parser.parse_args()
    try:
        matrix_bytes, helper_bytes = args.matrix.read_bytes(), Path(__file__).read_bytes()
        output = execute(json.loads(matrix_bytes), context(args.context_json, matrix_bytes, helper_bytes), args.fault)
    except (ContextError, OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        output = {"schema": OUTPUT_SCHEMA, "ok": False, "failure_class": "context", "detail": str(exc)}
        print(json.dumps(output, sort_keys=True))
        return 2
    print(json.dumps(output, sort_keys=True))
    return 0
if __name__ == "__main__":
    sys.exit(main())
