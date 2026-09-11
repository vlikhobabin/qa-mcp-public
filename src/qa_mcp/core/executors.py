"""Public local and Windows-host executor adapters."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from .contracts import (
    OperationKind,
    OperationRequest,
    OperationResult,
    SessionIdentity,
    TargetIdentity,
)

OperationHandler = Callable[[OperationRequest], OperationResult | Any]
OperationKey = tuple[OperationKind, str]


class HandlerQAExecutor:
    """Small explicit primitive dispatcher used by concrete public adapters."""

    name = "handler"

    def __init__(self, handlers: Mapping[OperationKey, OperationHandler] | None = None) -> None:
        self._handlers = dict(handlers or {})

    def execute(
        self,
        request: OperationRequest,
        *,
        target: TargetIdentity | None,
        session: SessionIdentity | None,
    ) -> OperationResult:
        del target, session
        handler = self._handlers.get((request.kind, request.name))
        if handler is None:
            return OperationResult.blocked(
                request,
                code="unsupported-operation",
                message=f"executor {self.name!r} does not implement {request.kind.value}:{request.name}",
            )
        try:
            value = handler(request)
        except Exception as exc:  # adapters translate exceptions into the shared taxonomy
            return OperationResult.failure(
                request,
                code="executor-failure",
                message=f"{type(exc).__name__}: {exc}",
            )
        return value if isinstance(value, OperationResult) else OperationResult.success(request, value=value)


class LocalQAExecutor(HandlerQAExecutor):
    name = "local"


class WindowsHostQAExecutor(HandlerQAExecutor):
    name = "windows-host"
