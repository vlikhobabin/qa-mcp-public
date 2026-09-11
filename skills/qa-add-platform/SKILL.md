---
name: qa-add-platform
description: Add qa-mcp support for a new 1C platform version. Use when the user asks to «добавить поддержку <версия>» / "add support for platform <x.y.z.w>", or invokes `$qa-add-platform <version>`. Classifies the build (probe), runs the deterministic validate+bless path for a wire-compatible same-family build, or routes a new-family / RED build to the headless-Codex capture pipeline.
---

# qa-add-platform

> Tracked source of truth: `skills/qa-add-platform/SKILL.md`. It is delivered to agents by a
> per-machine symlink `.codex/skills/qa-add-platform -> ../../skills/qa-add-platform` (the `.codex`
> tree is git-ignored / machine-rendered). Edit this file, not the symlink.

## Purpose

Turn "add support for 1C platform version X" into a systematic, mostly-deterministic
process. After the multi-version architecture (epic 112) the wire protocol is
version-generic — the live version string is injected at runtime from
`PLATFORM_ROOT` / `QA_MCP_PLATFORM_VERSION`. So adding a build of an already-supported
family is a **data + config + validate** operation with no protocol-code change; only a
genuinely new wire contour needs capture/code work.

This skill is the entry point and router. The engine is `python -m qa_mcp.platform_support`
(see `docs/platform-support.md`). Run from the qa-mcp repo root, on the dev box, with the
lab up (Apache on :8316, Xvfb available, the platform installed under
`/opt/1cv8/x86_64/<version>/`).

Invoke from Codex with the qa-mcp launcher (a plain `codex` here does not load these skills):
`./bin/codex exec '$qa-add-platform <version>'` (unattended) or interactive `./bin/codex`.

## Operating mode

Work in the foreground as the active agent for the Case-A (deterministic) path — there is
nothing to judge, only an exit code to read. Hand the Case-B (development) path to headless
Codex via `scripts/deliver-platform-support.sh`. Runs are **sequential**: platform work
monopolizes the TestClient (port 15381), Apache and the Xvfb display — never run two at once.

## Procedure

### 1. Classify (always)

```bash
python -m qa_mcp.platform_support probe <version> --json
```

Read `case`:

| case | meaning | go to |
| --- | --- | --- |
| `already` | build is the manifest baseline or already in `compatible_platform_versions` | done — report, nothing to do |
| `A` | supported family, protocol data available, not yet blessed → wire-compatible bump | §2 (deterministic) |
| `B` | unsupported family (a new wire contour) | §3 (development / Codex) |
| `unknown` | not a recognizable `x.y.z.w` | ask the user for a valid version |

### 2. Case A — validate then bless (deterministic, no code)

```bash
python -m qa_mcp.platform_support validate <version>        # boots /TESTCLIENT, runs live-regression --include-write
```

* **GREEN** (exit 0): all required checks passed (incl. the UI→DB write roundtrip). Then:
  ```bash
  python -m qa_mcp.platform_support bless <version> --notes "validated GREEN <date>"
  ```
  which appends the build to `config/protocol-capture-manifest-<family>.json`. Confirm with
  `python -m qa_mcp.regression.versioning --platform-root /opt/1cv8/x86_64/<version>` (expect OK).
  Then publish per project rules — update the supported-build list in `README.md`, `delivery/*`,
  and (for a new family only) keep `delivery/bootstrap.ps1` in parity — and make a scoped commit
  (via `$opsx-pub` on a card, or a direct scoped commit). **Commit/push only when the user asks.**
* **RED** (exit 1): the wire moved (or a real regression). Do NOT bless. Read
  `runtime/platform-support/<version>/verdict.json` (`failed_checks`, `drift`) and escalate to §3.

Batch form for several installed builds: `python -m qa_mcp.platform_support matrix --validate`.

### 3. Case B — new family / RED → headless-Codex capture pipeline

This is real development (stand up the lab, capture the moved frames per
`docs/capture-refresh-runbook.md`, declare the family in `SUPPORTED_VERSION_KEYS`, add any
version-conditional code, bundle assets, stamp the manifest, tests, release). It is driven as an
OpenSpec board card through `$opsx-deliver` in unattended Codex:

1. Seed a card in `openspec/board/1.backlog/` from
   `docs/platform-support-new-family-card-template.md` (fill the version/family and the RED
   evidence — the failed checks and the drift verdict).
2. Deliver it unattended:
   ```bash
   scripts/deliver-platform-support.sh <card.md>        # DRY_RUN=1 to preview the codex command
   ```
   The driver composes a CODEX_HOME (qa-mcp `.codex/config.toml` + `.codex/skills` + operator auth)
   and runs `$opsx-deliver <card>` (ff → do → review → pub) with `--sandbox danger-full-access
   -c approval_policy=never`. `$opsx-deliver` includes `pub`, so this **commits and pushes**.

Caveat: a genuine wire move needs a live capture step (tcpdump + Vanessa TestManager, licensed
user, real `$HOME`) that headless Codex cannot perform. Structure the card so the capture is
pre-bundled or its `$opsx-do` calls the lab tooling; otherwise Codex will correctly stop there and
you finish the capture by hand, then re-run validate.

## Guardrails

* Never bless a RED build. `bless` itself refuses unless a GREEN verdict for that version exists.
* Never edit the version-injection code for a same-family build — it is already generic.
* Keep the two family-policy copies in sync (Python `_bundled/__init__.py` `SUPPORTED_VERSION_KEYS`
  and PowerShell `delivery/bootstrap.ps1`); the parity test `tests/test_bootstrap_platform_selection.py`
  enforces this.
* Commit and push only when explicitly asked or via `$opsx-pub` / `$opsx-deliver`.
