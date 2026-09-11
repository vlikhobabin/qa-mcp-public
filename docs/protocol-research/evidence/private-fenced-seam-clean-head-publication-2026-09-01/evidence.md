# Private fenced-seam clean-HEAD publication evidence

## Safety boundary

This evidence is offline and privacy-safe. No Windows binary was executed; no
1C process, endpoint, target or real configuration was accessed; no live retry
or confirmation occurred. The evidence contains only repository identities,
closed source counts, test/build outcomes and artifact hashes.

## Clean-HEAD RED

The immutable baseline was
`875650a28c838580eb0b2b7516ddf7c274d8cb3d`; before the successor card was
materialized, `HEAD`, local `origin/main` and live GitHub `main` all matched it
and the working tree was empty.

A bounded `git grep` across the seven I5-owned paths returned zero occurrences
for each absent family:

- `hiddenDirectFencedSample`: 0
- `observeHiddenDirectFencedSample`: 0
- `observeHiddenDirectWindowsFencedSample`: 0
- `hiddenDirectPreReceiptDiagnostic`: 0

Extracting only `observeHiddenDirectInWorker` from the baseline tree returned
exactly two `inventoryHiddenWindowIsolation(` calls and zero
`observeHiddenDirectWindowsFencedSample(` calls. The RED assertion passed.

Baseline blob identities, in I5 ownership order:

- observation core: `e1e28ec7e68ba454c56a6e63fddeca7c790408dd`
- observation core test: `823f0a5f7c66bc66e7591194f2b68198c8d51125`
- observation Windows test tree: `814c78c2cf7b55da52a2b8b5f11e527ffeb65e4c`
- lifecycle core: `47f98d33abacff050aba4275ad5bff570dd89a50`
- lifecycle core test: `c3a4c74cde040a811803ce80d7d963ffbcf61b26`
- lifecycle Windows: `496e04cb9ea61416cc58aa2cddf4697a53e3a485`
- lifecycle Windows test: `c3a65be5a5477d3bd6b8fbfae5132d4650cb5349`

## Same-tree GREEN

The owned tree contains all four seam families. A bounded worker extraction
contains exactly two `observeHiddenDirectWindowsFencedSample(` calls, zero
direct `inventoryHiddenWindowIsolation(` calls and two failure-diagnostic
reporter calls.

An ignored Go harness executed a byte-identical extraction of
`observeHiddenDirectInWorker` and observed exactly two wrapper calls, two
passive-UIA calls, zero diagnostics on success and zero action. `cmp` bound the
executed function text to the owned source. The same harness also forced the
first and second wrapper refusals and reporter failures through those exact
call sites, with one bounded diagnostic and no retry or action. Platform-
neutral host-agent tests executed the underlying fenced sample and proved one
inventory per admitted boundary, one pre plus one post snapshot, and no
inventory after a hostile pre snapshot.

Injected matrices cover live/exited/unknown child and listener state, exact
job and response-TPort predicates, inventory error/empty/non-empty,
post-snapshot change, main absent/exact/changed, handle-close failure,
malformed diagnostics and both worker boundaries. Existing observation tests
continue to prove fail-closed identity/topology and passive UIA with zero
action. Transferred-observer tests prove validation and the ordering
acknowledgement -> exact callback -> local job close. A blocking Linux harness
AST-extracts and executes the byte-identical
`runHiddenWorkerLifecycleWorker` and validation predicates with only the
Windows API boundary replaced by an offline stub. At the actual worker callback
site it proves the exact response job remains open and the live listener owns
the exact response TPort while the callback is blocked. Job close, listener
cleanup and the final child wait remain zero until release, then each normal
cleanup transition occurs exactly once.

The new diagnostic uses the existing clean-HEAD private schema
`qa-mcp.s4-pre-receipt-diagnostic.v1`, allowlists only first/second inventory
stage/failure pairs, fixes action count to zero and raw-UI retention to false,
and round-trips through a strict checkpoint decoder. Otherwise-valid JSON with
an unknown raw-error, endpoint, desktop, handle, PID, port, UI-value or dynamic-
identity field is rejected, as is a trailing second JSON value. Reporter write
failure is surfaced as the closed `pre_receipt_diagnostic_failed` worker state
instead of being discarded.

## Verification outcomes

- Focused host-agent hostile tests: passed.
- Full `go test ./... -count=1`: passed.
- Full `go vet ./...`: passed.
- Offline Linux CI test command: 1,581 passed, 4 expected capture skips,
  74.67% coverage; no live-marked test ran.
- Deterministic Windows test cross-builds: passed twice per architecture with
  byte-identical pairs. Final amd64 SHA-256 is
  `32d4776c3ba5f0eca10d1ecaf4e0faf8d667e93fb0cd117d1aa7cca37ca53954`;
  final 386 SHA-256 is
  `d127b23432736e458d19917ca6fb657bcdfd394afe63bada7c31421443cb697d`.
- Windows-native execution: prohibited and not run. The Windows test tree was
  compiled only; the ignored byte-identical harness executed the two worker
  source call sites without Windows or 1C.
- Changed Go paths: exactly seven, split three non-test plus four test files.
  Added non-test Go lines: 122, below the I5 ceiling of 250.
- Forbidden added action, retry, fallback, marker-derivation, classifier,
  process-assignment and desktop/thread/window-station mutation symbols: zero.
- Hunk audit: every Go hunk maps to the I5-owned core fence/diagnostic,
  Windows wrapper/two call sites, transferred-observer validation/callback or
  corresponding hostile tests.

## Final staged-tree gates

The pre-archive explicit staging plan contained only the seven owned Go paths,
this evidence document, the exact card, its five active OpenSpec files and the
synced capability spec. Staged and working-tree manifest scope checks had zero
missing, extra or mismatched paths. The exported staged index passed full Go
test/vet, Windows amd64/386 test cross-build, strict change/all OpenSpec and
`git diff --cached --check`.

The final archived staging plan and payload fingerprint are recorded by the
ignored delivery manifest and fresh review verdict rather than duplicated
here.

## Review rescue cycle 1

Fresh review cycle 1 returned NO-GO before publication and identified four
hostile-path gaps: discarded diagnostic reporter errors, permissive unknown-
field JSON decoding, static rather than dynamic observer hold/release proof,
and success-only execution of the two real worker call sites. Rescue attempt 1
changed only the I5-owned diagnostic, transferred-observer and corresponding
test predicates. The complete Go, Linux and deterministic cross-build floors
above were rerun after that payload change. Publication remains gated on a new
fresh independent verdict bound to the rescued staged fingerprint.

## Review rescue cycle 2

Fresh review cycle 2 preserved the cycle-1 diagnostic and real worker-boundary
fixes, but returned NO-GO on two remaining blockers. First, the observer oracle
still exercised synthetic platform-neutral orchestration rather than the actual
`runHiddenWorkerLifecycleWorker` boundary. Second, that synthetic callback and
release orchestration exceeded the platform-neutral file's I5 authorization.

Final same-card rescue attempt 2 removes that generic orchestration completely:
`hidden_desktop_worker_lifecycle.go` now contains only the exact transferred-
observer validation predicate. Validation, callback invocation, held-job close
and final cleanup sequencing are direct statements in the already authorized
Windows worker predicate. The connected byte-identical offline harness above
executes that actual worker predicate, blocks its callback, observes the exact
held job and live listener/response TPort, and releases it before normal cleanup.
The full Go, Python, deterministic cross-build, OpenSpec, scope, ceiling and
staged-tree floors were rerun after this final bounded rescue.
