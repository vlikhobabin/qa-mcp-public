"""Application-owned runtime state and context binding."""

from __future__ import annotations

import contextvars
import functools
import inspect
from contextlib import contextmanager
from dataclasses import FrozenInstanceError, dataclass, field
from typing import Any, Callable, Iterator, Mapping, TypeVar, cast

from qa_mcp.config import Settings, activate_application_settings

from .boundary import EvidenceLedger, _compose_operation_schemas
from .contracts import QAExecutor, SessionIdentity, TargetIdentity
from .runtime_target import (
    RuntimeTargetBindingError,
    RuntimeTargetResolution,
    validate_runtime_target_resolution,
)

F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class ApplicationContext:
    """All mutable state owned by one composed qa-mcp application."""

    settings: Settings
    executor: QAExecutor
    target: TargetIdentity | None = None
    runtime_target: RuntimeTargetResolution | None = None
    session: SessionIdentity | None = None
    attachment: Any = None
    results_log: list[dict[str, Any]] = field(default_factory=list)
    operation_schemas: Mapping[str, Any] = field(init=False)
    evidence_ledger: EvidenceLedger = field(init=False)
    _operation_boundary_guard: tuple[Any, Any] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        binding = (
            validate_runtime_target_resolution(self.runtime_target).binding
            if self.runtime_target is not None else None
        )
        if binding is not None and self.session is not None and (
            self.session.target is not binding.target
            or self.session.sequence != binding.binding_generation
        ):
            raise RuntimeTargetBindingError(
                "runtime-target-mismatch", "session",
                "session is not bound to the current runtime resolution",
            )
        self.operation_schemas = _compose_operation_schemas()
        self.evidence_ledger = EvidenceLedger(
            binding.evidence_root if binding is not None else None,
            binding.evidence_policy.value if binding is not None else "sanitized",
        )
        self._operation_boundary_guard = (self.operation_schemas, self.evidence_ledger)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in {"runtime_target", "operation_schemas", "evidence_ledger", "_operation_boundary_guard"} and name in self.__dict__:
            raise FrozenInstanceError(f"cannot assign to field '{name}'")
        object.__setattr__(self, name, value)

    def __delattr__(self, name: str) -> None:
        if name in {"runtime_target", "operation_schemas", "evidence_ledger", "_operation_boundary_guard"}:
            raise FrozenInstanceError(f"cannot delete field '{name}'")
        object.__delattr__(self, name)


_ACTIVE_CONTEXT: contextvars.ContextVar[ApplicationContext | None] = contextvars.ContextVar(
    "qa_mcp_application_context",
    default=None,
)
_DEFAULT_CONTEXT: ApplicationContext | None = None


def set_default_application_context(context: ApplicationContext) -> None:
    global _DEFAULT_CONTEXT
    _DEFAULT_CONTEXT = context


def current_application_context() -> ApplicationContext:
    context = _ACTIVE_CONTEXT.get() or _DEFAULT_CONTEXT
    if context is None:
        raise RuntimeError("qa-mcp application context has not been configured")
    return context


@contextmanager
def activate_application_context(context: ApplicationContext) -> Iterator[ApplicationContext]:
    token = _ACTIVE_CONTEXT.set(context)
    with activate_application_settings(context.settings):
        try:
            yield context
        finally:
            _ACTIVE_CONTEXT.reset(token)


def bind_application_context(
    fn: F,
    context: ApplicationContext,
    *,
    argument_defaults: Mapping[str, Any] | None = None,
    hidden_arguments: Mapping[str, Any] | None = None,
    before_call: Callable[[], Any | None] | None = None,
) -> F:
    """Return a callable bound to one application context and its defaults.

    ``argument_defaults`` replaces defaults in both the exposed signature and
    omitted direct calls. ``hidden_arguments`` removes provider-owned inputs
    from the exposed signature and injects them inside the active context.
    ``before_call`` can return a public refusal before those hidden callbacks
    are evaluated.
    """

    signature = inspect.signature(fn)
    resolved_defaults = {
        name: value
        for name, value in (argument_defaults or {}).items()
        if name in signature.parameters
        and signature.parameters[name].default is not inspect.Parameter.empty
    }
    resolved_hidden = {
        name: value for name, value in (hidden_arguments or {}).items()
        if name in signature.parameters
    }
    bound_signature = signature.replace(
        parameters=[
            parameter.replace(default=resolved_defaults[parameter.name])
            if parameter.name in resolved_defaults
            else parameter
            for parameter in signature.parameters.values()
            if parameter.name not in resolved_hidden
        ]
    )

    def with_defaults(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
        supplied = signature.bind_partial(*args, **kwargs).arguments
        if set(supplied) & set(resolved_hidden):
            raise TypeError("provider-owned argument cannot be supplied")
        return {
            **{name: value for name, value in resolved_defaults.items() if name not in supplied},
            **{
                name: value() if callable(value) else value
                for name, value in resolved_hidden.items()
            },
            **kwargs,
        }

    if inspect.iscoroutinefunction(fn):
        @functools.wraps(fn)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            with activate_application_context(context):
                refused = before_call() if before_call is not None else None
                if refused is not None:
                    return refused
                return await fn(*args, **with_defaults(args, kwargs))

        async_wrapper.__annotations__ = dict(getattr(fn, "__annotations__", {}))
        async_wrapper.__signature__ = bound_signature  # type: ignore[attr-defined]
        return cast(F, async_wrapper)

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        with activate_application_context(context):
            refused = before_call() if before_call is not None else None
            if refused is not None:
                return refused
            return fn(*args, **with_defaults(args, kwargs))

    wrapper.__annotations__ = dict(getattr(fn, "__annotations__", {}))
    wrapper.__signature__ = bound_signature  # type: ignore[attr-defined]
    return cast(F, wrapper)
