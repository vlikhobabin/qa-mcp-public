"""Fresh target-profile inputs; callers own physical files and runtime contexts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _fingerprint(value: str) -> dict[str, str]:
    return {"algorithm": "sha256", "value": value}


@dataclass(frozen=True)
class TargetProfileInputs:
    root: Path
    target_kind: str = "file"
    fingerprint: str = "a" * 64
    principal: str = "principal-observed"
    evidence_policy: str = "sanitized"
    non_production_approved: bool = False

    def profile(self) -> dict[str, Any]:
        # Each call and each nested projection is independent, so tests may
        # invalidate one field without silently changing a paired observation.
        return {
            "schema": "qa-mcp.runtime-target-profile.v1",
            "binding_ref": "qa-demo",
            "target": {
                "id": "project-demo", "kind": self.target_kind,
                "fingerprint": _fingerprint(self.fingerprint),
            },
            "physical_config": {"env_file": str(self.root / "target.env")},
            "evidence": {
                "policy": self.evidence_policy, "root": str(self.root / "evidence"),
                "non_production_approved": self.non_production_approved,
            },
            "observation": {
                "target_id": "project-demo", "target_kind": self.target_kind,
                "target_fingerprint": _fingerprint(self.fingerprint),
                "effective_principal_fingerprint": _fingerprint(self.principal),
                "platform_fingerprint": _fingerprint("platform"),
                "extension_profile_fingerprint": _fingerprint("extensions"),
                "process_config_fingerprint": _fingerprint("process"),
                "security_receipt_id": "receipt-7", "binding_generation": 7,
            },
        }

    def handoff_env(self) -> dict[str, str]:
        return {
            "AI1C_RUNTIME_TARGET_ID": "project-demo",
            "AI1C_RUNTIME_TARGET_KIND": self.target_kind,
            "AI1C_RUNTIME_TARGET_FINGERPRINT": self.fingerprint,
            "AI1C_RUNTIME_TARGET_FINGERPRINT_ALGORITHM": "sha256",
            "AI1C_AGENT_PRINCIPAL_ID": "qa-agent",
            "AI1C_AGENT_EXPECTED_PRINCIPAL_FINGERPRINT": self.principal,
            "AI1C_AGENT_EXPECTED_PRINCIPAL_FINGERPRINT_ALGORITHM": "sha256",
            "AI1C_RUNTIME_TARGET_BINDING_GENERATION": "7",
            "AI1C_RUNTIME_TARGET_OBSERVATIONS": ".ai/runtime-provider-observations.json",
            "AI1C_RUNTIME_TARGET_BINDING_REF": "qa-demo",
            "AI1C_AGENT_TEST_SECURITY_RECEIPT_ID": "receipt-7",
            "QA_MCP_RUNTIME_TARGET_PROFILE": str(self.root / "profile.json"),
            "QA_MCP_RUNTIME_EVIDENCE_ALLOW_ROOT": str(self.root / "evidence"),
        }

    def write_profile(self) -> None:
        (self.root / "profile.json").write_text(json.dumps(self.profile()), encoding="utf-8")
