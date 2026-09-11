# Host-agent: server-side argv/mutation-policy enforcement + concurrency cap + token scoping

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- Delivery-system audit 2026-07-06 (5-agent parallel audit). Canonical report (root repo):
  `docs/audits/delivery-system-audit-2026-07-06.md` -> findings **S3a** and **H9**.

## Problem
The Windows host-agent (`qa-mcp/host-agent/windows-display-agent/`) executes commands on a developer
workstation and trusts any token-holder with workstation-level power. It did not re-enforce the
mutation-safety policy server-side, and had no concurrency cap.

- **S3a -- argv is verbatim; policy is cosmetic.** `platform_exec.go:30-132,266-270` passed
  `platformExecuteRequest.Argv []string` verbatim to `exec.Command`. The only allowlist was the
  executable NAME (`ibcmd`/`designer`/`1cv8`/`1cv8c`); argv validation was only "no NUL byte".
  `validatePlatformPolicy:106-123` checked that `operation`/`mutation_class` were valid enum strings
  and that `operator_intent` was non-empty for `execute`, but it did not compare the declared
  `mutation_class` against the actual argv. So `{"operation":"platform_command_execute",
  "mutation_class":"read_only","operator_intent":"x","argv":[<destructive>]}` was accepted, and `cwd`
  was attacker-chosen. admin-mcp's read-only/plan-first policy lived only in the Python client and was
  bypassable by a direct HTTP call. `1cv8 DESIGNER /Execute <attacker.epf>` could run arbitrary
  external-data-processor code as the workstation user.
- **H9 -- no concurrency / request cap -> subprocess-exhaustion DoS.** `main.go:406` served
  goroutine-per-conn; the only limiter was `failureLimiter` (5/min per IP) and it triggered only on
  failed auth (`main.go:98-104,313-341`). A valid-token caller had no rate/concurrency limit; each
  `/platform/execute`, `/com/execute`, `/agent/complete` could spawn a subprocess up to 600s. A
  malicious container could fire thousands concurrently -> unbounded `ibcmd`/`designer`/`codex`/
  COM-worker processes pinned up to 10 min each. `failureLimiter` also never evicted empty per-IP keys.

## Recommendation
- For `platform_command_execute`, validate argv server-side against the declared `mutation_class`
  (reject a mutating argv declared read-only), or accept only a structured, host-rendered command
  template rather than raw argv.
- Add an in-flight concurrency semaphore across the exec endpoints (and/or a per-token token-bucket).
- Evict stale `failureLimiter` entries.
- DECISION / cross-ref: per-capability token scoping is deferred from this card; the E2E-recipe
  bind/token hardening is the root card `audit-e2e-recipe-hardening`; the COM `progId`/infobase
  allowlist is the live-mcp card `audit-com-worker-progid-and-timeout`.

## Acceptance Criteria
- [x] `/platform/execute` validates argv against the declared `mutation_class` server-side. Added a Go test where a `read_only`-declared `designer /Execute` request is rejected and no exec occurs.
- [x] Positive Go test: correctly-declared read-only `ibcmd config generation-id` still passes.
- [x] In-flight concurrency semaphore caps simultaneous exec subprocesses; tests show N+1 `/agent/complete`, `/com/execute`, and `/platform/execute` requests are throttled before spawn.
- [x] `failureLimiter` evicts stale entries; unit-tested.
- [x] Existing host-agent and suite tests pass.

## Scope
- In scope: `qa-mcp/host-agent/windows-display-agent/platform_exec.go`, `main.go` (limiter +
  semaphore), related tests.
- Out of scope: the E2E recipe (root card); the COM worker progId/infobase allowlist (live-mcp card);
  per-capability host-agent token scoping.

## Affected Repositories
- qa-mcp. Cross-ref: root `audit-e2e-recipe-hardening`, live-mcp `audit-com-worker-progid-and-timeout`.

## Change Set
- `harden-host-agent-exec-authz` -> `openspec/changes/archive/2026-07-06-harden-host-agent-exec-authz/`

## Change 1: `harden-host-agent-exec-authz`

### Result
Implemented server-side platform argv mutation classification, shared in-process exec capacity limiting, and failed-auth limiter stale-key pruning. Updated host-agent docs and synced `qa-mcp-windows-host-agent-security`.

### Archive
- `openspec/changes/archive/2026-07-06-harden-host-agent-exec-authz/`

### Evidence
- `.artifacts/openspec/harden-host-agent-exec-authz/2026-07-06T134428Z/go-test-host-agent.txt`
- `.artifacts/openspec/harden-host-agent-exec-authz/2026-07-06T134428Z/pytest-full.txt`
- `.artifacts/openspec/harden-host-agent-exec-authz/2026-07-06T134428Z/pytest-smoke.txt`
- `.artifacts/openspec/harden-host-agent-exec-authz/2026-07-06T134428Z/source-of-truth-drift-fallback.txt`
- `.artifacts/openspec/harden-host-agent-exec-authz/2026-07-06T134428Z/matrix-archive-gate.json`
- `.artifacts/opsx-evidence/audit-host-agent-server-side-authz/2026-07-06T134428Z/opsx-evidence-index.json`

## Related
- root repo: `docs/audits/delivery-system-audit-2026-07-06.md`
- `host-agent/windows-display-agent/platform_exec.go`
- `host-agent/windows-display-agent/main.go`
- `host-agent/windows-display-agent/agent_cli.go`
- `host-agent/windows-display-agent/com_exec.go`
- `host-agent/windows-display-agent/main_test.go`
- `host-agent/README.md`
- `openspec/specs/qa-mcp-windows-host-agent-security/spec.md`
- `openspec/changes/archive/2026-07-06-harden-host-agent-exec-authz/`

## Verify
- `go test ./...` from `host-agent/windows-display-agent` - passed.
- `openspec validate harden-host-agent-exec-authz --strict` - passed before archive.
- `openspec validate qa-mcp-windows-host-agent-security --strict` - passed after spec sync.
- `openspec validate --all` - passed.
- `git diff --check` - passed.
- `uv run --with pytest --with pyyaml pytest` - 708 passed.
- `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/check_suite_source_of_truth_drift.py` - passed; component-local `scripts/check_suite_source_of_truth_drift.py` is absent.
- `uv run --with pytest --with pyyaml pytest -m smoke` - 2 passed.

## Archive
- `openspec/changes/archive/2026-07-06-harden-host-agent-exec-authz/`

## Result
Implemented, archived, and committed for publish. Push target: `origin/main`.

## Next
- none

## Log
- 2026-07-06 card created from the delivery-system audit (findings S3a, H9).
- 2026-07-06T13:44:28Z `$opsx-ff` created `harden-host-agent-exec-authz` artifacts and moved the card to `2.todo`.
- 2026-07-06T13:56:28Z `$opsx-do` implemented host-agent hardening, synced specs, archived `harden-host-agent-exec-authz`, and moved the card to `4.done`.
- 2026-07-06T14:01:24Z `$opsx-pub` committed the scoped card changes for push to `origin/main`.
