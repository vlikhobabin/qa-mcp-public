## Context

The final gate must exercise the exact Git-visible source without ignored auth,
runtime evidence, local captures or workspace configuration. Because the payload
is uncommitted until review, `git archive HEAD` alone is insufficient during
delivery; the verifier must construct an equivalent snapshot from Git-visible
tracked/untracked paths without copying `.git` or ignored state.

## Goals / Non-Goals

**Goals:**

- Create one owned temporary source snapshot from the reviewable tree.
- Build sdist/wheel, inspect metadata/imports and run focused readiness tests.
- Prove no ignored/runtime/auth input was copied.
- Run the full repository-declared offline floor before review and publication.

**Non-Goals:**

- Clone a private remote, test public release URLs or publish artifacts.
- Exercise Docker daemon, Windows executables, 1C or TestClient.

## Decisions

1. The snapshot command uses `git ls-files --cached --others
   --exclude-standard`, rejects staged/unmerged states, copies only those paths
   to `tempfile.TemporaryDirectory`, and asserts `.git`, `.runtime`, `runtime`
   payloads beyond tracked placeholders and local env/auth files are absent.
2. Build uses `uv build --offline` in the snapshot. Dependency installation is
   proven separately by locked `uv sync --offline --extra dev`; both consume
   only the public lock plus already-cached public packages and no credential.
3. Snapshot smoke parses policy/provenance, imports `qa_mcp` from source, runs
   focused readiness pytest and inspects wheel/sdist license metadata/files.
4. Full-suite evidence is retained outside the snapshot under ignored
   `.runtime/changerail/evidence/`; the tool emits only concise JSON summary.

## Risks / Trade-offs

- [Risk] Local public-package cache masks network availability. -> This card
  proves credential-free locked/offline reproducibility; OSS-08 owns anonymous
  network release/clone evidence.
- [Risk] Working-tree snapshot differs from future commit. -> Review verdict
  fingerprint/tree SHA and publish staged scope bind the exact bytes.
- [Risk] Copying ignored state leaks secrets. -> Source paths come only from
  Git exclude-visible enumeration and are asserted against denylisted roots.

## Migration Plan

Add RED tests, implement snapshot mode, run focused then full gates, sync specs
and archive. Temporary output is always deleted; no deployment rollback exists.

## Capture, Replay And Cleanup

No protocol capture or replay is used. The only dynamic fields are the owned
temporary root and build filenames. Cleanup deletes only the temporary root on
success, failure or interruption.

## Open Questions

- none.
