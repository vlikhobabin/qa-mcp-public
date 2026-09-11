# Native runtime checks

Place future pytest-based real TestClient checks in `linux/` or `windows/`.
These directories are separate from hermetic product tests and local subprocess
integration. No live 1C pytest test is currently registered here.

Use the explicit `live-linux` or `live-windows` lane only after target-specific
authorization and preflight, with `--qa-live-authorized`. Retain target identity,
preflight and recovery evidence. The runner prints lane and per-test start/end
events; an empty live lane is a runtime gap, not a passing qualification.

Existing native Windows Go tests remain under `host-agent/windows-display-agent/`.
Their JSON run/pass/fail/skip events and actual Windows evidence are distinct
from Linux offline pytest and cross-compilation.
