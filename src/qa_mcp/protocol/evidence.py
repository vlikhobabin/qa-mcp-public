"""Evidence-aware read-only protocol operation descriptors."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

from ..versioning import active_version_key


ACCEPTED_MAPPINGS_RELATIVE_PATH = (
    Path("docs")
    / "protocol-research"
    / "evidence"
    / "accepted-mappings"
    / "expanded-readonly-20260602-193802-vs-20260602-195407-probe-accepted"
    / "accepted_mappings.json"
)

def default_accepted_mappings_path(*, version: str | None = None) -> Path:
    """Bundled accepted-mappings for the active platform version family if present, else the dev-tree copy.

    The bundled copy is selected by active platform family, then mapped through the bundled protocol-data policy:
    direct-covered families use their own data, while 8.5 uses the validated 8.3 accepted mappings until a
    dedicated 8.5 bundle is populated.
    """
    from .._bundled import accepted_mappings_path as bundled_accepted_mappings  # local: _bundled is dep-free

    if version is None:
        version = active_version_key()
    bundled = bundled_accepted_mappings(version)
    if bundled.exists():
        return bundled
    return repo_root_from_package() / ACCEPTED_MAPPINGS_RELATIVE_PATH


class AcceptanceStatus(StrEnum):
    """Reviewed protocol evidence status for a read-only operation."""

    ACCEPTED = "accepted"
    PARTIAL = "partial"
    PENDING = "pending"
    INCOMPLETE_HASH = "incomplete_hash"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True)
class OperationDescriptor:
    """Package-level descriptor for a read-only TestClient protocol operation."""

    case_id: str
    query: str
    operation_family: str
    safety_class: str
    acceptance_status: AcceptanceStatus
    evidence_path: str | None = None
    accepted_normalized_hash: str | None = None
    source_capture_ids: tuple[str, ...] = ()
    probe_evidence_paths: tuple[str, ...] = ()
    unresolved_reason: str | None = None
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_accepted(self) -> bool:
        return self.acceptance_status == AcceptanceStatus.ACCEPTED

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "query": self.query,
            "operation_family": self.operation_family,
            "safety_class": self.safety_class,
            "acceptance_status": self.acceptance_status.value,
            "evidence_path": self.evidence_path,
            "accepted_normalized_hash": self.accepted_normalized_hash,
            "source_capture_ids": list(self.source_capture_ids),
            "probe_evidence_paths": list(self.probe_evidence_paths),
            "unresolved_reason": self.unresolved_reason,
            "notes": self.notes,
            "metadata": self.metadata,
        }


def repo_root_from_package() -> Path:
    return Path(__file__).resolve().parents[3]


def _repo_relative_path(path: Path, repo_root: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(repo_root.resolve())).replace("\\", "/")
    except ValueError:
        return str(resolved)


def load_accepted_mappings(path: Path | None = None) -> dict[str, dict[str, Any]]:
    """Load compact accepted-mapping evidence keyed by case id."""

    evidence_path = path or default_accepted_mappings_path()
    data = json.loads(evidence_path.read_text(encoding="utf-8-sig"))
    return {str(row["case_id"]): row for row in data.get("cases", [])}


def _accepted_descriptor(
    case_id: str,
    query: str,
    operation_family: str,
    accepted_row: dict[str, Any],
    evidence_path: Path,
    repo_root: Path,
) -> OperationDescriptor:
    return OperationDescriptor(
        case_id=case_id,
        query=query,
        operation_family=operation_family,
        safety_class="read_only",
        acceptance_status=AcceptanceStatus.ACCEPTED,
        evidence_path=_repo_relative_path(evidence_path, repo_root),
        accepted_normalized_hash=str(accepted_row["normalized_hash"]),
        source_capture_ids=tuple(str(item) for item in accepted_row.get("capture_ids", [])),
        probe_evidence_paths=tuple(str(item) for item in accepted_row.get("probe_evidence_paths", [])),
        notes="Accepted by repeated normalized hashes plus direct Python-manager probe evidence.",
        metadata={
            "request_sizes": accepted_row.get("request_sizes", []),
            "response_sizes": accepted_row.get("response_sizes", []),
        },
    )


def _unresolved_descriptor(
    case_id: str,
    query: str,
    operation_family: str,
    status: AcceptanceStatus,
    reason: str,
    notes: str,
    evidence_path: Path,
    repo_root: Path,
) -> OperationDescriptor:
    return OperationDescriptor(
        case_id=case_id,
        query=query,
        operation_family=operation_family,
        safety_class="read_only",
        acceptance_status=status,
        evidence_path=_repo_relative_path(evidence_path, repo_root),
        unresolved_reason=reason,
        notes=notes,
    )


def list_readonly_operation_descriptors(repo_root: Path | None = None) -> list[OperationDescriptor]:
    """Return reviewed read-only operations known to the package contract."""

    if repo_root is not None:
        root = repo_root
        evidence_path = root / ACCEPTED_MAPPINGS_RELATIVE_PATH
    else:
        root = repo_root_from_package()
        evidence_path = default_accepted_mappings_path()
    accepted = load_accepted_mappings(evidence_path)

    descriptors = [
        _unresolved_descriptor(
            case_id="initial-ui",
            query="initial-ui",
            operation_family="bootstrap_ui_context",
            status=AcceptanceStatus.PARTIAL,
            reason="bootstrap_context_not_promoted_as_separate_accepted_mapping",
            notes="Initial UI frames are required for later read-only queries but are not a standalone accepted mapping.",
            evidence_path=evidence_path,
            repo_root=root,
        ),
        _accepted_descriptor(
            case_id="active-window-context",
            query="active-window-context",
            operation_family="active_window_context",
            accepted_row=accepted["active-window-context"],
            evidence_path=evidence_path,
            repo_root=root,
        ),
        _accepted_descriptor(
            case_id="active-form-context",
            query="active-form-context",
            operation_family="active_form_context",
            accepted_row=accepted["active-form-context"],
            evidence_path=evidence_path,
            repo_root=root,
        ),
        _unresolved_descriptor(
            case_id="form-summary",
            query="form-summary",
            operation_family="form_summary",
            status=AcceptanceStatus.PARTIAL,
            reason="form_summary_is_supported_by_probe_but_not_a_separate_accepted_mapping",
            notes="Form summary uses the active-form/read-only element path but has no standalone accepted corpus row.",
            evidence_path=evidence_path,
            repo_root=root,
        ),
        _unresolved_descriptor(
            case_id="form-element-details",
            query="form-element-details",
            operation_family="form_element_details",
            status=AcceptanceStatus.INCOMPLETE_HASH,
            reason="accepted_probe_without_reviewed_request_hash",
            notes="Direct probe returned useful element details, but reviewed Vanessa-only request hashes are incomplete.",
            evidence_path=evidence_path,
            repo_root=root,
        ),
        _unresolved_descriptor(
            case_id="typed-input-field-readonly",
            query="form-element-details",
            operation_family="typed_input_field_readonly",
            status=AcceptanceStatus.INCOMPLETE_HASH,
            reason="accepted_probe_without_reviewed_request_hash",
            notes="Typed input is represented by current EditField details, but accepted request-hash evidence is missing.",
            evidence_path=evidence_path,
            repo_root=root,
        ),
        _unresolved_descriptor(
            case_id="form-value-read",
            query="form-value-read",
            operation_family="form_value_read",
            status=AcceptanceStatus.PARTIAL,
            reason="value_read_proven_live_but_not_a_separate_accepted_mapping",
            notes="Card 79: reads a field's LIVE data value (0x81 value mode) off an open form for "
            "effect verification on a READ; proven live on Linux, no standalone accepted corpus row yet.",
            evidence_path=evidence_path,
            repo_root=root,
        ),
    ]
    return descriptors


def get_readonly_operation_descriptor(case_id: str, repo_root: Path | None = None) -> OperationDescriptor:
    for descriptor in list_readonly_operation_descriptors(repo_root):
        if descriptor.case_id == case_id:
            return descriptor
    raise KeyError(f"Unknown read-only protocol operation descriptor: {case_id}")
