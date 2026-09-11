"""Systematic 1C-platform-version support factory (prototype).

Adding support for a new 1C platform build is, after the multi-version architecture landed (epic 112), almost
always a *data + config + validate* operation rather than code work: the wire protocol is version-generic and the
live version string is injected at runtime from ``PLATFORM_ROOT`` / ``QA_MCP_PLATFORM_VERSION``. This package turns
the manual "capture-refresh runbook" happy-path into one deterministic command that composes the pieces that
already exist:

    probe     — classify a version offline: is the family supported? is the build already blessed? case A vs B?
    validate  — boot a /TESTCLIENT on that build and run the live-regression harness → machine-readable verdict
    bless     — on GREEN, append the build to its family capture manifest (the supported-build list)
    matrix    — probe (and optionally validate) every installed /opt/1cv8/x86_64/* build → a support matrix

Two cases, per the split model:

  * **Case A** — same family, wire compatible (e.g. a new ``8.3.27.x`` build): fully deterministic here —
    ``validate`` reads GREEN/RED off the harness exit code, ``bless`` edits the family manifest. No LLM needed.
  * **Case B** — a new family or a RED validate (the wire genuinely moved): NOT handled here. That is real
    development (lab, capture, version-conditional code) and belongs in an OpenSpec card driven by headless Codex.
    ``probe`` flags it so the caller routes it there.

CLI: ``python -m qa_mcp.platform_support {probe|validate|bless|matrix} ...``.
"""

from __future__ import annotations

from .core import (
    BlessResult,
    Probe,
    ValidateVerdict,
    bless,
    installed_platforms,
    probe,
    validate,
)

__all__ = [
    "Probe",
    "ValidateVerdict",
    "BlessResult",
    "probe",
    "validate",
    "bless",
    "installed_platforms",
]
