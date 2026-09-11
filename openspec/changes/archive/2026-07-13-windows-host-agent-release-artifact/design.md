## Context

`publish_self_hosted.sh` currently contains an inline `GOOS=windows go build`,
while `install-windows-host-agent.ps1` defaults to an ignored executable beside
the source and tells operators to build it manually when absent. That permits a
stale local file to look deliverable and leaves T4 without a host-agent-only
artifact contract.

The release publisher already signs `manifest.json` with minisign and includes
asset sha256 values. This change does not invent a second signing mechanism; it
adds a reproducible verified build bundle that the signed publisher stages.

## Goals / Non-Goals

**Goals:**

- one command produces the Windows amd64 GUI artifact and provenance;
- verify current source markers before staging or installation;
- tie executable bytes to source fingerprint, revision and Go settings;
- make identical clean source/toolchain builds deterministic;
- reuse the contract in the full signed release path.

**Non-Goals:**

- commit the generated executable to Git;
- publish or activate a self-hosted release during this change;
- add Authenticode code signing (the release manifest's detached signature is
  the current download trust anchor);
- install or run the executable on a Windows station in offline verification.

## Decisions

### Python builder owns generation and verification

`tools/release/windows_host_agent_artifact.py build` runs Go with fixed
`GOOS=windows`, `GOARCH=amd64`, `CGO_ENABLED=0`, `-trimpath`, VCS build metadata
and `-H windowsgui`. It writes to a caller-selected or ignored default directory
using stable filenames and creates both a sha sidecar and JSON manifest.

The same tool's `verify` mode works on an existing bundle without rebuilding.
This keeps publisher and CI behavior identical and avoids parsing release shell
logic in multiple places.

### Source fingerprint covers build inputs

The manifest records HEAD, dirty state and a deterministic SHA-256 over Go
source, `go.mod` and `go.sum`. Release builds reject dirty inputs by default;
tests may opt in explicitly while the delivery diff is uncommitted. The
fingerprint makes a dirty development build honest instead of mislabeling it as
the clean HEAD.

### Binary verification is structural and capability-specific

The verifier parses the PE COFF machine and optional-header subsystem directly,
uses `go version -m` for Go/VCS settings, and scans bounded binary bytes for the
exact required CLI/contract markers for bridge registration, BSL supervision
and TestClient launch. It does not execute the Windows binary on Linux.

### Signed release remains the remote trust path

The host-only bundle has sha/provenance for local handoff. Public installation
still downloads the executable through `bootstrap.ps1`, after verifying the
detached signed component manifest and its asset digest. Authenticode would be
a separate release-security change.

## Risks / Trade-offs

- [Go version changes the digest] → Record toolchain version/settings; require
  equality only for identical source and toolchain.
- [Strings survive but behavior regresses] → Keep Go unit/runtime tests; marker
  verification prevents stale feature omission, not semantic proof by itself.
- [Dirty build is mislabeled] → Reject by default and record source fingerprint
  when explicit `--allow-dirty` is used for local delivery verification.
- [Publisher and standalone builder drift] → Publisher invokes the same tool
  and stages its verified output.

## Migration Plan

1. Run the host-agent artifact builder from a clean qa-mcp checkout.
2. Pass its executable to T4 or let the self-hosted publisher build it through
   the same contract.
3. Install only via explicit `-ExePath` or signed release bootstrap.
4. Stop treating the ignored adjacent executable as a shipped asset.

Rollback restores the publisher's inline build, but no generated bundle is
committed or remotely activated by this change.

## Open Questions

Authenticode signing is intentionally separate; the current self-hosted trust
model signs the manifest out of band with minisign.
