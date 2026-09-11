## Context

The self-hosted qa-mcp release flow stages a protected Docker image, Windows
host-agent executable, host-agent installer, bootstrap script and runbooks. The
Windows host-agent installer already supports a COM worker input, but
`publish_self_hosted.sh` does not stage `ai-com-worker.exe` and `bootstrap.ps1`
does not fetch it from the manifest.

`ai-com-worker.exe` is produced by live-mcp on Windows with pywin32. qa-mcp
should treat that executable as an optional release input, not as a build target
owned by this repository.

No protocol capture, frame replay, dynamic protocol fields or Linux TestClient
runtime cleanup behavior are changed by this work.

## Goals / Non-Goals

**Goals:**

- Let release operators pass a ready `ai-com-worker.exe` into
  `tools/release/publish_self_hosted.sh`.
- Stage the worker as a normal manifest asset with a sha256 sidecar when the
  input is present.
- Preserve existing non-COM release behavior when the worker input is absent.
- Make bootstrap download, verify and hand the worker to
  `install-windows-host-agent.ps1` before the scheduled task is created.
- Cover the optional and absent-worker paths with focused offline tests.

**Non-Goals:**

- Build `ai-com-worker.exe` in qa-mcp.
- Change host-agent `/com/execute` protocol behavior.
- Run a Windows COM bridge smoke from Linux.
- Change protected image layout or bundled protocol data handling.

## Decisions

1. Keep the worker optional in `publish_self_hosted.sh`.

   Rationale: existing release users that do not need COM support should be able
   to publish the same assets as before. The absence of the worker is an
   operator-visible warning, not a hard release failure.

   Alternative considered: make `--com-worker-exe` mandatory. That would close
   the COM gap but would couple every qa-mcp release to a Windows live-mcp build
   even for non-COM installs.

2. Represent the worker as an ordinary manifest asset named
   `ai-com-worker.exe`.

   Rationale: `bootstrap.ps1` already has common manifest asset lookup,
   download and sha256 verification helpers. Reusing that path keeps worker
   verification identical to the host-agent and installer verification path.

   Alternative considered: add a dedicated top-level manifest field. That would
   require extra parsing and schema branching without adding useful semantics for
   this optional executable.

3. Pass `-ComWorkerExe` explicitly to the installer when the manifest declares
   the worker.

   Rationale: the installer can auto-discover a colocated worker, but an
   explicit argument documents the intended handoff and avoids relying on path
   heuristics if bootstrap staging changes later.

   Alternative considered: only copy the worker next to `qa-mcp-host-agent.exe`
   and rely on auto-discovery. That is compatible but less direct in testable
   bootstrap code.

## Risks / Trade-offs

- Worker executable is built outside qa-mcp -> tests can validate staging and
  bootstrap contracts, but final `/com/execute` health still needs a Windows
  smoke with the live-mcp-built binary.
- Optional worker means a release can still lack COM support -> publish output
  must warn clearly when `--com-worker-exe` is omitted.
- PowerShell manifest asset lookup currently fails closed for missing required
  assets -> bootstrap needs a non-fatal manifest-presence check before trying to
  download the optional worker.

## Migration Plan

1. Add `--com-worker-exe` to the release helper usage, argument parsing and
   staging flow.
2. Include the staged worker in sha256 sidecar generation and
   `component_manifest.py --asset` arguments only when present.
3. Add a bootstrap helper that returns whether a manifest asset exists without
   failing, then download and verify `ai-com-worker.exe` when declared.
4. Build the host-agent installer argument list so `-ComWorkerExe` is present
   only after the worker asset has been downloaded and verified.
5. Add Linux offline tests for shell syntax, manifest asset presence and
   bootstrap contract strings. Record Windows COM smoke as a deferred runtime
   verification item.

Rollback is to omit `--com-worker-exe`; release staging returns to the existing
non-COM asset set. If bootstrap sees no worker in an older manifest, it follows
the current host-agent install path.

## Open Questions

- None for implementation. The Windows COM health smoke remains an environment
  prerequisite, not a design unknown.
