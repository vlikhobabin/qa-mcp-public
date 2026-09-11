"""Product-neutral public contracts for qa-mcp execution extensions."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol, runtime_checkable


class OperationKind(str, Enum):
    """Primitive families implemented by local or downstream executors."""

    READ = "read"
    WRITE = "write"
    LIFECYCLE = "lifecycle"
    DISPLAY = "display"


class OperationVerdict(str, Enum):
    """One shared result taxonomy for MCP and scenario operation paths."""

    SUCCESS = "success"
    BLOCKED = "blocked"
    AMBIGUOUS = "ambiguous"
    FAILURE = "failure"


@dataclass(frozen=True)
class TargetIdentity:
    """Secret-free logical target identity owned by qa-mcp callers."""

    logical_id: str
    fingerprint: str = ""
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class SessionIdentity:
    """Generic executor session identity with an optional immutable target."""

    session_id: str
    target: TargetIdentity | None = None
    sequence: int = 0


@dataclass(frozen=True)
class ArtifactReference:
    """Reference to retained evidence without imposing a product artifact store."""

    artifact_id: str
    media_type: str = "application/octet-stream"
    sha256: str = ""
    path: str = ""
    sensitivity: str = "internal"


@dataclass(frozen=True)
class OperationError:
    code: str
    message: str
    retryable: bool = False
    details: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
            "retryable": self.retryable,
        }
        if self.details:
            payload["details"] = dict(self.details)
        return payload


@dataclass(frozen=True)
class OperationRequest:
    kind: OperationKind
    name: str
    arguments: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OperationResult:
    request: OperationRequest
    verdict: OperationVerdict
    value: Any = None
    error: OperationError | None = None
    artifacts: tuple[ArtifactReference, ...] = ()
    provenance: Any = None

    @classmethod
    def success(cls, request: OperationRequest, *, value: Any = None) -> "OperationResult":
        return cls(request=request, verdict=OperationVerdict.SUCCESS, value=value)

    @classmethod
    def blocked(
        cls,
        request: OperationRequest,
        *,
        code: str,
        message: str,
        details: Mapping[str, Any] | None = None,
    ) -> "OperationResult":
        return cls(
            request=request,
            verdict=OperationVerdict.BLOCKED,
            error=OperationError(code=code, message=message, details=details or {}),
        )

    @classmethod
    def failure(
        cls,
        request: OperationRequest,
        *,
        code: str,
        message: str,
        retryable: bool = False,
    ) -> "OperationResult":
        return cls(
            request=request,
            verdict=OperationVerdict.FAILURE,
            error=OperationError(code=code, message=message, retryable=retryable),
        )

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "operation": self.request.name,
            "kind": self.request.kind.value,
            "verdict": self.verdict.value,
        }
        if self.value is not None:
            payload["value"] = self.value
        if self.error is not None:
            payload["error"] = self.error.to_dict()
        if self.artifacts:
            payload["artifacts"] = [
                {key: value for key, value in artifact.__dict__.items() if key != "path" or value}
                for artifact in self.artifacts
            ]
        if self.provenance is not None:
            payload["provenance"] = self.provenance.to_dict()
        return payload


@runtime_checkable
class QAExecutor(Protocol):
    """Neutral primitive executor implemented by local and downstream runtimes."""

    name: str

    def execute(
        self,
        request: OperationRequest,
        *,
        target: TargetIdentity | None,
        session: SessionIdentity | None,
    ) -> OperationResult: ...
